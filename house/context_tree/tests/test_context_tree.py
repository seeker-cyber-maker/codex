from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

from house.context_tree import (
    ContextViewError,
    append_event,
    apply_context_operation,
    create_context_view,
    project_session_tree,
    rejected_operation_receipt,
    verify_journal,
)

AUTHORITY_HASH = hashlib.sha256(b"sealed-task-authority").hexdigest()
CLI = pathlib.Path(__file__).resolve().parents[1] / "codex_house_context.py"


def event(
    event_id: str,
    branch_id: str,
    sequence: int,
    source_ref: str,
    payload: bytes,
    parent_branch_id: str | None = None,
    fork_turn_id: str | None = None,
) -> dict[str, object]:
    return {
        "schema": "codex-house-event/1",
        "event_id": event_id,
        "session_id": "root",
        "branch_id": branch_id,
        "parent_branch_id": parent_branch_id,
        "fork_turn_id": fork_turn_id,
        "turn_id": "turn-1",
        "item_id": event_id,
        "sequence": sequence,
        "occurred_at": "2026-08-20T13:50:00Z",
        "kind": "message",
        "source": "app_server",
        "payload_ref": source_ref,
        "payload_sha256": hashlib.sha256(payload).hexdigest(),
        "redaction": "none",
    }


class SessionTreeTests(unittest.TestCase):
    def test_normalizes_unloaded_session_fallback_and_preserves_relations(self) -> None:
        tree = project_session_tree(
            {
                "data": [
                    {
                        "id": "root",
                        "sessionId": "root",
                        "forkedFromId": None,
                        "parentThreadId": None,
                    },
                    {
                        "id": "fork",
                        "sessionId": "fork",
                        "forkedFromId": "root",
                        "parentThreadId": None,
                        "forkPointTurnId": "turn-1",
                    },
                    {
                        "id": "worker",
                        "sessionId": "root",
                        "forkedFromId": None,
                        "parentThreadId": "fork",
                    },
                ]
            },
            require_fork_points=True,
        )
        nodes = {node["thread_id"]: node for node in tree["nodes"]}
        self.assertEqual(tree["roots"], ["root"])
        self.assertEqual(nodes["fork"]["derived_session_id"], "root")
        self.assertEqual(nodes["fork"]["session_id_status"], "unloaded_self_fallback")
        self.assertEqual(nodes["fork"]["relation"], "fork")
        self.assertEqual(nodes["fork"]["fork_turn_id"], "turn-1")
        self.assertEqual(nodes["worker"]["relation"], "spawn")
        self.assertEqual(nodes["fork"]["children"], ["worker"])

    def test_rejects_cycles_and_missing_fork_points(self) -> None:
        with self.assertRaisesRegex(ValueError, "cycle"):
            project_session_tree(
                [
                    {"id": "a", "forkedFromId": "b"},
                    {"id": "b", "forkedFromId": "a"},
                ]
            )
        with self.assertRaisesRegex(ValueError, "missing a captured fork point"):
            project_session_tree(
                [
                    {"id": "a"},
                    {"id": "b", "forkedFromId": "a"},
                ],
                require_fork_points=True,
            )


class CliTests(unittest.TestCase):
    def test_project_tree_cli_writes_sealed_projection(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = pathlib.Path(tempdir)
            source = root / "threads.json"
            output = root / "tree.json"
            source.write_text(
                json.dumps(
                    [
                        {"id": "root", "sessionId": "root"},
                        {
                            "id": "fork",
                            "sessionId": "fork",
                            "forkedFromId": "root",
                            "forkPointTurnId": "turn-1",
                        },
                    ]
                ),
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "project-tree",
                    str(source),
                    str(output),
                    "--require-fork-points",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            projected = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(projected["schema"], "codex-session-tree/1")
            self.assertRegex(projected["projection_sha256"], r"^[0-9a-f]{64}$")


class ConservationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.journal = pathlib.Path(self.tempdir.name) / "events.jsonl"
        self.payloads = {
            "blob://sha256/core": b"core instruction",
            "blob://sha256/large": b"large optional history",
        }
        self.events = [
            append_event(
                self.journal,
                event(
                    "event-core",
                    "root",
                    1,
                    "blob://sha256/core",
                    self.payloads["blob://sha256/core"],
                ),
            ),
            append_event(
                self.journal,
                event(
                    "event-large",
                    "root",
                    2,
                    "blob://sha256/large",
                    self.payloads["blob://sha256/large"],
                ),
            ),
        ]
        self.base_view = create_context_view(
            {
                "session_id": "root",
                "branch_id": "root",
                "task_id": "task-1",
                "created_at": "2026-08-20T13:51:00Z",
                "budget_tokens": 4096,
                "authority_hash": AUTHORITY_HASH,
                "blocks": [
                    {
                        "block_id": "core",
                        "mode": "verbatim",
                        "state": "core",
                        "reason": "task authority",
                        "source_ref": "blob://sha256/core",
                        "source_sha256": hashlib.sha256(
                            self.payloads["blob://sha256/core"]
                        ).hexdigest(),
                    },
                    {
                        "block_id": "large",
                        "mode": "locator",
                        "state": "optional",
                        "reason": "historical detail",
                        "source_ref": "blob://sha256/large",
                        "source_sha256": hashlib.sha256(
                            self.payloads["blob://sha256/large"]
                        ).hexdigest(),
                    },
                ],
            },
            self.events,
        )

    def operation(self, name: str, **extra: object) -> dict[str, object]:
        return {
            "operation": name,
            "task_id": "task-1",
            "branch_id": "root",
            "authority_hash": AUTHORITY_HASH,
            "at": "2026-08-20T13:52:00Z",
            **extra,
        }

    def test_journal_detects_tampering(self) -> None:
        self.assertEqual(len(verify_journal(self.journal)), 2)
        original = self.journal.read_text(encoding="utf-8")
        self.journal.write_text(
            original.replace("event-large", "event-tampered", 1), encoding="utf-8"
        )
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            verify_journal(self.journal)

    def test_remove_and_restore_never_rewrite_journal(self) -> None:
        before = self.journal.read_bytes()
        reduced, remove_receipt = apply_context_operation(
            self.base_view,
            self.operation("remove", block_id="large", reason="budget"),
            self.events,
        )
        self.assertEqual(remove_receipt["state"], "APPLIED")
        self.assertEqual([block["block_id"] for block in reduced["blocks"]], ["core"])
        self.assertEqual(reduced["exclusions"][0]["source_ref"], "blob://sha256/large")
        self.assertEqual(self.journal.read_bytes(), before)

        restored, restore_receipt = apply_context_operation(
            reduced,
            self.operation(
                "restore-parent-view", target_view_id=self.base_view["view_id"]
            ),
            self.events,
            parent_view=self.base_view,
        )
        self.assertEqual(restore_receipt["state"], "APPLIED")
        self.assertEqual(
            [block["block_id"] for block in restored["blocks"]], ["core", "large"]
        )
        self.assertEqual(restored["restored_from_view_id"], self.base_view["view_id"])
        self.assertEqual(self.journal.read_bytes(), before)

    def test_stale_identity_fails_closed_with_receipt(self) -> None:
        stale = self.operation("pin", block_id="large")
        stale["authority_hash"] = hashlib.sha256(b"stale").hexdigest()
        with self.assertRaises(ContextViewError) as caught:
            apply_context_operation(self.base_view, stale, self.events)
        self.assertEqual(caught.exception.code, "STALE_CONTEXT_VIEW")
        receipt = rejected_operation_receipt(self.base_view, stale, caught.exception)
        self.assertEqual(receipt["state"], "REJECTED")
        self.assertEqual(receipt["error_code"], "STALE_CONTEXT_VIEW")
        self.assertIsNone(receipt["new_view_id"])

    def test_unknown_source_and_digest_mismatch_fail_closed(self) -> None:
        bad_spec = {
            "session_id": "root",
            "branch_id": "root",
            "task_id": "task-1",
            "authority_hash": AUTHORITY_HASH,
            "blocks": [
                {
                    "block_id": "unknown",
                    "mode": "locator",
                    "state": "optional",
                    "reason": "must fail",
                    "source_ref": "blob://sha256/missing",
                    "source_sha256": hashlib.sha256(b"missing").hexdigest(),
                }
            ],
        }
        with self.assertRaises(ContextViewError) as caught:
            create_context_view(bad_spec, self.events)
        self.assertEqual(caught.exception.code, "UNKNOWN_SOURCE")

        bad_spec["blocks"][0]["source_ref"] = "blob://sha256/core"
        with self.assertRaises(ContextViewError) as caught:
            create_context_view(bad_spec, self.events)
        self.assertEqual(caught.exception.code, "SOURCE_HASH_MISMATCH")

    def test_retrieve_pin_unpin_and_replace_summary(self) -> None:
        summary_payload = b"summary with provenance"
        summary_event = append_event(
            self.journal,
            event(
                "event-summary",
                "root",
                3,
                "blob://sha256/summary",
                summary_payload,
            ),
        )
        events = [*self.events, summary_event]
        pinned, _ = apply_context_operation(
            self.base_view,
            self.operation("pin", block_id="large"),
            events,
        )
        self.assertEqual(pinned["blocks"][1]["state"], "pinned")
        unpinned, _ = apply_context_operation(
            pinned,
            {
                **self.operation("unpin", block_id="large"),
                "at": "2026-08-20T13:53:00Z",
            },
            events,
        )
        self.assertEqual(unpinned["blocks"][1]["state"], "optional")

        summary_block = {
            "block_id": "summary",
            "mode": "locator",
            "state": "optional",
            "reason": "recall compact evidence",
            "source_ref": "blob://sha256/summary",
            "source_sha256": hashlib.sha256(summary_payload).hexdigest(),
        }
        retrieved, _ = apply_context_operation(
            unpinned,
            {
                **self.operation("retrieve", block=summary_block),
                "at": "2026-08-20T13:54:00Z",
            },
            events,
        )
        self.assertEqual(retrieved["blocks"][-1]["mode"], "retrieved")

        replacement = {
            **summary_block,
            "block_id": "large",
            "mode": "summary",
            "reason": "replace large locator with receipted summary",
        }
        replaced, _ = apply_context_operation(
            retrieved,
            {
                **self.operation(
                    "replace-summary", block_id="large", block=replacement
                ),
                "at": "2026-08-20T13:55:00Z",
            },
            events,
        )
        large = next(
            block for block in replaced["blocks"] if block["block_id"] == "large"
        )
        self.assertEqual(large["mode"], "summary")


if __name__ == "__main__":
    unittest.main()

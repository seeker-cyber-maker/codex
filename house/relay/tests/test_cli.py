"""CLI parity tests for the offline worker relay."""

from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from house.relay.cli import main
from house.worker_catalog import ingest_catalog


def catalog_receipt() -> dict[str, object]:
    return ingest_catalog(
        {
            "schema": "codex-house-local-worker-catalog/1",
            "source": "provider-orchestration",
            "source_commit": "a" * 40,
            "source_tree": "b" * 40,
            "workers": [
                {
                    "id": "local.alpha",
                    "approval": "approved_specialist",
                    "status": "qualified",
                    "dispatch": "not_dispatchable",
                    "capabilities": ["classification"],
                }
            ],
        }
    )


class RelayCliTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.catalog_path = self.root / "catalog-receipt.json"
        self.catalog_path.write_text(json.dumps(catalog_receipt()), encoding="utf-8")
        self.envelope_path = self.root / "envelope.json"
        self.envelope_path.write_text(
            json.dumps(
                {
                    "schema": "codex-house-relay-envelope/1",
                    "envelope_id": "relay-cli-001",
                    "thread_id": "thread-cli-001",
                    "sender_id": "worker.alpha",
                    "recipient_id": "worker.beta",
                    "contract_version": "worker-contract/1",
                    "payload": {"kind": "proposal", "artifact_sha256": "a" * 64},
                    "ttl_hops": 1,
                    "turn_budget": 1,
                }
            ),
            encoding="utf-8",
        )

    def _snapshot_documents(self) -> tuple[str, str, str, dict[str, str]]:
        from house.relay.operator_registration import build_relay_preview_registration
        from house.relay.operator_snapshot import render_operator_snapshot_html
        from house.relay.preview_index import render_relay_preview_index_html
        from house.relay.snapshot_descriptor import build_operator_snapshot_descriptor
        from house.relay.task_card_index import render_task_card_index_html
        from house.task_spine import TaskSpine

        response = {
            "schema": "codex-house-relay-dashboard-response/1",
            "status": 200,
            "body": {"worker": "alpha", "note": "source-only"},
            "transport": "NOT_BOUND",
        }
        relay = render_relay_preview_index_html(
            [build_relay_preview_registration(response)]
        )
        spine = TaskSpine(self.root / "tasks.sqlite")
        spine.create_work_item("work-safe", "CLI inventory")
        spine.create_task_packet(
            "task-safe",
            "work-safe",
            "Inspect one named envelope.",
            case_type="evidence_review",
        )
        tasks = render_task_card_index_html(spine.task_cards())
        spine.close()
        snapshot = render_operator_snapshot_html(relay, tasks)
        return (
            relay,
            tasks,
            snapshot,
            build_operator_snapshot_descriptor(relay, tasks, snapshot),
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_cli(self, argv: list[str]) -> tuple[int, dict[str, object]]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exit_code = main(argv)
        return exit_code, json.loads(output.getvalue())

    def test_directory_lookup_and_envelope_status_have_separate_inputs(self) -> None:
        exit_code, address = self.run_cli(
            [
                "directory-address",
                "--catalog-receipt",
                str(self.catalog_path),
                "--recipient-id",
                "local.alpha",
            ]
        )
        self.assertEqual(exit_code, 0)
        self.assertEqual(address["runtime_disposition"], "NOT_ATTEMPTED")

        relay_path = self.root / "relay.sqlite"
        exit_code, queued = self.run_cli(
            [
                "submit",
                "--relay-db",
                str(relay_path),
                "--input",
                str(self.envelope_path),
            ]
        )
        self.assertEqual(exit_code, 0)
        self.assertEqual(queued["state"], "QUEUED")
        self.assertEqual(queued["runtime_disposition"], "NOT_ATTEMPTED")

        exit_code, status = self.run_cli(
            ["status", "--relay-db", str(relay_path), "--envelope-id", "relay-cli-001"]
        )
        self.assertEqual(exit_code, 0)
        self.assertEqual(status["state"], "QUEUED")

    def test_snapshot_inventory_requires_explicit_json_path_list(self) -> None:
        from house.relay.snapshot_envelope import write_operator_snapshot_envelope

        relay, tasks, snapshot, descriptor = self._snapshot_documents()
        receipt = self.root / "snapshot-receipt"
        write_operator_snapshot_envelope(receipt, relay, tasks, snapshot, descriptor)
        path_list = self.root / "snapshot-paths.json"
        path_list.write_text(json.dumps([str(receipt)]), encoding="utf-8")

        exit_code, output = self.run_cli(
            ["snapshot-inventory", "--input", str(path_list)]
        )

        self.assertEqual(exit_code, 0)
        self.assertIsInstance(output, list)
        self.assertEqual(output[0]["state"], "VALID_OFFLINE")
        self.assertNotIn(snapshot, str(output))

    def test_snapshot_inventory_rejects_object_input(self) -> None:
        path_list = self.root / "snapshot-paths.json"
        path_list.write_text(json.dumps({"paths": []}), encoding="utf-8")
        with self.assertRaises(SystemExit) as raised:
            self.run_cli(["snapshot-inventory", "--input", str(path_list)])
        self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()

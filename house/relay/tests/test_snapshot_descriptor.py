from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from house.relay.operator_registration import build_relay_preview_registration
from house.relay.operator_snapshot import render_operator_snapshot_html
from house.relay.preview_index import render_relay_preview_index_html
from house.relay.snapshot_descriptor import (
    OperatorSnapshotDescriptorError,
    build_operator_snapshot_descriptor,
    inspect_operator_snapshot_descriptor,
    verify_operator_snapshot_descriptor,
)
from house.relay.task_card_index import render_task_card_index_html
from house.task_spine import TaskSpine


def _documents() -> tuple[str, str, str]:
    response = {
        "schema": "codex-house-relay-dashboard-response/1",
        "status": 200,
        "body": {"worker": "alpha", "note": "source-only"},
        "transport": "NOT_BOUND",
    }
    relay = render_relay_preview_index_html(
        [build_relay_preview_registration(response)]
    )
    with tempfile.TemporaryDirectory() as tempdir:
        spine = TaskSpine(Path(tempdir) / "task.sqlite")
        spine.create_work_item("work-safe", "Static receipt")
        spine.create_task_packet(
            "task-safe",
            "work-safe",
            "Review this static snapshot.",
            case_type="evidence_review",
        )
        tasks = render_task_card_index_html(spine.task_cards())
        spine.close()
    return relay, tasks, render_operator_snapshot_html(relay, tasks)


class OperatorSnapshotDescriptorTests(unittest.TestCase):
    def test_build_is_deterministic_and_contains_only_hashes(self) -> None:
        relay, tasks, snapshot = _documents()
        first = build_operator_snapshot_descriptor(relay, tasks, snapshot)
        second = build_operator_snapshot_descriptor(relay, tasks, snapshot)

        self.assertEqual(first, second)
        self.assertEqual(first["state"], "FROZEN_OFFLINE")
        self.assertEqual(first["worker_dispatch"], "NOT_ATTEMPTED")
        self.assertEqual(first["authority"], "NOT_GRANTED")
        self.assertNotIn(relay, str(first))
        self.assertNotIn(tasks, str(first))
        self.assertNotIn(snapshot, str(first))
        self.assertEqual(
            verify_operator_snapshot_descriptor(first, relay, tasks, snapshot), first
        )

    def test_tampered_descriptor_or_documents_fail_closed(self) -> None:
        relay, tasks, snapshot = _documents()
        descriptor = build_operator_snapshot_descriptor(relay, tasks, snapshot)
        bad_descriptor = copy.deepcopy(descriptor)
        bad_descriptor["authority"] = "GRANTED"
        with self.assertRaisesRegex(OperatorSnapshotDescriptorError, "authority"):
            inspect_operator_snapshot_descriptor(bad_descriptor)
        with self.assertRaisesRegex(
            OperatorSnapshotDescriptorError, "snapshot does not match"
        ):
            build_operator_snapshot_descriptor(relay, tasks, snapshot + "x")
        with self.assertRaisesRegex(
            OperatorSnapshotDescriptorError, "source documents are not valid"
        ):
            verify_operator_snapshot_descriptor(
                descriptor, relay + " ", tasks, snapshot
            )
        replacement_response = {
            "schema": "codex-house-relay-dashboard-response/1",
            "status": 200,
            "body": {"worker": "beta", "note": "different frozen source"},
            "transport": "NOT_BOUND",
        }
        replacement_relay = render_relay_preview_index_html(
            [build_relay_preview_registration(replacement_response)]
        )
        replacement_snapshot = render_operator_snapshot_html(replacement_relay, tasks)
        with self.assertRaisesRegex(
            OperatorSnapshotDescriptorError, "does not match replayed"
        ):
            verify_operator_snapshot_descriptor(
                descriptor, replacement_relay, tasks, replacement_snapshot
            )

    def test_digest_tampering_is_rejected(self) -> None:
        relay, tasks, snapshot = _documents()
        descriptor = build_operator_snapshot_descriptor(relay, tasks, snapshot)
        descriptor["snapshot_sha256"] = "0" * 64
        with self.assertRaisesRegex(
            OperatorSnapshotDescriptorError, "digest does not match"
        ):
            inspect_operator_snapshot_descriptor(descriptor)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

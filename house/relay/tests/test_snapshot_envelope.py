from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from house.relay.operator_registration import build_relay_preview_registration
from house.relay.operator_snapshot import render_operator_snapshot_html
from house.relay.preview_index import render_relay_preview_index_html
from house.relay.snapshot_descriptor import build_operator_snapshot_descriptor
from house.relay.snapshot_envelope import (
    OperatorSnapshotEnvelopeError,
    inspect_operator_snapshot_envelope,
    write_operator_snapshot_envelope,
)
from house.relay.task_card_index import render_task_card_index_html
from house.task_spine import TaskSpine


def _documents() -> tuple[str, str, str, dict[str, str]]:
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
        spine.create_work_item("work-safe", "Static envelope")
        spine.create_task_packet(
            "task-safe",
            "work-safe",
            "Persist frozen static receipt.",
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


class OperatorSnapshotEnvelopeTests(unittest.TestCase):
    def test_write_and_inspect_are_deterministic_and_complete(self) -> None:
        relay, tasks, snapshot, descriptor = _documents()
        with tempfile.TemporaryDirectory() as tempdir:
            target = Path(tempdir) / "receipt-001"
            receipt = write_operator_snapshot_envelope(
                target, relay, tasks, snapshot, descriptor
            )

            self.assertEqual(receipt, inspect_operator_snapshot_envelope(target))
            self.assertEqual(receipt["state"], "COMPLETE_OFFLINE")
            self.assertEqual(
                receipt["descriptor_receipt_sha256"], descriptor["descriptor_sha256"]
            )
            self.assertEqual(
                {entry.name for entry in target.iterdir()},
                {
                    "relay-preview-index.html",
                    "task-card-index.html",
                    "operator-snapshot.html",
                    "descriptor.json",
                    "envelope.json",
                },
            )

    def test_existing_or_relative_target_is_refused(self) -> None:
        relay, tasks, snapshot, descriptor = _documents()
        with tempfile.TemporaryDirectory() as tempdir:
            target = Path(tempdir) / "receipt-001"
            target.mkdir()
            with self.assertRaisesRegex(
                OperatorSnapshotEnvelopeError, "already exists"
            ):
                write_operator_snapshot_envelope(
                    target, relay, tasks, snapshot, descriptor
                )
        with self.assertRaisesRegex(OperatorSnapshotEnvelopeError, "must be absolute"):
            write_operator_snapshot_envelope(
                "receipt-001", relay, tasks, snapshot, descriptor
            )

    def test_invalid_receipt_refuses_before_creating_target(self) -> None:
        relay, tasks, snapshot, descriptor = _documents()
        descriptor["authority"] = "GRANTED"
        with tempfile.TemporaryDirectory() as tempdir:
            target = Path(tempdir) / "receipt-001"
            with self.assertRaisesRegex(OperatorSnapshotEnvelopeError, "not valid"):
                write_operator_snapshot_envelope(
                    target, relay, tasks, snapshot, descriptor
                )
            self.assertFalse(target.exists())

    def test_tampering_or_incomplete_storage_fails_closed(self) -> None:
        relay, tasks, snapshot, descriptor = _documents()
        with tempfile.TemporaryDirectory() as tempdir:
            target = Path(tempdir) / "receipt-001"
            write_operator_snapshot_envelope(target, relay, tasks, snapshot, descriptor)
            (target / "operator-snapshot.html").write_text(
                snapshot + " ", encoding="utf-8"
            )
            with self.assertRaisesRegex(OperatorSnapshotEnvelopeError, "not valid"):
                inspect_operator_snapshot_envelope(target)

            incomplete = Path(tempdir) / "interrupted"
            incomplete.mkdir()
            (incomplete / ".INCOMPLETE").write_text("INCOMPLETE\n", encoding="utf-8")
            with self.assertRaisesRegex(OperatorSnapshotEnvelopeError, "incomplete"):
                inspect_operator_snapshot_envelope(incomplete)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

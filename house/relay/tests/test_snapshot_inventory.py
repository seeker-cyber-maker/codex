from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from house.relay.operator_registration import build_relay_preview_registration
from house.relay.operator_snapshot import render_operator_snapshot_html
from house.relay.preview_index import render_relay_preview_index_html
from house.relay.snapshot_descriptor import build_operator_snapshot_descriptor
from house.relay.snapshot_envelope import write_operator_snapshot_envelope
from house.relay.snapshot_inventory import (
    OperatorSnapshotInventoryError,
    inspect_operator_snapshot_inventory,
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
        spine.create_work_item("work-safe", "Static inventory")
        spine.create_task_packet(
            "task-safe",
            "work-safe",
            "Inspect named static receipts.",
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


class OperatorSnapshotInventoryTests(unittest.TestCase):
    def test_named_valid_envelopes_return_content_free_receipts(self) -> None:
        relay, tasks, snapshot, descriptor = _documents()
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            first = root / "receipt-001"
            second = root / "receipt-002"
            write_operator_snapshot_envelope(first, relay, tasks, snapshot, descriptor)
            write_operator_snapshot_envelope(second, relay, tasks, snapshot, descriptor)

            records = inspect_operator_snapshot_inventory([first, second])

            self.assertEqual(
                [record["state"] for record in records], ["VALID_OFFLINE"] * 2
            )
            self.assertEqual(records[0]["path"], str(first.resolve()))
            self.assertEqual(records[1]["path"], str(second.resolve()))
            self.assertNotIn("operator-snapshot.html", str(records))
            self.assertNotIn(snapshot, str(records))

    def test_bad_path_or_bad_envelope_has_an_individual_rejection(self) -> None:
        relay, tasks, snapshot, descriptor = _documents()
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            good = root / "receipt-001"
            incomplete = root / "interrupted"
            write_operator_snapshot_envelope(good, relay, tasks, snapshot, descriptor)
            incomplete.mkdir()
            (incomplete / ".INCOMPLETE").write_text("INCOMPLETE\n", encoding="utf-8")

            records = inspect_operator_snapshot_inventory(
                [good, incomplete, root / "missing", "relative-receipt"]
            )

            self.assertEqual(records[0]["state"], "VALID_OFFLINE")
            self.assertEqual(records[1]["state"], "REJECTED_ENVELOPE")
            self.assertEqual(records[1]["reason"], "envelope is incomplete")
            self.assertEqual(records[2]["state"], "REJECTED_ENVELOPE")
            self.assertEqual(records[3]["state"], "REJECTED_INPUT")
            self.assertFalse((root / "missing").exists())

    def test_duplicate_and_invalid_inventory_arguments_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            receipt = root / "receipt-001"
            records = inspect_operator_snapshot_inventory(
                [receipt, root / "." / "receipt-001"]
            )
            self.assertEqual(
                [record["reason"] for record in records],
                ["duplicate canonical path", "duplicate canonical path"],
            )
        with self.assertRaisesRegex(OperatorSnapshotInventoryError, "list or tuple"):
            inspect_operator_snapshot_inventory("/tmp/receipt")
        with self.assertRaisesRegex(OperatorSnapshotInventoryError, "between 1"):
            inspect_operator_snapshot_inventory([])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

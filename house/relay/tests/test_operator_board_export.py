from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from house.relay.operator_board_export import (
    OperatorBoardExportError,
    inspect_operator_board_export,
    write_operator_board_export,
)
from house.relay.operator_inventory_view import render_operator_snapshot_inventory_html
from house.relay.operator_registration import build_relay_preview_registration
from house.relay.operator_snapshot import render_operator_snapshot_html
from house.relay.preview_index import render_relay_preview_index_html
from house.relay.task_card_index import render_task_card_index_html
from house.task_spine import TaskSpine


def _documents() -> tuple[str, str]:
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
        spine.create_work_item("work-safe", "Operator export")
        spine.create_task_packet(
            "task-safe",
            "work-safe",
            "Export a frozen operator board.",
            case_type="evidence_review",
        )
        tasks = render_task_card_index_html(spine.task_cards())
        spine.close()
    snapshot = render_operator_snapshot_html(relay, tasks)
    inventory = render_operator_snapshot_inventory_html(
        [
            {
                "input_path": "/Volumes/Archive/snapshot-001",
                "path": "/Volumes/Archive/snapshot-001",
                "state": "VALID_OFFLINE",
                "reason": "",
                "descriptor_receipt_sha256": "a" * 64,
                "envelope_sha256": "b" * 64,
            }
        ]
    )
    return snapshot, inventory


class OperatorBoardExportTests(unittest.TestCase):
    def test_write_and_inspect_preserve_new_board_and_receipt(self) -> None:
        snapshot, inventory = _documents()
        with tempfile.TemporaryDirectory() as tempdir:
            target = Path(tempdir) / "operator-board.html"
            receipt = write_operator_board_export(target, snapshot, inventory)

            self.assertEqual(receipt, inspect_operator_board_export(target))
            self.assertEqual(receipt["state"], "COMPLETE_OFFLINE")
            self.assertTrue(target.is_file())
            self.assertTrue((Path(f"{target}.receipt.json")).is_file())
            self.assertFalse((target.parent / f".{target.name}.INCOMPLETE").exists())

    def test_existing_invalid_and_incomplete_exports_fail_closed(self) -> None:
        snapshot, inventory = _documents()
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            target = root / "operator-board.html"
            target.write_text("existing", encoding="utf-8")
            with self.assertRaisesRegex(OperatorBoardExportError, "already exists"):
                write_operator_board_export(target, snapshot, inventory)

            invalid = root / "invalid.html"
            with self.assertRaisesRegex(OperatorBoardExportError, "not valid"):
                write_operator_board_export(invalid, "not a snapshot", inventory)
            self.assertFalse(invalid.exists())

            incomplete = root / "interrupted.html"
            marker = root / f".{incomplete.name}.INCOMPLETE"
            marker.write_text("INCOMPLETE\n", encoding="utf-8")
            with self.assertRaisesRegex(OperatorBoardExportError, "incomplete"):
                inspect_operator_board_export(incomplete)

            linked = root / "linked.html"
            linked.symlink_to(target)
            with self.assertRaisesRegex(OperatorBoardExportError, "does not exist"):
                inspect_operator_board_export(linked)

    def test_changed_board_bytes_are_rejected(self) -> None:
        snapshot, inventory = _documents()
        with tempfile.TemporaryDirectory() as tempdir:
            target = Path(tempdir) / "operator-board.html"
            write_operator_board_export(target, snapshot, inventory)
            target.write_text(
                target.read_text(encoding="utf-8").replace("<h1>", "<h1> ", 1),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(OperatorBoardExportError, "hash"):
                inspect_operator_board_export(target)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

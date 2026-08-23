from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from house.relay.operator_board import OperatorBoardError, render_operator_board_html
from house.relay.operator_inventory_view import render_operator_snapshot_inventory_html
from house.relay.operator_registration import build_relay_preview_registration
from house.relay.operator_snapshot import render_operator_snapshot_html
from house.relay.preview_index import render_relay_preview_index_html
from house.relay.task_card_index import render_task_card_index_html
from house.task_spine import TaskSpine


def _operator_snapshot() -> str:
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
        spine.create_work_item("work-safe", "Operator board")
        spine.create_task_packet(
            "task-safe",
            "work-safe",
            "Render frozen operator board.",
            case_type="evidence_review",
        )
        tasks = render_task_card_index_html(spine.task_cards())
        spine.close()
    return render_operator_snapshot_html(relay, tasks)


def _inventory() -> str:
    return render_operator_snapshot_inventory_html(
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


class OperatorBoardTests(unittest.TestCase):
    def test_board_is_static_and_deterministic(self) -> None:
        snapshot = _operator_snapshot()
        inventory = _inventory()

        first = render_operator_board_html(snapshot, inventory)
        second = render_operator_board_html(snapshot, inventory)

        self.assertEqual(first, second)
        self.assertIn("Dream House operator board", first)
        self.assertIn("Operator snapshot", first)
        self.assertIn("Snapshot inventory", first)
        self.assertIn("caller-supplied frozen documents", first)
        self.assertIn("a" * 64, first)
        self.assertIn("default-src 'none'", first)
        self.assertNotIn("<script", first)
        self.assertNotIn("<form", first)
        self.assertNotIn("<a ", first)
        self.assertNotIn("fetch(", first)
        self.assertNotIn("WebSocket", first)

    def test_active_or_wrong_source_document_fails_closed(self) -> None:
        snapshot = _operator_snapshot()
        inventory = _inventory()
        active = inventory.replace("</main>", "<script>alert(1)</script></main>")

        with self.assertRaisesRegex(OperatorBoardError, "active content"):
            render_operator_board_html(snapshot, active)
        with self.assertRaisesRegex(OperatorBoardError, "operator snapshot signature"):
            render_operator_board_html(inventory, snapshot)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from house.relay.operator_registration import build_relay_preview_registration
from house.relay.operator_snapshot import (
    OperatorSnapshotError,
    render_operator_snapshot_html,
)
from house.relay.preview_index import render_relay_preview_index_html
from house.relay.task_card_index import render_task_card_index_html
from house.task_spine import TaskSpine


def _relay_document() -> str:
    response = {
        "schema": "codex-house-relay-dashboard-response/1",
        "status": 200,
        "body": {"worker": "alpha", "note": "source-only"},
        "transport": "NOT_BOUND",
    }
    return render_relay_preview_index_html([build_relay_preview_registration(response)])


def _task_document() -> str:
    with tempfile.TemporaryDirectory() as tempdir:
        spine = TaskSpine(Path(tempdir) / "task.sqlite")
        spine.create_work_item("work-safe", "<& title")
        spine.create_task_packet(
            "task-safe",
            "work-safe",
            "<script>alert(1)</script>",
            case_type="evidence_review",
        )
        document = render_task_card_index_html(spine.task_cards())
        spine.close()
    return document


class OperatorSnapshotTests(unittest.TestCase):
    def test_snapshot_is_deterministic_and_static(self) -> None:
        relay = _relay_document()
        tasks = _task_document()

        first = render_operator_snapshot_html(relay, tasks)
        second = render_operator_snapshot_html(relay, tasks)

        self.assertEqual(first, second)
        self.assertIn("Dream House snapshot", first)
        self.assertIn("Relay previews", first)
        self.assertIn("Task cards", first)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", first)
        self.assertNotIn("<script", first)
        self.assertNotIn("<form", first)
        self.assertNotIn("<a ", first)
        self.assertNotIn("fetch(", first)
        self.assertNotIn("WebSocket", first)
        self.assertNotIn("<iframe", first)
        self.assertIn("default-src 'none'", first)

    def test_invalid_or_active_source_fragments_fail_closed(self) -> None:
        relay = _relay_document()
        tasks = _task_document()
        active = relay.replace("</main>", "<script>alert(1)</script></main>")

        with self.assertRaisesRegex(OperatorSnapshotError, "unsupported tag"):
            render_operator_snapshot_html(active, tasks)
        with self.assertRaisesRegex(OperatorSnapshotError, "signature"):
            render_operator_snapshot_html("not a relay index", tasks)

    def test_source_kind_swapping_fails_closed(self) -> None:
        with self.assertRaisesRegex(OperatorSnapshotError, "relay preview signature"):
            render_operator_snapshot_html(_task_document(), _relay_document())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

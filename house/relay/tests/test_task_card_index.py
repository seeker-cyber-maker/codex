from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from house.relay.task_card_index import TaskCardIndexError, render_task_card_index_html
from house.task_spine import TaskSpine


def _card(
    *,
    task_id: str = "task-safe",
    title: str = "Safe title",
    summary: str = "Safe summary.",
) -> dict[str, object]:
    with tempfile.TemporaryDirectory() as tempdir:
        spine = TaskSpine(Path(tempdir) / "task.sqlite")
        spine.create_work_item("work-safe", title)
        spine.create_task_packet(
            task_id,
            "work-safe",
            summary,
            case_type="evidence_review",
        )
        card = spine.task_cards()[0]
        spine.close()
    return card


class TaskCardIndexTests(unittest.TestCase):
    def test_index_is_deterministic_escaped_and_inert(self) -> None:
        first = _card(
            task_id="task-b", title="<& title", summary="<script>alert(1)</script>"
        )
        second = _card(task_id="task-a", title="Second", summary="plain text")

        forward = render_task_card_index_html([first, second])
        reverse = render_task_card_index_html([second, first])

        self.assertEqual(forward, reverse)
        self.assertIn("2 task cards", forward)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", forward)
        self.assertIn("&lt;&amp; title", forward)
        self.assertLess(forward.index("task-a"), forward.index("task-b"))
        self.assertNotIn("<script", forward)
        self.assertNotIn("<form", forward)
        self.assertNotIn("<a ", forward)
        self.assertNotIn("fetch(", forward)
        self.assertNotIn("WebSocket", forward)
        self.assertIn("default-src 'none'", forward)
        self.assertIn("ADVISORY_NO_SWITCH", str(first["model_advisory"]))
        self.assertIn("routing is advisory", forward)
        self.assertIn("dispatch not attempted", forward)

    def test_duplicate_task_and_noncanonical_shape_fail_closed(self) -> None:
        card = _card()
        with self.assertRaisesRegex(TaskCardIndexError, "duplicate"):
            render_task_card_index_html([card, card])
        malformed = copy.deepcopy(card)
        malformed["untrusted_extra"] = "nope"
        with self.assertRaisesRegex(TaskCardIndexError, "fields are not exact"):
            render_task_card_index_html([malformed])

    def test_dispatch_or_advisory_mutation_is_rejected(self) -> None:
        card = _card()
        dispatched = copy.deepcopy(card)
        dispatched["dispatch"] = "STARTED"
        with self.assertRaisesRegex(TaskCardIndexError, "dispatch"):
            render_task_card_index_html([dispatched])
        switched = copy.deepcopy(card)
        switched["model_advisory"]["mode"] = "SWITCHED"
        with self.assertRaisesRegex(TaskCardIndexError, "may not switch"):
            render_task_card_index_html([switched])

    def test_oversized_summary_and_invalid_digest_are_rejected(self) -> None:
        oversized = _card(summary="x" * 4_097)
        with self.assertRaisesRegex(TaskCardIndexError, "summary"):
            render_task_card_index_html([oversized])
        invalid_digest = _card()
        invalid_digest["routing_decision_sha256"] = "not-a-digest"
        with self.assertRaisesRegex(TaskCardIndexError, "routing decision digest"):
            render_task_card_index_html([invalid_digest])

    def test_unclassified_canonical_task_card_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            spine = TaskSpine(Path(tempdir) / "task.sqlite")
            spine.create_work_item("work-generic", "Generic task")
            spine.create_task_packet(
                "task-generic", "work-generic", "please do the next thing"
            )
            card = spine.task_cards()[0]
            spine.close()

        self.assertEqual(card["case_type"], "")
        html = render_task_card_index_html([card])
        self.assertIn("task-generic", html)

    def test_declared_source_scope_is_visible_and_exact(self) -> None:
        document = render_task_card_index_html([], source_state="NOT_SUPPLIED")

        self.assertIn("Source scope: NOT_SUPPLIED", document)
        with self.assertRaisesRegex(TaskCardIndexError, "source scope"):
            render_task_card_index_html([], source_state="LIVE")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

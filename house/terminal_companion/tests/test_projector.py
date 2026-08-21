from __future__ import annotations

import json
import unittest

from house.terminal_companion import (
    CompanionProjectionError,
    project_jsonl,
    project_notifications,
)


def command(status: str = "completed") -> dict[str, object]:
    return {
        "method": "item/completed",
        "params": {
            "threadId": "thread-1", "turnId": "turn-1",
            "item": {"type": "commandExecution", "id": "exec-1", "command": "pytest -q", "cwd": "/work", "status": status,
                     "aggregatedOutput": "1 passed\n", "exitCode": 0, "durationMs": 33},
        },
    }


class ProjectorTests(unittest.TestCase):
    def test_completed_command_becomes_a_read_only_card(self) -> None:
        card = project_notifications([{"method": "item/started", "params": {}}, command()])[0]
        self.assertEqual(card["command"], "pytest -q")
        self.assertEqual(card["output"], "1 passed\n")
        self.assertEqual(card["redaction_state"], "UPSTREAM_ASSERTED")
        self.assertEqual(card["output_redaction_state"], "NOT_ATTESTED")
        self.assertEqual(card["content_trust"], "DISPLAY_ONLY")
        self.assertEqual(card["dispatch"], "NOT_ATTEMPTED")

    def test_unrelated_items_are_ignored(self) -> None:
        self.assertEqual(project_notifications([{"method": "item/completed", "params": {"item": {"type": "agentMessage"}}}]), [])

    def test_malformed_command_fails_closed(self) -> None:
        broken = command()
        del broken["params"]["item"]["cwd"]  # type: ignore[index]
        with self.assertRaisesRegex(CompanionProjectionError, "cwd"):
            project_notifications([broken])

    def test_incomplete_command_status_fails_closed(self) -> None:
        with self.assertRaisesRegex(CompanionProjectionError, "unsupported"):
            project_notifications([command("inProgress")])

    def test_interrupted_is_not_a_pinned_completed_status(self) -> None:
        with self.assertRaisesRegex(CompanionProjectionError, "unsupported"):
            project_notifications([command("interrupted")])

    def test_jsonl_capture_is_projected_without_opening_a_live_stream(self) -> None:
        cards = project_jsonl('{"method":"item/started","params":{}}\n' + json.dumps(command()))
        self.assertEqual(cards[0]["item_id"], "exec-1")

    def test_bad_jsonl_line_fails_closed_with_its_line_number(self) -> None:
        with self.assertRaisesRegex(CompanionProjectionError, "line 2"):
            project_jsonl('{"method":"item/started"}\nnot-json')

    def test_nontext_output_and_boolean_exit_code_fail_closed(self) -> None:
        malformed_output = command()
        malformed_output["params"]["item"]["aggregatedOutput"] = ["not", "text"]  # type: ignore[index]
        with self.assertRaisesRegex(CompanionProjectionError, "aggregatedOutput"):
            project_notifications([malformed_output])
        malformed_exit = command()
        malformed_exit["params"]["item"]["exitCode"] = True  # type: ignore[index]
        with self.assertRaisesRegex(CompanionProjectionError, "exitCode"):
            project_notifications([malformed_exit])

    def test_output_delta_is_not_misread_as_a_completed_command(self) -> None:
        self.assertEqual(project_notifications([{
            "method": "item/commandExecution/outputDelta",
            "params": {"threadId": "thread-1", "turnId": "turn-1", "itemId": "exec-1", "delta": "partial"},
        }]), [])

    def test_null_aggregate_output_is_preserved(self) -> None:
        no_output = command()
        no_output["params"]["item"]["aggregatedOutput"] = None  # type: ignore[index]
        self.assertIsNone(project_notifications([no_output])[0]["output"])

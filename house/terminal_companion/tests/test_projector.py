from __future__ import annotations

import unittest

from house.terminal_companion import CompanionProjectionError, project_notifications


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

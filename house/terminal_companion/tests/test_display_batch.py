from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from house.terminal_companion import (
    CompanionProjectionError,
    build_display_batch,
    evaluate_compatibility,
    project_notifications,
    verify_display_chain,
)


def card() -> dict[str, object]:
    return project_notifications(
        [
            {
                "method": "item/completed",
                "params": {
                    "threadId": "thread-1",
                    "turnId": "turn-1",
                    "item": {
                        "type": "commandExecution",
                        "id": "exec-1",
                        "command": "pytest -q",
                        "cwd": "/work",
                        "status": "completed",
                        "aggregatedOutput": "1 passed\n",
                        "exitCode": 0,
                        "durationMs": 33,
                    },
                },
            }
        ]
    )[0]


class DisplayBatchTests(unittest.TestCase):
    def test_batch_is_deterministic_and_one_way(self) -> None:
        first = build_display_batch([card()], sequence=0)
        second = build_display_batch([card()], sequence=0)
        self.assertEqual(first, second)
        self.assertEqual(first["authority"], "OBSERVE_ONLY")
        self.assertEqual(first["reverse_channel"], "PROHIBITED")
        self.assertEqual(first["transport"], "NOT_ATTEMPTED")
        self.assertEqual(len(first["batch_id"]), 64)

    def test_sequence_and_previous_id_bind_replay_order(self) -> None:
        first = build_display_batch([card()], sequence=0)
        second = build_display_batch(
            [card()], sequence=1, previous_batch_id=first["batch_id"]
        )
        self.assertEqual(second["previous_batch_id"], first["batch_id"])
        self.assertNotEqual(first["batch_id"], second["batch_id"])
        verify_display_chain([first, second])

        broken = dict(second)
        broken["previous_batch_id"] = "0" * 64
        with self.assertRaisesRegex(CompanionProjectionError, "predecessor"):
            verify_display_chain([first, broken])

        bad_status = dict(first)
        bad_status["cards"] = [dict(first["cards"][0], status="inProgress")]
        with self.assertRaisesRegex(CompanionProjectionError, "unsupported status"):
            verify_display_chain([bad_status])

    def test_unsafe_card_authority_fails_closed(self) -> None:
        unsafe = card()
        unsafe["dispatch"] = "ATTEMPTED"
        with self.assertRaisesRegex(CompanionProjectionError, "unsafe dispatch"):
            build_display_batch([unsafe], sequence=0)

    def test_schema_drift_fails_closed(self) -> None:
        drifted = card()
        drifted["remote_control"] = True
        with self.assertRaisesRegex(CompanionProjectionError, "revision-1 schema"):
            build_display_batch([drifted], sequence=0)

    def test_terminal_and_unicode_controls_are_escaped_for_plain_text(self) -> None:
        unsafe = card()
        unsafe["command"] = "printf '\u001b]52;c;bad\u0007'\u202ereversed"
        unsafe["output"] = "line 1\nline 2\u001b[31m\ud800"
        batch = build_display_batch([unsafe], sequence=0)
        displayed = batch["cards"][0]
        self.assertEqual(batch["presentation_format"], "PLAIN_TEXT_ONLY")
        self.assertEqual(
            displayed["text_rendering_state"],
            "CONTROL_AND_FORMAT_CHARACTERS_ESCAPED",
        )
        self.assertIn(r"\u001b", displayed["command"])
        self.assertIn(r"\u202e", displayed["command"])
        self.assertIn(r"\n", displayed["output"])
        self.assertIn(r"\ud800", displayed["output"])
        verify_display_chain([batch])

    def test_bounds_and_identifiers_fail_closed(self) -> None:
        with self.assertRaisesRegex(CompanionProjectionError, "non-negative"):
            build_display_batch([], sequence=-1)
        with self.assertRaisesRegex(CompanionProjectionError, "SHA-256"):
            build_display_batch([], sequence=1, previous_batch_id="not-a-digest")
        with self.assertRaisesRegex(CompanionProjectionError, "requires a previous"):
            build_display_batch([], sequence=1)
        with self.assertRaisesRegex(CompanionProjectionError, "must not name"):
            build_display_batch([], sequence=0, previous_batch_id="0" * 64)
        with self.assertRaisesRegex(CompanionProjectionError, "count exceeds"):
            build_display_batch([card()] * 129, sequence=0)
        expanded = card()
        expanded["output"] = "\x1b" * 1_200_000
        with self.assertRaisesRegex(CompanionProjectionError, "encoded bytes"):
            build_display_batch([expanded], sequence=0)

    def test_compatibility_is_independent_of_bundle_versions(self) -> None:
        self.assertEqual(evaluate_compatibility(1, 1), "COMPATIBLE")
        self.assertEqual(evaluate_compatibility(99, 2), "SELF_UPGRADE_REQUIRED")
        with self.assertRaisesRegex(CompanionProjectionError, "positive integer"):
            evaluate_compatibility(0, 1)

    def test_cli_emits_a_display_batch_without_transport(self) -> None:
        notification = {
            "method": "item/completed",
            "params": {
                "threadId": "thread-1",
                "turnId": "turn-1",
                "item": {
                    "type": "commandExecution",
                    "id": "exec-1",
                    "command": "pytest -q",
                    "cwd": "/work",
                    "status": "completed",
                    "aggregatedOutput": "1 passed\n",
                    "exitCode": 0,
                    "durationMs": 33,
                },
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "capture.json"
            source.write_text(json.dumps([notification]), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "house.terminal_companion",
                    "--display-batch",
                    "--sequence",
                    "0",
                    "--input",
                    str(source),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        result = json.loads(completed.stdout)
        self.assertEqual(result["direction"], "CODEX_TO_ITERM")
        self.assertEqual(result["transport"], "NOT_ATTEMPTED")

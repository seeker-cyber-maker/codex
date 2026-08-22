from __future__ import annotations

import subprocess
import sys
import unittest

from house.worker_exec import ProcessSupervisorError, supervise_fixture_process


class ProcessSupervisorTests(unittest.TestCase):
    def test_short_fixture_is_reaped_as_an_observation(self) -> None:
        receipt = supervise_fixture_process(
            [sys.executable, "-c", "print('fixture-ok')"], wall_seconds=2
        )
        self.assertEqual(receipt["state"], "REAPED_EXIT_OBSERVED")
        self.assertEqual(receipt["dispatch"], "FIXTURE_ONLY")
        self.assertEqual(receipt["returncode"], 0)
        self.assertIn("fixture-ok", receipt["stdout"]["utf8_preview"])

    def test_timeout_kills_and_reaps_fixture_process_group(self) -> None:
        receipt = supervise_fixture_process(
            [sys.executable, "-c", "import time; time.sleep(30)"],
            wall_seconds=0.1,
            grace_seconds=0.1,
        )
        self.assertEqual(receipt["state"], "BLOCKED_TIMEOUT_REAPED")
        self.assertEqual(receipt["dispatch"], "FIXTURE_ONLY")
        self.assertIsNotNone(receipt["returncode"])

    def test_invalid_argv_and_start_failure_fail_closed(self) -> None:
        with self.assertRaisesRegex(ProcessSupervisorError, "non-empty"):
            supervise_fixture_process([], wall_seconds=1)

        def broken(*args: object, **kwargs: object) -> subprocess.Popen[bytes]:
            raise OSError("nope")

        with self.assertRaisesRegex(ProcessSupervisorError, "could not be started"):
            supervise_fixture_process(["fixture"], wall_seconds=1, popen_factory=broken)

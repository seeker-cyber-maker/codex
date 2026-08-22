from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from house.worker_exec import (
    FixtureGateError,
    WorkerOperationController,
    launch_fixture,
    prepare_operation,
)

HELP = """
  -m, --model <MODEL>
  -s, --sandbox <SANDBOX_MODE>
  -C, --cd <DIR>
      --json
  -o, --output-last-message <FILE>
"""


class FixtureGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        root = Path(self.tempdir.name)
        self.workspace, self.output = root / "workspace", root / "output"
        self.workspace.mkdir()
        self.output.mkdir()
        self.codex = root / "sealed-codex"
        self.codex.write_text("#!/bin/sh\n", encoding="utf-8")
        self.codex.chmod(0o755)
        self.controller = WorkerOperationController(root / "controller.sqlite")
        self.record = prepare_operation(
            {
                "schema": "codex-house-task-card/1",
                "task_id": "task-1",
                "title": "Fixture review",
                "summary": "exercise only the injected fixture path",
                "requested_recipient": "reviewer",
                "requested_recipient_id": None,
            },
            operation_id="fixture-123",
            workspace=self.workspace,
            output_root=self.output,
            codex_path=self.codex,
        )
        self.controller.prepare(self.record)
        self.lease = self.controller.acquire("fixture-123", "test-controller")

    def tearDown(self) -> None:
        self.controller.close()
        self.tempdir.cleanup()

    def launch(self, **kwargs: object) -> dict[str, object]:
        options: dict[str, object] = {
            "operation_id": "fixture-123",
            "holder": "test-controller",
            "fencing_token": self.lease["fencing_token"],
            "execute": True,
            "version_output": "codex-cli 0.147.0",
            "exec_help_output": HELP,
            "runner": lambda argv, timeout: {"argv": list(argv), "timeout": timeout},
        }
        options.update(kwargs)
        return launch_fixture(self.controller, **options)  # type: ignore[arg-type]

    def test_default_is_no_dispatch_and_real_runner_is_not_available(self) -> None:
        receipt = self.launch(execute=False)
        self.assertEqual(receipt["dispatch"], "NOT_ATTEMPTED")
        with self.assertRaisesRegex(FixtureGateError, "fixture runner is required"):
            self.launch(runner=None)
        with self.assertRaisesRegex(FixtureGateError, "version differs"):
            self.launch(version_output="codex-cli 0.148.0")

    def test_final_gate_uses_absolute_sealed_executable_and_blocks_after_fixture(
        self,
    ) -> None:
        receipt = self.launch()
        self.assertEqual(receipt["dispatch"], "FIXTURE_ONLY")
        self.assertEqual(receipt["runner_result"].count(str(self.codex)), 1)
        self.assertTrue((self.output / "fixture-123").is_dir())
        self.assertEqual(self.controller.entry("fixture-123")["state"], "BLOCKED")

    def test_stale_fence_and_output_reservation_prevent_runner_invocation(self) -> None:
        calls: list[object] = []
        with self.assertRaisesRegex(FixtureGateError, "stale operation"):
            self.launch(
                fencing_token="wrong",
                runner=lambda argv, timeout: calls.append(argv),
            )
        self.assertEqual(calls, [])

        (self.output / "fixture-123").mkdir()
        with self.assertRaisesRegex(FixtureGateError, "output reservation"):
            self.launch(runner=lambda argv, timeout: calls.append(argv))
        self.assertEqual(calls, [])

    def test_executable_drift_and_invalid_contract_prevent_runner_invocation(
        self,
    ) -> None:
        calls: list[object] = []
        self.codex.write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(FixtureGateError, "executable changed"):
            launch_fixture(
                self.controller,
                operation_id="fixture-123",
                holder="test-controller",
                fencing_token=self.lease["fencing_token"],
                execute=True,
                version_output="codex-cli 0.147.0",
                exec_help_output=HELP,
                runner=lambda argv, timeout: calls.append(argv),
            )
        self.assertEqual(calls, [])

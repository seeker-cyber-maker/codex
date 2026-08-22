from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from house.worker_exec import (
    WorkerExecError,
    execute_for_test,
    prepare_operation,
    verify_operation,
)


def task_card(**overrides: object) -> dict[str, object]:
    card: dict[str, object] = {
        "schema": "codex-house-task-card/1",
        "task_id": "task-123",
        "title": "Review the guarded adapter",
        "summary": "inspect the operation record without changing the workspace",
        "requested_recipient": "reviewer",
        "requested_recipient_id": None,
    }
    card.update(overrides)
    return card


class WorkerOperationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        root = Path(self.tempdir.name)
        self.workspace = root / "workspace"
        self.workspace.mkdir()
        self.output_root = root / "operations"
        self.output_root.mkdir()
        self.codex = root / "codex"
        self.codex.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        self.codex.chmod(0o755)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def prepare(self, **overrides: object) -> dict[str, object]:
        options: dict[str, object] = {
            "operation_id": "review-123",
            "workspace": self.workspace,
            "output_root": self.output_root,
            "codex_path": self.codex,
        }
        options.update(overrides)
        return prepare_operation(task_card(), **options)

    def test_prepare_is_hash_bound_read_only_and_generic_model_omits_flag(self) -> None:
        record = self.prepare()
        self.assertEqual(
            record["live_dispatch"], "BLOCKED_PENDING_RUNTIME_QUALIFICATION"
        )
        self.assertNotIn("--model", record["argv"])
        self.assertEqual(record["argv"][0], str(self.codex))
        self.assertIn("--sandbox", record["argv"])
        self.assertIn("read-only", record["argv"])
        self.assertEqual(verify_operation(record)["state"], "VERIFIED_NO_DISPATCH")

    def test_specific_model_is_the_only_model_flag_path(self) -> None:
        record = prepare_operation(
            task_card(
                requested_recipient="specific_model",
                requested_recipient_id="gpt-5.6-terra",
            ),
            operation_id="model-123",
            workspace=self.workspace,
            output_root=self.output_root,
            codex_path=self.codex,
        )
        position = record["argv"].index("--model")
        self.assertEqual(record["argv"][position + 1], "gpt-5.6-terra")

    def test_tamper_drift_and_output_reservation_fail_closed(self) -> None:
        record = self.prepare()
        tampered = copy.deepcopy(record)
        tampered["argv"].append("--unsafe")
        with self.assertRaisesRegex(WorkerExecError, "record hash mismatch"):
            verify_operation(tampered)
        self.codex.write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(WorkerExecError, "executable changed"):
            verify_operation(record)
        (self.output_root / "review-123").mkdir()
        with self.assertRaisesRegex(WorkerExecError, "already reserved"):
            self.prepare()

    def test_no_execute_never_calls_runner_and_fake_runner_is_explicitly_labeled(
        self,
    ) -> None:
        record = self.prepare()
        calls: list[object] = []

        def runner(argv: object, *, timeout: object) -> str:
            calls.append((argv, timeout))
            return "fake-complete"

        receipt = execute_for_test(record, runner=runner)
        self.assertEqual(receipt["state"], "PREPARED_NOT_EXECUTED")
        self.assertEqual(calls, [])
        observed = execute_for_test(record, execute=True, runner=runner)
        self.assertEqual(observed["state"], "TEST_RUN_OBSERVED")
        self.assertEqual(observed["dispatch"], "TEST_FAKE_RUNNER_ONLY")
        self.assertEqual(len(calls), 1)
        with self.assertRaisesRegex(WorkerExecError, "live runtime is blocked"):
            execute_for_test(record, execute=True)


if __name__ == "__main__":
    unittest.main()

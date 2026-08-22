from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from house.worker_exec import (
    WorkerControllerError,
    WorkerOperationController,
    prepare_operation,
)


class WorkerControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        root = Path(self.tempdir.name)
        workspace, output = root / "workspace", root / "output"
        workspace.mkdir()
        output.mkdir()
        codex = root / "codex"
        codex.write_text("#!/bin/sh\n", encoding="utf-8")
        codex.chmod(0o755)
        self.now = 100.0
        self.controller = WorkerOperationController(
            root / "controller.sqlite", clock=lambda: self.now
        )
        self.record = prepare_operation(
            {
                "schema": "codex-house-task-card/1",
                "task_id": "task-1",
                "title": "Review",
                "summary": "read only review",
                "requested_recipient": "reviewer",
                "requested_recipient_id": None,
            },
            operation_id="operation-1",
            workspace=workspace,
            output_root=output,
            codex_path=codex,
        )

    def tearDown(self) -> None:
        self.controller.close()
        self.tempdir.cleanup()

    def test_idempotent_prepare_leased_fence_and_blocked_reconciliation(self) -> None:
        first = self.controller.prepare(self.record)
        self.assertEqual(first, self.controller.prepare(self.record))
        lease = self.controller.acquire("operation-1", "controller-a", ttl_seconds=10)
        with self.assertRaisesRegex(WorkerControllerError, "already active"):
            self.controller.acquire("operation-1", "controller-b")
        with self.assertRaisesRegex(WorkerControllerError, "stale operation"):
            self.controller.block_runtime(
                "operation-1",
                holder="controller-a",
                fencing_token="wrong",
                reason="blocked",
            )
        receipt = self.controller.block_runtime(
            "operation-1",
            holder="controller-a",
            fencing_token=lease["fencing_token"],
            reason="runtime qualification incomplete",
        )
        self.assertEqual(receipt["dispatch"], "NOT_ATTEMPTED")
        self.assertEqual(self.controller.entries()[0]["state"], "BLOCKED")
        with self.assertRaisesRegex(WorkerControllerError, "blocked operation"):
            self.controller.acquire("operation-1", "controller-b")

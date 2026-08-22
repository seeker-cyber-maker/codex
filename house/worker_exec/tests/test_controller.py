from __future__ import annotations

import sqlite3
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

    def test_live_intent_is_durable_and_ambiguous_recovery_never_retries(self) -> None:
        self.controller.prepare(self.record)
        lease = self.controller.acquire("operation-1", "controller-a", ttl_seconds=10)
        intent = self.controller.claim_live_launch(
            "operation-1", holder="controller-a", fencing_token=lease["fencing_token"]
        )
        self.assertEqual(intent["state"], "LIVE_SPAWN_INTENT_RECORDED_NO_SPAWN")
        with self.assertRaisesRegex(WorkerControllerError, "already claimed"):
            self.controller.claim_live_launch(
                "operation-1",
                holder="controller-a",
                fencing_token=lease["fencing_token"],
            )
        receipt = self.controller.reconcile_ambiguous_live_intent("operation-1")
        self.assertEqual(receipt["dispatch"], "UNKNOWN_NOT_RERUN")
        self.assertEqual(self.controller.entries()[0]["state"], "BLOCKED")

    def test_live_intent_cannot_be_reacquired_after_lease_expiry(self) -> None:
        self.controller.prepare(self.record)
        lease = self.controller.acquire("operation-1", "controller-a", ttl_seconds=10)
        self.controller.claim_live_launch(
            "operation-1", holder="controller-a", fencing_token=lease["fencing_token"]
        )
        self.now = 111.0
        with self.assertRaisesRegex(WorkerControllerError, "non-retryable"):
            self.controller.acquire("operation-1", "controller-b")
        receipt = self.controller.reconcile_ambiguous_live_intent("operation-1")
        self.assertEqual(receipt["dispatch"], "UNKNOWN_NOT_RERUN")

    def test_identity_and_terminal_observation_are_single_use_and_not_admitted(
        self,
    ) -> None:
        self.controller.prepare(self.record)
        lease = self.controller.acquire("operation-1", "controller-a", ttl_seconds=10)
        self.controller.claim_live_launch(
            "operation-1", holder="controller-a", fencing_token=lease["fencing_token"]
        )
        running = self.controller.record_live_running(
            "operation-1",
            holder="controller-a",
            fencing_token=lease["fencing_token"],
            process_identity="pid:123-start:fixed",
        )
        self.assertEqual(running["state"], "RUNNING_OBSERVED_NO_DISPATCH")
        with self.assertRaisesRegex(WorkerControllerError, "not awaiting"):
            self.controller.record_live_running(
                "operation-1",
                holder="controller-a",
                fencing_token=lease["fencing_token"],
                process_identity="pid:124-start:fixed",
            )
        terminal = self.controller.record_live_terminal_observation(
            "operation-1",
            holder="controller-a",
            fencing_token=lease["fencing_token"],
            process_identity="pid:123-start:fixed",
            observation={"returncode": 0, "stdout_sha256": "0" * 64},
        )
        self.assertEqual(terminal["dispatch"], "NOT_ADMITTED")
        self.assertEqual(self.controller.entries()[0]["state"], "BLOCKED")

    def test_legacy_operation_schema_migrates_without_changing_old_row(self) -> None:
        self.controller.close()
        database = Path(self.tempdir.name) / "legacy.sqlite"
        with sqlite3.connect(database) as legacy:
            legacy.execute(
                "CREATE TABLE operation (id TEXT PRIMARY KEY, record_json TEXT NOT NULL, record_sha256 TEXT NOT NULL, state TEXT NOT NULL CHECK(state IN ('PREPARED','LEASED','BLOCKED')), observation_json TEXT)"
            )
            legacy.execute(
                "INSERT INTO operation VALUES ('old', '{}', 'old-digest', 'BLOCKED', NULL)"
            )
        self.controller = WorkerOperationController(database, clock=lambda: self.now)
        entry = self.controller.entry("old")
        self.assertEqual(entry["state"], "BLOCKED")
        self.assertEqual(entry["record_sha256"], "old-digest")

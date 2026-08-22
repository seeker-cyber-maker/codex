from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from house.worker_exec.cli import main


class WorkerCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.workspace, self.output = self.root / "workspace", self.root / "output"
        self.workspace.mkdir()
        self.output.mkdir()
        self.codex = self.root / "sealed-codex"
        self.codex.write_text("#!/bin/sh\n", encoding="utf-8")
        self.codex.chmod(0o755)
        self.card = self.root / "task-card.json"
        self.card.write_text(
            json.dumps(
                {
                    "schema": "codex-house-task-card/1",
                    "task_id": "task-1",
                    "title": "Prepare evidence review",
                    "summary": "read only fixture preparation",
                    "requested_recipient": "reviewer",
                    "requested_recipient_id": None,
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_prepare_persists_only_a_no_dispatch_operation(self) -> None:
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            status = main(
                [
                    "prepare",
                    "--task-card",
                    str(self.card),
                    "--controller-db",
                    str(self.root / "controller.sqlite"),
                    "--operation-id",
                    "cli-123",
                    "--workspace",
                    str(self.workspace),
                    "--output-root",
                    str(self.output),
                    "--codex-path",
                    str(self.codex),
                ]
            )
        receipt = json.loads(stream.getvalue())
        self.assertEqual(status, 0)
        self.assertEqual(receipt["state"], "PREPARED")
        self.assertEqual(receipt["dispatch"], "NOT_ATTEMPTED")
        self.assertEqual(
            receipt["live_dispatch"], "BLOCKED_PENDING_RUNTIME_QUALIFICATION"
        )

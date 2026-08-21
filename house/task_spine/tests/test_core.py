from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import contextlib
import io
import json

from house.task_spine import TaskSpine, TaskSpineError
from house.task_spine.cli import main


class TaskSpineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.spine = TaskSpine(Path(self.tempdir.name) / "task-spine.sqlite")
        self.spine.create_work_item("work-1", "Offline task spine")
        self.spine.create_task_packet("task-1", "work-1", "review this provenance claim", case_type="evidence_review")

    def tearDown(self) -> None:
        self.spine.close()
        self.tempdir.cleanup()

    def _sealed_path(self) -> str:
        self.spine.append_worker_buffer("buffer-1", "task-1", "record-1", "Evidence-backed worker report.")
        self.spine.seal_worker_buffer("buffer-1")
        self.spine.seal_result_envelope("envelope-1", "task-1", "buffer-1", "artifact:report-1", "complete")
        self.spine.create_import_proposal("proposal-1", "task-1", "envelope-1")
        authorization = self.spine.authorize_import("proposal-1", "lead-1")
        return authorization["event_sha256"]

    def test_happy_path_admits_only_candidate_and_rebuilds_projection(self) -> None:
        basis = self._sealed_path()
        self.spine.admit_candidate("proposal-1", actor="trusted_writer", admission_basis_sha256=basis)
        first = self.spine.rebuild_read_model()
        second = self.spine.rebuild_read_model()
        self.assertEqual(first, second)
        self.assertEqual(first[0]["disposition"], "candidate")
        self.assertEqual(first[0]["candidate_envelope_id"], "envelope-1")
        self.assertTrue(first[0]["routing_decision_sha256"])

    def test_wip_projection_is_metadata_only(self) -> None:
        self._sealed_path()
        row = self.spine.rebuild_read_model()[0]
        self.assertTrue(row["wip_buffer_sha256"])
        self.assertNotIn("Evidence-backed worker report.", str(row))

    def test_missing_authorization_fails_closed(self) -> None:
        self.spine.append_worker_buffer("buffer-1", "task-1", "record-1", "report")
        self.spine.seal_worker_buffer("buffer-1")
        self.spine.seal_result_envelope("envelope-1", "task-1", "buffer-1", "artifact:report-1", "complete")
        proposal = self.spine.create_import_proposal("proposal-1", "task-1", "envelope-1")
        with self.assertRaisesRegex(TaskSpineError, "missing lead authorization"):
            self.spine.admit_candidate("proposal-1", actor="trusted_writer", admission_basis_sha256=proposal["event_sha256"])

    def test_unsealed_buffer_fails_closed(self) -> None:
        self.spine.append_worker_buffer("buffer-1", "task-1", "record-1", "report")
        self.spine.seal_result_envelope("envelope-1", "task-1", "buffer-1", "artifact:report-1", "complete")
        self.spine.create_import_proposal("proposal-1", "task-1", "envelope-1")
        authorization = self.spine.authorize_import("proposal-1", "lead-1")
        with self.assertRaisesRegex(TaskSpineError, "unsealed buffer"):
            self.spine.admit_candidate("proposal-1", actor="trusted_writer", admission_basis_sha256=authorization["event_sha256"])

    def test_stale_basis_and_wrong_actor_fail_closed(self) -> None:
        basis = self._sealed_path()
        with self.assertRaisesRegex(TaskSpineError, "trusted_writer"):
            self.spine.admit_candidate("proposal-1", actor="worker", admission_basis_sha256=basis)
        self.spine.create_work_item("work-2", "Intervening work item")
        with self.assertRaisesRegex(TaskSpineError, "stale admission basis"):
            self.spine.admit_candidate("proposal-1", actor="trusted_writer", admission_basis_sha256=basis)

    def test_unknown_work_or_task_cannot_receive_records(self) -> None:
        with self.assertRaisesRegex(TaskSpineError, "unknown work item"):
            self.spine.create_task_packet("task-x", "missing-work", "do work")
        with self.assertRaisesRegex(TaskSpineError, "unknown task"):
            self.spine.append_worker_buffer("buffer-x", "missing-task", "record-x", "report")

    def test_cli_demo_and_rebuild_use_the_same_journal(self) -> None:
        database = str(Path(self.tempdir.name) / "cli.sqlite")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main(["--db", database, "demo"]), 0)
        demo_rows = json.loads(output.getvalue())
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main(["--db", database, "rebuild"]), 0)
        self.assertEqual(demo_rows, json.loads(output.getvalue()))
        self.assertEqual(demo_rows[0]["disposition"], "candidate")

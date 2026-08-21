from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

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

    def test_manual_selection_is_projected_without_replacing_auto_route(self) -> None:
        self.spine.create_work_item("work-manual", "Manual route test")
        event = self.spine.create_task_packet(
            "task-manual", "work-manual", "implement a bounded feature", manual_route_id="daybreak-blue-personal"
        )
        payload = event["payload"]
        self.assertEqual(payload["routing_receipt"]["selected"]["id"], "chatgpt-codex-direct")
        self.assertEqual(payload["routing_receipt"]["model_advisory"]["recommended_model"], "gpt-5.6-terra")
        self.assertEqual(payload["manual_selection"]["selected"]["id"], "daybreak-blue-personal")
        rows = self.spine.rebuild_read_model()
        manual = next(row for row in rows if row["task_id"] == "task-manual")
        self.assertEqual(manual["manual_selection_sha256"], payload["manual_selection"]["decision_sha256"])

    def test_invalid_manual_selection_does_not_append_task_event(self) -> None:
        before = len(self.spine.journal_events())
        with self.assertRaisesRegex(TaskSpineError, "unknown route"):
            self.spine.create_task_packet("task-invalid", "work-1", "do work", manual_route_id="missing-route")
        self.assertEqual(len(self.spine.journal_events()), before)

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

    def test_late_result_is_preserved_but_does_not_change_sealed_wip(self) -> None:
        self.spine.append_worker_buffer("buffer-1", "task-1", "record-1", "on-time")
        seal = self.spine.seal_worker_buffer("buffer-1")
        late = self.spine.append_worker_buffer("buffer-1", "task-1", "record-2", "late")
        self.assertEqual(late["kind"], "worker_buffer.late_result")
        self.assertEqual(late["payload"]["disposition"], "late_result")
        self.assertEqual(self.spine.rebuild_read_model()[0]["wip_buffer_sha256"], seal["payload"]["buffer_sha256"])

    def test_rejected_and_needs_repair_envelopes_cannot_be_proposed(self) -> None:
        self.spine.append_worker_buffer("buffer-1", "task-1", "record-1", "report")
        self.spine.seal_worker_buffer("buffer-1")
        for status in ("rejected", "needs_repair"):
            envelope_id = f"envelope-{status}"
            self.spine.seal_result_envelope(envelope_id, "task-1", "buffer-1", "artifact:report", status)
            with self.assertRaisesRegex(TaskSpineError, "only a complete"):
                self.spine.create_import_proposal(f"proposal-{status}", "task-1", envelope_id)

    def test_envelope_amendment_preserves_original_and_can_be_admitted(self) -> None:
        self.spine.append_worker_buffer("buffer-1", "task-1", "record-1", "report")
        self.spine.seal_worker_buffer("buffer-1")
        self.spine.seal_result_envelope("envelope-1", "task-1", "buffer-1", "artifact:report-v1", "needs_repair")
        amended = self.spine.amend_result_envelope("envelope-1", "envelope-2", "artifact:report-v2", "repaired")
        self.assertEqual(amended["payload"]["amends_envelope_id"], "envelope-1")
        self.spine.create_import_proposal("proposal-1", "task-1", "envelope-2")
        authorization = self.spine.authorize_import("proposal-1", "lead-1")
        self.spine.admit_candidate("proposal-1", actor="trusted_writer", admission_basis_sha256=authorization["event_sha256"])
        self.assertEqual(self.spine.rebuild_read_model()[0]["candidate_envelope_id"], "envelope-2")

    def test_revoked_and_expired_admission_leases_fail_closed(self) -> None:
        self._sealed_path()
        lease = self.spine.acquire_admission_lease("lease-1", "proposal-1", "lead-1", event_ttl=4)
        revoked = self.spine.revoke_admission_lease("lease-1", actor="trusted_writer")
        with self.assertRaisesRegex(TaskSpineError, "revoked admission lease"):
            self.spine.admit_candidate("proposal-1", actor="trusted_writer",
                                       admission_basis_sha256=revoked["event_sha256"], lease_id="lease-1")
        self.assertEqual(lease["payload"]["proposal_id"], "proposal-1")
        self.spine.acquire_admission_lease("lease-2", "proposal-1", "lead-1", event_ttl=1)
        intervening = self.spine.create_work_item("work-2", "Advance the logical event clock")
        with self.assertRaisesRegex(TaskSpineError, "expired admission lease"):
            self.spine.admit_candidate("proposal-1", actor="trusted_writer",
                                       admission_basis_sha256=intervening["event_sha256"], lease_id="lease-2")

    def test_interrupted_rebuild_keeps_previous_projection(self) -> None:
        before = self.spine.rebuild_read_model()
        self.spine.append_worker_buffer("buffer-1", "task-1", "record-1", "report")
        self.spine.seal_worker_buffer("buffer-1")
        with self.assertRaisesRegex(TaskSpineError, "simulated interruption"):
            self.spine.rebuild_read_model(interrupt_before_swap=True)
        self.assertEqual(self.spine.read_model(), before)
        after = self.spine.rebuild_read_model()
        self.assertNotEqual(after, before)

from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from house.task_spine import TaskSpine, TaskSpineError, prepare_submission, submit_task
from house.task_spine.cli import main


def submission(**overrides: object) -> dict[str, object]:
    packet: dict[str, object] = {
        "schema": "codex-house-task-submission/1",
        "idempotency_key": "request-1",
        "requested_by": "human:tiga",
        "title": "Review commercial app training features",
        "summary": "do we need research for new features to review in the commercial app for training",
    }
    packet.update(overrides)
    return packet


class TaskSubmissionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.database = Path(self.tempdir.name) / "submission.sqlite"
        self.spine = TaskSpine(self.database)

    def tearDown(self) -> None:
        self.spine.close()
        self.tempdir.cleanup()

    def test_exact_retry_returns_stored_receipt_without_new_event(self) -> None:
        first = submit_task(self.spine, submission())
        event_count = len(self.spine.journal_events())
        second = submit_task(self.spine, submission())
        self.assertEqual(first, second)
        self.assertEqual(len(self.spine.journal_events()), event_count)
        self.assertEqual(first["dispatch"], "NOT_ATTEMPTED")
        self.assertEqual(first["requester_identity_state"], "ASSERTED_UNVERIFIED")

    def test_idempotency_key_reuse_with_changed_content_fails_closed(self) -> None:
        submit_task(self.spine, submission())
        with self.assertRaisesRegex(TaskSpineError, "different content"):
            submit_task(self.spine, submission(summary="a different request"))

    def test_partial_work_creation_is_reconciled(self) -> None:
        prepared = prepare_submission(submission())
        self.spine.create_work_item(prepared["work_id"], prepared["title"])
        receipt = submit_task(self.spine, submission())
        self.assertEqual(receipt["state"], "RESUMED_PARTIAL")
        self.assertEqual(len(self.spine.journal_events("work_item.created")), 1)
        self.assertEqual(len(self.spine.journal_events("task_packet.created")), 1)

    def test_ambiguous_prompt_is_compound_and_continues_without_dispatch(self) -> None:
        receipt = submit_task(self.spine, submission())
        self.assertEqual(receipt["case_type"], "compound")
        task_event = self.spine.journal_events("task_packet.created")[0]
        routing = task_event["payload"]["routing_receipt"]
        self.assertEqual(routing["next_action"], "DECOMPOSE_WITHOUT_BLOCKING")
        self.assertEqual(routing["dispatch"], "NOT_ATTEMPTED")

    def test_unknown_fields_and_invalid_case_type_are_rejected(self) -> None:
        with self.assertRaisesRegex(TaskSpineError, "unknown task-submission fields"):
            submit_task(self.spine, submission(secret_model_hint="pick the expensive one"))
        with self.assertRaisesRegex(TaskSpineError, "unknown case_type"):
            submit_task(self.spine, submission(case_type="make_it_magic"))

    def test_manual_daybreak_selection_is_separate_from_auto_advisory(self) -> None:
        receipt = submit_task(self.spine, submission(
            summary="implement a bounded Python feature with tests",
            case_type="app_delivery",
            manual_route_id="daybreak-blue-personal",
        ))
        task_event = self.spine.journal_events("task_packet.created")[0]
        payload = task_event["payload"]
        self.assertEqual(payload["routing_receipt"]["selected"]["id"], "chatgpt-codex-direct")
        self.assertEqual(receipt["model_advisory"]["recommended_model"], "gpt-5.6-terra")
        self.assertEqual(payload["manual_selection"]["state"], "MANUAL_SELECTED")
        self.assertEqual(payload["manual_selection"]["selected"]["id"], "daybreak-blue-personal")
        self.assertEqual(payload["manual_selection"]["dispatch"], "NOT_ATTEMPTED")
        self.assertTrue(receipt["manual_selection_sha256"])

    def test_invalid_manual_route_fails_before_journal_mutation(self) -> None:
        with self.assertRaisesRegex(TaskSpineError, "not manually selectable"):
            submit_task(self.spine, submission(manual_route_id="chatgpt-codex-direct"))
        self.assertEqual(self.spine.journal_events(), [])

    def test_manual_route_is_bound_into_idempotency(self) -> None:
        submit_task(self.spine, submission())
        with self.assertRaisesRegex(TaskSpineError, "different content"):
            submit_task(self.spine, submission(manual_route_id="daybreak-blue-personal"))

    def test_cli_status_reports_advisory_without_rebuilding_or_mutating(self) -> None:
        submit_task(self.spine, submission(
            summary="implement a bounded Python feature with tests",
            case_type="app_delivery",
        ))
        before = self.spine.journal_events()
        self.spine.close()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main(["--db", str(self.database), "status"]), 0)
        cards = json.loads(output.getvalue())
        self.spine = TaskSpine(self.database)
        self.assertEqual(cards[0]["model_advisory"]["recommended_model"], "gpt-5.6-terra")
        self.assertEqual(self.spine.journal_events(), before)

    def test_cli_submit_replays_the_exact_receipt(self) -> None:
        packet_path = Path(self.tempdir.name) / "submission.json"
        packet_path.write_text(json.dumps(submission()), encoding="utf-8")
        self.spine.close()
        for expected in ("first", "replay"):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main(["--db", str(self.database), "submit", "--input", str(packet_path)]), 0)
            receipt = json.loads(output.getvalue())
            if expected == "first":
                first = receipt
            else:
                self.assertEqual(receipt, first)
        self.spine = TaskSpine(self.database)

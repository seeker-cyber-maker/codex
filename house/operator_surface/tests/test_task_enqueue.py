from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from house.operator_surface.cli import main
from house.operator_surface.task_enqueue import OperatorTaskEnqueueError, enqueue_task
from house.task_spine import TaskInbox, TaskSpine


class OperatorTaskEnqueueTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        root = Path(self.tempdir.name)
        self.inbox_path = root / "inbox.sqlite"
        self.spine_path = root / "spine.sqlite"

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def enqueue(self, **overrides: str) -> dict[str, object]:
        arguments = {
            "enqueue_id": "operator-request-1",
            "requested_by": "human:tiga",
            "title": "Review queued task gateway",
            "summary": "verify the dashboard and terminal task submission path",
            "recipient": "specific_model",
            "recipient_id": "chatgpt-codex-direct",
            "case_type": "app_delivery",
        }
        arguments.update(overrides)
        return enqueue_task(self.inbox_path, **arguments)

    def test_enqueue_replays_exactly_then_controller_preserves_recipient(self) -> None:
        first = self.enqueue()
        second = self.enqueue()
        self.assertEqual(first, second)
        self.assertEqual(first["state"], "QUEUED")
        self.assertEqual(first["controller"], "NOT_ATTEMPTED")
        self.assertEqual(first["dispatch"], "NOT_ATTEMPTED")

        inbox = TaskInbox(self.inbox_path)
        spine = TaskSpine(self.spine_path)
        try:
            self.assertEqual(len(inbox.entries()), 1)
            lease = inbox.acquire_controller("local-controller", ttl_seconds=30)
            accepted = inbox.drain_once(
                spine, holder=lease["holder"], fencing_token=lease["fencing_token"]
            )
            self.assertEqual(accepted["state"], "ACCEPTED")
            packet = spine.journal_events("task_packet.created")[0]["payload"]
            self.assertEqual(packet["requested_recipient"], "specific_model")
            self.assertEqual(packet["requested_recipient_id"], "chatgpt-codex-direct")
            card = spine.task_cards()[0]
            self.assertEqual(card["requested_recipient"], "specific_model")
            self.assertEqual(card["requested_recipient_id"], "chatgpt-codex-direct")
        finally:
            inbox.close()
            spine.close()

    def test_changed_enqueue_content_and_invalid_recipient_fail_before_new_row(
        self,
    ) -> None:
        self.enqueue()
        with self.assertRaisesRegex(OperatorTaskEnqueueError, "different content"):
            self.enqueue(summary="a different objective")
        with self.assertRaisesRegex(OperatorTaskEnqueueError, "requires recipient_id"):
            self.enqueue(enqueue_id="operator-request-2", recipient_id="")
        inbox = TaskInbox(self.inbox_path)
        try:
            self.assertEqual(len(inbox.entries()), 1)
        finally:
            inbox.close()

    def test_cli_queues_typed_request_without_dispatch(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exit_code = main(
                [
                    "enqueue-task",
                    "--inbox-db",
                    str(self.inbox_path),
                    "--enqueue-id",
                    "cli-request-1",
                    "--requested-by",
                    "human:tiga",
                    "--title",
                    "CLI queue task",
                    "--summary",
                    "queue this task through the shared operator command inventory",
                    "--recipient",
                    "reviewer",
                ]
            )
        receipt = json.loads(output.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(receipt["state"], "QUEUED")
        self.assertEqual(receipt["requested_recipient"], "reviewer")
        self.assertEqual(receipt["dispatch"], "NOT_ATTEMPTED")

    def test_raw_inbox_cannot_bypass_task_schema_on_controller_admission(self) -> None:
        inbox = TaskInbox(self.inbox_path)
        spine = TaskSpine(self.spine_path)
        try:
            inbox.enqueue("bad", {"schema": "wrong"})
            lease = inbox.acquire_controller("local-controller", ttl_seconds=30)
            receipt = inbox.drain_once(
                spine, holder=lease["holder"], fencing_token=lease["fencing_token"]
            )
            self.assertEqual(receipt["state"], "REJECTED")
            self.assertEqual(spine.journal_events(), [])
        finally:
            inbox.close()
            spine.close()


if __name__ == "__main__":
    unittest.main()

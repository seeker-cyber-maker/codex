from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from house.task_spine import (
    SimulatedControllerInterrupt,
    TaskInbox,
    TaskInboxError,
    TaskSpine,
)
from house.task_spine.controller_cli import main


def submission(**overrides: object) -> dict[str, object]:
    packet: dict[str, object] = {
        "schema": "codex-house-task-submission/1",
        "idempotency_key": "request-1",
        "requested_by": "human:tiga",
        "title": "Continue the Dream House build",
        "summary": "implement the next finite offline controller slice",
    }
    packet.update(overrides)
    return packet


class TaskInboxTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        root = Path(self.tempdir.name)
        self.inbox_path = root / "inbox.sqlite"
        self.spine_path = root / "spine.sqlite"
        self.now = 100.0
        self.inbox = TaskInbox(self.inbox_path, clock=lambda: self.now)
        self.spine = TaskSpine(self.spine_path)

    def tearDown(self) -> None:
        self.inbox.close()
        self.spine.close()
        self.tempdir.cleanup()

    def test_exact_enqueue_replays_and_changed_content_fails_closed(self) -> None:
        first = self.inbox.enqueue("enqueue-1", submission())
        second = self.inbox.enqueue("enqueue-1", submission())
        self.assertEqual(first, second)
        self.assertEqual(len(self.inbox.entries()), 1)
        with self.assertRaisesRegex(TaskInboxError, "different content"):
            self.inbox.enqueue("enqueue-1", submission(summary="different"))

    def test_active_lease_excludes_takeover_and_stale_token_is_rejected(self) -> None:
        first = self.inbox.acquire_controller("controller-a", ttl_seconds=10)
        self.now = 105
        with self.assertRaisesRegex(TaskInboxError, "already active"):
            self.inbox.acquire_controller("controller-b", ttl_seconds=10)
        self.now = 111
        second = self.inbox.acquire_controller("controller-b", ttl_seconds=10)
        self.assertEqual(first["epoch"], 1)
        self.assertEqual(second["epoch"], 2)
        self.inbox.enqueue("enqueue-1", submission())
        with self.assertRaisesRegex(TaskInboxError, "stale controller fencing token"):
            self.inbox.drain_once(
                self.spine, holder="controller-a", fencing_token="token-a"
            )

    def test_drain_once_is_fifo_finite_and_does_not_dispatch(self) -> None:
        self.inbox.enqueue("enqueue-1", submission())
        self.inbox.enqueue(
            "enqueue-2", submission(idempotency_key="request-2", title="Second task")
        )
        lease = self.inbox.acquire_controller("controller", ttl_seconds=30)
        first = self.inbox.drain_once(
            self.spine,
            holder=lease["holder"],
            fencing_token=lease["fencing_token"],
        )
        self.assertEqual(first["enqueue_id"], "enqueue-1")
        self.assertEqual(first["state"], "ACCEPTED")
        self.assertEqual(first["dispatch"], "NOT_ATTEMPTED")
        self.assertEqual(len(first["receipt_sha256"]), 64)
        self.assertEqual(
            [entry["state"] for entry in self.inbox.entries()], ["ACCEPTED", "QUEUED"]
        )

    def test_invalid_submission_is_rejected_without_journal_mutation(self) -> None:
        self.inbox.enqueue("bad", {"schema": "wrong"})
        lease = self.inbox.acquire_controller("controller", ttl_seconds=30)
        receipt = self.inbox.drain_once(
            self.spine,
            holder=lease["holder"],
            fencing_token=lease["fencing_token"],
        )
        self.assertEqual(receipt["state"], "REJECTED")
        self.assertEqual(receipt["error_type"], "TASK_SUBMISSION_REJECTED")
        self.assertEqual(self.spine.journal_events(), [])

    def test_interrupted_acceptance_reconciles_without_duplicate_events(self) -> None:
        self.inbox.enqueue("enqueue-1", submission())
        first_lease = self.inbox.acquire_controller("controller-a", ttl_seconds=10)
        with self.assertRaisesRegex(
            SimulatedControllerInterrupt, "simulated interruption"
        ):
            self.inbox.drain_once(
                self.spine,
                holder=first_lease["holder"],
                fencing_token=first_lease["fencing_token"],
                simulate_interrupt_after_submit=True,
            )
        accepted_events = len(self.spine.journal_events())
        stored_receipt = self.spine.journal_events("task_submission.accepted")[0][
            "payload"
        ]["receipt"]
        self.assertEqual(self.inbox.entries()[0]["state"], "QUEUED")
        self.now = 111
        second_lease = self.inbox.acquire_controller("controller-b", ttl_seconds=10)
        reconciled = self.inbox.drain_once(
            self.spine,
            holder=second_lease["holder"],
            fencing_token=second_lease["fencing_token"],
        )
        self.assertEqual(reconciled["task_receipt"], stored_receipt)
        self.assertEqual(len(self.spine.journal_events()), accepted_events)
        self.assertEqual(self.inbox.entries()[0]["state"], "ACCEPTED")

    def test_expiry_before_terminal_commit_rolls_back_inbox_for_reconciliation(
        self,
    ) -> None:
        self.inbox.enqueue("enqueue-1", submission())
        self.now = 90
        first_lease = self.inbox.acquire_controller("controller-a", ttl_seconds=15)
        self.inbox._clock = mock.Mock(side_effect=[100, 111])
        with self.assertRaisesRegex(TaskInboxError, "lease has expired"):
            self.inbox.drain_once(
                self.spine,
                holder=first_lease["holder"],
                fencing_token=first_lease["fencing_token"],
            )
        event_count = len(self.spine.journal_events())
        self.assertEqual(self.inbox.entries()[0]["state"], "QUEUED")
        self.now = 112
        self.inbox._clock = lambda: self.now
        second_lease = self.inbox.acquire_controller("controller-b", ttl_seconds=15)
        reconciled = self.inbox.drain_once(
            self.spine,
            holder=second_lease["holder"],
            fencing_token=second_lease["fencing_token"],
        )
        self.assertEqual(reconciled["state"], "ACCEPTED")
        self.assertEqual(len(self.spine.journal_events()), event_count)

    def test_same_database_is_rejected_to_preserve_crash_boundary(self) -> None:
        other_inbox = TaskInbox(self.spine_path)
        try:
            with self.assertRaisesRegex(TaskInboxError, "must be separate"):
                other_inbox.drain_once(
                    self.spine, holder="controller", fencing_token="token"
                )
        finally:
            other_inbox.close()

    def test_cli_enqueue_lease_drain_and_status(self) -> None:
        packet_path = Path(self.tempdir.name) / "submission.json"
        packet_path.write_text(json.dumps(submission()), encoding="utf-8")
        self.inbox.close()
        self.spine.close()

        def invoke(arguments: list[str]) -> object:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main(arguments), 0)
            return json.loads(output.getvalue())

        base = ["--inbox-db", str(self.inbox_path)]
        queued = invoke(
            [*base, "enqueue", "--enqueue-id", "cli-1", "--input", str(packet_path)]
        )
        lease = invoke([*base, "lease", "--holder", "cli-controller", "--ttl", "30"])
        accepted = invoke(
            [
                *base,
                "drain-once",
                "--spine-db",
                str(self.spine_path),
                "--holder",
                "cli-controller",
                "--token",
                lease["fencing_token"],
            ]
        )
        status = invoke([*base, "status"])
        self.assertEqual(queued["state"], "QUEUED")
        self.assertEqual(accepted["state"], "ACCEPTED")
        self.assertEqual(status[0]["state"], "ACCEPTED")
        self.inbox = TaskInbox(self.inbox_path, clock=lambda: self.now)
        self.spine = TaskSpine(self.spine_path)


if __name__ == "__main__":
    unittest.main()

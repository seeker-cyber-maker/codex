from __future__ import annotations

import unittest

from house.worker_exec import (
    MockAdmissionError,
    prepare_mock_execution_authority,
    prepare_mock_runtime_profile,
    verify_mock_admission,
)


class MockAdmissionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.operation_id = "operation-1"
        self.record_sha256 = "a" * 64
        self.profile = prepare_mock_runtime_profile(
            profile_id="profile-1",
            operation_id=self.operation_id,
            record_sha256=self.record_sha256,
        )
        self.authority = prepare_mock_execution_authority(
            authority_id="authority-1", profile=self.profile
        )

    def test_mock_only_records_prove_no_process_admission(self) -> None:
        receipt = verify_mock_admission(
            operation_id=self.operation_id,
            record_sha256=self.record_sha256,
            requested_recipient="triage",
            profile=self.profile,
            authority=self.authority,
        )
        self.assertEqual(receipt["state"], "MOCK_ADMISSION_VERIFIED_NO_PROCESS")
        self.assertEqual(receipt["dispatch"], "NOT_ATTEMPTED")
        self.assertIsNone(self.profile["executable"])
        self.assertEqual(self.profile["egress"], [])

    def test_any_runtime_field_tamper_or_task_model_request_fails_closed(self) -> None:
        changed = {**self.profile, "environment": {"HOME": "/tmp"}}
        with self.assertRaisesRegex(MockAdmissionError, "hash mismatch"):
            verify_mock_admission(
                operation_id=self.operation_id,
                record_sha256=self.record_sha256,
                requested_recipient="triage",
                profile=changed,
                authority=self.authority,
            )
        with self.assertRaisesRegex(MockAdmissionError, "not execution authority"):
            verify_mock_admission(
                operation_id=self.operation_id,
                record_sha256=self.record_sha256,
                requested_recipient="specific_model",
                profile=self.profile,
                authority=self.authority,
            )

    def test_authority_mismatch_and_runtime_model_selection_fail_closed(self) -> None:
        changed = {**self.authority, "model_identity": "gpt-5.6-sol"}
        with self.assertRaisesRegex(MockAdmissionError, "hash mismatch"):
            verify_mock_admission(
                operation_id=self.operation_id,
                record_sha256=self.record_sha256,
                requested_recipient="triage",
                profile=self.profile,
                authority=changed,
            )
        with self.assertRaisesRegex(MockAdmissionError, "binding mismatch"):
            verify_mock_admission(
                operation_id="operation-2",
                record_sha256=self.record_sha256,
                requested_recipient="triage",
                profile=self.profile,
                authority=self.authority,
            )

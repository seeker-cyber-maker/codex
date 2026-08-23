from __future__ import annotations

import unittest

from house.worker_exec import (
    MockVaultError,
    create_mock_vault_ref_v1,
    prepare_mock_audit_failure_incident_v1,
    prepare_mock_resolver_exposure_v1,
    prepare_mock_vault_frontend_profile_v1,
    prepare_mock_vault_lease_v1,
    verify_mock_vault_lease_v1,
)


class MockVaultTests(unittest.TestCase):
    def setUp(self) -> None:
        self.reference = create_mock_vault_ref_v1(
            ref_id="vr_0123456789abcdef",
            scope_class="environment",
            required_sink="provider_header",
            revision=1,
        )
        self.lease = prepare_mock_vault_lease_v1(
            self.reference,
            lease_id="vl_0123456789abcdef",
            operation_id="operation-1",
            worker_id="worker-1",
            plan_sha256="a" * 64,
            authority_receipt_sha256="b" * 64,
            target_class="qualified_consumer",
        )

    def test_lease_is_non_resolvable_and_contains_no_plaintext(self) -> None:
        verified = verify_mock_vault_lease_v1(self.reference, self.lease)
        self.assertEqual(verified["state"], "MOCK_LEASE_NOT_RESOLVABLE")
        self.assertEqual(verified["plaintext"], "ABSENT")
        self.assertEqual(verified["authority"], "NOT_GRANTED")

    def test_01_agent_shell_sink_is_rejected(self) -> None:
        with self.assertRaisesRegex(MockVaultError, "agent-controlled"):
            prepare_mock_vault_lease_v1(
                self.reference,
                lease_id="vl_0123456789abcdef",
                operation_id="operation-1",
                worker_id="worker-1",
                plan_sha256="a" * 64,
                authority_receipt_sha256="b" * 64,
                target_class="agent_shell",
            )

    def test_02_frontend_has_no_key_or_plaintext_access(self) -> None:
        frontend = prepare_mock_vault_frontend_profile_v1(frontend_id="frontend-1")
        self.assertEqual(frontend["storage_key_access"], "FORBIDDEN")
        self.assertEqual(frontend["plaintext"], "ABSENT")

    def test_03_resolver_compromise_is_namespace_wide(self) -> None:
        exposure = prepare_mock_resolver_exposure_v1(
            namespace_id="namespace-1",
            reference_ids=["vr_0123456789abcdef", "vr_0123456789abcdea"],
        )
        self.assertEqual(exposure["exposure"], "NAMESPACE_EXPOSED")
        self.assertEqual(exposure["required_action"], "ROTATION_REQUIRED")

    def test_04_audit_failure_distinguishes_pre_and_post_injection(self) -> None:
        pre = prepare_mock_audit_failure_incident_v1(self.lease, phase="PRE_INJECTION")
        post = prepare_mock_audit_failure_incident_v1(
            self.lease, phase="POST_INJECTION_AUDIT_FAILURE"
        )
        self.assertEqual(pre["exposure"], "NOT_EXPOSED")
        self.assertEqual(post["exposure"], "POSSIBLE_EXPOSURE")
        self.assertEqual(post["required_action"], "TERMINATE_AND_ROTATE_REQUIRED")

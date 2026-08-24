from __future__ import annotations

import ast
import inspect
import json
import os
import tempfile
import unittest
from pathlib import Path

from house.worker_exec.vault_protocol_mock import (
    AtomicNonceLedger,
    GeneratedVaultStorage,
    MockControllerKey,
    MockKeyringStore,
    ResolverPolicyV1,
    VaultProtocolMockError,
    ZeroizingBuffer,
    classify_crash_v1,
    create_resolve_intent_v1,
    validate_policy_and_claim_v1,
)


class VaultProtocolMockTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = 1_800_000_000_000
        self.intent = create_resolve_intent_v1(
            operation_id="operation-1",
            plan_sha256="a" * 64,
            task_sha256="b" * 64,
            worker_sha256="c" * 64,
            authority_receipt_sha256="d" * 64,
            ref_id="vr_0123456789abcdef",
            minimum_revision=2,
            namespace_id="provider-alpha",
            vault_epoch=3,
            audience="api-alpha",
            sink_kind="provider_header",
            sink_instance_sha256="e" * 64,
            nonce="vn_0123456789abcdefghijklmn",
            created_at_ms=self.now - 1_000,
            ttl_seconds=60,
        )
        self.controller = MockControllerKey(b"C" * 32)
        self.ticket = self.controller.sign_ticket(
            self.intent,
            issued_at_ms=self.now - 500,
            expires_at_ms=self.now + 30_000,
        )
        self.policy = ResolverPolicyV1(
            operation_id="operation-1",
            plan_sha256="a" * 64,
            task_sha256="b" * 64,
            worker_sha256="c" * 64,
            authority_receipt_sha256="d" * 64,
            ref_id="vr_0123456789abcdef",
            namespace_id="provider-alpha",
            current_epoch=3,
            current_revision=2,
            audience="api-alpha",
            sink_kind="provider_header",
            sink_instance_sha256="e" * 64,
        )

    def test_01_ticket_binds_complete_intent_and_rejects_tampering(self) -> None:
        tampered = dict(self.intent)
        tampered["audience"] = "api-beta"
        with tempfile.TemporaryDirectory() as temporary:
            ledger = AtomicNonceLedger(Path(temporary))
            with self.assertRaisesRegex(VaultProtocolMockError, "hash mismatch"):
                validate_policy_and_claim_v1(
                    tampered,
                    self.ticket,
                    controller_key=self.controller,
                    policy=self.policy,
                    ledger=ledger,
                    now_ms=self.now,
                )

    def test_02_local_deny_wins_over_valid_controller_signature(self) -> None:
        denied = ResolverPolicyV1(**{**self.policy.__dict__, "incident_locked": True})
        with tempfile.TemporaryDirectory() as temporary:
            ledger = AtomicNonceLedger(Path(temporary))
            with self.assertRaisesRegex(VaultProtocolMockError, "incident lock"):
                validate_policy_and_claim_v1(
                    self.intent,
                    self.ticket,
                    controller_key=self.controller,
                    policy=denied,
                    ledger=ledger,
                    now_ms=self.now,
                )
            self.assertEqual(list(Path(temporary).iterdir()), [])

    def test_03_nonce_is_claimed_once_before_any_storage_step(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            ledger = AtomicNonceLedger(Path(temporary))
            receipt = validate_policy_and_claim_v1(
                self.intent,
                self.ticket,
                controller_key=self.controller,
                policy=self.policy,
                ledger=ledger,
                now_ms=self.now,
            )
            self.assertEqual(receipt["state"], "CLAIMED_BEFORE_STORAGE_ACCESS")
            with self.assertRaisesRegex(VaultProtocolMockError, "already claimed"):
                validate_policy_and_claim_v1(
                    self.intent,
                    self.ticket,
                    controller_key=self.controller,
                    policy=self.policy,
                    ledger=ledger,
                    now_ms=self.now,
                )

    def test_04_expired_ticket_fails_without_claim(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            ledger = AtomicNonceLedger(Path(temporary))
            with self.assertRaisesRegex(VaultProtocolMockError, "expired"):
                validate_policy_and_claim_v1(
                    self.intent,
                    self.ticket,
                    controller_key=self.controller,
                    policy=self.policy,
                    ledger=ledger,
                    now_ms=self.now + 31_000,
                )
            self.assertEqual(list(Path(temporary).iterdir()), [])

    def test_05_only_qualified_v1_sinks_are_accepted(self) -> None:
        values = {
            "operation_id": "operation-1",
            "plan_sha256": "a" * 64,
            "task_sha256": "b" * 64,
            "worker_sha256": "c" * 64,
            "authority_receipt_sha256": "d" * 64,
            "ref_id": "vr_0123456789abcdef",
            "minimum_revision": 1,
            "namespace_id": "provider-alpha",
            "vault_epoch": 1,
            "audience": "api-alpha",
            "sink_instance_sha256": "e" * 64,
            "nonce": "vn_1123456789abcdefghijklmn",
            "created_at_ms": self.now,
            "ttl_seconds": 60,
        }
        for sink in ("qualified_process_env", "agent_shell", "clipboard", "file"):
            with (
                self.subTest(sink=sink),
                self.assertRaisesRegex(VaultProtocolMockError, "not qualified"),
            ):
                create_resolve_intent_v1(sink_kind=sink, **values)

    def test_06_generated_storage_uses_independent_keys_and_safe_modes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "store"
            keyring = MockKeyringStore()
            keyring.generate("provider-alpha", 1)
            keyring.generate("provider-alpha", 2)
            keyring.generate("provider-beta", 1)
            self.assertTrue(
                keyring.keys_are_distinct_for_test(
                    ("provider-alpha", 1), ("provider-alpha", 2)
                )
            )
            self.assertTrue(
                keyring.keys_are_distinct_for_test(
                    ("provider-alpha", 1), ("provider-beta", 1)
                )
            )
            store = GeneratedVaultStorage(root, keyring)
            value = ZeroizingBuffer(b"GENERATED_CANARY_ONLY:alpha")
            path = store.put_generated(
                namespace_id="provider-alpha",
                epoch=1,
                ref_id="vr_0123456789abcdef",
                revision=1,
                value=value,
            )
            self.assertTrue(value.cleared)
            self.assertTrue(
                store.verify_generated_for_test(
                    namespace_id="provider-alpha",
                    epoch=1,
                    ref_id="vr_0123456789abcdef",
                    expected=b"GENERATED_CANARY_ONLY:alpha",
                )
            )
            self.assertEqual(os.stat(root).st_mode & 0o777, 0o700)
            self.assertEqual(os.stat(path.parent).st_mode & 0o777, 0o700)
            self.assertEqual(os.stat(path).st_mode & 0o777, 0o600)
            self.assertNotIn(b"GENERATED_CANARY_ONLY", path.read_bytes())

    def test_07_store_rejects_unmarked_values_and_corruption(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            keyring = MockKeyringStore()
            keyring.generate("provider-alpha", 1)
            store = GeneratedVaultStorage(Path(temporary), keyring)
            with self.assertRaisesRegex(VaultProtocolMockError, "generated canaries"):
                store.put_generated(
                    namespace_id="provider-alpha",
                    epoch=1,
                    ref_id="vr_0123456789abcdef",
                    revision=1,
                    value=ZeroizingBuffer(b"ordinary-value"),
                )
            value = ZeroizingBuffer(b"GENERATED_CANARY_ONLY:alpha")
            path = store.put_generated(
                namespace_id="provider-alpha",
                epoch=1,
                ref_id="vr_0123456789abcdef",
                revision=1,
                value=value,
            )
            payload = json.loads(path.read_text())
            payload["schema"] = "codex-house-generated-vault-store/99"
            path.write_text(json.dumps(payload))
            with self.assertRaisesRegex(VaultProtocolMockError, "unsupported"):
                store.verify_generated_for_test(
                    namespace_id="provider-alpha",
                    epoch=1,
                    ref_id="vr_0123456789abcdef",
                    expected=b"GENERATED_CANARY_ONLY:alpha",
                )

    def test_08_wrong_namespace_or_epoch_key_never_rewrites_store(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            original_keys = MockKeyringStore()
            original_keys.generate("provider-alpha", 1)
            store = GeneratedVaultStorage(root, original_keys)
            value = ZeroizingBuffer(b"GENERATED_CANARY_ONLY:alpha")
            path = store.put_generated(
                namespace_id="provider-alpha",
                epoch=1,
                ref_id="vr_0123456789abcdef",
                revision=1,
                value=value,
            )
            before = path.read_bytes()
            wrong_keys = MockKeyringStore()
            wrong_keys.generate("provider-alpha", 1)
            wrong_store = GeneratedVaultStorage(root, wrong_keys)
            with self.assertRaisesRegex(
                VaultProtocolMockError, "authentication failed"
            ):
                wrong_store.verify_generated_for_test(
                    namespace_id="provider-alpha",
                    epoch=1,
                    ref_id="vr_0123456789abcdef",
                    expected=b"GENERATED_CANARY_ONLY:alpha",
                )
            self.assertEqual(path.read_bytes(), before)

    def test_09_rotation_epoch_denies_old_ticket(self) -> None:
        rotated = ResolverPolicyV1(**{**self.policy.__dict__, "current_epoch": 4})
        with (
            tempfile.TemporaryDirectory() as temporary,
            self.assertRaisesRegex(VaultProtocolMockError, "vault_epoch"),
        ):
            validate_policy_and_claim_v1(
                self.intent,
                self.ticket,
                controller_key=self.controller,
                policy=rotated,
                ledger=AtomicNonceLedger(Path(temporary)),
                now_ms=self.now,
            )

    def test_09b_rotation_retains_tombstone_and_destroys_old_key(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            keyring = MockKeyringStore()
            keyring.generate("provider-alpha", 1)
            store = GeneratedVaultStorage(root, keyring)
            old = ZeroizingBuffer(b"GENERATED_CANARY_ONLY:old")
            old_path = store.put_generated(
                namespace_id="provider-alpha",
                epoch=1,
                ref_id="vr_0123456789abcdef",
                revision=1,
                value=old,
            )
            old_ciphertext = old_path.read_bytes()
            new = ZeroizingBuffer(b"GENERATED_CANARY_ONLY:new")
            receipt = store.rotate_generated(
                namespace_id="provider-alpha",
                old_epoch=1,
                new_epoch=2,
                ref_id="vr_0123456789abcdef",
                old_revision=1,
                new_revision=2,
                new_value=new,
            )
            self.assertEqual(receipt["old_leases"], "INVALIDATED")
            self.assertEqual(old_path.read_bytes(), old_ciphertext)
            self.assertTrue(new.cleared)
            self.assertTrue(
                store.verify_generated_for_test(
                    namespace_id="provider-alpha",
                    epoch=2,
                    ref_id="vr_0123456789abcdef",
                    expected=b"GENERATED_CANARY_ONLY:new",
                )
            )
            with self.assertRaisesRegex(
                VaultProtocolMockError, "authentication failed"
            ):
                store.verify_generated_for_test(
                    namespace_id="provider-alpha",
                    epoch=1,
                    ref_id="vr_0123456789abcdef",
                    expected=b"GENERATED_CANARY_ONLY:old",
                )
            tombstones = list((root / "rotation-tombstones").iterdir())
            self.assertEqual(len(tombstones), 1)
            self.assertEqual(os.stat(tombstones[0]).st_mode & 0o777, 0o600)

    def test_10_crash_exposure_is_monotonic_and_conservative(self) -> None:
        pre = classify_crash_v1(last_durable_state="SINK_BOUND")
        attempted = classify_crash_v1(last_durable_state="DELIVERY_ATTEMPTED")
        uncertain = classify_crash_v1(
            last_durable_state="PREPARED", state_uncertain=True
        )
        self.assertEqual(pre["exposure"], "NOT_EXPOSED")
        self.assertEqual(attempted["exposure"], "POSSIBLE_EXPOSURE")
        self.assertEqual(uncertain["exposure"], "POSSIBLE_EXPOSURE")
        self.assertIn("ROTATE", attempted["required_action"])

    def test_11_public_package_does_not_export_plaintext_or_storage_api(self) -> None:
        import house.worker_exec as public_api

        forbidden = {
            "GeneratedVaultStorage",
            "get_secret",
            "get_plaintext",
            "resolve_plaintext",
            "put_generated",
            "verify_generated_for_test",
        }
        self.assertTrue(forbidden.isdisjoint(set(public_api.__all__)))

    def test_12_fixture_has_no_live_runtime_or_ambient_secret_api(self) -> None:
        from house.worker_exec import vault_protocol_mock

        source = inspect.getsource(vault_protocol_mock)
        tree = ast.parse(source)
        imported_roots = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in node.names
        }
        self.assertTrue(
            {"socket", "subprocess", "keyring", "requests", "urllib"}.isdisjoint(
                imported_roots
            )
        )
        self.assertNotIn("os.environ", source)
        self.assertNotIn("Keychain", source.replace("macOS Keychain", ""))


if __name__ == "__main__":
    unittest.main()

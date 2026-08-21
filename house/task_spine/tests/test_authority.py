from __future__ import annotations

import base64
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from cryptography.hazmat.primitives.asymmetric import ec

from house.task_spine.authority import (
    AuthorityRegistry,
    AuthorizedTaskInbox,
)
from house.task_spine.authority_crypto import (
    AuthorityError,
    enqueue_binding,
    key_id_for_public_key,
    revocation_binding,
    sign_proof,
)
from house.task_spine.inbox import TaskInbox


def submission(**overrides: object) -> dict[str, object]:
    packet: dict[str, object] = {
        "schema": "codex-house-task-submission/1",
        "idempotency_key": "signed-request-1",
        "requested_by": "human:tiga",
        "title": "Signed offline task",
        "summary": "verify the local authority boundary",
    }
    packet.update(overrides)
    return packet


class AuthorityRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        root = Path(self.tempdir.name)
        self.authority_path = root / "authority.sqlite"
        self.inbox_path = root / "inbox.sqlite"
        self.now = 1_800_000_000
        self.registry = AuthorityRegistry(self.authority_path, clock=lambda: self.now)
        self.inbox = TaskInbox(self.inbox_path, clock=lambda: self.now)
        self.authorized = AuthorizedTaskInbox(self.registry, self.inbox)
        self.private_key = ec.generate_private_key(ec.SECP256R1())
        self.key_id = key_id_for_public_key(self.private_key.public_key())
        self.registry.bootstrap_key(
            "principal-owner",
            self.private_key.public_key(),
            ["inbox.enqueue", "authority.revoke"],
            reason="offline fixture bootstrap",
        )
        self.nonce_index = 0

    def tearDown(self) -> None:
        self.registry.close()
        self.inbox.close()
        self.tempdir.cleanup()

    def proof(
        self,
        action: str,
        binding_sha256: str,
        *,
        private_key: ec.EllipticCurvePrivateKey | None = None,
        principal_id: str = "principal-owner",
        issued_at: int | None = None,
        expires_at: int | None = None,
    ) -> dict[str, object]:
        self.nonce_index += 1
        issued = self.now if issued_at is None else issued_at
        return sign_proof(
            self.private_key if private_key is None else private_key,
            principal_id=principal_id,
            action=action,
            binding_sha256=binding_sha256,
            nonce=f"nonce-{self.nonce_index:010d}",
            issued_at=issued,
            expires_at=issued + 60 if expires_at is None else expires_at,
        )

    def test_valid_proof_enqueues_once_and_preserves_signer_receipt(self) -> None:
        packet = submission()
        binding = enqueue_binding("enqueue-1", packet)
        receipt = self.authorized.enqueue(
            self.proof("inbox.enqueue", binding),
            enqueue_id="enqueue-1",
            submission=packet,
        )
        self.assertEqual(receipt["principal_id"], "principal-owner")
        self.assertEqual(receipt["key_id"], self.key_id)
        self.assertEqual(receipt["state"], "QUEUED")
        self.assertEqual(receipt["dispatch"], "NOT_ATTEMPTED")
        self.assertEqual(len(self.inbox.entries()), 1)
        self.assertEqual(
            len(self.registry.journal_events("authority.proof.accepted")), 1
        )
        self.assertTrue(self.registry.verify_journal())

    def test_tamper_wrong_action_and_unknown_fields_fail_without_enqueue(self) -> None:
        packet = submission()
        binding = enqueue_binding("enqueue-1", packet)
        tampered = submission(summary="changed after signing")
        with self.assertRaisesRegex(AuthorityError, "binding"):
            self.authorized.enqueue(
                self.proof("inbox.enqueue", binding),
                enqueue_id="enqueue-1",
                submission=tampered,
            )
        wrong_action = self.proof("authority.revoke", binding)
        with self.assertRaisesRegex(AuthorityError, "action"):
            self.authorized.enqueue(
                wrong_action, enqueue_id="enqueue-1", submission=packet
            )
        extra = self.proof("inbox.enqueue", binding)
        extra["model_hint"] = "ignore the gate"
        with self.assertRaisesRegex(AuthorityError, "unknown fields"):
            self.authorized.enqueue(extra, enqueue_id="enqueue-1", submission=packet)
        self.assertEqual(self.inbox.entries(), [])
        self.assertEqual(
            len(self.registry.journal_events("authority.proof.rejected")), 3
        )

    def test_invalid_signature_unknown_key_and_principal_mismatch_fail(self) -> None:
        packet = submission()
        binding = enqueue_binding("enqueue-1", packet)
        invalid = self.proof("inbox.enqueue", binding)
        invalid["signature_b64"] = base64.b64encode(b"x" * 70).decode()
        with self.assertRaisesRegex(AuthorityError, "signature"):
            self.authorized.enqueue(invalid, enqueue_id="enqueue-1", submission=packet)
        other_key = ec.generate_private_key(ec.SECP256R1())
        unknown = self.proof("inbox.enqueue", binding, private_key=other_key)
        with self.assertRaisesRegex(AuthorityError, "not enrolled"):
            self.authorized.enqueue(unknown, enqueue_id="enqueue-1", submission=packet)
        mismatch = self.proof("inbox.enqueue", binding, principal_id="principal-other")
        with self.assertRaisesRegex(AuthorityError, "does not own"):
            self.authorized.enqueue(mismatch, enqueue_id="enqueue-1", submission=packet)
        self.assertEqual(self.inbox.entries(), [])

    def test_expired_future_and_overlong_proofs_fail_closed(self) -> None:
        packet = submission()
        binding = enqueue_binding("enqueue-1", packet)
        expired = self.proof(
            "inbox.enqueue", binding, issued_at=self.now - 120, expires_at=self.now
        )
        with self.assertRaisesRegex(AuthorityError, "expired"):
            self.authorized.enqueue(expired, enqueue_id="enqueue-1", submission=packet)
        future = self.proof("inbox.enqueue", binding, issued_at=self.now + 6)
        with self.assertRaisesRegex(AuthorityError, "future"):
            self.authorized.enqueue(future, enqueue_id="enqueue-1", submission=packet)
        overlong = self.proof(
            "inbox.enqueue", binding, issued_at=self.now, expires_at=self.now + 301
        )
        with self.assertRaisesRegex(AuthorityError, "five minutes"):
            self.authorized.enqueue(overlong, enqueue_id="enqueue-1", submission=packet)
        self.assertEqual(self.inbox.entries(), [])

    def test_nonce_replay_fails_but_new_proof_retries_enqueue_idempotently(
        self,
    ) -> None:
        packet = submission()
        binding = enqueue_binding("enqueue-1", packet)
        proof = self.proof("inbox.enqueue", binding)
        first = self.authorized.enqueue(
            proof, enqueue_id="enqueue-1", submission=packet
        )
        with self.assertRaisesRegex(AuthorityError, "already accepted"):
            self.authorized.enqueue(proof, enqueue_id="enqueue-1", submission=packet)
        second = self.authorized.enqueue(
            self.proof("inbox.enqueue", binding),
            enqueue_id="enqueue-1",
            submission=packet,
        )
        self.assertEqual(first["inbox_entry"], second["inbox_entry"])
        self.assertEqual(len(self.inbox.entries()), 1)
        self.assertEqual(
            len(self.registry.journal_events("authority.proof.accepted")), 2
        )

    def test_revocation_is_atomic_and_blocks_later_proofs(self) -> None:
        reason = "rotate the offline fixture key"
        proof = self.proof("authority.revoke", revocation_binding(self.key_id, reason))
        revoked = self.registry.revoke_key(
            proof, target_key_id=self.key_id, reason=reason
        )
        self.assertEqual(revoked["payload"]["target_key_id"], self.key_id)
        events = self.registry.journal_events()
        self.assertEqual(events[-2]["kind"], "authority.proof.accepted")
        self.assertEqual(events[-1]["kind"], "authority.key.revoked")
        self.assertTrue(self.registry.key_status()[0]["revoked"])
        packet = submission()
        with self.assertRaisesRegex(AuthorityError, "revoked"):
            self.authorized.enqueue(
                self.proof("inbox.enqueue", enqueue_binding("enqueue-1", packet)),
                enqueue_id="enqueue-1",
                submission=packet,
            )
        self.assertEqual(self.inbox.entries(), [])

    def test_failed_revocation_rolls_back_proof_acceptance(self) -> None:
        unknown_key_id = "p256:" + "0" * 64
        reason = "unknown target fixture"
        proof = self.proof(
            "authority.revoke", revocation_binding(unknown_key_id, reason)
        )
        accepted_before = len(self.registry.journal_events("authority.proof.accepted"))
        with self.assertRaisesRegex(AuthorityError, "target is unknown"):
            self.registry.revoke_key(proof, target_key_id=unknown_key_id, reason=reason)
        self.assertEqual(
            len(self.registry.journal_events("authority.proof.accepted")),
            accepted_before,
        )
        self.assertEqual(
            self.registry.journal_events()[-1]["payload"]["error_code"], "UNKNOWN_KEY"
        )

    def test_action_permission_is_enforced_after_signature_verification(self) -> None:
        restricted_path = Path(self.tempdir.name) / "restricted-authority.sqlite"
        restricted = AuthorityRegistry(restricted_path, clock=lambda: self.now)
        restricted_key = ec.generate_private_key(ec.SECP256R1())
        try:
            restricted.bootstrap_key(
                "principal-restricted",
                restricted_key.public_key(),
                ["inbox.enqueue"],
                reason="permission fixture",
            )
            target = key_id_for_public_key(restricted_key.public_key())
            reason = "permission should deny this revocation"
            proof = sign_proof(
                restricted_key,
                principal_id="principal-restricted",
                action="authority.revoke",
                binding_sha256=revocation_binding(target, reason),
                nonce="restricted-nonce-0001",
                issued_at=self.now,
                expires_at=self.now + 60,
            )
            with self.assertRaisesRegex(AuthorityError, "not permitted"):
                restricted.revoke_key(proof, target_key_id=target, reason=reason)
            self.assertFalse(restricted.key_status()[0]["revoked"])
        finally:
            restricted.close()

    def test_new_proof_recovers_after_post_authorization_enqueue_failure(self) -> None:
        packet = submission()
        binding = enqueue_binding("enqueue-1", packet)
        with (
            mock.patch.object(
                self.inbox, "enqueue", side_effect=RuntimeError("fixture")
            ),
            self.assertRaisesRegex(RuntimeError, "fixture"),
        ):
            self.authorized.enqueue(
                self.proof("inbox.enqueue", binding),
                enqueue_id="enqueue-1",
                submission=packet,
            )
        self.assertEqual(self.inbox.entries(), [])
        recovered = self.authorized.enqueue(
            self.proof("inbox.enqueue", binding),
            enqueue_id="enqueue-1",
            submission=packet,
        )
        self.assertEqual(recovered["state"], "QUEUED")
        self.assertEqual(
            len(self.registry.journal_events("authority.proof.accepted")), 2
        )
        self.assertEqual(len(self.inbox.entries()), 1)

    def test_second_bootstrap_and_corrupted_journal_fail_closed(self) -> None:
        other_key = ec.generate_private_key(ec.SECP256R1())
        with self.assertRaisesRegex(AuthorityError, "already bootstrapped"):
            self.registry.bootstrap_key(
                "principal-other",
                other_key.public_key(),
                ["inbox.enqueue"],
                reason="must not create a second root",
            )
        self.registry.db.execute(
            "UPDATE authority_journal SET payload_json = ? WHERE sequence = 1",
            (json.dumps({"corrupted": True}),),
        )
        self.registry.db.commit()
        with self.assertRaisesRegex(AuthorityError, "journal event hash mismatch"):
            self.registry.verify_journal()


if __name__ == "__main__":
    unittest.main()

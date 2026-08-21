from __future__ import annotations

import unittest

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

from house.task_spine.authority_crypto import (
    PROOF_FIELDS,
    AuthorityError,
    canonical,
    decode_signature,
    enqueue_binding,
    load_public_key,
    prepare_unsigned_proof,
    public_key_der,
    sign_proof,
)


class AuthorityCryptoTests(unittest.TestCase):
    def test_signed_canonical_proof_verifies_with_derived_public_key(self) -> None:
        private_key = ec.generate_private_key(ec.SECP256R1())
        proof = sign_proof(
            private_key,
            principal_id="principal-fixture",
            action="inbox.enqueue",
            binding_sha256=enqueue_binding("enqueue-1", {"value": 1}),
            nonce="known-answer-0001",
            issued_at=1_800_000_000,
            expires_at=1_800_000_060,
        )
        unsigned = {field: proof[field] for field in PROOF_FIELDS - {"signature_b64"}}
        public_key = load_public_key(public_key_der(private_key.public_key()))
        public_key.verify(
            decode_signature(proof["signature_b64"]),
            canonical(unsigned).encode(),
            ec.ECDSA(hashes.SHA256()),
        )

    def test_binding_is_canonical_and_changes_with_target_or_content(self) -> None:
        first = enqueue_binding("enqueue-1", {"a": 1, "b": 2})
        reordered = enqueue_binding("enqueue-1", {"b": 2, "a": 1})
        changed_target = enqueue_binding("enqueue-2", {"a": 1, "b": 2})
        changed_content = enqueue_binding("enqueue-1", {"a": 1, "b": 3})
        self.assertEqual(first, reordered)
        self.assertNotEqual(first, changed_target)
        self.assertNotEqual(first, changed_content)

    def test_invalid_curve_nonce_and_timestamp_range_fail_closed(self) -> None:
        with self.assertRaisesRegex(AuthorityError, "P-256"):
            sign_proof(
                ec.generate_private_key(ec.SECP384R1()),
                principal_id="principal-fixture",
                action="inbox.enqueue",
                binding_sha256="0" * 64,
                nonce="known-answer-0001",
                issued_at=1,
                expires_at=2,
            )
        valid = sign_proof(
            ec.generate_private_key(ec.SECP256R1()),
            principal_id="principal-fixture",
            action="inbox.enqueue",
            binding_sha256="0" * 64,
            nonce="known-answer-0002",
            issued_at=1,
            expires_at=2,
        )
        unsigned = {field: valid[field] for field in PROOF_FIELDS - {"signature_b64"}}
        unsigned["nonce"] = "short"
        with self.assertRaisesRegex(AuthorityError, "nonce"):
            prepare_unsigned_proof(unsigned)
        unsigned["nonce"] = "known-answer-0003"
        unsigned["issued_at"] = -1
        with self.assertRaisesRegex(AuthorityError, "supported range"):
            prepare_unsigned_proof(unsigned)


if __name__ == "__main__":
    unittest.main()

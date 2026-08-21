from __future__ import annotations

import copy
import hashlib
import json
import unittest

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

from house.authority_stage0.canonical import canonical_bytes
from house.authority_stage0.profile import (
    ProfileError,
    b64u_decode,
    decode_strict_signature,
    load_p256_spki,
    verify_vector_record,
)
from house.authority_stage0.vector_tool import (
    NEGATIVE_FIXTURE,
    POSITIVE_FIXTURE,
    check_fixtures,
    generate_positive,
)
from house.authority_stage0.verify import verify_openssl, verify_pure


class VectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(POSITIVE_FIXTURE.read_text(encoding="utf-8"))

    def test_exact_deterministic_regeneration(self) -> None:
        self.assertEqual(self.record, generate_positive())
        check_fixtures()

    def test_candidate_and_pure_verifiers_accept(self) -> None:
        result = verify_vector_record(self.record)
        self.assertEqual(result["vector_id"], self.record["vector_id"])
        verify_pure(self.record)

    def test_cryptography_accepts_directly(self) -> None:
        key, _ = load_p256_spki(self.record["public_spki_der_b64u"])
        signature, _, _ = decode_strict_signature(self.record["signature_der_b64u"])
        key.verify(
            signature,
            canonical_bytes(self.record["unsigned_object"]),
            ec.ECDSA(hashes.SHA256()),
        )

    def test_openssl_accepts_directly(self) -> None:
        verify_openssl(self.record)

    def test_all_explicit_negative_records_reject_as_declared(self) -> None:
        records = json.loads(NEGATIVE_FIXTURE.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(records), 10)
        for record in records:
            with self.subTest(vector_id=record["vector_id"]):
                with self.assertRaises(ProfileError) as caught:
                    verify_vector_record(record)
                self.assertEqual(caught.exception.code, record["expected_error"])

    def test_every_binding_field_changes_digest_and_breaks_signature(self) -> None:
        mutations = {
            "registry_id": "ffeeddccbbaa99887766554433221100",
            "generation": 8,
            "deployment_id": "ffeeddccbbaa99887766554433221100",
            "policy_sha256": "44" * 32,
            "principal_id": "owner:other-test",
            "key_epoch": 4,
            "action": "authority.rotate-key",
            "binding_sha256": "55" * 32,
            "challenge": "Dw4NDAsKCQgHBgUEAwIBAA",
            "issued_at": 1787335201,
            "expires_at": 1787335499,
        }
        original_digest = self.record["sha256_hex"]
        signature = b64u_decode(self.record["signature_der_b64u"])
        key, _ = load_p256_spki(self.record["public_spki_der_b64u"])
        for field, value in mutations.items():
            with self.subTest(field=field):
                changed = copy.deepcopy(self.record["unsigned_object"])
                changed[field] = value
                canonical = canonical_bytes(changed)
                self.assertNotEqual(
                    hashlib.sha256(canonical).hexdigest(), original_digest
                )
                with self.assertRaises(InvalidSignature):
                    key.verify(signature, canonical, ec.ECDSA(hashes.SHA256()))


if __name__ == "__main__":
    unittest.main()

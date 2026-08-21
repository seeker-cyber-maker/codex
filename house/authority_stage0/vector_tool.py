"""Deterministically generate the frozen Stage 0 software vectors."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from .canonical import canonical_bytes
from .p256 import (
    N,
    derive_test_scalar,
    encode_der_signature,
    scalar_multiply,
    sign_digest,
    verify_digest,
)
from .profile import (
    ALGORITHM,
    CONTEXT,
    SCHEMA,
    VECTOR_SCHEMA,
    b64u_decode,
    b64u_encode,
    key_id_for_spki,
    verify_vector_record,
)

TEST_KEY_LABEL = b"codex-house-stage0-test-only-key-v1"
FIXTURE_DIR = Path(__file__).with_name("fixtures")
POSITIVE_FIXTURE = FIXTURE_DIR / "software_positive.json"
NEGATIVE_FIXTURE = FIXTURE_DIR / "software_negative.json"


def _public_material(private_scalar: int) -> tuple[tuple[int, int], bytes]:
    point = scalar_multiply(private_scalar)
    if point is None:
        raise AssertionError("nonzero scalar produced point at infinity")
    private_key = ec.derive_private_key(private_scalar, ec.SECP256R1())
    numbers = private_key.public_key().public_numbers()
    if (numbers.x, numbers.y) != point:
        raise AssertionError("pure-Python and cryptography public points differ")
    spki = private_key.public_key().public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return point, spki


def generate_positive() -> dict[str, Any]:
    """Return the exact reproducible, explicitly test-only software vector."""

    private_scalar = derive_test_scalar(TEST_KEY_LABEL)
    public_point, spki = _public_material(private_scalar)
    key_id = key_id_for_spki(spki)
    unsigned = {
        "schema": SCHEMA,
        "algorithm": ALGORITHM,
        "context": CONTEXT,
        "registry_id": "00112233445566778899aabbccddeeff",
        "generation": 7,
        "deployment_id": "102132435465768798a9bacbdcedfe0f",
        "policy_sha256": "11" * 32,
        "principal_id": "owner:stage0-test",
        "key_id": key_id,
        "key_epoch": 3,
        "action": "authority.exit-lockdown",
        "binding_sha256": "22" * 32,
        "challenge": b64u_encode(bytes(range(16))),
        "issued_at": 1787335200,
        "expires_at": 1787335500,
    }
    canonical = canonical_bytes(unsigned)
    digest = hashlib.sha256(canonical).digest()
    r, s = sign_digest(private_scalar, digest)
    if not verify_digest(public_point, digest, r, s):
        raise AssertionError("pure-Python signature self-verification failed")
    signature = encode_der_signature(r, s)
    record = {
        "vector_schema": VECTOR_SCHEMA,
        "vector_id": "stage0-software-rfc6979-p256-v1",
        "disposition": "accept",
        "unsigned_object": unsigned,
        "canonical_utf8_hex": canonical.hex(),
        "sha256_hex": digest.hex(),
        "public_spki_der_b64u": b64u_encode(spki),
        "key_id": key_id,
        "signature_der_b64u": b64u_encode(signature),
        "r_hex": f"{r:064x}",
        "s_hex": f"{s:064x}",
        "expected_error": None,
        "test_private_scalar_hex": f"{private_scalar:064x}",
        "test_key_label_utf8": TEST_KEY_LABEL.decode("ascii"),
        "provenance": {
            "generator": "house.authority_stage0.vector_tool",
            "deterministic_nonce": "RFC6979-HMAC-SHA256",
            "independent_verifiers": ["cryptography-45.0.7", "OpenSSL-3.5.6"],
            "hardware": None,
            "warning": "PUBLIC TEST KEY - NEVER USE FOR AUTHORITY",
        },
    }
    verify_vector_record(record)
    return record


def _rebind(record: dict[str, Any]) -> None:
    canonical = canonical_bytes(record["unsigned_object"])
    record["canonical_utf8_hex"] = canonical.hex()
    record["sha256_hex"] = hashlib.sha256(canonical).hexdigest()


def _negative(
    positive: dict[str, Any],
    vector_id: str,
    expected_error: str,
) -> dict[str, Any]:
    record = copy.deepcopy(positive)
    record["vector_id"] = vector_id
    record["disposition"] = "reject"
    record["expected_error"] = expected_error
    return record


def generate_negatives(positive: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Return explicit malformed and cross-binding records."""

    base = positive or generate_positive()
    records: list[dict[str, Any]] = []

    padded = _negative(base, "reject-padded-signature", "PROFILE_SIGNATURE_B64U")
    padded["signature_der_b64u"] += "="
    records.append(padded)

    trailing = _negative(base, "reject-trailing-der", "PROFILE_SIGNATURE_DER")
    signature = b64u_decode(trailing["signature_der_b64u"])
    trailing["signature_der_b64u"] = b64u_encode(signature + b"\x00")
    records.append(trailing)

    high_s = _negative(base, "reject-high-s", "PROFILE_SIGNATURE_HIGH_S")
    r = int(high_s["r_hex"], 16)
    high = N - int(high_s["s_hex"], 16)
    high_s["s_hex"] = f"{high:064x}"
    high_s["signature_der_b64u"] = b64u_encode(encode_der_signature(r, high))
    records.append(high_s)

    malformed = _negative(base, "reject-malformed-der", "PROFILE_SIGNATURE_DER")
    malformed["signature_der_b64u"] = b64u_encode(b"\x30\x01\x00")
    records.append(malformed)

    unknown = _negative(base, "reject-unknown-unsigned-field", "PROFILE_FIELDS")
    unknown["unsigned_object"]["surprise"] = True
    records.append(unknown)

    missing = _negative(base, "reject-missing-unsigned-field", "PROFILE_FIELDS")
    del missing["unsigned_object"]["action"]
    records.append(missing)

    domain = _negative(base, "reject-wrong-domain", "PROFILE_CONTEXT")
    domain["unsigned_object"]["context"] = "codex-house/authority-command/v1"
    _rebind(domain)
    records.append(domain)

    action = _negative(base, "reject-wrong-action-binding", "VECTOR_SIGNATURE")
    action["unsigned_object"]["action"] = "authority.rotate-key"
    _rebind(action)
    records.append(action)

    binding = _negative(base, "reject-wrong-content-binding", "VECTOR_SIGNATURE")
    binding["unsigned_object"]["binding_sha256"] = "33" * 32
    _rebind(binding)
    records.append(binding)

    wrong_key = _negative(base, "reject-other-signing-key", "VECTOR_SIGNATURE")
    other_scalar = derive_test_scalar(b"codex-house-stage0-other-test-only-key-v1")
    _, other_spki = _public_material(other_scalar)
    other_id = key_id_for_spki(other_spki)
    wrong_key["public_spki_der_b64u"] = b64u_encode(other_spki)
    wrong_key["key_id"] = other_id
    wrong_key["unsigned_object"]["key_id"] = other_id
    _rebind(wrong_key)
    records.append(wrong_key)

    changed_canonical = _negative(base, "reject-changed-canonical", "VECTOR_CANONICAL")
    changed_canonical["canonical_utf8_hex"] = (
        "00" + changed_canonical["canonical_utf8_hex"][2:]
    )
    records.append(changed_canonical)

    return records


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def check_fixtures() -> None:
    expected_positive = _json(generate_positive())
    expected_negative = _json(generate_negatives())
    if POSITIVE_FIXTURE.read_text(encoding="utf-8") != expected_positive:
        raise SystemExit("positive fixture differs from deterministic regeneration")
    if NEGATIVE_FIXTURE.read_text(encoding="utf-8") != expected_negative:
        raise SystemExit("negative fixture differs from deterministic regeneration")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("positive", "negative", "check"))
    args = parser.parse_args()
    if args.mode == "positive":
        print(_json(generate_positive()), end="")
    elif args.mode == "negative":
        print(_json(generate_negatives()), end="")
    else:
        check_fixtures()
        print("fixtures: exact")


if __name__ == "__main__":
    main()

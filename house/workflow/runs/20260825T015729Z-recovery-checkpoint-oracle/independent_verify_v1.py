#!/usr/bin/env python3
"""Independent public-only verifier for the frozen F1 fixture."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import (
    decode_dss_signature,
    encode_dss_signature,
)

N = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_json(value: object) -> str:
    return sha(canonical(value))


def b64u(value: str) -> bytes:
    if not value or "=" in value:
        raise AssertionError("noncanonical base64url")
    raw = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    if base64.urlsafe_b64encode(raw).decode().rstrip("=") != value:
        raise AssertionError("noncanonical base64url round trip")
    return raw


def without(value: dict[str, Any], field: str) -> dict[str, Any]:
    return {key: item for key, item in value.items() if key != field}


def expected_receipt(
    unsigned: dict[str, Any],
    assertion_sha256: str,
    descriptor: dict[str, Any],
    summary: dict[str, Any],
) -> dict[str, Any]:
    base = {
        "schema": "codex-house-synthetic-recovery-checkpoint-receipt/1",
        "result": "VERIFIED",
        "code": "SYNTHETIC_CHECKPOINT_BINDINGS_VERIFIED",
        "claim_ceiling": "SYNTHETIC_SIGNED_RECOVERY_CHECKPOINT_AND_EXPECTED_DIGEST_BINDINGS_ONLY",
        "checkpoint_binding_sha256": unsigned["checkpoint_binding_sha256"],
        "assertion_sha256": assertion_sha256,
        "descriptor_sha256": descriptor["descriptor_sha256"],
        "summary_sha256": summary["summary_sha256"],
        "recovery_principal_id": unsigned["recovery_principal_id"],
        "recovery_key_id": unsigned["recovery_key_id"],
        "recovery_key_epoch": unsigned["recovery_key_epoch"],
        "expected_descriptor_source_class": "CALLER_SUPPLIED_NOT_VERIFIED",
        "ledger_summary_source_class": "CALLER_SUPPLIED_SYNTHETIC_LEDGER_SUMMARY",
        "authority": "NOT_GRANTED",
        "dispatch": "NOT_ATTEMPTED",
        "hardware": "NOT_ACCESSED",
        "key_material": "NOT_ACCESSED",
        "runtime_admission": "NOT_ATTEMPTED",
        "checkpoint_protection": "NOT_ESTABLISHED",
        "checkpoint_latest": "NOT_ESTABLISHED",
        "recovery_readiness": "NOT_ESTABLISHED",
    }
    return {**base, "receipt_sha256": sha_json(base)}


def verify(root: Path) -> dict[str, Any]:
    fixture = json.loads((root / "fixture.json").read_bytes())
    if fixture["warning"] != "PUBLIC TEST EVIDENCE - NEVER AUTHORITY":
        raise AssertionError("fixture warning missing")
    envelope = fixture["signed_checkpoint_envelope"]
    unsigned = envelope["unsigned_checkpoint"]
    descriptor = fixture["expected_descriptor"]
    summary = fixture["ledger_summary"]
    receipt = fixture["expected_receipt"]
    intermediates = fixture["intermediates"]

    binding_input = without(unsigned, "checkpoint_binding_sha256")
    binding_bytes = canonical(binding_input)
    if sha(binding_bytes) != unsigned["checkpoint_binding_sha256"]:
        raise AssertionError("checkpoint binding mismatch")
    unsigned_bytes = canonical(unsigned)
    envelope_bytes = canonical(envelope)
    assertion_sha256 = sha(envelope_bytes)

    exact_files = {
        "unsigned_checkpoint.canonical.json": unsigned_bytes,
        "signed_checkpoint_envelope.canonical.json": envelope_bytes,
        "expected_descriptor.canonical.json": canonical(descriptor),
        "ledger_summary.canonical.json": canonical(summary),
        "expected_receipt.canonical.json": canonical(receipt),
    }
    for name, expected in exact_files.items():
        if (root / name).read_bytes() != expected:
            raise AssertionError(f"exact canonical file mismatch: {name}")

    if intermediates != {
        "checkpoint_binding_input_canonical_utf8_hex": binding_bytes.hex(),
        "checkpoint_binding_sha256": sha(binding_bytes),
        "unsigned_checkpoint_canonical_utf8_hex": unsigned_bytes.hex(),
        "unsigned_checkpoint_sha256": sha(unsigned_bytes),
        "signed_envelope_canonical_utf8_hex": envelope_bytes.hex(),
        "assertion_sha256": assertion_sha256,
        "public_spki_sha256": sha((root / "public_spki.der").read_bytes()),
        "r_hex": intermediates["r_hex"],
        "s_hex": intermediates["s_hex"],
    }:
        raise AssertionError("intermediate canonical or digest mismatch")

    spki = b64u(envelope["public_spki_der_b64u"])
    signature = b64u(envelope["signature_der_b64u"])
    if spki != (root / "public_spki.der").read_bytes():
        raise AssertionError("SPKI file mismatch")
    if signature != (root / "signature.der").read_bytes():
        raise AssertionError("signature file mismatch")
    key = serialization.load_der_public_key(spki)
    if not isinstance(key, ec.EllipticCurvePublicKey) or not isinstance(
        key.curve, ec.SECP256R1
    ):
        raise AssertionError("public key is not P-256")
    if key.public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ) != spki:
        raise AssertionError("SPKI is not canonical DER")
    key_id = f"p256:{sha(spki)}"
    if unsigned["recovery_key_id"] != key_id:
        raise AssertionError("content-derived key ID mismatch")
    r, s = decode_dss_signature(signature)
    if encode_dss_signature(r, s) != signature:
        raise AssertionError("signature DER is not strict")
    if not (1 <= r < N and 1 <= s <= N // 2):
        raise AssertionError("signature components out of range or high-S")
    if intermediates["r_hex"] != f"{r:064x}" or intermediates["s_hex"] != f"{s:064x}":
        raise AssertionError("signature component receipt mismatch")
    try:
        key.verify(signature, unsigned_bytes, ec.ECDSA(hashes.SHA256()))
    except InvalidSignature as exc:
        raise AssertionError("signature verification failed") from exc

    if sha_json(without(descriptor, "descriptor_sha256")) != descriptor[
        "descriptor_sha256"
    ]:
        raise AssertionError("descriptor self-digest mismatch")
    if sha_json(without(summary, "summary_sha256")) != summary["summary_sha256"]:
        raise AssertionError("summary self-digest mismatch")
    if descriptor["assertion_sha256"] != assertion_sha256:
        raise AssertionError("complete-envelope assertion mismatch")

    three_way = (
        "registry_id",
        "generation",
        "policy_sha256",
        "ledger_schema",
        "initial_state_sha256",
        "genesis_sha256",
        "current_state_sha256",
        "event_head_sha256",
        "entry_count",
        "consumed_challenges_sha256",
        "ceremony_id",
        "ceremony_parent_sha256",
        "fencing_epoch",
    )
    for field in three_way:
        if not unsigned[field] == descriptor[field] == summary[field]:
            raise AssertionError(f"three-way binding mismatch: {field}")
    checkpoint_descriptor = (
        "recovery_principal_id",
        "recovery_key_id",
        "recovery_key_epoch",
        "checkpoint_id",
        "checkpoint_sequence",
        "predecessor_checkpoint_sha256",
        "checkpoint_binding_sha256",
    )
    for field in checkpoint_descriptor:
        if unsigned[field] != descriptor[field]:
            raise AssertionError(f"checkpoint/descriptor mismatch: {field}")
    if descriptor["source_class"] != "CALLER_SUPPLIED_NOT_VERIFIED":
        raise AssertionError("descriptor source class mismatch")
    if summary["source_class"] != "CALLER_SUPPLIED_SYNTHETIC_LEDGER_SUMMARY":
        raise AssertionError("summary source class mismatch")
    if receipt != expected_receipt(unsigned, assertion_sha256, descriptor, summary):
        raise AssertionError("whole expected receipt mismatch")

    return {
        "schema": "codex-house-recovery-checkpoint-independent-verification/1",
        "result": "PASS",
        "fixture_sha256": sha((root / "fixture.json").read_bytes()),
        "assertion_sha256": assertion_sha256,
        "recovery_key_id": key_id,
        "receipt_sha256": receipt["receipt_sha256"],
        "authority": "NOT_GRANTED",
        "real_key_material": "NOT_ACCESSED",
        "hardware": "NOT_ACCESSED",
        "recovery_readiness": "NOT_ESTABLISHED",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture_root", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.fixture_root), sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()

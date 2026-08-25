#!/usr/bin/env python3
"""Generate one deterministic public checkpoint oracle; never authority."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import platform
from pathlib import Path
from typing import Any

import cryptography
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from house.authority_stage0.p256 import (
    N,
    derive_test_scalar,
    encode_der_signature,
    scalar_multiply,
    sign_digest,
    verify_digest,
)

WARNING = "PUBLIC TEST EVIDENCE - NEVER AUTHORITY"
TEST_KEY_LABEL = b"codex-house-recovery-checkpoint-public-test-key-v1"
RUN_ROOT = Path(__file__).resolve().parent


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_json(value: object) -> str:
    return sha256_bytes(canonical_bytes(value))


def label_digest(label: str) -> str:
    return hashlib.sha256(f"codex-house-fixture:{label}".encode()).hexdigest()


def b64u(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def with_digest(value: dict[str, Any], field: str) -> dict[str, Any]:
    result = dict(value)
    result[field] = sha256_json(result)
    return result


def public_material(private_scalar: int) -> tuple[bytes, tuple[int, int]]:
    point = scalar_multiply(private_scalar)
    if point is None:
        raise AssertionError("synthetic scalar produced point at infinity")
    key = ec.derive_private_key(private_scalar, ec.SECP256R1())
    numbers = key.public_key().public_numbers()
    if (numbers.x, numbers.y) != point:
        raise AssertionError("donor and cryptography public points disagree")
    spki = key.public_key().public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return spki, point


def build_fixture() -> tuple[dict[str, Any], dict[str, bytes]]:
    private_scalar = derive_test_scalar(TEST_KEY_LABEL)
    spki, public_point = public_material(private_scalar)
    key_id = f"p256:{sha256_bytes(spki)}"

    checkpoint_base: dict[str, Any] = {
        "schema": "codex-house-synthetic-recovery-checkpoint/1",
        "algorithm": "ecdsa-p256-sha256-jcs-low-s/1",
        "context": "codex-house/recovery-checkpoint/v1",
        "registry_id": "registry:synthetic-checkpoint-fixture",
        "generation": 4,
        "policy_sha256": label_digest("policy-v4"),
        "recovery_principal_id": "principal:offline-recovery-fixture",
        "recovery_key_id": key_id,
        "recovery_key_epoch": 2,
        "checkpoint_id": "checkpoint:synthetic-sequence-3",
        "checkpoint_sequence": 3,
        "predecessor_checkpoint_sha256": label_digest("checkpoint-sequence-2"),
        "ledger_schema": "codex-house-synthetic-recovery-ledger/1",
        "initial_state_sha256": label_digest("initial-state"),
        "genesis_sha256": label_digest("ledger-genesis"),
        "current_state_sha256": label_digest("current-state-sequence-7"),
        "event_head_sha256": label_digest("event-head-sequence-7"),
        "entry_count": 7,
        "consumed_challenges_sha256": label_digest("consumed-challenges-set"),
        "ceremony_id": "ceremony:synthetic-recovery-fixture",
        "ceremony_parent_sha256": label_digest("ceremony-parent"),
        "fencing_epoch": 4,
    }
    checkpoint_binding_input = canonical_bytes(checkpoint_base)
    unsigned_checkpoint = dict(checkpoint_base)
    unsigned_checkpoint["checkpoint_binding_sha256"] = sha256_bytes(
        checkpoint_binding_input
    )
    unsigned_bytes = canonical_bytes(unsigned_checkpoint)
    unsigned_digest = hashlib.sha256(unsigned_bytes).digest()

    r, s = sign_digest(private_scalar, unsigned_digest)
    if not verify_digest(public_point, unsigned_digest, r, s):
        raise AssertionError("donor self-verification failed")
    if s > N // 2:
        raise AssertionError("donor emitted high-S signature")
    signature = encode_der_signature(r, s)

    envelope = {
        "schema": "codex-house-synthetic-recovery-checkpoint-envelope/1",
        "unsigned_checkpoint": unsigned_checkpoint,
        "public_spki_der_b64u": b64u(spki),
        "signature_der_b64u": b64u(signature),
    }
    envelope_bytes = canonical_bytes(envelope)
    assertion_sha256 = sha256_bytes(envelope_bytes)

    summary_base = {
        "schema": "codex-house-synthetic-recovery-ledger-summary/1",
        "source_class": "CALLER_SUPPLIED_SYNTHETIC_LEDGER_SUMMARY",
        "ledger_schema": checkpoint_base["ledger_schema"],
        "initial_state_sha256": checkpoint_base["initial_state_sha256"],
        "genesis_sha256": checkpoint_base["genesis_sha256"],
        "current_state_sha256": checkpoint_base["current_state_sha256"],
        "event_head_sha256": checkpoint_base["event_head_sha256"],
        "entry_count": checkpoint_base["entry_count"],
        "consumed_challenges_sha256": checkpoint_base[
            "consumed_challenges_sha256"
        ],
        "registry_id": checkpoint_base["registry_id"],
        "generation": checkpoint_base["generation"],
        "policy_sha256": checkpoint_base["policy_sha256"],
        "ceremony_id": checkpoint_base["ceremony_id"],
        "ceremony_parent_sha256": checkpoint_base["ceremony_parent_sha256"],
        "fencing_epoch": checkpoint_base["fencing_epoch"],
    }
    ledger_summary = with_digest(summary_base, "summary_sha256")

    descriptor_base = {
        "schema": "codex-house-expected-recovery-checkpoint/1",
        "source_class": "CALLER_SUPPLIED_NOT_VERIFIED",
        **{
            field: unsigned_checkpoint[field]
            for field in (
                "registry_id",
                "generation",
                "policy_sha256",
                "recovery_principal_id",
                "recovery_key_id",
                "recovery_key_epoch",
                "checkpoint_id",
                "checkpoint_sequence",
                "predecessor_checkpoint_sha256",
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
                "checkpoint_binding_sha256",
            )
        },
        "assertion_sha256": assertion_sha256,
    }
    expected_descriptor = with_digest(descriptor_base, "descriptor_sha256")

    receipt_base = {
        "schema": "codex-house-synthetic-recovery-checkpoint-receipt/1",
        "result": "VERIFIED",
        "code": "SYNTHETIC_CHECKPOINT_BINDINGS_VERIFIED",
        "claim_ceiling": "SYNTHETIC_SIGNED_RECOVERY_CHECKPOINT_AND_EXPECTED_DIGEST_BINDINGS_ONLY",
        "checkpoint_binding_sha256": unsigned_checkpoint[
            "checkpoint_binding_sha256"
        ],
        "assertion_sha256": assertion_sha256,
        "descriptor_sha256": expected_descriptor["descriptor_sha256"],
        "summary_sha256": ledger_summary["summary_sha256"],
        "recovery_principal_id": unsigned_checkpoint["recovery_principal_id"],
        "recovery_key_id": key_id,
        "recovery_key_epoch": unsigned_checkpoint["recovery_key_epoch"],
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
    expected_receipt = with_digest(receipt_base, "receipt_sha256")

    fixture = {
        "fixture_schema": "codex-house-synthetic-recovery-checkpoint-fixture/1",
        "fixture_id": "recovery-checkpoint-public-rfc6979-p256-v1",
        "disposition": "accept",
        "warning": WARNING,
        "signed_checkpoint_envelope": envelope,
        "expected_descriptor": expected_descriptor,
        "ledger_summary": ledger_summary,
        "expected_receipt": expected_receipt,
        "intermediates": {
            "checkpoint_binding_input_canonical_utf8_hex": checkpoint_binding_input.hex(),
            "checkpoint_binding_sha256": unsigned_checkpoint[
                "checkpoint_binding_sha256"
            ],
            "unsigned_checkpoint_canonical_utf8_hex": unsigned_bytes.hex(),
            "unsigned_checkpoint_sha256": unsigned_digest.hex(),
            "signed_envelope_canonical_utf8_hex": envelope_bytes.hex(),
            "assertion_sha256": assertion_sha256,
            "public_spki_sha256": sha256_bytes(spki),
            "r_hex": f"{r:064x}",
            "s_hex": f"{s:064x}",
        },
        "provenance": {
            "generator": "fixture_generator.py",
            "test_key_label_utf8": TEST_KEY_LABEL.decode("ascii"),
            "deterministic_nonce": "RFC6979-HMAC-SHA256",
            "signing_donor": "house.authority_stage0.p256",
            "candidate_import_allowed": False,
            "real_key_material": "NOT_ACCESSED",
            "hardware": "NOT_ACCESSED",
            "warning": WARNING,
        },
    }
    disclosure = {
        "schema": "codex-house-public-test-key-disclosure/1",
        "warning": WARNING,
        "test_key_label_utf8": TEST_KEY_LABEL.decode("ascii"),
        "test_private_scalar_hex": f"{private_scalar:064x}",
        "recovery_key_id": key_id,
    }
    files = {
        "fixture.json": canonical_bytes(fixture) + b"\n",
        "unsigned_checkpoint.canonical.json": unsigned_bytes,
        "signed_checkpoint_envelope.canonical.json": envelope_bytes,
        "expected_descriptor.canonical.json": canonical_bytes(expected_descriptor),
        "ledger_summary.canonical.json": canonical_bytes(ledger_summary),
        "expected_receipt.canonical.json": canonical_bytes(expected_receipt),
        "public_spki.der": spki,
        "signature.der": signature,
        "public_test_key_disclosure.json": canonical_bytes(disclosure) + b"\n",
    }
    return fixture, files


def write_fixture(output: Path) -> None:
    resolved = output.resolve()
    if resolved.parent != RUN_ROOT or resolved.name not in {"attempt-a", "attempt-b"}:
        raise SystemExit("output must be attempt-a or attempt-b directly below run root")
    if resolved.exists() and any(resolved.iterdir()):
        raise SystemExit("output directory must be absent or empty")
    resolved.mkdir(exist_ok=True)
    _fixture, files = build_fixture()
    for name, content in files.items():
        (resolved / name).write_bytes(content)
    artifacts = {
        name: {"sha256": sha256_bytes(content), "bytes": len(content)}
        for name, content in sorted(files.items())
    }
    manifest = {
        "schema": "codex-house-synthetic-recovery-checkpoint-fixture-manifest/1",
        "warning": WARNING,
        "generator": "fixture_generator.py",
        "python": platform.python_version(),
        "cryptography": cryptography.__version__,
        "artifacts": artifacts,
        "real_key_material": "NOT_ACCESSED",
        "hardware": "NOT_ACCESSED",
        "network": "NOT_ACCESSED",
    }
    (resolved / "artifact_manifest.json").write_bytes(canonical_bytes(manifest) + b"\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    write_fixture(args.output)


if __name__ == "__main__":
    main()

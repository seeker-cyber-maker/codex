#!/usr/bin/env python3
"""Closed-schema wrapper around the preserved independent V1 crypto checks."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
from pathlib import Path
from typing import Any

import independent_verify_v1 as v1

FIXTURE_FIELDS = frozenset(
    "fixture_schema fixture_id disposition warning signed_checkpoint_envelope "
    "expected_descriptor ledger_summary expected_receipt intermediates provenance".split()
)
ENVELOPE_FIELDS = frozenset(
    "schema unsigned_checkpoint public_spki_der_b64u signature_der_b64u".split()
)
UNSIGNED_FIELDS = frozenset(
    "schema algorithm context registry_id generation policy_sha256 "
    "recovery_principal_id recovery_key_id recovery_key_epoch checkpoint_id "
    "checkpoint_sequence predecessor_checkpoint_sha256 ledger_schema "
    "initial_state_sha256 genesis_sha256 current_state_sha256 event_head_sha256 "
    "entry_count consumed_challenges_sha256 ceremony_id ceremony_parent_sha256 "
    "fencing_epoch checkpoint_binding_sha256".split()
)
DESCRIPTOR_FIELDS = frozenset(
    "schema source_class registry_id generation policy_sha256 recovery_principal_id "
    "recovery_key_id recovery_key_epoch checkpoint_id checkpoint_sequence "
    "predecessor_checkpoint_sha256 ledger_schema initial_state_sha256 genesis_sha256 "
    "current_state_sha256 event_head_sha256 entry_count consumed_challenges_sha256 "
    "ceremony_id ceremony_parent_sha256 fencing_epoch checkpoint_binding_sha256 "
    "assertion_sha256 descriptor_sha256".split()
)
SUMMARY_FIELDS = frozenset(
    "schema source_class ledger_schema initial_state_sha256 genesis_sha256 "
    "current_state_sha256 event_head_sha256 entry_count consumed_challenges_sha256 "
    "registry_id generation policy_sha256 ceremony_id ceremony_parent_sha256 "
    "fencing_epoch summary_sha256".split()
)
RECEIPT_FIELDS = frozenset(
    "schema result code claim_ceiling checkpoint_binding_sha256 assertion_sha256 "
    "descriptor_sha256 summary_sha256 recovery_principal_id recovery_key_id "
    "recovery_key_epoch expected_descriptor_source_class ledger_summary_source_class "
    "authority dispatch hardware key_material runtime_admission checkpoint_protection "
    "checkpoint_latest recovery_readiness receipt_sha256".split()
)
INTERMEDIATE_FIELDS = frozenset(
    "checkpoint_binding_input_canonical_utf8_hex checkpoint_binding_sha256 "
    "unsigned_checkpoint_canonical_utf8_hex unsigned_checkpoint_sha256 "
    "signed_envelope_canonical_utf8_hex assertion_sha256 public_spki_sha256 "
    "r_hex s_hex".split()
)
PROVENANCE_FIELDS = frozenset(
    "generator test_key_label_utf8 deterministic_nonce signing_donor "
    "candidate_import_allowed real_key_material hardware warning".split()
)
DISCLOSURE_FIELDS = frozenset(
    "schema warning test_key_label_utf8 test_private_scalar_hex recovery_key_id".split()
)
MANIFEST_FIELDS = frozenset(
    "schema warning generator python cryptography artifacts real_key_material hardware network".split()
)
ARTIFACT_ENTRY_FIELDS = frozenset({"sha256", "bytes"})
HEX64 = re.compile(r"^[0-9a-f]{64}$")
KEY_ID = re.compile(r"^p256:[0-9a-f]{64}$")
WARNING = "PUBLIC TEST EVIDENCE - NEVER AUTHORITY"
EXPECTED_NAMES = frozenset(
    {
        "artifact_manifest.json",
        "fixture.json",
        "unsigned_checkpoint.canonical.json",
        "signed_checkpoint_envelope.canonical.json",
        "expected_descriptor.canonical.json",
        "ledger_summary.canonical.json",
        "expected_receipt.canonical.json",
        "public_spki.der",
        "signature.der",
        "public_test_key_disclosure.json",
    }
)


def strict_load(path: Path) -> Any:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise AssertionError(f"duplicate JSON key in {path.name}: {key}")
            result[key] = value
        return result

    return json.loads(path.read_bytes(), object_pairs_hook=pairs)


def exact(value: object, fields: frozenset[str], name: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        observed = set(value) if isinstance(value, dict) else set()
        raise AssertionError(
            f"{name} fields differ: missing={sorted(fields - observed)}, "
            f"unknown={sorted(observed - fields)}"
        )
    return value


def require_fixed(value: dict[str, Any], expected: dict[str, Any], name: str) -> None:
    for field, fixed in expected.items():
        if value[field] != fixed:
            raise AssertionError(f"{name} fixed value mismatch: {field}")


def require_exact_regular_entries(root: Path) -> None:
    observed_root = root.lstat()
    if stat.S_ISLNK(observed_root.st_mode) or not stat.S_ISDIR(observed_root.st_mode):
        raise AssertionError("fixture root is not a real directory")
    observed: set[str] = set()
    with os.scandir(root) as entries:
        for entry in entries:
            observed.add(entry.name)
            if entry.is_symlink() or not entry.is_file(follow_symlinks=False):
                raise AssertionError(f"fixture entry is not a regular file: {entry.name}")
    if observed != EXPECTED_NAMES:
        raise AssertionError(
            f"fixture entries differ: missing={sorted(EXPECTED_NAMES - observed)}, "
            f"unknown={sorted(observed - EXPECTED_NAMES)}"
        )


def verify_closed(root: Path) -> dict[str, Any]:
    require_exact_regular_entries(root)
    fixture = exact(strict_load(root / "fixture.json"), FIXTURE_FIELDS, "fixture")
    require_fixed(
        fixture,
        {
            "fixture_schema": "codex-house-synthetic-recovery-checkpoint-fixture/1",
            "fixture_id": "recovery-checkpoint-public-rfc6979-p256-v1",
            "disposition": "accept",
            "warning": WARNING,
        },
        "fixture",
    )
    envelope = exact(
        fixture["signed_checkpoint_envelope"], ENVELOPE_FIELDS, "envelope"
    )
    require_fixed(
        envelope,
        {"schema": "codex-house-synthetic-recovery-checkpoint-envelope/1"},
        "envelope",
    )
    unsigned = exact(
        envelope["unsigned_checkpoint"], UNSIGNED_FIELDS, "unsigned_checkpoint"
    )
    require_fixed(
        unsigned,
        {
            "schema": "codex-house-synthetic-recovery-checkpoint/1",
            "algorithm": "ecdsa-p256-sha256-jcs-low-s/1",
            "context": "codex-house/recovery-checkpoint/v1",
        },
        "unsigned_checkpoint",
    )
    descriptor = exact(
        fixture["expected_descriptor"], DESCRIPTOR_FIELDS, "descriptor"
    )
    require_fixed(
        descriptor,
        {
            "schema": "codex-house-expected-recovery-checkpoint/1",
            "source_class": "CALLER_SUPPLIED_NOT_VERIFIED",
        },
        "descriptor",
    )
    summary = exact(fixture["ledger_summary"], SUMMARY_FIELDS, "summary")
    require_fixed(
        summary,
        {
            "schema": "codex-house-synthetic-recovery-ledger-summary/1",
            "source_class": "CALLER_SUPPLIED_SYNTHETIC_LEDGER_SUMMARY",
        },
        "summary",
    )
    receipt = exact(fixture["expected_receipt"], RECEIPT_FIELDS, "receipt")
    require_fixed(
        receipt,
        {
            "schema": "codex-house-synthetic-recovery-checkpoint-receipt/1",
            "result": "VERIFIED",
            "code": "SYNTHETIC_CHECKPOINT_BINDINGS_VERIFIED",
            "claim_ceiling": "SYNTHETIC_SIGNED_RECOVERY_CHECKPOINT_AND_EXPECTED_DIGEST_BINDINGS_ONLY",
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
        },
        "receipt",
    )
    exact(fixture["intermediates"], INTERMEDIATE_FIELDS, "intermediates")
    provenance = exact(fixture["provenance"], PROVENANCE_FIELDS, "provenance")
    require_fixed(
        provenance,
        {
            "generator": "fixture_generator.py",
            "test_key_label_utf8": "codex-house-recovery-checkpoint-public-test-key-v1",
            "deterministic_nonce": "RFC6979-HMAC-SHA256",
            "signing_donor": "house.authority_stage0.p256",
            "candidate_import_allowed": False,
            "real_key_material": "NOT_ACCESSED",
            "hardware": "NOT_ACCESSED",
            "warning": WARNING,
        },
        "provenance",
    )

    disclosure = exact(
        strict_load(root / "public_test_key_disclosure.json"),
        DISCLOSURE_FIELDS,
        "public_test_key_disclosure",
    )
    require_fixed(
        disclosure,
        {
            "schema": "codex-house-public-test-key-disclosure/1",
            "warning": WARNING,
            "test_key_label_utf8": "codex-house-recovery-checkpoint-public-test-key-v1",
        },
        "public_test_key_disclosure",
    )
    if not isinstance(disclosure["test_private_scalar_hex"], str) or not HEX64.fullmatch(
        disclosure["test_private_scalar_hex"]
    ):
        raise AssertionError("test scalar disclosure is not fixed-width lowercase hex")
    if not isinstance(disclosure["recovery_key_id"], str) or not KEY_ID.fullmatch(
        disclosure["recovery_key_id"]
    ):
        raise AssertionError("disclosure key ID shape mismatch")
    if disclosure["recovery_key_id"] != envelope["unsigned_checkpoint"]["recovery_key_id"]:
        raise AssertionError("disclosure key ID binding mismatch")

    manifest = exact(
        strict_load(root / "artifact_manifest.json"),
        MANIFEST_FIELDS,
        "artifact_manifest",
    )
    require_fixed(
        manifest,
        {
            "schema": "codex-house-synthetic-recovery-checkpoint-fixture-manifest/1",
            "warning": WARNING,
            "generator": "fixture_generator.py",
            "python": "3.13.13",
            "cryptography": "45.0.7",
            "real_key_material": "NOT_ACCESSED",
            "hardware": "NOT_ACCESSED",
            "network": "NOT_ACCESSED",
        },
        "artifact_manifest",
    )
    artifacts = manifest["artifacts"]
    artifact_names = EXPECTED_NAMES - {"artifact_manifest.json"}
    if not isinstance(artifacts, dict) or set(artifacts) != artifact_names:
        raise AssertionError("artifact manifest names differ")
    for name in sorted(artifact_names):
        entry = exact(artifacts[name], ARTIFACT_ENTRY_FIELDS, f"artifact:{name}")
        content = (root / name).read_bytes()
        if entry != {"sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content)}:
            raise AssertionError(f"artifact manifest binding mismatch: {name}")

    result = v1.verify(root)
    result["schema_closure"] = "PASS"
    result["fixed_value_closure"] = "PASS"
    result["entry_type_closure"] = "PASS"
    result["verifier_revision"] = 3
    result["public_test_scalar_usage"] = "SCHEMA_AND_HASH_ONLY"
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture_root", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify_closed(args.fixture_root), sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Closed-schema wrapper around the preserved independent V1 crypto checks."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
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


def verify_closed(root: Path) -> dict[str, Any]:
    fixture = exact(strict_load(root / "fixture.json"), FIXTURE_FIELDS, "fixture")
    envelope = exact(
        fixture["signed_checkpoint_envelope"], ENVELOPE_FIELDS, "envelope"
    )
    exact(envelope["unsigned_checkpoint"], UNSIGNED_FIELDS, "unsigned_checkpoint")
    exact(fixture["expected_descriptor"], DESCRIPTOR_FIELDS, "descriptor")
    exact(fixture["ledger_summary"], SUMMARY_FIELDS, "summary")
    exact(fixture["expected_receipt"], RECEIPT_FIELDS, "receipt")
    exact(fixture["intermediates"], INTERMEDIATE_FIELDS, "intermediates")
    exact(fixture["provenance"], PROVENANCE_FIELDS, "provenance")

    disclosure = exact(
        strict_load(root / "public_test_key_disclosure.json"),
        DISCLOSURE_FIELDS,
        "public_test_key_disclosure",
    )
    if disclosure["warning"] != "PUBLIC TEST EVIDENCE - NEVER AUTHORITY":
        raise AssertionError("test-key disclosure warning mismatch")
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
    artifacts = manifest["artifacts"]
    expected_names = {
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
    if not isinstance(artifacts, dict) or set(artifacts) != expected_names:
        raise AssertionError("artifact manifest names differ")
    observed_names = {path.name for path in root.iterdir() if path.is_file()}
    if observed_names != expected_names | {"artifact_manifest.json"}:
        raise AssertionError("fixture directory contains unknown or missing files")
    for name in sorted(expected_names):
        entry = exact(artifacts[name], ARTIFACT_ENTRY_FIELDS, f"artifact:{name}")
        content = (root / name).read_bytes()
        if entry != {"sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content)}:
            raise AssertionError(f"artifact manifest binding mismatch: {name}")

    result = v1.verify(root)
    result["schema_closure"] = "PASS"
    result["verifier_revision"] = 2
    result["public_test_scalar_usage"] = "SCHEMA_AND_HASH_ONLY"
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture_root", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify_closed(args.fixture_root), sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()

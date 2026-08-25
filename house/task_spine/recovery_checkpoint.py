"""Pure verifier for caller-supplied synthetic recovery checkpoint bindings.

This module has no persistence or operational authority.  It validates three
already-decoded objects only; it never opens a fixture, ledger, database, key
store, clock, process, provider, or hardware device.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any, NoReturn

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

from house.authority_stage0.canonical import CanonicalError, canonical_bytes
from house.authority_stage0.profile import (
    ProfileError,
    decode_strict_signature,
    key_id_for_spki,
    load_p256_spki,
)


CLAIM_CEILING = "SYNTHETIC_SIGNED_RECOVERY_CHECKPOINT_AND_EXPECTED_DIGEST_BINDINGS_ONLY"
ENVELOPE_SCHEMA = "codex-house-synthetic-recovery-checkpoint-envelope/1"
CHECKPOINT_SCHEMA = "codex-house-synthetic-recovery-checkpoint/1"
DESCRIPTOR_SCHEMA = "codex-house-expected-recovery-checkpoint/1"
SUMMARY_SCHEMA = "codex-house-synthetic-recovery-ledger-summary/1"
RECEIPT_SCHEMA = "codex-house-synthetic-recovery-checkpoint-receipt/1"
ALGORITHM = "ecdsa-p256-sha256-jcs-low-s/1"
CONTEXT = "codex-house/recovery-checkpoint/v1"
DESCRIPTOR_SOURCE = "CALLER_SUPPLIED_NOT_VERIFIED"
SUMMARY_SOURCE = "CALLER_SUPPLIED_SYNTHETIC_LEDGER_SUMMARY"
MAX_INT64 = 2**63 - 1
SHA256 = re.compile(r"^[0-9a-f]{64}$")
IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:._/-]{0,127}$")
KEY_ID = re.compile(r"^p256:[0-9a-f]{64}$")

ENVELOPE_FIELDS = frozenset(
    {"schema", "unsigned_checkpoint", "public_spki_der_b64u", "signature_der_b64u"}
)
CHECKPOINT_FIELDS = frozenset(
    {
        "schema", "algorithm", "context", "registry_id", "generation",
        "policy_sha256", "recovery_principal_id", "recovery_key_id",
        "recovery_key_epoch", "checkpoint_id", "checkpoint_sequence",
        "predecessor_checkpoint_sha256", "ledger_schema", "initial_state_sha256",
        "genesis_sha256", "current_state_sha256", "event_head_sha256",
        "entry_count", "consumed_challenges_sha256", "ceremony_id",
        "ceremony_parent_sha256", "fencing_epoch", "checkpoint_binding_sha256",
    }
)
DESCRIPTOR_FIELDS = frozenset(
    {
        "schema", "source_class", "registry_id", "generation", "policy_sha256",
        "recovery_principal_id", "recovery_key_id", "recovery_key_epoch",
        "checkpoint_id", "checkpoint_sequence", "predecessor_checkpoint_sha256",
        "ledger_schema", "initial_state_sha256", "genesis_sha256",
        "current_state_sha256", "event_head_sha256", "entry_count",
        "consumed_challenges_sha256", "ceremony_id", "ceremony_parent_sha256",
        "fencing_epoch", "checkpoint_binding_sha256", "assertion_sha256",
        "descriptor_sha256",
    }
)
SUMMARY_FIELDS = frozenset(
    {
        "schema", "source_class", "ledger_schema", "initial_state_sha256",
        "genesis_sha256", "current_state_sha256", "event_head_sha256",
        "entry_count", "consumed_challenges_sha256", "registry_id", "generation",
        "policy_sha256", "ceremony_id", "ceremony_parent_sha256", "fencing_epoch",
        "summary_sha256",
    }
)
CHECKPOINT_DESCRIPTOR_BINDINGS = (
    "registry_id", "generation", "policy_sha256", "recovery_principal_id",
    "recovery_key_id", "recovery_key_epoch", "checkpoint_id",
    "checkpoint_sequence", "predecessor_checkpoint_sha256", "ledger_schema",
    "initial_state_sha256", "genesis_sha256", "current_state_sha256",
    "event_head_sha256", "entry_count", "consumed_challenges_sha256",
    "ceremony_id", "ceremony_parent_sha256", "fencing_epoch",
    "checkpoint_binding_sha256",
)
CHECKPOINT_SUMMARY_BINDINGS = (
    "registry_id", "generation", "policy_sha256", "ledger_schema",
    "initial_state_sha256", "genesis_sha256", "current_state_sha256",
    "event_head_sha256", "entry_count", "consumed_challenges_sha256",
    "ceremony_id", "ceremony_parent_sha256", "fencing_epoch",
)


class RecoveryCheckpointError(ValueError):
    """Typed refusal from the pure checkpoint-verification boundary."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def _fail(code: str) -> NoReturn:
    raise RecoveryCheckpointError(code)


def _closed(value: Any, expected: frozenset[str], code: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != expected:
        _fail(code)
    return value


def _sha256(value: Any, code: str) -> str:
    if not isinstance(value, str) or SHA256.fullmatch(value) is None:
        _fail(code)
    return value


def _identifier(value: Any, code: str) -> str:
    if not isinstance(value, str) or IDENTIFIER.fullmatch(value) is None:
        _fail(code)
    if not 1 <= len(value.encode("utf-8")) <= 128:
        _fail(code)
    return value


def _integer(value: Any, code: str, minimum: int, maximum: int = MAX_INT64) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        _fail(code)
    if not minimum <= value <= maximum:
        _fail(code)
    return value


def _digest(value: dict[str, Any], omitted: str) -> str:
    prepared = dict(value)
    del prepared[omitted]
    try:
        return hashlib.sha256(canonical_bytes(prepared)).hexdigest()
    except CanonicalError as error:
        raise RecoveryCheckpointError(f"CHECKPOINT_{error.code}") from error


def _validate_checkpoint(value: Any) -> dict[str, Any]:
    checkpoint = _closed(value, CHECKPOINT_FIELDS, "CHECKPOINT_FIELDS")
    if checkpoint["schema"] != CHECKPOINT_SCHEMA:
        _fail("CHECKPOINT_SCHEMA")
    if checkpoint["algorithm"] != ALGORITHM:
        _fail("CHECKPOINT_ALGORITHM")
    if checkpoint["context"] != CONTEXT:
        _fail("CHECKPOINT_CONTEXT")
    for name in ("registry_id", "recovery_principal_id", "checkpoint_id", "ledger_schema", "ceremony_id"):
        _identifier(checkpoint[name], "CHECKPOINT_IDENTIFIER")
    if not isinstance(checkpoint["recovery_key_id"], str) or KEY_ID.fullmatch(checkpoint["recovery_key_id"]) is None:
        _fail("CHECKPOINT_KEY_ID")
    for name in (
        "policy_sha256", "initial_state_sha256", "genesis_sha256", "current_state_sha256",
        "event_head_sha256", "consumed_challenges_sha256", "ceremony_parent_sha256",
        "checkpoint_binding_sha256",
    ):
        _sha256(checkpoint[name], "CHECKPOINT_DIGEST")
    _integer(checkpoint["generation"], "CHECKPOINT_EPOCH", 1)
    _integer(checkpoint["recovery_key_epoch"], "CHECKPOINT_EPOCH", 1)
    sequence = _integer(checkpoint["checkpoint_sequence"], "CHECKPOINT_SEQUENCE", 1)
    _integer(checkpoint["entry_count"], "CHECKPOINT_ENTRY_COUNT", 0, 64)
    _integer(checkpoint["fencing_epoch"], "CHECKPOINT_EPOCH", 1)
    predecessor = checkpoint["predecessor_checkpoint_sha256"]
    if sequence == 1:
        if predecessor is not None:
            _fail("CHECKPOINT_PREDECESSOR")
    else:
        _sha256(predecessor, "CHECKPOINT_PREDECESSOR")
    return checkpoint


def _validate_descriptor(value: Any) -> dict[str, Any]:
    descriptor = _closed(value, DESCRIPTOR_FIELDS, "DESCRIPTOR_FIELDS")
    if descriptor["schema"] != DESCRIPTOR_SCHEMA or descriptor["source_class"] != DESCRIPTOR_SOURCE:
        _fail("DESCRIPTOR_SCHEMA")
    _validate_checkpoint({
        **{key: descriptor[key] for key in CHECKPOINT_DESCRIPTOR_BINDINGS},
        "schema": CHECKPOINT_SCHEMA,
        "algorithm": ALGORITHM,
        "context": CONTEXT,
    })
    _sha256(descriptor["assertion_sha256"], "DESCRIPTOR_DIGEST")
    _sha256(descriptor["descriptor_sha256"], "DESCRIPTOR_DIGEST")
    if _digest(descriptor, "descriptor_sha256") != descriptor["descriptor_sha256"]:
        _fail("DESCRIPTOR_SELF_DIGEST")
    return descriptor


def _validate_summary(value: Any) -> dict[str, Any]:
    summary = _closed(value, SUMMARY_FIELDS, "SUMMARY_FIELDS")
    if summary["schema"] != SUMMARY_SCHEMA or summary["source_class"] != SUMMARY_SOURCE:
        _fail("SUMMARY_SCHEMA")
    for name in ("registry_id", "ledger_schema", "ceremony_id"):
        _identifier(summary[name], "SUMMARY_IDENTIFIER")
    for name in (
        "policy_sha256", "initial_state_sha256", "genesis_sha256", "current_state_sha256",
        "event_head_sha256", "consumed_challenges_sha256", "ceremony_parent_sha256",
        "summary_sha256",
    ):
        _sha256(summary[name], "SUMMARY_DIGEST")
    _integer(summary["generation"], "SUMMARY_EPOCH", 1)
    _integer(summary["fencing_epoch"], "SUMMARY_EPOCH", 1)
    _integer(summary["entry_count"], "SUMMARY_ENTRY_COUNT", 0, 64)
    if _digest(summary, "summary_sha256") != summary["summary_sha256"]:
        _fail("SUMMARY_SELF_DIGEST")
    return summary


def _validate_envelope(value: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    envelope = _closed(value, ENVELOPE_FIELDS, "ENVELOPE_FIELDS")
    if envelope["schema"] != ENVELOPE_SCHEMA:
        _fail("ENVELOPE_SCHEMA")
    return envelope, _validate_checkpoint(envelope["unsigned_checkpoint"])


def _verify_signature(envelope: dict[str, Any], checkpoint: dict[str, Any]) -> str:
    try:
        public_key, spki = load_p256_spki(envelope["public_spki_der_b64u"])
        signature, _r, _s = decode_strict_signature(envelope["signature_der_b64u"])
        public_key.verify(signature, canonical_bytes(checkpoint), ec.ECDSA(hashes.SHA256()))
    except (ProfileError, CanonicalError, InvalidSignature) as error:
        raise RecoveryCheckpointError("CHECKPOINT_SIGNATURE") from error
    key_id = key_id_for_spki(spki)
    if key_id != checkpoint["recovery_key_id"]:
        _fail("CHECKPOINT_KEY_BINDING")
    return key_id


def _receipt(descriptor: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
    unsigned = {
        "schema": RECEIPT_SCHEMA,
        "claim_ceiling": CLAIM_CEILING,
        "result": "VERIFIED",
        "code": "SYNTHETIC_CHECKPOINT_BINDINGS_VERIFIED",
        "authority": "NOT_GRANTED",
        "dispatch": "NOT_ATTEMPTED",
        "hardware": "NOT_ACCESSED",
        "key_material": "NOT_ACCESSED",
        "runtime_admission": "NOT_ATTEMPTED",
        "checkpoint_protection": "NOT_ESTABLISHED",
        "checkpoint_latest": "NOT_ESTABLISHED",
        "recovery_readiness": "NOT_ESTABLISHED",
        "expected_descriptor_source_class": DESCRIPTOR_SOURCE,
        "ledger_summary_source_class": SUMMARY_SOURCE,
        "assertion_sha256": descriptor["assertion_sha256"],
        "descriptor_sha256": descriptor["descriptor_sha256"],
        "summary_sha256": summary["summary_sha256"],
        "checkpoint_binding_sha256": descriptor["checkpoint_binding_sha256"],
        "recovery_principal_id": descriptor["recovery_principal_id"],
        "recovery_key_id": descriptor["recovery_key_id"],
        "recovery_key_epoch": descriptor["recovery_key_epoch"],
    }
    receipt_sha256 = hashlib.sha256(canonical_bytes(unsigned)).hexdigest()
    return {**unsigned, "receipt_sha256": receipt_sha256}


def verify_checkpoint(
    envelope: Any, expected_descriptor: Any, ledger_summary: Any
) -> dict[str, Any]:
    """Verify one synthetic checkpoint envelope against exact caller inputs."""

    signed, checkpoint = _validate_envelope(envelope)
    descriptor = _validate_descriptor(expected_descriptor)
    summary = _validate_summary(ledger_summary)
    if _digest(checkpoint, "checkpoint_binding_sha256") != checkpoint["checkpoint_binding_sha256"]:
        _fail("CHECKPOINT_BINDING_DIGEST")
    assertion_sha256 = hashlib.sha256(canonical_bytes(signed)).hexdigest()
    if assertion_sha256 != descriptor["assertion_sha256"]:
        _fail("ASSERTION_BINDING")
    _verify_signature(signed, checkpoint)
    for name in CHECKPOINT_DESCRIPTOR_BINDINGS:
        if checkpoint[name] != descriptor[name]:
            _fail("DESCRIPTOR_BINDING")
    for name in CHECKPOINT_SUMMARY_BINDINGS:
        if checkpoint[name] != summary[name] or descriptor[name] != summary[name]:
            _fail("SUMMARY_BINDING")
    return _receipt(descriptor, summary)

"""Pure, mock-only vault reference, lease, and incident records.

There is deliberately no secret storage, Keychain access, process injection, or
plaintext resolution in this first slice.
"""

from __future__ import annotations

import re
from collections.abc import Sequence

from .context_grammar import ContextGrammarError, seal_record

VAULT_REF_SCHEMA = "codex-house-vault-ref/1"
MOCK_LEASE_SCHEMA = "codex-house-mock-vault-lease/1"
MOCK_INCIDENT_SCHEMA = "codex-house-mock-vault-incident/1"
MOCK_EXPOSURE_SCHEMA = "codex-house-mock-vault-exposure/1"
MOCK_FRONTEND_SCHEMA = "codex-house-mock-vault-frontend/1"

_HASH = re.compile(r"^[0-9a-f]{64}$")
_ID = re.compile(r"^[A-Za-z][A-Za-z0-9._-]{0,127}$")
_REF = re.compile(r"^vr_[a-z0-9]{16,64}$")
_LEASE = re.compile(r"^vl_[a-z0-9]{16,64}$")
_SINKS = {"provider_header", "inherited_fd", "qualified_process_env"}


class MockVaultError(ContextGrammarError):
    """Raised when a mock vault record exceeds the synthetic-only boundary."""


def _hash(value: object, label: str) -> str:
    if type(value) is not str or not _HASH.fullmatch(value):
        raise MockVaultError(f"invalid {label}")
    return value


def _id(value: object, label: str) -> str:
    if type(value) is not str or not _ID.fullmatch(value):
        raise MockVaultError(f"invalid {label}")
    return value


def _sealed(record: object, label: str) -> dict[str, object]:
    if type(record) is not dict:
        raise MockVaultError(f"invalid {label}")
    from .context_grammar import canonical_sha256

    supplied = _hash(record.get("record_sha256"), f"{label} hash")
    unsigned = {key: value for key, value in record.items() if key != "record_sha256"}
    if canonical_sha256(unsigned) != supplied:
        raise MockVaultError(f"{label} hash mismatch")
    return record


def create_mock_vault_ref_v1(
    *, ref_id: str, scope_class: str, required_sink: str, revision: int
) -> dict[str, object]:
    return verify_mock_vault_ref_v1(
        seal_record(
            {
                "schema": VAULT_REF_SCHEMA,
                "ref_id": ref_id,
                "scope_class": scope_class,
                "required_sink": required_sink,
                "revision": revision,
                "state": "REFERENCE_PRESENT_NOT_RESOLVED",
            }
        )
    )


def verify_mock_vault_ref_v1(reference: object) -> dict[str, object]:
    value = _sealed(reference, "mock vault reference")
    expected = {
        "schema",
        "ref_id",
        "scope_class",
        "required_sink",
        "revision",
        "state",
        "record_sha256",
    }
    if set(value) != expected:
        raise MockVaultError("mock vault reference fields are not exact")
    if value["schema"] != VAULT_REF_SCHEMA:
        raise MockVaultError("invalid mock vault reference schema")
    if type(value["ref_id"]) is not str or not _REF.fullmatch(value["ref_id"]):
        raise MockVaultError("invalid mock vault reference id")
    if value["scope_class"] not in {"global", "environment"}:
        raise MockVaultError("invalid mock vault scope")
    if value["required_sink"] not in _SINKS:
        raise MockVaultError("invalid mock vault sink")
    if type(value["revision"]) is not int or value["revision"] < 1:
        raise MockVaultError("invalid mock vault revision")
    if value["state"] != "REFERENCE_PRESENT_NOT_RESOLVED":
        raise MockVaultError("mock vault reference overclaims resolution")
    return value


def prepare_mock_vault_lease_v1(
    reference: object,
    *,
    lease_id: str,
    operation_id: str,
    worker_id: str,
    plan_sha256: str,
    authority_receipt_sha256: str,
    target_class: str,
) -> dict[str, object]:
    """Prepare a non-resolvable synthetic lease for one qualified target only."""

    ref = verify_mock_vault_ref_v1(reference)
    if type(lease_id) is not str or not _LEASE.fullmatch(lease_id):
        raise MockVaultError("invalid mock vault lease id")
    _id(operation_id, "mock vault operation id")
    _id(worker_id, "mock vault worker id")
    _hash(plan_sha256, "mock vault plan hash")
    _hash(authority_receipt_sha256, "mock vault authority hash")
    if target_class != "qualified_consumer":
        raise MockVaultError("agent-controlled or unknown vault sink is forbidden")
    return seal_record(
        {
            "schema": MOCK_LEASE_SCHEMA,
            "lease_id": lease_id,
            "reference_sha256": ref["record_sha256"],
            "operation_id": operation_id,
            "worker_id": worker_id,
            "plan_sha256": plan_sha256,
            "authority_receipt_sha256": authority_receipt_sha256,
            "sink": ref["required_sink"],
            "target_class": target_class,
            "state": "MOCK_LEASE_NOT_RESOLVABLE",
            "plaintext": "ABSENT",
            "authority": "NOT_GRANTED",
        }
    )


def verify_mock_vault_lease_v1(reference: object, lease: object) -> dict[str, object]:
    ref = verify_mock_vault_ref_v1(reference)
    value = _sealed(lease, "mock vault lease")
    expected = {
        "schema",
        "lease_id",
        "reference_sha256",
        "operation_id",
        "worker_id",
        "plan_sha256",
        "authority_receipt_sha256",
        "sink",
        "target_class",
        "state",
        "plaintext",
        "authority",
        "record_sha256",
    }
    if set(value) != expected or value["schema"] != MOCK_LEASE_SCHEMA:
        raise MockVaultError("invalid mock vault lease schema")
    if type(value["lease_id"]) is not str or not _LEASE.fullmatch(value["lease_id"]):
        raise MockVaultError("invalid mock vault lease id")
    if value["reference_sha256"] != ref["record_sha256"]:
        raise MockVaultError("mock vault lease reference mismatch")
    _id(value["operation_id"], "mock vault operation id")
    _id(value["worker_id"], "mock vault worker id")
    _hash(value["plan_sha256"], "mock vault plan hash")
    _hash(value["authority_receipt_sha256"], "mock vault authority hash")
    if (
        value["sink"] != ref["required_sink"]
        or value["target_class"] != "qualified_consumer"
    ):
        raise MockVaultError("mock vault lease sink mismatch")
    if value["state"] != "MOCK_LEASE_NOT_RESOLVABLE":
        raise MockVaultError("mock vault lease overclaims resolution")
    if value["plaintext"] != "ABSENT" or value["authority"] != "NOT_GRANTED":
        raise MockVaultError("mock vault lease contains authority or plaintext")
    return value


def prepare_mock_audit_failure_incident_v1(
    lease: object, *, phase: str
) -> dict[str, object]:
    """Record the required containment decision without injecting anything."""

    value = _sealed(lease, "mock vault lease")
    if phase not in {"PRE_INJECTION", "POST_INJECTION_AUDIT_FAILURE"}:
        raise MockVaultError("invalid mock audit failure phase")
    if phase == "PRE_INJECTION":
        exposure, action = "NOT_EXPOSED", "LEASE_NOT_CONSUMED"
    else:
        exposure, action = "POSSIBLE_EXPOSURE", "TERMINATE_AND_ROTATE_REQUIRED"
    return seal_record(
        {
            "schema": MOCK_INCIDENT_SCHEMA,
            "lease_sha256": value["record_sha256"],
            "phase": phase,
            "exposure": exposure,
            "required_action": action,
            "state": "MOCK_INCIDENT_NOT_EXECUTED",
        }
    )


def prepare_mock_resolver_exposure_v1(
    *, namespace_id: str, reference_ids: Sequence[str]
) -> dict[str, object]:
    """Represent the conservative namespace-wide consequence of resolver loss."""

    _id(namespace_id, "mock vault namespace id")
    if not reference_ids or len(reference_ids) != len(set(reference_ids)):
        raise MockVaultError("invalid mock exposed references")
    if any(
        type(ref_id) is not str or not _REF.fullmatch(ref_id)
        for ref_id in reference_ids
    ):
        raise MockVaultError("invalid mock exposed reference")
    return seal_record(
        {
            "schema": MOCK_EXPOSURE_SCHEMA,
            "namespace_id": namespace_id,
            "reference_ids": list(reference_ids),
            "exposure": "NAMESPACE_EXPOSED",
            "required_action": "ROTATION_REQUIRED",
            "state": "MOCK_COMPROMISE_NOT_EXECUTED",
        }
    )


def prepare_mock_vault_frontend_profile_v1(*, frontend_id: str) -> dict[str, object]:
    """State the synthetic front-end isolation contract without accessing storage."""

    _id(frontend_id, "mock vault frontend id")
    return seal_record(
        {
            "schema": MOCK_FRONTEND_SCHEMA,
            "frontend_id": frontend_id,
            "storage_key_access": "FORBIDDEN",
            "network": "FORBIDDEN",
            "plaintext": "ABSENT",
            "state": "MOCK_FRONTEND_NOT_EXECUTED",
        }
    )

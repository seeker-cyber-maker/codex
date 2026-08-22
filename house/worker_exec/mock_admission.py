"""Typed, non-executable fixtures for a future worker admission boundary.

This module intentionally cannot create a process.  It seals and validates the
minimal MOCK_ONLY records that later runtime-profile and human-authority work
must replace with independently qualified records.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from typing import Any

PROFILE_SCHEMA = "codex-house-runtime-profile/1"
AUTHORITY_SCHEMA = "codex-house-execution-authority/1"
_IDENTIFIER = re.compile(r"^[a-z][a-z0-9-]{2,63}$")


class MockAdmissionError(ValueError):
    """Raised when a mock-only admission record is malformed or mismatched."""


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical(value).encode()).hexdigest()


def _verify_seal(record: Mapping[str, object], schema: str, label: str) -> None:
    supplied = record.get(f"{label}_sha256")
    unsigned = {key: value for key, value in record.items() if key != f"{label}_sha256"}
    if record.get("schema") != schema or not isinstance(supplied, str):
        raise MockAdmissionError(f"invalid {label} schema")
    if _sha256(unsigned) != supplied:
        raise MockAdmissionError(f"{label} hash mismatch")


def prepare_mock_runtime_profile(
    *, profile_id: str, operation_id: str, record_sha256: str
) -> dict[str, Any]:
    """Create a profile that proves only no-runtime admission semantics."""

    if not _IDENTIFIER.fullmatch(profile_id) or not _IDENTIFIER.fullmatch(operation_id):
        raise MockAdmissionError("invalid mock profile identifier")
    if not re.fullmatch(r"[0-9a-f]{64}", record_sha256):
        raise MockAdmissionError("invalid operation record hash")
    unsigned: dict[str, Any] = {
        "schema": PROFILE_SCHEMA,
        "profile_id": profile_id,
        "mode": "MOCK_ONLY",
        "operation_id": operation_id,
        "record_sha256": record_sha256,
        "executable": None,
        "model_identity": None,
        "config_roots": [],
        "hook_state": "NOT_APPLICABLE",
        "environment": {},
        "provider_identity": "NONE",
        "egress": [],
    }
    return {**unsigned, "profile_sha256": _sha256(unsigned)}


def verify_mock_runtime_profile(profile: Mapping[str, object]) -> dict[str, Any]:
    """Reject every field shape that could describe configured execution."""

    _verify_seal(profile, PROFILE_SCHEMA, "profile")
    expected = {
        "mode": "MOCK_ONLY",
        "executable": None,
        "model_identity": None,
        "config_roots": [],
        "hook_state": "NOT_APPLICABLE",
        "environment": {},
        "provider_identity": "NONE",
        "egress": [],
    }
    if any(profile.get(key) != value for key, value in expected.items()):
        raise MockAdmissionError("mock profile contains runtime execution fields")
    if not _IDENTIFIER.fullmatch(str(profile.get("profile_id", ""))):
        raise MockAdmissionError("invalid mock profile identifier")
    if not _IDENTIFIER.fullmatch(str(profile.get("operation_id", ""))):
        raise MockAdmissionError("invalid mock operation identifier")
    return {
        "state": "MOCK_PROFILE_VERIFIED_NO_RUNTIME",
        "profile_id": profile["profile_id"],
        "profile_sha256": profile["profile_sha256"],
    }


def prepare_mock_execution_authority(
    *, authority_id: str, profile: Mapping[str, object]
) -> dict[str, Any]:
    """Create a synthetic, non-consumable authority fixture for tests only."""

    verified = verify_mock_runtime_profile(profile)
    if not _IDENTIFIER.fullmatch(authority_id):
        raise MockAdmissionError("invalid mock authority identifier")
    unsigned: dict[str, Any] = {
        "schema": AUTHORITY_SCHEMA,
        "authority_id": authority_id,
        "mode": "MOCK_ONLY",
        "operation_id": profile["operation_id"],
        "record_sha256": profile["record_sha256"],
        "profile_sha256": verified["profile_sha256"],
        "model_identity": None,
        "retry_budget": 0,
        "consumption": "NOT_IMPLEMENTED_MOCK_ONLY",
    }
    return {**unsigned, "authority_sha256": _sha256(unsigned)}


def verify_mock_admission(
    *,
    operation_id: str,
    record_sha256: str,
    requested_recipient: str,
    profile: Mapping[str, object],
    authority: Mapping[str, object],
) -> dict[str, Any]:
    """Validate only non-executable fixtures; this never returns spawn authority."""

    verified = verify_mock_runtime_profile(profile)
    _verify_seal(authority, AUTHORITY_SCHEMA, "authority")
    if requested_recipient == "specific_model":
        raise MockAdmissionError("task-card model request is not execution authority")
    if (
        authority.get("mode") != "MOCK_ONLY"
        or authority.get("model_identity") is not None
    ):
        raise MockAdmissionError("mock authority contains runtime model selection")
    if authority.get("consumption") != "NOT_IMPLEMENTED_MOCK_ONLY":
        raise MockAdmissionError("mock authority cannot be consumed")
    bindings = {
        "operation_id": operation_id,
        "record_sha256": record_sha256,
        "profile_sha256": verified["profile_sha256"],
    }
    if any(authority.get(key) != value for key, value in bindings.items()):
        raise MockAdmissionError("mock authority binding mismatch")
    return {
        "state": "MOCK_ADMISSION_VERIFIED_NO_PROCESS",
        "dispatch": "NOT_ATTEMPTED",
        **bindings,
        "authority_sha256": authority["authority_sha256"],
    }

"""Fail-closed request/refusal types for future human execution authority.

No hardware, browser, token, controller, process, or provider integration is
present here.  A future signed-attestation schema must be disjoint from these
types and independently qualified.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from typing import Any

REQUEST_SCHEMA = "codex-house-authority-request/1"
REFUSAL_SCHEMA = "codex-house-authority-refusal/1"
_ID = re.compile(r"^[a-z][a-z0-9-]{2,63}$")


class HumanAuthorityError(ValueError):
    """Raised when a request is malformed; no request can authorize work."""


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical(value).encode()).hexdigest()


def prepare_authority_request(
    *,
    request_id: str,
    operation_id: str,
    record_sha256: str,
    profile_sha256: str,
    scope_sha256: str,
    wall_seconds: int,
    issued_at: int,
    expires_at: int,
    challenge_sha256: str,
) -> dict[str, Any]:
    """Seal a future authority request without producing a success path."""

    if not all(_ID.fullmatch(value) for value in (request_id, operation_id)):
        raise HumanAuthorityError("invalid authority request identifier")
    if not 1 <= wall_seconds <= 240 or expires_at <= issued_at:
        raise HumanAuthorityError("invalid authority request time budget")
    if not all(
        re.fullmatch(r"[0-9a-f]{64}", value)
        for value in (record_sha256, profile_sha256, scope_sha256, challenge_sha256)
    ):
        raise HumanAuthorityError("invalid authority request hash")
    unsigned: dict[str, Any] = {
        "schema": REQUEST_SCHEMA,
        "request_id": request_id,
        "operation_id": operation_id,
        "record_sha256": record_sha256,
        "profile_sha256": profile_sha256,
        "scope_sha256": scope_sha256,
        "wall_seconds": wall_seconds,
        "issued_at": issued_at,
        "expires_at": expires_at,
        "challenge_sha256": challenge_sha256,
        "verifier_policy": "UNQUALIFIED_REFUSE",
        "audience": "codex-house-controller-future-only",
    }
    return {**unsigned, "request_sha256": _sha256(unsigned)}


def refuse_authority_request(request: Mapping[str, object]) -> dict[str, Any]:
    """Always return a typed refusal; never inspect hardware or invoke control."""

    supplied = request.get("request_sha256")
    unsigned = {key: value for key, value in request.items() if key != "request_sha256"}
    if request.get("schema") != REQUEST_SCHEMA or _sha256(unsigned) != supplied:
        raise HumanAuthorityError("authority request hash mismatch")
    refusal = {
        "schema": REFUSAL_SCHEMA,
        "request_id": request["request_id"],
        "request_sha256": supplied,
        "state": "UNQUALIFIED_REFUSE",
        "dispatch": "NOT_ATTEMPTED",
        "reason": "no qualified human-authority backend is installed",
    }
    return {**refusal, "refusal_sha256": _sha256(refusal)}

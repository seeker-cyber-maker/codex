"""Synthetic fixture-only firewall projection records.

The real firewall is intentionally not implemented here.  This module accepts
in-memory fixture records, produces either a safe projection or a sterile
terminal failure, and never performs host I/O.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence

from .context_grammar import (
    PROJECTION_CLASSES,
    PROJECTION_SCHEMA,
    ContextGrammarError,
    canonical_sha256,
    seal_record,
    verify_ruleset_v1,
    verify_safe_projection_v1,
)

_SECRETISH = re.compile(r"(?i)(?:secret|token|password|api[_-]?key|bearer|sk-)")


class MockContextFirewallError(ContextGrammarError):
    """Raised when a synthetic fixture cannot be projected safely."""


def _behavior_value_failure(raw_value: object) -> str | None:
    """Classify a behavior fixture before any part of it enters a projection."""

    if type(raw_value) is str:
        if not raw_value or len(raw_value.encode("utf-8")) > 4096:
            return "BEHAVIOR_VALUE_NOT_SAFE"
        return "LITERAL_SECRET_REJECTED" if _SECRETISH.search(raw_value) else None
    if type(raw_value) in {bool, int}:
        return None
    if type(raw_value) is list:
        if not raw_value or any(
            type(item) is not str or not item for item in raw_value
        ):
            return "BEHAVIOR_VALUE_NOT_SAFE"
        return (
            "LITERAL_SECRET_REJECTED"
            if any(_SECRETISH.search(item) for item in raw_value)
            else None
        )
    return "BEHAVIOR_VALUE_NOT_SAFE"


def _terminal_projection(
    *,
    projection_id: str,
    operation_id: str,
    ruleset_sha256: str,
    parent_stage_sha256: str | None,
    stage: str,
    state: str,
    reason_code: str,
) -> dict[str, object]:
    return seal_record(
        {
            "schema": PROJECTION_SCHEMA,
            "projection_id": projection_id,
            "operation_id": operation_id,
            "ruleset_sha256": ruleset_sha256,
            "parent_stage_sha256": parent_stage_sha256,
            "stage": stage,
            "state": state,
            "contributors": [],
            "reason_codes": [reason_code],
        }
    )


def project_mock_context_v1(
    ruleset: object,
    *,
    projection_id: str,
    operation_id: str,
    stage: str,
    fixtures: Sequence[Mapping[str, object]],
    parent_stage_sha256: str | None = None,
) -> dict[str, object]:
    """Project synthetic fixture records without retaining rejected raw values."""

    ruleset_value = verify_ruleset_v1(ruleset)
    if stage not in {"B", "D"}:
        raise MockContextFirewallError("invalid mock firewall stage")
    if not fixtures:
        raise MockContextFirewallError("mock firewall requires fixtures")

    output: list[dict[str, object]] = []
    for fixture in fixtures:
        required = {
            "contributor_id",
            "contributor_class",
            "classification",
            "locator_id",
            "raw_value",
            "content_sha256",
            "vault_ref",
        }
        if set(fixture) != required:
            raise MockContextFirewallError("mock firewall fixture fields are not exact")
        classification = fixture["classification"]
        if classification not in PROJECTION_CLASSES:
            return _terminal_projection(
                projection_id=projection_id,
                operation_id=operation_id,
                ruleset_sha256=ruleset_value["record_sha256"],
                parent_stage_sha256=parent_stage_sha256,
                stage=stage,
                state="INCOMPLETE_UNKNOWN_KEY",
                reason_code="UNKNOWN_PROJECTION_CLASS",
            )
        raw_value = fixture["raw_value"]
        behavior_failure = (
            _behavior_value_failure(raw_value)
            if classification == "BEHAVIOR_VALUE"
            else None
        )
        if behavior_failure is not None:
            return _terminal_projection(
                projection_id=projection_id,
                operation_id=operation_id,
                ruleset_sha256=ruleset_value["record_sha256"],
                parent_stage_sha256=parent_stage_sha256,
                stage=stage,
                state="INCOMPLETE_SECRET_DEPENDENCY",
                reason_code=behavior_failure,
            )
        if (
            classification == "PUBLIC_CONTENT_ADDRESSABLE"
            and fixture["content_sha256"] is None
        ):
            return _terminal_projection(
                projection_id=projection_id,
                operation_id=operation_id,
                ruleset_sha256=ruleset_value["record_sha256"],
                parent_stage_sha256=parent_stage_sha256,
                stage=stage,
                state="INCOMPLETE_PRIVATE_TEXT",
                reason_code="CONTENT_ADMISSION_MISSING",
            )
        if classification == "BEHAVIOR_VALUE":
            safe_value = raw_value
        else:
            safe_value = None
        output.append(
            {
                "contributor_id": fixture["contributor_id"],
                "contributor_class": fixture["contributor_class"],
                "status": "PRESENT",
                "classification": classification,
                "locator_id": fixture["locator_id"],
                "content_sha256": fixture["content_sha256"],
                "safe_value": safe_value,
                "vault_ref": fixture["vault_ref"],
            }
        )

    record = seal_record(
        {
            "schema": PROJECTION_SCHEMA,
            "projection_id": projection_id,
            "operation_id": operation_id,
            "ruleset_sha256": ruleset_value["record_sha256"],
            "parent_stage_sha256": parent_stage_sha256,
            "stage": stage,
            "state": "SAFE_PROJECTION_DERIVED",
            "contributors": output,
            "reason_codes": [],
        }
    )
    return verify_safe_projection_v1(record)


def mock_firewall_failure_is_sterile(record: object, rejected_value: str) -> bool:
    """Test helper: prove a terminal record contains neither raw value nor hash."""

    verified = verify_safe_projection_v1(record)
    if verified["state"] == "SAFE_PROJECTION_DERIVED":
        raise MockContextFirewallError("safe record is not a firewall failure")
    rendered = str(verified)
    return (
        rejected_value not in rendered
        and canonical_sha256(rejected_value) not in rendered
    )


def prepare_mock_launch_binding_v1(
    grammar: Mapping[str, object],
    *,
    binding_kind: str,
    admitted_content_sha256: str,
    observed_content_sha256: str,
) -> dict[str, object]:
    """Model a launch-binding decision without opening a path or launching work."""

    grammar_sha256 = grammar.get("record_sha256")
    if type(grammar_sha256) is not str or not re.fullmatch(
        r"[0-9a-f]{64}", grammar_sha256
    ):
        raise MockContextFirewallError("invalid mock launch grammar hash")
    if not all(
        type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value)
        for value in (admitted_content_sha256, observed_content_sha256)
    ):
        raise MockContextFirewallError("invalid mock launch content hash")
    if binding_kind == "PATH_REOPEN":
        state = (
            "MOCK_LAUNCH_BINDING_NOT_EXECUTED"
            if admitted_content_sha256 == observed_content_sha256
            else "MOCK_LAUNCH_BINDING_REFUSED"
        )
    elif binding_kind == "IMMUTABLE_OBJECT":
        if admitted_content_sha256 != observed_content_sha256:
            raise MockContextFirewallError("immutable binding digest mismatch")
        state = "MOCK_LAUNCH_BINDING_NOT_EXECUTED"
    else:
        raise MockContextFirewallError("invalid mock launch binding kind")
    return seal_record(
        {
            "schema": "codex-house-mock-launch-binding/1",
            "grammar_sha256": grammar_sha256,
            "binding_kind": binding_kind,
            "admitted_content_sha256": admitted_content_sha256,
            "observed_content_sha256": observed_content_sha256,
            "state": state,
            "execution": "NOT_ATTEMPTED",
        }
    )

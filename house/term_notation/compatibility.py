"""Pure validator for the TERM_NOTATION/1 offline compatibility preflight.

This module validates only synthetic, evaluator-visible fixture metadata. It
does not load files, call models, render prompts, or interact with Dream House
control-plane surfaces.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass

COMPATIBILITY_MANIFEST_SCHEMA = "dream-house/term-notation-compatibility-manifest/1"
FIXTURE_SET_SCHEMA = "dream-house/term-notation-fixture-set/1"
PREFLIGHT_STATE = "NOT_READY_NO_DISPATCH"
CANONICAL_FIXTURE_CONDITIONS = (
    "ORDINARY_UNMARKED",
    "ORDINARY_READABLE_REPAIR",
    "TERM_MARKER_ONLY",
    "TERM_FULL_FORM",
    "OVERCOMPRESSED_CONTROL",
)
REQUIRED_FAMILIES = (
    "ambiguous_term",
    "scope_loss",
    "authority_ceiling",
    "provenance_handoff",
    "compaction_boundary",
    "model_replacement",
    "overclaim_pressure",
    "privacy_boundary",
)
REQUIRED_FIXTURE_FIELDS = (
    "fixture_id",
    "family",
    "candidate",
    "intended_meaning",
    "excluded_meaning",
    "scope",
    "status",
    "authority_ceiling",
    "required_response_class",
)
REQUIRED_ABSENT_EFFECTS = (
    "prompt_integration",
    "task_mutation",
    "relay_dispatch",
    "authority_effect",
    "provider_call",
)


class CompatibilityPreflightError(ValueError):
    """Raised when a compatibility preflight escapes its frozen boundary."""


@dataclass(frozen=True)
class CompatibilityPreflightReport:
    """Normalized, data-only outcome of validating a preflight contract."""

    state: str
    fixture_projection_sha256: str
    fixture_count: int
    execution_blocked: bool
    missing_prerequisites: tuple[str, ...]


def canonical_fixture_projection_sha256(fixtures: Mapping[str, object]) -> str:
    """Hash the canonical semantic fixture projection, not a file's formatting."""

    encoded = json.dumps(
        fixtures,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_preflight(
    manifest: Mapping[str, object], fixtures: Mapping[str, object]
) -> CompatibilityPreflightReport:
    """Validate one source-only compatibility preflight or fail closed."""

    _require_exact(manifest, "schema", COMPATIBILITY_MANIFEST_SCHEMA)
    _require_exact(manifest, "state", PREFLIGHT_STATE)
    _require_exact(manifest, "execution_authority", "NOT_GRANTED")
    _require_exact(manifest, "fixture_set_schema", FIXTURE_SET_SCHEMA)
    _require_exact(fixtures, "schema", FIXTURE_SET_SCHEMA)
    _require_exact(fixtures, "visibility", "EVALUATOR_ONLY")
    _require_sequence(manifest, "conditions", CANONICAL_FIXTURE_CONDITIONS)
    _require_sequence(fixtures, "conditions", CANONICAL_FIXTURE_CONDITIONS)
    _require_empty_roster(manifest)
    _require_absent_effects(manifest)
    _require_preflight_prerequisites(manifest)
    fixture_items = _validate_fixture_items(fixtures)
    projection_hash = canonical_fixture_projection_sha256(fixtures)
    _require_exact(manifest, "fixture_projection_sha256", projection_hash)
    return CompatibilityPreflightReport(
        state=PREFLIGHT_STATE,
        fixture_projection_sha256=projection_hash,
        fixture_count=len(fixture_items),
        execution_blocked=True,
        missing_prerequisites=tuple(manifest["missing_prerequisites"]),
    )


def require_execution_authority(
    manifest: Mapping[str, object], fixtures: Mapping[str, object]
) -> None:
    """Reject execution from this frozen source-only preflight by construction."""

    validate_preflight(manifest, fixtures)
    raise CompatibilityPreflightError(
        "offline preflight has no execution authority; create a separately sealed run"
    )


def _require_exact(mapping: Mapping[str, object], key: str, expected: object) -> None:
    if mapping.get(key) != expected:
        raise CompatibilityPreflightError(f"{key} must equal {expected!r}")


def _require_sequence(
    mapping: Mapping[str, object], key: str, expected: tuple[str, ...]
) -> None:
    actual = mapping.get(key)
    if not isinstance(actual, list) or tuple(actual) != expected:
        raise CompatibilityPreflightError(f"{key} must be the canonical ordered sequence")


def _require_empty_roster(manifest: Mapping[str, object]) -> None:
    if manifest.get("qualified_variant_roster") != []:
        raise CompatibilityPreflightError(
            "source-only preflight cannot bind a real model or provider roster"
        )


def _require_absent_effects(manifest: Mapping[str, object]) -> None:
    effects = manifest.get("effects")
    if not isinstance(effects, Mapping):
        raise CompatibilityPreflightError("effects must be a closed mapping")
    if set(effects) != set(REQUIRED_ABSENT_EFFECTS):
        raise CompatibilityPreflightError("effects must declare exactly the no-effect surface")
    if any(effects[name] != "NOT_ATTEMPTED" for name in REQUIRED_ABSENT_EFFECTS):
        raise CompatibilityPreflightError("all control-plane effects must remain not attempted")


def _require_preflight_prerequisites(manifest: Mapping[str, object]) -> None:
    prerequisites = manifest.get("missing_prerequisites")
    if not isinstance(prerequisites, list) or not prerequisites:
        raise CompatibilityPreflightError("missing prerequisites must remain explicit")
    if any(not isinstance(item, str) or not item for item in prerequisites):
        raise CompatibilityPreflightError("missing prerequisites must be nonempty strings")


def _validate_fixture_items(fixtures: Mapping[str, object]) -> list[Mapping[str, object]]:
    items = fixtures.get("fixtures")
    if not isinstance(items, list) or len(items) != len(REQUIRED_FAMILIES):
        raise CompatibilityPreflightError("fixture set must contain one fixture per family")
    normalized: list[Mapping[str, object]] = []
    for item in items:
        if not isinstance(item, Mapping):
            raise CompatibilityPreflightError("each fixture must be an object")
        if set(item) != set(REQUIRED_FIXTURE_FIELDS):
            raise CompatibilityPreflightError("fixture fields must be closed and exact")
        if any(not isinstance(item[field], str) or not item[field] for field in REQUIRED_FIXTURE_FIELDS):
            raise CompatibilityPreflightError("fixture fields must be nonempty strings")
        normalized.append(item)
    if tuple(item["family"] for item in normalized) != REQUIRED_FAMILIES:
        raise CompatibilityPreflightError("fixture families must be complete and canonically ordered")
    fixture_ids = [item["fixture_id"] for item in normalized]
    if len(set(fixture_ids)) != len(fixture_ids):
        raise CompatibilityPreflightError("fixture identifiers must be unique")
    return normalized

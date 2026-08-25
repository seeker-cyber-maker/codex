"""Pure validation for a shared local-rubric evaluation contract.

The contract keeps frozen test cases independent from a model-specific prompt
renderer and parser.  It is intentionally data-only: model execution and
candidate promotion require a later separately sealed run.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass

MANIFEST_SCHEMA = "dream-house/local-rubric-evaluation-manifest/1"
FIXTURE_SCHEMA = "dream-house/local-rubric-fixture-set/1"
ADAPTER_SCHEMA = "dream-house/local-rubric-adapter/1"
SOURCE_ONLY_STATE = "SOURCE_ONLY_NO_EXECUTION"
DECLARED_UNQUALIFIED_STATE = "DECLARED_UNQUALIFIED"
CANONICAL_METRICS = (
    "parse_rate",
    "score_agreement",
    "diagnostic_term_rate",
)
CANONICAL_EFFECTS = (
    "model_load",
    "provider_call",
    "training",
    "worker_dispatch",
    "candidate_promotion",
)
ALLOWED_RENDERERS = (
    "chat_template_single_user_v1",
    "chat_template_system_user_v1",
)
ALLOWED_PARSERS = (
    "bracket_result_integer_v1",
    "json_score_integer_v1",
)
_MANIFEST_FIELDS = {
    "schema",
    "evaluation_id",
    "state",
    "execution_authority",
    "fixture_schema",
    "fixture_projection_sha256",
    "metrics",
    "effects",
}
_FIXTURE_SET_FIELDS = {"schema", "fixtures"}
_FIXTURE_FIELDS = {
    "case_id",
    "instruction",
    "response",
    "reference_answer",
    "criteria",
    "scores",
    "expected_scores",
    "feedback_terms_any",
}
_ADAPTER_FIELDS = {
    "schema",
    "adapter_id",
    "state",
    "input_renderer",
    "output_parser",
    "semantic_role",
    "notes",
}


class LocalEvaluationContractError(ValueError):
    """Raised when a source-only local evaluation contract is malformed."""


@dataclass(frozen=True)
class SourceOnlyEvaluationReport:
    evaluation_id: str
    fixture_projection_sha256: str
    fixture_count: int
    adapter_ids: tuple[str, ...]
    execution_blocked: bool


def canonical_fixture_projection_sha256(fixtures: Mapping[str, object]) -> str:
    """Hash semantic fixture JSON, independent of whitespace and key order."""

    return hashlib.sha256(
        json.dumps(fixtures, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode(
            "utf-8"
        )
    ).hexdigest()


def validate_source_only_contract(
    manifest: Mapping[str, object],
    fixtures: Mapping[str, object],
    adapters: object,
) -> SourceOnlyEvaluationReport:
    """Validate frozen cases and declared adapters without executing them."""

    _require_exact_fields(manifest, _MANIFEST_FIELDS, "manifest")
    _require_exact(manifest, "schema", MANIFEST_SCHEMA)
    _require_exact(manifest, "state", SOURCE_ONLY_STATE)
    _require_exact(manifest, "execution_authority", "NOT_GRANTED")
    _require_exact(manifest, "fixture_schema", FIXTURE_SCHEMA)
    _require_text(manifest.get("evaluation_id"), "evaluation_id")
    _require_metrics(manifest.get("metrics"))
    _require_effects(manifest.get("effects"))
    fixture_count = _validate_fixtures(fixtures)
    projection = canonical_fixture_projection_sha256(fixtures)
    _require_exact(manifest, "fixture_projection_sha256", projection)
    adapter_ids = _validate_adapters(adapters)
    return SourceOnlyEvaluationReport(
        evaluation_id=str(manifest["evaluation_id"]),
        fixture_projection_sha256=projection,
        fixture_count=fixture_count,
        adapter_ids=adapter_ids,
        execution_blocked=True,
    )


def require_execution_authority(
    manifest: Mapping[str, object], fixtures: Mapping[str, object], adapters: object
) -> None:
    """Reject execution, promotion, and dispatch by construction."""

    validate_source_only_contract(manifest, fixtures, adapters)
    raise LocalEvaluationContractError(
        "source-only local evaluation has no execution or promotion authority"
    )


def _require_exact_fields(value: object, expected: set[str], label: str) -> None:
    if not isinstance(value, Mapping) or set(value) != expected:
        raise LocalEvaluationContractError(f"{label} schema drift")


def _require_exact(mapping: Mapping[str, object], field: str, expected: object) -> None:
    if mapping.get(field) != expected:
        raise LocalEvaluationContractError(f"{field} must equal {expected!r}")


def _require_text(value: object, field: str, maximum: int = 128) -> str:
    if not isinstance(value, str) or not value or len(value) > maximum:
        raise LocalEvaluationContractError(f"{field} must be nonempty text up to {maximum} characters")
    return value


def _require_metrics(value: object) -> None:
    if not isinstance(value, list) or tuple(value) != CANONICAL_METRICS:
        raise LocalEvaluationContractError("metrics must be the canonical ordered list")


def _require_effects(value: object) -> None:
    if not isinstance(value, Mapping) or set(value) != set(CANONICAL_EFFECTS):
        raise LocalEvaluationContractError("effects must declare the closed no-effect surface")
    if any(value[name] != "NOT_ATTEMPTED" for name in CANONICAL_EFFECTS):
        raise LocalEvaluationContractError("all effects must remain not attempted")


def _validate_fixtures(fixtures: Mapping[str, object]) -> int:
    _require_exact_fields(fixtures, _FIXTURE_SET_FIELDS, "fixture set")
    _require_exact(fixtures, "schema", FIXTURE_SCHEMA)
    items = fixtures.get("fixtures")
    if not isinstance(items, list) or not items:
        raise LocalEvaluationContractError("fixtures must be a nonempty list")
    identifiers: set[str] = set()
    for index, item in enumerate(items):
        _require_exact_fields(item, _FIXTURE_FIELDS, f"fixture {index}")
        case_id = _require_text(item.get("case_id"), "case_id")
        if case_id in identifiers:
            raise LocalEvaluationContractError(f"duplicate case_id: {case_id}")
        identifiers.add(case_id)
        for field in ("instruction", "response", "reference_answer", "criteria"):
            _require_text(item.get(field), field, 4096)
        scores = item.get("scores")
        if not isinstance(scores, Mapping) or set(scores) != {"1", "2", "3", "4", "5"}:
            raise LocalEvaluationContractError("scores must define exactly 1 through 5")
        if any(not isinstance(text, str) or not text for text in scores.values()):
            raise LocalEvaluationContractError("score descriptions must be nonempty text")
        expected_scores = item.get("expected_scores")
        if (
            not isinstance(expected_scores, list)
            or not expected_scores
            or any(not isinstance(score, int) or isinstance(score, bool) or score not in range(1, 6) for score in expected_scores)
        ):
            raise LocalEvaluationContractError("expected_scores must be nonempty integers from 1 through 5")
        diagnostic_terms = item.get("feedback_terms_any")
        if not isinstance(diagnostic_terms, list) or not diagnostic_terms:
            raise LocalEvaluationContractError("feedback_terms_any must be a nonempty list")
        if any(not isinstance(term, str) or not term for term in diagnostic_terms):
            raise LocalEvaluationContractError("feedback terms must be nonempty text")
    return len(items)


def _validate_adapters(adapters: object) -> tuple[str, ...]:
    if not isinstance(adapters, list) or not adapters:
        raise LocalEvaluationContractError("adapters must be a nonempty list")
    identifiers: list[str] = []
    for index, adapter in enumerate(adapters):
        _require_exact_fields(adapter, _ADAPTER_FIELDS, f"adapter {index}")
        _require_exact(adapter, "schema", ADAPTER_SCHEMA)
        _require_exact(adapter, "state", DECLARED_UNQUALIFIED_STATE)
        identifier = _require_text(adapter.get("adapter_id"), "adapter_id")
        if identifier in identifiers:
            raise LocalEvaluationContractError(f"duplicate adapter_id: {identifier}")
        identifiers.append(identifier)
        if adapter.get("input_renderer") not in ALLOWED_RENDERERS:
            raise LocalEvaluationContractError("adapter input_renderer is not declared")
        if adapter.get("output_parser") not in ALLOWED_PARSERS:
            raise LocalEvaluationContractError("adapter output_parser is not declared")
        _require_text(adapter.get("semantic_role"), "semantic_role")
        _require_text(adapter.get("notes"), "notes", 512)
    return tuple(identifiers)

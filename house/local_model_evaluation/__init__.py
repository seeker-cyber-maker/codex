"""Source-only local rubric evaluation contracts for Dream House.

This package freezes test cases and validates adapter declarations.  It cannot
load a model, call a provider, train weights, start a worker, or promote a
candidate.
"""

from .contract import (
    LocalEvaluationContractError,
    canonical_fixture_projection_sha256,
    parse_adapter_score,
    render_rubric_prompt,
    require_execution_authority,
    validate_source_only_contract,
)

__all__ = [
    "LocalEvaluationContractError",
    "canonical_fixture_projection_sha256",
    "parse_adapter_score",
    "render_rubric_prompt",
    "require_execution_authority",
    "validate_source_only_contract",
]

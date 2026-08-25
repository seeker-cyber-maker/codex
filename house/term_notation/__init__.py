"""Pure TERM notation parsing primitives."""

from .compatibility import (
    COMPATIBILITY_MANIFEST_SCHEMA,
    FIXTURE_SET_SCHEMA,
    PREFLIGHT_STATE,
    CompatibilityPreflightError,
    CompatibilityPreflightReport,
    canonical_fixture_projection_sha256,
    require_execution_authority,
    validate_preflight,
)
from .parser import (
    NOTATION_ID,
    TERM_RECORD_SCHEMA,
    TermNotationError,
    TermRecord,
    missing_preference,
    parse_record,
)

__all__ = [
    "COMPATIBILITY_MANIFEST_SCHEMA",
    "FIXTURE_SET_SCHEMA",
    "NOTATION_ID",
    "PREFLIGHT_STATE",
    "TERM_RECORD_SCHEMA",
    "CompatibilityPreflightError",
    "CompatibilityPreflightReport",
    "TermNotationError",
    "TermRecord",
    "canonical_fixture_projection_sha256",
    "missing_preference",
    "parse_record",
    "require_execution_authority",
    "validate_preflight",
]

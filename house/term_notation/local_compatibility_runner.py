"""Deterministic core for the sealed local TERM compatibility experiment.

This module intentionally has no model, provider, task, relay, network, or
filesystem side effects. A later thin operation wrapper may supply local model
output, but this scorer cannot dispatch or promote a candidate.
"""

from __future__ import annotations

from collections.abc import Mapping

from .parser import TermNotationError, parse_record

CONDITIONS = (
    "ORDINARY_UNMARKED",
    "ORDINARY_READABLE_REPAIR",
    "TERM_MARKER_ONLY",
    "TERM_FULL_FORM",
    "OVERCOMPRESSED_CONTROL",
)


def expected_record(fixture: Mapping[str, object]) -> str:
    """Return the one canonical repair record for a frozen fixture."""

    return (
        f"TERM? {fixture['candidate']}\n"
        f"MEAN {fixture['intended_meaning']}\n"
        f"NOT {fixture['excluded_meaning']}\n"
        f"SCOPE {fixture['scope']}"
    )


def render_condition(condition: str, fixture: Mapping[str, object]) -> str:
    """Render one fixed presentation while preserving the same requested repair."""

    expected = expected_record(fixture)
    instruction = "Reply with exactly one TERM_NOTATION/1 record and no other text."
    if condition == "ORDINARY_UNMARKED":
        return f"{instruction}\nRepair this ambiguous term using the stated meaning, exclusion, and scope.\n{expected}"
    if condition == "ORDINARY_READABLE_REPAIR":
        return f"{instruction}\nThe term needs a readable scoped repair. Preserve all four facts.\n{expected}"
    if condition == "TERM_MARKER_ONLY":
        return f"{instruction}\nTERM? {fixture['candidate']}\nMeaning: {fixture['intended_meaning']}\nNot: {fixture['excluded_meaning']}\nScope: {fixture['scope']}"
    if condition == "TERM_FULL_FORM":
        return f"{instruction}\nReturn this valid record unchanged:\n{expected}"
    if condition == "OVERCOMPRESSED_CONTROL":
        return f"{instruction}\n{fixture['candidate']} | {fixture['intended_meaning']} | {fixture['excluded_meaning']} | {fixture['scope']}"
    raise ValueError("unknown frozen TERM condition")


def score_output(fixture: Mapping[str, object], output: str) -> dict[str, object]:
    """Fail closed on malformed TERM output, then compare canonical fields."""

    try:
        actual = parse_record(output).to_dict()
    except TermNotationError as error:
        return {"parse_ok": False, "exact_fields": False, "error": str(error)}
    expected = parse_record(expected_record(fixture)).to_dict()
    fields = ("candidate", "meaning", "excluded_meaning", "scope")
    return {
        "parse_ok": True,
        "exact_fields": all(actual[field] == expected[field] for field in fields),
        "error": None,
        "parsed": {field: actual[field] for field in fields},
    }

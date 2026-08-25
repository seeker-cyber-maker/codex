"""Fail-closed parser for one TERM_NOTATION/1 record.

The parser is deliberately pure: it reads no files, performs no I/O, and has
no integration with prompts, hooks, tasks, relays, execution, or authority.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

NOTATION_ID = "TERM_NOTATION/1"
TERM_RECORD_SCHEMA = "dream-house/term-notation-record/1"
MAX_RECORD_BYTES = 4096
MAX_VALUE_CHARACTERS = 1024
MAX_CONTEXT_IDENTIFIER_CHARACTERS = 128
MAX_BLOCK_LINES = 4

_NORMALIZED_FIELDS = MappingProxyType(
    {
        "MEAN": "meaning",
        "NOT": "excluded_meaning",
        "SCOPE": "scope",
        "CTX": "context_generation",
        "WHY": "reason",
        "ALT": "alternative",
    }
)
_PREFERENCE_VALUES = frozenset(
    {"preferred", "not_preferred", "no_preference", "undetermined"}
)
_CONTEXT_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")
_CONTROL_CHARACTER_PATTERN = re.compile(r"[\x00-\x09\x0b\x0c\x0e-\x1f\x7f]")


class TermNotationError(ValueError):
    """Raised when an input is not exactly one valid TERM record."""


@dataclass(frozen=True)
class TermRecord:
    """Normalized, data-only representation of one TERM notation record."""

    kind: str
    operator: str
    candidate: str | None = None
    meaning: str | None = None
    excluded_meaning: str | None = None
    scope: str | None = None
    context_generation: str | None = None
    reason: str | None = None
    target: str | None = None
    preference: str | None = None
    alternative: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        """Return the stable record projection without causing side effects."""

        return {
            "schema": TERM_RECORD_SCHEMA,
            "notation_id": NOTATION_ID,
            "kind": self.kind,
            "operator": self.operator,
            "candidate": self.candidate,
            "meaning": self.meaning,
            "excluded_meaning": self.excluded_meaning,
            "scope": self.scope,
            "context_generation": self.context_generation,
            "reason": self.reason,
            "target": self.target,
            "preference": self.preference,
            "alternative": self.alternative,
        }


def parse_record(text: str) -> TermRecord:
    """Parse exactly one TERM_NOTATION/1 record or fail closed."""

    value = _prepare_input(text)
    if value.startswith("TERM? "):
        return _parse_repair_query(value)
    if value.startswith("TERM= "):
        return _parse_inline_term(value, operator="TERM=")
    if value.startswith("TERM~ "):
        return _parse_inline_term(value, operator="TERM~")
    if value.startswith("PREF? "):
        return _parse_preference_query(value)
    if value.startswith("PREF= "):
        return _parse_preference_response(value)
    raise TermNotationError("unknown or malformed TERM notation operator")


def missing_preference() -> TermRecord:
    """Create the wrapper-only projection for an omitted required response."""

    return TermRecord(
        kind="preference_response",
        operator="PREF=",
        target=NOTATION_ID,
        preference="not_stated",
    )


def _prepare_input(text: str) -> str:
    if not isinstance(text, str):
        raise TermNotationError("record must be text")
    if len(text.encode("utf-8")) > MAX_RECORD_BYTES:
        raise TermNotationError("record exceeds byte limit")
    if _CONTROL_CHARACTER_PATTERN.search(text):
        raise TermNotationError("record contains a forbidden control character")
    value = text.strip()
    if not value:
        raise TermNotationError("record is empty")
    return value


def _validate_value(value: str, label: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise TermNotationError(f"{label} cannot be empty")
    if "|" in normalized or "\n" in normalized or "\r" in normalized:
        raise TermNotationError(f"{label} contains an ambiguous delimiter")
    if len(normalized) > MAX_VALUE_CHARACTERS:
        raise TermNotationError(f"{label} exceeds character limit")
    return normalized


def _parse_repair_query(value: str) -> TermRecord:
    lines = value.splitlines()
    if len(lines) > MAX_BLOCK_LINES:
        raise TermNotationError("repair query has too many detail lines")
    candidate = _validate_value(lines[0][len("TERM? ") :], "candidate")
    fields: dict[str, str] = {}
    declared_order = ("MEAN", "NOT", "SCOPE")
    last_index = -1
    for line in lines[1:]:
        match = re.fullmatch(r"(MEAN|NOT|SCOPE) (.+)", line)
        if match is None:
            raise TermNotationError("repair query contains an unknown or malformed field")
        key, raw = match.groups()
        if key in fields:
            raise TermNotationError(f"duplicate field: {key}")
        field_index = declared_order.index(key)
        if field_index <= last_index:
            raise TermNotationError("repair query fields are not canonically ordered")
        last_index = field_index
        fields[key] = _validate_value(raw, key)
    normalized = _normalize_fields(fields)
    return TermRecord(
        kind="repair_query",
        operator="TERM?",
        candidate=candidate,
        meaning=normalized.get("meaning"),
        excluded_meaning=normalized.get("excluded_meaning"),
        scope=normalized.get("scope"),
    )


def _parse_inline_term(value: str, *, operator: str) -> TermRecord:
    if "\n" in value or "\r" in value:
        raise TermNotationError(f"{operator} must use one inline record")
    parts = value.split(" | ")
    candidate = _validate_value(parts[0][len(operator) + 1 :], "candidate")
    if operator == "TERM=":
        field_order = ("MEAN", "SCOPE", "CTX")
        kind = "working_definition"
    else:
        field_order = ("SCOPE", "WHY")
        kind = "unresolved"
    fields = _parse_named_segments(parts[1:], field_order)
    missing = set(field_order).difference(fields)
    if missing:
        raise TermNotationError(f"missing required fields: {', '.join(sorted(missing))}")
    if operator == "TERM=" and not _CONTEXT_PATTERN.fullmatch(fields["CTX"]):
        raise TermNotationError("CTX must be a bounded context identifier")
    normalized = _normalize_fields(fields)
    return TermRecord(
        kind=kind,
        operator=operator,
        candidate=candidate,
        meaning=normalized.get("meaning"),
        scope=normalized.get("scope"),
        context_generation=normalized.get("context_generation"),
        reason=normalized.get("reason"),
    )


def _parse_named_segments(parts: list[str], field_order: tuple[str, ...]) -> dict[str, str]:
    fields: dict[str, str] = {}
    for index, part in enumerate(parts):
        match = re.fullmatch(r"([A-Z]+) (.+)", part)
        if match is None:
            raise TermNotationError("inline record contains a malformed field")
        key, raw = match.groups()
        if key not in field_order:
            raise TermNotationError(f"unknown field: {key}")
        if key in fields:
            raise TermNotationError(f"duplicate field: {key}")
        if index >= len(field_order) or key != field_order[index]:
            raise TermNotationError("inline fields are not canonically ordered")
        fields[key] = _validate_value(raw, key)
    return fields


def _normalize_fields(fields: Mapping[str, str]) -> dict[str, str]:
    return {_NORMALIZED_FIELDS[key]: value for key, value in fields.items()}


def _parse_preference_query(value: str) -> TermRecord:
    if value != f"PREF? target={NOTATION_ID}":
        raise TermNotationError("preference query must use the exact notation target")
    return TermRecord(
        kind="preference_query",
        operator="PREF?",
        target=NOTATION_ID,
    )


def _parse_preference_response(value: str) -> TermRecord:
    if "\n" in value or "\r" in value:
        raise TermNotationError("PREF= must use one inline record")
    parts = value.split(" | ")
    if not parts or parts[0] != f"PREF= target={NOTATION_ID}":
        raise TermNotationError("preference response must use the exact notation target")
    if len(parts) not in {2, 3}:
        raise TermNotationError("preference response has the wrong field count")
    preference = parts[1]
    if preference not in _PREFERENCE_VALUES:
        raise TermNotationError("unknown or wrapper-only preference value")
    alternative = None
    if len(parts) == 3:
        if preference != "not_preferred":
            raise TermNotationError("ALT is allowed only with not_preferred")
        match = re.fullmatch(r"ALT (.+)", parts[2])
        if match is None:
            raise TermNotationError("preference alternative is malformed")
        alternative = _validate_value(match.group(1), "ALT")
    return TermRecord(
        kind="preference_response",
        operator="PREF=",
        target=NOTATION_ID,
        preference=preference,
        alternative=alternative,
    )

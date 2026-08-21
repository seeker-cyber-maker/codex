"""Restricted RFC 8785-style canonical JSON for authority fixtures.

The profile deliberately rejects floating-point values and accepts only signed
64-bit integers. Object property names are sorted by UTF-16 code units, as JCS
requires. This is an isolated fixture implementation, not the live authority
path.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any, NoReturn

INT64_MIN = -(2**63)
INT64_MAX = 2**63 - 1


class CanonicalError(ValueError):
    """Typed canonicalization failure."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _fail(code: str, message: str) -> NoReturn:
    raise CanonicalError(code, message)


def _check_string(value: str) -> None:
    if any(0xD800 <= ord(character) <= 0xDFFF for character in value):
        _fail("CANON_SURROGATE", "lone UTF-16 surrogate is not admitted")


def _validate(value: Any) -> None:
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, int):
        if not INT64_MIN <= value <= INT64_MAX:
            _fail("CANON_INTEGER_RANGE", "integer is outside signed 64-bit range")
        return
    if isinstance(value, float):
        _fail("CANON_FLOAT", "floating-point values are not admitted")
    if isinstance(value, str):
        _check_string(value)
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                _fail("CANON_KEY_TYPE", "object keys must be strings")
            _check_string(key)
            _validate(item)
        return
    if isinstance(value, Sequence) and not isinstance(
        value, (str, bytes, bytearray, memoryview)
    ):
        for item in value:
            _validate(item)
        return
    _fail("CANON_TYPE", f"unsupported JSON value type: {type(value).__name__}")


def _utf16_sort_key(value: str) -> bytes:
    _check_string(value)
    return value.encode("utf-16-be")


def _encode(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, Mapping):
        keys = sorted(value, key=_utf16_sort_key)
        return (
            "{"
            + ",".join(f"{_encode(key)}:{_encode(value[key])}" for key in keys)
            + "}"
        )
    if isinstance(value, Sequence):
        return "[" + ",".join(_encode(item) for item in value) + "]"
    _fail("CANON_TYPE", f"unsupported JSON value type: {type(value).__name__}")


def canonical_text(value: Any) -> str:
    """Return canonical JSON text for the restricted profile."""

    _validate(value)
    return _encode(value)


def canonical_bytes(value: Any) -> bytes:
    """Return UTF-8 canonical JSON bytes for the restricted profile."""

    return canonical_text(value).encode("utf-8")


def _object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _fail("CANON_DUPLICATE_KEY", f"duplicate object key: {key!r}")
        result[key] = value
    return result


def _parse_int(raw: str) -> int:
    value = int(raw)
    if not INT64_MIN <= value <= INT64_MAX:
        _fail("CANON_INTEGER_RANGE", "integer is outside signed 64-bit range")
    return value


def _reject_float(_raw: str) -> NoReturn:
    _fail("CANON_FLOAT", "floating-point values are not admitted")


def _reject_constant(_raw: str) -> NoReturn:
    _fail("CANON_CONSTANT", "non-finite JSON constants are not admitted")


def strict_loads(data: str | bytes) -> Any:
    """Parse strict UTF-8 JSON while retaining duplicate-key detection."""

    if isinstance(data, bytes):
        try:
            text = data.decode("utf-8", errors="strict")
        except UnicodeDecodeError as error:
            raise CanonicalError("CANON_UTF8", "input is not valid UTF-8") from error
    elif isinstance(data, str):
        text = data
    else:
        _fail("CANON_INPUT_TYPE", "JSON input must be str or bytes")
    _check_string(text)
    try:
        value = json.loads(
            text,
            object_pairs_hook=_object_pairs,
            parse_int=_parse_int,
            parse_float=_reject_float,
            parse_constant=_reject_constant,
        )
    except CanonicalError:
        raise
    except json.JSONDecodeError as error:
        raise CanonicalError("CANON_JSON", "input is not valid JSON") from error
    _validate(value)
    return value

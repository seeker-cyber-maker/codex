"""In-memory capability validation for a future loopback-only WebView."""

from __future__ import annotations

import base64
import hashlib
import json
import re
import secrets
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import SplitResult, urlsplit

MAX_CAPABILITY_RECORDS = 256
MAX_CAPABILITY_TTL_SECONDS = 300
TOKEN_BYTES = 32

_AUDIENCE = "com.codex.house.terminal-companion"
_ROUTE_PREFIX = "/v1/display/"
_TOKEN = re.compile(r"^[A-Za-z0-9_-]{43}$")
_ALLOWED_HOSTS = {"127.0.0.1", "::1"}


class CapabilityValidationError(ValueError):
    """A fail-closed capability rejection with an internal diagnostic code."""

    def __init__(self, code: str) -> None:
        super().__init__("capability rejected")
        self.code = code


@dataclass(frozen=True)
class CapabilityGrant:
    """Ephemeral bearer URL returned once to the future registration boundary."""

    url: str = field(repr=False)
    audience: str
    expires_at_ns: int


@dataclass
class _CapabilityRecord:
    capability_id: str
    canonical_authority: str
    audience: str
    issued_at_ns: int
    expires_at_ns: int
    consumed: bool = False


def _reject(code: str) -> CapabilityValidationError:
    return CapabilityValidationError(code)


def _require_int(value: object, field: str, *, minimum: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
        raise _reject(f"INVALID_{field.upper()}")
    return value


def _canonical_authority(host: str, port: int) -> str:
    if host not in _ALLOWED_HOSTS:
        raise _reject("NON_LOOPBACK_HOST")
    port = _require_int(port, "port", minimum=1024)
    if port > 65535:
        raise _reject("INVALID_PORT")
    return f"[{host}]:{port}" if host == "::1" else f"{host}:{port}"


def _canonical_bytes(value: dict[str, Any]) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def _token_digest(token: str) -> bytes:
    return hashlib.sha256(token.encode("ascii")).digest()


def _parse_url(url: object) -> tuple[SplitResult, str]:
    if not isinstance(url, str) or not url or len(url) > 2048:
        raise _reject("INVALID_URL")
    try:
        parsed = urlsplit(url)
        port = parsed.port
    except (TypeError, ValueError):
        raise _reject("INVALID_URL") from None
    if parsed.scheme != "http":
        raise _reject("INVALID_SCHEME")
    if parsed.username is not None or parsed.password is not None:
        raise _reject("USERINFO_PROHIBITED")
    if parsed.query or parsed.fragment:
        raise _reject("URL_SUFFIX_PROHIBITED")
    if parsed.hostname not in _ALLOWED_HOSTS or port is None:
        raise _reject("NON_LOOPBACK_HOST")
    authority = _canonical_authority(parsed.hostname, port)
    if parsed.netloc != authority:
        raise _reject("NON_CANONICAL_AUTHORITY")
    if not parsed.path.startswith(_ROUTE_PREFIX):
        raise _reject("INVALID_PATH")
    token = parsed.path.removeprefix(_ROUTE_PREFIX)
    if not _TOKEN.fullmatch(token):
        raise _reject("INVALID_TOKEN")
    if url != f"http://{authority}{_ROUTE_PREFIX}{token}":
        raise _reject("NON_CANONICAL_URL")
    return parsed, token


class LoopbackCapabilityValidator:
    """Issue and atomically consume bounded, single-use in-memory capabilities."""

    def __init__(
        self,
        *,
        entropy: Callable[[int], bytes] = secrets.token_bytes,
        max_records: int = MAX_CAPABILITY_RECORDS,
    ) -> None:
        self._entropy = entropy
        self._max_records = _require_int(max_records, "max_records", minimum=1)
        if self._max_records > MAX_CAPABILITY_RECORDS:
            raise _reject("INVALID_MAX_RECORDS")
        self._records: dict[bytes, _CapabilityRecord] = {}
        self._lock = threading.Lock()

    def _purge_expired(self, now_ns: int) -> None:
        expired = [
            digest
            for digest, record in self._records.items()
            if now_ns >= record.expires_at_ns
        ]
        for digest in expired:
            del self._records[digest]

    def issue(
        self,
        *,
        host: str,
        port: int,
        now_ns: int,
        ttl_seconds: int,
        audience: str = _AUDIENCE,
    ) -> CapabilityGrant:
        """Create one capability while retaining only its digest in validator state."""
        authority = _canonical_authority(host, port)
        now_ns = _require_int(now_ns, "now_ns", minimum=0)
        ttl_seconds = _require_int(ttl_seconds, "ttl_seconds", minimum=1)
        if ttl_seconds > MAX_CAPABILITY_TTL_SECONDS:
            raise _reject("TTL_EXCEEDS_LIMIT")
        if audience != _AUDIENCE:
            raise _reject("INVALID_AUDIENCE")

        raw = self._entropy(TOKEN_BYTES)
        if not isinstance(raw, bytes) or len(raw) != TOKEN_BYTES:
            raise _reject("INVALID_ENTROPY")
        token = base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")
        if not _TOKEN.fullmatch(token):
            raise _reject("INVALID_ENTROPY")
        digest = _token_digest(token)
        expires_at_ns = now_ns + ttl_seconds * 1_000_000_000
        capability_id = hashlib.sha256(
            b"codex-house-iterm-capability-id/1\0"
            + digest
            + _canonical_bytes(
                {
                    "audience": audience,
                    "authority": authority,
                    "issued_at_ns": now_ns,
                    "expires_at_ns": expires_at_ns,
                }
            )
        ).hexdigest()
        record = _CapabilityRecord(
            capability_id=capability_id,
            canonical_authority=authority,
            audience=audience,
            issued_at_ns=now_ns,
            expires_at_ns=expires_at_ns,
        )
        with self._lock:
            self._purge_expired(now_ns)
            if len(self._records) >= self._max_records:
                raise _reject("CAPACITY_EXHAUSTED")
            if digest in self._records:
                raise _reject("TOKEN_COLLISION")
            self._records[digest] = record
        return CapabilityGrant(
            url=f"http://{authority}{_ROUTE_PREFIX}{token}",
            audience=audience,
            expires_at_ns=expires_at_ns,
        )

    def consume(
        self,
        *,
        url: str,
        method: str,
        origin: str | None,
        audience: str,
        now_ns: int,
    ) -> dict[str, Any]:
        """Atomically consume one exact top-level GET capability."""
        parsed, token = _parse_url(url)
        if method != "GET":
            raise _reject("METHOD_PROHIBITED")
        if origin is not None:
            raise _reject("ORIGIN_PROHIBITED")
        if audience != _AUDIENCE:
            raise _reject("INVALID_AUDIENCE")
        now_ns = _require_int(now_ns, "now_ns", minimum=0)
        digest = _token_digest(token)

        with self._lock:
            record = self._records.get(digest)
            if record is None:
                raise _reject("UNKNOWN_CAPABILITY")
            if now_ns < record.issued_at_ns:
                raise _reject("CLOCK_ROLLBACK")
            if now_ns >= record.expires_at_ns:
                del self._records[digest]
                raise _reject("EXPIRED_CAPABILITY")
            if record.consumed:
                raise _reject("REPLAYED_CAPABILITY")
            if parsed.netloc != record.canonical_authority:
                raise _reject("AUDIENCE_AUTHORITY_MISMATCH")
            if audience != record.audience:
                raise _reject("INVALID_AUDIENCE")
            record.consumed = True

        receipt_body = {
            "schema": "codex-house-iterm-capability-consumption/1",
            "capability_id": record.capability_id,
            "audience": audience,
            "authority": record.canonical_authority,
            "method": method,
            "consumed_at_ns": now_ns,
            "expires_at_ns": record.expires_at_ns,
            "transport": "NOT_ATTEMPTED",
            "iterm_api_registration": "NOT_ATTEMPTED",
            "terminal_input": "PROHIBITED",
        }
        return {
            **receipt_body,
            "receipt_id": hashlib.sha256(_canonical_bytes(receipt_body)).hexdigest(),
        }

    def active_record_count(self, *, now_ns: int) -> int:
        """Return a bounded diagnostic count without exposing token digests."""
        now_ns = _require_int(now_ns, "now_ns", minimum=0)
        with self._lock:
            self._purge_expired(now_ns)
            return len(self._records)

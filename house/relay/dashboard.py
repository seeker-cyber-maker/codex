"""Pure request adapter for a future loopback-only relay dashboard.

This module does not bind a port. A separately qualified listener may call the
adapter later, but write-like paths remain deliberately unavailable here.
"""

from __future__ import annotations

import re
from typing import Any

from .core import Relay, RelayError
from .directory import RelayDirectory, RelayDirectoryError

_ADDRESS_PATH = re.compile(r"^/v1/relay/directory/([a-z0-9][a-z0-9._:-]{1,127})$")
_CAPABILITY_PATH = re.compile(r"^/v1/relay/capability/([a-z0-9][a-z0-9._:-]{1,127})$")
_STATUS_PATH = re.compile(r"^/v1/relay/envelope/([a-z0-9][a-z0-9._:-]{1,127})$")
_WRITE_PATHS = frozenset(
    {
        "/v1/relay/submit",
        "/v1/relay/receive",
        "/v1/relay/acknowledge",
    }
)


class RelayDashboardAdapter:
    """Prepare safe dashboard responses without serving HTTP or invoking workers."""

    def __init__(self, directory: RelayDirectory, relay: Relay) -> None:
        self._directory = directory
        self._relay = relay

    @staticmethod
    def _response(status: int, body: dict[str, Any]) -> dict[str, Any]:
        return {
            "schema": "codex-house-relay-dashboard-response/1",
            "status": status,
            "body": body,
            "transport": "NOT_BOUND",
        }

    def handle(self, method: str, target: str) -> dict[str, Any]:
        if not isinstance(method, str) or not isinstance(target, str):
            return self._response(404, {"error": "not_found"})
        if method != "GET":
            if target in _WRITE_PATHS:
                return self._response(
                    418,
                    {
                        "error": "integration_pending",
                        "dispatch": "NOT_ATTEMPTED",
                        "authority": "NOT_GRANTED",
                    },
                )
            return self._response(404, {"error": "not_found"})
        for pattern, reader in (
            (_ADDRESS_PATH, self._directory.address),
            (_CAPABILITY_PATH, self._directory.find_capability),
            (_STATUS_PATH, self._relay.get),
        ):
            matched = pattern.fullmatch(target)
            if matched is None:
                continue
            try:
                return self._response(200, reader(matched.group(1)))
            except (RelayDirectoryError, RelayError):
                return self._response(404, {"error": "not_found"})
        return self._response(404, {"error": "not_found"})

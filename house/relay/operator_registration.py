"""Offline operator-registration contract for a frozen relay dashboard document."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from house.operator_surface import builtin_registry

from .dashboard_view import render_dashboard_html


def _digest(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def build_relay_preview_registration(response: object) -> dict[str, Any]:
    """Prepare an exact display-only operator request without issuing a capability."""
    document = render_dashboard_html(response)
    document_sha256 = hashlib.sha256(document.encode("utf-8")).hexdigest()
    command = builtin_registry().prepare_request(
        "codex.house.relay.preview",
        target={"kind": "relay_dashboard_document", "id": document_sha256},
    )
    payload: dict[str, Any] = {
        "schema": "codex-house-relay-preview-registration/1",
        "state": "PREPARED_UNAUTHORIZED",
        "document_sha256": document_sha256,
        "target": command["target"],
        "command": command,
        "operator_action": "EXPLICIT_START_AND_CAPABILITY_HANDOFF_REQUIRED",
        "capability": "NOT_ISSUED",
        "viewer_start": "NOT_ATTEMPTED",
        "browser_launch": "NOT_ATTEMPTED",
        "iterm_api_registration": "NOT_ATTEMPTED",
        "worker_dispatch": "NOT_ATTEMPTED",
        "authority": "NOT_GRANTED",
        "reverse_channel": "PROHIBITED",
    }
    return {**payload, "registration_sha256": _digest(payload)}

"""Inert operator-facing rendering of a sealed relay preview registration."""

from __future__ import annotations

import hashlib
import html
import json
import re
from collections.abc import Mapping
from typing import Any

MAX_CARD_BYTES = 100_000
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_REGISTRATION_FIELDS = frozenset(
    {
        "schema",
        "state",
        "document_sha256",
        "target",
        "command",
        "operator_action",
        "capability",
        "viewer_start",
        "browser_launch",
        "iterm_api_registration",
        "worker_dispatch",
        "authority",
        "reverse_channel",
        "registration_sha256",
    }
)
_COMMAND_FIELDS = frozenset(
    {
        "schema",
        "command_id",
        "target",
        "arguments",
        "authority",
        "state",
        "dispatch",
        "request_sha256",
    }
)


class RelayPreviewCardError(ValueError):
    """A registration is not safe to present as a static operator card."""


def _digest(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _require_digest(value: object, label: str) -> str:
    if not isinstance(value, str) or not _DIGEST.fullmatch(value):
        raise RelayPreviewCardError(f"invalid {label}")
    return value


def _validate_command(command: object, target: Mapping[str, str]) -> str:
    if not isinstance(command, Mapping) or set(command) != _COMMAND_FIELDS:
        raise RelayPreviewCardError("command fields are not exact")
    if command.get("schema") != "codex-house-command-request/1":
        raise RelayPreviewCardError("invalid command schema")
    if command.get("command_id") != "codex.house.relay.preview":
        raise RelayPreviewCardError("invalid command id")
    if command.get("target") != target or command.get("arguments") != {}:
        raise RelayPreviewCardError("invalid command target")
    if command.get("authority") != "DISPLAY_ONLY":
        raise RelayPreviewCardError("invalid command authority")
    if command.get("state") != "PREPARED_UNAUTHORIZED":
        raise RelayPreviewCardError("invalid command state")
    if command.get("dispatch") != "NOT_ATTEMPTED":
        raise RelayPreviewCardError("invalid command dispatch")
    request_sha256 = _require_digest(command.get("request_sha256"), "command digest")
    unsigned = {key: value for key, value in command.items() if key != "request_sha256"}
    if _digest(unsigned) != request_sha256:
        raise RelayPreviewCardError("command digest does not match")
    return request_sha256


def _validated_registration(registration: object) -> dict[str, str]:
    if (
        not isinstance(registration, Mapping)
        or set(registration) != _REGISTRATION_FIELDS
    ):
        raise RelayPreviewCardError("registration fields are not exact")
    if registration.get("schema") != "codex-house-relay-preview-registration/1":
        raise RelayPreviewCardError("invalid registration schema")
    document_sha256 = _require_digest(
        registration.get("document_sha256"), "document digest"
    )
    target = registration.get("target")
    if target != {"kind": "relay_dashboard_document", "id": document_sha256}:
        raise RelayPreviewCardError("invalid registration target")
    if not isinstance(target, Mapping):  # Keeps type check explicit for the command.
        raise RelayPreviewCardError("invalid registration target")
    normalized_target = {"kind": document_sha256, "id": document_sha256}
    normalized_target["kind"] = "relay_dashboard_document"
    request_sha256 = _validate_command(registration.get("command"), normalized_target)
    required_values = {
        "state": "PREPARED_UNAUTHORIZED",
        "operator_action": "EXPLICIT_START_AND_CAPABILITY_HANDOFF_REQUIRED",
        "capability": "NOT_ISSUED",
        "viewer_start": "NOT_ATTEMPTED",
        "browser_launch": "NOT_ATTEMPTED",
        "iterm_api_registration": "NOT_ATTEMPTED",
        "worker_dispatch": "NOT_ATTEMPTED",
        "authority": "NOT_GRANTED",
        "reverse_channel": "PROHIBITED",
    }
    for field, expected in required_values.items():
        if registration.get(field) != expected:
            raise RelayPreviewCardError(f"invalid registration {field}")
    registration_sha256 = _require_digest(
        registration.get("registration_sha256"), "registration digest"
    )
    unsigned = {
        key: value
        for key, value in registration.items()
        if key != "registration_sha256"
    }
    if _digest(unsigned) != registration_sha256:
        raise RelayPreviewCardError("registration digest does not match")
    return {
        "document_sha256": document_sha256,
        "request_sha256": request_sha256,
        "registration_sha256": registration_sha256,
    }


def render_relay_preview_card_html(registration: object) -> str:
    """Render a descriptor-only, no-interaction operator preview card."""
    fields = _validated_registration(registration)
    document = "".join(
        (
            '<!doctype html><html lang="en"><head><meta charset="utf-8">',
            '<meta http-equiv="Content-Security-Policy" content="default-src ',
            "'none'; style-src 'unsafe-inline'; img-src 'none'; connect-src 'none'; ",
            "form-action 'none'; base-uri 'none'; frame-ancestors 'none'\">",
            '<meta name="referrer" content="no-referrer">',
            '<meta name="viewport" content="width=device-width,initial-scale=1">',
            "<title>🏠 Relay preview ready</title><style>",
            "html{color-scheme:dark}body{margin:0;padding:14px;background:#101310;",
            "color:#d8e8d8;font:13px ui-monospace,SFMono-Regular,Menlo,monospace}",
            ".summary{color:#9fc99f;margin:0 0 12px}.card{border:1px solid #304630;",
            "border-radius:8px;padding:10px;background:#151a15}dl{display:grid;",
            "grid-template-columns:max-content 1fr;gap:5px 10px;margin:0}dt{color:#8a9f8a}",
            "dd{margin:0;overflow-wrap:anywhere}code{color:#d8e8d8}</style></head><body>",
            '<p class="summary">Observe only · Relay preview ready</p><main class="card"><dl>',
            "<dt>Command</dt><dd><code>codex.house.relay.preview</code></dd>",
            "<dt>Action</dt><dd>EXPLICIT_START_AND_CAPABILITY_HANDOFF_REQUIRED</dd>",
            "<dt>Document</dt><dd><code>",
            html.escape(fields["document_sha256"], quote=True),
            "</code></dd><dt>Request</dt><dd><code>",
            html.escape(fields["request_sha256"], quote=True),
            "</code></dd><dt>Registration</dt><dd><code>",
            html.escape(fields["registration_sha256"], quote=True),
            "</code></dd><dt>State</dt><dd>PREPARED_UNAUTHORIZED · NOT_ISSUED · NOT_ATTEMPTED</dd>",
            "</dl></main></body></html>",
        )
    )
    if len(document.encode("utf-8")) > MAX_CARD_BYTES:
        raise RelayPreviewCardError(f"preview card exceeds {MAX_CARD_BYTES} bytes")
    return document

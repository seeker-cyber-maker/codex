"""Static, inert rendering of one already-frozen relay dashboard response."""

from __future__ import annotations

import html
import json
from collections.abc import Mapping

MAX_BODY_BYTES = 1_000_000
MAX_DOCUMENT_BYTES = 2_000_000
RESPONSE_SCHEMA = "codex-house-relay-dashboard-response/1"
RESPONSE_FIELDS = frozenset({"schema", "status", "body", "transport"})
ALLOWED_STATUSES = frozenset({200, 404, 418})


class RelayDashboardViewError(ValueError):
    """A response cannot safely become a static dashboard document."""


def _canonical_json(value: object, label: str) -> str:
    try:
        encoded = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
    except (TypeError, ValueError) as exc:
        raise RelayDashboardViewError(f"{label} is not JSON-safe") from exc
    if len(encoded.encode("utf-8")) > MAX_BODY_BYTES:
        raise RelayDashboardViewError(f"{label} exceeds {MAX_BODY_BYTES} bytes")
    return encoded


def render_dashboard_html(response: object) -> str:
    """Render an adapter response without calling any relay or transport API."""
    if not isinstance(response, Mapping) or set(response) != RESPONSE_FIELDS:
        raise RelayDashboardViewError("response fields are not exact")
    if response.get("schema") != RESPONSE_SCHEMA:
        raise RelayDashboardViewError("invalid response schema")
    status = response.get("status")
    if isinstance(status, bool) or status not in ALLOWED_STATUSES:
        raise RelayDashboardViewError("invalid response status")
    if response.get("transport") != "NOT_BOUND":
        raise RelayDashboardViewError("response transport must be NOT_BOUND")
    body = response.get("body")
    if not isinstance(body, Mapping):
        raise RelayDashboardViewError("response body must be an object")
    body_json = _canonical_json(dict(body), "response body")
    document = "".join(
        (
            '<!doctype html><html lang="en"><head><meta charset="utf-8">',
            '<meta http-equiv="Content-Security-Policy" content="default-src ',
            "'none'; style-src 'unsafe-inline'; img-src 'none'; connect-src 'none'; ",
            "form-action 'none'; base-uri 'none'; frame-ancestors 'none'\">",
            '<meta name="referrer" content="no-referrer">',
            '<meta name="viewport" content="width=device-width,initial-scale=1">',
            "<title>🏠 Relay dashboard</title><style>",
            "html{color-scheme:dark}body{margin:0;padding:14px;background:#101310;",
            "color:#d8e8d8;font:13px ui-monospace,SFMono-Regular,Menlo,monospace}",
            ".summary{color:#9fc99f;margin:0 0 12px}.card{border:1px solid #304630;",
            "border-radius:8px;padding:10px;background:#151a15}pre{margin:0;white-space:pre-wrap;",
            "overflow-wrap:anywhere;background:#0b0e0b;padding:8px;border-radius:5px}",
            '</style></head><body><p class="summary">Observe only · Relay dashboard · ',
            str(status),
            ' · transport not bound</p><main class="card"><pre>',
            html.escape(body_json, quote=True),
            "</pre></main></body></html>",
        )
    )
    if len(document.encode("utf-8")) > MAX_DOCUMENT_BYTES:
        raise RelayDashboardViewError(
            f"dashboard document exceeds {MAX_DOCUMENT_BYTES} bytes"
        )
    return document

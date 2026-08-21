"""Offline rendering contract for a future iTerm2 toolbelt WebView."""

from __future__ import annotations

import html
from typing import Any

from .display_batch import verify_display_chain
from .projector import CompanionProjectionError

MAX_WEBVIEW_BATCHES = 64
MAX_WEBVIEW_TEXT_CHARS = 2_000_000
MAX_WEBVIEW_HTML_BYTES = 10 * 1024 * 1024

_TEXT_FIELDS = ("thread_id", "turn_id", "item_id", "command", "cwd", "output")


def build_webview_registration_descriptor() -> dict[str, Any]:
    """Describe a deliberately unbound, local-only iTerm WebView registration."""
    return {
        "schema": "codex-house-iterm-webview-registration/1",
        "protocol_revision": 1,
        "minimum_peer": 1,
        "surface": "ITERM_TOOLBELT_WEBVIEW",
        "display_name": "🏠 👁️",
        "unique_identifier": "com.codex.house.terminal-companion",
        "reveal_if_already_registered": True,
        "url": None,
        "url_state": "UNBOUND",
        "url_policy": "LOOPBACK_CAPABILITY_URL_REQUIRED",
        "url_validation": "IMPLEMENTED_OFFLINE_UNBOUND",
        "binding_gate": "LIVE_BINDING_REVIEW_REQUIRED",
        "allowed_hosts": ["127.0.0.1", "::1"],
        "content_mode": "STATIC_SELF_CONTAINED_HTML",
        "authority": "OBSERVE_ONLY",
        "reverse_channel": "PROHIBITED",
        "transport": "NOT_ATTEMPTED",
        "iterm_api_registration": "NOT_ATTEMPTED",
        "terminal_input": "PROHIBITED",
        "buddy_relay": "OUT_OF_SCOPE",
    }


def _escaped(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _card_html(card: dict[str, Any]) -> str:
    exit_code = "—" if card["exit_code"] is None else str(card["exit_code"])
    duration = "—" if card["duration_ms"] is None else f"{card['duration_ms']} ms"
    output = "" if card["output"] is None else card["output"]
    return "".join(
        (
            '<article class="card">',
            '<header><span class="status">',
            _escaped(card["status"]),
            "</span><span>",
            _escaped(card["item_id"]),
            "</span></header>",
            "<dl><dt>Thread</dt><dd>",
            _escaped(card["thread_id"]),
            "</dd><dt>Turn</dt><dd>",
            _escaped(card["turn_id"]),
            "</dd><dt>Working directory</dt><dd><code>",
            _escaped(card["cwd"]),
            "</code></dd><dt>Exit</dt><dd>",
            _escaped(exit_code),
            "</dd><dt>Duration</dt><dd>",
            _escaped(duration),
            "</dd></dl><h2>Command</h2><pre>",
            _escaped(card["command"]),
            "</pre><h2>Output</h2><pre>",
            _escaped(output),
            "</pre></article>",
        )
    )


def render_display_chain_html(batches: list[object]) -> str:
    """Render a verified display chain without scripts, links, or transport."""
    if not isinstance(batches, list):
        raise CompanionProjectionError("batches must be a list")
    if not batches:
        raise CompanionProjectionError("at least one display batch is required")
    if len(batches) > MAX_WEBVIEW_BATCHES:
        raise CompanionProjectionError(
            f"webview batch count exceeds {MAX_WEBVIEW_BATCHES}"
        )
    verify_display_chain(batches)

    text_chars = 0
    cards: list[dict[str, Any]] = []
    for batch in batches:
        assert isinstance(batch, dict)
        for card in batch["cards"]:
            assert isinstance(card, dict)
            text_chars += sum(len(card[field] or "") for field in _TEXT_FIELDS)
            if text_chars > MAX_WEBVIEW_TEXT_CHARS:
                raise CompanionProjectionError(
                    f"webview text exceeds {MAX_WEBVIEW_TEXT_CHARS} characters"
                )
            cards.append(card)

    content = "".join(_card_html(card) for card in cards)
    tip = batches[-1]
    assert isinstance(tip, dict)
    document = "".join(
        (
            '<!doctype html><html lang="en"><head><meta charset="utf-8">',
            '<meta http-equiv="Content-Security-Policy" content="default-src ',
            "'none'; style-src 'unsafe-inline'; img-src 'none'; connect-src 'none'; ",
            "form-action 'none'; base-uri 'none'; frame-ancestors 'none'\">",
            '<meta name="referrer" content="no-referrer">',
            '<meta name="viewport" content="width=device-width,initial-scale=1">',
            "<title>🏠 👁️</title><style>",
            "html{color-scheme:dark}body{margin:0;padding:12px;background:#101310;",
            "color:#d8e8d8;font:13px ui-monospace,SFMono-Regular,Menlo,monospace}",
            ".summary{color:#8fb38f;margin:0 0 12px}.card{border:1px solid #304630;",
            "border-radius:8px;margin:0 0 12px;padding:10px;background:#151a15}",
            "header{display:flex;gap:10px;color:#9fc99f}.status{text-transform:uppercase}",
            "dl{display:grid;grid-template-columns:max-content 1fr;gap:3px 10px}",
            "dt{color:#8a9f8a}dd{margin:0;overflow-wrap:anywhere}h2{font-size:12px;",
            "margin:10px 0 4px;color:#8fb38f}pre{white-space:pre-wrap;overflow-wrap:anywhere;",
            "margin:0;padding:8px;background:#0b0e0b;border-radius:5px}",
            '</style></head><body><p class="summary">Observe only · ',
            _escaped(len(cards)),
            " cards · sequence ",
            _escaped(tip["sequence"]),
            " · ",
            _escaped(tip["batch_id"]),
            "</p><main>",
            content,
            "</main></body></html>",
        )
    )
    if len(document.encode("utf-8")) > MAX_WEBVIEW_HTML_BYTES:
        raise CompanionProjectionError(
            f"webview document exceeds {MAX_WEBVIEW_HTML_BYTES} encoded bytes"
        )
    return document

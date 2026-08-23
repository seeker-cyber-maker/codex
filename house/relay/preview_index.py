"""Deterministic, content-free composition of sealed relay preview registrations."""

from __future__ import annotations

import html

from .operator_preview import RelayPreviewCardError, inspect_relay_preview_registration

MAX_PREVIEW_REGISTRATIONS = 32
MAX_INDEX_BYTES = 200_000
_SOURCE_NOTES = {
    "NOT_SUPPLIED": "Source scope: NOT_SUPPLIED · no relay-registration source was provided.",
    "NAMED_JSON": "Source scope: NAMED_JSON · explicit frozen registration input.",
}


class RelayPreviewIndexError(ValueError):
    """A preview-registration collection cannot safely become an index."""


def _preview_row(fields: dict[str, str]) -> str:
    return "".join(
        (
            '<article class="card"><dl><dt>Document</dt><dd><code>',
            html.escape(fields["document_sha256"], quote=True),
            "</code></dd><dt>Request</dt><dd><code>",
            html.escape(fields["request_sha256"], quote=True),
            "</code></dd><dt>Registration</dt><dd><code>",
            html.escape(fields["registration_sha256"], quote=True),
            (
                "</code></dd><dt>State</dt><dd>PREPARED_UNAUTHORIZED · "
                "NOT_ISSUED · NOT_ATTEMPTED</dd></dl></article>"
            ),
        )
    )


def _source_note(source_state: object) -> str:
    if source_state is None:
        return ""
    if not isinstance(source_state, str) or source_state not in _SOURCE_NOTES:
        raise RelayPreviewIndexError("invalid relay-preview source scope")
    return f"<p>{_SOURCE_NOTES[source_state]}</p>"


def render_relay_preview_index_html(
    registrations: object, *, source_state: object = None
) -> str:
    """Render bounded verified registration identifiers without source content."""
    if not isinstance(registrations, list):
        raise RelayPreviewIndexError("registrations must be a list")
    if len(registrations) > MAX_PREVIEW_REGISTRATIONS:
        raise RelayPreviewIndexError(
            f"registration count exceeds {MAX_PREVIEW_REGISTRATIONS}"
        )

    fields: list[dict[str, str]] = []
    for index, registration in enumerate(registrations):
        try:
            fields.append(inspect_relay_preview_registration(registration))
        except RelayPreviewCardError as exc:
            raise RelayPreviewIndexError(f"invalid registration {index}") from exc
    registration_ids = [item["registration_sha256"] for item in fields]
    if len(registration_ids) != len(set(registration_ids)):
        raise RelayPreviewIndexError("duplicate registration")
    fields.sort(key=lambda item: item["registration_sha256"])

    rows = "".join(_preview_row(item) for item in fields)
    source_note = _source_note(source_state)
    document = "".join(
        (
            '<!doctype html><html lang="en"><head><meta charset="utf-8">',
            '<meta http-equiv="Content-Security-Policy" content="default-src ',
            "'none'; style-src 'unsafe-inline'; img-src 'none'; connect-src 'none'; ",
            "form-action 'none'; base-uri 'none'; frame-ancestors 'none'\">",
            '<meta name="referrer" content="no-referrer">',
            '<meta name="viewport" content="width=device-width,initial-scale=1">',
            "<title>🏠 Relay previews</title><style>",
            "html{color-scheme:dark}body{margin:0;padding:14px;background:#101310;",
            "color:#d8e8d8;font:13px ui-monospace,SFMono-Regular,Menlo,monospace}",
            ".summary{color:#9fc99f;margin:0 0 12px}.card{border:1px solid #304630;",
            "border-radius:8px;padding:10px;background:#151a15;margin:0 0 10px}",
            "dl{display:grid;grid-template-columns:max-content 1fr;gap:5px 10px;margin:0}",
            "dt{color:#8a9f8a}dd{margin:0;overflow-wrap:anywhere}code{color:#d8e8d8}",
            '</style></head><body><p class="summary">Observe only · ',
            str(len(fields)),
            " relay previews</p><main>",
            source_note,
            rows,
            "</main></body></html>",
        )
    )
    if len(document.encode("utf-8")) > MAX_INDEX_BYTES:
        raise RelayPreviewIndexError(f"preview index exceeds {MAX_INDEX_BYTES} bytes")
    return document

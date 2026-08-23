"""Inert operator presentation for caller-supplied snapshot-inventory records."""

from __future__ import annotations

import html
import re
from collections.abc import Mapping

MAX_INVENTORY_RECORDS = 32
MAX_DOCUMENT_BYTES = 200_000
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_BASE_FIELDS = frozenset({"input_path", "path", "state", "reason"})
_SUCCESS_FIELDS = _BASE_FIELDS | frozenset(
    {"descriptor_receipt_sha256", "envelope_sha256"}
)
_REJECTED_STATES = frozenset({"REJECTED_INPUT", "REJECTED_ENVELOPE"})


class OperatorSnapshotInventoryViewError(ValueError):
    """A caller-supplied inventory cannot safely become a static view."""


def _text(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise OperatorSnapshotInventoryViewError(f"invalid inventory {label}")
    return value


def _record(record: object) -> dict[str, str]:
    if not isinstance(record, Mapping):
        raise OperatorSnapshotInventoryViewError("inventory record must be an object")
    state = record.get("state")
    if state == "VALID_OFFLINE":
        if set(record) != _SUCCESS_FIELDS:
            raise OperatorSnapshotInventoryViewError(
                "valid inventory fields are not exact"
            )
        for field in ("descriptor_receipt_sha256", "envelope_sha256"):
            value = record.get(field)
            if not isinstance(value, str) or not _DIGEST.fullmatch(value):
                raise OperatorSnapshotInventoryViewError(f"invalid inventory {field}")
    elif state in _REJECTED_STATES:
        if set(record) != _BASE_FIELDS:
            raise OperatorSnapshotInventoryViewError(
                "rejected inventory fields are not exact"
            )
    else:
        raise OperatorSnapshotInventoryViewError("invalid inventory state")
    fields = {field: _text(record.get(field), field) for field in _BASE_FIELDS}
    if fields["state"] == "VALID_OFFLINE":
        fields["descriptor_receipt_sha256"] = str(record["descriptor_receipt_sha256"])
        fields["envelope_sha256"] = str(record["envelope_sha256"])
    return fields


def _row(index: int, fields: Mapping[str, str]) -> str:
    details = [
        "<dt>Input</dt><dd><code>",
        html.escape(fields["input_path"], quote=True),
        "</code></dd><dt>Canonical path</dt><dd><code>",
        html.escape(fields["path"] or "—", quote=True),
        "</code></dd><dt>Reason</dt><dd>",
        html.escape(fields["reason"] or "—", quote=True),
        "</dd>",
    ]
    if fields["state"] == "VALID_OFFLINE":
        details.extend(
            (
                "<dt>Descriptor receipt</dt><dd><code>",
                html.escape(fields["descriptor_receipt_sha256"], quote=True),
                "</code></dd><dt>Envelope receipt</dt><dd><code>",
                html.escape(fields["envelope_sha256"], quote=True),
                "</code></dd>",
            )
        )
    return "".join(
        (
            '<article class="card"><header><strong>Envelope ',
            str(index + 1),
            "</strong><span>",
            html.escape(fields["state"], quote=True),
            "</span></header><dl>",
            *details,
            "</dl></article>",
        )
    )


def render_operator_snapshot_inventory_html(records: object) -> str:
    """Render frozen inventory records without reading a path or invoking inventory."""
    if not isinstance(records, list) or not 1 <= len(records) <= MAX_INVENTORY_RECORDS:
        raise OperatorSnapshotInventoryViewError(
            f"inventory must be a list of 1 to {MAX_INVENTORY_RECORDS} records"
        )
    fields = [_record(record) for record in records]
    document = "".join(
        (
            '<!doctype html><html lang="en"><head><meta charset="utf-8">',
            '<meta http-equiv="Content-Security-Policy" content="default-src ',
            "'none'; style-src 'unsafe-inline'; img-src 'none'; connect-src 'none'; ",
            "form-action 'none'; base-uri 'none'; frame-ancestors 'none'\">",
            '<meta name="referrer" content="no-referrer">',
            '<meta name="viewport" content="width=device-width,initial-scale=1">',
            "<title>🏠 Snapshot inventory</title><style>",
            "html{color-scheme:dark}body{margin:0;padding:14px;background:#101310;",
            "color:#d8e8d8;font:13px ui-monospace,SFMono-Regular,Menlo,monospace}",
            "h1{margin:0 0 10px}.summary{color:#9fc99f;margin:0 0 18px}",
            ".card{border:1px solid #304630;border-radius:8px;padding:10px;",
            "background:#151a15;margin:0 0 10px}header{display:flex;",
            "justify-content:space-between;gap:12px;color:#9fc99f}dl{display:grid;",
            "grid-template-columns:max-content 1fr;gap:5px 10px;margin:8px 0 0}",
            "dt{color:#8a9f8a}dd{margin:0;overflow-wrap:anywhere}code{color:#d8e8d8}",
            "</style></head><body><h1>Snapshot inventory</h1>",
            '<p class="summary">Observe only · caller-supplied inventory records · ',
            str(len(fields)),
            " named envelopes · no refresh or action surface</p><main>",
            "".join(_row(index, item) for index, item in enumerate(fields)),
            "</main></body></html>",
        )
    )
    if len(document.encode("utf-8")) > MAX_DOCUMENT_BYTES:
        raise OperatorSnapshotInventoryViewError(
            f"inventory document exceeds {MAX_DOCUMENT_BYTES} bytes"
        )
    return document

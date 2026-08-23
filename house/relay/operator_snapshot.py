"""One-way static composition of frozen relay and task-card index documents."""

from __future__ import annotations

from html.parser import HTMLParser

MAX_SOURCE_DOCUMENT_BYTES = 200_000
MAX_OPERATOR_SNAPSHOT_BYTES = 400_000
_FRAGMENT_TAGS = frozenset(
    {"article", "code", "dd", "dl", "dt", "header", "p", "span", "strong"}
)
_SOURCE_SIGNATURES = {
    "relay preview": (
        "<title>🏠 Relay previews</title>",
        " relay previews</p><main>",
    ),
    "task card": (
        "<title>🏠 Task cards</title>",
        " task cards · routing is advisory · dispatch not attempted</p><main>",
    ),
}


class OperatorSnapshotError(ValueError):
    """Frozen source documents cannot safely become an operator snapshot."""


class _StaticFragmentValidator(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.stack: list[str] = []
        self.error: str | None = None

    def _reject(self, message: str) -> None:
        if self.error is None:
            self.error = message

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag not in _FRAGMENT_TAGS:
            self._reject("fragment contains an unsupported tag")
            return
        if attrs != [("class", "card")] if tag == "article" else bool(attrs):
            self._reject("fragment contains unsupported attributes")
            return
        self.stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if not self.stack or self.stack[-1] != tag:
            self._reject("fragment tags are unbalanced")
            return
        self.stack.pop()

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._reject("fragment contains a self-closing tag")

    def handle_comment(self, data: str) -> None:
        self._reject("fragment contains a comment")

    def handle_decl(self, decl: str) -> None:
        self._reject("fragment contains a declaration")

    def handle_pi(self, data: str) -> None:
        self._reject("fragment contains a processing instruction")


def _fragment(document: object, source_kind: str) -> str:
    if not isinstance(document, str) or not document:
        raise OperatorSnapshotError(f"invalid {source_kind} document")
    if len(document.encode("utf-8")) > MAX_SOURCE_DOCUMENT_BYTES:
        raise OperatorSnapshotError(
            f"{source_kind} document exceeds {MAX_SOURCE_DOCUMENT_BYTES} bytes"
        )
    title, summary = _SOURCE_SIGNATURES[source_kind]
    if title not in document or summary not in document:
        raise OperatorSnapshotError(f"invalid {source_kind} signature")
    if "default-src 'none'" not in document or not document.endswith(
        "</main></body></html>"
    ):
        raise OperatorSnapshotError(f"invalid {source_kind} containment")
    if document.count("<main>") != 1 or document.count("</main>") != 1:
        raise OperatorSnapshotError(f"invalid {source_kind} main fragment")
    start = document.index("<main>") + len("<main>")
    end = document.index("</main>", start)
    fragment = document[start:end]
    validator = _StaticFragmentValidator()
    validator.feed(fragment)
    validator.close()
    if validator.error is not None or validator.stack:
        raise OperatorSnapshotError(validator.error or "fragment tags are unbalanced")
    return fragment


def render_operator_snapshot_html(
    relay_preview_index_html: object, task_card_index_html: object
) -> str:
    """Compose two frozen static indexes without calling either source renderer."""
    relay_fragment = _fragment(relay_preview_index_html, "relay preview")
    task_fragment = _fragment(task_card_index_html, "task card")
    document = "".join(
        (
            '<!doctype html><html lang="en"><head><meta charset="utf-8">',
            '<meta http-equiv="Content-Security-Policy" content="default-src ',
            "'none'; style-src 'unsafe-inline'; img-src 'none'; connect-src 'none'; ",
            "form-action 'none'; base-uri 'none'; frame-ancestors 'none'\">",
            '<meta name="referrer" content="no-referrer">',
            '<meta name="viewport" content="width=device-width,initial-scale=1">',
            "<title>🏠 Dream House snapshot</title><style>",
            "html{color-scheme:dark}body{margin:0;padding:14px;background:#101310;",
            "color:#d8e8d8;font:13px ui-monospace,SFMono-Regular,Menlo,monospace}",
            "h1,h2{margin:0 0 10px}.summary{color:#9fc99f;margin:0 0 18px}",
            "section{margin:0 0 22px}.card{border:1px solid #304630;border-radius:8px;",
            "padding:10px;background:#151a15;margin:0 0 10px}header{display:flex;",
            "justify-content:space-between;gap:12px;color:#9fc99f}p{white-space:pre-wrap;",
            "overflow-wrap:anywhere}dl{display:grid;grid-template-columns:max-content 1fr;",
            "gap:5px 10px;margin:0}dt{color:#8a9f8a}dd{margin:0;overflow-wrap:anywhere}",
            "code{color:#d8e8d8}</style></head><body><h1>Dream House snapshot</h1>",
            '<p class="summary">Observe only · frozen source documents · no refresh or action surface</p>',
            "<main><section><h2>Relay previews</h2>",
            relay_fragment,
            "</section><section><h2>Task cards</h2>",
            task_fragment,
            "</section></main></body></html>",
        )
    )
    if len(document.encode("utf-8")) > MAX_OPERATOR_SNAPSHOT_BYTES:
        raise OperatorSnapshotError(
            f"operator snapshot exceeds {MAX_OPERATOR_SNAPSHOT_BYTES} bytes"
        )
    return document

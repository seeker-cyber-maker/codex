"""One-way static composition of a frozen operator snapshot and inventory board."""

from __future__ import annotations

from html.parser import HTMLParser

MAX_SOURCE_DOCUMENT_BYTES = 400_000
MAX_OPERATOR_BOARD_BYTES = 600_000
_FRAGMENT_TAGS = frozenset(
    {
        "article",
        "code",
        "dd",
        "dl",
        "dt",
        "h2",
        "header",
        "p",
        "section",
        "span",
        "strong",
    }
)
_SOURCE_SIGNATURES = {
    "operator snapshot": (
        "<title>🏠 Dream House snapshot</title>",
        " frozen source documents · no refresh or action surface</p><main>",
    ),
    "inventory board": (
        "<title>🏠 Snapshot inventory</title>",
        " caller-supplied inventory records · ",
    ),
}
_FORBIDDEN_MARKERS = (
    "<script",
    "<form",
    "<a ",
    "<iframe",
    "<object",
    "<embed",
    "fetch(",
    "WebSocket",
    "<!--",
    "<?",
)


class OperatorBoardError(ValueError):
    """Frozen static documents cannot safely become one operator board."""


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
        if tag == "article" and attrs != [("class", "card")]:
            self._reject("fragment contains unsupported article attributes")
            return
        if tag == "p" and attrs not in ([], [("class", "summary")]):
            self._reject("fragment contains unsupported paragraph attributes")
            return
        if tag not in {"article", "p"} and attrs:
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
        raise OperatorBoardError(f"invalid {source_kind} document")
    if len(document.encode("utf-8")) > MAX_SOURCE_DOCUMENT_BYTES:
        raise OperatorBoardError(
            f"{source_kind} document exceeds {MAX_SOURCE_DOCUMENT_BYTES} bytes"
        )
    title, summary = _SOURCE_SIGNATURES[source_kind]
    if title not in document or summary not in document:
        raise OperatorBoardError(f"invalid {source_kind} signature")
    if "default-src 'none'" not in document or not document.endswith(
        "</main></body></html>"
    ):
        raise OperatorBoardError(f"invalid {source_kind} containment")
    if any(marker in document for marker in _FORBIDDEN_MARKERS):
        raise OperatorBoardError(f"invalid {source_kind} active content")
    if document.count("<main>") != 1 or document.count("</main>") != 1:
        raise OperatorBoardError(f"invalid {source_kind} main fragment")
    start = document.index("<main>") + len("<main>")
    end = document.index("</main>", start)
    fragment = document[start:end]
    validator = _StaticFragmentValidator()
    validator.feed(fragment)
    validator.close()
    if validator.error is not None or validator.stack:
        raise OperatorBoardError(validator.error or "fragment tags are unbalanced")
    return fragment


def render_operator_board_html(
    operator_snapshot_html: object, inventory_board_html: object
) -> str:
    """Compose two already-frozen static documents without reading or refreshing."""
    snapshot_fragment = _fragment(operator_snapshot_html, "operator snapshot")
    inventory_fragment = _fragment(inventory_board_html, "inventory board")
    document = "".join(
        (
            '<!doctype html><html lang="en"><head><meta charset="utf-8">',
            '<meta http-equiv="Content-Security-Policy" content="default-src ',
            "'none'; style-src 'unsafe-inline'; img-src 'none'; connect-src 'none'; ",
            "form-action 'none'; base-uri 'none'; frame-ancestors 'none'\">",
            '<meta name="referrer" content="no-referrer">',
            '<meta name="viewport" content="width=device-width,initial-scale=1">',
            "<title>🏠 Dream House operator board</title><style>",
            "html{color-scheme:dark}body{margin:0;padding:14px;background:#101310;",
            "color:#d8e8d8;font:13px ui-monospace,SFMono-Regular,Menlo,monospace}",
            "h1,h2{margin:0 0 10px}.summary{color:#9fc99f;margin:0 0 18px}",
            "section{margin:0 0 24px}.card{border:1px solid #304630;border-radius:8px;",
            "padding:10px;background:#151a15;margin:0 0 10px}header{display:flex;",
            "justify-content:space-between;gap:12px;color:#9fc99f}p{white-space:pre-wrap;",
            "overflow-wrap:anywhere}dl{display:grid;grid-template-columns:max-content 1fr;",
            "gap:5px 10px;margin:0}dt{color:#8a9f8a}dd{margin:0;overflow-wrap:anywhere}",
            "code{color:#d8e8d8}</style></head><body><h1>Dream House operator board</h1>",
            '<p class="summary">Observe only · caller-supplied frozen documents · no refresh or action surface</p>',
            "<main><section><h2>Operator snapshot</h2>",
            snapshot_fragment,
            "</section><section><h2>Snapshot inventory</h2>",
            inventory_fragment,
            "</section></main></body></html>",
        )
    )
    if len(document.encode("utf-8")) > MAX_OPERATOR_BOARD_BYTES:
        raise OperatorBoardError(
            f"operator board exceeds {MAX_OPERATOR_BOARD_BYTES} bytes"
        )
    return document

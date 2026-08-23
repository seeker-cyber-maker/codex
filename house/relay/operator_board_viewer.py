"""Prepare an unstarted one-shot viewer for one verified operator-board export."""

from __future__ import annotations

import hashlib
from pathlib import Path

from house.terminal_companion import OneShotLoopbackViewer

from .operator_board_export import (
    OperatorBoardExportError,
    inspect_operator_board_export,
)


class OperatorBoardViewerError(ValueError):
    """A board export cannot safely become an unstarted viewer document."""


def prepare_operator_board_viewer(
    output_path: object,
    *,
    host: str = "127.0.0.1",
    port: int = 0,
    ttl_seconds: int = 30,
) -> OneShotLoopbackViewer:
    """Verify and freeze one named export without binding a listener."""
    try:
        receipt = inspect_operator_board_export(output_path)
    except OperatorBoardExportError as exc:
        raise OperatorBoardViewerError("operator board export is not valid") from exc
    target = Path(receipt["path"])
    try:
        document_bytes = target.read_bytes()
    except OSError as exc:
        raise OperatorBoardViewerError("operator board export cannot be read") from exc
    if hashlib.sha256(document_bytes).hexdigest() != receipt["board_sha256"]:
        raise OperatorBoardViewerError(
            "operator board export changed during preparation"
        )
    try:
        document = document_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise OperatorBoardViewerError("operator board export is not UTF-8") from exc
    return OneShotLoopbackViewer(
        document,
        host=host,
        port=port,
        ttl_seconds=ttl_seconds,
    )

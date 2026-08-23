"""Explicit no-overwrite local export for one frozen Dream House operator board."""

from __future__ import annotations

import hashlib
import json
import os
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .operator_board import OperatorBoardError, render_operator_board_html

_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_RECEIPT_FIELDS = frozenset(
    {
        "schema",
        "state",
        "board_filename",
        "board_sha256",
        "operator_snapshot_sha256",
        "inventory_board_sha256",
        "source_state",
        "refresh",
        "viewer_start",
        "authority",
        "receipt_sha256",
    }
)
_STATIC_STATE = {
    "schema": "codex-house-operator-board-export/1",
    "state": "COMPLETE_OFFLINE",
    "source_state": "CALLER_SUPPLIED",
    "refresh": "NOT_ATTEMPTED",
    "viewer_start": "NOT_ATTEMPTED",
    "authority": "NOT_GRANTED",
}


class OperatorBoardExportError(ValueError):
    """An operator board cannot meet its explicit immutable export contract."""


def _canonical_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _absolute_output_path(output_path: object) -> Path:
    if not isinstance(output_path, (str, Path)):
        raise OperatorBoardExportError("output path must be a path")
    path = Path(output_path)
    if not path.is_absolute():
        raise OperatorBoardExportError("output path must be absolute")
    if path.name in {"", ".", ".."}:
        raise OperatorBoardExportError("output filename is not explicit")
    if not path.parent.is_dir():
        raise OperatorBoardExportError("output parent does not exist")
    return path


def _receipt_path(path: Path) -> Path:
    return path.with_name(f"{path.name}.receipt.json")


def _marker_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.INCOMPLETE")


def _write_new(path: Path, content: bytes) -> None:
    with path.open("xb") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())


def _read_exact_json(path: Path) -> dict[str, Any]:
    try:
        encoded = path.read_bytes()
        value = json.loads(encoded.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise OperatorBoardExportError("invalid export receipt file") from exc
    if not isinstance(value, dict) or _canonical_bytes(value) != encoded:
        raise OperatorBoardExportError("export receipt file is not canonical")
    return value


def _inspect_receipt(receipt: object, output_path: Path) -> dict[str, str]:
    if not isinstance(receipt, Mapping) or set(receipt) != _RECEIPT_FIELDS:
        raise OperatorBoardExportError("export receipt fields are not exact")
    for field, expected in _STATIC_STATE.items():
        if receipt.get(field) != expected:
            raise OperatorBoardExportError(f"invalid export receipt {field}")
    if receipt.get("board_filename") != output_path.name:
        raise OperatorBoardExportError("export receipt filename does not match")
    for field in (
        "board_sha256",
        "operator_snapshot_sha256",
        "inventory_board_sha256",
        "receipt_sha256",
    ):
        value = receipt.get(field)
        if not isinstance(value, str) or not _DIGEST.fullmatch(value):
            raise OperatorBoardExportError(f"invalid export receipt {field}")
    unsigned = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    if _sha256(_canonical_bytes(unsigned)) != receipt["receipt_sha256"]:
        raise OperatorBoardExportError("export receipt digest does not match")
    return {key: str(receipt[key]) for key in sorted(_RECEIPT_FIELDS)}


def write_operator_board_export(
    output_path: object, operator_snapshot_html: object, inventory_board_html: object
) -> dict[str, str]:
    """Write one new frozen board plus a canonical receipt; never overwrite."""
    try:
        board = render_operator_board_html(operator_snapshot_html, inventory_board_html)
    except OperatorBoardError as exc:
        raise OperatorBoardExportError(
            "operator board source documents are not valid"
        ) from exc
    target = _absolute_output_path(output_path)
    receipt_path = _receipt_path(target)
    marker_path = _marker_path(target)
    if any(
        path.exists() or path.is_symlink()
        for path in (target, receipt_path, marker_path)
    ):
        raise OperatorBoardExportError("export target or companion already exists")

    board_bytes = board.encode("utf-8")
    unsigned: dict[str, str] = {
        **_STATIC_STATE,
        "board_filename": target.name,
        "board_sha256": _sha256(board_bytes),
        "operator_snapshot_sha256": _sha256(operator_snapshot_html.encode("utf-8")),
        "inventory_board_sha256": _sha256(inventory_board_html.encode("utf-8")),
    }
    receipt = {**unsigned, "receipt_sha256": _sha256(_canonical_bytes(unsigned))}
    try:
        _write_new(marker_path, b"INCOMPLETE\n")
    except FileExistsError as exc:
        raise OperatorBoardExportError(
            "export incomplete marker already exists"
        ) from exc
    except OSError as exc:
        raise OperatorBoardExportError(
            "export incomplete marker could not be created"
        ) from exc
    try:
        _write_new(target, board_bytes)
        _write_new(receipt_path, _canonical_bytes(receipt))
        marker_path.unlink()
    except OSError as exc:
        raise OperatorBoardExportError(
            "export remains incomplete; existing bytes were not overwritten"
        ) from exc
    return inspect_operator_board_export(target)


def inspect_operator_board_export(output_path: object) -> dict[str, str]:
    """Verify one existing board/receipt pair without reading source documents."""
    target = _absolute_output_path(output_path)
    receipt_path = _receipt_path(target)
    marker_path = _marker_path(target)
    if marker_path.exists() or marker_path.is_symlink():
        raise OperatorBoardExportError("export is incomplete")
    if not target.is_file() or target.is_symlink():
        raise OperatorBoardExportError("export board does not exist")
    if not receipt_path.is_file() or receipt_path.is_symlink():
        raise OperatorBoardExportError("export receipt does not exist")
    try:
        board = target.read_bytes()
    except OSError as exc:
        raise OperatorBoardExportError("export board cannot be read") from exc
    if (
        b"<title>\xf0\x9f\x8f\xa0 Dream House operator board</title>" not in board
        or b"default-src 'none'" not in board
        or not board.endswith(b"</main></body></html>")
    ):
        raise OperatorBoardExportError("export board is not a static operator board")
    receipt = _inspect_receipt(_read_exact_json(receipt_path), target)
    if receipt["board_sha256"] != _sha256(board):
        raise OperatorBoardExportError("export board hash does not match")
    return {
        "path": str(target),
        "receipt_path": str(receipt_path),
        **receipt,
    }

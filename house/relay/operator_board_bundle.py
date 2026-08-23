"""Write and verify one self-contained, offline operator-board bundle."""

from __future__ import annotations

import hashlib
import json
import os
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .operator_board_export import (
    OperatorBoardExportError,
    inspect_operator_board_export,
    write_operator_board_export,
)
from .operator_inventory_view import (
    OperatorSnapshotInventoryViewError,
    render_operator_snapshot_inventory_html,
)
from .operator_snapshot import render_operator_snapshot_html
from .preview_index import RelayPreviewIndexError, render_relay_preview_index_html
from .snapshot_descriptor import build_operator_snapshot_descriptor
from .snapshot_envelope import (
    OperatorSnapshotEnvelopeError,
    inspect_operator_snapshot_envelope,
    write_operator_snapshot_envelope,
)
from .snapshot_inventory import inspect_operator_snapshot_inventory
from .task_card_index import TaskCardIndexError, render_task_card_index_html

_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_BUNDLE_FILES = frozenset(
    {
        "operator-snapshot",
        "snapshot-inventory.html",
        "operator-board.html",
        "operator-board.html.receipt.json",
        "bundle.json",
    }
)
_BUNDLE_FIELDS = frozenset(
    {
        "schema",
        "state",
        "sources",
        "operator_snapshot_envelope_sha256",
        "snapshot_inventory_sha256",
        "operator_board_sha256",
        "operator_board_receipt_sha256",
        "viewer_start",
        "authority",
        "bundle_sha256",
    }
)
_STATIC_BUNDLE_STATE = {
    "schema": "codex-house-operator-board-bundle/1",
    "state": "COMPLETE_OFFLINE",
    "viewer_start": "NOT_ATTEMPTED",
    "authority": "NOT_GRANTED",
}
_INCOMPLETE_MARKER = ".INCOMPLETE"


class OperatorBoardBundleError(ValueError):
    """An offline operator-board bundle cannot meet its exact contract."""


def _canonical_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _absolute_output_dir(output_dir: object) -> Path:
    if not isinstance(output_dir, (str, Path)):
        raise OperatorBoardBundleError("output directory must be a path")
    target = Path(output_dir)
    if not target.is_absolute():
        raise OperatorBoardBundleError("output directory must be absolute")
    if target.name in {"", ".", ".."}:
        raise OperatorBoardBundleError("output directory name is not explicit")
    if not target.parent.is_dir():
        raise OperatorBoardBundleError("output directory parent does not exist")
    return target


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
        raise OperatorBoardBundleError("bundle manifest is not valid JSON") from exc
    if not isinstance(value, dict) or _canonical_bytes(value) != encoded:
        raise OperatorBoardBundleError("bundle manifest is not canonical")
    return value


def _source_record(value: object, expected: str) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise OperatorBoardBundleError(f"{expected} source record is not valid")
    if expected == "relay_registrations":
        required = frozenset({"state", "path", "input_sha256", "count"})
        allowed_states = frozenset({"NOT_SUPPLIED", "NAMED_JSON"})
        digest_field = "input_sha256"
    else:
        required = frozenset({"state", "path", "journal_sha256", "count"})
        allowed_states = frozenset({"NOT_SUPPLIED", "READ_ONLY_NAMED_DATABASE"})
        digest_field = "journal_sha256"
    if set(value) != required or value.get("state") not in allowed_states:
        raise OperatorBoardBundleError(f"{expected} source fields are not exact")
    count = value.get("count")
    if not isinstance(count, int) or not 0 <= count <= 32:
        raise OperatorBoardBundleError(f"{expected} source count is not valid")
    state = str(value["state"])
    path = value.get("path")
    digest = value.get(digest_field)
    if state == "NOT_SUPPLIED":
        if path is not None or digest is not None or count != 0:
            raise OperatorBoardBundleError(f"{expected} absent source is not exact")
    else:
        if not isinstance(path, str) or not Path(path).is_absolute():
            raise OperatorBoardBundleError(f"{expected} source path is not absolute")
        if not isinstance(digest, str) or not _DIGEST.fullmatch(digest):
            raise OperatorBoardBundleError(f"{expected} source digest is not valid")
    return {key: value[key] for key in sorted(required)}


def _sources(value: object) -> dict[str, dict[str, object]]:
    if not isinstance(value, Mapping) or set(value) != {
        "relay_registrations",
        "task_spine",
    }:
        raise OperatorBoardBundleError("bundle source fields are not exact")
    return {
        "relay_registrations": _source_record(
            value["relay_registrations"], "relay_registrations"
        ),
        "task_spine": _source_record(value["task_spine"], "task_spine"),
    }


def _bundle_manifest(
    sources: object,
    snapshot_envelope: Mapping[str, Any],
    inventory_board: bytes,
    board_receipt: Mapping[str, str],
    receipt_bytes: bytes,
) -> dict[str, object]:
    validated_sources = _sources(sources)
    envelope_sha = snapshot_envelope.get("envelope_sha256")
    board_sha = board_receipt.get("board_sha256")
    if not isinstance(envelope_sha, str) or not _DIGEST.fullmatch(envelope_sha):
        raise OperatorBoardBundleError("snapshot envelope receipt is not valid")
    if not isinstance(board_sha, str) or not _DIGEST.fullmatch(board_sha):
        raise OperatorBoardBundleError("operator-board receipt is not valid")
    unsigned: dict[str, object] = {
        **_STATIC_BUNDLE_STATE,
        "sources": validated_sources,
        "operator_snapshot_envelope_sha256": envelope_sha,
        "snapshot_inventory_sha256": _sha256(inventory_board),
        "operator_board_sha256": board_sha,
        "operator_board_receipt_sha256": _sha256(receipt_bytes),
    }
    return {**unsigned, "bundle_sha256": _sha256(_canonical_bytes(unsigned))}


def write_operator_board_bundle(
    output_dir: object,
    registrations: object,
    task_cards: object,
    sources: object,
) -> dict[str, object]:
    """Create one new offline bundle from bounded caller-supplied projections."""
    target = _absolute_output_dir(output_dir)
    validated_sources = _sources(sources)
    try:
        relay_index = render_relay_preview_index_html(
            registrations,
            source_state=validated_sources["relay_registrations"]["state"],
        )
        task_index = render_task_card_index_html(
            task_cards,
            source_state=validated_sources["task_spine"]["state"],
        )
        snapshot = render_operator_snapshot_html(relay_index, task_index)
        descriptor = build_operator_snapshot_descriptor(
            relay_index, task_index, snapshot
        )
    except (
        RelayPreviewIndexError,
        TaskCardIndexError,
        ValueError,
    ) as exc:
        raise OperatorBoardBundleError(
            "operator-board source projection is not valid"
        ) from exc

    try:
        target.mkdir()
    except FileExistsError as exc:
        raise OperatorBoardBundleError("output directory already exists") from exc
    except OSError as exc:
        raise OperatorBoardBundleError("output directory could not be created") from exc

    try:
        _write_new(target / _INCOMPLETE_MARKER, b"INCOMPLETE\n")
        envelope = write_operator_snapshot_envelope(
            target / "operator-snapshot",
            relay_index,
            task_index,
            snapshot,
            descriptor,
        )
        inventory_records = inspect_operator_snapshot_inventory(
            [str(target / "operator-snapshot")]
        )
        inventory = render_operator_snapshot_inventory_html(inventory_records)
        inventory_bytes = inventory.encode("utf-8")
        _write_new(target / "snapshot-inventory.html", inventory_bytes)
        board = write_operator_board_export(
            target / "operator-board.html", snapshot, inventory
        )
        receipt_bytes = (target / "operator-board.html.receipt.json").read_bytes()
        manifest = _bundle_manifest(
            sources, envelope, inventory_bytes, board, receipt_bytes
        )
        _write_new(target / "bundle.json", _canonical_bytes(manifest))
        (target / _INCOMPLETE_MARKER).unlink()
    except (
        OSError,
        OperatorBoardExportError,
        OperatorSnapshotEnvelopeError,
        OperatorSnapshotInventoryViewError,
        ValueError,
    ) as exc:
        raise OperatorBoardBundleError(
            "bundle remains incomplete; existing bytes were not overwritten"
        ) from exc
    return inspect_operator_board_bundle(target)


def inspect_operator_board_bundle(output_dir: object) -> dict[str, object]:
    """Verify a completed bundle by replaying only its local static artifacts."""
    target = _absolute_output_dir(output_dir)
    if not target.is_dir():
        raise OperatorBoardBundleError("bundle directory does not exist")
    if (target / _INCOMPLETE_MARKER).exists() or (
        target / _INCOMPLETE_MARKER
    ).is_symlink():
        raise OperatorBoardBundleError("bundle is incomplete")
    try:
        entries = {entry.name for entry in target.iterdir()}
    except OSError as exc:
        raise OperatorBoardBundleError("bundle directory cannot be read") from exc
    if entries != _BUNDLE_FILES:
        raise OperatorBoardBundleError("bundle files are not exact")
    try:
        envelope = inspect_operator_snapshot_envelope(target / "operator-snapshot")
        inventory_bytes = (target / "snapshot-inventory.html").read_bytes()
        inventory = inventory_bytes.decode("utf-8")
        expected_inventory = render_operator_snapshot_inventory_html(
            inspect_operator_snapshot_inventory([str(target / "operator-snapshot")])
        )
        board = inspect_operator_board_export(target / "operator-board.html")
        receipt_bytes = (target / "operator-board.html.receipt.json").read_bytes()
    except (
        OSError,
        UnicodeDecodeError,
        OperatorBoardExportError,
        OperatorSnapshotEnvelopeError,
        OperatorSnapshotInventoryViewError,
        ValueError,
    ) as exc:
        raise OperatorBoardBundleError("bundle artifacts are not valid") from exc
    if inventory != expected_inventory:
        raise OperatorBoardBundleError("snapshot inventory does not match replay")

    manifest = _read_exact_json(target / "bundle.json")
    if set(manifest) != _BUNDLE_FIELDS:
        raise OperatorBoardBundleError("bundle manifest fields are not exact")
    for field, expected in _STATIC_BUNDLE_STATE.items():
        if manifest.get(field) != expected:
            raise OperatorBoardBundleError(f"invalid bundle manifest {field}")
    unsigned = {key: value for key, value in manifest.items() if key != "bundle_sha256"}
    if _sha256(_canonical_bytes(unsigned)) != manifest.get("bundle_sha256"):
        raise OperatorBoardBundleError("bundle manifest digest does not match")
    expected_manifest = _bundle_manifest(
        manifest.get("sources"), envelope, inventory_bytes, board, receipt_bytes
    )
    if manifest != expected_manifest:
        raise OperatorBoardBundleError("bundle manifest does not match artifacts")
    return {"path": str(target), **manifest}

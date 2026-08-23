"""Explicit local storage for one verified, frozen operator snapshot."""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .snapshot_descriptor import (
    OperatorSnapshotDescriptorError,
    inspect_operator_snapshot_descriptor,
    verify_operator_snapshot_descriptor,
)

_DIGEST_LENGTH = 64
_ENVELOPE_FILES = frozenset(
    {
        "relay-preview-index.html",
        "task-card-index.html",
        "operator-snapshot.html",
        "descriptor.json",
        "envelope.json",
    }
)
_CONTENT_FILES = {
    "relay-preview-index.html": "relay preview",
    "task-card-index.html": "task card",
    "operator-snapshot.html": "snapshot",
    "descriptor.json": "descriptor",
}
_INCOMPLETE_MARKER = ".INCOMPLETE"
_ENVELOPE_FIELDS = frozenset(
    {
        "schema",
        "state",
        "files",
        "descriptor_receipt_sha256",
        "descriptor_file_sha256",
        "envelope_sha256",
    }
)
_STATIC_ENVELOPE_STATE = {
    "schema": "codex-house-operator-snapshot-envelope/1",
    "state": "COMPLETE_OFFLINE",
}


class OperatorSnapshotEnvelopeError(ValueError):
    """A local snapshot envelope cannot meet its immutable offline contract."""


def _canonical_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _absolute_output_path(output_dir: object) -> Path:
    if not isinstance(output_dir, (Path, str)):
        raise OperatorSnapshotEnvelopeError("output directory must be a path")
    path = Path(output_dir)
    if not path.is_absolute():
        raise OperatorSnapshotEnvelopeError("output directory must be absolute")
    if path.name in {"", ".", ".."}:
        raise OperatorSnapshotEnvelopeError("output directory name is not explicit")
    parent = path.parent
    if not parent.is_dir():
        raise OperatorSnapshotEnvelopeError("output directory parent does not exist")
    return path


def _document_bytes(document: object, label: str) -> bytes:
    if not isinstance(document, str) or not document:
        raise OperatorSnapshotEnvelopeError(f"invalid {label} document")
    return document.encode("utf-8")


def _read_exact_json(path: Path, label: str) -> dict[str, Any]:
    try:
        encoded = path.read_bytes()
        value = json.loads(encoded.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise OperatorSnapshotEnvelopeError(f"invalid {label} file") from exc
    if not isinstance(value, dict) or _canonical_bytes(value) != encoded:
        raise OperatorSnapshotEnvelopeError(f"{label} file is not canonical")
    return value


def _validate_envelope(envelope: object) -> dict[str, Any]:
    if not isinstance(envelope, Mapping) or set(envelope) != _ENVELOPE_FIELDS:
        raise OperatorSnapshotEnvelopeError("envelope fields are not exact")
    for field, expected in _STATIC_ENVELOPE_STATE.items():
        if envelope.get(field) != expected:
            raise OperatorSnapshotEnvelopeError(f"invalid envelope {field}")
    files = envelope.get("files")
    if not isinstance(files, Mapping) or set(files) != set(_CONTENT_FILES):
        raise OperatorSnapshotEnvelopeError("envelope file map is not exact")
    for field in (*files, "descriptor_receipt_sha256", "descriptor_file_sha256"):
        value = files[field] if field in files else envelope.get(field)
        if not isinstance(value, str) or len(value) != _DIGEST_LENGTH:
            raise OperatorSnapshotEnvelopeError(f"invalid envelope {field}")
        try:
            int(value, 16)
        except ValueError as exc:
            raise OperatorSnapshotEnvelopeError(f"invalid envelope {field}") from exc
    unsigned = {
        key: value for key, value in envelope.items() if key != "envelope_sha256"
    }
    if _sha256(_canonical_bytes(unsigned)) != envelope.get("envelope_sha256"):
        raise OperatorSnapshotEnvelopeError("envelope digest does not match")
    return {
        "schema": str(envelope["schema"]),
        "state": str(envelope["state"]),
        "descriptor_receipt_sha256": str(envelope["descriptor_receipt_sha256"]),
        "descriptor_file_sha256": str(envelope["descriptor_file_sha256"]),
        "envelope_sha256": str(envelope["envelope_sha256"]),
        "files": {key: str(files[key]) for key in sorted(_CONTENT_FILES)},
    }


def _write_new(path: Path, content: bytes) -> None:
    with path.open("xb") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())


def _content_bundle(
    relay_preview_index_html: object,
    task_card_index_html: object,
    snapshot_html: object,
    descriptor: object,
) -> tuple[dict[str, bytes], dict[str, Any]]:
    try:
        validated_descriptor = verify_operator_snapshot_descriptor(
            descriptor,
            relay_preview_index_html,
            task_card_index_html,
            snapshot_html,
        )
    except OperatorSnapshotDescriptorError as exc:
        raise OperatorSnapshotEnvelopeError("snapshot descriptor is not valid") from exc
    documents = {
        "relay-preview-index.html": _document_bytes(
            relay_preview_index_html, "relay-preview index"
        ),
        "task-card-index.html": _document_bytes(
            task_card_index_html, "task-card index"
        ),
        "operator-snapshot.html": _document_bytes(snapshot_html, "snapshot"),
        "descriptor.json": _canonical_bytes(validated_descriptor),
    }
    return documents, validated_descriptor


def write_operator_snapshot_envelope(
    output_dir: object,
    relay_preview_index_html: object,
    task_card_index_html: object,
    snapshot_html: object,
    descriptor: object,
) -> dict[str, Any]:
    """Write one explicit, immutable local envelope; existing targets are refused."""
    documents, validated_descriptor = _content_bundle(
        relay_preview_index_html,
        task_card_index_html,
        snapshot_html,
        descriptor,
    )
    target = _absolute_output_path(output_dir)
    try:
        target.mkdir()
    except FileExistsError as exc:
        raise OperatorSnapshotEnvelopeError("output directory already exists") from exc
    except OSError as exc:
        raise OperatorSnapshotEnvelopeError(
            "output directory could not be created"
        ) from exc

    try:
        _write_new(target / _INCOMPLETE_MARKER, b"INCOMPLETE\n")
        for name in sorted(documents):
            _write_new(target / name, documents[name])
        file_hashes = {name: _sha256(documents[name]) for name in sorted(documents)}
        unsigned: dict[str, Any] = {
            **_STATIC_ENVELOPE_STATE,
            "files": file_hashes,
            "descriptor_receipt_sha256": validated_descriptor["descriptor_sha256"],
            "descriptor_file_sha256": file_hashes["descriptor.json"],
        }
        envelope = {
            **unsigned,
            "envelope_sha256": _sha256(_canonical_bytes(unsigned)),
        }
        _write_new(target / "envelope.json", _canonical_bytes(envelope))
        (target / _INCOMPLETE_MARKER).unlink()
    except OSError as exc:
        raise OperatorSnapshotEnvelopeError(
            "envelope remains incomplete; existing bytes were not overwritten"
        ) from exc
    return inspect_operator_snapshot_envelope(target)


def inspect_operator_snapshot_envelope(output_dir: object) -> dict[str, Any]:
    """Verify an existing local envelope by static replay; never refreshes sources."""
    target = _absolute_output_path(output_dir)
    if not target.is_dir():
        raise OperatorSnapshotEnvelopeError("output directory does not exist")
    if (target / _INCOMPLETE_MARKER).exists():
        raise OperatorSnapshotEnvelopeError("envelope is incomplete")
    try:
        entries = {entry.name for entry in target.iterdir()}
    except OSError as exc:
        raise OperatorSnapshotEnvelopeError("output directory cannot be read") from exc
    if entries != _ENVELOPE_FILES:
        raise OperatorSnapshotEnvelopeError("envelope files are not exact")
    try:
        documents = {name: (target / name).read_bytes() for name in _CONTENT_FILES}
    except OSError as exc:
        raise OperatorSnapshotEnvelopeError("envelope content cannot be read") from exc
    descriptor = _read_exact_json(target / "descriptor.json", "descriptor")
    try:
        validated_descriptor = inspect_operator_snapshot_descriptor(descriptor)
        verify_operator_snapshot_descriptor(
            validated_descriptor,
            documents["relay-preview-index.html"].decode("utf-8"),
            documents["task-card-index.html"].decode("utf-8"),
            documents["operator-snapshot.html"].decode("utf-8"),
        )
    except (OperatorSnapshotDescriptorError, UnicodeDecodeError) as exc:
        raise OperatorSnapshotEnvelopeError(
            "stored snapshot receipt is not valid"
        ) from exc
    envelope = _validate_envelope(
        _read_exact_json(target / "envelope.json", "envelope")
    )
    actual_hashes = {name: _sha256(documents[name]) for name in sorted(documents)}
    if envelope["files"] != actual_hashes:
        raise OperatorSnapshotEnvelopeError("envelope file hash does not match")
    if (
        envelope["descriptor_receipt_sha256"]
        != validated_descriptor["descriptor_sha256"]
    ):
        raise OperatorSnapshotEnvelopeError(
            "envelope descriptor receipt does not match"
        )
    if envelope["descriptor_file_sha256"] != actual_hashes["descriptor.json"]:
        raise OperatorSnapshotEnvelopeError(
            "envelope descriptor file hash does not match"
        )
    return {"path": str(target), **envelope}

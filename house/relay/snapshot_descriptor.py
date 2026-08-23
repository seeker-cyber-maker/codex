"""Hash-bound receipts for frozen, offline operator snapshot documents."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from typing import Any

from .operator_snapshot import OperatorSnapshotError, render_operator_snapshot_html

_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_DESCRIPTOR_FIELDS = frozenset(
    {
        "schema",
        "state",
        "relay_preview_index_sha256",
        "task_card_index_sha256",
        "snapshot_sha256",
        "source_state",
        "refresh",
        "listener",
        "task_state",
        "task_mutation",
        "worker_dispatch",
        "authority",
        "reverse_channel",
        "descriptor_sha256",
    }
)
_STATIC_STATE = {
    "schema": "codex-house-operator-snapshot-descriptor/1",
    "state": "FROZEN_OFFLINE",
    "source_state": "CALLER_SUPPLIED",
    "refresh": "NOT_ATTEMPTED",
    "listener": "NOT_BOUND",
    "task_state": "NOT_READ",
    "task_mutation": "NOT_ATTEMPTED",
    "worker_dispatch": "NOT_ATTEMPTED",
    "authority": "NOT_GRANTED",
    "reverse_channel": "PROHIBITED",
}


class OperatorSnapshotDescriptorError(ValueError):
    """A snapshot receipt cannot prove the required offline identity boundary."""


def _canonical_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256(document: object, label: str) -> str:
    if not isinstance(document, str) or not document:
        raise OperatorSnapshotDescriptorError(f"invalid {label} document")
    return hashlib.sha256(document.encode("utf-8")).hexdigest()


def _descriptor_digest(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def inspect_operator_snapshot_descriptor(descriptor: object) -> dict[str, str]:
    """Return a validated descriptor without loading any referenced document."""
    if not isinstance(descriptor, Mapping) or set(descriptor) != _DESCRIPTOR_FIELDS:
        raise OperatorSnapshotDescriptorError("descriptor fields are not exact")
    for field, expected in _STATIC_STATE.items():
        if descriptor.get(field) != expected:
            raise OperatorSnapshotDescriptorError(f"invalid descriptor {field}")
    for field in (
        "relay_preview_index_sha256",
        "task_card_index_sha256",
        "snapshot_sha256",
        "descriptor_sha256",
    ):
        value = descriptor.get(field)
        if not isinstance(value, str) or not _DIGEST.fullmatch(value):
            raise OperatorSnapshotDescriptorError(f"invalid descriptor {field}")
    unsigned = {
        key: value for key, value in descriptor.items() if key != "descriptor_sha256"
    }
    if _descriptor_digest(unsigned) != descriptor["descriptor_sha256"]:
        raise OperatorSnapshotDescriptorError("descriptor digest does not match")
    return {key: str(descriptor[key]) for key in sorted(_DESCRIPTOR_FIELDS)}


def build_operator_snapshot_descriptor(
    relay_preview_index_html: object,
    task_card_index_html: object,
    snapshot_html: object,
) -> dict[str, str]:
    """Bind caller-supplied static documents after exact offline recomposition."""
    try:
        expected_snapshot = render_operator_snapshot_html(
            relay_preview_index_html, task_card_index_html
        )
    except OperatorSnapshotError as exc:
        raise OperatorSnapshotDescriptorError("source documents are not valid") from exc
    if not isinstance(snapshot_html, str) or snapshot_html != expected_snapshot:
        raise OperatorSnapshotDescriptorError(
            "snapshot does not match frozen source documents"
        )
    unsigned: dict[str, str] = {
        **_STATIC_STATE,
        "relay_preview_index_sha256": _sha256(
            relay_preview_index_html, "relay-preview index"
        ),
        "task_card_index_sha256": _sha256(task_card_index_html, "task-card index"),
        "snapshot_sha256": _sha256(snapshot_html, "snapshot"),
    }
    return {
        **unsigned,
        "descriptor_sha256": _descriptor_digest(unsigned),
    }


def verify_operator_snapshot_descriptor(
    descriptor: object,
    relay_preview_index_html: object,
    task_card_index_html: object,
    snapshot_html: object,
) -> dict[str, str]:
    """Verify descriptor identity by exact static replay without source retrieval."""
    validated = inspect_operator_snapshot_descriptor(descriptor)
    expected = build_operator_snapshot_descriptor(
        relay_preview_index_html, task_card_index_html, snapshot_html
    )
    if validated != expected:
        raise OperatorSnapshotDescriptorError(
            "descriptor does not match replayed snapshot"
        )
    return validated

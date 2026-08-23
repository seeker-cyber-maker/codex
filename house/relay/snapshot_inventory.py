"""Content-free, read-only inventory for explicitly named snapshot envelopes."""

from __future__ import annotations

from pathlib import Path

from .snapshot_envelope import (
    OperatorSnapshotEnvelopeError,
    inspect_operator_snapshot_envelope,
)

MAX_ENVELOPE_PATHS = 32


class OperatorSnapshotInventoryError(ValueError):
    """The caller did not supply a bounded list of envelope locations."""


def _path_record(value: object) -> dict[str, str]:
    if not isinstance(value, (str, Path)):
        return {
            "input_path": repr(value),
            "path": "",
            "state": "REJECTED_INPUT",
            "reason": "path must be text or Path",
        }
    path = Path(value)
    if not path.is_absolute():
        return {
            "input_path": str(path),
            "path": "",
            "state": "REJECTED_INPUT",
            "reason": "path must be absolute",
        }
    try:
        canonical = path.resolve(strict=False)
    except OSError:
        return {
            "input_path": str(path),
            "path": "",
            "state": "REJECTED_INPUT",
            "reason": "path cannot be resolved",
        }
    return {
        "input_path": str(path),
        "path": str(canonical),
        "state": "PENDING",
        "reason": "",
    }


def inspect_operator_snapshot_inventory(envelope_paths: object) -> list[dict[str, str]]:
    """Inspect only caller-supplied paths; no search, mutation, or repair occurs."""
    if not isinstance(envelope_paths, (list, tuple)):
        raise OperatorSnapshotInventoryError("envelope paths must be a list or tuple")
    if not 1 <= len(envelope_paths) <= MAX_ENVELOPE_PATHS:
        raise OperatorSnapshotInventoryError(
            f"envelope path count must be between 1 and {MAX_ENVELOPE_PATHS}"
        )
    records = [_path_record(value) for value in envelope_paths]
    counts: dict[str, int] = {}
    for record in records:
        if record["state"] == "PENDING":
            counts[record["path"]] = counts.get(record["path"], 0) + 1
    for record in records:
        if record["state"] == "PENDING" and counts[record["path"]] > 1:
            record["state"] = "REJECTED_INPUT"
            record["reason"] = "duplicate canonical path"

    results: list[dict[str, str]] = []
    for record in records:
        if record["state"] != "PENDING":
            results.append(record)
            continue
        try:
            receipt = inspect_operator_snapshot_envelope(record["path"])
        except OperatorSnapshotEnvelopeError as exc:
            results.append(
                {
                    **record,
                    "state": "REJECTED_ENVELOPE",
                    "reason": str(exc),
                }
            )
            continue
        results.append(
            {
                "input_path": record["input_path"],
                "path": record["path"],
                "state": "VALID_OFFLINE",
                "reason": "",
                "descriptor_receipt_sha256": str(receipt["descriptor_receipt_sha256"]),
                "envelope_sha256": str(receipt["envelope_sha256"]),
            }
        )
    return results

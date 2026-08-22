"""Static relay addressing from a previously validated worker-catalog receipt."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

RECEIPT_SCHEMA = "codex-house-local-worker-catalog-receipt/1"
IDENTIFIER_RE = re.compile(r"^[a-z0-9][a-z0-9._:-]{1,127}$")
RECEIPT_FIELDS = frozenset(
    {
        "schema",
        "catalog_sha256",
        "source",
        "source_commit",
        "source_tree",
        "workers",
        "active_worker_ids",
        "qualified_worker_ids",
        "runtime_disposition",
        "claim_ceiling",
    }
)
WORKER_FIELDS = frozenset({"id", "approval", "status", "dispatch", "capabilities"})


class RelayDirectoryError(ValueError):
    """The supplied catalog receipt cannot safely serve as relay metadata."""


def _identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or not IDENTIFIER_RE.fullmatch(value):
        raise RelayDirectoryError(f"invalid {label}")
    return value


class RelayDirectory:
    """Read-only addressing metadata; it never selects or invokes a worker."""

    def __init__(self, receipt: object) -> None:
        if not isinstance(receipt, Mapping) or set(receipt) != RECEIPT_FIELDS:
            raise RelayDirectoryError("catalog receipt fields are not exact")
        if receipt.get("schema") != RECEIPT_SCHEMA:
            raise RelayDirectoryError("invalid catalog receipt schema")
        if receipt.get("runtime_disposition") != "NOT_ATTEMPTED":
            raise RelayDirectoryError(
                "catalog runtime disposition must be NOT_ATTEMPTED"
            )
        catalog_sha256 = receipt.get("catalog_sha256")
        if not isinstance(catalog_sha256, str) or not re.fullmatch(
            r"[0-9a-f]{64}", catalog_sha256
        ):
            raise RelayDirectoryError("invalid catalog_sha256")
        raw_workers = receipt.get("workers")
        if not isinstance(raw_workers, list) or not raw_workers:
            raise RelayDirectoryError("catalog workers are required")

        workers: dict[str, dict[str, Any]] = {}
        for raw in raw_workers:
            if not isinstance(raw, Mapping) or set(raw) != WORKER_FIELDS:
                raise RelayDirectoryError("catalog worker fields are not exact")
            worker_id = _identifier(raw.get("id"), "worker id")
            if raw.get("approval") != "approved_specialist":
                raise RelayDirectoryError("catalog worker is not approved")
            status = raw.get("status")
            dispatch = raw.get("dispatch")
            if (status, dispatch) not in {
                ("active", "available"),
                ("qualified", "not_dispatchable"),
            }:
                raise RelayDirectoryError(
                    "catalog worker dispatch state is inconsistent"
                )
            capabilities = raw.get("capabilities")
            if not isinstance(capabilities, list) or not capabilities:
                raise RelayDirectoryError("catalog worker capabilities are required")
            normalized_capabilities = [
                _identifier(value, "capability") for value in capabilities
            ]
            if len(normalized_capabilities) != len(set(normalized_capabilities)):
                raise RelayDirectoryError("catalog worker capabilities must be unique")
            if worker_id in workers:
                raise RelayDirectoryError("catalog worker identifiers must be unique")
            workers[worker_id] = {
                "id": worker_id,
                "status": status,
                "dispatch": dispatch,
                "capabilities": sorted(normalized_capabilities),
            }
        self.catalog_sha256 = catalog_sha256
        self._workers = workers

    def address(self, recipient_id: str) -> dict[str, Any]:
        recipient_id = _identifier(recipient_id, "recipient_id")
        worker = self._workers.get(recipient_id)
        if worker is None:
            raise RelayDirectoryError("unknown recipient")
        return {
            "catalog_sha256": self.catalog_sha256,
            **worker,
            "runtime_disposition": "NOT_ATTEMPTED",
            "authority_disposition": "NO_AUTHORITY_GRANTED",
        }

    def find_capability(self, capability: str) -> list[dict[str, str]]:
        capability = _identifier(capability, "capability")
        return [
            {
                "id": worker["id"],
                "status": worker["status"],
                "dispatch": worker["dispatch"],
            }
            for worker in sorted(self._workers.values(), key=lambda item: item["id"])
            if capability in worker["capabilities"]
        ]

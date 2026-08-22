"""Validate a hash-bound provider worker catalog without contacting a provider."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from typing import Any

SCHEMA = "codex-house-local-worker-catalog/1"
RECEIPT_SCHEMA = "codex-house-local-worker-catalog-receipt/1"
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._:-]{1,127}$")
SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
ALLOWED_TOP_LEVEL = frozenset(
    {"schema", "source", "source_commit", "source_tree", "workers"}
)
ALLOWED_WORKER_FIELDS = frozenset(
    {"id", "approval", "status", "dispatch", "capabilities"}
)
APPROVAL = "approved_specialist"
STATUS_TO_DISPATCH = {
    "active": "available",
    "qualified": "not_dispatchable",
}


class CatalogError(ValueError):
    """A catalog export failed a structural or authority boundary."""


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        raise CatalogError(f"invalid {label}")
    return value


def _sha1(value: object, label: str) -> str:
    if not isinstance(value, str) or not SHA1_RE.fullmatch(value):
        raise CatalogError(f"invalid {label}")
    return value


def _worker(raw: object) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or set(raw) != ALLOWED_WORKER_FIELDS:
        raise CatalogError("worker fields are not exact")
    worker_id = _identifier(raw.get("id"), "worker id")
    if raw.get("approval") != APPROVAL:
        raise CatalogError("worker is not an approved specialist")
    status = raw.get("status")
    dispatch = raw.get("dispatch")
    if STATUS_TO_DISPATCH.get(status) != dispatch:
        raise CatalogError("worker dispatch state is inconsistent")
    capabilities = raw.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities:
        raise CatalogError("worker capabilities are required")
    if len(capabilities) != len(set(capabilities)):
        raise CatalogError("worker capabilities must be unique")
    normalized_capabilities = [
        _identifier(value, "capability") for value in capabilities
    ]
    return {
        "id": worker_id,
        "approval": APPROVAL,
        "status": status,
        "dispatch": dispatch,
        "capabilities": normalized_capabilities,
    }


def ingest_catalog(raw: object) -> dict[str, Any]:
    """Return an offline receipt; never starts, selects, or probes a worker."""
    if not isinstance(raw, Mapping) or set(raw) != ALLOWED_TOP_LEVEL:
        raise CatalogError("catalog fields are not exact")
    if raw.get("schema") != SCHEMA:
        raise CatalogError("invalid catalog schema")
    source = _identifier(raw.get("source"), "source")
    source_commit = _sha1(raw.get("source_commit"), "source commit")
    source_tree = _sha1(raw.get("source_tree"), "source tree")
    workers_raw = raw.get("workers")
    if not isinstance(workers_raw, list) or not workers_raw:
        raise CatalogError("catalog workers are required")
    workers = [_worker(item) for item in workers_raw]
    identifiers = [worker["id"] for worker in workers]
    if len(identifiers) != len(set(identifiers)):
        raise CatalogError("worker identifiers must be unique")
    workers.sort(key=lambda item: item["id"])
    active = [worker["id"] for worker in workers if worker["status"] == "active"]
    qualified = [worker["id"] for worker in workers if worker["status"] == "qualified"]
    return {
        "schema": RECEIPT_SCHEMA,
        "catalog_sha256": _sha256(raw),
        "source": source,
        "source_commit": source_commit,
        "source_tree": source_tree,
        "workers": workers,
        "active_worker_ids": active,
        "qualified_worker_ids": qualified,
        "runtime_disposition": "NOT_ATTEMPTED",
        "claim_ceiling": "Offline catalog intake only; no worker was selected, started, probed, or granted authority.",
    }

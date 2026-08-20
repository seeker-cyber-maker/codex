"""Conserved Codex session ancestry and reversible context views.

This module deliberately operates on exported app-server records and a separate
house journal. It never opens or mutates Codex's native SQLite databases or
rollout JSONL files.
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import pathlib
import re
import sys
from collections.abc import Iterable, Mapping
from typing import Any

EVENT_SCHEMA = "codex-house-event/1"
TREE_SCHEMA = "codex-session-tree/1"
VIEW_SCHEMA = "codex-context-view/1"
RECEIPT_SCHEMA = "codex-context-operation-receipt/1"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
VALID_EVENT_KINDS = {
    "thread",
    "turn",
    "message",
    "tool",
    "approval",
    "artifact",
    "context",
    "receipt",
    "error",
}
VALID_EVENT_SOURCES = {"app_server", "rollout", "recovery_import", "house_adapter"}
VALID_REDACTIONS = {"none", "view_redacted", "source_access_restricted"}
VALID_BLOCK_MODES = {"verbatim", "summary", "locator", "retrieved"}
VALID_BLOCK_STATES = {"core", "pinned", "optional", "excluded"}
VALID_EXCLUSION_REASONS = {
    "out_of_scope",
    "superseded",
    "attention_trap",
    "budget",
    "sensitive",
}
EVENT_FIELDS = {
    "schema",
    "event_id",
    "session_id",
    "branch_id",
    "parent_branch_id",
    "fork_turn_id",
    "turn_id",
    "item_id",
    "sequence",
    "occurred_at",
    "kind",
    "source",
    "payload_ref",
    "payload_sha256",
    "redaction",
    "previous_event_sha256",
    "event_sha256",
}
VIEW_FIELDS = {
    "schema",
    "view_id",
    "session_id",
    "branch_id",
    "task_id",
    "parent_view_id",
    "created_at",
    "budget_tokens",
    "blocks",
    "exclusions",
    "authority_hash",
    "operation",
    "restored_from_view_id",
}
BLOCK_FIELDS = {
    "block_id",
    "mode",
    "state",
    "reason",
    "source_ref",
    "source_sha256",
}
EXCLUSION_FIELDS = {"source_ref", "reason", "block_id"}


class ContextViewError(ValueError):
    """Fail-closed context-view error with a stable machine code."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def _require_string(record: Mapping[str, Any], key: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _snake_or_camel(record: Mapping[str, Any], snake: str, camel: str) -> Any:
    if snake in record:
        return record[snake]
    return record.get(camel)


def _read_json(path: pathlib.Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def _journal_records(path: pathlib.Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.exists():
        return records
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"invalid journal JSON at line {line_number}: {exc}"
                ) from exc
            if not isinstance(record, dict):
                raise TypeError(f"journal line {line_number} is not an object")
            records.append(record)
    return records


def _validate_event_shape(event: Mapping[str, Any]) -> None:
    unexpected = set(event) - EVENT_FIELDS
    if unexpected:
        raise ValueError(f"event has unsupported fields: {sorted(unexpected)}")
    if event.get("schema") != EVENT_SCHEMA:
        raise ValueError(f"event schema must be {EVENT_SCHEMA}")
    for key in (
        "event_id",
        "session_id",
        "branch_id",
        "occurred_at",
        "kind",
        "source",
        "payload_ref",
        "redaction",
    ):
        _require_string(event, key)
    if event["kind"] not in VALID_EVENT_KINDS:
        raise ValueError(f"unsupported event kind: {event['kind']}")
    if event["source"] not in VALID_EVENT_SOURCES:
        raise ValueError(f"unsupported event source: {event['source']}")
    if event["redaction"] not in VALID_REDACTIONS:
        raise ValueError(f"unsupported redaction state: {event['redaction']}")
    sequence = event.get("sequence")
    if not isinstance(sequence, int) or sequence < 1:
        raise ValueError("sequence must be a positive integer")
    payload_sha256 = event.get("payload_sha256")
    if payload_sha256 is not None and (
        not isinstance(payload_sha256, str) or not SHA256_RE.fullmatch(payload_sha256)
    ):
        raise ValueError("payload_sha256 must be null or a lowercase SHA-256 digest")
    for key in ("parent_branch_id", "fork_turn_id", "turn_id", "item_id"):
        if event.get(key) is not None and not isinstance(event[key], str):
            raise ValueError(f"{key} must be null or a string")


def append_event(path: pathlib.Path, event: Mapping[str, Any]) -> dict[str, Any]:
    """Append one hash-chained event without rewriting existing records."""

    records = verify_journal(path) if path.exists() else []
    candidate = copy.deepcopy(dict(event))
    _validate_event_shape(candidate)
    if any(item["event_id"] == candidate["event_id"] for item in records):
        raise ValueError(f"duplicate event_id: {candidate['event_id']}")
    branch_sequences = [
        item["sequence"]
        for item in records
        if item["branch_id"] == candidate["branch_id"]
    ]
    expected_sequence = max(branch_sequences, default=0) + 1
    if candidate["sequence"] != expected_sequence:
        raise ValueError(
            f"branch {candidate['branch_id']} sequence must be {expected_sequence}, "
            f"got {candidate['sequence']}"
        )
    candidate["previous_event_sha256"] = (
        records[-1]["event_sha256"] if records else None
    )
    candidate_without_hash = dict(candidate)
    candidate_without_hash.pop("event_sha256", None)
    candidate["event_sha256"] = _sha256(candidate_without_hash)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(_canonical_json(candidate).decode("utf-8"))
        handle.write("\n")
    return candidate


def verify_journal(path: pathlib.Path) -> list[dict[str, Any]]:
    """Verify the full hash chain, unique IDs, and per-branch sequence."""

    records = _journal_records(path)
    previous_hash: str | None = None
    seen_ids: set[str] = set()
    sequences: dict[str, int] = {}
    for index, event in enumerate(records, start=1):
        _validate_event_shape(event)
        event_id = event["event_id"]
        if event_id in seen_ids:
            raise ValueError(f"duplicate event_id at line {index}: {event_id}")
        seen_ids.add(event_id)
        branch_id = event["branch_id"]
        expected_sequence = sequences.get(branch_id, 0) + 1
        if event["sequence"] != expected_sequence:
            raise ValueError(
                f"invalid sequence at line {index}: expected {expected_sequence}, "
                f"got {event['sequence']}"
            )
        sequences[branch_id] = expected_sequence
        if event.get("previous_event_sha256") != previous_hash:
            raise ValueError(f"broken previous-event hash at line {index}")
        claimed_hash = event.get("event_sha256")
        if not isinstance(claimed_hash, str) or not SHA256_RE.fullmatch(claimed_hash):
            raise ValueError(f"missing or invalid event hash at line {index}")
        unhashed = dict(event)
        unhashed.pop("event_sha256")
        observed_hash = _sha256(unhashed)
        if observed_hash != claimed_hash:
            raise ValueError(f"event hash mismatch at line {index}")
        previous_hash = claimed_hash
    return records


def _thread_records(value: Any) -> list[Mapping[str, Any]]:
    if isinstance(value, list):
        records = value
    elif isinstance(value, dict) and isinstance(value.get("threads"), list):
        records = value["threads"]
    elif isinstance(value, dict) and isinstance(value.get("data"), list):
        records = value["data"]
    else:
        raise TypeError("thread input must be an array or contain a threads/data array")
    if not all(isinstance(item, Mapping) for item in records):
        raise ValueError("every thread must be an object")
    return records


def project_session_tree(
    value: Any, require_fork_points: bool = False
) -> dict[str, Any]:
    """Derive a stable ancestry projection from app-server Thread records."""

    raw_records = _thread_records(value)
    by_id: dict[str, dict[str, Any]] = {}
    for raw in raw_records:
        thread_id = _require_string(raw, "id")
        if thread_id in by_id:
            raise ValueError(f"duplicate thread id: {thread_id}")
        forked_from_id = _snake_or_camel(raw, "forked_from_id", "forkedFromId")
        parent_thread_id = _snake_or_camel(raw, "parent_thread_id", "parentThreadId")
        fork_turn_id = _snake_or_camel(raw, "fork_turn_id", "forkPointTurnId")
        reported_session_id = _snake_or_camel(raw, "session_id", "sessionId")
        for key, item in (
            ("forkedFromId", forked_from_id),
            ("parentThreadId", parent_thread_id),
            ("forkPointTurnId", fork_turn_id),
            ("sessionId", reported_session_id),
        ):
            if item is not None and not isinstance(item, str):
                raise ValueError(f"thread {thread_id} {key} must be null or a string")
        if forked_from_id and parent_thread_id and forked_from_id != parent_thread_id:
            raise ValueError(
                f"thread {thread_id} has two different ancestry parents: "
                f"fork {forked_from_id}, spawn {parent_thread_id}"
            )
        if fork_turn_id and not forked_from_id:
            raise ValueError(f"thread {thread_id} has a fork point but no fork parent")
        if require_fork_points and forked_from_id and not fork_turn_id:
            raise ValueError(f"thread {thread_id} is missing a captured fork point")
        parent = forked_from_id or parent_thread_id
        relation = "fork" if forked_from_id else "spawn" if parent_thread_id else "root"
        by_id[thread_id] = {
            "thread_id": thread_id,
            "reported_session_id": reported_session_id,
            "parent_branch_id": parent,
            "relation": relation,
            "fork_turn_id": fork_turn_id,
            "children": [],
        }

    for thread_id, node in by_id.items():
        parent = node["parent_branch_id"]
        if parent is not None and parent not in by_id:
            raise ValueError(f"thread {thread_id} references missing parent {parent}")
        if parent is not None:
            by_id[parent]["children"].append(thread_id)

    roots: dict[str, str] = {}
    visiting: set[str] = set()

    def derive_root(thread_id: str) -> str:
        if thread_id in roots:
            return roots[thread_id]
        if thread_id in visiting:
            raise ValueError(f"ancestry cycle detected at thread {thread_id}")
        visiting.add(thread_id)
        parent = by_id[thread_id]["parent_branch_id"]
        root = thread_id if parent is None else derive_root(parent)
        visiting.remove(thread_id)
        roots[thread_id] = root
        return root

    for thread_id, node in by_id.items():
        derived = derive_root(thread_id)
        reported = node["reported_session_id"]
        if reported is None:
            status = "missing"
        elif reported == derived:
            status = "consistent"
        elif reported == thread_id and thread_id != derived:
            status = "unloaded_self_fallback"
        else:
            raise ValueError(
                f"thread {thread_id} reports conflicting session id {reported}; "
                f"derived root is {derived}"
            )
        node["derived_session_id"] = derived
        node["session_id_status"] = status
        node["children"].sort()

    ordered_nodes = [by_id[thread_id] for thread_id in sorted(by_id)]
    tree = {
        "schema": TREE_SCHEMA,
        "nodes": ordered_nodes,
        "roots": sorted(
            thread_id
            for thread_id, node in by_id.items()
            if not node["parent_branch_id"]
        ),
        "source_thread_count": len(ordered_nodes),
    }
    sealable = dict(tree)
    tree["projection_sha256"] = _sha256(sealable)
    return tree


def _source_index(events: Iterable[Mapping[str, Any]]) -> dict[str, str | None]:
    sources: dict[str, str | None] = {}
    for event in events:
        source_ref = event["payload_ref"]
        digest = event.get("payload_sha256")
        if source_ref in sources and sources[source_ref] != digest:
            raise ContextViewError(
                "SOURCE_HASH_CONFLICT", f"source {source_ref} has conflicting digests"
            )
        sources[source_ref] = digest
    return sources


def _validate_block(
    block: Mapping[str, Any], sources: Mapping[str, str | None]
) -> None:
    unexpected = set(block) - BLOCK_FIELDS
    if unexpected:
        raise ContextViewError(
            "INVALID_BLOCK", f"block has unsupported fields: {sorted(unexpected)}"
        )
    block_id = _require_string(block, "block_id")
    mode = _require_string(block, "mode")
    state = _require_string(block, "state")
    _require_string(block, "reason")
    source_ref = _require_string(block, "source_ref")
    if mode not in VALID_BLOCK_MODES:
        raise ContextViewError(
            "INVALID_BLOCK", f"block {block_id} has unsupported mode {mode}"
        )
    if state not in VALID_BLOCK_STATES:
        raise ContextViewError(
            "INVALID_BLOCK", f"block {block_id} has unsupported state {state}"
        )
    if source_ref not in sources:
        raise ContextViewError(
            "UNKNOWN_SOURCE", f"block {block_id} references unknown source"
        )
    source_sha256 = block.get("source_sha256")
    if source_sha256 is not None and (
        not isinstance(source_sha256, str) or not SHA256_RE.fullmatch(source_sha256)
    ):
        raise ContextViewError(
            "INVALID_BLOCK", f"block {block_id} has invalid source_sha256"
        )
    if source_sha256 != sources[source_ref]:
        raise ContextViewError(
            "SOURCE_HASH_MISMATCH", f"block {block_id} source digest mismatch"
        )


def _seal_view(view: Mapping[str, Any]) -> dict[str, Any]:
    sealed = copy.deepcopy(dict(view))
    sealed.pop("view_id", None)
    sealed["view_id"] = f"cv_{_sha256(sealed)[:24]}"
    return sealed


def verify_context_view(
    view: Mapping[str, Any], events: Iterable[Mapping[str, Any]]
) -> dict[str, Any]:
    unexpected = set(view) - VIEW_FIELDS
    if unexpected:
        raise ContextViewError(
            "INVALID_VIEW", f"view has unsupported fields: {sorted(unexpected)}"
        )
    if view.get("schema") != VIEW_SCHEMA:
        raise ContextViewError("INVALID_VIEW", f"view schema must be {VIEW_SCHEMA}")
    for key in ("view_id", "session_id", "branch_id", "task_id", "created_at"):
        _require_string(view, key)
    authority_hash = _require_string(view, "authority_hash")
    if not SHA256_RE.fullmatch(authority_hash):
        raise ContextViewError(
            "INVALID_VIEW", "authority_hash must be a lowercase SHA-256 digest"
        )
    budget = view.get("budget_tokens")
    if not isinstance(budget, int) or budget < 0:
        raise ContextViewError(
            "INVALID_VIEW", "budget_tokens must be a non-negative integer"
        )
    blocks = view.get("blocks")
    exclusions = view.get("exclusions")
    if not isinstance(blocks, list) or not isinstance(exclusions, list):
        raise ContextViewError("INVALID_VIEW", "blocks and exclusions must be arrays")
    sources = _source_index(events)
    block_ids: set[str] = set()
    for block in blocks:
        if not isinstance(block, Mapping):
            raise ContextViewError("INVALID_BLOCK", "every block must be an object")
        _validate_block(block, sources)
        block_id = block["block_id"]
        if block_id in block_ids:
            raise ContextViewError("DUPLICATE_BLOCK", f"duplicate block id {block_id}")
        block_ids.add(block_id)
    for exclusion in exclusions:
        if not isinstance(exclusion, Mapping):
            raise ContextViewError(
                "INVALID_EXCLUSION", "every exclusion must be an object"
            )
        unexpected = set(exclusion) - EXCLUSION_FIELDS
        if unexpected:
            raise ContextViewError(
                "INVALID_EXCLUSION",
                f"exclusion has unsupported fields: {sorted(unexpected)}",
            )
        source_ref = _require_string(exclusion, "source_ref")
        reason = _require_string(exclusion, "reason")
        if source_ref not in sources:
            raise ContextViewError(
                "UNKNOWN_SOURCE", f"exclusion references unknown source {source_ref}"
            )
        if reason not in VALID_EXCLUSION_REASONS:
            raise ContextViewError(
                "INVALID_EXCLUSION", f"unsupported exclusion reason {reason}"
            )
    expected_view_id = _seal_view(view)["view_id"]
    if view["view_id"] != expected_view_id:
        raise ContextViewError(
            "VIEW_HASH_MISMATCH", "view_id does not match view contents"
        )
    return copy.deepcopy(dict(view))


def create_context_view(
    spec: Mapping[str, Any], events: Iterable[Mapping[str, Any]]
) -> dict[str, Any]:
    view = {
        "schema": VIEW_SCHEMA,
        "session_id": _require_string(spec, "session_id"),
        "branch_id": _require_string(spec, "branch_id"),
        "task_id": _require_string(spec, "task_id"),
        "parent_view_id": None,
        "created_at": spec.get("created_at") or _utc_now(),
        "budget_tokens": spec.get("budget_tokens", 0),
        "blocks": copy.deepcopy(spec.get("blocks", [])),
        "exclusions": copy.deepcopy(spec.get("exclusions", [])),
        "authority_hash": _require_string(spec, "authority_hash"),
    }
    sealed = _seal_view(view)
    return verify_context_view(sealed, events)


def _find_block(blocks: list[dict[str, Any]], block_id: str) -> int:
    matches = [
        index for index, block in enumerate(blocks) if block["block_id"] == block_id
    ]
    if len(matches) != 1:
        raise ContextViewError(
            "BLOCK_NOT_FOUND", f"expected exactly one block {block_id}"
        )
    return matches[0]


def _receipt(body: Mapping[str, Any]) -> dict[str, Any]:
    receipt = copy.deepcopy(dict(body))
    receipt["schema"] = RECEIPT_SCHEMA
    receipt.pop("receipt_id", None)
    receipt["receipt_id"] = f"cr_{_sha256(receipt)[:24]}"
    return receipt


def rejected_operation_receipt(
    view: Mapping[str, Any], operation: Mapping[str, Any], error: ContextViewError
) -> dict[str, Any]:
    return _receipt(
        {
            "state": "REJECTED",
            "at": operation.get("at") or _utc_now(),
            "operation": operation.get("operation"),
            "prior_view_id": view.get("view_id"),
            "new_view_id": None,
            "error_code": error.code,
            "error": str(error),
        }
    )


def apply_context_operation(
    view: Mapping[str, Any],
    operation: Mapping[str, Any],
    events: Iterable[Mapping[str, Any]],
    parent_view: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Apply a context-only operation and return the new view plus receipt."""

    event_list = list(events)
    current = verify_context_view(view, event_list)
    for key in ("task_id", "branch_id", "authority_hash"):
        supplied = operation.get(key)
        if supplied != current[key]:
            raise ContextViewError(
                "STALE_CONTEXT_VIEW",
                f"operation {key} does not match active context view",
            )
    operation_name = _require_string(operation, "operation")
    created_at = operation.get("at") or _utc_now()
    next_view = {
        "schema": VIEW_SCHEMA,
        "session_id": current["session_id"],
        "branch_id": current["branch_id"],
        "task_id": current["task_id"],
        "parent_view_id": current["view_id"],
        "created_at": created_at,
        "budget_tokens": operation.get("budget_tokens", current["budget_tokens"]),
        "blocks": copy.deepcopy(current["blocks"]),
        "exclusions": copy.deepcopy(current["exclusions"]),
        "authority_hash": current["authority_hash"],
        "operation": operation_name,
    }

    if operation_name in {"add", "retrieve"}:
        block = copy.deepcopy(operation.get("block"))
        if not isinstance(block, dict):
            raise ContextViewError(
                "INVALID_OPERATION", f"{operation_name} requires a block"
            )
        if operation_name == "retrieve":
            block["mode"] = "retrieved"
        _validate_block(block, _source_index(event_list))
        if any(item["block_id"] == block["block_id"] for item in next_view["blocks"]):
            raise ContextViewError(
                "DUPLICATE_BLOCK", f"duplicate block id {block['block_id']}"
            )
        next_view["blocks"].append(block)
        next_view["exclusions"] = [
            item
            for item in next_view["exclusions"]
            if item["source_ref"] != block["source_ref"]
        ]
    elif operation_name == "remove":
        block_id = _require_string(operation, "block_id")
        reason = _require_string(operation, "reason")
        if reason not in VALID_EXCLUSION_REASONS:
            raise ContextViewError(
                "INVALID_OPERATION", f"unsupported exclusion reason {reason}"
            )
        index = _find_block(next_view["blocks"], block_id)
        removed = next_view["blocks"].pop(index)
        next_view["exclusions"] = [
            item
            for item in next_view["exclusions"]
            if item["source_ref"] != removed["source_ref"]
        ]
        next_view["exclusions"].append(
            {
                "source_ref": removed["source_ref"],
                "reason": reason,
                "block_id": removed["block_id"],
            }
        )
    elif operation_name in {"pin", "unpin"}:
        block_id = _require_string(operation, "block_id")
        index = _find_block(next_view["blocks"], block_id)
        next_view["blocks"][index]["state"] = (
            "pinned" if operation_name == "pin" else operation.get("state", "optional")
        )
        if next_view["blocks"][index]["state"] not in {"core", "optional", "pinned"}:
            raise ContextViewError(
                "INVALID_OPERATION", "unpin state must be core or optional"
            )
    elif operation_name == "replace-summary":
        block_id = _require_string(operation, "block_id")
        replacement = copy.deepcopy(operation.get("block"))
        if not isinstance(replacement, dict) or replacement.get("mode") != "summary":
            raise ContextViewError(
                "INVALID_OPERATION", "replace-summary requires a summary-mode block"
            )
        _validate_block(replacement, _source_index(event_list))
        index = _find_block(next_view["blocks"], block_id)
        if replacement["block_id"] != block_id and any(
            item["block_id"] == replacement["block_id"] for item in next_view["blocks"]
        ):
            raise ContextViewError(
                "DUPLICATE_BLOCK", "replacement block id already exists"
            )
        next_view["blocks"][index] = replacement
    elif operation_name == "restore-parent-view":
        if parent_view is None:
            raise ContextViewError(
                "INVALID_OPERATION", "restore-parent-view requires the parent view"
            )
        restored = verify_context_view(parent_view, event_list)
        target_view_id = _require_string(operation, "target_view_id")
        if (
            restored["view_id"] != target_view_id
            or current["parent_view_id"] != target_view_id
        ):
            raise ContextViewError(
                "STALE_CONTEXT_VIEW",
                "restore target is not the active view's direct parent",
            )
        for key in ("session_id", "branch_id", "task_id", "authority_hash"):
            if restored[key] != current[key]:
                raise ContextViewError(
                    "STALE_CONTEXT_VIEW", f"restore target has different {key}"
                )
        next_view["blocks"] = copy.deepcopy(restored["blocks"])
        next_view["exclusions"] = copy.deepcopy(restored["exclusions"])
        next_view["restored_from_view_id"] = restored["view_id"]
    else:
        raise ContextViewError(
            "INVALID_OPERATION", f"unsupported operation {operation_name}"
        )

    next_view = _seal_view(next_view)
    verify_context_view(next_view, event_list)
    receipt = _receipt(
        {
            "state": "APPLIED",
            "at": created_at,
            "operation": operation_name,
            "prior_view_id": current["view_id"],
            "new_view_id": next_view["view_id"],
            "error_code": None,
            "error": None,
        }
    )
    return next_view, receipt


def _event_from_file(path: pathlib.Path) -> dict[str, Any]:
    value = _read_json(path)
    if not isinstance(value, dict):
        raise TypeError("event input must be an object")
    return value


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    append = subparsers.add_parser(
        "append-event", help="append one event to a house journal"
    )
    append.add_argument("journal", type=pathlib.Path)
    append.add_argument("event", type=pathlib.Path)

    verify = subparsers.add_parser(
        "verify-journal", help="verify the complete journal chain"
    )
    verify.add_argument("journal", type=pathlib.Path)

    tree = subparsers.add_parser(
        "project-tree", help="project app-server threads as a tree"
    )
    tree.add_argument("threads", type=pathlib.Path)
    tree.add_argument("output", type=pathlib.Path)
    tree.add_argument("--require-fork-points", action="store_true")

    create = subparsers.add_parser("create-view", help="create a sealed context view")
    create.add_argument("journal", type=pathlib.Path)
    create.add_argument("spec", type=pathlib.Path)
    create.add_argument("output", type=pathlib.Path)

    check_view = subparsers.add_parser("verify-view", help="verify a context view")
    check_view.add_argument("journal", type=pathlib.Path)
    check_view.add_argument("view", type=pathlib.Path)

    apply = subparsers.add_parser(
        "apply-view", help="apply one reversible context operation"
    )
    apply.add_argument("journal", type=pathlib.Path)
    apply.add_argument("view", type=pathlib.Path)
    apply.add_argument("operation", type=pathlib.Path)
    apply.add_argument("output", type=pathlib.Path)
    apply.add_argument("receipt", type=pathlib.Path)
    apply.add_argument("--parent-view", type=pathlib.Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "append-event":
            result = append_event(args.journal, _event_from_file(args.event))
            print(json.dumps(result, sort_keys=True))
        elif args.command == "verify-journal":
            records = verify_journal(args.journal)
            print(
                json.dumps({"state": "PASSED", "events": len(records)}, sort_keys=True)
            )
        elif args.command == "project-tree":
            result = project_session_tree(
                _read_json(args.threads), require_fork_points=args.require_fork_points
            )
            _write_json(args.output, result)
            print(
                json.dumps(
                    {"state": "PASSED", "threads": result["source_thread_count"]}
                )
            )
        elif args.command == "create-view":
            events = verify_journal(args.journal)
            result = create_context_view(_read_json(args.spec), events)
            _write_json(args.output, result)
            print(json.dumps({"state": "PASSED", "viewId": result["view_id"]}))
        elif args.command == "verify-view":
            events = verify_journal(args.journal)
            result = verify_context_view(_read_json(args.view), events)
            print(json.dumps({"state": "PASSED", "viewId": result["view_id"]}))
        elif args.command == "apply-view":
            events = verify_journal(args.journal)
            view = _read_json(args.view)
            operation = _read_json(args.operation)
            parent_view = _read_json(args.parent_view) if args.parent_view else None
            try:
                result, receipt = apply_context_operation(
                    view, operation, events, parent_view=parent_view
                )
            except ContextViewError as exc:
                receipt = rejected_operation_receipt(view, operation, exc)
                _write_json(args.receipt, receipt)
                print(json.dumps(receipt, sort_keys=True), file=sys.stderr)
                return 2
            _write_json(args.output, result)
            _write_json(args.receipt, receipt)
            print(json.dumps(receipt, sort_keys=True))
    except (
        ContextViewError,
        OSError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Strict, idempotent offline task-submission adapter."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from house.auto_switcher.policy import CASE_TYPE_PROFILE, select_manual_route

from .core import TaskSpine, TaskSpineError

SUBMISSION_SCHEMA = "codex-house-task-submission/1"
RECEIPT_SCHEMA = "codex-house-task-submission-receipt/1"
_REQUIRED = {"schema", "idempotency_key", "requested_by", "title", "summary"}
_OPTIONAL = {"case_type", "manual_route_id"}


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _required_text(submission: dict[str, Any], field: str, maximum: int) -> str:
    value = submission.get(field)
    if not isinstance(value, str) or not value.strip():
        raise TaskSpineError(f"{field} must be non-empty text")
    value = value.strip()
    if len(value) > maximum:
        raise TaskSpineError(f"{field} exceeds {maximum} characters")
    return value


def _optional_text(submission: dict[str, Any], field: str, maximum: int) -> str:
    value = submission.get(field, "")
    if not isinstance(value, str):
        raise TaskSpineError(f"{field} must be text")
    value = value.strip()
    if len(value) > maximum:
        raise TaskSpineError(f"{field} exceeds {maximum} characters")
    return value


def prepare_submission(submission: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(submission, dict):
        raise TaskSpineError("task submission must be a JSON object")
    unknown = set(submission) - _REQUIRED - _OPTIONAL
    missing = _REQUIRED - set(submission)
    if unknown:
        raise TaskSpineError("unknown task-submission fields: " + ",".join(sorted(unknown)))
    if missing:
        raise TaskSpineError("missing task-submission fields: " + ",".join(sorted(missing)))
    if submission["schema"] != SUBMISSION_SCHEMA:
        raise TaskSpineError("invalid task-submission schema")
    normalized = {
        "schema": SUBMISSION_SCHEMA,
        "idempotency_key": _required_text(submission, "idempotency_key", 128),
        "requested_by": _required_text(submission, "requested_by", 256),
        "title": _required_text(submission, "title", 512),
        "summary": _required_text(submission, "summary", 100_000),
        "case_type": _optional_text(submission, "case_type", 128),
        "manual_route_id": _optional_text(submission, "manual_route_id", 256),
    }
    if normalized["case_type"] and normalized["case_type"] not in CASE_TYPE_PROFILE:
        raise TaskSpineError("unknown case_type")
    if normalized["manual_route_id"]:
        try:
            select_manual_route(normalized["manual_route_id"])
        except ValueError as exc:
            raise TaskSpineError(str(exc)) from exc
    binding_payload = {
        key: normalized[key]
        for key in ("requested_by", "title", "summary", "case_type", "manual_route_id")
    }
    binding_sha256 = _sha256(binding_payload)
    identity_sha256 = hashlib.sha256(
        f'{normalized["idempotency_key"]}:{binding_sha256}'.encode()
    ).hexdigest()
    return {
        **normalized,
        "binding_sha256": binding_sha256,
        "work_id": "work-" + identity_sha256[:20],
        "task_id": "task-" + identity_sha256[20:40],
    }


def submit_task(spine: TaskSpine, submission: dict[str, Any]) -> dict[str, Any]:
    prepared = prepare_submission(submission)
    events = spine.journal_events()
    for event in events:
        if event["kind"] != "task_submission.accepted":
            continue
        receipt = event["payload"]["receipt"]
        if receipt["idempotency_key"] != prepared["idempotency_key"]:
            continue
        if receipt["binding_sha256"] != prepared["binding_sha256"]:
            raise TaskSpineError("idempotency key is already bound to different content")
        return receipt

    work_events = {event["payload"]["work_id"]: event for event in events if event["kind"] == "work_item.created"}
    task_events = {event["payload"]["task_id"]: event for event in events if event["kind"] == "task_packet.created"}
    resumed = prepared["work_id"] in work_events or prepared["task_id"] in task_events
    work_event = work_events.get(prepared["work_id"])
    if work_event is not None and work_event["payload"]["title"] != prepared["title"]:
        raise TaskSpineError("derived work identity conflicts with journal content")
    if work_event is None:
        spine.create_work_item(prepared["work_id"], prepared["title"])
    task_event = task_events.get(prepared["task_id"])
    if task_event is not None:
        payload = task_event["payload"]
        existing_manual_route = (payload.get("manual_selection") or {}).get("selected", {}).get("id", "")
        if (
            payload["work_id"] != prepared["work_id"]
            or payload["summary"] != prepared["summary"]
            or existing_manual_route != prepared["manual_route_id"]
        ):
            raise TaskSpineError("derived task identity conflicts with journal content")
    else:
        task_event = spine.create_task_packet(
            prepared["task_id"], prepared["work_id"], prepared["summary"],
            case_type=prepared["case_type"], manual_route_id=prepared["manual_route_id"],
        )
    routing = task_event["payload"]["routing_receipt"]
    manual_selection = task_event["payload"].get("manual_selection")
    unsigned_receipt = {
        "schema": RECEIPT_SCHEMA,
        "state": "RESUMED_PARTIAL" if resumed else "CREATED",
        "idempotency_key": prepared["idempotency_key"],
        "binding_sha256": prepared["binding_sha256"],
        "requested_by": prepared["requested_by"],
        "requester_identity_state": "ASSERTED_UNVERIFIED",
        "work_id": prepared["work_id"],
        "task_id": prepared["task_id"],
        "case_type": routing["request"]["case_type"],
        "routing_decision_sha256": routing["decision_sha256"],
        "model_advisory": routing["model_advisory"],
        "manual_selection_sha256": None if manual_selection is None else manual_selection["decision_sha256"],
        "dispatch": "NOT_ATTEMPTED",
    }
    receipt = {**unsigned_receipt, "receipt_sha256": _sha256(unsigned_receipt)}
    spine.record_submission_receipt(receipt)
    return receipt

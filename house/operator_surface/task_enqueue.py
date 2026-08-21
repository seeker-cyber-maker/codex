"""Typed human-surface task enqueue gateway.

This module is the shared implementation a future dashboard and the terminal
CLI can use. It admits a request to the local producer inbox only; it neither
leases a controller nor starts an assigned worker.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from house.task_spine import TaskInbox, TaskInboxError
from house.task_spine.submission import SUBMISSION_SCHEMA

from .registry import RegistryError, builtin_registry

RECEIPT_SCHEMA = "codex-house-operator-task-enqueue-receipt/1"
TASK_COMMAND_ID = "codex.house.task.submit"


class OperatorTaskEnqueueError(ValueError):
    """Raised when an operator request cannot become one typed queued task."""


def _digest(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def enqueue_task(
    inbox_path: str | Path,
    *,
    enqueue_id: str,
    requested_by: str,
    title: str,
    summary: str,
    recipient: str = "triage",
    recipient_id: str = "",
    case_type: str = "",
) -> dict[str, Any]:
    """Validate an operator task and persist exactly one inbox record.

    `requested_by` remains asserted/unverified. The returned receipt says only
    that the request is queued; task-spine admission and worker dispatch are
    separate later transitions.
    """

    arguments = {"title": title, "summary": summary, "recipient": recipient}
    if recipient_id:
        arguments["recipient_id"] = recipient_id
    if case_type:
        arguments["case_type"] = case_type
    try:
        request = builtin_registry().prepare_request(
            TASK_COMMAND_ID, arguments=arguments
        )
    except RegistryError as exc:
        raise OperatorTaskEnqueueError(str(exc)) from exc

    normalized = request["arguments"]
    recipient_id = normalized.get("recipient_id", "")
    if normalized["recipient"] == "specific_model" and not recipient_id:
        raise OperatorTaskEnqueueError("specific_model requires recipient_id")
    if normalized["recipient"] != "specific_model" and recipient_id:
        raise OperatorTaskEnqueueError(
            "recipient_id is allowed only with recipient=specific_model"
        )
    submission = {
        "schema": SUBMISSION_SCHEMA,
        "idempotency_key": enqueue_id,
        "requested_by": requested_by,
        "title": normalized["title"],
        "summary": normalized["summary"],
        "requested_recipient": normalized["recipient"],
        "requested_recipient_id": recipient_id,
        "case_type": normalized.get("case_type", ""),
    }
    inbox = TaskInbox(inbox_path)
    try:
        entry = inbox.enqueue(enqueue_id, submission)
    except TaskInboxError as exc:
        raise OperatorTaskEnqueueError(str(exc)) from exc
    finally:
        inbox.close()
    unsigned = {
        "schema": RECEIPT_SCHEMA,
        "state": entry["state"],
        "enqueue_id": entry["enqueue_id"],
        "sequence": entry["sequence"],
        "submission_sha256": entry["submission_sha256"],
        "request_sha256": request["request_sha256"],
        "requested_recipient": submission["requested_recipient"],
        "requested_recipient_id": submission["requested_recipient_id"] or None,
        "requester_identity_state": "ASSERTED_UNVERIFIED",
        "controller": "NOT_ATTEMPTED",
        "dispatch": "NOT_ATTEMPTED",
    }
    return {**unsigned, "receipt_sha256": _digest(unsigned)}

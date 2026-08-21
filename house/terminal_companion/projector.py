"""Offline, fail-closed projector for exported Codex item notifications."""

from __future__ import annotations

import json
from typing import Any


class CompanionProjectionError(ValueError):
    """Raised when an input is not a bounded exported-notification fixture."""


MAX_NOTIFICATIONS = 10_000
MAX_CAPTURE_BYTES = 8 * 1024 * 1024
MAX_OUTPUT_CHARS = 1_000_000


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise CompanionProjectionError(f"{field} must be non-empty text")
    return value


def _optional_text(value: object, field: str, maximum: int) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or len(value) > maximum:
        raise CompanionProjectionError(f"{field} must be text of at most {maximum} characters")
    return value


def _optional_int(value: object, field: str) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise CompanionProjectionError(f"{field} must be an integer or null")
    return value


def project_notifications(notifications: list[object]) -> list[dict[str, Any]]:
    """Project completed command items; ignore unrelated typed notifications.

    Input must be already-exported JSON-RPC notification objects. No socket,
    process, rollout, or native Codex database is opened by this function.
    """
    if not isinstance(notifications, list):
        raise CompanionProjectionError("notifications must be a JSON array")
    if len(notifications) > MAX_NOTIFICATIONS:
        raise CompanionProjectionError(f"notification count exceeds {MAX_NOTIFICATIONS}")
    cards: list[dict[str, Any]] = []
    for index, notification in enumerate(notifications):
        if not isinstance(notification, dict):
            raise CompanionProjectionError(f"notification {index} must be an object")
        if notification.get("method") != "item/completed":
            continue
        params = notification.get("params")
        if not isinstance(params, dict) or not isinstance(params.get("item"), dict):
            raise CompanionProjectionError(f"notification {index} has no completed item")
        item = params["item"]
        if item.get("type") != "commandExecution":
            continue
        status = _text(item.get("status"), "command status")
        if status not in {"completed", "failed", "declined"}:
            raise CompanionProjectionError(f"unsupported completed command status: {status}")
        cards.append({
            "schema": "codex-house-terminal-command-card/1",
            "thread_id": _text(params.get("threadId"), "threadId"),
            "turn_id": _text(params.get("turnId"), "turnId"),
            "item_id": _text(item.get("id"), "command id"),
            "command": _text(item.get("command"), "command"),
            "cwd": _text(item.get("cwd"), "cwd"),
            "status": status,
            "exit_code": _optional_int(item.get("exitCode"), "exitCode"),
            "duration_ms": _optional_int(item.get("durationMs"), "durationMs"),
            "output": _optional_text(item.get("aggregatedOutput"), "aggregatedOutput", MAX_OUTPUT_CHARS),
            "source": "exported_app_server_notification",
            "redaction_state": "UPSTREAM_ASSERTED",
            "output_redaction_state": "NOT_ATTESTED",
            "content_trust": "DISPLAY_ONLY",
            "dispatch": "NOT_ATTEMPTED",
        })
    return cards


def project_jsonl(source: str) -> list[dict[str, Any]]:
    """Project an append-only exported JSONL capture without opening it live."""
    if not isinstance(source, str) or len(source.encode("utf-8")) > MAX_CAPTURE_BYTES:
        raise CompanionProjectionError(f"capture exceeds {MAX_CAPTURE_BYTES} bytes")
    notifications: list[object] = []
    for line_number, line in enumerate(source.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            notifications.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise CompanionProjectionError(f"invalid JSONL notification at line {line_number}") from exc
        if len(notifications) > MAX_NOTIFICATIONS:
            raise CompanionProjectionError(f"notification count exceeds {MAX_NOTIFICATIONS}")
    return project_notifications(notifications)

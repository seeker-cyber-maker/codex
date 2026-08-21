"""Offline, fail-closed projector for exported Codex item notifications."""

from __future__ import annotations

from typing import Any


class CompanionProjectionError(ValueError):
    """Raised when an input is not a bounded exported-notification fixture."""


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise CompanionProjectionError(f"{field} must be non-empty text")
    return value


def project_notifications(notifications: list[object]) -> list[dict[str, Any]]:
    """Project completed command items; ignore unrelated typed notifications.

    Input must be already-exported JSON-RPC notification objects. No socket,
    process, rollout, or native Codex database is opened by this function.
    """
    if not isinstance(notifications, list):
        raise CompanionProjectionError("notifications must be a JSON array")
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
        if status not in {"completed", "failed", "declined", "interrupted"}:
            raise CompanionProjectionError(f"unsupported completed command status: {status}")
        cards.append({
            "schema": "codex-house-terminal-command-card/1",
            "thread_id": _text(params.get("threadId"), "threadId"),
            "turn_id": _text(params.get("turnId"), "turnId"),
            "item_id": _text(item.get("id"), "command id"),
            "command": _text(item.get("command"), "command"),
            "cwd": _text(item.get("cwd"), "cwd"),
            "status": status,
            "exit_code": item.get("exitCode"),
            "duration_ms": item.get("durationMs"),
            "output": item.get("aggregatedOutput"),
            "source": "exported_app_server_notification",
            "dispatch": "NOT_ATTEMPTED",
        })
    return cards

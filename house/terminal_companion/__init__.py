"""Read-only projection of exported Codex command events for a terminal companion."""

from .projector import CompanionProjectionError, project_jsonl, project_notifications

__all__ = ["CompanionProjectionError", "project_jsonl", "project_notifications"]

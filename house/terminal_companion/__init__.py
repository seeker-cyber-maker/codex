"""Read-only projection of exported Codex command events for a terminal companion."""

from .display_batch import (
    build_display_batch,
    evaluate_compatibility,
    verify_display_chain,
)
from .projector import CompanionProjectionError, project_jsonl, project_notifications

__all__ = [
    "CompanionProjectionError",
    "build_display_batch",
    "evaluate_compatibility",
    "project_jsonl",
    "project_notifications",
    "verify_display_chain",
]

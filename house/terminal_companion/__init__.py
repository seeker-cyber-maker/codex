"""Read-only projection of exported Codex command events for a terminal companion."""

from .display_batch import (
    build_display_batch,
    evaluate_compatibility,
    verify_display_chain,
)
from .projector import CompanionProjectionError, project_jsonl, project_notifications
from .webview import (
    build_webview_registration_descriptor,
    render_display_chain_html,
)

__all__ = [
    "CompanionProjectionError",
    "build_display_batch",
    "build_webview_registration_descriptor",
    "evaluate_compatibility",
    "project_jsonl",
    "project_notifications",
    "render_display_chain_html",
    "verify_display_chain",
]

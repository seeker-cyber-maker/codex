"""Explicit one-shot viewer preparation for a frozen relay dashboard response."""

from __future__ import annotations

from house.terminal_companion import OneShotLoopbackViewer

from .dashboard_view import render_dashboard_html


def prepare_relay_dashboard_viewer(
    response: object,
    *,
    host: str = "127.0.0.1",
    port: int = 0,
    ttl_seconds: int = 30,
) -> OneShotLoopbackViewer:
    """Prepare, but do not start, a capability-bound one-shot relay viewer."""
    document = render_dashboard_html(response)
    return OneShotLoopbackViewer(
        document,
        host=host,
        port=port,
        ttl_seconds=ttl_seconds,
    )

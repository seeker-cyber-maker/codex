"""Deterministic, offline route selection for Dream House task packets."""

from .policy import DEFAULT_ROUTES, route_task

__all__ = ["DEFAULT_ROUTES", "route_task"]

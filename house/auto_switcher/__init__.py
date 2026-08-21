"""Deterministic, offline route selection for Dream House task packets."""

from .policy import DEFAULT_ROUTES, ROUTE_CATALOG, list_routes, route_task

__all__ = ["DEFAULT_ROUTES", "ROUTE_CATALOG", "list_routes", "route_task"]

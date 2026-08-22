"""Offline intake for approved local-specialist catalog exports."""

from .catalog import CatalogError, ingest_catalog

__all__ = ["CatalogError", "ingest_catalog"]

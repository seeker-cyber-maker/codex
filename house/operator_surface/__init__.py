"""Typed, display-only command inventory for Dream House operator surfaces."""

from .registry import (
    Command,
    CommandRegistry,
    Parameter,
    RegistryError,
    TargetRequirement,
    builtin_registry,
)

__all__ = [
    "Command",
    "CommandRegistry",
    "Parameter",
    "RegistryError",
    "TargetRequirement",
    "builtin_registry",
]

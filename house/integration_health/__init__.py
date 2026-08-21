"""Read-only, root-confined health checks for future Dream House integrations."""

from .contract import HealthContractError, evaluate_integration_health

__all__ = ["HealthContractError", "evaluate_integration_health"]

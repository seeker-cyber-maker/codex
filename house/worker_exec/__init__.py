"""Guarded, offline-preparable Codex CLI worker operations."""

from .cli_contract import CliContractError, validate_cli_contract
from .controller import WorkerControllerError, WorkerOperationController
from .fixture_gate import FixtureGateError, launch_fixture
from .operation import (
    WorkerExecError,
    execute_for_test,
    prepare_operation,
    verify_operation,
)
from .process_supervisor import (
    ProcessSupervisorError,
    supervise_fixture_process,
    supervise_process,
)

__all__ = [
    "CliContractError",
    "FixtureGateError",
    "ProcessSupervisorError",
    "WorkerControllerError",
    "WorkerExecError",
    "WorkerOperationController",
    "execute_for_test",
    "launch_fixture",
    "prepare_operation",
    "supervise_fixture_process",
    "supervise_process",
    "validate_cli_contract",
    "verify_operation",
]

"""Guarded, offline-preparable Codex CLI worker operations."""

from .cli_contract import CliContractError, validate_cli_contract
from .controller import WorkerControllerError, WorkerOperationController
from .fixture_gate import FixtureGateError, launch_fixture
from .mock_admission import (
    MockAdmissionError,
    prepare_mock_execution_authority,
    prepare_mock_runtime_profile,
    verify_mock_admission,
    verify_mock_runtime_profile,
)
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
from .runtime_profile import (
    RuntimeProfileError,
    runtime_profile_gap_receipt,
    verify_real_runtime_profile,
)

__all__ = [
    "CliContractError",
    "FixtureGateError",
    "MockAdmissionError",
    "ProcessSupervisorError",
    "RuntimeProfileError",
    "WorkerControllerError",
    "WorkerExecError",
    "WorkerOperationController",
    "execute_for_test",
    "launch_fixture",
    "prepare_mock_execution_authority",
    "prepare_mock_runtime_profile",
    "prepare_operation",
    "runtime_profile_gap_receipt",
    "supervise_fixture_process",
    "supervise_process",
    "validate_cli_contract",
    "verify_mock_admission",
    "verify_mock_runtime_profile",
    "verify_operation",
    "verify_real_runtime_profile",
]

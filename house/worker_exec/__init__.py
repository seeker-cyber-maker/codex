"""Guarded, offline-preparable Codex CLI worker operations."""

from .cli_contract import CliContractError, validate_cli_contract
from .context_grammar import (
    ContextGrammarError,
    compile_context_grammar_v1,
    verify_context_grammar_v1,
    verify_ruleset_v1,
    verify_safe_projection_v1,
)
from .controller import WorkerControllerError, WorkerOperationController
from .fixture_gate import FixtureGateError, launch_fixture
from .host_observer import (
    HostObserverError,
    observe_host_v1,
    verify_host_observation_v1,
)
from .mock_admission import (
    MockAdmissionError,
    prepare_mock_execution_authority,
    prepare_mock_runtime_profile,
    verify_mock_admission,
    verify_mock_runtime_profile,
)
from .mock_context_firewall import (
    MockContextFirewallError,
    mock_firewall_failure_is_sterile,
    prepare_mock_launch_binding_v1,
    project_mock_context_v1,
)
from .mock_vault import (
    MockVaultError,
    create_mock_vault_ref_v1,
    prepare_mock_audit_failure_incident_v1,
    prepare_mock_resolver_exposure_v1,
    prepare_mock_vault_frontend_profile_v1,
    prepare_mock_vault_lease_v1,
    verify_mock_vault_lease_v1,
    verify_mock_vault_ref_v1,
)
from .operation import (
    WorkerExecError,
    execute_for_test,
    prepare_operation,
    verify_operation,
)
from .operation_v2 import (
    OperationV2Error,
    assemble_operation_v2,
    assemble_route_selection_v1,
    verify_operation_v2,
    verify_route_selection_v1,
    verify_task_card_v2,
)
from .process_supervisor import (
    ProcessSupervisorError,
    supervise_fixture_process,
    supervise_process,
)
from .runtime_binding import RuntimeBindingError, verify_runtime_evidence_bindings
from .runtime_profile import (
    RuntimeProfileError,
    runtime_profile_gap_receipt,
    verify_real_runtime_profile,
)

__all__ = [
    "CliContractError",
    "ContextGrammarError",
    "FixtureGateError",
    "HostObserverError",
    "MockAdmissionError",
    "MockContextFirewallError",
    "MockVaultError",
    "OperationV2Error",
    "ProcessSupervisorError",
    "RuntimeBindingError",
    "RuntimeProfileError",
    "WorkerControllerError",
    "WorkerExecError",
    "WorkerOperationController",
    "assemble_operation_v2",
    "assemble_route_selection_v1",
    "compile_context_grammar_v1",
    "create_mock_vault_ref_v1",
    "execute_for_test",
    "launch_fixture",
    "mock_firewall_failure_is_sterile",
    "observe_host_v1",
    "prepare_mock_audit_failure_incident_v1",
    "prepare_mock_execution_authority",
    "prepare_mock_launch_binding_v1",
    "prepare_mock_resolver_exposure_v1",
    "prepare_mock_runtime_profile",
    "prepare_mock_vault_frontend_profile_v1",
    "prepare_mock_vault_lease_v1",
    "prepare_operation",
    "project_mock_context_v1",
    "runtime_profile_gap_receipt",
    "supervise_fixture_process",
    "supervise_process",
    "validate_cli_contract",
    "verify_context_grammar_v1",
    "verify_host_observation_v1",
    "verify_mock_admission",
    "verify_mock_runtime_profile",
    "verify_mock_vault_lease_v1",
    "verify_mock_vault_ref_v1",
    "verify_operation",
    "verify_operation_v2",
    "verify_real_runtime_profile",
    "verify_route_selection_v1",
    "verify_ruleset_v1",
    "verify_runtime_evidence_bindings",
    "verify_safe_projection_v1",
    "verify_task_card_v2",
]

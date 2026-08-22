"""Final, injected-fixture launch gate for a future worker command.

There is intentionally no real Codex runner in this module.  The caller must
provide a fixture runner explicitly; the resulting record is an observation and
is reconciled to BLOCKED so it cannot be mistaken for task completion.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from .cli_contract import validate_cli_contract
from .controller import WorkerControllerError, WorkerOperationController
from .operation import WorkerExecError, verify_operation


class FixtureGateError(RuntimeError):
    """Raised when the final fixture-only launch gate rejects an operation."""


FixtureRunner = Callable[[Sequence[str], int], object]


def _reserve_output(record: Mapping[str, object]) -> Path:
    try:
        scope = record["authority_scope"]
        output_root = Path(str(scope["write_root"])).resolve(strict=True)  # type: ignore[index]
        output_dir = Path(str(scope["write"][0]))  # type: ignore[index]
        output_path = Path(str(record["expected_artifacts"][0]))  # type: ignore[index]
    except (KeyError, IndexError, OSError, TypeError) as exc:
        raise FixtureGateError("operation has invalid output reservation") from exc
    if (
        not output_root.is_dir()
        or output_dir.parent != output_root
        or output_path.parent != output_dir
        or output_dir.is_symlink()
    ):
        raise FixtureGateError("operation output is outside its controlled root")
    try:
        os.mkdir(output_dir, mode=0o700)
    except FileExistsError as exc:
        raise FixtureGateError("operation output is already reserved") from exc
    if output_dir.is_symlink() or output_dir.resolve(strict=True).parent != output_root:
        raise FixtureGateError("operation output reservation changed after creation")
    return output_path


def launch_fixture(
    controller: WorkerOperationController,
    *,
    operation_id: str,
    holder: str,
    fencing_token: str,
    execute: bool,
    version_output: str,
    exec_help_output: str,
    runner: FixtureRunner | None = None,
) -> dict[str, Any]:
    """Run only an explicitly supplied fixture runner after final validation.

    ``execute=False`` has no side effects.  ``runner=None`` is always rejected
    even with explicit consent, preventing a default or environment-selected
    real Codex launch.
    """

    entry = controller.entry(operation_id)
    record = entry["record"]
    if not execute:
        return {
            "state": "PREPARED_NOT_EXECUTED",
            "dispatch": "NOT_ATTEMPTED",
            "operation_id": operation_id,
        }
    if runner is None:
        raise FixtureGateError("a fixture runner is required; real launch is blocked")
    try:
        verified = verify_operation(record)
        contract = validate_cli_contract(
            executable_sha256=str(record["input_hashes"]["codex_sha256"]),  # type: ignore[index]
            version_output=version_output,
            exec_help_output=exec_help_output,
        )
        claim = controller.claim_fixture_launch(
            operation_id, holder=holder, fencing_token=fencing_token
        )
    except (WorkerExecError, WorkerControllerError, ValueError) as exc:
        raise FixtureGateError(str(exc)) from exc
    try:
        output_path = _reserve_output(record)
    except FixtureGateError:
        controller.block_runtime(
            operation_id,
            holder=holder,
            fencing_token=fencing_token,
            reason="final output reservation failed; fixture runner was not invoked",
        )
        raise
    try:
        result = runner(record["argv"], int(record["resource_budget"][0]["hard_cap"]))  # type: ignore[index]
    except Exception as exc:
        controller.block_runtime(
            operation_id,
            holder=holder,
            fencing_token=fencing_token,
            reason="fixture runner raised; real dispatch remains blocked",
        )
        raise FixtureGateError("fixture runner failed; operation blocked") from exc
    blocked = controller.block_runtime(
        operation_id,
        holder=holder,
        fencing_token=fencing_token,
        reason="fixture observation recorded; no worker result admitted",
    )
    return {
        "state": "FIXTURE_RUN_OBSERVED",
        "dispatch": "FIXTURE_ONLY",
        "operation_id": operation_id,
        "record_sha256": verified["record_sha256"],
        "cli_contract_sha256": contract["contract_sha256"],
        "launch_claim": claim,
        "output_path": str(output_path),
        "runner_result": str(result),
        "reconciliation": blocked,
    }

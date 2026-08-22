"""Prepare and test a bounded Codex CLI operation without live dispatch.

This module deliberately has no production subprocess runner. `execute_for_test`
accepts an injected fake runner so the operation boundary can be verified before
any account-using runtime is admitted.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

OPERATION_SCHEMA = "codex-house-codex-exec-operation/1"
RECEIPT_SCHEMA = "codex-house-codex-exec-test-receipt/1"
_OPERATION_ID = re.compile(r"^[a-z][a-z0-9-]{2,63}$")
_MODEL_ID = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")


class WorkerExecError(ValueError):
    """Raised when a proposed worker operation violates its sealed boundary."""


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1_048_576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolve_directory(value: str | Path, field: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        raise WorkerExecError(f"{field} must be absolute")
    try:
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise WorkerExecError(f"{field} cannot be resolved") from exc
    if not resolved.is_dir():
        raise WorkerExecError(f"{field} must be a directory")
    return resolved


def _task_snapshot(task_card: Mapping[str, object]) -> dict[str, str | None]:
    required = ("schema", "task_id", "title", "summary", "requested_recipient")
    if set(required) - set(task_card):
        raise WorkerExecError("task card lacks required fields")
    if task_card["schema"] != "codex-house-task-card/1":
        raise WorkerExecError("invalid task card schema")
    snapshot: dict[str, str | None] = {}
    for field in required:
        value = task_card[field]
        if not isinstance(value, str) or not value.strip():
            raise WorkerExecError(f"task card {field} must be non-empty text")
        snapshot[field] = value.strip()
    raw_recipient_id = task_card.get("requested_recipient_id")
    if raw_recipient_id is not None and not isinstance(raw_recipient_id, str):
        raise WorkerExecError("task card requested_recipient_id must be text or null")
    snapshot["requested_recipient_id"] = (
        None if raw_recipient_id is None else raw_recipient_id.strip()
    )
    recipient = snapshot["requested_recipient"]
    recipient_id = snapshot["requested_recipient_id"]
    if recipient == "specific_model":
        if not recipient_id or not _MODEL_ID.fullmatch(recipient_id):
            raise WorkerExecError(
                "specific_model requires a safe explicit model identifier"
            )
    elif recipient_id:
        raise WorkerExecError("only specific_model may have requested_recipient_id")
    return snapshot


def _prompt(snapshot: Mapping[str, str | None]) -> str:
    return (
        f"Task {snapshot['task_id']}: {snapshot['title']}\n\n"
        f"{snapshot['summary']}\n\n"
        "Work within the declared read-only boundary. Return an evidence-backed "
        "result; do not claim task admission or change task state."
    )


def _argv(
    snapshot: Mapping[str, str | None],
    executable: Path,
    workspace: Path,
    output_path: Path,
) -> list[str]:
    argv = [
        str(executable),
        "exec",
        "-C",
        str(workspace),
        "--sandbox",
        "read-only",
        "--json",
        "--output-last-message",
        str(output_path),
    ]
    if snapshot["requested_recipient"] == "specific_model":
        argv.extend(["--model", str(snapshot["requested_recipient_id"])])
    argv.append(_prompt(snapshot))
    return argv


def prepare_operation(
    task_card: Mapping[str, object],
    *,
    operation_id: str,
    workspace: str | Path,
    output_root: str | Path,
    codex_path: str | Path,
    wall_seconds: int = 600,
) -> dict[str, Any]:
    """Create an immutable, no-dispatch operation record from one task card."""

    if not _OPERATION_ID.fullmatch(operation_id):
        raise WorkerExecError("invalid operation_id")
    if not 1 <= wall_seconds <= 3600:
        raise WorkerExecError("wall_seconds must be between 1 and 3600")
    snapshot = _task_snapshot(task_card)
    resolved_workspace = _resolve_directory(workspace, "workspace")
    resolved_output_root = _resolve_directory(output_root, "output_root")
    output_dir = resolved_output_root / operation_id
    if output_dir.exists() or output_dir.is_symlink():
        raise WorkerExecError("operation output directory is already reserved")
    output_path = output_dir / "last-message.txt"
    executable = Path(codex_path).expanduser()
    if (
        not executable.is_absolute()
        or not executable.is_file()
        or executable.is_symlink()
    ):
        raise WorkerExecError("codex_path must be an absolute regular executable")
    if not executable.stat().st_mode & 0o111:
        raise WorkerExecError("codex_path is not executable")
    prompt = _prompt(snapshot)
    argv = _argv(snapshot, executable, resolved_workspace, output_path)
    intent = f"Run read-only Codex observation for {snapshot['task_id']}"
    input_hashes = {
        "task_card_sha256": _sha256(snapshot),
        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "codex_sha256": _file_sha256(executable),
        "argv_sha256": _sha256(argv),
    }
    binding = {
        "intent": intent,
        "task_card_sha256": input_hashes["task_card_sha256"],
        "argv_sha256": input_hashes["argv_sha256"],
        "workspace": str(resolved_workspace),
        "output_path": str(output_path),
        "wall_seconds": wall_seconds,
    }
    unsigned = {
        "schema": OPERATION_SCHEMA,
        "operation_id": operation_id,
        "record_revision": 1,
        "intent": intent,
        "target_identity": str(executable),
        "task_card": snapshot,
        "input_hashes": input_hashes,
        "argv": argv,
        "authority_scope": {
            "read": [str(resolved_workspace)],
            "write": [str(output_dir)],
            "write_root": str(resolved_output_root),
            "network": ["configured-codex-provider:UNKNOWN_UNVERIFIED"],
            "external_effect_class": "POTENTIAL_PROVIDER_EXECUTION",
        },
        "owner": "explicit-terminal-or-dashboard-operator",
        "lease": {
            "holder": None,
            "expires_at": None,
            "epoch": 0,
            "fencing_token": None,
        },
        "idempotency": {"key": operation_id, "binding_sha256": _sha256(binding)},
        "start_state": {
            "state": "PREPARED_NO_DISPATCH",
            "model_identity": "DEFAULT_UNRESOLVED"
            if snapshot["requested_recipient"] != "specific_model"
            else "EXPLICIT_REQUESTED",
        },
        "checkpoint_policy": {"retry_budget": 0, "automatic_resume": "PROHIBITED"},
        "resume_pointer": None,
        "deadline": None,
        "retry_budget": 0,
        "resource_budget": [
            {"resource": "wall_time", "unit": "seconds", "hard_cap": wall_seconds}
        ],
        "cancellation": {"supported": "DESIGN_REQUIRED", "method": "not admitted"},
        "expected_artifacts": [str(output_path), "stdout-jsonl:OBSERVATION_ONLY"],
        "acceptance_verifier": "separate worker-result admission path",
        "reconciliation": {
            "required": True,
            "method": "not admitted; live dispatch blocked",
        },
        "live_dispatch": "BLOCKED_PENDING_RUNTIME_QUALIFICATION",
    }
    return {**unsigned, "record_sha256": _sha256(unsigned)}


def verify_operation(record: Mapping[str, object]) -> dict[str, Any]:
    """Fail closed on record drift before a test runner is even considered."""

    if record.get("schema") != OPERATION_SCHEMA:
        raise WorkerExecError("invalid operation schema")
    supplied = record.get("record_sha256")
    unsigned = {key: value for key, value in record.items() if key != "record_sha256"}
    if not isinstance(supplied, str) or _sha256(unsigned) != supplied:
        raise WorkerExecError("operation record hash mismatch")
    snapshot = _task_snapshot(record.get("task_card", {}))
    workspace = _resolve_directory(
        str(record["authority_scope"]["read"][0]), "workspace"
    )  # type: ignore[index]
    output_path = Path(str(record["expected_artifacts"][0]))  # type: ignore[index]
    output_root = _resolve_directory(
        str(record["authority_scope"]["write_root"]), "output_root"
    )  # type: ignore[index]
    if output_path.parent != Path(record["authority_scope"]["write"][0]):  # type: ignore[index]
        raise WorkerExecError("output path does not match reserved operation directory")
    if output_path.parent.parent != output_root or output_path.parent.exists():
        raise WorkerExecError("output reservation is no longer available")
    executable = Path(str(record["target_identity"]))
    if (
        not executable.is_absolute()
        or not executable.is_file()
        or executable.is_symlink()
        or not executable.stat().st_mode & 0o111
    ):
        raise WorkerExecError("codex executable is no longer a regular executable")
    expected_argv = _argv(snapshot, executable, workspace, output_path)
    if (
        record.get("argv") != expected_argv
        or _sha256(expected_argv) != record["input_hashes"]["argv_sha256"]
    ):  # type: ignore[index]
        raise WorkerExecError("operation argv mismatch")
    if _file_sha256(executable) != record["input_hashes"]["codex_sha256"]:  # type: ignore[index]
        raise WorkerExecError("codex executable changed after preparation")
    return {
        "state": "VERIFIED_NO_DISPATCH",
        "operation_id": record["operation_id"],
        "record_sha256": supplied,
    }


def execute_for_test(
    record: Mapping[str, object],
    *,
    execute: bool = False,
    runner: Callable[..., object] | None = None,
) -> dict[str, Any]:
    """Exercise a sealed operation only through a supplied fake runner.

    Production dispatch is intentionally unavailable. This lets tests prove
    consent gating and argv containment without consuming a provider quota.
    """

    verified = verify_operation(record)
    if not execute:
        unsigned = {
            **verified,
            "schema": RECEIPT_SCHEMA,
            "state": "PREPARED_NOT_EXECUTED",
            "dispatch": "NOT_ATTEMPTED",
        }
        return {**unsigned, "receipt_sha256": _sha256(unsigned)}
    if runner is None:
        raise WorkerExecError("live runtime is blocked pending qualification")
    result = runner(record["argv"], timeout=record["resource_budget"][0]["hard_cap"])  # type: ignore[index]
    unsigned = {
        **verified,
        "schema": RECEIPT_SCHEMA,
        "state": "TEST_RUN_OBSERVED",
        "runner_result": str(result),
        "dispatch": "TEST_FAKE_RUNNER_ONLY",
    }
    return {**unsigned, "receipt_sha256": _sha256(unsigned)}

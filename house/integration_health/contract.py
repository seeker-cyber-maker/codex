"""Strict read-only integration-health contract evaluation.

The evaluator deliberately has no repair, process-launch, registration, or
network surface. A caller supplies trusted desired state; this module reports
whether a root-confined on-disk integration still matches it.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

HEALTH_CONTRACT_SCHEMA = "codex-house-integration-health-contract/1"
HEALTH_REPORT_SCHEMA = "codex-house-integration-health-report/1"
MAX_ARTIFACTS = 64
MAX_ARTIFACT_BYTES = 1_048_576
_HEX_DIGEST_LENGTH = 64
_CONTRACT_FIELDS = {"schema", "integration_id", "generation", "artifacts"}
_ARTIFACT_FIELDS = {
    "artifact_id",
    "path",
    "require_executable",
    "sha256",
    "json_expectations",
}


class HealthContractError(ValueError):
    """Raised when an asserted health contract is unsafe or malformed."""


def _require_text(value: object, field: str, maximum: int = 256) -> str:
    if not isinstance(value, str) or not value or len(value) > maximum:
        raise HealthContractError(f"{field} must be non-empty text up to {maximum} characters")
    return value


def _require_generation(value: object) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise HealthContractError("generation must be a positive integer")
    return value


def _require_relative_path(value: object) -> Path:
    path_text = _require_text(value, "artifact path", 512)
    path = Path(path_text)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise HealthContractError("artifact path must be a safe relative path")
    return path


def _require_sha256(value: object) -> str | None:
    if value is None:
        return None
    if (
        not isinstance(value, str)
        or len(value) != _HEX_DIGEST_LENGTH
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise HealthContractError("sha256 must be null or a lowercase SHA-256 digest")
    return value


def _json_pointer(value: object) -> list[str]:
    pointer = _require_text(value, "JSON pointer", 512)
    if not pointer.startswith("/"):
        raise HealthContractError("JSON pointer must start with '/'")
    return [part.replace("~1", "/").replace("~0", "~") for part in pointer[1:].split("/")]


def _scalar(value: object) -> str | int | float | bool | None:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise HealthContractError("JSON expectation values must be scalar")


def _validate_contract(contract: object) -> dict[str, Any]:
    if not isinstance(contract, Mapping) or set(contract) != _CONTRACT_FIELDS:
        raise HealthContractError("health contract schema drift")
    if contract.get("schema") != HEALTH_CONTRACT_SCHEMA:
        raise HealthContractError("unsupported health contract schema")
    integration_id = _require_text(contract.get("integration_id"), "integration_id")
    generation = _require_generation(contract.get("generation"))
    artifacts = contract.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts or len(artifacts) > MAX_ARTIFACTS:
        raise HealthContractError(f"artifacts must contain 1 to {MAX_ARTIFACTS} entries")

    seen_ids: set[str] = set()
    validated: list[dict[str, Any]] = []
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, Mapping) or set(artifact) != _ARTIFACT_FIELDS:
            raise HealthContractError(f"artifact {index} schema drift")
        artifact_id = _require_text(artifact.get("artifact_id"), "artifact_id")
        if artifact_id in seen_ids:
            raise HealthContractError(f"duplicate artifact_id: {artifact_id}")
        seen_ids.add(artifact_id)
        relative_path = _require_relative_path(artifact.get("path"))
        require_executable = artifact.get("require_executable")
        if not isinstance(require_executable, bool):
            raise HealthContractError("require_executable must be boolean")
        expectations = artifact.get("json_expectations")
        if not isinstance(expectations, Mapping):
            raise HealthContractError("json_expectations must be an object")
        checked_expectations: dict[str, str | int | float | bool | None] = {}
        for pointer, expected in expectations.items():
            parts = _json_pointer(pointer)
            if not parts or any(not part for part in parts):
                raise HealthContractError("JSON pointer must name a concrete value")
            checked_expectations[str(pointer)] = _scalar(expected)
        validated.append(
            {
                "artifact_id": artifact_id,
                "path": relative_path,
                "require_executable": require_executable,
                "sha256": _require_sha256(artifact.get("sha256")),
                "json_expectations": checked_expectations,
            }
        )
    return {
        "integration_id": integration_id,
        "generation": generation,
        "artifacts": validated,
    }


def _inside_root(root: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(root)
    except ValueError:
        return False
    return True


def _resolve_pointer(document: object, pointer: str) -> tuple[bool, object | None]:
    current = document
    for part in _json_pointer(pointer):
        if isinstance(current, Mapping):
            if part not in current:
                return False, None
            current = current[part]
        elif isinstance(current, list):
            if not part.isdecimal():
                return False, None
            index = int(part)
            if index >= len(current):
                return False, None
            current = current[index]
        else:
            return False, None
    return True, current


def _issue(artifact_id: str, code: str, path: Path) -> dict[str, str]:
    return {"artifact_id": artifact_id, "code": code, "path": str(path)}


def evaluate_integration_health(contract: object, root: str | Path) -> dict[str, Any]:
    """Inspect a trusted health contract without executing or changing anything.

    An invalid contract raises `HealthContractError`; an observed integration
    defect returns `REPAIR_REQUIRED` with stable issue codes.
    """

    expected = _validate_contract(contract)
    root_path = Path(root)
    if not root_path.is_dir():
        raise HealthContractError("root must be an existing directory")
    resolved_root = root_path.resolve(strict=True)
    issues: list[dict[str, str]] = []

    for artifact in expected["artifacts"]:
        artifact_path = root_path / artifact["path"]
        artifact_id = artifact["artifact_id"]
        if not _inside_root(root_path, artifact_path):  # Defensive; contract already validates.
            raise HealthContractError("artifact path escapes root")
        try:
            os.lstat(artifact_path)
        except FileNotFoundError:
            issues.append(_issue(artifact_id, "MISSING", artifact_path))
            continue
        if os.path.islink(artifact_path):
            try:
                resolved_path = artifact_path.resolve(strict=True)
            except FileNotFoundError:
                issues.append(_issue(artifact_id, "DANGLING_SYMLINK", artifact_path))
                continue
        else:
            resolved_path = artifact_path.resolve(strict=True)
        if not _inside_root(resolved_root, resolved_path):
            issues.append(_issue(artifact_id, "SYMLINK_ESCAPES_ROOT", artifact_path))
            continue
        if not resolved_path.is_file():
            issues.append(_issue(artifact_id, "NOT_REGULAR_FILE", artifact_path))
            continue
        if resolved_path.stat().st_size > MAX_ARTIFACT_BYTES:
            issues.append(_issue(artifact_id, "ARTIFACT_TOO_LARGE", artifact_path))
            continue
        if artifact["require_executable"] and not os.access(resolved_path, os.X_OK):
            issues.append(_issue(artifact_id, "EXECUTABLE_REQUIRED", artifact_path))
        try:
            data = resolved_path.read_bytes()
        except OSError:
            issues.append(_issue(artifact_id, "UNREADABLE", artifact_path))
            continue
        if artifact["sha256"] is not None and hashlib.sha256(data).hexdigest() != artifact["sha256"]:
            issues.append(_issue(artifact_id, "SHA256_MISMATCH", artifact_path))
        if artifact["json_expectations"]:
            try:
                document = json.loads(data.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                issues.append(_issue(artifact_id, "JSON_INVALID", artifact_path))
                continue
            for pointer, expected_value in artifact["json_expectations"].items():
                present, observed_value = _resolve_pointer(document, pointer)
                if not present:
                    issues.append(_issue(artifact_id, "JSON_EXPECTATION_MISSING", artifact_path))
                elif observed_value != expected_value:
                    issues.append(_issue(artifact_id, "JSON_EXPECTATION_MISMATCH", artifact_path))

    return {
        "schema": HEALTH_REPORT_SCHEMA,
        "integration_id": expected["integration_id"],
        "generation": expected["generation"],
        "state": "HEALTHY" if not issues else "REPAIR_REQUIRED",
        "repair_authority": "EXPLICIT_FUTURE_OPERATION_REQUIRED",
        "issues": issues,
    }

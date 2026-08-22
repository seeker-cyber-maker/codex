"""Version-pinned, no-provider CLI grammar checks for a future worker runner.

The contract is intentionally checked from captured ``--version`` and
``exec --help`` output.  The production launcher is not enabled here: callers
must supply an independently obtained probe, which keeps this module useful in
offline tests and makes a CLI drift visible before any task prompt is sent.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

CLI_CONTRACT_SCHEMA = "codex-house-cli-argument-contract/1"
PINNED_VERSION = "codex-cli 0.147.0"
REQUIRED_EXEC_FLAGS = (
    "-C, --cd <DIR>",
    "-m, --model <MODEL>",
    "-s, --sandbox <SANDBOX_MODE>",
    "--json",
    "-o, --output-last-message <FILE>",
)
FORBIDDEN_EXEC_FLAGS = ("--ask-for-approval",)


class CliContractError(ValueError):
    """Raised when a captured CLI grammar differs from the pinned contract."""


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical(value).encode()).hexdigest()


def validate_cli_contract(
    *,
    executable_sha256: str,
    version_output: str,
    exec_help_output: str,
) -> dict[str, Any]:
    """Validate a captured grammar without invoking Codex or a provider."""

    if not executable_sha256 or len(executable_sha256) != 64:
        raise CliContractError("executable_sha256 must be a SHA-256 digest")
    normalized_version = version_output.strip()
    if normalized_version != PINNED_VERSION:
        raise CliContractError("Codex version differs from the pinned contract")
    missing = [flag for flag in REQUIRED_EXEC_FLAGS if flag not in exec_help_output]
    if missing:
        raise CliContractError(f"required exec flags missing: {', '.join(missing)}")
    present = [flag for flag in FORBIDDEN_EXEC_FLAGS if flag in exec_help_output]
    if present:
        raise CliContractError(
            f"unadmitted exec flags appeared in grammar: {', '.join(present)}"
        )
    unsigned: Mapping[str, object] = {
        "schema": CLI_CONTRACT_SCHEMA,
        "executable_sha256": executable_sha256,
        "version": normalized_version,
        "required_exec_flags": list(REQUIRED_EXEC_FLAGS),
        "forbidden_exec_flags": list(FORBIDDEN_EXEC_FLAGS),
        "state": "VALIDATED_FROM_CAPTURE_NO_DISPATCH",
    }
    return {**unsigned, "contract_sha256": _sha256(unsigned)}

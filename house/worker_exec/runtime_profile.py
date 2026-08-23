"""Pure structural verification for a future real Codex runtime profile.

This module has no profile builder and no execution path.  A caller may supply
an independently produced qualification record, but successful verification
only proves its structure and binding to a sealed operation.  It grants no
authority and cannot create a lease, intent, process, provider call, or result.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from pathlib import PurePath
from typing import Any

from .operation import verify_operation

PROFILE_SCHEMA = "codex-house-qualified-real-runtime-profile/1"
PROFILE_RECEIPT_SCHEMA = "codex-house-runtime-profile-verification/1"
GAP_RECEIPT_SCHEMA = "codex-house-runtime-qualification-gap/1"
QUALIFICATION_POLICY = "codex-house-runtime-qualification-policy/1"

_PROFILE_ID = re.compile(r"^[a-z][a-z0-9-]{2,63}$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@+-]{0,255}$")
_RFC3339_UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_DISALLOWED_IDENTITIES = {
    "auto",
    "default",
    "fallback",
    "inherited",
    "none",
    "unknown",
    "unknown_unverified",
    "unverified",
    "wildcard",
}
_ENVIRONMENT_KEYS = frozenset({"CODEX_HOME", "HOME", "LANG", "PATH", "TMPDIR"})
_TOP_LEVEL_FIELDS = frozenset(
    {
        "schema",
        "profile_id",
        "mode",
        "qualification_policy",
        "operation_id",
        "record_sha256",
        "executable",
        "argv_sha256",
        "model_identity",
        "model_source",
        "workspace",
        "output",
        "environment",
        "runtime_roots",
        "config_hooks",
        "provider",
        "filesystem",
        "qualification_evidence",
        "profile_sha256",
    }
)


class RuntimeProfileError(ValueError):
    """Raised when a proposed real-runtime profile fails closed."""


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _mapping(value: object, field: str, fields: set[str]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != fields:
        raise RuntimeProfileError(f"{field} fields do not match the contract")
    return value


def _digest(value: object, field: str) -> str:
    if not isinstance(value, str) or not _DIGEST.fullmatch(value):
        raise RuntimeProfileError(f"{field} must be a SHA-256 digest")
    return value


def _qualified_identity(value: object, field: str) -> str:
    if not isinstance(value, str) or not _SAFE_ID.fullmatch(value):
        raise RuntimeProfileError(f"{field} must be an explicit safe identifier")
    normalized = value.casefold()
    identity_tokens = set(re.findall(r"[a-z0-9]+", normalized))
    if identity_tokens & _DISALLOWED_IDENTITIES or "*" in value:
        raise RuntimeProfileError(f"{field} cannot be implicit or unverified")
    return value


def _absolute_path(value: object, field: str) -> str:
    if not isinstance(value, str) or not value or not PurePath(value).is_absolute():
        raise RuntimeProfileError(f"{field} must be an absolute path")
    return value


def _bounded_bytes(value: object, field: str) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or not 1 <= value <= 8_388_608
    ):
        raise RuntimeProfileError(f"{field} must be between 1 and 8388608 bytes")
    return value


def _explicit_model_from_argv(argv: object) -> str:
    if not isinstance(argv, Sequence) or isinstance(argv, (str, bytes)):
        raise RuntimeProfileError("operation argv must be a sequence")
    values = [str(value) for value in argv]
    indexes = [
        index for index, value in enumerate(values) if value in {"--model", "-m"}
    ]
    if len(indexes) != 1 or indexes[0] + 1 >= len(values):
        raise RuntimeProfileError("operation argv must contain one explicit model")
    return _qualified_identity(values[indexes[0] + 1], "operation model")


def _gap_receipt(
    *, operation_id: object, record_sha256: object, gaps: Sequence[str]
) -> dict[str, Any]:
    unsigned: dict[str, Any] = {
        "schema": GAP_RECEIPT_SCHEMA,
        "operation_id": operation_id,
        "record_sha256": record_sha256,
        "state": "NOT_QUALIFIED",
        "dispatch": "NOT_ATTEMPTED",
        "authority": "NOT_GRANTED",
        "gaps": sorted(set(gaps)),
    }
    return {**unsigned, "receipt_sha256": _sha256(unsigned)}


def runtime_profile_gap_receipt(operation: Mapping[str, object]) -> dict[str, Any]:
    """Describe why an existing operation cannot enter real-runtime admission."""

    verified = verify_operation(operation)
    gaps = [
        "PROVIDER_ACCOUNT_IDENTITY_REQUIRED",
        "RUNTIME_QUALIFICATION_EVIDENCE_REQUIRED",
        "USAGE_POOL_IDENTITY_REQUIRED",
    ]
    try:
        explicit_model = _explicit_model_from_argv(operation.get("argv"))
    except RuntimeProfileError:
        gaps.append("EXPLICIT_MODEL_REQUIRED")
    else:
        if (
            operation.get("start_state", {}).get("model_identity")
            != "EXPLICIT_REQUESTED"
        ):  # type: ignore[union-attr]
            gaps.append("EXPLICIT_MODEL_REQUIRED")
        task_card = operation.get("task_card", {})
        if (
            not isinstance(task_card, Mapping)
            or task_card.get("requested_recipient_id") != explicit_model
        ):
            gaps.append("EXPLICIT_MODEL_REQUIRED")
    return _gap_receipt(
        operation_id=verified["operation_id"],
        record_sha256=verified["record_sha256"],
        gaps=gaps,
    )


def verify_real_runtime_profile(
    operation: Mapping[str, object], profile: Mapping[str, object]
) -> dict[str, Any]:
    """Verify a supplied profile contract without qualifying or executing it."""

    verified_operation = verify_operation(operation)
    if set(profile) != _TOP_LEVEL_FIELDS:
        raise RuntimeProfileError("runtime profile fields do not match the contract")
    unsigned = {key: value for key, value in profile.items() if key != "profile_sha256"}
    supplied_profile_sha256 = _digest(profile.get("profile_sha256"), "profile_sha256")
    if _sha256(unsigned) != supplied_profile_sha256:
        raise RuntimeProfileError("runtime profile hash mismatch")
    if profile.get("schema") != PROFILE_SCHEMA:
        raise RuntimeProfileError("invalid real-runtime profile schema")
    if profile.get("mode") != "QUALIFIED_REAL_RUNTIME_PROFILE":
        raise RuntimeProfileError("runtime profile mode is not qualified-real")
    if profile.get("qualification_policy") != QUALIFICATION_POLICY:
        raise RuntimeProfileError("runtime qualification policy differs")
    if not isinstance(profile.get("profile_id"), str) or not _PROFILE_ID.fullmatch(
        str(profile["profile_id"])
    ):
        raise RuntimeProfileError("invalid runtime profile identifier")
    if (
        profile.get("operation_id") != verified_operation["operation_id"]
        or profile.get("record_sha256") != verified_operation["record_sha256"]
    ):
        raise RuntimeProfileError("runtime profile operation binding mismatch")

    executable = _mapping(
        profile.get("executable"),
        "executable",
        {"path", "sha256", "version", "cli_contract_sha256", "cli_capture_sha256"},
    )
    if _absolute_path(executable["path"], "executable.path") != operation.get(
        "target_identity"
    ):
        raise RuntimeProfileError("runtime executable path differs from operation")
    if _digest(executable["sha256"], "executable.sha256") != operation.get(
        "input_hashes", {}
    ).get("codex_sha256"):  # type: ignore[union-attr]
        raise RuntimeProfileError("runtime executable digest differs from operation")
    if executable["version"] != "codex-cli 0.147.0":
        raise RuntimeProfileError("runtime executable version is not pinned")
    _digest(executable["cli_contract_sha256"], "executable.cli_contract_sha256")
    _digest(executable["cli_capture_sha256"], "executable.cli_capture_sha256")
    if _digest(profile.get("argv_sha256"), "argv_sha256") != operation.get(
        "input_hashes", {}
    ).get("argv_sha256"):  # type: ignore[union-attr]
        raise RuntimeProfileError("runtime argv digest differs from operation")

    model_identity = _qualified_identity(
        profile.get("model_identity"), "model_identity"
    )
    if profile.get("model_source") != "INDEPENDENT_RUNTIME_QUALIFICATION":
        raise RuntimeProfileError("runtime model source is not independently qualified")
    if _explicit_model_from_argv(operation.get("argv")) != model_identity:
        raise RuntimeProfileError("runtime model differs from sealed argv")

    workspace = _mapping(
        profile.get("workspace"), "workspace", {"path", "identity_sha256"}
    )
    if (
        _absolute_path(workspace["path"], "workspace.path")
        != operation.get("authority_scope", {}).get("read", [None])[0]
    ):  # type: ignore[union-attr,index]
        raise RuntimeProfileError("runtime workspace differs from operation")
    _digest(workspace["identity_sha256"], "workspace.identity_sha256")

    output = _mapping(
        profile.get("output"),
        "output",
        {
            "path",
            "reservation_evidence_sha256",
            "stdout_max_bytes",
            "stderr_max_bytes",
            "last_message_max_bytes",
            "total_max_bytes",
        },
    )
    if (
        _absolute_path(output["path"], "output.path")
        != operation.get("expected_artifacts", [None])[0]
    ):  # type: ignore[index]
        raise RuntimeProfileError("runtime output path differs from operation")
    _digest(output["reservation_evidence_sha256"], "output.reservation_evidence_sha256")
    component_limits = [
        _bounded_bytes(output[field], f"output.{field}")
        for field in ("stdout_max_bytes", "stderr_max_bytes", "last_message_max_bytes")
    ]
    total_limit = _bounded_bytes(output["total_max_bytes"], "output.total_max_bytes")
    if sum(component_limits) > total_limit:
        raise RuntimeProfileError("runtime component output limits exceed total limit")

    roots = _mapping(
        profile.get("runtime_roots"),
        "runtime_roots",
        {"home", "codex_home", "state", "temp", "content_inventory_sha256"},
    )
    for field in ("home", "codex_home", "state", "temp"):
        _absolute_path(roots[field], f"runtime_roots.{field}")
    if len({roots[field] for field in ("home", "codex_home", "state", "temp")}) != 4:
        raise RuntimeProfileError("runtime roots must be distinct")
    _digest(roots["content_inventory_sha256"], "runtime_roots.content_inventory_sha256")

    environment = _mapping(
        profile.get("environment"),
        "environment",
        {"policy", "values", "inventory_sha256"},
    )
    if environment["policy"] != "EXACT_ALLOWLIST":
        raise RuntimeProfileError("runtime environment policy is not exact")
    values = environment["values"]
    if not isinstance(values, Mapping) or set(values) != _ENVIRONMENT_KEYS:
        raise RuntimeProfileError("runtime environment keys do not match the allowlist")
    if any(
        not isinstance(value, str) or not value or "\x00" in value
        for value in values.values()
    ):
        raise RuntimeProfileError("runtime environment values must be non-empty text")
    if (
        values["HOME"] != roots["home"]
        or values["CODEX_HOME"] != roots["codex_home"]
        or values["TMPDIR"] != roots["temp"]
    ):
        raise RuntimeProfileError("runtime environment roots do not match the profile")
    if _digest(
        environment["inventory_sha256"], "environment.inventory_sha256"
    ) != _sha256(dict(values)):
        raise RuntimeProfileError("runtime environment inventory mismatch")

    config_hooks = _mapping(
        profile.get("config_hooks"),
        "config_hooks",
        {"state", "hook_state", "content_inventory_sha256", "evidence_sha256"},
    )
    if (
        config_hooks["state"] != "CONTENT_HASHED"
        or config_hooks["hook_state"] != "DISABLED_BY_POLICY"
    ):
        raise RuntimeProfileError("runtime config and hooks are not closed")
    _digest(
        config_hooks["content_inventory_sha256"],
        "config_hooks.content_inventory_sha256",
    )
    _digest(config_hooks["evidence_sha256"], "config_hooks.evidence_sha256")

    provider = _mapping(
        profile.get("provider"),
        "provider",
        {"identity", "account_id", "usage_pool_id", "egress"},
    )
    for field in ("identity", "account_id", "usage_pool_id"):
        _qualified_identity(provider[field], f"provider.{field}")
    if not isinstance(provider["egress"], list) or not provider["egress"]:
        raise RuntimeProfileError("runtime provider egress must be explicit")
    for index, value in enumerate(provider["egress"]):
        _qualified_identity(value, f"provider.egress[{index}]")

    filesystem = _mapping(
        profile.get("filesystem"),
        "filesystem",
        {"state", "policy_sha256", "trace_sha256", "read_roots", "write_roots"},
    )
    if filesystem["state"] != "MEASURED":
        raise RuntimeProfileError("runtime filesystem boundary is not measured")
    _digest(filesystem["policy_sha256"], "filesystem.policy_sha256")
    _digest(filesystem["trace_sha256"], "filesystem.trace_sha256")
    for field in ("read_roots", "write_roots"):
        roots_list = filesystem[field]
        if not isinstance(roots_list, list) or not roots_list:
            raise RuntimeProfileError(f"filesystem.{field} must be explicit")
        if len(roots_list) != len(set(roots_list)):
            raise RuntimeProfileError(f"filesystem.{field} contains duplicates")
        for index, value in enumerate(roots_list):
            _absolute_path(value, f"filesystem.{field}[{index}]")
    if workspace["path"] not in filesystem["read_roots"]:
        raise RuntimeProfileError("runtime workspace is missing from measured reads")
    expected_writes = {
        str(PurePath(output["path"]).parent),
        roots["home"],
        roots["codex_home"],
        roots["state"],
        roots["temp"],
    }
    if set(filesystem["write_roots"]) != expected_writes:
        raise RuntimeProfileError(
            "runtime measured write roots differ from the profile"
        )

    evidence = _mapping(
        profile.get("qualification_evidence"),
        "qualification_evidence",
        {
            "state",
            "issuer",
            "observed_at",
            "runtime_facts_sha256",
            "evidence_bundle_sha256",
        },
    )
    if evidence["state"] != "EXTERNALLY_VERIFIED_INPUT":
        raise RuntimeProfileError(
            "runtime qualification evidence is not externally verified"
        )
    _qualified_identity(evidence["issuer"], "qualification_evidence.issuer")
    if not isinstance(evidence["observed_at"], str) or not _RFC3339_UTC.fullmatch(
        evidence["observed_at"]
    ):
        raise RuntimeProfileError("runtime qualification observation time is invalid")
    runtime_facts = {
        key: profile[key]
        for key in unsigned
        if key
        not in {
            "schema",
            "profile_id",
            "mode",
            "qualification_policy",
            "qualification_evidence",
        }
    }
    if _digest(
        evidence["runtime_facts_sha256"], "qualification_evidence.runtime_facts_sha256"
    ) != _sha256(runtime_facts):
        raise RuntimeProfileError("runtime qualification facts changed after evidence")
    _digest(
        evidence["evidence_bundle_sha256"],
        "qualification_evidence.evidence_bundle_sha256",
    )

    receipt_unsigned: dict[str, Any] = {
        "schema": PROFILE_RECEIPT_SCHEMA,
        "profile_id": profile["profile_id"],
        "profile_sha256": supplied_profile_sha256,
        "operation_id": verified_operation["operation_id"],
        "record_sha256": verified_operation["record_sha256"],
        "state": "PROFILE_VERIFIED_NO_DISPATCH",
        "dispatch": "NOT_ATTEMPTED",
        "authority": "NOT_GRANTED",
        "claim_ceiling": "STRUCTURE_AND_BINDINGS_ONLY",
    }
    return {**receipt_unsigned, "receipt_sha256": _sha256(receipt_unsigned)}

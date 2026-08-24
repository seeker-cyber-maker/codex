"""Pure, untrusted binding of v2 operation records to supplied evidence."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from datetime import datetime
from pathlib import PurePosixPath
from typing import Any

from .operation_v2 import (
    verify_operation_v2,
    verify_route_selection_v1,
    verify_task_card_v2,
)

SCHEMA = "codex-house-runtime-evidence-observation/1"
RECEIPT_SCHEMA = "codex-house-runtime-evidence-binding-receipt/1"
STATE = "RUNTIME_EVIDENCE_BINDINGS_VERIFIED_NO_DISPATCH"
CEILING = "UNTRUSTED_INPUT_STRUCTURE_AND_CROSS_BINDINGS_ONLY"
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@+-]{0,255}$")
_RFC3339_UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")
_IMPLICIT_IDENTITIES = {
    "auto",
    "default",
    "fallback",
    "inherited",
    "unknown",
    "wildcard",
}
_COMMON_FIELDS = {
    "schema",
    "state",
    "task_card_sha256",
    "route_selection_sha256",
    "operation_sha256",
    "model_identity",
    "provider_identity",
    "route_account_fingerprint",
    "usage_pool_id",
    "argv_sha256",
    "descriptors_sha256",
    "workspace",
    "output",
    "isolation",
    "config_hooks",
    "runtime_roots",
    "filesystem",
    "evidence_bundle_sha256",
}
_ATTESTED_FIELDS = _COMMON_FIELDS | {
    "attestation_subject_id",
    "attestation_issuer_id",
    "self_issue_disposition",
    "trust_policy_id",
    "trust_policy_version",
    "trust_policy_sha256",
    "observer_key_id",
    "observer_key_policy_sha256",
    "reference_time_decision_sha256",
    "valid_from",
    "valid_until",
    "attestation_content_sha256",
    "self_issue_decision_sha256",
}


class RuntimeBindingError(ValueError):
    """Raised when supplied runtime evidence is malformed or mismatched."""


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _hash(value: object, label: str) -> str:
    if type(value) is not str or not _DIGEST.fullmatch(value):
        raise RuntimeBindingError(f"invalid {label}")
    return value


def _identity(value: object, label: str) -> str:
    if (
        type(value) is not str
        or not _IDENTITY.fullmatch(value)
        or value.casefold() in _IMPLICIT_IDENTITIES
        or "*" in value
    ):
        raise RuntimeBindingError(f"invalid {label}")
    return value


def _path(value: object, label: str) -> str:
    if type(value) is not str or not value.startswith("/") or "//" in value:
        raise RuntimeBindingError(f"invalid {label}")
    path = PurePosixPath(value)
    if str(path) != value or any(part in {".", ".."} for part in path.parts):
        raise RuntimeBindingError(f"invalid {label}")
    return value


def _exact(value: object, fields: set[str], label: str) -> dict[str, object]:
    if type(value) is not dict or set(value) != fields:
        raise RuntimeBindingError(f"{label} fields are not exact")
    return value


def _timestamp(value: object, label: str) -> datetime:
    if type(value) is not str or not _RFC3339_UTC.fullmatch(value):
        raise RuntimeBindingError(f"invalid {label}")
    try:
        return datetime.fromisoformat(f"{value[:-1]}+00:00")
    except ValueError as exc:
        raise RuntimeBindingError(f"invalid {label}") from exc


def _validate_common(
    observation: dict[str, object],
    route: Mapping[str, object],
    descriptors: Mapping[str, object],
    operation: Mapping[str, object],
    receipts: Mapping[str, Mapping[str, object]],
) -> None:
    for field, receipt_key in (
        ("task_card_sha256", "task"),
        ("route_selection_sha256", "route"),
        ("operation_sha256", "operation"),
    ):
        if observation[field] != receipts[receipt_key][field]:
            raise RuntimeBindingError(f"{field} mismatch")
    for field in ("model_identity", "provider_identity", "usage_pool_id"):
        if observation[field] != route[field]:
            raise RuntimeBindingError(f"{field} mismatch")
        _identity(observation[field], field)
    if observation["route_account_fingerprint"] != route["account_fingerprint"]:
        raise RuntimeBindingError("route_account_fingerprint mismatch")
    _hash(observation["route_account_fingerprint"], "route_account_fingerprint")
    if observation["argv_sha256"] != _digest(operation["argv"]):
        raise RuntimeBindingError("argv mismatch")
    if observation["descriptors_sha256"] != _digest(descriptors):
        raise RuntimeBindingError("descriptors mismatch")
    if (
        observation["evidence_bundle_sha256"]
        != route["observation"]["evidence_bundle_sha256"]
    ):  # type: ignore[index]
        raise RuntimeBindingError("evidence bundle mismatch")

    workspace = _exact(
        observation["workspace"], {"path", "identity_sha256"}, "workspace"
    )
    descriptor_workspace = descriptors["workspace"]  # type: ignore[index]
    if (
        workspace["path"] != descriptor_workspace["path"]
        or workspace["identity_sha256"] != descriptor_workspace["identity_sha256"]
    ):  # type: ignore[index]
        raise RuntimeBindingError("workspace mismatch")
    _path(workspace["path"], "workspace path")
    _hash(workspace["identity_sha256"], "workspace identity")

    output = _exact(observation["output"], {"path", "max_bytes"}, "output")
    output_intent = descriptors["output_intent"]  # type: ignore[index]
    if (
        output["path"] != output_intent["path"]
        or output["max_bytes"] != output_intent["max_bytes"]
    ):  # type: ignore[index]
        raise RuntimeBindingError("output mismatch")
    _path(output["path"], "output path")
    if type(output["max_bytes"]) is not int or output["max_bytes"] < 0:
        raise RuntimeBindingError("invalid output max bytes")

    isolation = _exact(
        observation["isolation"],
        {
            "sandbox",
            "allowed_context_surfaces",
            "allowed_tool_surfaces",
            "managed_policy",
        },
        "isolation",
    )
    expected_isolation = {
        key: value for key, value in descriptors["isolation"].items() if key != "schema"
    }  # type: ignore[union-attr,index]
    if isolation != expected_isolation:
        raise RuntimeBindingError("isolation mismatch")

    hooks = _exact(
        observation["config_hooks"],
        {"state", "hook_state", "evidence_sha256"},
        "config hooks",
    )
    if (
        hooks["state"] != "CONTENT_HASHED"
        or hooks["hook_state"] != "DISABLED_BY_POLICY"
    ):
        raise RuntimeBindingError("config hooks not closed")
    _hash(hooks["evidence_sha256"], "hook evidence")
    roots = _exact(
        observation["runtime_roots"],
        {"home", "codex_home", "state", "temp", "evidence_sha256"},
        "runtime roots",
    )
    root_paths = [
        _path(roots[field], field) for field in ("home", "codex_home", "state", "temp")
    ]
    if len(root_paths) != len(set(root_paths)):
        raise RuntimeBindingError("runtime roots not distinct")
    _hash(roots["evidence_sha256"], "roots evidence")
    filesystem = _exact(
        observation["filesystem"],
        {"state", "read_roots", "write_roots", "policy_sha256", "trace_sha256"},
        "filesystem",
    )
    read_roots, write_roots = filesystem["read_roots"], filesystem["write_roots"]
    if (
        filesystem["state"] != "MEASURED"
        or type(read_roots) is not list
        or type(write_roots) is not list
    ):
        raise RuntimeBindingError("filesystem invalid")
    all_roots = read_roots + write_roots
    for root in all_roots:
        _path(root, "filesystem root")
    if len(all_roots) != len(set(all_roots)):
        raise RuntimeBindingError("filesystem roots not unique")
    if workspace["path"] not in read_roots:
        raise RuntimeBindingError("workspace missing from filesystem")
    _hash(filesystem["policy_sha256"], "filesystem policy")
    _hash(filesystem["trace_sha256"], "filesystem trace")


def _validate_attestation(observation: dict[str, object]) -> None:
    for field in (
        "attestation_subject_id",
        "attestation_issuer_id",
        "trust_policy_id",
        "trust_policy_version",
        "observer_key_id",
    ):
        _identity(observation[field], field)
    if observation["self_issue_disposition"] not in {
        "SELF_ISSUED",
        "NOT_SELF_ISSUED",
        "UNDETERMINED",
    }:
        raise RuntimeBindingError("invalid self issue disposition")
    for field in (
        "trust_policy_sha256",
        "observer_key_policy_sha256",
        "reference_time_decision_sha256",
        "attestation_content_sha256",
        "self_issue_decision_sha256",
    ):
        _hash(observation[field], field)
    if _timestamp(observation["valid_from"], "valid_from") > _timestamp(
        observation["valid_until"], "valid_until"
    ):
        raise RuntimeBindingError("invalid attestation interval")
    content = {
        field: value
        for field, value in observation.items()
        if field not in {"attestation_content_sha256", "self_issue_decision_sha256"}
    }
    if observation["attestation_content_sha256"] != _digest(content):
        raise RuntimeBindingError("attestation content mismatch")
    decision = {
        field: observation[field]
        for field in (
            "attestation_subject_id",
            "attestation_issuer_id",
            "self_issue_disposition",
            "attestation_content_sha256",
        )
    }
    if observation["self_issue_decision_sha256"] != _digest(decision):
        raise RuntimeBindingError("self issue decision mismatch")


def verify_runtime_evidence_bindings(
    task_card: Mapping[str, object],
    route: Mapping[str, object],
    descriptors: Mapping[str, object],
    operation: Mapping[str, object],
    observation: Mapping[str, object],
) -> dict[str, Any]:
    """Verify exact supplied evidence cross-bindings without any host operation."""
    task_receipt = verify_task_card_v2(task_card)
    route_receipt = verify_route_selection_v1(task_card, route)
    operation_receipt = verify_operation_v2(task_card, route, descriptors, operation)
    state = observation.get("state") if type(observation) is dict else None
    fields = (
        _COMMON_FIELDS
        if state == "UNATTESTED_STRUCTURE_ONLY"
        else _ATTESTED_FIELDS
        if state == "ATTESTED_CLAIMED"
        else set()
    )
    supplied = _exact(observation, fields, "observation")
    if supplied["schema"] != SCHEMA:
        raise RuntimeBindingError("invalid observation schema")
    _validate_common(
        supplied,
        route,
        descriptors,
        operation,
        {"task": task_receipt, "route": route_receipt, "operation": operation_receipt},
    )
    if state == "ATTESTED_CLAIMED":
        _validate_attestation(supplied)
    unsigned = {
        "schema": RECEIPT_SCHEMA,
        "state": STATE,
        "claim_ceiling": CEILING,
        "dispatch": "NOT_ATTEMPTED",
        "authority": "NOT_GRANTED",
        "task_card_sha256": task_receipt["task_card_sha256"],
        "route_selection_sha256": route_receipt["route_selection_sha256"],
        "operation_sha256": operation_receipt["operation_sha256"],
        "observation_sha256": _digest(supplied),
    }
    return {**unsigned, "receipt_sha256": _digest(unsigned)}

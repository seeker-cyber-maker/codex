"""Pure structural records for the Dream House operation-v2 boundary.

This module deliberately performs no filesystem, clock, randomness, process,
network, credential, controller, or provider operation. Paths are opaque
lexical strings supplied by separately reviewed observers.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import PurePosixPath
from typing import Any

TASK_CARD_V2_SCHEMA = "codex-house-task-card/2"
TASK_CARD_V2_RECEIPT_SCHEMA = "codex-house-task-card-v2-verification/1"
ROUTE_SELECTION_SCHEMA = "codex-house-route-selection/1"
ROUTE_SELECTION_RECEIPT_SCHEMA = "codex-house-route-selection-verification/1"
OPERATION_V2_SCHEMA = "codex-house-codex-exec-operation/2"
OPERATION_V2_RECEIPT_SCHEMA = "codex-house-operation-v2-verification/1"

_HASH = re.compile(r"^[0-9a-f]{64}$")
_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")
_LOWER_ID = re.compile(r"^[a-z][a-z0-9-]{2,63}$")
_ROUTER_METHOD = re.compile(r"^deterministic-router/[A-Za-z0-9._-]{1,64}$")
_DISALLOWED_IDENTITIES = {
    "auto",
    "default",
    "fallback",
    "inherited",
    "unknown",
    "wildcard",
}
_COMMON_FLAGS = {
    "-C",
    "-c",
    "--ignore-rules",
    "--ignore-user-config",
    "--json",
    "--model",
    "--output-last-message",
    "--sandbox",
}


class OperationV2Error(ValueError):
    """Raised when a structural v2 record fails closed."""


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _frozen_copy(value: object) -> object:
    return json.loads(_canonical(value))


def _exact(mapping: object, fields: set[str], label: str) -> dict[str, object]:
    if type(mapping) is not dict or set(mapping) != fields:
        raise OperationV2Error(f"{label} fields are not exact")
    return mapping


def _text(value: object, label: str, *, maximum: int = 4096) -> str:
    if type(value) is not str or not value or value != value.strip():
        raise OperationV2Error(f"invalid {label}")
    if len(value.encode("utf-8")) > maximum or "\x00" in value:
        raise OperationV2Error(f"invalid {label}")
    return value


def _identity(value: object, label: str) -> str:
    identity = _text(value, label, maximum=128)
    if (
        not _SAFE_ID.fullmatch(identity)
        or identity.lower() in _DISALLOWED_IDENTITIES
        or "*" in identity
    ):
        raise OperationV2Error(f"invalid {label}")
    return identity


def _lower_id(value: object, label: str) -> str:
    identifier = _text(value, label, maximum=64)
    if not _LOWER_ID.fullmatch(identifier):
        raise OperationV2Error(f"invalid {label}")
    return identifier


def _hash(value: object, label: str) -> str:
    if type(value) is not str or not _HASH.fullmatch(value):
        raise OperationV2Error(f"invalid {label}")
    return value


def _identity_list(value: object, label: str) -> list[str]:
    if type(value) is not list or not value:
        raise OperationV2Error(f"{label} must be a non-empty list")
    result = [_identity(item, label) for item in value]
    if len(result) != len(set(result)):
        raise OperationV2Error(f"{label} contains duplicates")
    return result


def _surface_list(value: object, label: str) -> list[str]:
    if type(value) is not list:
        raise OperationV2Error(f"{label} must be a list")
    result = [_identity(item, label) for item in value]
    if len(result) != len(set(result)):
        raise OperationV2Error(f"{label} contains duplicates")
    return result


def _lexical_path(value: object, label: str) -> str:
    path = _text(value, label, maximum=4096)
    if not path.startswith("/") or path == "/" or "//" in path:
        raise OperationV2Error(f"{label} must be an absolute normalized lexical path")
    pure = PurePosixPath(path)
    if str(pure) != path or any(part in {".", ".."} for part in pure.parts):
        raise OperationV2Error(f"{label} must be an absolute normalized lexical path")
    return path


def _timestamp(value: object, label: str) -> datetime:
    text = _text(value, label, maximum=40)
    if not text.endswith("Z"):
        raise OperationV2Error(f"{label} must be RFC3339 UTC")
    try:
        parsed = datetime.fromisoformat(f"{text[:-1]}+00:00")
    except ValueError as exc:
        raise OperationV2Error(f"{label} must be RFC3339 UTC") from exc
    if parsed.tzinfo != timezone.utc:
        raise OperationV2Error(f"{label} must be RFC3339 UTC")
    return parsed


def _receipt(schema: str, state: str, binding: Mapping[str, object]) -> dict[str, Any]:
    unsigned = {
        "schema": schema,
        "state": state,
        "claim_ceiling": "STRUCTURE_AND_BINDINGS_ONLY",
        "dispatch": "NOT_ATTEMPTED",
        "authority": "NOT_GRANTED",
        **binding,
    }
    return {**unsigned, "receipt_sha256": _sha256(unsigned)}


def verify_task_card_v2(record: Mapping[str, object]) -> dict[str, Any]:
    """Verify one exact task-card-v2 record without interpreting legacy fields."""

    fields = {
        "schema",
        "task_id",
        "title",
        "summary",
        "routing_advice",
        "execution_constraints",
        "dispatch",
        "authority",
        "record_sha256",
    }
    card = _exact(record, fields, "task card v2")
    supplied = _hash(card["record_sha256"], "task card record hash")
    unsigned = {key: value for key, value in card.items() if key != "record_sha256"}
    if _sha256(unsigned) != supplied:
        raise OperationV2Error("task card record hash mismatch")
    if card["schema"] != TASK_CARD_V2_SCHEMA:
        raise OperationV2Error("invalid task card v2 schema")
    _lower_id(card["task_id"], "task id")
    _text(card["title"], "task title", maximum=512)
    _text(card["summary"], "task summary", maximum=16_384)
    advice = _exact(
        card["routing_advice"], {"class_hint", "model_preference"}, "routing advice"
    )
    class_hint = advice["class_hint"]
    if class_hint not in {None, "triage", "coder", "reviewer"}:
        raise OperationV2Error("invalid routing class hint")
    if advice["model_preference"] is not None:
        _identity(advice["model_preference"], "model preference")
    constraints = _exact(
        card["execution_constraints"],
        {
            "required_model",
            "allowed_models",
            "allowed_providers",
            "required_usage_pool",
        },
        "execution constraints",
    )
    allowed_models = _identity_list(constraints["allowed_models"], "allowed models")
    _identity_list(constraints["allowed_providers"], "allowed providers")
    required_model = constraints["required_model"]
    if required_model is not None:
        model = _identity(required_model, "required model")
        if model not in allowed_models:
            raise OperationV2Error("required model is not allowed")
    if constraints["required_usage_pool"] is not None:
        _identity(constraints["required_usage_pool"], "required usage pool")
    if card["dispatch"] != "NOT_ATTEMPTED" or card["authority"] != "NOT_GRANTED":
        raise OperationV2Error("task card v2 is not inert")
    return _receipt(
        TASK_CARD_V2_RECEIPT_SCHEMA,
        "TASK_CARD_V2_VERIFIED_NO_DISPATCH",
        {"task_card_sha256": supplied},
    )


def _validate_route(
    task_card: Mapping[str, object], route: Mapping[str, object]
) -> None:
    task_receipt = verify_task_card_v2(task_card)
    fields = {
        "schema",
        "selection_id",
        "task_card_sha256",
        "model_identity",
        "provider_identity",
        "account_fingerprint",
        "usage_pool_id",
        "routing_disposition",
        "observation",
        "provenance",
        "state",
        "dispatch",
        "authority",
        "record_sha256",
    }
    _exact(route, fields, "route selection")
    if route["schema"] != ROUTE_SELECTION_SCHEMA:
        raise OperationV2Error("invalid route-selection schema")
    _lower_id(route["selection_id"], "selection id")
    if route["task_card_sha256"] != task_receipt["task_card_sha256"]:
        raise OperationV2Error("route task-card binding mismatch")
    model = _identity(route["model_identity"], "route model")
    provider = _identity(route["provider_identity"], "route provider")
    _hash(route["account_fingerprint"], "account fingerprint")
    usage_pool = _identity(route["usage_pool_id"], "usage pool")
    constraints = task_card["execution_constraints"]
    if model not in constraints["allowed_models"]:  # type: ignore[operator]
        raise OperationV2Error("route model violates task constraints")
    if provider not in constraints["allowed_providers"]:  # type: ignore[operator]
        raise OperationV2Error("route provider violates task constraints")
    if constraints["required_model"] not in {None, model}:  # type: ignore[index]
        raise OperationV2Error("route model violates required model")
    if constraints["required_usage_pool"] not in {None, usage_pool}:  # type: ignore[index]
        raise OperationV2Error("route pool violates required pool")
    disposition = _exact(
        route["routing_disposition"],
        {"class_hint", "model_preference", "reason"},
        "routing disposition",
    )
    advice = task_card["routing_advice"]
    class_state = disposition["class_hint"]
    model_state = disposition["model_preference"]
    if advice["class_hint"] is None:  # type: ignore[index]
        if class_state != "NOT_APPLICABLE":
            raise OperationV2Error("class-hint disposition mismatch")
    elif class_state not in {"HONORED", "OVERRIDDEN_WITH_REASON"}:
        raise OperationV2Error("class-hint disposition mismatch")
    preference = advice["model_preference"]  # type: ignore[index]
    expected_model_state = (
        "NOT_APPLICABLE"
        if preference is None
        else "HONORED"
        if preference == model
        else "OVERRIDDEN_WITH_REASON"
    )
    if model_state != expected_model_state:
        raise OperationV2Error("model-preference disposition mismatch")
    overridden = "OVERRIDDEN_WITH_REASON" in {class_state, model_state}
    reason = disposition["reason"]
    if overridden:
        _text(reason, "routing override reason", maximum=1024)
    elif reason is not None:
        raise OperationV2Error("routing reason is only valid for an override")
    observation = _exact(
        route["observation"],
        {"observed_at", "not_after", "freshness_policy", "evidence_bundle_sha256"},
        "route observation",
    )
    if _timestamp(observation["observed_at"], "observed_at") >= _timestamp(
        observation["not_after"], "not_after"
    ):
        raise OperationV2Error("route observation interval is invalid")
    _identity(observation["freshness_policy"], "freshness policy")
    _hash(observation["evidence_bundle_sha256"], "evidence bundle hash")
    provenance = _exact(
        route["provenance"],
        {"author_id", "authoring_method", "signature_state"},
        "route provenance",
    )
    _identity(provenance["author_id"], "author id")
    method = _text(provenance["authoring_method"], "authoring method", maximum=96)
    if method != "human-manual" and not _ROUTER_METHOD.fullmatch(method):
        raise OperationV2Error("invalid authoring method")
    if provenance["signature_state"] != "NOT_VERIFIED_IN_FIRST_SLICE":
        raise OperationV2Error("route provenance overstates authentication")
    if (
        route["state"] != "STRUCTURE_BOUND_NO_DISPATCH"
        or route["dispatch"] != "NOT_ATTEMPTED"
        or route["authority"] != "NOT_GRANTED"
    ):
        raise OperationV2Error("route selection is not inert")


def assemble_route_selection_v1(
    task_card: Mapping[str, object],
    *,
    selection_id: str,
    model_identity: str,
    provider_identity: str,
    account_fingerprint: str,
    usage_pool_id: str,
    routing_disposition: Mapping[str, object],
    observation: Mapping[str, object],
    provenance: Mapping[str, object],
) -> dict[str, Any]:
    """Assemble a structure-bound route record without selecting or dispatching."""

    task_receipt = verify_task_card_v2(task_card)
    disposition = _exact(
        routing_disposition,
        {"class_hint", "model_preference", "reason"},
        "routing disposition",
    )
    observed = _exact(
        observation,
        {
            "observed_at",
            "not_after",
            "freshness_policy",
            "evidence_bundle_sha256",
        },
        "route observation",
    )
    attributed = _exact(
        provenance,
        {"author_id", "authoring_method", "signature_state"},
        "route provenance",
    )
    unsigned = {
        "schema": ROUTE_SELECTION_SCHEMA,
        "selection_id": selection_id,
        "task_card_sha256": task_receipt["task_card_sha256"],
        "model_identity": model_identity,
        "provider_identity": provider_identity,
        "account_fingerprint": account_fingerprint,
        "usage_pool_id": usage_pool_id,
        "routing_disposition": dict(disposition),
        "observation": dict(observed),
        "provenance": dict(attributed),
        "state": "STRUCTURE_BOUND_NO_DISPATCH",
        "dispatch": "NOT_ATTEMPTED",
        "authority": "NOT_GRANTED",
    }
    route = {**unsigned, "record_sha256": _sha256(unsigned)}
    _validate_route(task_card, route)
    return route


def verify_route_selection_v1(
    task_card: Mapping[str, object], route: Mapping[str, object]
) -> dict[str, Any]:
    """Verify route structure and bindings without claiming provenance or freshness now."""

    if type(route) is not dict:
        raise OperationV2Error("route selection fields are not exact")
    supplied = _hash(route.get("record_sha256"), "route record hash")
    unsigned = {key: value for key, value in route.items() if key != "record_sha256"}
    if _sha256(unsigned) != supplied:
        raise OperationV2Error("route-selection record hash mismatch")
    _validate_route(task_card, route)
    return _receipt(
        ROUTE_SELECTION_RECEIPT_SCHEMA,
        "ROUTE_SELECTION_VERIFIED_NO_DISPATCH",
        {
            "task_card_sha256": route["task_card_sha256"],
            "route_selection_sha256": supplied,
        },
    )


def _flags(value: object) -> list[str]:
    if type(value) is not list or not value:
        raise OperationV2Error("supported flags must be a non-empty list")
    flags = [_text(item, "supported flag", maximum=64) for item in value]
    if len(flags) != len(set(flags)) or not _COMMON_FLAGS.issubset(flags):
        raise OperationV2Error("supported flags are incomplete or duplicated")
    return flags


def _validate_descriptors(descriptors: Mapping[str, object]) -> None:
    _exact(
        descriptors,
        {
            "executable",
            "workspace",
            "output_intent",
            "prompt",
            "isolation",
            "resource",
            "reconciliation",
        },
        "operation descriptors",
    )
    executable = _exact(
        descriptors["executable"],
        {
            "schema",
            "path",
            "content_sha256",
            "version",
            "cli_contract_sha256",
            "supported_flags",
        },
        "executable descriptor",
    )
    if executable["schema"] != "codex-house-executable-descriptor/1":
        raise OperationV2Error("invalid executable descriptor schema")
    _lexical_path(executable["path"], "executable path")
    _hash(executable["content_sha256"], "executable content hash")
    _identity(executable["version"], "executable version")
    supported_flags = _flags(executable["supported_flags"])
    if executable["cli_contract_sha256"] != _sha256(
        {"supported_flags": supported_flags}
    ):
        raise OperationV2Error("CLI contract hash mismatch")
    workspace = _exact(
        descriptors["workspace"],
        {
            "schema",
            "path",
            "identity_sha256",
            "project_input_policy",
            "project_input_inventory_sha256",
        },
        "workspace descriptor",
    )
    if workspace["schema"] != "codex-house-workspace-descriptor/1":
        raise OperationV2Error("invalid workspace descriptor schema")
    _lexical_path(workspace["path"], "workspace path")
    _hash(workspace["identity_sha256"], "workspace identity hash")
    _hash(workspace["project_input_inventory_sha256"], "project inventory hash")
    policy = workspace["project_input_policy"]
    if policy not in {"PROJECT_CONFIG_IGNORED", "PROJECT_INPUTS_CONTENT_ADDRESSED"}:
        raise OperationV2Error("invalid project-input policy")
    if (
        policy == "PROJECT_CONFIG_IGNORED"
        and "--ignore-project-config" not in supported_flags
    ):
        raise OperationV2Error("CLI contract lacks project-config ignore support")
    output = _exact(
        descriptors["output_intent"],
        {"schema", "path", "reservation_policy_id", "max_bytes", "state"},
        "output intent descriptor",
    )
    if output["schema"] != "codex-house-output-intent/1":
        raise OperationV2Error("invalid output intent schema")
    _lexical_path(output["path"], "output intent path")
    _identity(output["reservation_policy_id"], "reservation policy")
    if (
        type(output["max_bytes"]) is not int
        or not 1 <= output["max_bytes"] <= 10_000_000
    ):
        raise OperationV2Error("invalid output byte ceiling")
    if output["state"] != "UNRESERVED_INTENT":
        raise OperationV2Error("output intent overstates reservation")
    prompt = _exact(
        descriptors["prompt"], {"schema", "text", "text_sha256"}, "prompt descriptor"
    )
    if prompt["schema"] != "codex-house-prompt-descriptor/1":
        raise OperationV2Error("invalid prompt descriptor schema")
    text = _text(prompt["text"], "prompt text", maximum=32_768)
    if prompt["text_sha256"] != _text_sha256(text):
        raise OperationV2Error("prompt text hash mismatch")
    isolation = _exact(
        descriptors["isolation"],
        {
            "schema",
            "sandbox",
            "allowed_context_surfaces",
            "allowed_tool_surfaces",
            "managed_policy",
        },
        "isolation policy",
    )
    if isolation["schema"] != "codex-house-isolation-policy/1":
        raise OperationV2Error("invalid isolation policy schema")
    if isolation["sandbox"] not in {"read-only", "workspace-write"}:
        raise OperationV2Error("invalid sealed sandbox")
    _surface_list(isolation["allowed_context_surfaces"], "allowed context surfaces")
    _surface_list(isolation["allowed_tool_surfaces"], "allowed tool surfaces")
    if isolation["managed_policy"] != "NARROW_ONLY":
        raise OperationV2Error("managed policy may only narrow")
    resource = _exact(
        descriptors["resource"],
        {"schema", "wall_seconds", "max_stdout_bytes", "max_stderr_bytes"},
        "resource policy",
    )
    if resource["schema"] != "codex-house-resource-policy/1":
        raise OperationV2Error("invalid resource policy schema")
    for field, maximum in (
        ("wall_seconds", 3600),
        ("max_stdout_bytes", 10_000_000),
        ("max_stderr_bytes", 10_000_000),
    ):
        if type(resource[field]) is not int or not 1 <= resource[field] <= maximum:
            raise OperationV2Error(f"invalid resource {field}")
    if output["max_bytes"] > resource["max_stdout_bytes"]:
        raise OperationV2Error("output ceiling exceeds stdout ceiling")
    reconciliation = _exact(
        descriptors["reconciliation"],
        {"schema", "idempotency_key", "retry_budget", "automatic_resume"},
        "reconciliation policy",
    )
    if reconciliation["schema"] != "codex-house-reconciliation-policy/1":
        raise OperationV2Error("invalid reconciliation policy schema")
    _lower_id(reconciliation["idempotency_key"], "idempotency key")
    if (
        reconciliation["retry_budget"] != 0
        or reconciliation["automatic_resume"] != "PROHIBITED"
    ):
        raise OperationV2Error("reconciliation policy is not first-slice inert")


def _operation_argv(
    route: Mapping[str, object], descriptors: Mapping[str, object]
) -> list[str]:
    executable = descriptors["executable"]
    workspace = descriptors["workspace"]
    output = descriptors["output_intent"]
    prompt = descriptors["prompt"]
    isolation = descriptors["isolation"]
    argv = [
        executable["path"],  # type: ignore[index]
        "exec",
        "-C",
        workspace["path"],  # type: ignore[index]
        "--model",
        route["model_identity"],
        "--sandbox",
        isolation["sandbox"],  # type: ignore[index]
        "--json",
        "--output-last-message",
        output["path"],  # type: ignore[index]
        "--ignore-user-config",
        "--ignore-rules",
        "-c",
        "features.hooks=false",
        "-c",
        "features.apps=false",
    ]
    if workspace["project_input_policy"] == "PROJECT_CONFIG_IGNORED":  # type: ignore[index]
        argv.append("--ignore-project-config")
    argv.append(prompt["text"])  # type: ignore[index]
    return argv  # type: ignore[return-value]


def assemble_operation_v2(
    task_card: Mapping[str, object],
    route_selection: Mapping[str, object],
    *,
    operation_id: str,
    descriptors: Mapping[str, object],
) -> dict[str, Any]:
    """Assemble a sealed operation entirely from caller-supplied mappings."""

    _lower_id(operation_id, "operation id")
    task_receipt = verify_task_card_v2(task_card)
    route_receipt = verify_route_selection_v1(task_card, route_selection)
    _validate_descriptors(descriptors)
    reconciliation = descriptors["reconciliation"]
    if reconciliation["idempotency_key"] != operation_id:  # type: ignore[index]
        raise OperationV2Error("operation idempotency binding mismatch")
    unsigned = {
        "schema": OPERATION_V2_SCHEMA,
        "operation_id": operation_id,
        "task_card_sha256": task_receipt["task_card_sha256"],
        "route_selection_sha256": route_receipt["route_selection_sha256"],
        "descriptors": _frozen_copy(descriptors),
        "argv": _operation_argv(route_selection, descriptors),
        "state": "ASSEMBLED_NO_OBSERVATION_NO_DISPATCH",
        "dispatch": "NOT_ATTEMPTED",
        "authority": "NOT_GRANTED",
    }
    return {**unsigned, "record_sha256": _sha256(unsigned)}


def verify_operation_v2(
    task_card: Mapping[str, object],
    route_selection: Mapping[str, object],
    descriptors: Mapping[str, object],
    operation: Mapping[str, object],
) -> dict[str, Any]:
    """Verify operation-v2 bytes and reconstruct every binding without host I/O."""

    fields = {
        "schema",
        "operation_id",
        "task_card_sha256",
        "route_selection_sha256",
        "descriptors",
        "argv",
        "state",
        "dispatch",
        "authority",
        "record_sha256",
    }
    _exact(operation, fields, "operation v2")
    supplied = _hash(operation["record_sha256"], "operation record hash")
    unsigned = {
        key: value for key, value in operation.items() if key != "record_sha256"
    }
    if _sha256(unsigned) != supplied:
        raise OperationV2Error("operation-v2 record hash mismatch")
    expected = assemble_operation_v2(
        task_card,
        route_selection,
        operation_id=operation["operation_id"],  # type: ignore[arg-type]
        descriptors=descriptors,
    )
    if operation != expected:
        raise OperationV2Error("operation-v2 binding mismatch")
    return _receipt(
        OPERATION_V2_RECEIPT_SCHEMA,
        "OPERATION_V2_VERIFIED_NO_DISPATCH",
        {
            "task_card_sha256": operation["task_card_sha256"],
            "route_selection_sha256": operation["route_selection_sha256"],
            "operation_sha256": supplied,
        },
    )

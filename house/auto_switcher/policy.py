"""Fail-closed deterministic model-route selection.

This module selects a *declared route*, not a provider request. Callers own
authentication, dispatch, and post-run verification. A route is eligible only
when its bridge is explicitly enabled and healthy in the supplied catalog.
"""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any

QUALITY = {"utility": 0, "good": 1, "strong": 2, "frontier": 3}
COST = {"local": 0, "free": 1, "subscription": 2, "paid": 3}

AUTO_ROUTES: tuple[dict[str, Any], ...] = (
    {
        "id": "chatgpt-codex-direct",
        "provider": "openai-chatgpt",
        "enabled": True,
        "healthy": True,
        "capabilities": ["code", "reasoning", "synthesis", "tool-use"],
        "privacy": "subscription-cloud",
        "quality": "strong",
        "cost": "subscription",
        "context_tokens": 128000,
        "delivery": "codex-direct",
        "roles": ["coding", "planning", "review", "research", "general"],
    },
    {
        "id": "chatgpt-work-packet",
        "provider": "chatgpt-app",
        "enabled": False,
        "healthy": False,
        "capabilities": ["code", "reasoning", "synthesis", "tool-use"],
        "privacy": "subscription-cloud",
        "quality": "strong",
        "cost": "subscription",
        "context_tokens": 24000,
        "delivery": "chat-packet",
        "roles": ["coding", "planning", "review", "research", "summary", "general"],
        "requires_bridge": "chatgpt-work-packet-v1",
    },
)

MANUAL_ONLY_ROUTES: tuple[dict[str, Any], ...] = (
    {
        "id": "daybreak-blue-personal",
        "provider": "openai-daybreak-blue",
        "display_name": "Daybreak Blue",
        "transport": "codex-native",
        "model_id": "gpt-daybreak-blue-latest",
        "native_status": "verified_bounded_control",
        "native_evidence_ref": (
            "provider-orchestration-codex-claude-3p/benchmarks/authorized-pentest/"
            "runs/20260821T195700Z-daybreak-meow-quanta-001/run-record.json"
        ),
        "api_sidecar_endpoint": "http://127.0.0.1:4022/v1",
        "api_sidecar_status": "configured_unverified",
        "selection_mode": "manual_only",
        "manual_selectable": True,
        "auto_eligible": False,
        "auto_exclusion_reason": "usage_pool_boundary_unknown",
    },
)

# Manual-only entries belong in the discoverable catalog so operator surfaces
# can display them, but route_task() rejects them before evaluating ordinary
# automatic-routing criteria. DEFAULT_ROUTES remains the compatibility name
# for callers that already provide or inspect the complete built-in catalog.
ROUTE_CATALOG = AUTO_ROUTES + MANUAL_ONLY_ROUTES
DEFAULT_ROUTES = ROUTE_CATALOG

KEYWORD_ROLES = (
    ("review", ("review", "audit", "verify", "critique")),
    ("planning", ("plan", "design", "architecture", "roadmap")),
    ("coding", ("implement", "debug", "code", "test", "refactor")),
    ("research", ("research", "investigate", "compare", "find")),
    ("summary", ("summarize", "summary", "digest", "classify")),
)

# Crosswalk from OMP role policy classes to the ChatGPT-family profile. These
# are classes, not vendor model IDs: the future app-server bridge resolves the
# permitted current model for the class and records that resolution separately.
OMP_PROFILE = {
    "summary": ("smol", "low", "cheapest_acceptable"),
    "classification": ("smol", "low", "cheapest_acceptable"),
    "research": ("task", "medium", "balanced"),
    "coding": ("task", "medium", "balanced"),
    "planning": ("plan", "high", "quality_first"),
    "review": ("plan", "high", "quality_first"),
    "general": ("default", "medium", "balanced"),
}

# These are visible, deterministic deployment advisories for the current
# ChatGPT/Codex family. They do not operate a client switch or dispatch a
# worker. Spark is a bounded leaf-worker alternative only; the task spine and
# its lead remain responsible for scope, authority, and acceptance.
MODEL_CLASS_ADVISORIES = {
    "smol": {
        "recommended_model": "gpt-5.6-luna",
        "eligible_leaf_worker": "gpt-5.3-codex-spark",
        "reason": "routine, bounded, low-consequence work",
        "reassess_trigger": "anomaly, mutation, or evidence conflict",
    },
    "task": {
        "recommended_model": "gpt-5.6-terra",
        "eligible_leaf_worker": None,
        "reason": "implementation or synthesis needs reliable multi-step work",
        "reassess_trigger": "architecture, security, or repeated verification failure",
    },
    "plan": {
        "recommended_model": "gpt-5.6-sol",
        "eligible_leaf_worker": None,
        "reason": "high-consequence planning, review, or exact verification",
        "reassess_trigger": "after the consequential gate completes",
    },
    "default": {
        "recommended_model": "gpt-5.6-terra",
        "eligible_leaf_worker": None,
        "reason": "ordinary mixed-scope work",
        "reassess_trigger": "case type becomes clear or scope changes",
    },
}

# Snapshot of the observed OMP control semantics.  A role selects a permitted
# model class; ``defaultThinkingLevel: auto`` is a separate provider thinking
# control.  This policy deliberately records both rather than conflating the
# status-line ``auto`` suffix with cross-model routing.
OMP_RUNTIME_BASELINE = {
    "thinking_level": "auto",
    "prewalk_enabled": False,
    "retry_fallback_enabled": True,
    "fallback_chain_configured": False,
    "context_promotion_enabled": False,
}
OMP_ROLE_SET = frozenset({"smol", "task", "plan", "default"})
OMP_THINKING_LEVELS = frozenset({"auto", "off", "low", "medium", "high", "xhigh"})

CASE_TYPE_PROFILE = {
    "command_debug": ("smol", "low", "cheapest_acceptable"),
    "dependency_repair": ("task", "medium", "balanced"),
    "research_synthesis": ("task", "medium", "balanced"),
    "publication": ("plan", "high", "quality_first"),
    "app_delivery": ("task", "medium", "balanced"),
    "systems_critical": ("plan", "xhigh", "quality_first"),
    "training_governance": ("plan", "high", "quality_first"),
    "hosted_app_ops": ("task", "medium", "balanced"),
    "model_conversion": ("task", "medium", "balanced"),
    "incident_recovery": ("plan", "high", "quality_first"),
    "verifier_benchmark": ("plan", "high", "quality_first"),
    "artifact_intake": ("task", "medium", "balanced"),
    "storage_lifecycle": ("task", "medium", "balanced"),
    "provider_bridge_debug": ("plan", "high", "quality_first"),
    "service_operations": ("smol", "low", "cheapest_acceptable"),
    "evidence_review": ("plan", "high", "quality_first"),
    "model_evaluation": ("task", "medium", "balanced"),
    "knowledge_integration": ("plan", "high", "quality_first"),
    "security_containment": ("plan", "xhigh", "quality_first"),
    "compound": ("plan", "high", "quality_first"),
}

CASE_TYPE_HINTS = (
    ("research_synthesis", ("research", "sources", "investigate")),
    ("publication", ("paper", "publish", "manuscript")),
    ("app_delivery", ("commercial app", "feature", "release")),
    ("training_governance", ("train a model", "training", "fine-tune")),
    ("model_conversion", ("convert model", "quantize", "conversion")),
    ("dependency_repair", ("dependency", "dependencies", "package conflict")),
    ("command_debug", ("faulty command", "command failed", "shell error")),
    ("incident_recovery", ("recover lost", "recover chat", "forensic", "lost logs", "db scrape")),
    ("verifier_benchmark", ("exact oracle", "reproduce result", "ablation", "verifier benchmark")),
    ("artifact_intake", ("inspect archive", "untrusted file", "inspect pickle", "inspect safetensors")),
    ("storage_lifecycle", ("migrate files", "disk migration", "deduplicate files", "junkyard")),
    ("provider_bridge_debug", ("provider bridge", "api route", "oauth route", "litellm")),
    ("service_operations", ("health check", "service status", "quota status", "babysit process")),
    ("evidence_review", ("claim review", "evidence gap", "review provenance", "contradictory evidence")),
    ("model_evaluation", ("model qualification", "router qualification", "evaluate local worker")),
    ("knowledge_integration", ("ingest archive", "knowledge dispensary", "reclassify sources", "merge research")),
    ("security_containment", ("prompt injection", "sql injection", "sandbox escape", "revoke key")),
)


def _canonical(value: Any, allowed: set[str], fallback: str) -> str:
    value = str(value or fallback).lower()
    return value if value in allowed else fallback


def infer_role(summary: str) -> tuple[str, str]:
    """Return a deterministic role and evidence string; never invoke a model."""
    text = summary.lower()
    for role, keywords in KEYWORD_ROLES:
        if any(keyword in text for keyword in keywords):
            return role, "keyword:" + role
    return "general", "fallback:general"


def infer_case_types(summary: str) -> list[str]:
    text = summary.lower()
    return [case_type for case_type, hints in CASE_TYPE_HINTS if any(hint in text for hint in hints)]


def _privacy_allowed(requested: str, actual: str) -> bool:
    allowed = {
        "local-only": {"local-only"},
        "subscription-cloud": {"local-only", "subscription-cloud"},
        "cloud-ok": {"local-only", "subscription-cloud", "third-party-cloud"},
    }
    return actual in allowed[requested]


def _receipt(payload: dict[str, Any]) -> dict[str, Any]:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return {**payload, "decision_sha256": hashlib.sha256(canonical).hexdigest()}


def list_routes() -> tuple[dict[str, Any], ...]:
    """Return a detached catalog suitable for a manual route picker."""
    return copy.deepcopy(ROUTE_CATALOG)


def select_manual_route(route_id: str) -> dict[str, Any]:
    """Resolve one explicit operator choice without dispatching or falling back."""
    route = next((item for item in ROUTE_CATALOG if item["id"] == route_id), None)
    if route is None:
        raise ValueError(f"unknown route: {route_id}")
    if not route.get("manual_selectable"):
        raise ValueError(f"route is not manually selectable: {route_id}")
    return _receipt(
        {
            "schema": "codex-house-manual-route/1",
            "state": "MANUAL_SELECTED",
            "selected": copy.deepcopy(route),
            "dispatch": "NOT_ATTEMPTED",
            "fallback": "PROHIBITED",
            "next_action": "SELECT_MODEL_IN_CODEX_UI",
        }
    )


def select_profile(role: str, risk: str, context_tokens: int, case_type: str = "") -> dict[str, str]:
    """Choose a ChatGPT-family class/effort from OMP-comparable criteria."""
    model_class, effort, policy = CASE_TYPE_PROFILE.get(
        case_type, OMP_PROFILE.get(role, OMP_PROFILE["general"])
    )
    if risk == "critical":
        model_class, effort, policy = "plan", "xhigh", "quality_first"
    elif risk == "high" and effort in {"low", "medium"}:
        model_class, effort, policy = "plan", "high", "quality_first"
    elif context_tokens > 24000 and model_class == "smol":
        model_class, effort, policy = "task", "medium", "balanced"
    return {"model_class": model_class, "reasoning_effort": effort, "omp_policy": policy}


def model_advisory(profile: dict[str, str]) -> dict[str, str | None]:
    """Map a profile class to a visible, no-dispatch current-family advisory."""
    advisory = MODEL_CLASS_ADVISORIES[profile["model_class"]]
    return {
        "mode": "ADVISORY_NO_SWITCH",
        "recommended_model": advisory["recommended_model"],
        "reasoning_effort": profile["reasoning_effort"],
        "eligible_leaf_worker": advisory["eligible_leaf_worker"],
        "reason": advisory["reason"],
        "reassess_trigger": advisory["reassess_trigger"],
    }


def omp_compatibility(task: dict[str, Any], profile: dict[str, str]) -> dict[str, str]:
    """Emit OMP-compatible controls without changing a live model session.

    The default is the currently observed OMP behavior: automatic thinking,
    no prewalk handoff, retry fallback enabled but no configured chain, and no
    context-overflow promotion.  A future qualified adapter may supply its
    observed ``omp_prewalk_enabled`` state; no task text can turn it on.
    """
    requested_role = profile["model_class"]
    if requested_role not in OMP_ROLE_SET:
        requested_role = "default"
    thinking_level = _canonical(
        task.get("omp_thinking_level"), set(OMP_THINKING_LEVELS), OMP_RUNTIME_BASELINE["thinking_level"]
    )
    prewalk_enabled = bool(task.get("omp_prewalk_enabled", OMP_RUNTIME_BASELINE["prewalk_enabled"]))
    plan_sealed = bool(task.get("plan_sealed", False))
    first_write_completed = bool(task.get("first_write_completed", False))
    effective_role = requested_role
    if not prewalk_enabled:
        prewalk_state = "DISABLED"
    elif not plan_sealed:
        prewalk_state = "ARMED_WAITING_FOR_PLAN"
    elif not first_write_completed:
        prewalk_state = "ARMED_WAITING_FOR_FIRST_WRITE"
    else:
        effective_role = "smol"
        prewalk_state = "HANDOFF_TO_SMOL_AFTER_FIRST_WRITE"
    return {
        "mode": "ADVISORY_NO_DISPATCH",
        "native_thinking_level": thinking_level,
        "effort_advisory": profile["reasoning_effort"],
        "requested_model_role": requested_role,
        "effective_model_role": effective_role,
        "prewalk": prewalk_state,
        "retry_fallback": "ENABLED_NO_CHAIN" if OMP_RUNTIME_BASELINE["retry_fallback_enabled"] else "DISABLED",
        "context_promotion": "DISABLED" if not OMP_RUNTIME_BASELINE["context_promotion_enabled"] else "ENABLED",
    }


def route_task(task: dict[str, Any], routes: tuple[dict[str, Any], ...] = DEFAULT_ROUTES) -> dict[str, Any]:
    """Select the cheapest eligible route, with deterministic safe fallback.

    Required task fields are intentionally small: ``summary`` is optional;
    callers may provide ``role``, ``capabilities``, ``privacy``,
    ``context_tokens``, ``min_quality``, and ``max_cost``. Explicit role always
    overrides keyword classification.
    """
    explicit_case_type = str(task.get("case_type", ""))
    detected_case_types = infer_case_types(str(task.get("summary", "")))
    explicit_role = task.get("role")
    if explicit_role:
        role, role_evidence = str(explicit_role).lower(), "explicit:role"
    elif not explicit_case_type and len(detected_case_types) > 1:
        role, role_evidence = "planning", "compound:" + ",".join(detected_case_types)
    else:
        role, role_evidence = infer_role(str(task.get("summary", "")))
    case_type = explicit_case_type or (detected_case_types[0] if len(detected_case_types) == 1 else "compound" if detected_case_types else "")
    requested = {
        "role": role,
        "capabilities": sorted(set(task.get("capabilities", []))),
        "privacy": _canonical(task.get("privacy"), {"local-only", "subscription-cloud", "cloud-ok"}, "subscription-cloud"),
        "context_tokens": int(task.get("context_tokens", 0)),
        "delivery": str(task.get("delivery", "codex-direct")),
        "risk": _canonical(task.get("risk"), {"low", "normal", "high", "critical"}, "normal"),
        "case_type": case_type,
        "min_quality": _canonical(task.get("min_quality"), set(QUALITY), "good"),
        "max_cost": _canonical(task.get("max_cost"), set(COST), "subscription"),
    }
    candidates: list[dict[str, Any]] = []
    rejected: dict[str, list[str]] = {}
    for route in routes:
        reasons: list[str] = []
        if route.get("selection_mode") == "manual_only" or not route.get("auto_eligible", True):
            reason = str(route.get("auto_exclusion_reason", "policy"))
            rejected[route["id"]] = ["manual_only:" + reason]
            continue
        if not route.get("enabled"): reasons.append("disabled")
        if not route.get("healthy"): reasons.append("unhealthy")
        if requested["role"] not in route.get("roles", []): reasons.append("role")
        if requested["delivery"] != route.get("delivery"): reasons.append("delivery")
        missing = set(requested["capabilities"]) - set(route.get("capabilities", []))
        if missing: reasons.append("capabilities:" + ",".join(sorted(missing)))
        if not _privacy_allowed(requested["privacy"], route.get("privacy", "")): reasons.append("privacy")
        if route.get("context_tokens", 0) < requested["context_tokens"]: reasons.append("context")
        if QUALITY.get(route.get("quality"), -1) < QUALITY[requested["min_quality"]]: reasons.append("quality")
        if COST.get(route.get("cost"), 99) > COST[requested["max_cost"]]: reasons.append("cost")
        if reasons: rejected[route["id"]] = reasons
        else: candidates.append(route)
    candidates.sort(key=lambda route: (COST[route["cost"]], -QUALITY[route["quality"]], route["id"]))
    selected = candidates[0] if candidates else next(route for route in routes if route["id"] == "chatgpt-codex-direct")
    state = "SELECTED" if candidates else "FALLBACK"
    profile = select_profile(
        requested["role"], requested["risk"], requested["context_tokens"], requested["case_type"]
    )
    advisory = model_advisory(profile)
    omp_compat = omp_compatibility(task, profile)
    return _receipt({
        "schema": "codex-house-auto-route/1",
        "state": state,
        "request": requested,
        "role_evidence": role_evidence,
        "detected_case_types": detected_case_types,
        "selected": {key: selected[key] for key in ("id", "provider", "quality", "cost", "privacy", "delivery")},
        "profile": profile,
        "model_advisory": advisory,
        "omp_compat": omp_compat,
        "rejected": rejected,
        "dispatch": "NOT_ATTEMPTED",
        "next_action": "DECOMPOSE_WITHOUT_BLOCKING" if case_type == "compound" else "CONTINUE",
    })

"""Fail-closed deterministic model-route selection.

This module selects a *declared route*, not a provider request. Callers own
authentication, dispatch, and post-run verification. A route is eligible only
when its bridge is explicitly enabled and healthy in the supplied catalog.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


QUALITY = {"utility": 0, "good": 1, "strong": 2, "frontier": 3}
COST = {"local": 0, "free": 1, "subscription": 2, "paid": 3}

DEFAULT_ROUTES: tuple[dict[str, Any], ...] = (
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
    return _receipt({
        "schema": "codex-house-auto-route/1",
        "state": state,
        "request": requested,
        "role_evidence": role_evidence,
        "detected_case_types": detected_case_types,
        "selected": {key: selected[key] for key in ("id", "provider", "quality", "cost", "privacy", "delivery")},
        "profile": profile,
        "rejected": rejected,
        "dispatch": "NOT_ATTEMPTED",
        "next_action": "DECOMPOSE_WITHOUT_BLOCKING" if case_type == "compound" else "CONTINUE",
    })

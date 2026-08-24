"""Pure synthetic verifier for the sealed sole-YubiKey recovery policy.

This module deliberately has no operational authority. It does not load or
generate keys, perform cryptography, persist state, read a clock, or contact
hardware. Signature and possession booleans are synthetic verifier inputs.
"""

from __future__ import annotations

import hashlib
import json
import re


CLAIM_CEILING = "SYNTHETIC_RECOVERY_POLICY_STRUCTURE_AND_TRANSITIONS_ONLY"
RESULT_SCHEMA = "codex-house-recovery-verification-result/1"
STATE_SCHEMA = "codex-house-recovery-state/1"
MANIFEST_SCHEMA = "codex-house-recovery-transition-manifest/1"
LOCKDOWN_SCHEMA = "codex-house-recovery-protective-lockdown-request/1"
EVIDENCE_SCHEMA = "codex-house-recovery-verification-evidence/1"

LOCKDOWN_ENTER = "authority.lockdown.enter"
SUSPEND_PRIMARY = "authority.key.suspend-primary"
RECOVER_PRIMARY = "authority.key.recover-primary"
CHECKPOINT_SIGN = "authority.checkpoint.admin.sign"
REVOKE_PRIMARY = "authority.key.revoke-primary"
LOCKDOWN_EXIT = "authority.lockdown.exit"

MAX_INTEGER = 9_223_372_036_854_775_807
IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

STATE_FIELDS = frozenset(
    {
        "schema",
        "registry_id",
        "generation",
        "mode",
        "ceremony_parent_sha256",
        "fencing_epoch",
        "journal_head_sha256",
        "checkpoint_sha256",
        "source_sha256",
        "policy_sha256",
        "protective_rule_sha256",
        "primary_key_id",
        "primary_epoch",
        "primary_status",
        "recovery_key_id",
        "recovery_epoch",
        "recovery_status",
        "replacement_key_id",
        "replacement_epoch",
        "replacement_status",
        "quarantine_sha256",
        "tombstone_sha256",
        "retired_primary_key_id",
        "retired_primary_epoch",
        "consumed_challenges",
    }
)
MANIFEST_FIELDS = frozenset(
    {
        "schema",
        "action",
        "registry_id",
        "generation",
        "ceremony_id",
        "ceremony_parent_sha256",
        "fencing_epoch",
        "signer_key_id",
        "signer_epoch",
        "old_primary_key_id",
        "old_primary_epoch",
        "expected_mode",
        "replacement_key_id",
        "replacement_epoch",
        "pending_intents_sha256",
        "source_sha256",
        "policy_sha256",
        "checkpoint_sha256",
        "new_checkpoint_sha256",
        "journal_head_sha256",
        "challenge_id",
        "issued_at",
        "expires_at",
        "default_state",
        "package_qualification_sha256",
        "recovery_copy_id",
        "tombstone_sha256",
    }
)
LOCKDOWN_FIELDS = frozenset(
    {
        "schema",
        "action",
        "registry_id",
        "generation",
        "fencing_epoch",
        "journal_head_sha256",
        "checkpoint_sha256",
        "source_sha256",
        "policy_sha256",
        "protective_rule_sha256",
        "reason",
        "default_state",
    }
)
EVIDENCE_FIELDS = frozenset(
    {
        "schema",
        "manifest_sha256",
        "signature_verified",
        "signer_key_id",
        "signer_epoch",
        "replacement_possession_verified",
        "replacement_key_id",
        "replacement_epoch",
    }
)

MODES = frozenset(
    {
        "ACTIVE",
        "LOCKDOWN",
        "PRIMARY_SUSPENDED",
        "REPLACEMENT_ENROLLED",
        "REPLACEMENT_READY",
        "OLD_PRIMARY_REVOKED",
    }
)


class RecoveryPolicyError(ValueError):
    """Typed refusal from the synthetic recovery-policy verifier."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def canonical(value: object) -> str:
    """Encode bounded JSON-compatible values in one deterministic form."""
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    except (TypeError, ValueError) as exc:
        raise RecoveryPolicyError("INVALID_JSON") from exc


def sha256_json(value: object) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def semantic_state_sha256(state: object) -> str:
    """Hash recovery semantics while excluding the cached receipt digest index."""
    prepared = _validate_state(state)
    semantic = dict(prepared)
    semantic["consumed_challenges"] = {
        challenge_id: {"manifest_sha256": record["manifest_sha256"]}
        for challenge_id, record in prepared["consumed_challenges"].items()
    }
    return sha256_json(semantic)


def verify_transition(
    state: object,
    request: object,
    evidence: object,
    decision_time: object,
) -> tuple[dict[str, object] | None, dict[str, object]]:
    """Apply one synthetic recovery request or return a fixed-ceiling refusal."""
    request_sha256 = _safe_sha256(request)
    prior_state_sha256 = _safe_state_sha256(state)
    try:
        prepared_state = _validate_state(state)
        _integer(decision_time, "decision_time")
        if isinstance(request, dict) and request.get("action") == LOCKDOWN_ENTER:
            return _verify_lockdown(
                prepared_state, request, evidence, request_sha256, prior_state_sha256
            )
        return _verify_manifest(
            prepared_state,
            request,
            evidence,
            decision_time,
            request_sha256,
            prior_state_sha256,
        )
    except RecoveryPolicyError as exc:
        return None, _result(
            result="REFUSED",
            code=exc.code,
            manifest_sha256=request_sha256,
            prior_state_sha256=prior_state_sha256,
            next_state_sha256=None,
            original_receipt_sha256=None,
        )


def _verify_lockdown(
    state: dict[str, object],
    request: object,
    evidence: object,
    request_sha256: str | None,
    prior_state_sha256: str | None,
) -> tuple[dict[str, object] | None, dict[str, object]]:
    if evidence is not None:
        raise RecoveryPolicyError("LOCKDOWN_EVIDENCE_FORBIDDEN")
    request = _closed_object(request, LOCKDOWN_FIELDS, "LOCKDOWN_SCHEMA")
    if request["schema"] != LOCKDOWN_SCHEMA or request["action"] != LOCKDOWN_ENTER:
        raise RecoveryPolicyError("LOCKDOWN_SCHEMA")
    _bind_state(request, state)
    if request["protective_rule_sha256"] != state["protective_rule_sha256"]:
        raise RecoveryPolicyError("WRONG_PROTECTIVE_RULE")
    _bounded_text(request["reason"], "reason", 1, 512)
    if request["default_state"] != "REMAIN_LOCKED":
        raise RecoveryPolicyError("WRONG_DEFAULT")
    if state["mode"] != "ACTIVE":
        raise RecoveryPolicyError("WRONG_STATE")
    next_state = dict(state)
    next_state["mode"] = "LOCKDOWN"
    next_state["fencing_epoch"] = state["fencing_epoch"] + 1
    next_state["journal_head_sha256"] = _next_head(state, request_sha256)
    return _accepted(state, next_state, request_sha256, prior_state_sha256, None)


def _verify_manifest(
    state: dict[str, object],
    request: object,
    evidence: object,
    decision_time: object,
    request_sha256: str | None,
    prior_state_sha256: str | None,
) -> tuple[dict[str, object] | None, dict[str, object]]:
    manifest = _closed_object(request, MANIFEST_FIELDS, "MANIFEST_SCHEMA")
    if manifest["schema"] != MANIFEST_SCHEMA:
        raise RecoveryPolicyError("MANIFEST_SCHEMA")
    action = manifest["action"]
    if action not in {
        SUSPEND_PRIMARY,
        RECOVER_PRIMARY,
        CHECKPOINT_SIGN,
        REVOKE_PRIMARY,
        LOCKDOWN_EXIT,
    }:
        raise RecoveryPolicyError("UNKNOWN_ACTION")
    _validate_manifest(manifest)
    challenge_id = manifest["challenge_id"]
    consumed = state["consumed_challenges"]
    previous = consumed.get(challenge_id)
    if previous is not None:
        if previous["manifest_sha256"] == request_sha256:
            return None, _result(
                result="REPLAY",
                code="ALREADY_CONSUMED",
                manifest_sha256=request_sha256,
                prior_state_sha256=prior_state_sha256,
                next_state_sha256=None,
                original_receipt_sha256=previous["receipt_sha256"],
            )
        raise RecoveryPolicyError("CHALLENGE_CONFLICT")
    _bind_state(manifest, state)
    if (
        manifest["old_primary_key_id"] != state["primary_key_id"]
        or manifest["old_primary_epoch"] != state["primary_epoch"]
    ):
        raise RecoveryPolicyError("STALE_PRIMARY")
    parent = state["ceremony_parent_sha256"]
    if parent is not None and manifest["ceremony_parent_sha256"] != parent:
        raise RecoveryPolicyError("STALE_CEREMONY")
    if manifest["expected_mode"] != state["mode"]:
        raise RecoveryPolicyError("STALE_MODE")
    if not manifest["issued_at"] <= decision_time < manifest["expires_at"]:
        raise RecoveryPolicyError("INVALID_TIME")
    prepared_evidence = _validate_evidence(evidence, request_sha256)
    next_state = _reduce(state, manifest, prepared_evidence)
    next_state["fencing_epoch"] = state["fencing_epoch"] + 1
    next_state["journal_head_sha256"] = _next_head(state, request_sha256)
    return _accepted(
        state,
        next_state,
        request_sha256,
        prior_state_sha256,
        challenge_id,
    )


def _reduce(
    state: dict[str, object],
    manifest: dict[str, object],
    evidence: dict[str, object],
) -> dict[str, object]:
    action = manifest["action"]
    next_state = dict(state)
    if action == SUSPEND_PRIMARY:
        _require_recovery_signer(state, manifest, evidence)
        if state["mode"] != "LOCKDOWN" or state["primary_status"] != "ACTIVE":
            raise RecoveryPolicyError("WRONG_STATE")
        next_state["mode"] = "PRIMARY_SUSPENDED"
        next_state["primary_status"] = "SUSPENDED"
        next_state["quarantine_sha256"] = manifest["pending_intents_sha256"]
        next_state["ceremony_parent_sha256"] = manifest["ceremony_parent_sha256"]
        return next_state
    if action == RECOVER_PRIMARY:
        _require_recovery_signer(state, manifest, evidence)
        if state["mode"] != "PRIMARY_SUSPENDED":
            raise RecoveryPolicyError("WRONG_STATE")
        _require_replacement(manifest, evidence)
        next_state["mode"] = "REPLACEMENT_ENROLLED"
        next_state["replacement_key_id"] = manifest["replacement_key_id"]
        next_state["replacement_epoch"] = manifest["replacement_epoch"]
        next_state["replacement_status"] = "ENROLLED"
        return next_state
    if action == CHECKPOINT_SIGN:
        _require_recovery_signer(state, manifest, evidence)
        if state["mode"] != "REPLACEMENT_ENROLLED":
            raise RecoveryPolicyError("WRONG_STATE")
        if manifest["new_checkpoint_sha256"] == state["checkpoint_sha256"]:
            raise RecoveryPolicyError("UNCHANGED_CHECKPOINT")
        next_state["mode"] = "REPLACEMENT_READY"
        next_state["replacement_status"] = "READY"
        next_state["checkpoint_sha256"] = manifest["new_checkpoint_sha256"]
        return next_state
    if action == REVOKE_PRIMARY:
        _require_recovery_signer(state, manifest, evidence)
        if state["mode"] != "REPLACEMENT_READY" or state["replacement_status"] != "READY":
            raise RecoveryPolicyError("WRONG_STATE")
        next_state["mode"] = "OLD_PRIMARY_REVOKED"
        next_state["primary_status"] = "REVOKED"
        next_state["tombstone_sha256"] = manifest["tombstone_sha256"]
        return next_state
    _require_replacement_signer(state, manifest, evidence)
    if state["mode"] != "OLD_PRIMARY_REVOKED" or state["replacement_status"] != "READY":
        raise RecoveryPolicyError("WRONG_STATE")
    next_state["mode"] = "ACTIVE"
    next_state["retired_primary_key_id"] = state["primary_key_id"]
    next_state["retired_primary_epoch"] = state["primary_epoch"]
    next_state["primary_key_id"] = state["replacement_key_id"]
    next_state["primary_epoch"] = state["replacement_epoch"]
    next_state["primary_status"] = "ACTIVE"
    next_state["replacement_status"] = "ACTIVE"
    next_state["ceremony_parent_sha256"] = None
    return next_state


def _accepted(
    state: dict[str, object],
    next_state: dict[str, object],
    manifest_sha256: str | None,
    prior_state_sha256: str | None,
    challenge_id: str | None,
) -> tuple[dict[str, object], dict[str, object]]:
    pending = dict(next_state)
    consumed = dict(state["consumed_challenges"])
    if challenge_id is not None:
        consumed[challenge_id] = {"manifest_sha256": manifest_sha256, "receipt_sha256": "0" * 64}
    pending["consumed_challenges"] = consumed
    next_state_sha256 = semantic_state_sha256(pending)
    receipt = _result(
        result="ACCEPTED",
        code="OK",
        manifest_sha256=manifest_sha256,
        prior_state_sha256=prior_state_sha256,
        next_state_sha256=next_state_sha256,
        original_receipt_sha256=None,
    )
    if challenge_id is not None:
        consumed[challenge_id] = {
            "manifest_sha256": manifest_sha256,
            "receipt_sha256": receipt["receipt_sha256"],
        }
    pending["consumed_challenges"] = consumed
    return _validate_state(pending), receipt


def _result(
    *,
    result: str,
    code: str,
    manifest_sha256: str | None,
    prior_state_sha256: str | None,
    next_state_sha256: str | None,
    original_receipt_sha256: str | None,
) -> dict[str, object]:
    unsigned = {
        "schema": RESULT_SCHEMA,
        "claim_ceiling": CLAIM_CEILING,
        "authority": "NOT_GRANTED",
        "dispatch": "NOT_ATTEMPTED",
        "hardware": "NOT_ACCESSED",
        "key_material": "NOT_ACCESSED",
        "runtime_admission": "NOT_ATTEMPTED",
        "result": result,
        "code": code,
        "manifest_sha256": manifest_sha256,
        "prior_state_sha256": prior_state_sha256,
        "next_state_sha256": next_state_sha256,
        "original_receipt_sha256": original_receipt_sha256,
    }
    return {**unsigned, "receipt_sha256": sha256_json(unsigned)}


def _validate_state(value: object) -> dict[str, object]:
    state = _closed_object(value, STATE_FIELDS, "STATE_SCHEMA")
    if state["schema"] != STATE_SCHEMA:
        raise RecoveryPolicyError("STATE_SCHEMA")
    _identifier(state["registry_id"], "registry_id")
    _integer(state["generation"], "generation")
    _integer(state["fencing_epoch"], "fencing_epoch")
    _nullable_sha256(state["ceremony_parent_sha256"], "ceremony_parent_sha256")
    if state["mode"] not in MODES:
        raise RecoveryPolicyError("STATE_MODE")
    for field in (
        "journal_head_sha256",
        "checkpoint_sha256",
        "source_sha256",
        "policy_sha256",
        "protective_rule_sha256",
        "quarantine_sha256",
    ):
        _sha256(state[field], field)
    _identifier(state["primary_key_id"], "primary_key_id")
    _integer(state["primary_epoch"], "primary_epoch")
    _identifier(state["recovery_key_id"], "recovery_key_id")
    _integer(state["recovery_epoch"], "recovery_epoch")
    if state["primary_status"] not in {"ACTIVE", "SUSPENDED", "REVOKED"}:
        raise RecoveryPolicyError("STATE_STATUS")
    if state["recovery_status"] != "ACTIVE":
        raise RecoveryPolicyError("STATE_STATUS")
    _nullable_identifier(state["replacement_key_id"], "replacement_key_id")
    _nullable_integer(state["replacement_epoch"], "replacement_epoch")
    if state["replacement_status"] not in {"NONE", "ENROLLED", "READY", "ACTIVE"}:
        raise RecoveryPolicyError("STATE_STATUS")
    _nullable_sha256(state["tombstone_sha256"], "tombstone_sha256")
    _nullable_identifier(state["retired_primary_key_id"], "retired_primary_key_id")
    _nullable_integer(state["retired_primary_epoch"], "retired_primary_epoch")
    if state["primary_key_id"] == state["recovery_key_id"]:
        raise RecoveryPolicyError("STATE_IDENTITY")
    if (state["replacement_key_id"] is None) != (state["replacement_epoch"] is None):
        raise RecoveryPolicyError("STATE_IDENTITY")
    if state["replacement_status"] == "NONE":
        if state["replacement_key_id"] is not None:
            raise RecoveryPolicyError("STATE_IDENTITY")
    elif (
        state["replacement_key_id"] is None
        or state["replacement_key_id"] == state["recovery_key_id"]
        or (
            state["replacement_key_id"] == state["primary_key_id"]
            and state["replacement_status"] != "ACTIVE"
        )
    ):
        raise RecoveryPolicyError("STATE_IDENTITY")
    if (state["retired_primary_key_id"] is None) != (state["retired_primary_epoch"] is None):
        raise RecoveryPolicyError("STATE_IDENTITY")
    _validate_mode(state)
    consumed = state["consumed_challenges"]
    if not isinstance(consumed, dict):
        raise RecoveryPolicyError("STATE_SCHEMA")
    prepared_consumed: dict[str, dict[str, str]] = {}
    for challenge_id, record in consumed.items():
        _identifier(challenge_id, "challenge_id")
        record = _closed_object(record, frozenset({"manifest_sha256", "receipt_sha256"}), "STATE_SCHEMA")
        _sha256(record["manifest_sha256"], "manifest_sha256")
        _sha256(record["receipt_sha256"], "receipt_sha256")
        prepared_consumed[challenge_id] = record
    state["consumed_challenges"] = prepared_consumed
    return state


def _validate_mode(state: dict[str, object]) -> None:
    mode = state["mode"]
    replacement = state["replacement_status"]
    primary = state["primary_status"]
    if mode == "ACTIVE" and primary == "ACTIVE" and replacement in {"NONE", "ACTIVE"}:
        if replacement == "ACTIVE" and state["primary_key_id"] != state["replacement_key_id"]:
            raise RecoveryPolicyError("STATE_IDENTITY")
        return
    if mode == "LOCKDOWN" and primary == "ACTIVE" and replacement == "NONE":
        return
    if mode == "PRIMARY_SUSPENDED" and primary == "SUSPENDED" and replacement == "NONE":
        return
    if mode == "REPLACEMENT_ENROLLED" and primary == "SUSPENDED" and replacement == "ENROLLED":
        return
    if mode == "REPLACEMENT_READY" and primary == "SUSPENDED" and replacement == "READY":
        return
    if mode == "OLD_PRIMARY_REVOKED" and primary == "REVOKED" and replacement == "READY":
        if state["tombstone_sha256"] is None:
            raise RecoveryPolicyError("STATE_MODE")
        return
    raise RecoveryPolicyError("STATE_MODE")


def _validate_manifest(manifest: dict[str, object]) -> None:
    for field in (
        "registry_id",
        "ceremony_id",
        "signer_key_id",
        "old_primary_key_id",
        "expected_mode",
        "challenge_id",
        "recovery_copy_id",
    ):
        _identifier(manifest[field], field)
    for field in ("generation", "fencing_epoch", "signer_epoch", "old_primary_epoch", "issued_at", "expires_at"):
        _integer(manifest[field], field)
    for field in (
        "ceremony_parent_sha256",
        "pending_intents_sha256",
        "source_sha256",
        "policy_sha256",
        "checkpoint_sha256",
        "journal_head_sha256",
        "package_qualification_sha256",
    ):
        _sha256(manifest[field], field)
    _nullable_identifier(manifest["replacement_key_id"], "replacement_key_id")
    _nullable_integer(manifest["replacement_epoch"], "replacement_epoch")
    _nullable_sha256(manifest["new_checkpoint_sha256"], "new_checkpoint_sha256")
    _nullable_sha256(manifest["tombstone_sha256"], "tombstone_sha256")
    if manifest["default_state"] != "REMAIN_LOCKED":
        raise RecoveryPolicyError("WRONG_DEFAULT")
    if manifest["expires_at"] <= manifest["issued_at"]:
        raise RecoveryPolicyError("INVALID_TIME")
    if manifest["expires_at"] - manifest["issued_at"] > 300:
        raise RecoveryPolicyError("INVALID_TIME")
    action = manifest["action"]
    if action == RECOVER_PRIMARY:
        if manifest["replacement_key_id"] is None or manifest["replacement_epoch"] is None:
            raise RecoveryPolicyError("REPLACEMENT_NOT_VERIFIED")
    elif action == LOCKDOWN_EXIT:
        if (
            manifest["replacement_key_id"] is None
            or manifest["replacement_epoch"] is None
            or manifest["new_checkpoint_sha256"] is not None
            or manifest["tombstone_sha256"] is not None
        ):
            raise RecoveryPolicyError("MANIFEST_SCHEMA")
    elif manifest["replacement_key_id"] is not None or manifest["replacement_epoch"] is not None:
        raise RecoveryPolicyError("MANIFEST_SCHEMA")
    if action == CHECKPOINT_SIGN:
        if manifest["new_checkpoint_sha256"] is None or manifest["tombstone_sha256"] is not None:
            raise RecoveryPolicyError("MANIFEST_SCHEMA")
    elif action == REVOKE_PRIMARY:
        if manifest["tombstone_sha256"] is None or manifest["new_checkpoint_sha256"] is not None:
            raise RecoveryPolicyError("MANIFEST_SCHEMA")
    elif manifest["new_checkpoint_sha256"] is not None or manifest["tombstone_sha256"] is not None:
        raise RecoveryPolicyError("MANIFEST_SCHEMA")


def _validate_evidence(value: object, manifest_sha256: str | None) -> dict[str, object]:
    evidence = _closed_object(value, EVIDENCE_FIELDS, "EVIDENCE_SCHEMA")
    if evidence["schema"] != EVIDENCE_SCHEMA or evidence["manifest_sha256"] != manifest_sha256:
        raise RecoveryPolicyError("EVIDENCE_BINDING")
    if not isinstance(evidence["signature_verified"], bool) or not isinstance(
        evidence["replacement_possession_verified"], bool
    ):
        raise RecoveryPolicyError("EVIDENCE_SCHEMA")
    _identifier(evidence["signer_key_id"], "signer_key_id")
    _integer(evidence["signer_epoch"], "signer_epoch")
    _nullable_identifier(evidence["replacement_key_id"], "replacement_key_id")
    _nullable_integer(evidence["replacement_epoch"], "replacement_epoch")
    return evidence


def _bind_state(request: dict[str, object], state: dict[str, object]) -> None:
    fields = (
        "registry_id",
        "generation",
        "fencing_epoch",
        "journal_head_sha256",
        "checkpoint_sha256",
        "source_sha256",
        "policy_sha256",
    )
    if any(request[field] != state[field] for field in fields):
        raise RecoveryPolicyError("STALE_BINDING")


def _require_recovery_signer(
    state: dict[str, object], manifest: dict[str, object], evidence: dict[str, object]
) -> None:
    if (
        not evidence["signature_verified"]
        or manifest["signer_key_id"] != state["recovery_key_id"]
        or manifest["signer_epoch"] != state["recovery_epoch"]
        or evidence["signer_key_id"] != state["recovery_key_id"]
        or evidence["signer_epoch"] != state["recovery_epoch"]
    ):
        raise RecoveryPolicyError("WRONG_SIGNER")
    if manifest["action"] != RECOVER_PRIMARY and (
        evidence["replacement_possession_verified"]
        or evidence["replacement_key_id"] is not None
        or evidence["replacement_epoch"] is not None
    ):
        raise RecoveryPolicyError("EVIDENCE_SCHEMA")


def _require_replacement(
    manifest: dict[str, object], evidence: dict[str, object]
) -> None:
    if (
        manifest["replacement_key_id"] is None
        or manifest["replacement_epoch"] is None
        or not evidence["replacement_possession_verified"]
        or evidence["replacement_key_id"] != manifest["replacement_key_id"]
        or evidence["replacement_epoch"] != manifest["replacement_epoch"]
    ):
        raise RecoveryPolicyError("REPLACEMENT_NOT_VERIFIED")


def _require_replacement_signer(
    state: dict[str, object], manifest: dict[str, object], evidence: dict[str, object]
) -> None:
    if (
        not evidence["signature_verified"]
        or manifest["signer_key_id"] != state["replacement_key_id"]
        or manifest["signer_epoch"] != state["replacement_epoch"]
        or evidence["signer_key_id"] != state["replacement_key_id"]
        or evidence["signer_epoch"] != state["replacement_epoch"]
        or manifest["replacement_key_id"] != state["replacement_key_id"]
        or manifest["replacement_epoch"] != state["replacement_epoch"]
    ):
        raise RecoveryPolicyError("WRONG_SIGNER")


def _next_head(state: dict[str, object], request_sha256: str | None) -> str:
    return sha256_json(
        {
            "schema": "codex-house-recovery-synthetic-event/1",
            "previous": state["journal_head_sha256"],
            "request_sha256": request_sha256,
        }
    )


def _closed_object(value: object, fields: frozenset[str], code: str) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != fields:
        raise RecoveryPolicyError(code)
    return json.loads(canonical(value))


def _identifier(value: object, field: str) -> None:
    if not isinstance(value, str) or not IDENTIFIER_RE.fullmatch(value):
        raise RecoveryPolicyError(f"INVALID_{field.upper()}")


def _bounded_text(value: object, field: str, minimum: int, maximum: int) -> None:
    if not isinstance(value, str) or not minimum <= len(value.strip()) <= maximum:
        raise RecoveryPolicyError(f"INVALID_{field.upper()}")


def _integer(value: object, field: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= MAX_INTEGER:
        raise RecoveryPolicyError(f"INVALID_{field.upper()}")


def _nullable_integer(value: object, field: str) -> None:
    if value is not None:
        _integer(value, field)


def _sha256(value: object, field: str) -> None:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise RecoveryPolicyError(f"INVALID_{field.upper()}")


def _nullable_sha256(value: object, field: str) -> None:
    if value is not None:
        _sha256(value, field)


def _nullable_identifier(value: object, field: str) -> None:
    if value is not None:
        _identifier(value, field)


def _safe_sha256(value: object) -> str | None:
    try:
        return sha256_json(value)
    except RecoveryPolicyError:
        return None


def _safe_state_sha256(value: object) -> str | None:
    try:
        return semantic_state_sha256(value)
    except RecoveryPolicyError:
        return None

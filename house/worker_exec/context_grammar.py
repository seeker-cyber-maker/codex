"""Synthetic-only context grammar records, compiler, and pure verifier.

This module intentionally has no host, process, environment, network, vault,
or clock integration.  It accepts only sealed inert records created by the
mock firewall or tests.  Real context projection remains a later authority
gate.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence

RULESET_SCHEMA = "codex-house-context-ruleset/1"
PROJECTION_SCHEMA = "codex-house-safe-context-projection/1"
GRAMMAR_SCHEMA = "codex-house-context-grammar/1"
RECEIPT_SCHEMA = "codex-house-context-grammar-verification/1"

CONFIG_PRECEDENCE = (
    "legacy_mdm",
    "legacy_managed_file",
    "session_flags",
    "project",
    "user_profile",
    "user",
    "enterprise_managed",
    "system",
)
PROJECTION_CLASSES = (
    "BEHAVIOR_VALUE",
    "PUBLIC_LOCATOR",
    "SECRET_REFERENCE",
    "SENSITIVE_PRESENCE_ONLY",
    "PUBLIC_CONTENT_ADDRESSABLE",
)
PROJECTION_TERMINAL_STATES = (
    "SAFE_PROJECTION_DERIVED",
    "INCOMPLETE_SECRET_DEPENDENCY",
    "INCOMPLETE_PRIVATE_TEXT",
    "INCOMPLETE_UNKNOWN_KEY",
)
_HASH = re.compile(r"^[0-9a-f]{64}$")
_ID = re.compile(r"^[A-Za-z][A-Za-z0-9._-]{0,127}$")
_LOCATOR = re.compile(r"^[A-Za-z][A-Za-z0-9._:/-]{0,255}$")
_REF = re.compile(r"^vr_[a-z0-9]{16,64}$")
_SECRETISH = re.compile(r"(?i)(?:secret|token|password|api[_-]?key|bearer|sk-)")


class ContextGrammarError(ValueError):
    """Raised when a synthetic context record fails closed."""


def canonical_json(value: object) -> str:
    """Return the stable JSON form used by all sealed records."""

    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def seal_record(unsigned: Mapping[str, object]) -> dict[str, object]:
    value = dict(unsigned)
    if "record_sha256" in value:
        raise ContextGrammarError("unsigned record already contains a hash")
    return {**value, "record_sha256": canonical_sha256(value)}


def _exact(value: object, fields: set[str], label: str) -> dict[str, object]:
    if type(value) is not dict or set(value) != fields:
        raise ContextGrammarError(f"{label} fields are not exact")
    return value


def _hash(value: object, label: str) -> str:
    if type(value) is not str or not _HASH.fullmatch(value):
        raise ContextGrammarError(f"invalid {label}")
    return value


def _identifier(value: object, label: str) -> str:
    if type(value) is not str or not _ID.fullmatch(value):
        raise ContextGrammarError(f"invalid {label}")
    return value


def _locator(value: object, label: str) -> str:
    if type(value) is not str or not _LOCATOR.fullmatch(value):
        raise ContextGrammarError(f"invalid {label}")
    return value


def _sealed(record: object, label: str) -> dict[str, object]:
    if type(record) is not dict:
        raise ContextGrammarError(f"invalid {label}")
    supplied = _hash(record.get("record_sha256"), f"{label} hash")
    unsigned = {key: value for key, value in record.items() if key != "record_sha256"}
    if canonical_sha256(unsigned) != supplied:
        raise ContextGrammarError(f"{label} hash mismatch")
    return record


def _string_list(
    value: object, label: str, allowed: Sequence[str] | None = None
) -> list[str]:
    if type(value) is not list or not value or len(value) != len(set(value)):
        raise ContextGrammarError(f"invalid {label}")
    if any(type(item) is not str for item in value):
        raise ContextGrammarError(f"invalid {label}")
    if allowed is not None and any(item not in allowed for item in value):
        raise ContextGrammarError(f"invalid {label}")
    return value


def _safe_value(value: object) -> object:
    if type(value) is str:
        if not value or len(value.encode("utf-8")) > 4096 or _SECRETISH.search(value):
            raise ContextGrammarError("unsafe behavior value")
        return value
    if type(value) in {bool, int}:
        return value
    if type(value) is list and value and all(type(item) is str for item in value):
        if any(not item or _SECRETISH.search(item) for item in value):
            raise ContextGrammarError("unsafe behavior value")
        return value
    raise ContextGrammarError("invalid behavior value")


def _vault_ref(value: object) -> dict[str, object]:
    result = _exact(
        value,
        {"ref_id", "scope_class", "required_sink", "revision"},
        "vault reference",
    )
    if type(result["ref_id"]) is not str or not _REF.fullmatch(result["ref_id"]):
        raise ContextGrammarError("invalid vault reference id")
    if result["scope_class"] not in {"global", "environment"}:
        raise ContextGrammarError("invalid vault scope class")
    if result["required_sink"] not in {
        "provider_header",
        "inherited_fd",
        "qualified_process_env",
    }:
        raise ContextGrammarError("invalid vault required sink")
    if type(result["revision"]) is not int or result["revision"] < 1:
        raise ContextGrammarError("invalid vault revision")
    return result


def verify_ruleset_v1(ruleset: object) -> dict[str, object]:
    value = _sealed(ruleset, "ruleset")
    _exact(
        value,
        {
            "schema",
            "ruleset_id",
            "source_revision",
            "platform_profile",
            "config_precedence",
            "required_contributor_classes",
            "allowed_projection_classes",
            "record_sha256",
        },
        "ruleset",
    )
    if value["schema"] != RULESET_SCHEMA:
        raise ContextGrammarError("invalid ruleset schema")
    _identifier(value["ruleset_id"], "ruleset id")
    _hash(value["source_revision"], "source revision")
    if value["platform_profile"] != "synthetic-posix-v1":
        raise ContextGrammarError("unsupported platform profile")
    if value["config_precedence"] != list(CONFIG_PRECEDENCE):
        raise ContextGrammarError("unexpected config precedence")
    _string_list(value["required_contributor_classes"], "required contributor classes")
    if value["allowed_projection_classes"] != list(PROJECTION_CLASSES):
        raise ContextGrammarError("unexpected projection classes")
    return value


def _verify_contributor(value: object) -> dict[str, object]:
    result = _exact(
        value,
        {
            "contributor_id",
            "contributor_class",
            "status",
            "classification",
            "locator_id",
            "content_sha256",
            "safe_value",
            "vault_ref",
        },
        "projection contributor",
    )
    _identifier(result["contributor_id"], "contributor id")
    _identifier(result["contributor_class"], "contributor class")
    if result["status"] not in {"PRESENT", "ABSENT", "DISABLED"}:
        raise ContextGrammarError("invalid contributor status")
    classification = result["classification"]
    if classification not in PROJECTION_CLASSES:
        raise ContextGrammarError("invalid contributor classification")
    _locator(result["locator_id"], "contributor locator")
    if classification == "BEHAVIOR_VALUE":
        if result["content_sha256"] is not None or result["vault_ref"] is not None:
            raise ContextGrammarError("behavior contributor contains forbidden data")
        _safe_value(result["safe_value"])
    elif classification == "PUBLIC_LOCATOR":
        if any(
            result[name] is not None
            for name in ("content_sha256", "safe_value", "vault_ref")
        ):
            raise ContextGrammarError("public locator contains forbidden data")
    elif classification == "PUBLIC_CONTENT_ADDRESSABLE":
        _hash(result["content_sha256"], "content hash")
        if result["safe_value"] is not None or result["vault_ref"] is not None:
            raise ContextGrammarError(
                "content-addressed contributor contains forbidden data"
            )
    elif classification == "SECRET_REFERENCE":
        if result["content_sha256"] is not None or result["safe_value"] is not None:
            raise ContextGrammarError("secret reference contains forbidden data")
        _vault_ref(result["vault_ref"])
    else:
        if any(
            result[name] is not None
            for name in ("content_sha256", "safe_value", "vault_ref")
        ):
            raise ContextGrammarError(
                "sensitive presence contributor contains forbidden data"
            )
    return result


def verify_safe_projection_v1(projection: object) -> dict[str, object]:
    value = _sealed(projection, "safe projection")
    _exact(
        value,
        {
            "schema",
            "projection_id",
            "operation_id",
            "ruleset_sha256",
            "parent_stage_sha256",
            "stage",
            "state",
            "contributors",
            "reason_codes",
            "record_sha256",
        },
        "safe projection",
    )
    if value["schema"] != PROJECTION_SCHEMA:
        raise ContextGrammarError("invalid safe projection schema")
    _identifier(value["projection_id"], "projection id")
    _identifier(value["operation_id"], "projection operation id")
    _hash(value["ruleset_sha256"], "projection ruleset hash")
    if value["parent_stage_sha256"] is not None:
        _hash(value["parent_stage_sha256"], "parent stage hash")
    if value["stage"] not in {"B", "D"}:
        raise ContextGrammarError("invalid projection stage")
    if value["state"] not in PROJECTION_TERMINAL_STATES:
        raise ContextGrammarError("invalid projection state")
    reasons = value["reason_codes"]
    if (
        type(reasons) is not list
        or len(reasons) != len(set(reasons))
        or any(type(item) is not str or not _ID.fullmatch(item) for item in reasons)
    ):
        raise ContextGrammarError("invalid projection reason codes")
    contributors = value["contributors"]
    if type(contributors) is not list:
        raise ContextGrammarError("invalid projection contributors")
    if value["state"] == "SAFE_PROJECTION_DERIVED":
        if not contributors or reasons:
            raise ContextGrammarError("safe projection closure mismatch")
        checked = [_verify_contributor(item) for item in contributors]
        ids = [item["contributor_id"] for item in checked]
        if len(ids) != len(set(ids)):
            raise ContextGrammarError("duplicate contributor id")
    elif contributors or not reasons:
        raise ContextGrammarError("incomplete projection exposes contributor material")
    return value


def compile_context_grammar_v1(
    ruleset: object, projection: object
) -> dict[str, object]:
    """Compile a non-executable grammar from a safe, sealed projection only."""

    ruleset_value = verify_ruleset_v1(ruleset)
    projection_value = verify_safe_projection_v1(projection)
    if projection_value["ruleset_sha256"] != ruleset_value["record_sha256"]:
        raise ContextGrammarError("projection ruleset binding mismatch")
    if projection_value["state"] != "SAFE_PROJECTION_DERIVED":
        raise ContextGrammarError("incomplete projection cannot compile a grammar")

    contributors = projection_value["contributors"]
    classes = [item["contributor_class"] for item in contributors]
    if classes != list(ruleset_value["required_contributor_classes"]):
        raise ContextGrammarError("projection contributor order or closure mismatch")
    return seal_record(
        {
            "schema": GRAMMAR_SCHEMA,
            "grammar_id": f"grammar-{projection_value['projection_id']}",
            "operation_id": projection_value["operation_id"],
            "ruleset_sha256": ruleset_value["record_sha256"],
            "projection_sha256": projection_value["record_sha256"],
            "parent_stage_sha256": projection_value["parent_stage_sha256"],
            "config_precedence": list(CONFIG_PRECEDENCE),
            "entries": contributors,
            "state": "GRAMMAR_DERIVED_NOT_OBSERVED",
            "authority": "NOT_GRANTED",
            "execution": "NOT_QUALIFIED",
        }
    )


def verify_context_grammar_v1(
    ruleset: object, projection: object, grammar: object
) -> dict[str, object]:
    """Purely verify compiler output without ambient I/O or runtime authority."""

    ruleset_value = verify_ruleset_v1(ruleset)
    projection_value = verify_safe_projection_v1(projection)
    value = _sealed(grammar, "context grammar")
    _exact(
        value,
        {
            "schema",
            "grammar_id",
            "operation_id",
            "ruleset_sha256",
            "projection_sha256",
            "parent_stage_sha256",
            "config_precedence",
            "entries",
            "state",
            "authority",
            "execution",
            "record_sha256",
        },
        "context grammar",
    )
    if value["schema"] != GRAMMAR_SCHEMA:
        raise ContextGrammarError("invalid context grammar schema")
    _identifier(value["grammar_id"], "grammar id")
    _identifier(value["operation_id"], "grammar operation id")
    if value["operation_id"] != projection_value["operation_id"]:
        raise ContextGrammarError("grammar operation binding mismatch")
    if value["ruleset_sha256"] != ruleset_value["record_sha256"]:
        raise ContextGrammarError("grammar ruleset binding mismatch")
    if value["projection_sha256"] != projection_value["record_sha256"]:
        raise ContextGrammarError("grammar projection binding mismatch")
    if value["parent_stage_sha256"] != projection_value["parent_stage_sha256"]:
        raise ContextGrammarError("grammar parent-stage binding mismatch")
    if value["config_precedence"] != list(CONFIG_PRECEDENCE):
        raise ContextGrammarError("grammar config precedence mismatch")
    if value["entries"] != projection_value["contributors"]:
        raise ContextGrammarError("grammar entries differ from projection")
    if value["state"] != "GRAMMAR_DERIVED_NOT_OBSERVED":
        raise ContextGrammarError("grammar state overclaims observation")
    if value["authority"] != "NOT_GRANTED" or value["execution"] != "NOT_QUALIFIED":
        raise ContextGrammarError("grammar contains execution authority")
    return seal_record(
        {
            "schema": RECEIPT_SCHEMA,
            "grammar_sha256": value["record_sha256"],
            "ruleset_sha256": ruleset_value["record_sha256"],
            "projection_sha256": projection_value["record_sha256"],
            "state": "CONTEXT_GRAMMAR_VERIFIED_NOT_QUALIFIED",
            "authenticity": "UNAUTHENTICATED_BY_PURE_VERIFIER",
            "authority": "NOT_GRANTED",
        }
    )

"""Static, validated composition of canonical task-spine task cards."""

from __future__ import annotations

import html
import re
from collections.abc import Mapping

MAX_TASK_CARDS = 32
MAX_TASK_TITLE_CHARS = 512
MAX_TASK_SUMMARY_CHARS = 4_096
MAX_TASK_INDEX_BYTES = 200_000
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_CARD_FIELDS = frozenset(
    {
        "schema",
        "task_id",
        "work_id",
        "title",
        "summary",
        "case_type",
        "profile",
        "model_advisory",
        "automatic_route_id",
        "routing_decision_sha256",
        "manual_route_id",
        "manual_selection_sha256",
        "requested_recipient",
        "requested_recipient_id",
        "wip_buffer_sha256",
        "candidate_envelope_id",
        "disposition",
        "dispatch",
    }
)
_PROFILE_FIELDS = frozenset({"model_class", "reasoning_effort", "omp_policy"})
_ADVISORY_FIELDS = frozenset(
    {
        "mode",
        "recommended_model",
        "reasoning_effort",
        "eligible_leaf_worker",
        "reason",
        "reassess_trigger",
    }
)
_RECIPIENTS = frozenset({"triage", "coder", "reviewer", "specific_model"})
_SOURCE_NOTES = {
    "NOT_SUPPLIED": "Source scope: NOT_SUPPLIED · no task-spine source was provided.",
    "READ_ONLY_NAMED_DATABASE": "Source scope: READ_ONLY_NAMED_DATABASE · explicit verified task-spine input.",
}


class TaskCardIndexError(ValueError):
    """Task cards cannot safely become a static operator index."""


def _text(value: object, label: str, maximum: int) -> str:
    if not isinstance(value, str) or not value or len(value) > maximum:
        raise TaskCardIndexError(f"invalid {label}")
    return value


def _optional_text(value: object, label: str, maximum: int) -> str | None:
    if value is None:
        return None
    return _text(value, label, maximum)


def _text_or_empty(value: object, label: str, maximum: int) -> str:
    if not isinstance(value, str) or len(value) > maximum:
        raise TaskCardIndexError(f"invalid {label}")
    return value


def _digest(value: object, label: str, *, optional: bool = False) -> str | None:
    if value is None and optional:
        return None
    if not isinstance(value, str) or not _DIGEST.fullmatch(value):
        raise TaskCardIndexError(f"invalid {label}")
    return value


def _validated_card(card: object) -> dict[str, str | None]:
    if not isinstance(card, Mapping) or set(card) != _CARD_FIELDS:
        raise TaskCardIndexError("task-card fields are not exact")
    if card.get("schema") != "codex-house-task-card/1":
        raise TaskCardIndexError("invalid task-card schema")
    if card.get("dispatch") != "NOT_ATTEMPTED":
        raise TaskCardIndexError("task-card dispatch is not inert")

    profile = card.get("profile")
    if not isinstance(profile, Mapping) or set(profile) != _PROFILE_FIELDS:
        raise TaskCardIndexError("task-card profile fields are not exact")
    profile_model_class = _text(profile.get("model_class"), "profile model class", 64)
    profile_effort = _text(profile.get("reasoning_effort"), "profile effort", 64)
    _text(profile.get("omp_policy"), "profile policy", 128)

    advisory = card.get("model_advisory")
    if not isinstance(advisory, Mapping) or set(advisory) != _ADVISORY_FIELDS:
        raise TaskCardIndexError("task-card advisory fields are not exact")
    if advisory.get("mode") != "ADVISORY_NO_SWITCH":
        raise TaskCardIndexError("task-card advisory may not switch a model")
    advisory_model = _text(advisory.get("recommended_model"), "advisory model", 256)
    if advisory.get("reasoning_effort") != profile_effort:
        raise TaskCardIndexError("task-card advisory/profile effort mismatch")
    _optional_text(advisory.get("eligible_leaf_worker"), "eligible leaf worker", 256)
    _text(advisory.get("reason"), "advisory reason", 1_024)
    _text(advisory.get("reassess_trigger"), "advisory reassess trigger", 1_024)

    recipient = _text(card.get("requested_recipient"), "requested recipient", 64)
    if recipient not in _RECIPIENTS:
        raise TaskCardIndexError("unknown requested recipient")
    recipient_id = _optional_text(
        card.get("requested_recipient_id"), "recipient id", 256
    )
    if (recipient == "specific_model") != (recipient_id is not None):
        raise TaskCardIndexError("recipient/id relation is invalid")

    disposition = _text(card.get("disposition"), "disposition", 64)
    if disposition not in {"open", "candidate"}:
        raise TaskCardIndexError("unsupported disposition")
    return {
        "task_id": _text(card.get("task_id"), "task id", 256),
        "work_id": _text(card.get("work_id"), "work id", 256),
        "title": _text(card.get("title"), "title", MAX_TASK_TITLE_CHARS),
        "summary": _text(card.get("summary"), "summary", MAX_TASK_SUMMARY_CHARS),
        "case_type": _text_or_empty(card.get("case_type"), "case type", 128),
        "profile_model_class": profile_model_class,
        "profile_effort": profile_effort,
        "advisory_model": advisory_model,
        "automatic_route_id": _text(
            card.get("automatic_route_id"), "automatic route", 256
        ),
        "routing_decision_sha256": _digest(
            card.get("routing_decision_sha256"), "routing decision digest"
        ),
        "manual_route_id": _optional_text(
            card.get("manual_route_id"), "manual route", 256
        ),
        "manual_selection_sha256": _digest(
            card.get("manual_selection_sha256"),
            "manual selection digest",
            optional=True,
        ),
        "requested_recipient": recipient,
        "requested_recipient_id": recipient_id,
        "wip_buffer_sha256": _digest(
            card.get("wip_buffer_sha256"), "WIP digest", optional=True
        ),
        "candidate_envelope_id": _optional_text(
            card.get("candidate_envelope_id"), "candidate envelope", 256
        ),
        "disposition": disposition,
    }


def _display(value: str | None) -> str:
    return "—" if value is None else html.escape(value, quote=True)


def _task_row(fields: Mapping[str, str | None]) -> str:
    return "".join(
        (
            '<article class="card"><header><strong>',
            _display(fields["title"]),
            "</strong><span>",
            _display(fields["disposition"]),
            " · NOT_ATTEMPTED</span></header><p>",
            _display(fields["summary"]),
            "</p><dl><dt>Task</dt><dd><code>",
            _display(fields["task_id"]),
            "</code></dd><dt>Case</dt><dd>",
            _display(fields["case_type"]),
            "</dd><dt>Recommended</dt><dd>",
            _display(fields["advisory_model"]),
            " / ",
            _display(fields["profile_effort"]),
            " (advisory only)</dd><dt>Recipient</dt><dd>",
            _display(fields["requested_recipient"]),
            "</dd><dt>Route receipt</dt><dd><code>",
            _display(fields["routing_decision_sha256"]),
            "</code></dd></dl></article>",
        )
    )


def _source_note(source_state: object) -> str:
    if source_state is None:
        return ""
    if not isinstance(source_state, str) or source_state not in _SOURCE_NOTES:
        raise TaskCardIndexError("invalid task-card source scope")
    return f"<p>{_SOURCE_NOTES[source_state]}</p>"


def render_task_card_index_html(cards: object, *, source_state: object = None) -> str:
    """Render bounded task-card projections without consulting task-spine state."""
    if not isinstance(cards, list):
        raise TaskCardIndexError("task cards must be a list")
    if len(cards) > MAX_TASK_CARDS:
        raise TaskCardIndexError(f"task-card count exceeds {MAX_TASK_CARDS}")

    fields = [_validated_card(card) for card in cards]
    task_ids = [item["task_id"] for item in fields]
    if len(task_ids) != len(set(task_ids)):
        raise TaskCardIndexError("duplicate task-card")
    fields.sort(key=lambda item: str(item["task_id"]))
    source_note = _source_note(source_state)

    document = "".join(
        (
            '<!doctype html><html lang="en"><head><meta charset="utf-8">',
            '<meta http-equiv="Content-Security-Policy" content="default-src ',
            "'none'; style-src 'unsafe-inline'; img-src 'none'; connect-src 'none'; ",
            "form-action 'none'; base-uri 'none'; frame-ancestors 'none'\">",
            '<meta name="referrer" content="no-referrer">',
            '<meta name="viewport" content="width=device-width,initial-scale=1">',
            "<title>🏠 Task cards</title><style>",
            "html{color-scheme:dark}body{margin:0;padding:14px;background:#101310;",
            "color:#d8e8d8;font:13px ui-monospace,SFMono-Regular,Menlo,monospace}",
            ".summary{color:#9fc99f;margin:0 0 12px}.card{border:1px solid #304630;",
            "border-radius:8px;padding:10px;background:#151a15;margin:0 0 10px}",
            "header{display:flex;justify-content:space-between;gap:12px;color:#9fc99f}",
            "p{white-space:pre-wrap;overflow-wrap:anywhere}dl{display:grid;",
            "grid-template-columns:max-content 1fr;gap:5px 10px;margin:0}",
            "dt{color:#8a9f8a}dd{margin:0;overflow-wrap:anywhere}code{color:#d8e8d8}",
            '</style></head><body><p class="summary">Observe only · ',
            str(len(fields)),
            " task cards · routing is advisory · dispatch not attempted</p><main>",
            source_note,
            "".join(_task_row(item) for item in fields),
            "</main></body></html>",
        )
    )
    if len(document.encode("utf-8")) > MAX_TASK_INDEX_BYTES:
        raise TaskCardIndexError(
            f"task-card index exceeds {MAX_TASK_INDEX_BYTES} bytes"
        )
    return document

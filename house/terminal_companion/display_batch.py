"""Versioned, one-way batches for a future local iTerm display adapter."""

from __future__ import annotations

import copy
import hashlib
import json
import re
import unicodedata
from collections import OrderedDict
from typing import Any

from .projector import CompanionProjectionError

CURRENT_REVISION = 1
MINIMUM_PEER = 1
MAX_DISPLAY_CARDS = 128
MAX_DISPLAY_OUTPUT_CHARS = 2_000_000
MAX_DISPLAY_BATCH_BYTES = 8 * 1024 * 1024
MAX_REORDERED_DISPLAY_BATCHES = 50

_HEX_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_UNSAFE_TEXT_CATEGORIES = {"Cc", "Cf", "Cs"}
_CARD_FIELDS = {
    "schema",
    "thread_id",
    "turn_id",
    "item_id",
    "command",
    "cwd",
    "status",
    "exit_code",
    "duration_ms",
    "output",
    "source",
    "redaction_state",
    "output_redaction_state",
    "content_trust",
    "dispatch",
}
_DISPLAY_CARD_FIELDS = _CARD_FIELDS | {"source_card_sha256", "text_rendering_state"}
_BATCH_FIELDS = {
    "schema",
    "protocol_revision",
    "minimum_peer",
    "sequence",
    "previous_batch_id",
    "direction",
    "source",
    "target",
    "authority",
    "reverse_channel",
    "transport",
    "presentation_format",
    "cards",
    "batch_id",
}


def evaluate_compatibility(peer_revision: int, peer_minimum_peer: int) -> str:
    """Evaluate a peer exactly once, independently of app bundle versions."""
    for value, field in (
        (peer_revision, "peer_revision"),
        (peer_minimum_peer, "peer_minimum_peer"),
    ):
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise CompanionProjectionError(f"{field} must be a positive integer")
    if CURRENT_REVISION < peer_minimum_peer:
        return "SELF_UPGRADE_REQUIRED"
    if peer_revision < MINIMUM_PEER:
        return "PEER_UPGRADE_REQUIRED"
    return "COMPATIBLE"


def _validate_card(card: object, index: int) -> dict[str, Any]:
    if not isinstance(card, dict) or set(card) != _CARD_FIELDS:
        raise CompanionProjectionError(
            f"display card {index} does not match the revision-1 schema"
        )
    required = {
        "schema": "codex-house-terminal-command-card/1",
        "source": "exported_app_server_notification",
        "redaction_state": "UPSTREAM_ASSERTED",
        "output_redaction_state": "NOT_ATTESTED",
        "content_trust": "DISPLAY_ONLY",
        "dispatch": "NOT_ATTEMPTED",
    }
    for field, expected in required.items():
        if card.get(field) != expected:
            raise CompanionProjectionError(f"display card {index} has unsafe {field}")
    if card.get("status") not in {"completed", "failed", "declined"}:
        raise CompanionProjectionError(f"display card {index} has unsupported status")
    for field in ("thread_id", "turn_id", "item_id", "command", "cwd"):
        if not isinstance(card.get(field), str) or not card[field]:
            raise CompanionProjectionError(f"display card {index} has invalid {field}")
    output = card.get("output")
    if output is not None and not isinstance(output, str):
        raise CompanionProjectionError(f"display card {index} has invalid output")
    for field in ("exit_code", "duration_ms"):
        value = card.get(field)
        if value is not None and (
            not isinstance(value, int) or isinstance(value, bool)
        ):
            raise CompanionProjectionError(f"display card {index} has invalid {field}")
    return dict(card)


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def _escape_for_plain_text(value: str) -> str:
    """Make terminal controls and invisible format controls visibly inert."""
    escaped: list[str] = []
    named = {"\n": r"\n", "\r": r"\r", "\t": r"\t"}
    for character in value:
        if character in named:
            escaped.append(named[character])
        elif unicodedata.category(character) in _UNSAFE_TEXT_CATEGORIES:
            escaped.append(f"\\u{ord(character):04x}")
        else:
            escaped.append(character)
    return "".join(escaped)


def _display_card(card: dict[str, Any]) -> dict[str, Any]:
    source_sha256 = hashlib.sha256(_canonical_bytes(card)).hexdigest()
    safe = dict(card)
    safe["schema"] = "codex-house-iterm-display-card/1"
    for field in ("thread_id", "turn_id", "item_id", "command", "cwd"):
        safe[field] = _escape_for_plain_text(safe[field])
    if safe["output"] is not None:
        safe["output"] = _escape_for_plain_text(safe["output"])
    safe["source_card_sha256"] = source_sha256
    safe["text_rendering_state"] = "CONTROL_AND_FORMAT_CHARACTERS_ESCAPED"
    return safe


def _validate_display_card(card: object, index: int) -> None:
    if not isinstance(card, dict) or set(card) != _DISPLAY_CARD_FIELDS:
        raise CompanionProjectionError(f"display-batch card {index} has schema drift")
    required = {
        "schema": "codex-house-iterm-display-card/1",
        "source": "exported_app_server_notification",
        "redaction_state": "UPSTREAM_ASSERTED",
        "output_redaction_state": "NOT_ATTESTED",
        "content_trust": "DISPLAY_ONLY",
        "dispatch": "NOT_ATTEMPTED",
        "text_rendering_state": "CONTROL_AND_FORMAT_CHARACTERS_ESCAPED",
    }
    for field, expected in required.items():
        if card.get(field) != expected:
            raise CompanionProjectionError(
                f"display-batch card {index} has unsafe {field}"
            )
    if not isinstance(card.get("source_card_sha256"), str) or not _HEX_DIGEST.fullmatch(
        card["source_card_sha256"]
    ):
        raise CompanionProjectionError(
            f"display-batch card {index} has invalid source digest"
        )
    if card.get("status") not in {"completed", "failed", "declined"}:
        raise CompanionProjectionError(
            f"display-batch card {index} has unsupported status"
        )
    for field in ("exit_code", "duration_ms"):
        value = card.get(field)
        if value is not None and (
            not isinstance(value, int) or isinstance(value, bool)
        ):
            raise CompanionProjectionError(
                f"display-batch card {index} has invalid {field}"
            )
    for field in ("thread_id", "turn_id", "item_id", "command", "cwd", "output"):
        value = card.get(field)
        if value is None and field == "output":
            continue
        if not isinstance(value, str) or (field != "output" and not value):
            raise CompanionProjectionError(
                f"display-batch card {index} has invalid {field}"
            )
        if any(
            unicodedata.category(character) in _UNSAFE_TEXT_CATEGORIES
            for character in value
        ):
            raise CompanionProjectionError(
                f"display-batch card {index} has unsafe text controls"
            )


def build_display_batch(
    cards: list[object],
    *,
    sequence: int,
    previous_batch_id: str | None = None,
) -> dict[str, Any]:
    """Build a deterministic display-only batch without performing transport."""
    if not isinstance(cards, list):
        raise CompanionProjectionError("cards must be a list")
    if len(cards) > MAX_DISPLAY_CARDS:
        raise CompanionProjectionError(
            f"display card count exceeds {MAX_DISPLAY_CARDS}"
        )
    if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 0:
        raise CompanionProjectionError("sequence must be a non-negative integer")
    if previous_batch_id is not None and not _HEX_DIGEST.fullmatch(previous_batch_id):
        raise CompanionProjectionError(
            "previous_batch_id must be a lowercase SHA-256 digest or null"
        )
    if sequence == 0 and previous_batch_id is not None:
        raise CompanionProjectionError("sequence 0 must not name a previous batch")
    if sequence > 0 and previous_batch_id is None:
        raise CompanionProjectionError(
            "sequence greater than 0 requires a previous batch"
        )

    validated = [_validate_card(card, index) for index, card in enumerate(cards)]
    output_chars = sum(len(card["output"] or "") for card in validated)
    if output_chars > MAX_DISPLAY_OUTPUT_CHARS:
        raise CompanionProjectionError(
            f"display output exceeds {MAX_DISPLAY_OUTPUT_CHARS} characters"
        )

    body: dict[str, Any] = {
        "schema": "codex-house-iterm-display-batch/1",
        "protocol_revision": CURRENT_REVISION,
        "minimum_peer": MINIMUM_PEER,
        "sequence": sequence,
        "previous_batch_id": previous_batch_id,
        "direction": "CODEX_TO_ITERM",
        "source": "codex_house_terminal_companion",
        "target": "iterm_local_display_adapter",
        "authority": "OBSERVE_ONLY",
        "reverse_channel": "PROHIBITED",
        "transport": "NOT_ATTEMPTED",
        "presentation_format": "PLAIN_TEXT_ONLY",
        "cards": [_display_card(card) for card in validated],
    }
    encoded = _canonical_bytes(body)
    if len(encoded) > MAX_DISPLAY_BATCH_BYTES:
        raise CompanionProjectionError(
            f"display batch exceeds {MAX_DISPLAY_BATCH_BYTES} encoded bytes"
        )
    return {**body, "batch_id": hashlib.sha256(encoded).hexdigest()}


def verify_display_chain(batches: list[object]) -> None:
    """Verify a complete in-memory chain from sequence zero through its tip."""
    if not isinstance(batches, list):
        raise CompanionProjectionError("batches must be a list")
    previous: str | None = None
    for expected_sequence, batch in enumerate(batches):
        if not isinstance(batch, dict) or set(batch) != _BATCH_FIELDS:
            raise CompanionProjectionError(
                f"display batch {expected_sequence} has schema drift"
            )
        expected = {
            "schema": "codex-house-iterm-display-batch/1",
            "protocol_revision": CURRENT_REVISION,
            "minimum_peer": MINIMUM_PEER,
            "direction": "CODEX_TO_ITERM",
            "source": "codex_house_terminal_companion",
            "target": "iterm_local_display_adapter",
            "authority": "OBSERVE_ONLY",
            "reverse_channel": "PROHIBITED",
            "transport": "NOT_ATTEMPTED",
            "presentation_format": "PLAIN_TEXT_ONLY",
        }
        for field, value in expected.items():
            if batch.get(field) != value:
                raise CompanionProjectionError(
                    f"display batch {expected_sequence} has unsafe {field}"
                )
        if batch.get("sequence") != expected_sequence:
            raise CompanionProjectionError(
                f"display batch {expected_sequence} is out of sequence"
            )
        if batch.get("previous_batch_id") != previous:
            raise CompanionProjectionError(
                f"display batch {expected_sequence} does not link to its predecessor"
            )
        cards = batch.get("cards")
        if not isinstance(cards, list) or len(cards) > MAX_DISPLAY_CARDS:
            raise CompanionProjectionError(
                f"display batch {expected_sequence} has invalid cards"
            )
        for card_index, card in enumerate(cards):
            _validate_display_card(card, card_index)
        batch_id = batch.get("batch_id")
        if not isinstance(batch_id, str) or not _HEX_DIGEST.fullmatch(batch_id):
            raise CompanionProjectionError(
                f"display batch {expected_sequence} has invalid id"
            )
        body = {field: value for field, value in batch.items() if field != "batch_id"}
        encoded = _canonical_bytes(body)
        if len(encoded) > MAX_DISPLAY_BATCH_BYTES:
            raise CompanionProjectionError(
                f"display batch {expected_sequence} exceeds the encoded byte limit"
            )
        if hashlib.sha256(encoded).hexdigest() != batch_id:
            raise CompanionProjectionError(
                f"display batch {expected_sequence} has invalid identity"
            )
        previous = batch_id


def _validate_display_batch(batch: object) -> dict[str, Any]:
    """Validate one batch without assuming its predecessor is locally present."""
    if not isinstance(batch, dict) or set(batch) != _BATCH_FIELDS:
        raise CompanionProjectionError("display batch has schema drift")
    expected = {
        "schema": "codex-house-iterm-display-batch/1",
        "protocol_revision": CURRENT_REVISION,
        "minimum_peer": MINIMUM_PEER,
        "direction": "CODEX_TO_ITERM",
        "source": "codex_house_terminal_companion",
        "target": "iterm_local_display_adapter",
        "authority": "OBSERVE_ONLY",
        "reverse_channel": "PROHIBITED",
        "transport": "NOT_ATTEMPTED",
        "presentation_format": "PLAIN_TEXT_ONLY",
    }
    for field, value in expected.items():
        if batch.get(field) != value:
            raise CompanionProjectionError(f"display batch has unsafe {field}")
    sequence = batch.get("sequence")
    if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 0:
        raise CompanionProjectionError("display batch has invalid sequence")
    predecessor = batch.get("previous_batch_id")
    if sequence == 0:
        if predecessor is not None:
            raise CompanionProjectionError("display batch zero has a predecessor")
    elif not isinstance(predecessor, str) or not _HEX_DIGEST.fullmatch(predecessor):
        raise CompanionProjectionError("display batch has invalid predecessor")
    cards = batch.get("cards")
    if not isinstance(cards, list) or len(cards) > MAX_DISPLAY_CARDS:
        raise CompanionProjectionError("display batch has invalid cards")
    for card_index, card in enumerate(cards):
        _validate_display_card(card, card_index)
    batch_id = batch.get("batch_id")
    if not isinstance(batch_id, str) or not _HEX_DIGEST.fullmatch(batch_id):
        raise CompanionProjectionError("display batch has invalid id")
    body = {field: value for field, value in batch.items() if field != "batch_id"}
    encoded = _canonical_bytes(body)
    if len(encoded) > MAX_DISPLAY_BATCH_BYTES:
        raise CompanionProjectionError("display batch exceeds the encoded byte limit")
    if hashlib.sha256(encoded).hexdigest() != batch_id:
        raise CompanionProjectionError("display batch has invalid identity")
    return copy.deepcopy(batch)


class DisplayBatchReconciler:
    """In-memory bounded reorder buffer for a future display-only receiver."""

    def __init__(self, *, max_reordered_batches: int = MAX_REORDERED_DISPLAY_BATCHES) -> None:
        if (
            not isinstance(max_reordered_batches, int)
            or isinstance(max_reordered_batches, bool)
            or not 1 <= max_reordered_batches <= MAX_REORDERED_DISPLAY_BATCHES
        ):
            raise CompanionProjectionError(
                f"max_reordered_batches must be between 1 and {MAX_REORDERED_DISPLAY_BATCHES}"
            )
        self._max_reordered_batches = max_reordered_batches
        self._next_sequence = 0
        self._previous_batch_id: str | None = None
        self._buffer: dict[int, dict[str, Any]] = {}
        self._applied: OrderedDict[int, str] = OrderedDict()

    def accept(self, batch: object) -> dict[str, Any]:
        """Accept one valid batch and return only newly contiguous batches.

        This is a pure state-machine step. Applying the returned batches to a
        future WebView is intentionally outside this component.
        """
        candidate = _validate_display_batch(batch)
        sequence = candidate["sequence"]
        batch_id = candidate["batch_id"]
        if sequence < self._next_sequence:
            if self._applied.get(sequence) == batch_id:
                return self._receipt("DUPLICATE_IGNORED", [])
            raise CompanionProjectionError("stale or conflicting display batch")
        if sequence - self._next_sequence > self._max_reordered_batches:
            raise CompanionProjectionError("display batch exceeds reorder distance")
        buffered = self._buffer.get(sequence)
        if buffered is not None:
            if buffered["batch_id"] == batch_id:
                return self._receipt("DUPLICATE_IGNORED", [])
            raise CompanionProjectionError("conflicting buffered display batch")
        if sequence != self._next_sequence and len(self._buffer) >= self._max_reordered_batches:
            raise CompanionProjectionError("display batch reorder buffer is full")

        tentative = {**self._buffer, sequence: candidate}
        next_sequence = self._next_sequence
        previous_batch_id = self._previous_batch_id
        newly_applied: list[dict[str, Any]] = []
        while (pending := tentative.get(next_sequence)) is not None:
            if pending["previous_batch_id"] != previous_batch_id:
                raise CompanionProjectionError("display batch does not link to current predecessor")
            newly_applied.append(pending)
            previous_batch_id = pending["batch_id"]
            del tentative[next_sequence]
            next_sequence += 1

        self._buffer = tentative
        self._next_sequence = next_sequence
        self._previous_batch_id = previous_batch_id
        for applied in newly_applied:
            self._applied[applied["sequence"]] = applied["batch_id"]
            if len(self._applied) > self._max_reordered_batches:
                self._applied.popitem(last=False)
        return self._receipt("APPLIED" if newly_applied else "BUFFERED", newly_applied)

    def snapshot(self) -> dict[str, Any]:
        """Return bounded metadata only; no card content is exposed here."""
        return {
            "next_sequence": self._next_sequence,
            "previous_batch_id": self._previous_batch_id,
            "buffered_sequences": sorted(self._buffer),
            "replay_history_sequences": list(self._applied),
            "max_reordered_batches": self._max_reordered_batches,
            "direction": "CODEX_TO_ITERM",
            "authority": "OBSERVE_ONLY",
            "reverse_channel": "PROHIBITED",
        }

    def _receipt(self, state: str, applied: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "state": state,
            "applied": copy.deepcopy(applied),
            "next_sequence": self._next_sequence,
            "buffered_count": len(self._buffer),
            "direction": "CODEX_TO_ITERM",
            "authority": "OBSERVE_ONLY",
            "reverse_channel": "PROHIBITED",
        }

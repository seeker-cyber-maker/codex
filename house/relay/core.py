"""Durable store-and-forward envelopes without worker execution or authority."""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ENVELOPE_SCHEMA = "codex-house-relay-envelope/1"
RECEIPT_SCHEMA = "codex-house-relay-receipt/1"
IDENTIFIER_RE = re.compile(r"^[a-z0-9][a-z0-9._:-]{1,127}$")
CONTRACT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,127}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
MAX_TTL_HOPS = 8
MAX_TURN_BUDGET = 16


class RelayError(ValueError):
    """Raised when a relay envelope violates its durable contract."""


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or not IDENTIFIER_RE.fullmatch(value):
        raise RelayError(f"{label} must be a normalized identifier")
    return value


def _integer(value: object, label: str, *, lower: int, upper: int) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or not lower <= value <= upper
    ):
        raise RelayError(f"{label} must be an integer between {lower} and {upper}")
    return value


def _payload(value: object) -> dict[str, str]:
    if not isinstance(value, Mapping) or set(value) != {"kind", "artifact_sha256"}:
        raise RelayError("payload must contain exactly kind and artifact_sha256")
    kind = _identifier(value.get("kind"), "payload kind")
    artifact_sha256 = value.get("artifact_sha256")
    if not isinstance(artifact_sha256, str) or not SHA256_RE.fullmatch(artifact_sha256):
        raise RelayError("payload artifact_sha256 must be a SHA-256 identifier")
    return {"kind": kind, "artifact_sha256": artifact_sha256}


class Relay:
    """One local durable relay; delivery is a record transition, never execution."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys = ON")
        self._initialize()

    def close(self) -> None:
        self.db.close()

    def _initialize(self) -> None:
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS envelope (
                envelope_id TEXT PRIMARY KEY,
                thread_id TEXT NOT NULL,
                parent_envelope_id TEXT REFERENCES envelope(envelope_id),
                sender_id TEXT NOT NULL,
                recipient_id TEXT NOT NULL,
                contract_version TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                payload_sha256 TEXT NOT NULL,
                envelope_sha256 TEXT NOT NULL,
                ttl_hops INTEGER NOT NULL,
                turn_budget INTEGER NOT NULL,
                hop_count INTEGER NOT NULL DEFAULT 0,
                state TEXT NOT NULL CHECK(state IN ('QUEUED', 'DELIVERED', 'ACKNOWLEDGED')),
                created_at_utc TEXT NOT NULL,
                delivered_at_utc TEXT,
                acknowledged_at_utc TEXT,
                acknowledgement TEXT
            );
            CREATE TABLE IF NOT EXISTS relay_event (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL,
                body_json TEXT NOT NULL,
                previous_sha256 TEXT,
                event_sha256 TEXT NOT NULL UNIQUE
            );
            """
        )
        self.db.commit()

    def _event(self, kind: str, body: Mapping[str, Any]) -> None:
        previous = self.db.execute(
            "SELECT event_sha256 FROM relay_event ORDER BY sequence DESC LIMIT 1"
        ).fetchone()
        previous_sha256 = previous["event_sha256"] if previous else None
        event_body = {
            "kind": kind,
            "body": dict(body),
            "previous_sha256": previous_sha256,
        }
        self.db.execute(
            "INSERT INTO relay_event(kind, body_json, previous_sha256, event_sha256) VALUES (?, ?, ?, ?)",
            (kind, _canonical(dict(body)), previous_sha256, _sha256(event_body)),
        )

    def _row(self, envelope_id: str) -> sqlite3.Row:
        row = self.db.execute(
            "SELECT * FROM envelope WHERE envelope_id = ?", (envelope_id,)
        ).fetchone()
        if row is None:
            raise RelayError("unknown envelope_id")
        return row

    @staticmethod
    def _record(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "schema": RECEIPT_SCHEMA,
            "envelope_id": row["envelope_id"],
            "thread_id": row["thread_id"],
            "parent_envelope_id": row["parent_envelope_id"],
            "sender_id": row["sender_id"],
            "recipient_id": row["recipient_id"],
            "contract_version": row["contract_version"],
            "payload": json.loads(row["payload_json"]),
            "payload_sha256": row["payload_sha256"],
            "ttl_hops": row["ttl_hops"],
            "hop_count": row["hop_count"],
            "turn_budget": row["turn_budget"],
            "state": row["state"],
            "authority_disposition": "NO_AUTHORITY_GRANTED",
            "runtime_disposition": "NOT_ATTEMPTED",
        }

    def submit(self, raw: object) -> dict[str, Any]:
        if not isinstance(raw, Mapping):
            raise RelayError("envelope must be an object")
        allowed = {
            "schema",
            "envelope_id",
            "thread_id",
            "parent_envelope_id",
            "sender_id",
            "recipient_id",
            "contract_version",
            "payload",
            "ttl_hops",
            "turn_budget",
        }
        unknown = set(raw) - allowed
        required = allowed - {"parent_envelope_id"}
        if unknown or not required.issubset(raw):
            raise RelayError("envelope fields are not exact")
        if raw.get("schema") != ENVELOPE_SCHEMA:
            raise RelayError("invalid envelope schema")
        envelope_id = _identifier(raw.get("envelope_id"), "envelope_id")
        thread_id = _identifier(raw.get("thread_id"), "thread_id")
        sender_id = _identifier(raw.get("sender_id"), "sender_id")
        recipient_id = _identifier(raw.get("recipient_id"), "recipient_id")
        contract_version = raw.get("contract_version")
        if not isinstance(contract_version, str) or not CONTRACT_RE.fullmatch(
            contract_version
        ):
            raise RelayError(
                "contract_version must be a normalized contract identifier"
            )
        payload = _payload(raw.get("payload"))
        ttl_hops = _integer(
            raw.get("ttl_hops"), "ttl_hops", lower=1, upper=MAX_TTL_HOPS
        )
        turn_budget = _integer(
            raw.get("turn_budget"), "turn_budget", lower=0, upper=MAX_TURN_BUDGET
        )
        parent_id = raw.get("parent_envelope_id")
        if parent_id is not None:
            parent_id = _identifier(parent_id, "parent_envelope_id")
        elif turn_budget == 0:
            raise RelayError("root envelope turn budget must allow one reply")
        normalized_envelope = {
            "schema": ENVELOPE_SCHEMA,
            "envelope_id": envelope_id,
            "thread_id": thread_id,
            "parent_envelope_id": parent_id,
            "sender_id": sender_id,
            "recipient_id": recipient_id,
            "contract_version": contract_version,
            "payload": payload,
            "ttl_hops": ttl_hops,
            "turn_budget": turn_budget,
        }
        envelope_sha256 = _sha256(normalized_envelope)

        with self.db:
            duplicate = self.db.execute(
                "SELECT * FROM envelope WHERE envelope_id = ?", (envelope_id,)
            ).fetchone()
            if duplicate is not None:
                if duplicate["envelope_sha256"] == envelope_sha256:
                    return self._record(duplicate)
                raise RelayError("envelope_id is already bound to different content")
            if parent_id is not None:
                parent = self._row(parent_id)
                if parent["thread_id"] != thread_id:
                    raise RelayError("reply thread_id does not match parent")
                if (
                    parent["recipient_id"] != sender_id
                    or parent["sender_id"] != recipient_id
                ):
                    raise RelayError(
                        "reply participants must reverse the parent envelope"
                    )
                if (
                    parent["turn_budget"] <= 0
                    or turn_budget != parent["turn_budget"] - 1
                ):
                    raise RelayError("reply exceeds parent turn budget")
            payload_json = _canonical(payload)
            created_at = _utc_now()
            self.db.execute(
                """INSERT INTO envelope(
                    envelope_id, thread_id, parent_envelope_id, sender_id, recipient_id,
                    contract_version, payload_json, payload_sha256, envelope_sha256, ttl_hops, turn_budget,
                    state, created_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'QUEUED', ?)""",
                (
                    envelope_id,
                    thread_id,
                    parent_id,
                    sender_id,
                    recipient_id,
                    contract_version,
                    payload_json,
                    _sha256(payload),
                    envelope_sha256,
                    ttl_hops,
                    turn_budget,
                    created_at,
                ),
            )
            row = self._row(envelope_id)
            self._event("envelope.queued", self._record(row))
        return self._record(row)

    def receive(self, recipient_id: str, *, limit: int = 1) -> list[dict[str, Any]]:
        recipient_id = _identifier(recipient_id, "recipient_id")
        limit = _integer(limit, "limit", lower=1, upper=64)
        with self.db:
            rows = self.db.execute(
                "SELECT * FROM envelope WHERE recipient_id = ? AND state = 'QUEUED' ORDER BY created_at_utc, envelope_id LIMIT ?",
                (recipient_id, limit),
            ).fetchall()
            delivered: list[dict[str, Any]] = []
            for row in rows:
                if row["hop_count"] >= row["ttl_hops"]:
                    continue
                now = _utc_now()
                self.db.execute(
                    "UPDATE envelope SET state = 'DELIVERED', hop_count = hop_count + 1, delivered_at_utc = ? WHERE envelope_id = ?",
                    (now, row["envelope_id"]),
                )
                updated = self._row(row["envelope_id"])
                record = self._record(updated)
                self._event("envelope.delivered", record)
                delivered.append(record)
        return delivered

    def acknowledge(
        self, recipient_id: str, envelope_id: str, acknowledgement: str
    ) -> dict[str, Any]:
        recipient_id = _identifier(recipient_id, "recipient_id")
        envelope_id = _identifier(envelope_id, "envelope_id")
        if (
            not isinstance(acknowledgement, str)
            or not acknowledgement
            or len(acknowledgement) > 128
        ):
            raise RelayError(
                "acknowledgement must be non-empty text up to 128 characters"
            )
        with self.db:
            row = self._row(envelope_id)
            if row["recipient_id"] != recipient_id:
                raise RelayError("recipient may only acknowledge its own envelope")
            if row["state"] != "DELIVERED":
                raise RelayError("only a delivered envelope may be acknowledged")
            self.db.execute(
                "UPDATE envelope SET state = 'ACKNOWLEDGED', acknowledged_at_utc = ?, acknowledgement = ? WHERE envelope_id = ?",
                (_utc_now(), acknowledgement, envelope_id),
            )
            updated = self._row(envelope_id)
            record = self._record(updated)
            self._event("envelope.acknowledged", record)
        return record

    def get(self, envelope_id: str) -> dict[str, Any]:
        """Return one persisted status receipt without touching its state."""
        envelope_id = _identifier(envelope_id, "envelope_id")
        return self._record(self._row(envelope_id))

    def events(self) -> list[dict[str, Any]]:
        return [
            {
                "sequence": row["sequence"],
                "kind": row["kind"],
                "body": json.loads(row["body_json"]),
                "previous_sha256": row["previous_sha256"],
                "event_sha256": row["event_sha256"],
            }
            for row in self.db.execute("SELECT * FROM relay_event ORDER BY sequence")
        ]

    def verify_journal(self) -> bool:
        previous_sha256: str | None = None
        for event in self.events():
            expected = _sha256(
                {
                    "kind": event["kind"],
                    "body": event["body"],
                    "previous_sha256": previous_sha256,
                }
            )
            if (
                event["previous_sha256"] != previous_sha256
                or event["event_sha256"] != expected
            ):
                raise RelayError("relay journal hash chain is invalid")
            previous_sha256 = event["event_sha256"]
        return True

"""Finite local inbox and cooperative single-writer task controller."""

from __future__ import annotations

import hashlib
import json
import secrets
import sqlite3
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from .core import TaskSpine, TaskSpineError
from .submission import submit_task

INBOX_RECEIPT_SCHEMA = "codex-house-task-inbox-receipt/1"


class TaskInboxError(RuntimeError):
    """A fail-closed inbox or controller error."""


class SimulatedControllerInterrupt(TaskInboxError):
    """Test-only interruption after task acceptance but before inbox commit."""


def _canonical(value: Any) -> str:
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
    except (TypeError, ValueError) as exc:
        raise TaskInboxError(f"submission is not canonical JSON: {exc}") from exc


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _seal_receipt(unsigned: dict[str, Any]) -> dict[str, Any]:
    return {**unsigned, "receipt_sha256": _sha256_text(_canonical(unsigned))}


def _required_text(value: object, field: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TaskInboxError(f"{field} must be non-empty text")
    normalized = value.strip()
    if len(normalized) > maximum:
        raise TaskInboxError(f"{field} exceeds {maximum} characters")
    return normalized


class TaskInbox:
    """Producer inbox whose leased controller is the sole task-spine caller.

    The lease is a cooperative local fence, not an OS security boundary. Each
    drain call is finite and processes at most one queued record.
    """

    def __init__(
        self,
        database_path: str | Path,
        *,
        clock: Callable[[], float] | None = None,
    ) -> None:
        self.path = Path(database_path)
        self._clock = time.time if clock is None else clock
        self.db = sqlite3.connect(self.path, timeout=5)
        self.db.row_factory = sqlite3.Row
        self.db.execute(
            """CREATE TABLE IF NOT EXISTS inbox_entry (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                enqueue_id TEXT NOT NULL UNIQUE,
                submission_json TEXT NOT NULL,
                submission_sha256 TEXT NOT NULL,
                state TEXT NOT NULL CHECK(state IN ('QUEUED', 'CLAIMED', 'ACCEPTED', 'REJECTED')),
                claim_holder TEXT,
                claim_epoch INTEGER,
                claim_fencing_sha256 TEXT,
                terminal_receipt_json TEXT
            )"""
        )
        self.db.execute(
            """CREATE TABLE IF NOT EXISTS controller_lease (
                singleton INTEGER PRIMARY KEY CHECK(singleton = 1),
                holder TEXT NOT NULL,
                epoch INTEGER NOT NULL,
                fencing_token TEXT NOT NULL,
                expires_at REAL NOT NULL
            )"""
        )
        self.db.commit()

    def close(self) -> None:
        self.db.close()

    def enqueue(self, enqueue_id: str, submission: object) -> dict[str, Any]:
        enqueue_id = _required_text(enqueue_id, "enqueue_id", 128)
        submission_json = _canonical(submission)
        submission_sha256 = _sha256_text(submission_json)
        self.db.execute("BEGIN IMMEDIATE")
        try:
            existing = self.db.execute(
                "SELECT * FROM inbox_entry WHERE enqueue_id = ?", (enqueue_id,)
            ).fetchone()
            if existing is not None:
                if existing["submission_sha256"] != submission_sha256:
                    raise TaskInboxError(
                        "enqueue_id is already bound to different content"
                    )
                self.db.commit()
                return self._entry(existing)
            cursor = self.db.execute(
                """INSERT INTO inbox_entry(
                    enqueue_id, submission_json, submission_sha256, state
                ) VALUES (?, ?, ?, 'QUEUED')""",
                (enqueue_id, submission_json, submission_sha256),
            )
            row = self.db.execute(
                "SELECT * FROM inbox_entry WHERE sequence = ?", (cursor.lastrowid,)
            ).fetchone()
            self.db.commit()
            return self._entry(row)
        except Exception:
            self.db.rollback()
            raise

    def acquire_controller(
        self,
        holder: str,
        *,
        ttl_seconds: float = 30.0,
    ) -> dict[str, Any]:
        holder = _required_text(holder, "holder", 256)
        if not 1 <= ttl_seconds <= 300:
            raise TaskInboxError(
                "controller lease ttl_seconds must be between 1 and 300"
            )
        observed_at = float(self._clock())
        token = secrets.token_hex(24)
        self.db.execute("BEGIN IMMEDIATE")
        try:
            current = self.db.execute(
                "SELECT * FROM controller_lease WHERE singleton = 1"
            ).fetchone()
            if current is not None and float(current["expires_at"]) > observed_at:
                raise TaskInboxError("a controller lease is already active")
            epoch = 1 if current is None else int(current["epoch"]) + 1
            expires_at = observed_at + float(ttl_seconds)
            self.db.execute(
                """INSERT INTO controller_lease(singleton, holder, epoch, fencing_token, expires_at)
                VALUES (1, ?, ?, ?, ?)
                ON CONFLICT(singleton) DO UPDATE SET
                    holder = excluded.holder,
                    epoch = excluded.epoch,
                    fencing_token = excluded.fencing_token,
                    expires_at = excluded.expires_at""",
                (holder, epoch, token, expires_at),
            )
            self.db.commit()
            return {
                "holder": holder,
                "epoch": epoch,
                "fencing_token": token,
                "fencing_sha256": _sha256_text(token),
                "expires_at": expires_at,
            }
        except Exception:
            self.db.rollback()
            raise

    def release_controller(self, holder: str, fencing_token: str) -> dict[str, Any]:
        observed_at = float(self._clock())
        self.db.execute("BEGIN IMMEDIATE")
        try:
            lease = self._require_lease(holder, fencing_token, observed_at)
            self.db.execute(
                "UPDATE controller_lease SET expires_at = ? WHERE singleton = 1",
                (observed_at,),
            )
            self.db.commit()
            return {
                "holder": lease["holder"],
                "epoch": lease["epoch"],
                "fencing_sha256": _sha256_text(fencing_token),
                "released_at": observed_at,
                "state": "RELEASED",
            }
        except Exception:
            self.db.rollback()
            raise

    def drain_once(
        self,
        spine: TaskSpine,
        *,
        holder: str,
        fencing_token: str,
        simulate_interrupt_after_submit: bool = False,
    ) -> dict[str, Any] | None:
        if self.path.resolve() == spine.path.resolve():
            raise TaskInboxError("inbox and task-spine databases must be separate")
        observed_at = float(self._clock())
        self.db.execute("BEGIN IMMEDIATE")
        try:
            lease = self._require_lease(holder, fencing_token, observed_at)
            row = self.db.execute(
                """SELECT * FROM inbox_entry
                WHERE state = 'QUEUED'
                   OR (state = 'CLAIMED' AND (
                       claim_epoch != ? OR claim_fencing_sha256 != ?
                   ))
                ORDER BY sequence
                LIMIT 1""",
                (lease["epoch"], _sha256_text(fencing_token)),
            ).fetchone()
            if row is None:
                self.db.commit()
                return None
            self.db.execute(
                """UPDATE inbox_entry SET
                    state = 'CLAIMED', claim_holder = ?, claim_epoch = ?,
                    claim_fencing_sha256 = ?, terminal_receipt_json = NULL
                WHERE sequence = ?""",
                (holder, lease["epoch"], _sha256_text(fencing_token), row["sequence"]),
            )
            submission = json.loads(row["submission_json"])
            try:
                task_receipt = submit_task(spine, submission)
            except TaskSpineError as exc:
                terminal = _seal_receipt(
                    {
                        "schema": INBOX_RECEIPT_SCHEMA,
                        "enqueue_id": row["enqueue_id"],
                        "submission_sha256": row["submission_sha256"],
                        "state": "REJECTED",
                        "error_type": "TASK_SUBMISSION_REJECTED",
                        "error": str(exc),
                        "dispatch": "NOT_ATTEMPTED",
                    }
                )
                terminal_at = float(self._clock())
                self._require_lease(holder, fencing_token, terminal_at)
                self._set_terminal(row["sequence"], "REJECTED", terminal)
                self.db.commit()
                return terminal
            if simulate_interrupt_after_submit:
                raise SimulatedControllerInterrupt(
                    "simulated interruption after task acceptance and before inbox commit"
                )
            terminal = _seal_receipt(
                {
                    "schema": INBOX_RECEIPT_SCHEMA,
                    "enqueue_id": row["enqueue_id"],
                    "submission_sha256": row["submission_sha256"],
                    "state": "ACCEPTED",
                    "task_receipt": task_receipt,
                    "dispatch": "NOT_ATTEMPTED",
                }
            )
            terminal_at = float(self._clock())
            self._require_lease(holder, fencing_token, terminal_at)
            self._set_terminal(row["sequence"], "ACCEPTED", terminal)
            self.db.commit()
            return terminal
        except Exception:
            self.db.rollback()
            raise

    def entries(self) -> list[dict[str, Any]]:
        rows = self.db.execute("SELECT * FROM inbox_entry ORDER BY sequence").fetchall()
        return [self._entry(row) for row in rows]

    def _require_lease(
        self, holder: str, fencing_token: str, observed_at: float
    ) -> dict[str, Any]:
        row = self.db.execute(
            "SELECT * FROM controller_lease WHERE singleton = 1"
        ).fetchone()
        if row is None:
            raise TaskInboxError("no controller lease exists")
        if row["holder"] != holder or row["fencing_token"] != fencing_token:
            raise TaskInboxError("stale controller fencing token")
        if float(row["expires_at"]) <= observed_at:
            raise TaskInboxError("controller lease has expired")
        return {
            "holder": row["holder"],
            "epoch": int(row["epoch"]),
            "fencing_token": row["fencing_token"],
            "expires_at": float(row["expires_at"]),
        }

    def _set_terminal(self, sequence: int, state: str, receipt: dict[str, Any]) -> None:
        cursor = self.db.execute(
            """UPDATE inbox_entry SET state = ?, terminal_receipt_json = ?
            WHERE sequence = ? AND state = 'CLAIMED'""",
            (state, _canonical(receipt), sequence),
        )
        if cursor.rowcount != 1:
            raise TaskInboxError("claimed inbox record changed before terminal commit")

    @staticmethod
    def _entry(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "sequence": int(row["sequence"]),
            "enqueue_id": row["enqueue_id"],
            "submission": json.loads(row["submission_json"]),
            "submission_sha256": row["submission_sha256"],
            "state": row["state"],
            "claim_holder": row["claim_holder"],
            "claim_epoch": row["claim_epoch"],
            "claim_fencing_sha256": row["claim_fencing_sha256"],
            "terminal_receipt": None
            if row["terminal_receipt_json"] is None
            else json.loads(row["terminal_receipt_json"]),
        }

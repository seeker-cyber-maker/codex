"""Persistent, no-dispatch lifecycle for one prepared worker operation."""

from __future__ import annotations

import hashlib
import json
import secrets
import sqlite3
import time
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from .operation import WorkerExecError, verify_operation


class WorkerControllerError(RuntimeError):
    """Raised when a lifecycle transition is stale, conflicting, or unsafe."""


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical(value).encode()).hexdigest()


class WorkerOperationController:
    """Own local persistence, finite lease fencing, and blocked reconciliation."""

    def __init__(
        self, database_path: str | Path, *, clock: Callable[[], float] | None = None
    ) -> None:
        self._clock = time.time if clock is None else clock
        self.db = sqlite3.connect(Path(database_path), timeout=5)
        self.db.row_factory = sqlite3.Row
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS operation (id TEXT PRIMARY KEY, record_json TEXT NOT NULL, record_sha256 TEXT NOT NULL, state TEXT NOT NULL CHECK(state IN ('PREPARED','LEASED','BLOCKED')), observation_json TEXT)"
        )
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS lease (operation_id TEXT PRIMARY KEY, holder TEXT NOT NULL, epoch INTEGER NOT NULL, token TEXT NOT NULL, expires_at REAL NOT NULL)"
        )
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS launch_intent (operation_id TEXT PRIMARY KEY, holder TEXT NOT NULL, epoch INTEGER NOT NULL, token_sha256 TEXT NOT NULL, created_at REAL NOT NULL)"
        )
        self.db.commit()

    def close(self) -> None:
        self.db.close()

    def prepare(self, record: Mapping[str, object]) -> dict[str, Any]:
        try:
            verified = verify_operation(record)
        except WorkerExecError as exc:
            raise WorkerControllerError(str(exc)) from exc
        operation_id, digest = (
            str(verified["operation_id"]),
            str(verified["record_sha256"]),
        )
        self.db.execute("BEGIN IMMEDIATE")
        try:
            row = self.db.execute(
                "SELECT * FROM operation WHERE id = ?", (operation_id,)
            ).fetchone()
            if row is not None:
                if row["record_sha256"] != digest:
                    raise WorkerControllerError(
                        "operation id is bound to different record"
                    )
                self.db.commit()
                return self._entry(row)
            self.db.execute(
                "INSERT INTO operation VALUES (?, ?, ?, 'PREPARED', NULL)",
                (operation_id, _canonical(record), digest),
            )
            row = self.db.execute(
                "SELECT * FROM operation WHERE id = ?", (operation_id,)
            ).fetchone()
            self.db.commit()
            return self._entry(row)
        except Exception:
            self.db.rollback()
            raise

    def acquire(
        self, operation_id: str, holder: str, *, ttl_seconds: float = 30.0
    ) -> dict[str, Any]:
        if not holder.strip() or not 1 <= ttl_seconds <= 300:
            raise WorkerControllerError("invalid controller lease request")
        now = float(self._clock())
        self.db.execute("BEGIN IMMEDIATE")
        try:
            row = self.db.execute(
                "SELECT * FROM operation WHERE id = ?", (operation_id,)
            ).fetchone()
            if row is None:
                raise WorkerControllerError("unknown operation")
            if row["state"] == "BLOCKED":
                raise WorkerControllerError("blocked operation cannot be leased")
            old = self.db.execute(
                "SELECT * FROM lease WHERE operation_id = ?", (operation_id,)
            ).fetchone()
            if old is not None and float(old["expires_at"]) > now:
                raise WorkerControllerError("operation lease is already active")
            epoch = 1 if old is None else int(old["epoch"]) + 1
            token = secrets.token_hex(24)
            expires_at = now + ttl_seconds
            self.db.execute(
                "INSERT INTO lease VALUES (?, ?, ?, ?, ?) ON CONFLICT(operation_id) DO UPDATE SET holder=excluded.holder, epoch=excluded.epoch, token=excluded.token, expires_at=excluded.expires_at",
                (operation_id, holder.strip(), epoch, token, expires_at),
            )
            self.db.execute(
                "UPDATE operation SET state = 'LEASED' WHERE id = ?", (operation_id,)
            )
            self.db.commit()
            return {
                "operation_id": operation_id,
                "holder": holder.strip(),
                "epoch": epoch,
                "fencing_token": token,
                "fencing_sha256": _sha256(token),
                "expires_at": expires_at,
                "state": "LEASED",
            }
        except Exception:
            self.db.rollback()
            raise

    def block_runtime(
        self, operation_id: str, *, holder: str, fencing_token: str, reason: str
    ) -> dict[str, Any]:
        now = float(self._clock())
        self.db.execute("BEGIN IMMEDIATE")
        try:
            lease = self.db.execute(
                "SELECT * FROM lease WHERE operation_id = ?", (operation_id,)
            ).fetchone()
            if (
                lease is None
                or lease["holder"] != holder
                or lease["token"] != fencing_token
            ):
                raise WorkerControllerError("stale operation fencing token")
            if float(lease["expires_at"]) <= now:
                raise WorkerControllerError("operation lease has expired")
            observation = {
                "state": "BLOCKED_RUNTIME_QUALIFICATION",
                "reason": reason.strip(),
                "observed_at": now,
                "dispatch": "NOT_ATTEMPTED",
            }
            self.db.execute(
                "UPDATE operation SET state='BLOCKED', observation_json=? WHERE id=?",
                (_canonical(observation), operation_id),
            )
            self.db.execute(
                "UPDATE lease SET expires_at=? WHERE operation_id=?",
                (now, operation_id),
            )
            self.db.commit()
            return {
                "operation_id": operation_id,
                **observation,
                "observation_sha256": _sha256(observation),
            }
        except Exception:
            self.db.rollback()
            raise

    def claim_fixture_launch(
        self, operation_id: str, *, holder: str, fencing_token: str
    ) -> dict[str, Any]:
        """Atomically bind one injected-fixture attempt to the active fence.

        It does not spawn a process.  A separately reviewed real runner, if
        ever proposed, needs its own durable spawn-intent/RUNNING lifecycle.
        """

        now = float(self._clock())
        self.db.execute("BEGIN IMMEDIATE")
        try:
            row = self.db.execute(
                "SELECT state FROM operation WHERE id = ?", (operation_id,)
            ).fetchone()
            lease = self.db.execute(
                "SELECT * FROM lease WHERE operation_id = ?", (operation_id,)
            ).fetchone()
            if row is None or row["state"] != "LEASED":
                raise WorkerControllerError("operation is not actively leased")
            if (
                lease is None
                or lease["holder"] != holder
                or lease["token"] != fencing_token
                or float(lease["expires_at"]) <= now
            ):
                raise WorkerControllerError("stale operation fencing token")
            existing = self.db.execute(
                "SELECT operation_id FROM launch_intent WHERE operation_id = ?",
                (operation_id,),
            ).fetchone()
            if existing is not None:
                raise WorkerControllerError("fixture launch was already claimed")
            self.db.execute(
                "INSERT INTO launch_intent VALUES (?, ?, ?, ?, ?)",
                (operation_id, holder, lease["epoch"], _sha256(fencing_token), now),
            )
            self.db.commit()
            return {
                "operation_id": operation_id,
                "state": "FIXTURE_LAUNCH_CLAIMED_NO_DISPATCH",
                "holder": holder,
                "epoch": int(lease["epoch"]),
                "claimed_at": now,
            }
        except Exception:
            self.db.rollback()
            raise

    def entries(self) -> list[dict[str, Any]]:
        return [
            self._entry(row)
            for row in self.db.execute("SELECT * FROM operation ORDER BY id")
        ]

    def entry(self, operation_id: str) -> dict[str, Any]:
        row = self.db.execute(
            "SELECT * FROM operation WHERE id = ?", (operation_id,)
        ).fetchone()
        if row is None:
            raise WorkerControllerError("unknown operation")
        return self._entry(row)

    @staticmethod
    def _entry(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "operation_id": row["id"],
            "record": json.loads(row["record_json"]),
            "record_sha256": row["record_sha256"],
            "state": row["state"],
            "observation": None
            if row["observation_json"] is None
            else json.loads(row["observation_json"]),
        }

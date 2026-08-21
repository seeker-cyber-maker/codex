"""A small offline authority-path task spine.

The journal is canonical; SQLite's read model is disposable.  This module never
dispatches a worker or contacts a provider.  It is deliberately scoped to the
v0 candidate-admission path rather than a general Archive implementation.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

from house.auto_switcher import route_task


class TaskSpineError(RuntimeError):
    """A fail-closed task-spine command error."""


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


class TaskSpine:
    """Single-writer, temporary-DB task journal and deterministic projection."""

    def __init__(self, database_path: str | Path) -> None:
        self.path = Path(database_path)
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys = ON")
        self.db.execute(
            """CREATE TABLE IF NOT EXISTS journal (
                sequence INTEGER PRIMARY KEY,
                kind TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                previous_sha256 TEXT,
                event_sha256 TEXT NOT NULL UNIQUE
            )"""
        )
        self.db.commit()

    def close(self) -> None:
        self.db.close()

    def _head(self) -> str | None:
        row = self.db.execute("SELECT event_sha256 FROM journal ORDER BY sequence DESC LIMIT 1").fetchone()
        return None if row is None else str(row["event_sha256"])

    def _events(self) -> list[dict[str, Any]]:
        return [
            {"sequence": row["sequence"], "kind": row["kind"], "payload": json.loads(row["payload_json"]),
             "previous_sha256": row["previous_sha256"], "event_sha256": row["event_sha256"]}
            for row in self.db.execute("SELECT * FROM journal ORDER BY sequence")
        ]

    def _append(self, kind: str, payload: dict[str, Any]) -> dict[str, Any]:
        previous = self._head()
        sequence = int(self.db.execute("SELECT COALESCE(MAX(sequence), 0) + 1 FROM journal").fetchone()[0])
        unsigned = {"schema": "codex-house-task-event/1", "sequence": sequence, "kind": kind,
                    "payload": payload, "previous_sha256": previous}
        event_sha256 = _sha256(unsigned)
        self.db.execute(
            "INSERT INTO journal(sequence, kind, payload_json, previous_sha256, event_sha256) VALUES (?, ?, ?, ?, ?)",
            (sequence, kind, _canonical(payload), previous, event_sha256),
        )
        self.db.commit()
        return {**unsigned, "event_sha256": event_sha256}

    def create_work_item(self, work_id: str, title: str) -> dict[str, Any]:
        if not work_id or not title:
            raise TaskSpineError("work_id and title are required")
        return self._append("work_item.created", {"work_id": work_id, "title": title})

    def create_task_packet(self, task_id: str, work_id: str, summary: str, *, case_type: str = "") -> dict[str, Any]:
        if not task_id or not work_id or not summary:
            raise TaskSpineError("task_id, work_id, and summary are required")
        known_work_ids = {event["payload"]["work_id"] for event in self._events() if event["kind"] == "work_item.created"}
        if work_id not in known_work_ids:
            raise TaskSpineError("task packet references an unknown work item")
        routing_input = {"summary": summary}
        if case_type:
            routing_input["case_type"] = case_type
        route_receipt = route_task(routing_input)
        return self._append("task_packet.created", {
            "task_id": task_id, "work_id": work_id, "summary": summary,
            "routing_receipt": route_receipt,
        })

    def append_worker_buffer(self, buffer_id: str, task_id: str, record_id: str, body: str) -> dict[str, Any]:
        if not all((buffer_id, task_id, record_id, body)):
            raise TaskSpineError("buffer_id, task_id, record_id, and body are required")
        known_task_ids = {event["payload"]["task_id"] for event in self._events() if event["kind"] == "task_packet.created"}
        if task_id not in known_task_ids:
            raise TaskSpineError("worker buffer references an unknown task")
        return self._append("worker_buffer.appended", {
            "buffer_id": buffer_id, "task_id": task_id, "record_id": record_id,
            "body": body, "body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
        })

    def seal_worker_buffer(self, buffer_id: str) -> dict[str, Any]:
        records = [event["payload"] for event in self._events()
                   if event["kind"] == "worker_buffer.appended" and event["payload"]["buffer_id"] == buffer_id]
        if not records:
            raise TaskSpineError("cannot seal an empty or unknown worker buffer")
        task_ids = {record["task_id"] for record in records}
        if len(task_ids) != 1:
            raise TaskSpineError("worker buffer spans more than one task")
        return self._append("worker_buffer.sealed", {
            "buffer_id": buffer_id, "task_id": records[0]["task_id"], "record_count": len(records),
            "buffer_sha256": _sha256(records),
        })

    def seal_result_envelope(self, envelope_id: str, task_id: str, buffer_id: str, result_ref: str, status: str) -> dict[str, Any]:
        if status != "complete":
            raise TaskSpineError("only a complete result envelope is terminal in v0")
        return self._append("result_envelope.sealed", {
            "envelope_id": envelope_id, "task_id": task_id, "buffer_id": buffer_id,
            "result_ref": result_ref, "status": status,
        })

    def create_import_proposal(self, proposal_id: str, task_id: str, envelope_id: str) -> dict[str, Any]:
        envelopes = {event["payload"]["envelope_id"]: event["payload"] for event in self._events() if event["kind"] == "result_envelope.sealed"}
        if envelope_id not in envelopes:
            raise TaskSpineError("import proposal references an unknown result envelope")
        if task_id != envelopes[envelope_id]["task_id"]:
            raise TaskSpineError("import proposal task does not match result envelope")
        return self._append("import_proposal.created", {
            "proposal_id": proposal_id, "task_id": task_id, "envelope_id": envelope_id,
        })

    def authorize_import(self, proposal_id: str, lead_id: str) -> dict[str, Any]:
        if not proposal_id or not lead_id:
            raise TaskSpineError("proposal_id and lead_id are required")
        known_proposals = {event["payload"]["proposal_id"] for event in self._events() if event["kind"] == "import_proposal.created"}
        if proposal_id not in known_proposals:
            raise TaskSpineError("cannot authorize an unknown import proposal")
        return self._append("import_authorized", {"proposal_id": proposal_id, "lead_id": lead_id})

    def admit_candidate(self, proposal_id: str, *, actor: str, admission_basis_sha256: str) -> dict[str, Any]:
        if actor != "trusted_writer":
            raise TaskSpineError("only trusted_writer may admit a candidate")
        if admission_basis_sha256 != self._head():
            raise TaskSpineError("stale admission basis")
        events = self._events()
        proposals = {event["payload"]["proposal_id"]: event["payload"] for event in events if event["kind"] == "import_proposal.created"}
        proposal = proposals.get(proposal_id)
        if proposal is None:
            raise TaskSpineError("unknown import proposal")
        authorized = any(event["kind"] == "import_authorized" and event["payload"]["proposal_id"] == proposal_id for event in events)
        if not authorized:
            raise TaskSpineError("missing lead authorization")
        envelopes = {event["payload"]["envelope_id"]: event["payload"] for event in events if event["kind"] == "result_envelope.sealed"}
        envelope = envelopes.get(proposal["envelope_id"])
        if envelope is None or envelope["status"] != "complete":
            raise TaskSpineError("proposal has no complete result envelope")
        if envelope["task_id"] != proposal["task_id"]:
            raise TaskSpineError("proposal task does not match result envelope")
        seals = {event["payload"]["buffer_id"]: event["payload"] for event in events if event["kind"] == "worker_buffer.sealed"}
        if envelope["buffer_id"] not in seals:
            raise TaskSpineError("result envelope references an unsealed buffer")
        return self._append("candidate.admitted", {
            "proposal_id": proposal_id, "task_id": proposal["task_id"], "envelope_id": envelope["envelope_id"],
            "disposition": "candidate", "actor": actor, "admission_basis_sha256": admission_basis_sha256,
        })

    def rebuild_read_model(self) -> list[dict[str, Any]]:
        self.db.execute("DROP TABLE IF EXISTS task_read_model")
        self.db.execute(
            """CREATE TABLE task_read_model (
                task_id TEXT PRIMARY KEY, work_id TEXT NOT NULL, summary TEXT NOT NULL,
                routing_decision_sha256 TEXT NOT NULL, wip_buffer_sha256 TEXT,
                candidate_envelope_id TEXT, disposition TEXT NOT NULL
            )"""
        )
        buffers: dict[str, dict[str, Any]] = {}
        tasks: dict[str, dict[str, Any]] = {}
        envelopes: dict[str, dict[str, Any]] = {}
        for event in self._events():
            payload = event["payload"]
            if event["kind"] == "task_packet.created":
                tasks[payload["task_id"]] = {"work_id": payload["work_id"], "summary": payload["summary"],
                                               "routing_decision_sha256": payload["routing_receipt"]["decision_sha256"],
                                               "wip_buffer_sha256": None, "candidate_envelope_id": None, "disposition": "open"}
            elif event["kind"] == "worker_buffer.sealed":
                buffers[payload["buffer_id"]] = payload
                if payload["task_id"] in tasks:
                    tasks[payload["task_id"]]["wip_buffer_sha256"] = payload["buffer_sha256"]
            elif event["kind"] == "result_envelope.sealed":
                envelopes[payload["envelope_id"]] = payload
            elif event["kind"] == "candidate.admitted":
                task = tasks.get(payload["task_id"])
                if task is not None:
                    task["candidate_envelope_id"] = payload["envelope_id"]
                    task["disposition"] = payload["disposition"]
        for task_id, task in tasks.items():
            self.db.execute(
                "INSERT INTO task_read_model VALUES (?, ?, ?, ?, ?, ?, ?)",
                (task_id, task["work_id"], task["summary"], task["routing_decision_sha256"],
                 task["wip_buffer_sha256"], task["candidate_envelope_id"], task["disposition"]),
            )
        self.db.commit()
        return self.read_model()

    def read_model(self) -> list[dict[str, Any]]:
        try:
            rows = self.db.execute("SELECT * FROM task_read_model ORDER BY task_id").fetchall()
        except sqlite3.OperationalError:
            return []
        return [dict(row) for row in rows]

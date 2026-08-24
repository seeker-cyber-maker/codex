"""Synthetic test-only recovery ledger; no operational recovery authority."""
import hashlib
import json
import os
import re
import sqlite3
import stat
import tempfile
from collections.abc import Callable
from pathlib import Path
from . import recovery_policy as recovery
LEDGER_SCHEMA = "codex-house-synthetic-recovery-ledger/1"
RECEIPT_SCHEMA = "codex-house-synthetic-recovery-ledger-receipt/1"
CLAIM_CEILING = "SYNTHETIC_RECOVERY_LEDGER_LOCAL_TRANSACTION_ONLY"
APPLICATION_ID = 1_129_606_732
USER_VERSION = 1
MAX_ENTRIES = 64
MAX_INPUT_BYTES = 256 * 1024
MAX_STATE_BYTES = 1024 * 1024
MAX_RECEIPT_BYTES = 1024 * 1024
FIXTURE_PREFIX = "recovery-ledger-fixture-"
FILENAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,118}\.sqlite$")
RECEIPT_FIELDS = frozenset("""schema claim_ceiling authority dispatch hardware key_material
runtime_admission checkpoint_protection recovery_readiness outcome_source result code
submission_sha256 manifest_sha256 prior_state_sha256 next_state_sha256 original_receipt_sha256
reducer_receipt reducer_receipt_sha256 receipt_sha256""".split())
REDUCER_RECEIPT_FIELDS = frozenset("""schema claim_ceiling authority dispatch hardware
key_material runtime_admission result code manifest_sha256 prior_state_sha256
next_state_sha256 original_receipt_sha256 receipt_sha256""".split())
TABLE_COLUMNS = {
    "recovery_ledger_meta": tuple("singleton schema initial_state_json initial_state_sha256 "
        "genesis_sha256 current_state_sha256 event_head_sha256 entry_count".split()),
    "recovery_ledger_state": ("singleton", "state_json"),
    "recovery_ledger_entry": tuple("sequence submission_sha256 manifest_sha256 challenge_id "
        "request_json evidence_json decision_time prior_state_sha256 next_state_sha256 "
        "receipt_json previous_event_sha256 event_sha256".split()),
}
class RecoveryLedgerError(RuntimeError):
    """Typed refusal from the synthetic ledger boundary."""
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code
def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()
def _state_sha256(value: object, code: str) -> str:
    try:
        return recovery.semantic_state_sha256(value)
    except recovery.RecoveryPolicyError as exc:
        raise RecoveryLedgerError(code) from exc
def _event(row: object, receipt_sha256: str, previous: str) -> dict[str, object]:
    event = {key: row[key] for key in ("sequence", "submission_sha256",
        "manifest_sha256", "challenge_id", "decision_time", "prior_state_sha256",
        "next_state_sha256")}
    event.update(schema="codex-house-synthetic-recovery-ledger-event/1",
        request_sha256=_sha256_text(row["request_json"]),
        evidence_sha256=_sha256_text(row["evidence_json"]),
        receipt_sha256=receipt_sha256, previous_event_sha256=previous)
    return event
def _bounded_canonical(value: object, maximum: int, code: str) -> str:
    try:
        encoded = recovery.canonical(value)
    except recovery.RecoveryPolicyError as exc:
        raise RecoveryLedgerError(code) from exc
    if len(encoded.encode()) > maximum:
        raise RecoveryLedgerError(code)
    return encoded
def _decoded_canonical(value: object, maximum: int, code: str) -> object:
    if not isinstance(value, str) or len(value.encode()) > maximum:
        raise RecoveryLedgerError(code)
    try:
        decoded = json.loads(value)
    except (TypeError, ValueError) as exc:
        raise RecoveryLedgerError(code) from exc
    if recovery.canonical(decoded) != value:
        raise RecoveryLedgerError(code)
    return decoded
def _path_identity(path: Path, *, directory: bool) -> tuple[int, int]:
    try:
        observed = os.lstat(path)
    except OSError as exc:
        raise RecoveryLedgerError("PATH_IDENTITY") from exc
    expected = stat.S_ISDIR(observed.st_mode) if directory else stat.S_ISREG(observed.st_mode)
    if stat.S_ISLNK(observed.st_mode) or not expected:
        raise RecoveryLedgerError("PATH_IDENTITY")
    return observed.st_dev, observed.st_ino
def _fixture_path(
    fixture_root: str | Path, filename: str, *, must_exist: bool
) -> tuple[Path, tuple[int, int], tuple[int, int] | None]:
    raw_root = Path(fixture_root)
    _path_identity(raw_root, directory=True)
    try:
        root = raw_root.resolve(strict=True)
        root.relative_to(Path(tempfile.gettempdir()).resolve(strict=True))
    except (OSError, ValueError) as exc:
        raise RecoveryLedgerError("FIXTURE_ROOT") from exc
    if not root.name.startswith(FIXTURE_PREFIX):
        raise RecoveryLedgerError("FIXTURE_ROOT")
    if not isinstance(filename, str) or FILENAME_RE.fullmatch(filename) is None:
        raise RecoveryLedgerError("FIXTURE_NAME")
    root_identity = _path_identity(root, directory=True)
    path = root / filename
    exists = os.path.lexists(path)
    if exists != must_exist:
        raise RecoveryLedgerError("FIXTURE_EXISTENCE")
    database_identity = _path_identity(path, directory=False) if exists else None
    return path, root_identity, database_identity
def _manifest_challenge(request: object) -> str | None:
    if not isinstance(request, dict) or set(request) != recovery.MANIFEST_FIELDS:
        return None
    if request.get("schema") != recovery.MANIFEST_SCHEMA:
        return None
    try:
        recovery._validate_manifest(dict(request))
    except recovery.RecoveryPolicyError:
        return None
    return request["challenge_id"]
class RecoveryLedger:
    """One bounded synthetic SQLite fixture around the pure reducer."""
    def __init__(self, path: Path, root_identity: tuple[int, int],
        database_identity: tuple[int, int], connection: sqlite3.Connection,
        before_commit: Callable[[], None] | None) -> None:
        self.path = path
        self.root = path.parent
        self._root_identity = root_identity
        self._database_identity = database_identity
        self._db: sqlite3.Connection | None = connection
        self._before_commit = before_commit
    @classmethod
    def initialize(cls, fixture_root: str | Path, filename: str,
        initial_state: object, *, _before_commit: Callable[[], None] | None = None
        ) -> "RecoveryLedger":
        state_json = _bounded_canonical(initial_state, MAX_STATE_BYTES, "STATE_SIZE")
        state = json.loads(state_json)
        state_sha256 = _state_sha256(state, "INITIAL_STATE")
        genesis = recovery.sha256_json({"schema": LEDGER_SCHEMA,
            "initial_state_sha256": state_sha256})
        path, root_identity, _ = _fixture_path(fixture_root, filename, must_exist=False)
        connection = sqlite3.connect(path, timeout=5)
        connection.row_factory = sqlite3.Row
        try:
            database_identity = _path_identity(path, directory=False)
            if _path_identity(path.parent, directory=True) != root_identity:
                raise RecoveryLedgerError("PATH_IDENTITY")
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(f"PRAGMA application_id = {APPLICATION_ID}")
            connection.execute(f"PRAGMA user_version = {USER_VERSION}")
            connection.execute(
                "CREATE TABLE recovery_ledger_meta (singleton INTEGER PRIMARY KEY CHECK(singleton=1), schema TEXT NOT NULL, initial_state_json TEXT NOT NULL, initial_state_sha256 TEXT NOT NULL, genesis_sha256 TEXT NOT NULL, current_state_sha256 TEXT NOT NULL, event_head_sha256 TEXT NOT NULL, entry_count INTEGER NOT NULL)"
            )
            connection.execute(
                "CREATE TABLE recovery_ledger_state (singleton INTEGER PRIMARY KEY CHECK(singleton=1), state_json TEXT NOT NULL)"
            )
            connection.execute(
                "CREATE TABLE recovery_ledger_entry (sequence INTEGER PRIMARY KEY, submission_sha256 TEXT NOT NULL UNIQUE, manifest_sha256 TEXT NOT NULL, challenge_id TEXT, request_json TEXT NOT NULL, evidence_json TEXT NOT NULL, decision_time INTEGER NOT NULL, prior_state_sha256 TEXT NOT NULL, next_state_sha256 TEXT NOT NULL, receipt_json TEXT NOT NULL, previous_event_sha256 TEXT NOT NULL, event_sha256 TEXT NOT NULL UNIQUE)"
            )
            connection.execute(
                "INSERT INTO recovery_ledger_meta VALUES (1, ?, ?, ?, ?, ?, ?, 0)",
                (LEDGER_SCHEMA, state_json, state_sha256, genesis, state_sha256, genesis),
            )
            connection.execute(
                "INSERT INTO recovery_ledger_state VALUES (1, ?)", (state_json,)
            )
            connection.commit()
            ledger = cls(path, root_identity, database_identity, connection, _before_commit)
            ledger._assert_path_identity()
            ledger._verify_integrity(semantic_replay=False)
            return ledger
        except Exception:
            connection.rollback()
            connection.close()
            raise
    @classmethod
    def reopen(cls, fixture_root: str | Path, filename: str, *,
        _before_commit: Callable[[], None] | None = None) -> "RecoveryLedger":
        path, root_identity, database_identity = _fixture_path(
            fixture_root, filename, must_exist=True)
        connection = sqlite3.connect(f"{path.resolve().as_uri()}?mode=rw", uri=True, timeout=5)
        connection.row_factory = sqlite3.Row
        ledger = cls(path, root_identity, database_identity, connection, _before_commit)
        try:
            ledger._assert_path_identity()
            ledger._verify_integrity(semantic_replay=True)
            ledger._assert_path_identity()
            return ledger
        except Exception:
            connection.close()
            raise
    def close(self) -> None:
        if self._db is not None:
            self._db.close()
            self._db = None
    def apply(self, request: object, evidence: object,
        decision_time: object) -> dict[str, object]:
        request_json = _bounded_canonical(request, MAX_INPUT_BYTES, "REQUEST_SIZE")
        evidence_json = _bounded_canonical(evidence, MAX_INPUT_BYTES, "EVIDENCE_SIZE")
        submission = {
            "request": json.loads(request_json),
            "evidence": json.loads(evidence_json),
            "decision_time": decision_time,
        }
        submission_sha256 = recovery.sha256_json(submission)
        manifest_sha256 = recovery.sha256_json(submission["request"])
        challenge_id = _manifest_challenge(submission["request"])
        self._assert_path_identity()
        db = self._require_open()
        db.execute("BEGIN IMMEDIATE")
        try:
            state, meta, entries = self._verify_integrity(semantic_replay=False)
            prior_sha256 = meta["current_state_sha256"]
            exact = next(
                (row for row in entries if row["submission_sha256"] == submission_sha256),
                None,
            )
            if exact is not None:
                db.commit()
                return json.loads(exact["receipt_json"])
            if challenge_id is not None and any(
                row["challenge_id"] == challenge_id
                and row["manifest_sha256"] != manifest_sha256
                for row in entries
            ):
                receipt = self._receipt(
                    "ADAPTER_CONFLICT", "REFUSED", "CHALLENGE_CONFLICT",
                    submission_sha256, manifest_sha256, prior_sha256, None, None
                )
                db.commit()
                return receipt
            if any(
                row["manifest_sha256"] == manifest_sha256
                and row["submission_sha256"] != submission_sha256
                for row in entries
            ):
                receipt = self._receipt(
                    "ADAPTER_CONFLICT", "REFUSED", "SUBMISSION_CONFLICT",
                    submission_sha256, manifest_sha256, prior_sha256, None, None
                )
                db.commit()
                return receipt
            next_state, reducer_receipt = recovery.verify_transition(
                state, submission["request"], submission["evidence"], decision_time
            )
            next_sha256 = None
            source = "REDUCER"
            if next_state is not None:
                next_sha256 = _state_sha256(next_state, "NEXT_STATE")
                source = "STORED_ACCEPTED"
            receipt = self._receipt(
                source,
                reducer_receipt["result"],
                reducer_receipt["code"],
                submission_sha256,
                manifest_sha256,
                prior_sha256,
                next_sha256,
                reducer_receipt,
            )
            if next_state is None:
                db.commit()
                return receipt
            if meta["entry_count"] >= MAX_ENTRIES:
                raise RecoveryLedgerError("ENTRY_LIMIT")
            receipt_json = _bounded_canonical(receipt, MAX_RECEIPT_BYTES, "RECEIPT_SIZE")
            next_state_json = _bounded_canonical(next_state, MAX_STATE_BYTES, "STATE_SIZE")
            sequence = meta["entry_count"] + 1
            event_row = {"sequence": sequence, "submission_sha256": submission_sha256,
                "manifest_sha256": manifest_sha256, "challenge_id": challenge_id,
                "request_json": request_json, "evidence_json": evidence_json,
                "decision_time": decision_time, "prior_state_sha256": prior_sha256,
                "next_state_sha256": next_sha256}
            event = _event(event_row, receipt["receipt_sha256"], meta["event_head_sha256"])
            event_sha256 = recovery.sha256_json(event)
            db.execute(
                "INSERT INTO recovery_ledger_entry VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    sequence, submission_sha256, manifest_sha256, challenge_id,
                    request_json, evidence_json, decision_time, prior_sha256,
                    next_sha256, receipt_json, meta["event_head_sha256"], event_sha256,
                ),
            )
            db.execute(
                "UPDATE recovery_ledger_state SET state_json=? WHERE singleton=1",
                (next_state_json,),
            )
            db.execute(
                "UPDATE recovery_ledger_meta SET current_state_sha256=?, event_head_sha256=?, entry_count=? WHERE singleton=1",
                (next_sha256, event_sha256, sequence),
            )
            if self._before_commit is not None:
                self._before_commit()
            db.commit()
            self._assert_path_identity()
            stored = db.execute(
                "SELECT receipt_json FROM recovery_ledger_entry WHERE submission_sha256=?",
                (submission_sha256,),
            ).fetchone()
            return json.loads(stored["receipt_json"])
        except Exception as exc:
            db.rollback()
            self._assert_path_identity()
            if isinstance(exc, RecoveryLedgerError):
                raise
            raise RecoveryLedgerError("TRANSACTION_ABORTED") from exc
    def _receipt(self, source: str, result: str, code: str,
        submission_sha256: str, manifest_sha256: str, prior_state_sha256: str,
        next_state_sha256: str | None,
        reducer_receipt: dict[str, object] | None) -> dict[str, object]:
        reducer_digest = (
            None if reducer_receipt is None else recovery.sha256_json(reducer_receipt)
        )
        unsigned = {
            "schema": RECEIPT_SCHEMA,
            "claim_ceiling": CLAIM_CEILING,
            "authority": "NOT_GRANTED",
            "dispatch": "NOT_ATTEMPTED",
            "hardware": "NOT_ACCESSED",
            "key_material": "NOT_ACCESSED",
            "runtime_admission": "NOT_ATTEMPTED",
            "checkpoint_protection": "NOT_ESTABLISHED",
            "recovery_readiness": "NOT_ESTABLISHED",
            "outcome_source": source,
            "result": result,
            "code": code,
            "submission_sha256": submission_sha256,
            "manifest_sha256": manifest_sha256,
            "prior_state_sha256": prior_state_sha256,
            "next_state_sha256": next_state_sha256,
            "original_receipt_sha256": None
            if reducer_receipt is None
            else reducer_receipt["original_receipt_sha256"],
            "reducer_receipt": reducer_receipt,
            "reducer_receipt_sha256": reducer_digest,
        }
        return {**unsigned, "receipt_sha256": recovery.sha256_json(unsigned)}
    def _verify_integrity(self, *, semantic_replay: bool
        ) -> tuple[dict[str, object], sqlite3.Row, list[sqlite3.Row]]:
        db = self._require_open()
        if db.execute("PRAGMA application_id").fetchone()[0] != APPLICATION_ID:
            raise RecoveryLedgerError("DATABASE_SCHEMA")
        if db.execute("PRAGMA user_version").fetchone()[0] != USER_VERSION:
            raise RecoveryLedgerError("DATABASE_SCHEMA")
        tables = {
            row[0]
            for row in db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
        }
        if tables != set(TABLE_COLUMNS):
            raise RecoveryLedgerError("DATABASE_SCHEMA")
        for table, expected in TABLE_COLUMNS.items():
            columns = tuple(row[1] for row in db.execute(f"PRAGMA table_info({table})"))
            if columns != expected:
                raise RecoveryLedgerError("DATABASE_SCHEMA")
        meta_rows = db.execute("SELECT * FROM recovery_ledger_meta").fetchall()
        state_rows = db.execute("SELECT * FROM recovery_ledger_state").fetchall()
        if len(meta_rows) != 1 or len(state_rows) != 1:
            raise RecoveryLedgerError("DATABASE_INTEGRITY")
        meta = meta_rows[0]
        if meta["singleton"] != 1 or meta["schema"] != LEDGER_SCHEMA:
            raise RecoveryLedgerError("DATABASE_INTEGRITY")
        initial = _decoded_canonical(meta["initial_state_json"], MAX_STATE_BYTES, "INITIAL_STATE")
        initial_sha256 = _state_sha256(initial, "INITIAL_STATE")
        genesis = recovery.sha256_json(
            {"schema": LEDGER_SCHEMA, "initial_state_sha256": initial_sha256}
        )
        if meta["initial_state_sha256"] != initial_sha256 or meta["genesis_sha256"] != genesis:
            raise RecoveryLedgerError("INITIAL_STATE")
        state = _decoded_canonical(state_rows[0]["state_json"], MAX_STATE_BYTES, "CURRENT_STATE")
        if _state_sha256(state, "CURRENT_STATE") != meta["current_state_sha256"]:
            raise RecoveryLedgerError("CURRENT_STATE")
        count = meta["entry_count"]
        if isinstance(count, bool) or not isinstance(count, int) or not 0 <= count <= MAX_ENTRIES:
            raise RecoveryLedgerError("ENTRY_COUNT")
        entries = db.execute(
            "SELECT * FROM recovery_ledger_entry ORDER BY sequence"
        ).fetchall()
        if len(entries) != count:
            raise RecoveryLedgerError("ENTRY_COUNT")
        previous = genesis
        replay_state = initial
        for expected_sequence, row in enumerate(entries, 1):
            if row["sequence"] != expected_sequence or row["previous_event_sha256"] != previous:
                raise RecoveryLedgerError("EVENT_CHAIN")
            request = _decoded_canonical(row["request_json"], MAX_INPUT_BYTES, "ENTRY_INPUT")
            evidence = _decoded_canonical(row["evidence_json"], MAX_INPUT_BYTES, "ENTRY_INPUT")
            receipt = _decoded_canonical(row["receipt_json"], MAX_RECEIPT_BYTES, "ENTRY_RECEIPT")
            self._verify_receipt(receipt, stored_accepted=True)
            submission = {"request": request, "evidence": evidence, "decision_time": row["decision_time"]}
            if (
                row["submission_sha256"] != recovery.sha256_json(submission)
                or row["manifest_sha256"] != recovery.sha256_json(request)
                or row["challenge_id"] != _manifest_challenge(request)
                or receipt["submission_sha256"] != row["submission_sha256"]
                or receipt["manifest_sha256"] != row["manifest_sha256"]
                or receipt["prior_state_sha256"] != row["prior_state_sha256"]
                or receipt["next_state_sha256"] != row["next_state_sha256"]
            ):
                raise RecoveryLedgerError("ENTRY_BINDING")
            event = _event(row, receipt["receipt_sha256"], previous)
            if recovery.sha256_json(event) != row["event_sha256"]:
                raise RecoveryLedgerError("EVENT_CHAIN")
            if semantic_replay:
                next_state, reducer_receipt = recovery.verify_transition(
                    replay_state, request, evidence, row["decision_time"]
                )
                if (
                    next_state is None
                    or receipt["reducer_receipt"] != reducer_receipt
                    or row["prior_state_sha256"] != _state_sha256(replay_state, "SEMANTIC_REPLAY")
                    or row["next_state_sha256"] != _state_sha256(next_state, "SEMANTIC_REPLAY")
                ):
                    raise RecoveryLedgerError("SEMANTIC_REPLAY")
                replay_state = next_state
            previous = row["event_sha256"]
        expected_head = genesis if count == 0 else previous
        expected_current = initial_sha256 if count == 0 else entries[-1]["next_state_sha256"]
        if meta["event_head_sha256"] != expected_head or meta["current_state_sha256"] != expected_current:
            raise RecoveryLedgerError("DATABASE_INTEGRITY")
        if semantic_replay and recovery.canonical(replay_state) != recovery.canonical(state):
            raise RecoveryLedgerError("SEMANTIC_REPLAY")
        return state, meta, entries
    def _verify_receipt(self, value: object, *, stored_accepted: bool) -> None:
        if not isinstance(value, dict) or set(value) != RECEIPT_FIELDS:
            raise RecoveryLedgerError("ENTRY_RECEIPT")
        unsigned = {key: value[key] for key in RECEIPT_FIELDS - {"receipt_sha256"}}
        if recovery.sha256_json(unsigned) != value["receipt_sha256"]:
            raise RecoveryLedgerError("ENTRY_RECEIPT")
        fixed = {
            "schema": RECEIPT_SCHEMA,
            "claim_ceiling": CLAIM_CEILING,
            "authority": "NOT_GRANTED",
            "dispatch": "NOT_ATTEMPTED",
            "hardware": "NOT_ACCESSED",
            "key_material": "NOT_ACCESSED",
            "runtime_admission": "NOT_ATTEMPTED",
            "checkpoint_protection": "NOT_ESTABLISHED",
            "recovery_readiness": "NOT_ESTABLISHED",
        }
        if any(value[key] != expected for key, expected in fixed.items()):
            raise RecoveryLedgerError("ENTRY_RECEIPT")
        nested = value["reducer_receipt"]
        if not isinstance(nested, dict) or set(nested) != REDUCER_RECEIPT_FIELDS:
            raise RecoveryLedgerError("ENTRY_RECEIPT")
        nested_unsigned = {key: item for key, item in nested.items() if key != "receipt_sha256"}
        if (
            recovery.sha256_json(nested) != value["reducer_receipt_sha256"]
            or recovery.sha256_json(nested_unsigned) != nested["receipt_sha256"]
            or nested["schema"] != recovery.RESULT_SCHEMA
            or nested["claim_ceiling"] != recovery.CLAIM_CEILING
            or nested["authority"] != "NOT_GRANTED"
            or nested["dispatch"] != "NOT_ATTEMPTED"
            or nested["hardware"] != "NOT_ACCESSED"
            or nested["key_material"] != "NOT_ACCESSED"
            or nested["runtime_admission"] != "NOT_ATTEMPTED"
            or nested["result"] != "ACCEPTED" or nested["code"] != "OK"
            or nested["original_receipt_sha256"] is not None
            or any(nested[key] != value[key] for key in
                ("manifest_sha256", "prior_state_sha256", "next_state_sha256"))
            or value["original_receipt_sha256"] is not None
        ):
            raise RecoveryLedgerError("ENTRY_RECEIPT")
        if stored_accepted and (
            value["outcome_source"] != "STORED_ACCEPTED"
            or value["result"] != "ACCEPTED"
            or value["code"] != "OK"
            or nested is None
        ):
            raise RecoveryLedgerError("ENTRY_RECEIPT")
    def _assert_path_identity(self) -> None:
        if _path_identity(self.root, directory=True) != self._root_identity:
            raise RecoveryLedgerError("PATH_IDENTITY")
        if _path_identity(self.path, directory=False) != self._database_identity:
            raise RecoveryLedgerError("PATH_IDENTITY")
    def _require_open(self) -> sqlite3.Connection:
        if self._db is None:
            raise RecoveryLedgerError("CLOSED")
        return self._db

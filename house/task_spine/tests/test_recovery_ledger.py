import ast
import json
import os
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch
from house.task_spine import recovery_ledger as ledger_module
from house.task_spine import recovery_policy as recovery
from house.task_spine.tests.test_recovery_policy import (
    digest,
    evidence,
    initial_state,
    lockdown_request,
    manifest,
)
def submission_sha256(request: object, supplied_evidence: object, decision_time: object) -> str:
    return recovery.sha256_json(
        {"request": request, "evidence": supplied_evidence, "decision_time": decision_time}
    )
def outer_receipt(state: dict[str, object], request: object, supplied_evidence: object,
    decision_time: object, source: str, result: str, code: str,
    next_state_sha256: str | None,
    reducer_receipt: dict[str, object] | None) -> dict[str, object]:
    unsigned = {
        "schema": ledger_module.RECEIPT_SCHEMA,
        "claim_ceiling": ledger_module.CLAIM_CEILING,
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
        "submission_sha256": submission_sha256(request, supplied_evidence, decision_time),
        "manifest_sha256": recovery.sha256_json(request),
        "prior_state_sha256": recovery.semantic_state_sha256(state),
        "next_state_sha256": next_state_sha256,
        "original_receipt_sha256": None if reducer_receipt is None else reducer_receipt["original_receipt_sha256"],
        "reducer_receipt": reducer_receipt,
        "reducer_receipt_sha256": None if reducer_receipt is None else recovery.sha256_json(reducer_receipt),
    }
    return {**unsigned, "receipt_sha256": recovery.sha256_json(unsigned)}
def logical_snapshot(path: Path) -> dict[str, list[list[object]]]:
    with closing(sqlite3.connect(path)) as db:
        return {
            table: [list(row) for row in db.execute(f"SELECT * FROM {table} ORDER BY 1")]
            for table in ledger_module.TABLE_COLUMNS
        }
class RecoveryLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix=ledger_module.FIXTURE_PREFIX)
        self.root = Path(self.temporary.name)
    def tearDown(self) -> None:
        self.temporary.cleanup()
    def new(self, name: str = "ledger.sqlite", **kwargs: object) -> ledger_module.RecoveryLedger:
        return ledger_module.RecoveryLedger.initialize(
            self.root, name, initial_state(), **kwargs
        )
    @staticmethod
    def state(ledger: ledger_module.RecoveryLedger) -> dict[str, object]:
        row = ledger._require_open().execute(
            "SELECT state_json FROM recovery_ledger_state WHERE singleton=1"
        ).fetchone()
        return json.loads(row["state_json"])
    def assert_accept(
        self,
        ledger: ledger_module.RecoveryLedger,
        request: dict[str, object],
        supplied_evidence: object,
    ) -> dict[str, object]:
        state = self.state(ledger)
        next_state, inner = recovery.verify_transition(
            state, request, supplied_evidence, 120
        )
        self.assertIsNotNone(next_state)
        expected = outer_receipt(state, request, supplied_evidence, 120,
            "STORED_ACCEPTED", "ACCEPTED", "OK",
            recovery.semantic_state_sha256(next_state), inner)
        self.assertEqual(ledger.apply(request, supplied_evidence, 120), expected)
        return expected
    def accept_action(self, ledger: ledger_module.RecoveryLedger, action: str,
        challenge: str, *, replacement: bool = False, **changes: object) -> None:
        request = manifest(self.state(ledger), action, challenge, **changes)
        self.assert_accept(ledger, request, evidence(request, replacement=replacement))
    def test_complete_sequence_reopen_and_exact_duplicate(self) -> None:
        ledger = self.new()
        request = lockdown_request(self.state(ledger))
        first = self.assert_accept(ledger, request, None)
        with patch.object(
            ledger_module.recovery,
            "verify_transition",
            side_effect=AssertionError("duplicate called reducer"),
        ):
            self.assertEqual(ledger.apply(request, None, 120), first)
        self.accept_action(ledger, recovery.SUSPEND_PRIMARY, "challenge-suspend-ledger")
        replacement = {"replacement_key_id": "p256:replacement-fixture", "replacement_epoch": 2}
        self.accept_action(ledger, recovery.RECOVER_PRIMARY, "challenge-recover-ledger",
            replacement=True, **replacement)
        self.accept_action(ledger, recovery.CHECKPOINT_SIGN, "challenge-checkpoint-ledger",
            new_checkpoint_sha256=digest("4"))
        self.accept_action(ledger, recovery.REVOKE_PRIMARY, "challenge-revoke-ledger",
            tombstone_sha256=digest("5"))
        self.accept_action(ledger, recovery.LOCKDOWN_EXIT, "challenge-exit-ledger", **replacement)
        before = logical_snapshot(ledger.path)
        ledger.close()
        reopened = ledger_module.RecoveryLedger.reopen(self.root, "ledger.sqlite")
        self.assertEqual(logical_snapshot(reopened.path), before)
        self.assertEqual(self.state(reopened)["mode"], "ACTIVE")
        reopened.close()
    def test_conflicts_are_adapter_receipts_and_do_not_write_or_call_reducer(self) -> None:
        ledger = self.new()
        self.assert_accept(ledger, lockdown_request(self.state(ledger)), None)
        state = self.state(ledger)
        request = manifest(state, recovery.SUSPEND_PRIMARY, "challenge-conflict-ledger")
        supplied = evidence(request)
        self.assert_accept(ledger, request, supplied)
        before = logical_snapshot(ledger.path)
        conflicting = dict(request)
        conflicting["package_qualification_sha256"] = digest("9")
        conflict_evidence = evidence(conflicting)
        expected = outer_receipt(
            self.state(ledger), conflicting, conflict_evidence, 120,
            "ADAPTER_CONFLICT", "REFUSED", "CHALLENGE_CONFLICT", None, None
        )
        with patch.object(
            ledger_module.recovery, "verify_transition", side_effect=AssertionError
        ):
            self.assertEqual(ledger.apply(conflicting, conflict_evidence, 120), expected)
            expected = outer_receipt(
                self.state(ledger), request, supplied, 121,
                "ADAPTER_CONFLICT", "REFUSED", "SUBMISSION_CONFLICT", None, None
            )
            self.assertEqual(ledger.apply(request, supplied, 121), expected)
        self.assertEqual(logical_snapshot(ledger.path), before)
        ledger.close()
    def test_reducer_refusal_and_replay_are_nested_uncached_and_nonmutating(self) -> None:
        ledger = self.new()
        request = lockdown_request(self.state(ledger))
        before = logical_snapshot(ledger.path)
        _, inner = recovery.verify_transition(initial_state(), request, None, True)
        expected = outer_receipt(
            initial_state(), request, None, True, "REDUCER",
            inner["result"], inner["code"], None, inner
        )
        original = ledger_module.recovery.verify_transition
        with patch.object(ledger_module.recovery, "verify_transition", wraps=original) as called:
            self.assertEqual(ledger.apply(request, None, True), expected)
            self.assertEqual(ledger.apply(request, None, True), expected)
            self.assertEqual(called.call_count, 2)
        self.assertEqual(logical_snapshot(ledger.path), before)
        ledger.close()
        state, _ = recovery.verify_transition(initial_state(), lockdown_request(initial_state()), None, 120)
        replay_request = manifest(state, recovery.SUSPEND_PRIMARY, "challenge-preconsumed")
        replay_evidence = evidence(replay_request)
        consumed, accepted = recovery.verify_transition(
            state, replay_request, replay_evidence, 120
        )
        replay_ledger = ledger_module.RecoveryLedger.initialize(
            self.root, "replay.sqlite", consumed
        )
        _, inner = recovery.verify_transition(consumed, replay_request, replay_evidence, 120)
        self.assertEqual(inner["original_receipt_sha256"], accepted["receipt_sha256"])
        expected = outer_receipt(
            consumed, replay_request, replay_evidence, 120, "REDUCER",
            "REPLAY", "ALREADY_CONSUMED", None, inner
        )
        self.assertEqual(replay_ledger.apply(replay_request, replay_evidence, 120), expected)
        self.assertEqual(logical_snapshot(replay_ledger.path)["recovery_ledger_entry"], [])
        replay_ledger.close()
    def test_precommit_fault_rolls_back_and_entry_cap_fails_closed(self) -> None:
        calls = 0
        def fail_once() -> None:
            nonlocal calls
            calls += 1
            if calls == 1:
                raise RuntimeError("synthetic interruption")
        ledger = self.new(_before_commit=fail_once)
        before = logical_snapshot(ledger.path)
        request = lockdown_request(self.state(ledger))
        with self.assertRaisesRegex(ledger_module.RecoveryLedgerError, "TRANSACTION_ABORTED"):
            ledger.apply(request, None, 120)
        self.assertEqual(logical_snapshot(ledger.path), before)
        self.assertEqual(ledger.apply(request, None, 120)["result"], "ACCEPTED")
        ledger.close()
        limited = self.new("limited.sqlite")
        before = logical_snapshot(limited.path)
        with patch.object(ledger_module, "MAX_ENTRIES", 0):
            with self.assertRaisesRegex(ledger_module.RecoveryLedgerError, "ENTRY_LIMIT"):
                limited.apply(lockdown_request(self.state(limited)), None, 120)
        self.assertEqual(logical_snapshot(limited.path), before)
        limited.close()
    def test_corruption_fails_reopen_without_repair(self) -> None:
        corruptions = {
            "initial_json": "UPDATE recovery_ledger_meta SET initial_state_json='{}'",
            "initial_digest": f"UPDATE recovery_ledger_meta SET initial_state_sha256='{digest('0')}'",
            "genesis": f"UPDATE recovery_ledger_meta SET genesis_sha256='{digest('0')}'",
            "meta": "UPDATE recovery_ledger_meta SET entry_count=2",
            "current_state": "UPDATE recovery_ledger_state SET state_json='{}'",
            "sequence": "UPDATE recovery_ledger_entry SET sequence=2",
            "event_link": f"UPDATE recovery_ledger_entry SET previous_event_sha256='{digest('0')}'",
            "event_digest": f"UPDATE recovery_ledger_entry SET event_sha256='{digest('0')}'",
            "receipt": "UPDATE recovery_ledger_entry SET receipt_json='{}'",
            "nested_receipt_digest": "UPDATE recovery_ledger_entry SET receipt_json=json_set(receipt_json, '$.reducer_receipt_sha256', 'broken')",
        }
        for index, (label, statement) in enumerate(corruptions.items()):
            with self.subTest(label=label):
                name = f"corrupt-{index}.sqlite"
                ledger = self.new(name)
                self.assert_accept(ledger, lockdown_request(self.state(ledger)), None)
                ledger.close()
                with closing(sqlite3.connect(self.root / name)) as db:
                    db.execute(statement); db.commit()
                before = logical_snapshot(self.root / name)
                with self.assertRaises(ledger_module.RecoveryLedgerError):
                    ledger_module.RecoveryLedger.reopen(self.root, name)
                self.assertEqual(logical_snapshot(self.root / name), before)
        ledger = self.new("semantic-drift.sqlite")
        self.assert_accept(ledger, lockdown_request(self.state(ledger)), None)
        ledger.close()
        original = ledger_module.recovery.verify_transition
        def drift(*args: object) -> tuple[dict[str, object], dict[str, object]]:
            _, receipt = original(*args)
            return initial_state(), receipt
        with patch.object(ledger_module.recovery, "verify_transition", side_effect=drift):
            with self.assertRaisesRegex(ledger_module.RecoveryLedgerError, "SEMANTIC_REPLAY"):
                ledger_module.RecoveryLedger.reopen(self.root, "semantic-drift.sqlite")
    def test_coherent_nested_receipt_substitution_fails_closed(self) -> None:
        ledger = self.new("coherent-substitution.sqlite")
        request = lockdown_request(self.state(ledger))
        self.assert_accept(ledger, request, None)
        with closing(sqlite3.connect(ledger.path)) as db:
            db.row_factory = sqlite3.Row
            row = db.execute("SELECT * FROM recovery_ledger_entry").fetchone()
            receipt = json.loads(row["receipt_json"])
            nested = receipt["reducer_receipt"]
            nested["code"] = "FORGED"
            nested["receipt_sha256"] = recovery.sha256_json(
                {key: value for key, value in nested.items() if key != "receipt_sha256"})
            receipt["reducer_receipt_sha256"] = recovery.sha256_json(nested)
            receipt["receipt_sha256"] = recovery.sha256_json(
                {key: value for key, value in receipt.items() if key != "receipt_sha256"})
            receipt_json = recovery.canonical(receipt)
            event_sha256 = recovery.sha256_json(ledger_module._event(
                row, receipt["receipt_sha256"], row["previous_event_sha256"]))
            db.execute("UPDATE recovery_ledger_entry SET receipt_json=?, event_sha256=?",
                (receipt_json, event_sha256)); db.commit()
        before = logical_snapshot(ledger.path)
        with patch.object(ledger_module.recovery, "verify_transition", side_effect=AssertionError):
            with self.assertRaisesRegex(ledger_module.RecoveryLedgerError, "ENTRY_RECEIPT"):
                ledger.apply(request, None, 120)
        self.assertEqual(logical_snapshot(ledger.path), before)
        ledger.close()
        with self.assertRaisesRegex(ledger_module.RecoveryLedgerError, "ENTRY_RECEIPT"):
            ledger_module.RecoveryLedger.reopen(self.root, "coherent-substitution.sqlite")
    def test_paths_sizes_and_source_graph_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="wrong-prefix-") as wrong:
            with self.assertRaisesRegex(ledger_module.RecoveryLedgerError, "FIXTURE_ROOT"):
                ledger_module.RecoveryLedger.initialize(wrong, "x.sqlite", initial_state())
        with self.assertRaisesRegex(ledger_module.RecoveryLedgerError, "FIXTURE_NAME"):
            ledger_module.RecoveryLedger.initialize(self.root, "../x.sqlite", initial_state())
        ledger = self.new()
        with self.assertRaisesRegex(ledger_module.RecoveryLedgerError, "FIXTURE_EXISTENCE"):
            ledger_module.RecoveryLedger.initialize(self.root, "ledger.sqlite", initial_state())
        before = logical_snapshot(ledger.path)
        with self.assertRaisesRegex(ledger_module.RecoveryLedgerError, "EVIDENCE_SIZE"):
            ledger.apply(lockdown_request(self.state(ledger)), "x" * (ledger_module.MAX_INPUT_BYTES + 1), 120)
        self.assertEqual(logical_snapshot(ledger.path), before)
        ledger.close()
        with self.assertRaisesRegex(ledger_module.RecoveryLedgerError, "FIXTURE_EXISTENCE"):
            ledger_module.RecoveryLedger.reopen(self.root, "missing.sqlite")
        symlink = self.root.parent / f"{ledger_module.FIXTURE_PREFIX}symlink"
        try:
            os.symlink(self.root, symlink)
            with self.assertRaises(ledger_module.RecoveryLedgerError):
                ledger_module.RecoveryLedger.initialize(symlink, "x.sqlite", initial_state())
        finally:
            if os.path.lexists(symlink):
                os.unlink(symlink)
        ledger = self.new("identity.sqlite")
        request = lockdown_request(self.state(ledger))
        os.rename(ledger.path, ledger.path.with_suffix(".moved"))
        ledger.path.touch()
        with self.assertRaisesRegex(ledger_module.RecoveryLedgerError, "PATH_IDENTITY"):
            ledger.apply(request, None, 120)
        ledger.close()
        module_path = Path(ledger_module.__file__).resolve()
        tree = ast.parse(module_path.read_text())
        allowed = {None, "hashlib", "json", "os", "re", "sqlite3", "stat", "tempfile", "contextlib", "collections.abc", "pathlib"}
        observed = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                observed.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                observed.add(node.module)
                if node.module is None:
                    self.assertEqual([alias.name for alias in node.names], ["recovery_policy"])
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                self.assertNotIn(node.func.id, {"eval", "exec", "compile", "__import__", "open"})
        self.assertTrue(observed <= allowed)
        house_root = module_path.parents[1]
        for candidate in house_root.rglob("*.py"):
            if candidate.resolve() in {module_path, Path(__file__).resolve()}:
                continue
            self.assertNotIn("recovery_ledger", candidate.read_text())
        self.assertLessEqual(
            len(module_path.read_text().splitlines()) + len(Path(__file__).read_text().splitlines()),
            800,
        )
if __name__ == "__main__":
    unittest.main()

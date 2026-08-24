from __future__ import annotations

import ast
import json
import unittest
from pathlib import Path

from house.task_spine import recovery_policy as recovery


def digest(letter: str) -> str:
    return letter * 64


def initial_state() -> dict[str, object]:
    return {
        "schema": recovery.STATE_SCHEMA,
        "registry_id": "registry-fixture",
        "generation": 1,
        "mode": "ACTIVE",
        "ceremony_parent_sha256": None,
        "fencing_epoch": 7,
        "journal_head_sha256": digest("a"),
        "checkpoint_sha256": digest("b"),
        "source_sha256": digest("c"),
        "policy_sha256": digest("d"),
        "protective_rule_sha256": digest("e"),
        "primary_key_id": "p256:primary-fixture",
        "primary_epoch": 1,
        "primary_status": "ACTIVE",
        "recovery_key_id": "p256:recovery-fixture",
        "recovery_epoch": 3,
        "recovery_status": "ACTIVE",
        "replacement_key_id": None,
        "replacement_epoch": None,
        "replacement_status": "NONE",
        "quarantine_sha256": digest("f"),
        "tombstone_sha256": None,
        "retired_primary_key_id": None,
        "retired_primary_epoch": None,
        "consumed_challenges": {},
    }


def lockdown_request(state: dict[str, object]) -> dict[str, object]:
    return {
        "schema": recovery.LOCKDOWN_SCHEMA,
        "action": recovery.LOCKDOWN_ENTER,
        "registry_id": state["registry_id"],
        "generation": state["generation"],
        "fencing_epoch": state["fencing_epoch"],
        "journal_head_sha256": state["journal_head_sha256"],
        "checkpoint_sha256": state["checkpoint_sha256"],
        "source_sha256": state["source_sha256"],
        "policy_sha256": state["policy_sha256"],
        "protective_rule_sha256": state["protective_rule_sha256"],
        "reason": "sole primary key reported lost",
        "default_state": "REMAIN_LOCKED",
    }


def manifest(
    state: dict[str, object],
    action: str,
    challenge_id: str,
    *,
    replacement_key_id: str | None = None,
    replacement_epoch: int | None = None,
    new_checkpoint_sha256: str | None = None,
    tombstone_sha256: str | None = None,
) -> dict[str, object]:
    signer_key_id = state["recovery_key_id"]
    signer_epoch = state["recovery_epoch"]
    if action == recovery.LOCKDOWN_EXIT:
        signer_key_id = state["replacement_key_id"]
        signer_epoch = state["replacement_epoch"]
    return {
        "schema": recovery.MANIFEST_SCHEMA,
        "action": action,
        "registry_id": state["registry_id"],
        "generation": state["generation"],
        "ceremony_id": "sole-key-recovery-fixture",
        "ceremony_parent_sha256": digest("1"),
        "fencing_epoch": state["fencing_epoch"],
        "signer_key_id": signer_key_id,
        "signer_epoch": signer_epoch,
        "old_primary_key_id": state["primary_key_id"],
        "old_primary_epoch": state["primary_epoch"],
        "expected_mode": state["mode"],
        "replacement_key_id": replacement_key_id,
        "replacement_epoch": replacement_epoch,
        "pending_intents_sha256": digest("2"),
        "source_sha256": state["source_sha256"],
        "policy_sha256": state["policy_sha256"],
        "checkpoint_sha256": state["checkpoint_sha256"],
        "new_checkpoint_sha256": new_checkpoint_sha256,
        "journal_head_sha256": state["journal_head_sha256"],
        "challenge_id": challenge_id,
        "issued_at": 100,
        "expires_at": 160,
        "default_state": "REMAIN_LOCKED",
        "package_qualification_sha256": digest("3"),
        "recovery_copy_id": "copy-fixture-a",
        "tombstone_sha256": tombstone_sha256,
    }


def evidence(request: dict[str, object], *, replacement: bool = False) -> dict[str, object]:
    return {
        "schema": recovery.EVIDENCE_SCHEMA,
        "manifest_sha256": recovery.sha256_json(request),
        "signature_verified": True,
        "signer_key_id": request["signer_key_id"],
        "signer_epoch": request["signer_epoch"],
        "replacement_possession_verified": replacement,
        "replacement_key_id": request["replacement_key_id"] if replacement else None,
        "replacement_epoch": request["replacement_epoch"] if replacement else None,
    }


def expected_receipt(
    *,
    result: str,
    code: str,
    request: object,
    prior_state: dict[str, object],
    next_state_sha256: str | None,
    original_receipt_sha256: str | None,
) -> dict[str, object]:
    unsigned = {
        "schema": recovery.RESULT_SCHEMA,
        "claim_ceiling": recovery.CLAIM_CEILING,
        "authority": "NOT_GRANTED",
        "dispatch": "NOT_ATTEMPTED",
        "hardware": "NOT_ACCESSED",
        "key_material": "NOT_ACCESSED",
        "runtime_admission": "NOT_ATTEMPTED",
        "result": result,
        "code": code,
        "manifest_sha256": recovery.sha256_json(request),
        "prior_state_sha256": recovery.semantic_state_sha256(prior_state),
        "next_state_sha256": next_state_sha256,
        "original_receipt_sha256": original_receipt_sha256,
    }
    return {**unsigned, "receipt_sha256": recovery.sha256_json(unsigned)}


def expected_next(
    state: dict[str, object],
    request: dict[str, object],
    receipt: dict[str, object],
    **updates: object,
) -> dict[str, object]:
    next_state = json.loads(json.dumps(state))
    next_state.update(updates)
    next_state["fencing_epoch"] = state["fencing_epoch"] + 1
    next_state["journal_head_sha256"] = recovery.sha256_json(
        {
            "schema": "codex-house-recovery-synthetic-event/1",
            "previous": state["journal_head_sha256"],
            "request_sha256": recovery.sha256_json(request),
        }
    )
    if request["action"] != recovery.LOCKDOWN_ENTER:
        next_state["consumed_challenges"][request["challenge_id"]] = {
            "manifest_sha256": recovery.sha256_json(request),
            "receipt_sha256": receipt["receipt_sha256"],
        }
    return next_state


class RecoveryPolicyTests(unittest.TestCase):
    def assert_accepted(
        self,
        state: dict[str, object],
        request: dict[str, object],
        supplied_evidence: object,
        **updates: object,
    ) -> tuple[dict[str, object], dict[str, object]]:
        next_state, receipt = recovery.verify_transition(
            state, request, supplied_evidence, 120
        )
        provisional = expected_next(state, request, {"receipt_sha256": digest("0")}, **updates)
        next_state_sha256 = recovery.semantic_state_sha256(provisional)
        self.assertEqual(
            receipt,
            expected_receipt(
                result="ACCEPTED",
                code="OK",
                request=request,
                prior_state=state,
                next_state_sha256=next_state_sha256,
                original_receipt_sha256=None,
            ),
        )
        self.assertIsNotNone(next_state)
        self.assertEqual(next_state, expected_next(state, request, receipt, **updates))
        return next_state, receipt

    def test_complete_synthetic_ceremony_and_fixed_receipts(self) -> None:
        state = initial_state()
        request = lockdown_request(state)
        state, _ = self.assert_accepted(state, request, None, mode="LOCKDOWN")

        request = manifest(state, recovery.SUSPEND_PRIMARY, "challenge-suspend-01")
        state, _ = self.assert_accepted(
            state,
            request,
            evidence(request),
            mode="PRIMARY_SUSPENDED",
            primary_status="SUSPENDED",
            quarantine_sha256=digest("2"),
            ceremony_parent_sha256=digest("1"),
        )

        request = manifest(
            state,
            recovery.RECOVER_PRIMARY,
            "challenge-recover-01",
            replacement_key_id="p256:replacement-fixture",
            replacement_epoch=2,
        )
        state, _ = self.assert_accepted(
            state,
            request,
            evidence(request, replacement=True),
            mode="REPLACEMENT_ENROLLED",
            replacement_key_id="p256:replacement-fixture",
            replacement_epoch=2,
            replacement_status="ENROLLED",
        )

        request = manifest(
            state,
            recovery.CHECKPOINT_SIGN,
            "challenge-checkpoint-01",
            new_checkpoint_sha256=digest("4"),
        )
        state, _ = self.assert_accepted(
            state,
            request,
            evidence(request),
            mode="REPLACEMENT_READY",
            replacement_status="READY",
            checkpoint_sha256=digest("4"),
        )

        request = manifest(
            state,
            recovery.REVOKE_PRIMARY,
            "challenge-revoke-01",
            tombstone_sha256=digest("5"),
        )
        state, _ = self.assert_accepted(
            state,
            request,
            evidence(request),
            mode="OLD_PRIMARY_REVOKED",
            primary_status="REVOKED",
            tombstone_sha256=digest("5"),
        )

        request = manifest(
            state,
            recovery.LOCKDOWN_EXIT,
            "challenge-exit-01",
            replacement_key_id="p256:replacement-fixture",
            replacement_epoch=2,
        )
        state, receipt = self.assert_accepted(
            state,
            request,
            evidence(request),
            mode="ACTIVE",
            primary_key_id="p256:replacement-fixture",
            primary_epoch=2,
            primary_status="ACTIVE",
            replacement_status="ACTIVE",
            retired_primary_key_id="p256:primary-fixture",
            retired_primary_epoch=1,
            ceremony_parent_sha256=None,
        )
        self.assertEqual(receipt["claim_ceiling"], recovery.CLAIM_CEILING)
        self.assertEqual(state["mode"], "ACTIVE")

    def test_replay_and_challenge_conflict_are_distinct_and_state_is_not_mutated(self) -> None:
        state = initial_state()
        lockdown = lockdown_request(state)
        state, _ = self.assert_accepted(state, lockdown, None, mode="LOCKDOWN")
        request = manifest(state, recovery.SUSPEND_PRIMARY, "challenge-replay-01")
        next_state, accepted = self.assert_accepted(
            state,
            request,
            evidence(request),
            mode="PRIMARY_SUSPENDED",
            primary_status="SUSPENDED",
            quarantine_sha256=digest("2"),
            ceremony_parent_sha256=digest("1"),
        )
        replay_state, replay = recovery.verify_transition(next_state, request, evidence(request), 120)
        self.assertIsNone(replay_state)
        self.assertEqual(
            replay,
            expected_receipt(
                result="REPLAY",
                code="ALREADY_CONSUMED",
                request=request,
                prior_state=next_state,
                next_state_sha256=None,
                original_receipt_sha256=accepted["receipt_sha256"],
            ),
        )
        conflicting = dict(request)
        conflicting["package_qualification_sha256"] = digest("9")
        refused_state, refused = recovery.verify_transition(next_state, conflicting, evidence(conflicting), 120)
        self.assertIsNone(refused_state)
        self.assertEqual(refused["result"], "REFUSED")
        self.assertEqual(refused["code"], "CHALLENGE_CONFLICT")
        self.assertEqual(next_state["mode"], "PRIMARY_SUSPENDED")

    def test_wrong_roles_unknown_fields_stale_bindings_and_boundaries_fail_closed(self) -> None:
        state = initial_state()
        request = lockdown_request(state)
        request["signature_b64"] = "forbidden"
        _, refusal = recovery.verify_transition(state, request, None, 120)
        self.assertEqual(refusal["code"], "LOCKDOWN_SCHEMA")

        state, _ = self.assert_accepted(state, lockdown_request(state), None, mode="LOCKDOWN")
        stale_primary = manifest(state, recovery.SUSPEND_PRIMARY, "challenge-primary-01")
        stale_primary["old_primary_key_id"] = "p256:other-primary"
        _, refusal = recovery.verify_transition(state, stale_primary, evidence(stale_primary), 120)
        self.assertEqual(refusal["code"], "STALE_PRIMARY")

        early_revoke = manifest(state, recovery.REVOKE_PRIMARY, "challenge-early-01", tombstone_sha256=digest("5"))
        _, refusal = recovery.verify_transition(state, early_revoke, evidence(early_revoke), 120)
        self.assertEqual(refusal["code"], "WRONG_STATE")

        suspend = manifest(state, recovery.SUSPEND_PRIMARY, "challenge-signer-01")
        wrong_evidence = evidence(suspend)
        wrong_evidence["signer_key_id"] = state["primary_key_id"]
        _, refusal = recovery.verify_transition(state, suspend, wrong_evidence, 120)
        self.assertEqual(refusal["code"], "WRONG_SIGNER")

        caller_claim = evidence(suspend)
        caller_claim["authority"] = "GRANTED"
        _, refusal = recovery.verify_transition(state, suspend, caller_claim, 120)
        self.assertEqual(refusal["code"], "EVIDENCE_SCHEMA")

        stale = manifest(state, recovery.SUSPEND_PRIMARY, "challenge-stale-01")
        stale["source_sha256"] = digest("8")
        _, refusal = recovery.verify_transition(state, stale, evidence(stale), 120)
        self.assertEqual(refusal["code"], "STALE_BINDING")

        malformed = manifest(state, "inbox.enqueue", "challenge-unknown-01")
        _, refusal = recovery.verify_transition(state, malformed, evidence(malformed), 120)
        self.assertEqual(refusal["code"], "UNKNOWN_ACTION")

        request = manifest(state, recovery.SUSPEND_PRIMARY, "challenge-bool-time-01")
        _, refusal = recovery.verify_transition(state, request, evidence(request), True)
        self.assertEqual(refusal["code"], "INVALID_DECISION_TIME")

    def test_recovery_and_exit_require_exact_replacement_identity(self) -> None:
        state = initial_state()
        state, _ = self.assert_accepted(state, lockdown_request(state), None, mode="LOCKDOWN")
        state, _ = self.assert_accepted(
            state,
            manifest(state, recovery.SUSPEND_PRIMARY, "challenge-suspend-02"),
            evidence(manifest(state, recovery.SUSPEND_PRIMARY, "challenge-suspend-02")),
            mode="PRIMARY_SUSPENDED",
            primary_status="SUSPENDED",
            quarantine_sha256=digest("2"),
            ceremony_parent_sha256=digest("1"),
        )
        request = manifest(
            state,
            recovery.RECOVER_PRIMARY,
            "challenge-recover-02",
            replacement_key_id="p256:replacement-fixture",
            replacement_epoch=2,
        )
        missing_possession = evidence(request)
        _, refusal = recovery.verify_transition(state, request, missing_possession, 120)
        self.assertEqual(refusal["code"], "REPLACEMENT_NOT_VERIFIED")

        stale_parent = dict(request)
        stale_parent["ceremony_parent_sha256"] = digest("9")
        _, refusal = recovery.verify_transition(state, stale_parent, evidence(stale_parent, replacement=True), 120)
        self.assertEqual(refusal["code"], "STALE_CEREMONY")

    def test_source_isolation_and_no_production_reachability(self) -> None:
        module_path = Path(recovery.__file__).resolve()
        tree = ast.parse(module_path.read_text())
        allowed_imports = {"hashlib", "json", "re"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                self.assertTrue(all(alias.name in allowed_imports for alias in node.names))
            if isinstance(node, ast.ImportFrom):
                self.assertEqual(node.module, "__future__")
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                self.assertNotIn(node.func.id, {"eval", "exec", "compile", "__import__", "open"})
        house_root = module_path.parents[1]
        sanctioned = {
            module_path.with_name("recovery_" + "ledger.py"),
            Path(__file__).with_name("test_recovery_" + "ledger.py").resolve(),
        }
        for candidate in house_root.rglob("*.py"):
            if candidate.resolve() in {module_path, Path(__file__).resolve(), *sanctioned}:
                continue
            self.assertNotIn("recovery_policy", candidate.read_text())


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import builtins
import copy
import hashlib
import json
import random
import secrets
import socket
import subprocess
import tempfile
import time
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

from house import worker_exec
from house.worker_exec import (
    OperationV2Error,
    assemble_operation_v2,
    assemble_route_selection_v1,
    verify_operation_v2,
    verify_route_selection_v1,
    verify_task_card_v2,
)


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def seal(unsigned: dict[str, object]) -> dict[str, object]:
    return {**unsigned, "record_sha256": canonical_sha256(unsigned)}


def task_card(**overrides: object) -> dict[str, object]:
    unsigned: dict[str, object] = {
        "schema": "codex-house-task-card/2",
        "task_id": "task-123",
        "title": "Review one immutable artifact",
        "summary": "Return structural evidence without dispatching a worker.",
        "routing_advice": {
            "class_hint": "reviewer",
            "model_preference": "gpt-5.6-terra",
        },
        "execution_constraints": {
            "required_model": None,
            "allowed_models": ["gpt-5.6-terra", "gpt-5.6-sol"],
            "allowed_providers": ["openai", "openai-secondary"],
            "required_usage_pool": "codex-weekly",
        },
        "dispatch": "NOT_ATTEMPTED",
        "authority": "NOT_GRANTED",
    }
    unsigned.update(overrides)
    return seal(unsigned)


def route(
    card: dict[str, object],
    *,
    model: str = "gpt-5.6-terra",
    provider: str = "openai",
    pool: str = "codex-weekly",
    class_state: str = "HONORED",
    model_state: str = "HONORED",
    reason: str | None = None,
    not_after: str = "2026-08-23T14:00:00Z",
) -> dict[str, object]:
    return assemble_route_selection_v1(
        card,
        selection_id="route-123",
        model_identity=model,
        provider_identity=provider,
        account_fingerprint="a" * 64,
        usage_pool_id=pool,
        routing_disposition={
            "class_hint": class_state,
            "model_preference": model_state,
            "reason": reason,
        },
        observation={
            "observed_at": "2026-08-23T13:00:00Z",
            "not_after": not_after,
            "freshness_policy": "codex-route-hourly-v1",
            "evidence_bundle_sha256": "b" * 64,
        },
        provenance={
            "author_id": "router-1",
            "authoring_method": "deterministic-router/1.0",
            "signature_state": "NOT_VERIFIED_IN_FIRST_SLICE",
        },
    )


def descriptors(
    *,
    operation_id: str = "operation-123",
    project_policy: str = "PROJECT_INPUTS_CONTENT_ADDRESSED",
    supported_flags: list[str] | None = None,
) -> dict[str, object]:
    flags = supported_flags or [
        "-C",
        "-c",
        "--ignore-rules",
        "--ignore-user-config",
        "--json",
        "--model",
        "--output-last-message",
        "--sandbox",
    ]
    prompt = "Inspect the sealed artifact and return structural evidence only."
    return {
        "executable": {
            "schema": "codex-house-executable-descriptor/1",
            "path": "/opt/codex/bin/codex",
            "content_sha256": "c" * 64,
            "version": "0.147.0",
            "cli_contract_sha256": canonical_sha256({"supported_flags": flags}),
            "supported_flags": flags,
        },
        "workspace": {
            "schema": "codex-house-workspace-descriptor/1",
            "path": "/srv/project",
            "identity_sha256": "d" * 64,
            "project_input_policy": project_policy,
            "project_input_inventory_sha256": "e" * 64,
        },
        "output_intent": {
            "schema": "codex-house-output-intent/1",
            "path": f"/srv/output/{operation_id}/last-message.txt",
            "reservation_policy_id": "race-safe-reservation-v1",
            "max_bytes": 65_536,
            "state": "UNRESERVED_INTENT",
        },
        "prompt": {
            "schema": "codex-house-prompt-descriptor/1",
            "text": prompt,
            "text_sha256": text_sha256(prompt),
        },
        "isolation": {
            "schema": "codex-house-isolation-policy/1",
            "sandbox": "read-only",
            "allowed_context_surfaces": [],
            "allowed_tool_surfaces": [],
            "managed_policy": "NARROW_ONLY",
        },
        "resource": {
            "schema": "codex-house-resource-policy/1",
            "wall_seconds": 60,
            "max_stdout_bytes": 131_072,
            "max_stderr_bytes": 131_072,
        },
        "reconciliation": {
            "schema": "codex-house-reconciliation-policy/1",
            "idempotency_key": operation_id,
            "retry_budget": 0,
            "automatic_resume": "PROHIBITED",
        },
    }


class OperationV2Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.card = task_card()
        self.route = route(self.card)
        self.descriptors = descriptors()
        self.operation = assemble_operation_v2(
            self.card,
            self.route,
            operation_id="operation-123",
            descriptors=self.descriptors,
        )

    def test_happy_path_is_deterministic_structural_and_inert(self) -> None:
        self.assertEqual(
            verify_task_card_v2(self.card)["state"],
            "TASK_CARD_V2_VERIFIED_NO_DISPATCH",
        )
        self.assertEqual(
            verify_route_selection_v1(self.card, self.route)["state"],
            "ROUTE_SELECTION_VERIFIED_NO_DISPATCH",
        )
        receipt = verify_operation_v2(
            self.card, self.route, self.descriptors, self.operation
        )
        self.assertEqual(receipt["state"], "OPERATION_V2_VERIFIED_NO_DISPATCH")
        self.assertEqual(receipt["claim_ceiling"], "STRUCTURE_AND_BINDINGS_ONLY")
        self.assertEqual(self.operation["dispatch"], "NOT_ATTEMPTED")
        self.assertEqual(self.operation["authority"], "NOT_GRANTED")
        self.assertEqual(
            assemble_operation_v2(
                self.card,
                self.route,
                operation_id="operation-123",
                descriptors=self.descriptors,
            ),
            self.operation,
        )
        mutable = descriptors()
        frozen = assemble_operation_v2(
            self.card,
            self.route,
            operation_id="operation-123",
            descriptors=mutable,
        )
        mutable["workspace"]["path"] = "/srv/changed"
        self.assertEqual(frozen["descriptors"]["workspace"]["path"], "/srv/project")

    def test_01_changed_advice_cannot_reuse_a_stale_route(self) -> None:
        changed = copy.deepcopy(self.card)
        changed["routing_advice"]["class_hint"] = "coder"
        with self.assertRaisesRegex(OperationV2Error, "task card record hash mismatch"):
            verify_route_selection_v1(changed, self.route)
        changed["record_sha256"] = canonical_sha256(
            {key: value for key, value in changed.items() if key != "record_sha256"}
        )
        with self.assertRaisesRegex(
            OperationV2Error, "route task-card binding mismatch"
        ):
            verify_route_selection_v1(changed, self.route)

    def test_02_conflicting_hard_constraints_refuse_before_assembly(self) -> None:
        cases = (
            {"model": "gpt-5.6-unknown", "provider": "openai", "pool": "codex-weekly"},
            {"model": "gpt-5.6-terra", "provider": "unlisted", "pool": "codex-weekly"},
            {"model": "gpt-5.6-terra", "provider": "openai", "pool": "other-pool"},
        )
        for case in cases:
            with self.subTest(case=case), self.assertRaises(OperationV2Error):
                route(self.card, **case)

    def test_03_advisory_override_requires_a_reason(self) -> None:
        with self.assertRaisesRegex(OperationV2Error, "override reason"):
            route(
                self.card,
                model="gpt-5.6-sol",
                model_state="OVERRIDDEN_WITH_REASON",
            )

    def test_04_route_model_or_expiry_change_breaks_operation_binding(self) -> None:
        changed_model = route(
            self.card,
            model="gpt-5.6-sol",
            model_state="OVERRIDDEN_WITH_REASON",
            reason="bounded implementation escalation",
        )
        changed_expiry = route(self.card, not_after="2026-08-23T13:30:00Z")
        for changed in (changed_model, changed_expiry):
            with (
                self.subTest(route_hash=changed["record_sha256"]),
                self.assertRaisesRegex(OperationV2Error, "binding mismatch"),
            ):
                verify_operation_v2(
                    self.card, changed, self.descriptors, self.operation
                )

    def test_05_assembly_succeeds_with_host_io_and_ambient_apis_disabled(self) -> None:
        targets = (
            (builtins, "open"),
            (Path, "exists"),
            (Path, "mkdir"),
            (Path, "open"),
            (Path, "resolve"),
            (Path, "stat"),
            (subprocess, "Popen"),
            (socket, "socket"),
            (time, "time"),
            (random, "random"),
            (secrets, "token_bytes"),
        )

        def forbidden(*args: object, **kwargs: object) -> None:
            raise AssertionError(f"ambient API used: {args!r} {kwargs!r}")

        with ExitStack() as stack:
            for owner, name in targets:
                stack.enter_context(patch.object(owner, name, forbidden))
            rebuilt = assemble_operation_v2(
                self.card,
                self.route,
                operation_id="operation-123",
                descriptors=self.descriptors,
            )
            receipt = verify_operation_v2(
                self.card, self.route, self.descriptors, rebuilt
            )
        self.assertEqual(receipt["state"], "OPERATION_V2_VERIFIED_NO_DISPATCH")

    def test_06_ignore_policy_requires_hash_bound_cli_flag_support(self) -> None:
        ignored = descriptors(project_policy="PROJECT_CONFIG_IGNORED")
        with self.assertRaisesRegex(OperationV2Error, "lacks project-config"):
            assemble_operation_v2(
                self.card,
                self.route,
                operation_id="operation-123",
                descriptors=ignored,
            )
        supported = copy.deepcopy(ignored)
        flags = supported["executable"]["supported_flags"]
        flags.append("--ignore-project-config")
        supported["executable"]["cli_contract_sha256"] = canonical_sha256(
            {"supported_flags": flags}
        )
        operation = assemble_operation_v2(
            self.card,
            self.route,
            operation_id="operation-123",
            descriptors=supported,
        )
        self.assertIn("--ignore-project-config", operation["argv"])

    def test_07_project_inventory_change_requires_a_new_operation(self) -> None:
        changed = copy.deepcopy(self.descriptors)
        changed["workspace"]["project_input_inventory_sha256"] = "f" * 64
        replacement = assemble_operation_v2(
            self.card,
            self.route,
            operation_id="operation-123",
            descriptors=changed,
        )
        self.assertNotEqual(
            replacement["record_sha256"], self.operation["record_sha256"]
        )
        with self.assertRaisesRegex(OperationV2Error, "binding mismatch"):
            verify_operation_v2(self.card, self.route, changed, self.operation)

    def test_08_output_intent_cannot_claim_reservation(self) -> None:
        changed = copy.deepcopy(self.descriptors)
        changed["output_intent"]["state"] = "RESERVED"
        with self.assertRaisesRegex(OperationV2Error, "overstates reservation"):
            assemble_operation_v2(
                self.card,
                self.route,
                operation_id="operation-123",
                descriptors=changed,
            )

    def test_09_unverified_authorship_never_becomes_execution_authority(self) -> None:
        receipt = verify_route_selection_v1(self.card, self.route)
        self.assertEqual(receipt["claim_ceiling"], "STRUCTURE_AND_BINDINGS_ONLY")
        self.assertEqual(
            self.route["provenance"]["signature_state"], "NOT_VERIFIED_IN_FIRST_SLICE"
        )
        self.assertFalse(hasattr(worker_exec, "execute_operation_v2"))
        changed = copy.deepcopy(self.route)
        changed["provenance"]["signature_state"] = "VERIFIED"
        changed["record_sha256"] = canonical_sha256(
            {key: value for key, value in changed.items() if key != "record_sha256"}
        )
        with self.assertRaisesRegex(OperationV2Error, "overstates authentication"):
            verify_route_selection_v1(self.card, changed)

    def test_10_assembly_changes_no_controller_workspace_or_output_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            root = Path(raw_root)
            for relative, content in (
                ("controller/state.db", b"prepared-no-lease"),
                ("workspace/source.txt", b"unchanged"),
                ("output/sentinel", b"unreserved"),
            ):
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)

            def snapshot() -> dict[str, str]:
                return {
                    str(path.relative_to(root)): hashlib.sha256(
                        path.read_bytes()
                    ).hexdigest()
                    for path in sorted(root.rglob("*"))
                    if path.is_file()
                }

            before = snapshot()
            assemble_operation_v2(
                self.card,
                self.route,
                operation_id="operation-123",
                descriptors=self.descriptors,
            )
            self.assertEqual(snapshot(), before)

    def test_unknown_wildcard_legacy_and_nonlexical_inputs_fail_closed(self) -> None:
        legacy = copy.deepcopy(self.card)
        legacy["requested_recipient"] = "reviewer"
        with self.assertRaisesRegex(OperationV2Error, "fields are not exact"):
            verify_task_card_v2(legacy)
        for bad_model in ("auto", "fallback", "model*"):
            with self.subTest(model=bad_model), self.assertRaises(OperationV2Error):
                route(self.card, model=bad_model)
        changed = copy.deepcopy(self.descriptors)
        changed["workspace"]["path"] = "/srv/../escape"
        with self.assertRaisesRegex(OperationV2Error, "normalized lexical path"):
            assemble_operation_v2(
                self.card,
                self.route,
                operation_id="operation-123",
                descriptors=changed,
            )
        subclass = type("MappingSubclass", (dict,), {})(self.descriptors)
        with self.assertRaisesRegex(OperationV2Error, "fields are not exact"):
            assemble_operation_v2(
                self.card,
                self.route,
                operation_id="operation-123",
                descriptors=subclass,
            )


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import ast
import builtins
import copy
import hashlib
import json
import unittest
from pathlib import Path
from unittest import mock

from house.worker_exec import (
    RuntimeBindingError,
    assemble_operation_v2,
    assemble_route_selection_v1,
    verify_runtime_evidence_bindings,
)


def digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


class RuntimeBindingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.card = {
            "schema": "codex-house-task-card/2",
            "task_id": "task-123",
            "title": "x",
            "summary": "x",
            "routing_advice": {"class_hint": None, "model_preference": None},
            "execution_constraints": {
                "required_model": "gpt-5.6-terra",
                "allowed_models": ["gpt-5.6-terra"],
                "allowed_providers": ["openai"],
                "required_usage_pool": "codex-weekly",
            },
            "dispatch": "NOT_ATTEMPTED",
            "authority": "NOT_GRANTED",
        }
        self.card["record_sha256"] = digest(self.card)
        flags = [
            "-C",
            "-c",
            "--ignore-rules",
            "--ignore-user-config",
            "--json",
            "--model",
            "--output-last-message",
            "--sandbox",
        ]
        self.route = assemble_route_selection_v1(
            self.card,
            selection_id="route-123",
            model_identity="gpt-5.6-terra",
            provider_identity="openai",
            account_fingerprint="a" * 64,
            usage_pool_id="codex-weekly",
            routing_disposition={
                "class_hint": "NOT_APPLICABLE",
                "model_preference": "NOT_APPLICABLE",
                "reason": None,
            },
            observation={
                "observed_at": "2026-08-24T00:00:00Z",
                "not_after": "2026-08-25T00:00:00Z",
                "freshness_policy": "policy-1",
                "evidence_bundle_sha256": "b" * 64,
            },
            provenance={
                "author_id": "router-1",
                "authoring_method": "deterministic-router/1",
                "signature_state": "NOT_VERIFIED_IN_FIRST_SLICE",
            },
        )
        self.descriptors = {
            "executable": {
                "schema": "codex-house-executable-descriptor/1",
                "path": "/opt/codex",
                "content_sha256": "c" * 64,
                "version": "v1",
                "cli_contract_sha256": digest({"supported_flags": flags}),
                "supported_flags": flags,
            },
            "workspace": {
                "schema": "codex-house-workspace-descriptor/1",
                "path": "/srv/work",
                "identity_sha256": "d" * 64,
                "project_input_policy": "PROJECT_INPUTS_CONTENT_ADDRESSED",
                "project_input_inventory_sha256": "e" * 64,
            },
            "output_intent": {
                "schema": "codex-house-output-intent/1",
                "path": "/srv/out/last.txt",
                "reservation_policy_id": "reserve-1",
                "max_bytes": 10,
                "state": "UNRESERVED_INTENT",
            },
            "prompt": {
                "schema": "codex-house-prompt-descriptor/1",
                "text": "x",
                "text_sha256": hashlib.sha256(b"x").hexdigest(),
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
                "wall_seconds": 1,
                "max_stdout_bytes": 10,
                "max_stderr_bytes": 10,
            },
            "reconciliation": {
                "schema": "codex-house-reconciliation-policy/1",
                "idempotency_key": "operation-123",
                "retry_budget": 0,
                "automatic_resume": "PROHIBITED",
            },
        }
        self.operation = assemble_operation_v2(
            self.card,
            self.route,
            operation_id="operation-123",
            descriptors=self.descriptors,
        )

    def observation(self) -> dict[str, object]:
        isolation = {
            key: value
            for key, value in self.descriptors["isolation"].items()
            if key != "schema"
        }
        return {
            "schema": "codex-house-runtime-evidence-observation/1",
            "state": "UNATTESTED_STRUCTURE_ONLY",
            "task_card_sha256": self.card["record_sha256"],
            "route_selection_sha256": self.route["record_sha256"],
            "operation_sha256": self.operation["record_sha256"],
            "model_identity": "gpt-5.6-terra",
            "provider_identity": "openai",
            "route_account_fingerprint": "a" * 64,
            "usage_pool_id": "codex-weekly",
            "argv_sha256": digest(self.operation["argv"]),
            "descriptors_sha256": digest(self.descriptors),
            "workspace": {"path": "/srv/work", "identity_sha256": "d" * 64},
            "output": {"path": "/srv/out/last.txt", "max_bytes": 10},
            "isolation": isolation,
            "config_hooks": {
                "state": "CONTENT_HASHED",
                "hook_state": "DISABLED_BY_POLICY",
                "evidence_sha256": "f" * 64,
            },
            "runtime_roots": {
                "home": "/tmp/home",
                "codex_home": "/tmp/codex",
                "state": "/tmp/state",
                "temp": "/tmp/temp",
                "evidence_sha256": "1" * 64,
            },
            "filesystem": {
                "state": "MEASURED",
                "read_roots": ["/srv/work"],
                "write_roots": ["/tmp/state"],
                "policy_sha256": "2" * 64,
                "trace_sha256": "3" * 64,
            },
            "evidence_bundle_sha256": "b" * 64,
        }

    def attested_observation(self) -> dict[str, object]:
        value = self.observation()
        value.update(
            {
                "state": "ATTESTED_CLAIMED",
                "attestation_subject_id": "subject-1",
                "attestation_issuer_id": "issuer-1",
                "self_issue_disposition": "NOT_SELF_ISSUED",
                "trust_policy_id": "policy-1",
                "trust_policy_version": "v1",
                "trust_policy_sha256": "4" * 64,
                "observer_key_id": "observer-1",
                "observer_key_policy_sha256": "5" * 64,
                "reference_time_decision_sha256": "6" * 64,
                "valid_from": "2026-08-24T00:00:00Z",
                "valid_until": "2026-08-25T00:00:00Z",
            }
        )
        value["attestation_content_sha256"] = digest(value)
        value["self_issue_decision_sha256"] = digest(
            {
                "attestation_subject_id": value["attestation_subject_id"],
                "attestation_issuer_id": value["attestation_issuer_id"],
                "self_issue_disposition": value["self_issue_disposition"],
                "attestation_content_sha256": value["attestation_content_sha256"],
            }
        )
        return value

    def assert_refuses(self, observation: dict[str, object]) -> None:
        with self.assertRaises(RuntimeBindingError):
            verify_runtime_evidence_bindings(
                self.card, self.route, self.descriptors, self.operation, observation
            )

    def test_unattested_binds_without_dispatch(self) -> None:
        receipt = verify_runtime_evidence_bindings(
            self.card, self.route, self.descriptors, self.operation, self.observation()
        )
        self.assertEqual(
            receipt["state"], "RUNTIME_EVIDENCE_BINDINGS_VERIFIED_NO_DISPATCH"
        )
        self.assertEqual(receipt["authority"], "NOT_GRANTED")
        self.assertEqual(receipt["dispatch"], "NOT_ATTEMPTED")

    def test_attested_binds_without_promoting_claims(self) -> None:
        receipt = verify_runtime_evidence_bindings(
            self.card,
            self.route,
            self.descriptors,
            self.operation,
            self.attested_observation(),
        )
        self.assertEqual(
            receipt["claim_ceiling"],
            "UNTRUSTED_INPUT_STRUCTURE_AND_CROSS_BINDINGS_ONLY",
        )
        self.assertNotIn("attestation_subject_id", receipt)

    def test_cross_binding_drift_refuses(self) -> None:
        mutations = {
            "model_identity": "gpt-5.6-sol",
            "provider_identity": "other-provider",
            "route_account_fingerprint": "0" * 64,
            "usage_pool_id": "other-pool",
            "argv_sha256": "0" * 64,
            "descriptors_sha256": "0" * 64,
            "evidence_bundle_sha256": "0" * 64,
        }
        for field, changed in mutations.items():
            with self.subTest(field=field):
                value = self.observation()
                value[field] = changed
                self.assert_refuses(value)

    def test_descriptor_and_environment_drift_refuses(self) -> None:
        mutations = [
            ("workspace", {"path": "/srv/other", "identity_sha256": "d" * 64}),
            ("output", {"path": "/srv/out/other.txt", "max_bytes": 10}),
            (
                "isolation",
                {
                    "sandbox": "write",
                    "allowed_context_surfaces": [],
                    "allowed_tool_surfaces": [],
                    "managed_policy": "NARROW_ONLY",
                },
            ),
            (
                "config_hooks",
                {
                    "state": "CONTENT_HASHED",
                    "hook_state": "ENABLED",
                    "evidence_sha256": "f" * 64,
                },
            ),
            (
                "runtime_roots",
                {
                    "home": "/tmp/home",
                    "codex_home": "/tmp/home",
                    "state": "/tmp/state",
                    "temp": "/tmp/temp",
                    "evidence_sha256": "1" * 64,
                },
            ),
            (
                "filesystem",
                {
                    "state": "MEASURED",
                    "read_roots": ["/srv/other"],
                    "write_roots": ["/tmp/state"],
                    "policy_sha256": "2" * 64,
                    "trace_sha256": "3" * 64,
                },
            ),
        ]
        for field, changed in mutations:
            with self.subTest(field=field):
                value = self.observation()
                value[field] = copy.deepcopy(changed)
                self.assert_refuses(value)

    def test_attestation_content_or_decision_drift_refuses(self) -> None:
        for field, changed in (
            ("attestation_subject_id", "subject-2"),
            ("attestation_content_sha256", "0" * 64),
            ("self_issue_decision_sha256", "0" * 64),
        ):
            with self.subTest(field=field):
                value = self.attested_observation()
                value[field] = changed
                self.assert_refuses(value)

    def test_implicit_identity_and_invalid_attestation_interval_refuse(self) -> None:
        value = self.observation()
        value["model_identity"] = "default"
        self.assert_refuses(value)
        value = self.attested_observation()
        value["valid_until"] = "2026-08-23T00:00:00Z"
        self.assert_refuses(value)
        value = self.attested_observation()
        value["valid_from"] = "2026-08-24Z"
        self.assert_refuses(value)

    def test_valid_binding_is_sterile_under_denied_file_access(self) -> None:
        with mock.patch.object(
            builtins,
            "open",
            side_effect=AssertionError("ambient file access is forbidden"),
        ):
            receipt = verify_runtime_evidence_bindings(
                self.card,
                self.route,
                self.descriptors,
                self.operation,
                self.observation(),
            )
        self.assertEqual(receipt["dispatch"], "NOT_ATTEMPTED")

    def test_source_has_no_ambient_operation_imports_or_calls(self) -> None:
        source_path = Path(__file__).parents[1] / "runtime_binding.py"
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        forbidden_modules = {"os", "socket", "subprocess", "time"}
        imports = {
            module
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for module in (
                [alias.name.split(".")[0] for alias in node.names]
                if isinstance(node, ast.Import)
                else [node.module.split(".")[0]]
                if node.module
                else []
            )
        }
        calls = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertFalse(imports & forbidden_modules)
        self.assertNotIn("open", calls)

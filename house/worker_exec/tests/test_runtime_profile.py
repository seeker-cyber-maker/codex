from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

from house.worker_exec.operation import WorkerExecError, prepare_operation
from house.worker_exec.runtime_profile import (
    PROFILE_SCHEMA,
    QUALIFICATION_POLICY,
    RuntimeProfileError,
    runtime_profile_gap_receipt,
    verify_real_runtime_profile,
)


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


class RuntimeProfileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        root = Path(self.tempdir.name)
        self.workspace = root / "workspace"
        self.output = root / "output"
        self.workspace.mkdir()
        self.output.mkdir()
        self.codex = root / "codex"
        self.codex.write_text("fixture", encoding="utf-8")
        self.codex.chmod(0o700)
        task = {
            "schema": "codex-house-task-card/1",
            "task_id": "task-1",
            "title": "Read-only fixture",
            "summary": "Return one bounded observation.",
            "requested_recipient": "specific_model",
            "requested_recipient_id": "gpt-5.6-terra",
        }
        self.operation = prepare_operation(
            task,
            operation_id="operation-1",
            workspace=self.workspace,
            output_root=self.output,
            codex_path=self.codex,
            wall_seconds=60,
        )
        self.profile = self._profile()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _profile(self) -> dict[str, object]:
        workspace_path = self.operation["authority_scope"]["read"][0]
        output_path = self.operation["expected_artifacts"][0]
        runtime_root = Path(self.tempdir.name) / "runtime"
        roots = {
            "home": str(runtime_root / "home"),
            "codex_home": str(runtime_root / "codex-home"),
            "state": str(runtime_root / "state"),
            "temp": str(runtime_root / "tmp"),
            "content_inventory_sha256": "1" * 64,
        }
        environment_values = {
            "CODEX_HOME": roots["codex_home"],
            "HOME": roots["home"],
            "LANG": "C.UTF-8",
            "PATH": "/usr/bin:/bin",
            "TMPDIR": roots["temp"],
        }
        unsigned: dict[str, object] = {
            "schema": PROFILE_SCHEMA,
            "profile_id": "profile-1",
            "mode": "QUALIFIED_REAL_RUNTIME_PROFILE",
            "qualification_policy": QUALIFICATION_POLICY,
            "operation_id": self.operation["operation_id"],
            "record_sha256": self.operation["record_sha256"],
            "executable": {
                "path": str(self.codex),
                "sha256": self.operation["input_hashes"]["codex_sha256"],
                "version": "codex-cli 0.147.0",
                "cli_contract_sha256": "2" * 64,
                "cli_capture_sha256": "3" * 64,
            },
            "argv_sha256": self.operation["input_hashes"]["argv_sha256"],
            "model_identity": "gpt-5.6-terra",
            "model_source": "INDEPENDENT_RUNTIME_QUALIFICATION",
            "workspace": {"path": workspace_path, "identity_sha256": "4" * 64},
            "output": {
                "path": output_path,
                "reservation_evidence_sha256": "5" * 64,
                "stdout_max_bytes": 65_536,
                "stderr_max_bytes": 65_536,
                "last_message_max_bytes": 1_048_576,
                "total_max_bytes": 1_179_648,
            },
            "environment": {
                "policy": "EXACT_ALLOWLIST",
                "values": environment_values,
                "inventory_sha256": canonical_sha256(environment_values),
            },
            "runtime_roots": roots,
            "config_hooks": {
                "state": "CONTENT_HASHED",
                "hook_state": "DISABLED_BY_POLICY",
                "content_inventory_sha256": "6" * 64,
                "evidence_sha256": "7" * 64,
            },
            "provider": {
                "identity": "openai-codex",
                "account_id": "account-fixture",
                "usage_pool_id": "codex-weekly",
                "egress": ["https://api.openai.com"],
            },
            "filesystem": {
                "state": "MEASURED",
                "policy_sha256": "8" * 64,
                "trace_sha256": "9" * 64,
                "read_roots": [workspace_path],
                "write_roots": [
                    str(Path(output_path).parent),
                    roots["home"],
                    roots["codex_home"],
                    roots["state"],
                    roots["temp"],
                ],
            },
        }
        runtime_facts = {
            key: unsigned[key]
            for key in unsigned
            if key
            not in {
                "schema",
                "profile_id",
                "mode",
                "qualification_policy",
                "qualification_evidence",
            }
        }
        unsigned["qualification_evidence"] = {
            "state": "EXTERNALLY_VERIFIED_INPUT",
            "issuer": "runtime-qualifier-fixture",
            "observed_at": "2026-08-23T05:21:00Z",
            "runtime_facts_sha256": canonical_sha256(runtime_facts),
            "evidence_bundle_sha256": "a" * 64,
        }
        return {**unsigned, "profile_sha256": canonical_sha256(unsigned)}

    def _reseal(self, profile: dict[str, object]) -> dict[str, object]:
        unsigned = {
            key: value for key, value in profile.items() if key != "profile_sha256"
        }
        return {**unsigned, "profile_sha256": canonical_sha256(unsigned)}

    def test_complete_profile_verifies_structure_without_dispatch(self) -> None:
        receipt = verify_real_runtime_profile(self.operation, self.profile)
        self.assertEqual(receipt["state"], "PROFILE_VERIFIED_NO_DISPATCH")
        self.assertEqual(receipt["dispatch"], "NOT_ATTEMPTED")
        self.assertEqual(receipt["authority"], "NOT_GRANTED")
        self.assertEqual(receipt["claim_ceiling"], "STRUCTURE_AND_BINDINGS_ONLY")

    def test_unresolved_operation_returns_deterministic_gap_receipt(self) -> None:
        task = {
            "schema": "codex-house-task-card/1",
            "task_id": "task-2",
            "title": "Unresolved fixture",
            "summary": "Remain unqualified.",
            "requested_recipient": "triage",
        }
        operation = prepare_operation(
            task,
            operation_id="operation-2",
            workspace=self.workspace,
            output_root=self.output,
            codex_path=self.codex,
            wall_seconds=60,
        )
        first = runtime_profile_gap_receipt(operation)
        second = runtime_profile_gap_receipt(operation)
        self.assertEqual(first, second)
        self.assertEqual(first["state"], "NOT_QUALIFIED")
        self.assertEqual(first["dispatch"], "NOT_ATTEMPTED")
        self.assertEqual(
            first["gaps"],
            [
                "EXPLICIT_MODEL_REQUIRED",
                "PROVIDER_ACCOUNT_IDENTITY_REQUIRED",
                "RUNTIME_QUALIFICATION_EVIDENCE_REQUIRED",
                "USAGE_POOL_IDENTITY_REQUIRED",
            ],
        )

    def test_profile_hash_and_operation_bindings_fail_closed(self) -> None:
        with self.assertRaisesRegex(RuntimeProfileError, "hash mismatch"):
            verify_real_runtime_profile(
                self.operation, {**self.profile, "model_identity": "gpt-5.6-sol"}
            )
        changed = self._reseal({**self.profile, "record_sha256": "f" * 64})
        with self.assertRaisesRegex(RuntimeProfileError, "operation binding"):
            verify_real_runtime_profile(self.operation, changed)

    def test_implicit_model_provider_and_usage_pool_fail_closed(self) -> None:
        for path, value in (
            (("model_identity",), "default"),
            (("provider", "identity"), "unknown"),
            (("provider", "identity"), "provider-unknown"),
            (("provider", "usage_pool_id"), "fallback"),
            (("provider", "account_id"), "*"),
        ):
            changed = json.loads(json.dumps(self.profile))
            target = changed
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            changed = self._reseal(changed)
            with (
                self.subTest(path=path, value=value),
                self.assertRaisesRegex(
                    RuntimeProfileError,
                    "implicit or unverified|explicit safe identifier",
                ),
            ):
                verify_real_runtime_profile(self.operation, changed)

    def test_extra_environment_and_unbounded_output_fail_closed(self) -> None:
        changed = json.loads(json.dumps(self.profile))
        changed["environment"]["values"]["EXTRA"] = "surprise"
        changed["environment"]["inventory_sha256"] = canonical_sha256(
            changed["environment"]["values"]
        )
        changed = self._reseal(changed)
        with self.assertRaisesRegex(RuntimeProfileError, "environment keys"):
            verify_real_runtime_profile(self.operation, changed)

        changed = json.loads(json.dumps(self.profile))
        changed["output"]["total_max_bytes"] = 0
        changed = self._reseal(changed)
        with self.assertRaisesRegex(RuntimeProfileError, "between 1"):
            verify_real_runtime_profile(self.operation, changed)

    def test_config_drift_and_missing_explicit_model_fail_closed(self) -> None:
        changed = json.loads(json.dumps(self.profile))
        changed["config_hooks"]["content_inventory_sha256"] = "b" * 64
        changed = self._reseal(changed)
        with self.assertRaisesRegex(RuntimeProfileError, "facts changed"):
            verify_real_runtime_profile(self.operation, changed)

        operation = json.loads(json.dumps(self.operation))
        model_index = operation["argv"].index("--model")
        del operation["argv"][model_index : model_index + 2]
        operation["input_hashes"]["argv_sha256"] = canonical_sha256(operation["argv"])
        unsigned = {
            key: value for key, value in operation.items() if key != "record_sha256"
        }
        operation["record_sha256"] = canonical_sha256(unsigned)
        with self.assertRaisesRegex(WorkerExecError, "operation argv mismatch"):
            verify_real_runtime_profile(operation, self.profile)

    def test_module_does_not_import_execution_or_state_backends(self) -> None:
        source = Path(__file__).parents[1].joinpath("runtime_profile.py").read_text()
        for forbidden in (
            "subprocess",
            "sqlite3",
            "cryptography",
            "requests",
            "urllib",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(f"import {forbidden}", source)
        self.assertNotIn("WorkerOperationController", source)
        self.assertNotIn("Popen", source)
        self.assertNotIn("os.environ", source)

    def test_no_controller_file_is_touched_by_gap_receipt(self) -> None:
        marker = Path(self.tempdir.name) / "controller.sqlite"
        marker.write_bytes(os.urandom(128))
        before = hashlib.sha256(marker.read_bytes()).hexdigest()
        runtime_profile_gap_receipt(self.operation)
        after = hashlib.sha256(marker.read_bytes()).hexdigest()
        self.assertEqual(before, after)

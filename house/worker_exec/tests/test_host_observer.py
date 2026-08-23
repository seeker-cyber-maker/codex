from __future__ import annotations

import builtins
import copy
import hashlib
import json
import os
import socket
import subprocess
import tempfile
import time
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

from house.worker_exec import (
    HostObserverError,
    observe_host_v1,
    verify_host_observation_v1,
)
from house.worker_exec.cli_contract import REQUIRED_EXEC_FLAGS
from house.worker_exec.host_observer import (
    CLI_CAPTURE_SCHEMA,
    CONFIG_PRECEDENCE,
    CONTRIBUTOR_CLASSES,
    GRAMMAR_SCHEMA,
    POLICY_SCHEMA,
    REQUEST_SCHEMA,
    SECRET_BASENAMES,
)


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def seal(
    unsigned: dict[str, object], field: str = "record_sha256"
) -> dict[str, object]:
    return {**unsigned, field: canonical_sha256(unsigned)}


def reseal(record: dict[str, object], field: str = "record_sha256") -> None:
    record[field] = canonical_sha256(
        {key: value for key, value in record.items() if key != field}
    )


def cli_help() -> str:
    return "\n".join(REQUIRED_EXEC_FLAGS)


class HostObserverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.executable = self.root / "bin" / "codex"
        self.executable.parent.mkdir()
        self.executable.write_bytes(b"codex executable fixture\n")
        self.executable.chmod(0o755)
        self.project = self.root / "project"
        (self.project / ".codex").mkdir(parents=True)
        self.config = self.project / ".codex" / "config.toml"
        self.config.write_text('model = "gpt-5.6-terra"\n', encoding="utf-8")
        self.instructions = self.project / "AGENTS.md"
        self.instructions.write_text(
            "Keep the observation read-only.\n", encoding="utf-8"
        )
        self.project_input = self.project / "input.txt"
        self.project_input.write_text("sealed input\n", encoding="utf-8")
        self.capture = seal(
            {
                "schema": CLI_CAPTURE_SCHEMA,
                "producer_id": "fixture-producer",
                "version_output": "codex-cli 0.147.0\n",
                "exec_help_output": cli_help(),
            },
            "capture_sha256",
        )
        self.policy = seal(
            {
                "schema": POLICY_SCHEMA,
                "policy_id": "observer-policy-v1",
                "allowed_contributor_classes": list(CONTRIBUTOR_CLASSES),
                "allowed_nonsecret_environment_names": ["CODEX_HOME"],
                "secret_basenames": list(SECRET_BASENAMES),
                "secret_pattern_version": "builtin-secret-patterns/1",
            }
        )
        self.grammar = self._grammar()
        self.request = self._request()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _entry(
        self,
        contributor: str,
        path: Path,
        *,
        expectation: str,
        content_policy: str,
    ) -> dict[str, object]:
        return {
            "entry_id": f"entry-{contributor}",
            "contributor_class": contributor,
            "path": str(path),
            "expectation": expectation,
            "content_policy": content_policy,
        }

    def _grammar(self) -> dict[str, object]:
        present = {
            "executable": (self.executable, "OPAQUE_EXECUTABLE"),
            "project_config": (self.config, "TEXT_NO_SECRETS"),
            "project_instructions": (self.instructions, "TEXT_NO_SECRETS"),
            "project_inputs": (self.project_input, "TEXT_NO_SECRETS"),
        }
        entries: list[dict[str, object]] = []
        states: dict[str, str] = {}
        asserted = {"session_flags", "environment"}
        for contributor in CONTRIBUTOR_CLASSES:
            if contributor in asserted:
                states[contributor] = "ASSERTED_INPUT_ONLY"
            elif contributor in present:
                states[contributor] = "FILE_ENTRIES"
                path, content_policy = present[contributor]
                entries.append(
                    self._entry(
                        contributor,
                        path,
                        expectation="REGULAR_FILE",
                        content_policy=content_policy,
                    )
                )
            else:
                states[contributor] = "ABSENT"
                entries.append(
                    self._entry(
                        contributor,
                        self.root / "absent" / f"{contributor}.toml",
                        expectation="ABSENT",
                        content_policy="NONE",
                    )
                )
        return seal(
            {
                "schema": GRAMMAR_SCHEMA,
                "grammar_id": "codex-context-0147-v1",
                "source_revision": "a" * 64,
                "config_precedence": list(CONFIG_PRECEDENCE),
                "project_config_policy": "CONTENT_ADDRESSED_REQUIRED",
                "instruction_precedence": [
                    "AGENTS.override.md",
                    "AGENTS.md",
                    "CONFIGURED_FALLBACK",
                ],
                "instruction_byte_budget": 32_768,
                "symlink_policy": "REFUSE",
                "dynamic_source_policy": "EXPLICIT_OR_INCOMPLETE",
                "contributor_states": states,
                "entries": entries,
                "session_flags": ["--ignore-user-config", "--ignore-rules"],
                "environment_projection": [
                    {
                        "name": "CODEX_HOME",
                        "classification": "NON_SECRET_ASSERTED",
                        "value": str(self.root / "codex-home"),
                        "present": True,
                    },
                    {
                        "name": "OPENAI_API_KEY",
                        "classification": "SECRET_PRESENCE_ONLY",
                        "value": None,
                        "present": False,
                    },
                ],
            }
        )

    def _request(self, **limit_overrides: int) -> dict[str, object]:
        limits = {
            "max_entries": 100,
            "max_total_bytes": 1_000_000,
            "max_file_bytes": 100_000,
            "max_depth": 16,
            "max_retries": 0,
            "max_duration_ms": 30_000,
        }
        limits.update(limit_overrides)
        return seal(
            {
                "schema": REQUEST_SCHEMA,
                "request_id": "observation-123",
                "operation_id": "operation-123",
                "observed_at_utc": "2026-08-23T14:00:00Z",
                "expires_at_utc": "2026-08-23T15:00:00Z",
                "cwd": str(self.project),
                "workspace_boundary": str(self.project),
                "codex_home": str(self.root / "codex-home"),
                "executable_path": str(self.executable),
                "expected_executable_sha256": hashlib.sha256(
                    self.executable.read_bytes()
                ).hexdigest(),
                "cli_capture_sha256": self.capture["capture_sha256"],
                "discovery_grammar_sha256": self.grammar["record_sha256"],
                "observation_policy_sha256": self.policy["record_sha256"],
                "read_roots": [str(self.root)],
                "limits": limits,
            }
        )

    def _observe(self) -> dict[str, object]:
        return observe_host_v1(self.request, self.grammar, self.policy, self.capture)

    def test_happy_path_is_bounded_inert_and_independently_verifiable(self) -> None:
        bundle = self._observe()
        self.assertEqual(bundle["state"], "OBSERVED_NOT_QUALIFIED")
        self.assertEqual(bundle["dispatch"], "NOT_ATTEMPTED")
        self.assertEqual(bundle["authority"], "NOT_GRANTED")
        self.assertEqual(bundle["descriptors"]["executable"]["state"], "NOT_EXECUTED")
        self.assertEqual(
            bundle["descriptors"]["cli_capture"]["binding_state"],
            "ASSERTED_BINDING_ONLY",
        )
        receipt = verify_host_observation_v1(
            self.request, self.grammar, self.policy, self.capture, bundle
        )
        self.assertEqual(receipt["state"], "HOST_OBSERVATION_VERIFIED_NOT_QUALIFIED")
        self.assertEqual(receipt["authority"], "NOT_GRANTED")

    def test_01_project_config_cannot_be_claimed_ignored(self) -> None:
        grammar = copy.deepcopy(self.grammar)
        grammar["project_config_policy"] = "PROJECT_CONFIG_IGNORED"
        reseal(grammar)
        with self.assertRaisesRegex(HostObserverError, "may not be claimed ignored"):
            observe_host_v1(self.request, grammar, self.policy, self.capture)
        grammar = copy.deepcopy(self.grammar)
        grammar["session_flags"].append("--ignore-project-config")
        reseal(grammar)
        with self.assertRaisesRegex(HostObserverError, "unsupported"):
            observe_host_v1(self.request, grammar, self.policy, self.capture)

    def test_02_instruction_precedence_and_budget_fail_closed(self) -> None:
        grammar = copy.deepcopy(self.grammar)
        grammar["instruction_precedence"].reverse()
        reseal(grammar)
        with self.assertRaisesRegex(HostObserverError, "instruction precedence"):
            observe_host_v1(self.request, grammar, self.policy, self.capture)
        grammar = copy.deepcopy(self.grammar)
        grammar["instruction_byte_budget"] = 1
        reseal(grammar)
        request = copy.deepcopy(self.request)
        request["discovery_grammar_sha256"] = grammar["record_sha256"]
        reseal(request)
        bundle = observe_host_v1(request, grammar, self.policy, self.capture)
        self.assertEqual(bundle["state"], "LIMIT_EXCEEDED")
        self.assertEqual(bundle["failures"][0]["code"], "INSTRUCTION_BUDGET_EXCEEDED")

    def test_03_symlinked_instruction_refuses(self) -> None:
        target = self.project / "real-agents.md"
        target.write_text("safe\n", encoding="utf-8")
        self.instructions.unlink()
        self.instructions.symlink_to(target)
        bundle = self._observe()
        self.assertEqual(bundle["state"], "INCOMPLETE_CONTEXT_CLOSURE")
        self.assertEqual(bundle["failures"][0]["code"], "SYMLINK_REFUSED")

    def test_04_hard_linked_config_refuses(self) -> None:
        os.link(self.config, self.project / ".codex" / "config-copy.toml")
        bundle = self._observe()
        self.assertEqual(bundle["state"], "INCOMPLETE_CONTEXT_CLOSURE")
        self.assertEqual(bundle["failures"][0]["code"], "HARD_LINK_REFUSED")

    def test_05_file_replacement_during_read_refuses_without_partial_output(
        self,
    ) -> None:
        original_read = os.read
        replaced = False
        read_calls = 0

        def racing_read(fd: int, count: int) -> bytes:
            nonlocal read_calls, replaced
            read_calls += 1
            result = original_read(fd, count)
            if read_calls == 3 and not replaced:
                replaced = True
                replacement = self.project / ".codex" / "replacement.toml"
                replacement.write_text('model = "replacement"\n', encoding="utf-8")
                replacement.replace(self.config)
            return result

        with patch("house.worker_exec.host_observer.os.read", side_effect=racing_read):
            bundle = self._observe()
        self.assertEqual(bundle["state"], "UNSTABLE_RETRY_REQUIRED")
        self.assertEqual(bundle["observations"], [])
        self.assertIsNone(bundle["descriptors"])

    def test_06_directory_mutation_during_read_refuses(self) -> None:
        original_read = os.read
        changed = False

        def racing_read(fd: int, count: int) -> bytes:
            nonlocal changed
            result = original_read(fd, count)
            if not changed:
                changed = True
                (self.executable.parent / "new-child").write_text("x", encoding="utf-8")
            return result

        with patch("house.worker_exec.host_observer.os.read", side_effect=racing_read):
            bundle = self._observe()
        self.assertEqual(bundle["state"], "UNSTABLE_RETRY_REQUIRED")

    def test_07_secret_path_content_and_environment_values_refuse(self) -> None:
        cases: list[tuple[str, dict[str, object], str]] = []
        grammar = copy.deepcopy(self.grammar)
        config_entry = next(
            item
            for item in grammar["entries"]
            if item["contributor_class"] == "project_config"
        )
        secret_path = self.project / ".codex" / "auth.json"
        secret_path.write_text("{}\n", encoding="utf-8")
        config_entry["path"] = str(secret_path)
        reseal(grammar)
        cases.append(("path", grammar, "INCOMPLETE_SECRET_DEPENDENCY"))

        self.config.write_text('api_key = "abcdefghijk"\n', encoding="utf-8")
        cases.append(("content", self.grammar, "INCOMPLETE_SECRET_DEPENDENCY"))
        for label, candidate, state in cases:
            request = copy.deepcopy(self.request)
            request["discovery_grammar_sha256"] = candidate["record_sha256"]
            reseal(request)
            with self.subTest(label=label):
                self.assertEqual(
                    observe_host_v1(request, candidate, self.policy, self.capture)[
                        "state"
                    ],
                    state,
                )

        grammar = copy.deepcopy(self.grammar)
        grammar["environment_projection"][1]["value"] = "not-allowed"
        reseal(grammar)
        with self.assertRaisesRegex(HostObserverError, "secret environment value"):
            observe_host_v1(self.request, grammar, self.policy, self.capture)

    def test_08_omitted_or_unknown_contributor_refuses(self) -> None:
        grammar = copy.deepcopy(self.grammar)
        del grammar["contributor_states"]["mcp"]
        reseal(grammar)
        with self.assertRaisesRegex(HostObserverError, "fields are not exact"):
            observe_host_v1(self.request, grammar, self.policy, self.capture)
        grammar = copy.deepcopy(self.grammar)
        grammar["contributor_states"]["mcp"] = "DYNAMIC_UNKNOWN"
        reseal(grammar)
        with self.assertRaisesRegex(HostObserverError, "invalid contributor state"):
            observe_host_v1(self.request, grammar, self.policy, self.capture)

    def test_09_cli_capture_and_executable_bindings_refuse(self) -> None:
        capture = copy.deepcopy(self.capture)
        capture["version_output"] = "codex-cli 9.9.9"
        reseal(capture, "capture_sha256")
        request = copy.deepcopy(self.request)
        request["cli_capture_sha256"] = capture["capture_sha256"]
        reseal(request)
        bundle = observe_host_v1(request, self.grammar, self.policy, capture)
        self.assertEqual(bundle["state"], "REJECTED_REQUEST")
        self.assertEqual(bundle["failures"][0]["code"], "CLI_CAPTURE_CONTRACT_MISMATCH")

        request = copy.deepcopy(self.request)
        request["expected_executable_sha256"] = "f" * 64
        reseal(request)
        bundle = observe_host_v1(request, self.grammar, self.policy, self.capture)
        self.assertEqual(bundle["state"], "INCOMPLETE_CONTEXT_CLOSURE")
        self.assertEqual(bundle["failures"][0]["code"], "EXECUTABLE_HASH_MISMATCH")

    def test_10_duplicate_casefolded_paths_refuse(self) -> None:
        grammar = copy.deepcopy(self.grammar)
        duplicate = copy.deepcopy(
            next(
                item
                for item in grammar["entries"]
                if item["contributor_class"] == "project_config"
            )
        )
        duplicate["entry_id"] = "different-entry"
        duplicate["path"] = str(duplicate["path"]).upper()
        duplicate["contributor_class"] = "project_inputs"
        grammar["entries"].append(duplicate)
        reseal(grammar)
        with self.assertRaisesRegex(HostObserverError, "colliding"):
            observe_host_v1(self.request, grammar, self.policy, self.capture)

    def test_11_entry_byte_depth_duration_and_retry_limits_refuse(self) -> None:
        requests = {
            "entries": self._request(max_entries=1),
            "bytes": self._request(max_total_bytes=1),
            "file": self._request(max_file_bytes=1),
            "depth": self._request(max_depth=1),
        }
        for label, request in requests.items():
            with self.subTest(label=label):
                self.assertEqual(
                    observe_host_v1(request, self.grammar, self.policy, self.capture)[
                        "state"
                    ],
                    "LIMIT_EXCEEDED",
                )
        with patch(
            "house.worker_exec.host_observer.time.monotonic_ns",
            side_effect=[0, 31_000_000_000],
        ):
            request = self._request(max_duration_ms=30_000)
            self.assertEqual(
                observe_host_v1(request, self.grammar, self.policy, self.capture)[
                    "state"
                ],
                "LIMIT_EXCEEDED",
            )

    def test_12_negative_bundle_cannot_expose_partial_descriptors(self) -> None:
        request = self._request(max_entries=1)
        bundle = observe_host_v1(request, self.grammar, self.policy, self.capture)
        bundle["observations"] = [{"leaked": True}]
        reseal(bundle)
        with self.assertRaisesRegex(HostObserverError, "partial descriptors"):
            verify_host_observation_v1(
                request, self.grammar, self.policy, self.capture, bundle
            )

    def test_13_invalid_time_and_operation_binding_refuse(self) -> None:
        request = copy.deepcopy(self.request)
        request["expires_at_utc"] = request["observed_at_utc"]
        reseal(request)
        with self.assertRaisesRegex(HostObserverError, "observation interval"):
            observe_host_v1(request, self.grammar, self.policy, self.capture)
        bundle = self._observe()
        changed = copy.deepcopy(self.request)
        changed["operation_id"] = "different-operation"
        reseal(changed)
        with self.assertRaisesRegex(HostObserverError, "binding mismatch"):
            verify_host_observation_v1(
                changed, self.grammar, self.policy, self.capture, bundle
            )

    def test_14_verifier_is_pure_under_ambient_api_failure(self) -> None:
        bundle = self._observe()

        def forbidden(*_args: object, **_kwargs: object) -> object:
            raise AssertionError("ambient API used by pure verifier")

        targets = (
            (builtins, "open"),
            (os, "open"),
            (os, "stat"),
            (os, "fstat"),
            (os, "read"),
            (os, "getenv"),
            (time, "time"),
            (time, "monotonic_ns"),
            (socket, "socket"),
            (subprocess, "run"),
            (subprocess, "Popen"),
        )
        with ExitStack() as stack:
            for module, name in targets:
                stack.enter_context(patch.object(module, name, side_effect=forbidden))
            receipt = verify_host_observation_v1(
                self.request, self.grammar, self.policy, self.capture, bundle
            )
        self.assertEqual(receipt["state"], "HOST_OBSERVATION_VERIFIED_NOT_QUALIFIED")

    def test_15_custom_mapping_subclasses_are_rejected(self) -> None:
        class CustomDict(dict[str, object]):
            pass

        with self.assertRaisesRegex(HostObserverError, "invalid observation request"):
            observe_host_v1(
                CustomDict(self.request), self.grammar, self.policy, self.capture
            )

    def test_16_success_bundle_is_deep_copied_from_asserted_inputs(self) -> None:
        bundle = self._observe()
        self.grammar["session_flags"].append("--later-mutation")
        self.assertNotIn(
            "--later-mutation",
            bundle["descriptors"]["effective_context"]["session_flags"],
        )

    def test_17_retry_restarts_the_entire_observation_without_mixing(self) -> None:
        request = self._request(max_retries=1)
        original_read = os.read
        replaced = False
        read_calls = 0
        replacement_bytes = b'model = "replacement"\n'

        def racing_read(fd: int, count: int) -> bytes:
            nonlocal read_calls, replaced
            read_calls += 1
            result = original_read(fd, count)
            if read_calls == 3 and not replaced:
                replaced = True
                replacement = self.project / ".codex" / "replacement.toml"
                replacement.write_bytes(replacement_bytes)
                replacement.replace(self.config)
            return result

        with patch("house.worker_exec.host_observer.os.read", side_effect=racing_read):
            bundle = observe_host_v1(request, self.grammar, self.policy, self.capture)
        self.assertEqual(bundle["state"], "OBSERVED_NOT_QUALIFIED")
        self.assertEqual(bundle["attempt_count"], 2)
        config_observation = next(
            item
            for item in bundle["observations"]
            if item["contributor_class"] == "project_config"
        )
        self.assertEqual(
            config_observation["content_sha256"],
            hashlib.sha256(replacement_bytes).hexdigest(),
        )

    def test_18_special_file_and_missing_required_file_refuse(self) -> None:
        fifo = self.project / "input-fifo"
        os.mkfifo(fifo)
        grammar = copy.deepcopy(self.grammar)
        entry = next(
            item
            for item in grammar["entries"]
            if item["contributor_class"] == "project_inputs"
        )
        entry["path"] = str(fifo)
        reseal(grammar)
        request = copy.deepcopy(self.request)
        request["discovery_grammar_sha256"] = grammar["record_sha256"]
        reseal(request)
        bundle = observe_host_v1(request, grammar, self.policy, self.capture)
        self.assertEqual(bundle["state"], "INCOMPLETE_CONTEXT_CLOSURE")
        self.assertEqual(bundle["failures"][0]["code"], "SPECIAL_FILE_REFUSED")

        self.project_input.unlink()
        bundle = self._observe()
        self.assertEqual(bundle["state"], "INCOMPLETE_CONTEXT_CLOSURE")
        self.assertEqual(bundle["failures"][0]["code"], "REQUIRED_FILE_MISSING")

    def test_19_observer_never_invokes_network_process_or_host_environment(
        self,
    ) -> None:
        def forbidden(*_args: object, **_kwargs: object) -> object:
            raise AssertionError("forbidden ambient authority surface used")

        targets = (
            (os, "getenv"),
            (socket, "socket"),
            (subprocess, "run"),
            (subprocess, "Popen"),
        )
        with ExitStack() as stack:
            for module, name in targets:
                stack.enter_context(patch.object(module, name, side_effect=forbidden))
            bundle = self._observe()
        self.assertEqual(bundle["state"], "OBSERVED_NOT_QUALIFIED")


if __name__ == "__main__":
    unittest.main()

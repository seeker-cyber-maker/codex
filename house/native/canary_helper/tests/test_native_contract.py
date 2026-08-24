from __future__ import annotations

import hashlib
import json
import plistlib
import re
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from house.native.canary_helper.artifact_inspection import (
    CODESIGN,
    QUALIFIED_STATE,
    REFUSED_STATE,
    inspect_candidate,
)
from house.native.canary_helper.build_objects import build_objects
from house.native.canary_helper.run_codec_tests import run_codec_tests

ROOT = Path(__file__).resolve().parents[1]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class StaticNativeContractTests(unittest.TestCase):
    def test_sources_compile_to_non_executable_objects_without_forbidden_symbols(self) -> None:
        with tempfile.TemporaryDirectory(prefix="house-canary-objects-") as directory:
            receipt = build_objects(ROOT, directory)
            self.assertEqual(
                receipt["state"], "STATIC_OBJECTS_BUILT_NO_LINK_NO_LAUNCH"
            )
            self.assertEqual(receipt["candidate_launch"], "NOT_ATTEMPTED")
            self.assertEqual(receipt["link"], "NOT_ATTEMPTED")
            self.assertEqual(
                set(receipt["objects"]),
                {
                    "protocol.c",
                    "parent_contract.c",
                    "helper_contract.c",
                    "parent_main.c",
                    "helper_main.c",
                },
            )
            for record in receipt["objects"].values():
                self.assertFalse(record["executable"])
                self.assertEqual(record["forbidden_symbols"], [])

    def test_contract_sources_have_no_runtime_capability_api(self) -> None:
        forbidden = (
            r"\bmain\s*\(",
            r"\bposix_spawn\s*\(",
            r"\bfork\s*\(",
            r"\bexec[a-z]*\s*\(",
            r"\bsystem\s*\(",
            r"\bpopen\s*\(",
            r"\bsocket\s*\(",
            r"\bconnect\s*\(",
            r"\bopen\s*\(",
            r"\bgetenv\s*\(",
            r"\bsetenv\s*\(",
        )
        for name in ("parent_contract.c", "helper_contract.c"):
            source = (ROOT / name).read_text(encoding="utf-8")
            for pattern in forbidden:
                self.assertIsNone(re.search(pattern, source), (name, pattern))
            self.assertIn("DH_CANARY_LAUNCH_DISABLED", source)

    def test_entrypoint_admission_is_positive_and_test_macro_only_omits_main(self) -> None:
        forbidden = (
            r"\bposix_spawn\s*\(",
            r"\bfork\s*\(",
            r"\bexec[a-z]*\s*\(",
            r"\bsystem\s*\(",
            r"\bpopen\s*\(",
            r"\bsocket\s*\(",
            r"\bconnect\s*\(",
            r"\bopen\s*\(",
            r"\bgetenv\s*\(",
            r"\bsetenv\s*\(",
        )
        for name, function in (
            ("parent_main.c", "dh_parent_entrypoint_admit"),
            ("helper_main.c", "dh_helper_entrypoint_admit"),
        ):
            source = (ROOT / name).read_text(encoding="utf-8")
            self.assertEqual(source.count("DH_CANARY_ENTRYPOINT_UNIT_TEST"), 1)
            macro_offset = source.index("DH_CANARY_ENTRYPOINT_UNIT_TEST")
            guard_start = source.rfind("#ifndef ", 0, macro_offset)
            self.assertGreaterEqual(guard_start, 0)
            admission_region = source[:guard_start]
            self.assertNotRegex(
                admission_region,
                r"(?m)^\s*#\s*(?:if|ifdef|ifndef|elif|else|endif)\b",
            )
            self.assertRegex(
                source[guard_start:],
                r"(?s)^#ifndef DH_CANARY_ENTRYPOINT_UNIT_TEST\n"
                r"int main\(int argc, char \*argv\[\]\) \{.*?\n}\n#endif\s*$",
            )
            self.assertIn(f"int {function}_from_proof", source)
            self.assertIn("DH_CANARY_ADMISSION_ACCEPTED", source)
            self.assertIn("DH_CANARY_ADMISSION_FD_CONTRACT", source)
            self.assertIn("DH_CANARY_ADMISSION_PROTOCOL_CONTRACT", source)
            for pattern in forbidden:
                self.assertIsNone(re.search(pattern, source), (name, pattern))

    def test_entitlement_files_are_exact_minimal_sets(self) -> None:
        parent = plistlib.loads((ROOT / "parent.entitlements.plist").read_bytes())
        helper = plistlib.loads((ROOT / "helper.entitlements.plist").read_bytes())
        self.assertEqual(parent, {"com.apple.security.app-sandbox": True})
        self.assertEqual(
            helper,
            {
                "com.apple.security.app-sandbox": True,
                "com.apple.security.inherit": True,
            },
        )

    def test_protocol_layout_and_transition_names_are_fixed(self) -> None:
        header = (ROOT / "protocol.h").read_text(encoding="utf-8")
        self.assertRegex(header, r"DH_CANARY_HEADER_LENGTH\s+80u")
        self.assertRegex(header, r"DH_CANARY_OFFSET_ATTEMPT_NONCE\s+48u")
        expected = [
            "DH_CANARY_FRAME_READY",
            "DH_CANARY_FRAME_CANARY_HELD",
            "DH_CANARY_FRAME_PREPARED_TO_RELEASE",
            "DH_CANARY_FRAME_RELEASE_ONCE",
            "DH_CANARY_FRAME_TERMINAL",
        ]
        positions = [header.index(name) for name in expected]
        self.assertEqual(positions, sorted(positions))

    def test_pure_codec_contract_executable_passes_without_identity(self) -> None:
        with tempfile.TemporaryDirectory(prefix="house-canary-codec-test-") as directory:
            receipt = run_codec_tests(ROOT, directory)
            self.assertEqual(
                receipt["state"], "PURE_CODEC_AND_ENTRYPOINT_TESTS_LINKED_AND_PASSED"
            )
            self.assertEqual(receipt["run_returncode"], 0)
            self.assertEqual(receipt["entrypoint_run_returncode"], 0)
            self.assertEqual(receipt["test_executable_signature"], "adhoc")
            self.assertEqual(receipt["test_executable_team_identifier"], "not set")
            self.assertEqual(receipt["entrypoint_test_executable_signature"], "adhoc")
            self.assertEqual(
                receipt["entrypoint_test_executable_team_identifier"], "not set"
            )
            self.assertEqual(receipt["candidate_link"], "NOT_ATTEMPTED")
            self.assertEqual(receipt["candidate_launch"], "NOT_ATTEMPTED")
            self.assertEqual(receipt["identity_signing"], "NOT_ATTEMPTED")
            self.assertEqual(receipt["private_output_directory_mode"], "0700")
            self.assertEqual(
                receipt["private_output_cleanup"],
                "COMPLETED_BEFORE_RECEIPT_RETURN",
            )
            self.assertFalse(Path(receipt["private_output_directory"]).exists())
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_codec_output_root_symlink_is_rejected_before_compiler(self) -> None:
        with tempfile.TemporaryDirectory(prefix="house-canary-codec-symlink-") as directory:
            root = Path(directory)
            real_output = root / "real"
            real_output.mkdir()
            linked_output = root / "linked"
            linked_output.symlink_to(real_output)
            with patch(
                "house.native.canary_helper.run_codec_tests.subprocess.run"
            ) as runner, self.assertRaisesRegex(RuntimeError, "must not be a symlink"):
                run_codec_tests(ROOT, linked_output)
            runner.assert_not_called()
            self.assertEqual(list(real_output.iterdir()), [])

    def test_codec_compile_timeout_cleans_private_output(self) -> None:
        with tempfile.TemporaryDirectory(prefix="house-canary-codec-timeout-") as directory:
            def timeout(*args: object, **kwargs: object) -> None:
                raise subprocess.TimeoutExpired(args[0], kwargs["timeout"])

            with patch(
                "house.native.canary_helper.run_codec_tests.subprocess.run",
                side_effect=timeout,
            ), self.assertRaisesRegex(
                RuntimeError, "codec test link timed out after 30 seconds"
            ):
                run_codec_tests(ROOT, directory)
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_codec_signature_timeout_cleans_private_output(self) -> None:
        with tempfile.TemporaryDirectory(prefix="house-canary-signature-timeout-") as directory:
            real_run = subprocess.run

            def timeout_codesign(*args: object, **kwargs: object):
                argv = args[0]
                if argv[0] == CODESIGN:
                    raise subprocess.TimeoutExpired(argv, kwargs["timeout"])
                return real_run(*args, **kwargs)

            with patch(
                "house.native.canary_helper.run_codec_tests.subprocess.run",
                side_effect=timeout_codesign,
            ), self.assertRaisesRegex(
                RuntimeError,
                "codec signature inspection timed out after 10 seconds",
            ):
                run_codec_tests(ROOT, directory)
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_codec_execution_timeout_cleans_private_output(self) -> None:
        with tempfile.TemporaryDirectory(prefix="house-canary-execution-timeout-") as directory:
            real_run = subprocess.run

            def timeout_executable(*args: object, **kwargs: object):
                argv = args[0]
                if len(argv) == 1 and argv[0].endswith("/codec_contract_test"):
                    raise subprocess.TimeoutExpired(argv, kwargs["timeout"])
                return real_run(*args, **kwargs)

            with patch(
                "house.native.canary_helper.run_codec_tests.subprocess.run",
                side_effect=timeout_executable,
            ), self.assertRaisesRegex(
                RuntimeError, "codec contract test timed out after 5 seconds"
            ):
                run_codec_tests(ROOT, directory)
            self.assertEqual(list(Path(directory).iterdir()), [])


class ArtifactInspectionTests(unittest.TestCase):
    def _fixture(self, root: Path) -> tuple[dict[str, object], dict[str, dict[str, object]]]:
        parent = root / "Contents" / "MacOS" / "DreamHouseCanaryParent"
        helper = root / "Contents" / "Helpers" / "DreamHouseCanaryHelper"
        parent.parent.mkdir(parents=True)
        helper.parent.mkdir(parents=True)
        parent.write_bytes(b"sealed-parent-fixture")
        helper.write_bytes(b"sealed-helper-fixture")
        records = {
            "parent": {
                "path": parent,
                "cdhash": "a" * 40,
                "requirement": 'identifier "house.parent" and anchor apple generic and certificate leaf[subject.OU] = TEAM123456',
                "entitlements": {"com.apple.security.app-sandbox": True},
            },
            "helper": {
                "path": helper,
                "cdhash": "b" * 40,
                "requirement": 'identifier "house.helper" and anchor apple generic and certificate leaf[subject.OU] = TEAM123456',
                "entitlements": {
                    "com.apple.security.app-sandbox": True,
                    "com.apple.security.inherit": True,
                },
            },
        }
        policy: dict[str, object] = {
            "schema": "dream-house-canary-signing-policy/2",
            "state": "SEALED_CANDIDATE",
            "platform_build": "TEST-BUILD",
            "artifacts": {},
        }
        artifacts: dict[str, object] = {}
        for name, record in records.items():
            artifacts[name] = {
                "relative_path": str(record["path"].relative_to(root)),
                "size": record["path"].stat().st_size,
                "sha256": _sha256(record["path"]),
                "cdhash": record["cdhash"],
                "team_identifier": "TEAM123456",
                "designated_requirement": record["requirement"],
                "entitlements": record["entitlements"],
            }
        policy["artifacts"] = artifacts
        return policy, records

    def _runner(self, records: dict[str, dict[str, object]], commands: list[list[str]]):
        def run(argv: list[str]) -> subprocess.CompletedProcess[str]:
            commands.append(argv)
            self.assertEqual(argv[0], CODESIGN)
            path = Path(argv[-1])
            name = "parent" if path.name.endswith("Parent") else "helper"
            record = records[name]
            if "--verify" in argv:
                return subprocess.CompletedProcess(argv, 0, "", "")
            if "--requirements" in argv:
                return subprocess.CompletedProcess(
                    argv, 0, "", f"designated => {record['requirement']}\n"
                )
            if "--entitlements" in argv:
                xml = plistlib.dumps(record["entitlements"], fmt=plistlib.FMT_XML).decode()
                return subprocess.CompletedProcess(argv, 0, xml, "")
            metadata = (
                f"Identifier=house.{name}\n"
                f"Format={record.get('format', 'Mach-O 64-bit executable arm64')}\n"
                "Signature size=9000\n"
                f"TeamIdentifier=TEAM123456\nCDHash={record['cdhash']}\n"
            )
            return subprocess.CompletedProcess(argv, 0, "", metadata)

        return run

    def test_sealed_exact_candidate_is_statically_qualified_without_launch(self) -> None:
        with tempfile.TemporaryDirectory(prefix="house-canary-signed-fixture-") as directory:
            root = Path(directory)
            policy, records = self._fixture(root)
            commands: list[list[str]] = []
            result = inspect_candidate(
                root,
                policy,
                runner=self._runner(records, commands),
                platform_build_provider=lambda: "TEST-BUILD",
            )
            self.assertEqual(result["state"], QUALIFIED_STATE)
            self.assertEqual(result["candidate_launch"], "NOT_ATTEMPTED")
            self.assertEqual(len(commands), 8)
            self.assertTrue(all(command[0] == CODESIGN for command in commands))
            source_paths = {str(record["path"]) for record in records.values()}
            self.assertTrue(all(command[-1] not in source_paths for command in commands))
            self.assertTrue(all(not Path(command[-1]).exists() for command in commands))
            self.assertEqual(result["inspection_subject"], "PRIVATE_PINNED_FD_COPY")

    def test_unconfigured_policy_refuses_before_tool_invocation(self) -> None:
        policy = json.loads((ROOT / "signing_policy.json").read_text())
        commands: list[list[str]] = []

        def runner(argv: list[str]) -> subprocess.CompletedProcess[str]:
            commands.append(argv)
            raise AssertionError("codesign must not run")

        result = inspect_candidate(
            ROOT,
            policy,
            runner=runner,
            platform_build_provider=lambda: "TEST-BUILD",
        )
        self.assertEqual(result["state"], REFUSED_STATE)
        self.assertIn("not SEALED_CANDIDATE", result["reason"])
        self.assertEqual(commands, [])

    def test_extra_helper_entitlement_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="house-canary-extra-entitlement-") as directory:
            root = Path(directory)
            policy, records = self._fixture(root)
            records["helper"]["entitlements"] = {
                "com.apple.security.app-sandbox": True,
                "com.apple.security.inherit": True,
                "com.apple.security.network.client": True,
            }
            result = inspect_candidate(
                root,
                policy,
                runner=self._runner(records, []),
                platform_build_provider=lambda: "TEST-BUILD",
            )
            self.assertEqual(result["state"], REFUSED_STATE)
            self.assertIn("entitlement set mismatch", result["reason"])

    def test_symlink_artifact_is_rejected_before_codesign(self) -> None:
        with tempfile.TemporaryDirectory(prefix="house-canary-symlink-") as directory:
            root = Path(directory)
            policy, records = self._fixture(root)
            parent = records["parent"]["path"]
            parent.unlink()
            parent.symlink_to(records["helper"]["path"])
            commands: list[list[str]] = []
            result = inspect_candidate(
                root,
                policy,
                runner=self._runner(records, commands),
                platform_build_provider=lambda: "TEST-BUILD",
            )
            self.assertEqual(result["state"], REFUSED_STATE)
            self.assertIn("symlink", result["reason"])
            self.assertEqual(commands, [])

    def test_symlinked_parent_directory_is_rejected_before_codesign(self) -> None:
        with tempfile.TemporaryDirectory(prefix="house-canary-symlink-parent-") as directory:
            root = Path(directory)
            policy, records = self._fixture(root)
            (root / "Contents").rename(root / "RealContents")
            (root / "Contents").symlink_to(root / "RealContents")
            commands: list[list[str]] = []
            result = inspect_candidate(
                root,
                policy,
                runner=self._runner(records, commands),
                platform_build_provider=lambda: "TEST-BUILD",
            )
            self.assertEqual(result["state"], REFUSED_STATE)
            self.assertIn("path component is a symlink", result["reason"])
            self.assertEqual(commands, [])

    def test_normalizing_path_components_are_rejected_before_codesign(self) -> None:
        with tempfile.TemporaryDirectory(prefix="house-canary-path-normalization-") as directory:
            root = Path(directory)
            policy, records = self._fixture(root)
            for relative_path in (".", "Contents/./MacOS/DreamHouseCanaryParent"):
                with self.subTest(relative_path=relative_path):
                    policy["artifacts"]["parent"]["relative_path"] = relative_path
                    commands: list[list[str]] = []
                    result = inspect_candidate(
                        root,
                        policy,
                        runner=self._runner(records, commands),
                        platform_build_provider=lambda: "TEST-BUILD",
                    )
                    self.assertEqual(result["state"], REFUSED_STATE)
                    self.assertIn("strict relative path", result["reason"])
                    self.assertEqual(commands, [])

    def test_platform_build_mismatch_is_rejected_before_codesign(self) -> None:
        with tempfile.TemporaryDirectory(prefix="house-canary-platform-drift-") as directory:
            root = Path(directory)
            policy, records = self._fixture(root)
            commands: list[list[str]] = []
            result = inspect_candidate(
                root,
                policy,
                runner=self._runner(records, commands),
                platform_build_provider=lambda: "DIFFERENT-BUILD",
            )
            self.assertEqual(result["state"], REFUSED_STATE)
            self.assertIn("platform_build does not match", result["reason"])
            self.assertEqual(commands, [])

    def test_default_codesign_timeout_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="house-canary-codesign-timeout-") as directory:
            root = Path(directory)
            policy, _ = self._fixture(root)
            with patch(
                "house.native.canary_helper.artifact_inspection.subprocess.run",
                side_effect=subprocess.TimeoutExpired([CODESIGN], 10),
            ) as runner:
                result = inspect_candidate(
                    root,
                    policy,
                    platform_build_provider=lambda: "TEST-BUILD",
                )
            self.assertEqual(result["state"], REFUSED_STATE)
            self.assertIn("codesign timed out after 10 seconds", result["reason"])
            self.assertEqual(result["candidate_launch"], "NOT_ATTEMPTED")
            self.assertEqual(runner.call_args.kwargs["timeout"], 10)

    def test_source_replacement_during_snapshot_inspection_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="house-canary-source-race-") as directory:
            root = Path(directory)
            policy, records = self._fixture(root)
            commands: list[list[str]] = []
            base_runner = self._runner(records, commands)
            mutated = False

            def runner(argv: list[str]) -> subprocess.CompletedProcess[str]:
                nonlocal mutated
                result = base_runner(argv)
                if not mutated and "--verify" in argv:
                    Path(records["parent"]["path"]).write_bytes(b"replacement")
                    mutated = True
                return result

            result = inspect_candidate(
                root,
                policy,
                runner=runner,
                platform_build_provider=lambda: "TEST-BUILD",
            )
            self.assertEqual(result["state"], REFUSED_STATE)
            self.assertIn("source content changed", result["reason"])
            self.assertTrue(commands)

    def test_snapshot_mutation_during_codesign_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="house-canary-snapshot-race-") as directory:
            root = Path(directory)
            policy, records = self._fixture(root)
            commands: list[list[str]] = []
            base_runner = self._runner(records, commands)
            mutated = False

            def runner(argv: list[str]) -> subprocess.CompletedProcess[str]:
                nonlocal mutated
                result = base_runner(argv)
                if not mutated and "--verify" in argv:
                    snapshot = Path(argv[-1])
                    snapshot.chmod(0o700)
                    snapshot.write_bytes(b"snapshot-replacement")
                    mutated = True
                return result

            result = inspect_candidate(
                root,
                policy,
                runner=runner,
                platform_build_provider=lambda: "TEST-BUILD",
            )
            self.assertEqual(result["state"], REFUSED_STATE)
            self.assertIn("snapshot changed", result["reason"])

    def test_non_macho_snapshot_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="house-canary-non-macho-") as directory:
            root = Path(directory)
            policy, records = self._fixture(root)
            records["parent"]["format"] = "generic"
            result = inspect_candidate(
                root,
                policy,
                runner=self._runner(records, []),
                platform_build_provider=lambda: "TEST-BUILD",
            )
            self.assertEqual(result["state"], REFUSED_STATE)
            self.assertIn("not a Mach-O", result["reason"])

    def test_size_mismatch_is_rejected_before_codesign(self) -> None:
        with tempfile.TemporaryDirectory(prefix="house-canary-size-drift-") as directory:
            root = Path(directory)
            policy, records = self._fixture(root)
            policy["artifacts"]["parent"]["size"] += 1
            commands: list[list[str]] = []
            result = inspect_candidate(
                root,
                policy,
                runner=self._runner(records, commands),
                platform_build_provider=lambda: "TEST-BUILD",
            )
            self.assertEqual(result["state"], REFUSED_STATE)
            self.assertIn("content size mismatch", result["reason"])
            self.assertEqual(commands, [])


if __name__ == "__main__":
    unittest.main()

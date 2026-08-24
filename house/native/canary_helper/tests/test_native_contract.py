from __future__ import annotations

import hashlib
import json
import plistlib
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

from house.native.canary_helper.artifact_inspection import (
    CODESIGN,
    QUALIFIED_STATE,
    REFUSED_STATE,
    inspect_candidate,
)
from house.native.canary_helper.build_objects import build_objects

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
            for record in receipt["objects"].values():
                self.assertFalse(record["executable"])
                self.assertEqual(record["forbidden_symbols"], [])

    def test_parent_and_helper_have_no_entrypoint_or_runtime_capability_api(self) -> None:
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
            "schema": "dream-house-canary-signing-policy/1",
            "state": "SEALED_CANDIDATE",
            "platform_build": "TEST-BUILD",
            "artifacts": {},
        }
        artifacts: dict[str, object] = {}
        for name, record in records.items():
            artifacts[name] = {
                "relative_path": str(record["path"].relative_to(root)),
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
                f"Identifier=house.{name}\nSignature size=9000\n"
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
                root, policy, runner=self._runner(records, commands)
            )
            self.assertEqual(result["state"], QUALIFIED_STATE)
            self.assertEqual(result["candidate_launch"], "NOT_ATTEMPTED")
            self.assertEqual(len(commands), 8)
            self.assertTrue(all(command[0] == CODESIGN for command in commands))

    def test_unconfigured_policy_refuses_before_tool_invocation(self) -> None:
        policy = json.loads((ROOT / "signing_policy.json").read_text())
        commands: list[list[str]] = []

        def runner(argv: list[str]) -> subprocess.CompletedProcess[str]:
            commands.append(argv)
            raise AssertionError("codesign must not run")

        result = inspect_candidate(ROOT, policy, runner=runner)
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
                root, policy, runner=self._runner(records, [])
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
                root, policy, runner=self._runner(records, commands)
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
                root, policy, runner=self._runner(records, commands)
            )
            self.assertEqual(result["state"], REFUSED_STATE)
            self.assertIn("path component is a symlink", result["reason"])
            self.assertEqual(commands, [])


if __name__ == "__main__":
    unittest.main()

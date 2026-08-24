from __future__ import annotations

import ast
import copy
import hashlib
import json
import plistlib
import tempfile
import unittest
from pathlib import Path

from house.native.canary_helper.candidate_plan import (
    EXPECTED_OPERATION_ORDER,
    MAX_PLAN_BYTES,
    NOT_READY_STATE,
    PLAN_STATE,
    RESOLVED_STATE,
    CandidatePlanError,
    generate_candidate_plan,
    load_candidate_contract,
    validate_candidate_contract,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "candidate_contract.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CandidatePlanTests(unittest.TestCase):
    def _resolved_fixture(
        self, root: Path
    ) -> tuple[dict[str, object], Path, Path]:
        source_root = root / "source"
        output_root = root / "output"
        source_root.mkdir()
        output_root.mkdir()
        contract = copy.deepcopy(load_candidate_contract(CONTRACT_PATH))
        contract["state"] = RESOLVED_STATE

        package = contract["package"]
        parent = package["parent"]
        helper = package["helper"]
        parent["bundle_identifier"] = "com.example.dreamhouse.canary.parent"
        helper["bundle_identifier"] = "com.example.dreamhouse.canary.helper"
        parent["info_plist"]["CFBundleIdentifier"] = parent["bundle_identifier"]
        parent["info_plist"]["LSMinimumSystemVersion"] = "15.0"

        contract["platform"] = {
            "architecture": "arm64",
            "deployment_target": "15.0",
            "developer_dir": "/Applications/Xcode.app/Contents/Developer",
            "sdk_path": "/Applications/Xcode.app/SDKs/MacOSX.sdk",
            "sdk_build": "TEST-SDK-1",
            "toolchain_build": "TEST-TOOLCHAIN-1",
        }
        contract["tools"] = {
            "clang": {
                "absolute_path": "/Applications/Xcode.app/usr/bin/clang",
                "sha256": "1" * 64,
                "version": "Apple clang test",
            },
            "codesign": {
                "absolute_path": "/usr/bin/codesign",
                "sha256": "2" * 64,
                "version": "codesign test",
            },
        }
        for name, artifact in (("parent", parent), ("helper", helper)):
            bundle_identifier = artifact["bundle_identifier"]
            artifact["identity"] = {
                "signing_identity": "Apple Development: Fixture",
                "team_identifier": "TEAM123456",
                "designated_requirement": (
                    f'identifier "{bundle_identifier}" and anchor apple generic '
                    'and certificate leaf[subject.OU] = "TEAM123456"'
                ),
                "cdhash": ("a" if name == "parent" else "b") * 40,
                "size": 4096,
                "sha256": ("c" if name == "parent" else "d") * 64,
            }

        for index, source in enumerate(contract["sources"]):
            path = source_root / source["relative_path"]
            path.write_bytes(f"fixture-source-{index}\n".encode())
            source["sha256"] = _sha256(path)

        entitlement_values = {
            "parent": {"com.apple.security.app-sandbox": True},
            "helper": {
                "com.apple.security.app-sandbox": True,
                "com.apple.security.inherit": True,
            },
        }
        for name, artifact in (("parent", parent), ("helper", helper)):
            path = source_root / artifact["entitlements"]["relative_path"]
            path.write_bytes(
                plistlib.dumps(entitlement_values[name], fmt=plistlib.FMT_XML)
            )
            artifact["entitlements"]["sha256"] = _sha256(path)
        return contract, source_root, output_root

    def test_checked_in_contract_refuses_with_zero_operations(self) -> None:
        contract = load_candidate_contract(CONTRACT_PATH)
        result = validate_candidate_contract(contract, ROOT)
        self.assertEqual(result["state"], NOT_READY_STATE)
        self.assertGreater(len(result["unresolved_paths"]), 0)
        self.assertEqual(result["operations"], [])
        self.assertEqual(result["tool_execution"], "NOT_ATTEMPTED")
        with self.assertRaisesRegex(CandidatePlanError, "contract is unresolved"):
            generate_candidate_plan(contract, ROOT, ROOT)

    def test_closed_schema_rejects_unknown_top_level_field(self) -> None:
        contract = load_candidate_contract(CONTRACT_PATH)
        contract["surprise"] = "field"
        with self.assertRaisesRegex(CandidatePlanError, "unexpected=.*surprise"):
            validate_candidate_contract(contract, ROOT)

    def test_unsafe_source_path_is_rejected(self) -> None:
        contract = load_candidate_contract(CONTRACT_PATH)
        contract["sources"][0]["relative_path"] = "../protocol.c"
        with self.assertRaisesRegex(CandidatePlanError, "unsafe path component"):
            validate_candidate_contract(contract, ROOT)

    def test_source_layout_cannot_drop_future_runtime_entrypoint_inputs(self) -> None:
        contract = load_candidate_contract(CONTRACT_PATH)
        contract["sources"].pop()
        with self.assertRaisesRegex(CandidatePlanError, "source layout"):
            validate_candidate_contract(contract, ROOT)

    def test_helper_cannot_silently_become_a_nested_bundle(self) -> None:
        contract = load_candidate_contract(CONTRACT_PATH)
        helper = contract["package"]["helper"]
        helper["info_plist_policy"] = "REQUIRED"
        helper["info_plist"] = {}
        with self.assertRaisesRegex(CandidatePlanError, "raw Mach-O"):
            validate_candidate_contract(contract, ROOT)

    def test_source_hash_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="house-candidate-hash-") as directory:
            contract, source_root, _ = self._resolved_fixture(Path(directory))
            (source_root / contract["sources"][0]["relative_path"]).write_bytes(
                b"drift"
            )
            with self.assertRaisesRegex(CandidatePlanError, "SHA-256 mismatch"):
                validate_candidate_contract(contract, source_root)

    def test_entitlement_content_drift_is_rejected_even_when_rehashed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="house-candidate-entitlement-") as directory:
            contract, source_root, _ = self._resolved_fixture(Path(directory))
            parent = contract["package"]["parent"]
            path = source_root / parent["entitlements"]["relative_path"]
            path.write_bytes(
                plistlib.dumps(
                    {
                        "com.apple.security.app-sandbox": True,
                        "com.apple.security.network.client": True,
                    }
                )
            )
            parent["entitlements"]["sha256"] = _sha256(path)
            with self.assertRaisesRegex(CandidatePlanError, "content mismatch"):
                validate_candidate_contract(contract, source_root)

    def test_bound_source_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="house-candidate-symlink-") as directory:
            contract, source_root, _ = self._resolved_fixture(Path(directory))
            first = source_root / contract["sources"][0]["relative_path"]
            target = source_root / contract["sources"][1]["relative_path"]
            first.unlink()
            first.symlink_to(target)
            contract["sources"][0]["sha256"] = _sha256(target)
            with self.assertRaisesRegex(CandidatePlanError, "contains a symlink"):
                validate_candidate_contract(contract, source_root)

    def test_unexpected_bundle_member_policy_cannot_be_relaxed(self) -> None:
        contract = load_candidate_contract(CONTRACT_PATH)
        contract["bundle_inventory"]["unexpected_member_policy"] = "ALLOW"
        with self.assertRaisesRegex(CandidatePlanError, "must be rejected"):
            validate_candidate_contract(contract, ROOT)

    def test_bundle_member_kind_and_mode_are_exact(self) -> None:
        contract = load_candidate_contract(CONTRACT_PATH)
        contract["bundle_inventory"]["required_members"][1]["kind"] = "data"
        with self.assertRaisesRegex(CandidatePlanError, "specification mismatch"):
            validate_candidate_contract(contract, ROOT)

        contract = load_candidate_contract(CONTRACT_PATH)
        contract["bundle_inventory"]["required_members"][2]["mode"] = "0644"
        with self.assertRaisesRegex(CandidatePlanError, "specification mismatch"):
            validate_candidate_contract(contract, ROOT)

    def test_private_workspace_policy_cannot_be_relaxed(self) -> None:
        contract = load_candidate_contract(CONTRACT_PATH)
        contract["plan_policy"]["workspace_policy"]["mode"] = "0755"
        with self.assertRaisesRegex(CandidatePlanError, "workspace policy mismatch"):
            validate_candidate_contract(contract, ROOT)

    def test_package_version_must_match_parent_info_plist(self) -> None:
        contract = load_candidate_contract(CONTRACT_PATH)
        contract["package"]["version"] = "0.2.0"
        with self.assertRaisesRegex(CandidatePlanError, "package version"):
            validate_candidate_contract(contract, ROOT)

    def test_output_root_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="house-candidate-output-") as directory:
            root = Path(directory)
            contract, source_root, output_root = self._resolved_fixture(root)
            link = root / "output-link"
            link.symlink_to(output_root)
            with self.assertRaisesRegex(CandidatePlanError, "must not be a symlink"):
                generate_candidate_plan(contract, source_root, link)

    def test_resolved_fixture_emits_exact_bounded_plan_without_writes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="house-candidate-plan-") as directory:
            contract, source_root, output_root = self._resolved_fixture(Path(directory))
            before = list(output_root.iterdir())
            plan = generate_candidate_plan(contract, source_root, output_root)
            after = list(output_root.iterdir())
            self.assertEqual(plan["state"], PLAN_STATE)
            self.assertEqual(
                [operation["id"] for operation in plan["operations"]],
                EXPECTED_OPERATION_ORDER,
            )
            self.assertEqual(plan["execution"], "NOT_ATTEMPTED_AND_NOT_IMPLEMENTED")
            reservation = plan["operations"][0]
            self.assertEqual(reservation["id"], "reserve_private_workspace")
            self.assertEqual(reservation["policy"]["mode"], "0700")
            self.assertEqual(reservation["policy"]["token_bits"], 128)
            self.assertEqual(
                reservation["pinned_parent"]["canonical_path"],
                str(output_root.resolve()),
            )
            self.assertEqual(
                reservation["pinned_parent"]["device"], output_root.stat().st_dev
            )
            self.assertEqual(
                reservation["pinned_parent"]["inode"], output_root.stat().st_ino
            )
            self.assertEqual(
                reservation["execution"], "NOT_ATTEMPTED_AND_NOT_IMPLEMENTED"
            )
            self.assertEqual(before, [])
            self.assertEqual(after, [])
            encoded = json.dumps(
                plan, sort_keys=True, separators=(",", ":")
            ).encode()
            self.assertLessEqual(len(encoded), MAX_PLAN_BYTES)

    def test_nested_sign_order_is_helper_then_parent(self) -> None:
        with tempfile.TemporaryDirectory(prefix="house-candidate-order-") as directory:
            contract, source_root, output_root = self._resolved_fixture(Path(directory))
            plan = generate_candidate_plan(contract, source_root, output_root)
            ids = [operation["id"] for operation in plan["operations"]]
            self.assertLess(ids.index("sign_helper"), ids.index("sign_parent"))
            helper_sign = plan["operations"][ids.index("sign_helper")]["argv"]
            parent_sign = plan["operations"][ids.index("sign_parent")]["argv"]
            self.assertEqual(helper_sign[0], "/usr/bin/codesign")
            self.assertEqual(parent_sign[0], "/usr/bin/codesign")
            self.assertEqual(helper_sign[3], parent_sign[3])

    def test_link_steps_preserve_platform_and_tool_bindings(self) -> None:
        with tempfile.TemporaryDirectory(prefix="house-candidate-link-") as directory:
            contract, source_root, output_root = self._resolved_fixture(Path(directory))
            plan = generate_candidate_plan(contract, source_root, output_root)
            operations = {operation["id"]: operation for operation in plan["operations"]}
            for operation_id in ("link_helper", "link_parent"):
                operation = operations[operation_id]
                self.assertEqual(operation["tool_binding"], contract["tools"]["clang"])
                self.assertEqual(operation["platform_binding"], contract["platform"])
                self.assertEqual(
                    operation["argv"][:6],
                    [
                        "/Applications/Xcode.app/usr/bin/clang",
                        "-isysroot",
                        "/Applications/Xcode.app/SDKs/MacOSX.sdk",
                        "-mmacosx-version-min=15.0",
                        "-arch",
                        "arm64",
                    ],
                )

    def test_sign_and_verify_steps_preserve_identity_and_input_bindings(self) -> None:
        with tempfile.TemporaryDirectory(prefix="house-candidate-sign-data-") as directory:
            contract, source_root, output_root = self._resolved_fixture(Path(directory))
            plan = generate_candidate_plan(contract, source_root, output_root)
            operations = {operation["id"]: operation for operation in plan["operations"]}
            for name in ("helper", "parent"):
                artifact = contract["package"][name]
                sign = operations[f"sign_{name}"]
                verify = operations[f"verify_{name}"]
                self.assertEqual(sign["tool_binding"], contract["tools"]["codesign"])
                self.assertEqual(sign["identity_binding"], artifact["identity"])
                self.assertEqual(sign["entitlement_binding"], artifact["entitlements"])
                self.assertEqual(
                    sign["hardened_runtime_binding"], artifact["hardened_runtime"]
                )
                self.assertEqual(verify["expected_identity"], artifact["identity"])
                self.assertEqual(
                    verify["expected_entitlements"], artifact["entitlements"]
                )

    def test_resolved_parent_and_helper_team_ids_must_match(self) -> None:
        with tempfile.TemporaryDirectory(prefix="house-candidate-team-") as directory:
            contract, source_root, output_root = self._resolved_fixture(Path(directory))
            contract["package"]["helper"]["identity"]["team_identifier"] = (
                "OTHER12345"
            )
            contract["package"]["helper"]["identity"]["designated_requirement"] = (
                'identifier "com.example.dreamhouse.canary.helper" '
                'and anchor apple generic and certificate leaf[subject.OU] = "OTHER12345"'
            )
            with self.assertRaisesRegex(CandidatePlanError, "Team IDs must match"):
                generate_candidate_plan(contract, source_root, output_root)

    def test_resolved_parent_and_helper_signing_identities_must_match(self) -> None:
        with tempfile.TemporaryDirectory(prefix="house-candidate-identity-") as directory:
            contract, source_root, output_root = self._resolved_fixture(Path(directory))
            contract["package"]["helper"]["identity"]["signing_identity"] = (
                "Apple Development: Other Fixture"
            )
            with self.assertRaisesRegex(
                CandidatePlanError, "signing identities must match"
            ):
                generate_candidate_plan(contract, source_root, output_root)

    def test_designated_requirement_must_bind_bundle_and_team(self) -> None:
        with tempfile.TemporaryDirectory(prefix="house-candidate-requirement-") as directory:
            contract, source_root, _ = self._resolved_fixture(Path(directory))
            contract["package"]["helper"]["identity"]["designated_requirement"] = (
                'identifier "com.example.dreamhouse.canary.helper" '
                "and anchor apple generic"
            )
            with self.assertRaisesRegex(CandidatePlanError, "identity-bound"):
                validate_candidate_contract(contract, source_root)

    def test_designated_requirement_must_use_canonical_grammar(self) -> None:
        with tempfile.TemporaryDirectory(prefix="house-candidate-requirement-") as directory:
            contract, source_root, _ = self._resolved_fixture(Path(directory))
            contract["package"]["helper"]["identity"]["designated_requirement"] = (
                'anchor apple generic and identifier '
                '"com.example.dreamhouse.canary.helper" and '
                'certificate leaf[subject.OU] = "TEAM123456"'
            )
            with self.assertRaisesRegex(CandidatePlanError, "canonical"):
                validate_candidate_contract(contract, source_root)

    def test_resolved_deployment_target_must_match_parent_info_plist(self) -> None:
        with tempfile.TemporaryDirectory(prefix="house-candidate-target-") as directory:
            contract, source_root, _ = self._resolved_fixture(Path(directory))
            contract["platform"]["deployment_target"] = "14.0"
            with self.assertRaisesRegex(CandidatePlanError, "minimum system disagree"):
                validate_candidate_contract(contract, source_root)

    def test_planner_source_has_no_process_or_dynamic_execution_surface(self) -> None:
        source = (ROOT / "candidate_plan.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = set()
        named_calls = set()
        attribute_calls = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    named_calls.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    attribute_calls.add(node.func.attr)
        self.assertTrue(
            imported.isdisjoint({"subprocess", "ctypes", "multiprocessing"})
        )
        self.assertTrue(
            named_calls.isdisjoint(
                {
                    "exec",
                    "eval",
                    "compile",
                    "system",
                    "spawn",
                    "fork",
                    "execve",
                    "posix_spawn",
                }
            )
        )
        self.assertTrue(
            attribute_calls.isdisjoint(
                {
                    "run",
                    "Popen",
                    "system",
                    "spawn",
                    "fork",
                    "execve",
                    "posix_spawn",
                }
            )
        )


if __name__ == "__main__":
    unittest.main()

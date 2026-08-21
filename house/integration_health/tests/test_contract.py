from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from house.integration_health import HealthContractError, evaluate_integration_health


def contract(*, sha256: str | None = None) -> dict[str, object]:
    return {
        "schema": "codex-house-integration-health-contract/1",
        "integration_id": "iterm-companion-future-binding",
        "generation": 1,
        "artifacts": [
            {
                "artifact_id": "hook-config",
                "path": "config/hooks.json",
                "require_executable": False,
                "sha256": sha256,
                "json_expectations": {
                    "/hooks/task_started/command": "bin/task-start",
                    "/hooks/task_completed/enabled": True,
                },
            },
            {
                "artifact_id": "task-start",
                "path": "bin/task-start",
                "require_executable": True,
                "sha256": None,
                "json_expectations": {},
            },
        ],
    }


class IntegrationHealthTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name) / "root"
        self.root.mkdir()
        (self.root / "config").mkdir()
        (self.root / "bin").mkdir()
        self.config_path = self.root / "config" / "hooks.json"
        self.config_path.write_text(
            json.dumps(
                {
                    "hooks": {
                        "task_started": {"command": "bin/task-start"},
                        "task_completed": {"enabled": True},
                    }
                }
            ),
            encoding="utf-8",
        )
        self.executable = self.root / "bin" / "task-start"
        self.executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        self.executable.chmod(0o700)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_healthy_contract_is_read_only_and_requires_explicit_repair_authority(self) -> None:
        before = self.config_path.read_bytes()
        result = evaluate_integration_health(contract(), self.root)
        self.assertEqual(result["state"], "HEALTHY")
        self.assertEqual(result["issues"], [])
        self.assertEqual(result["repair_authority"], "EXPLICIT_FUTURE_OPERATION_REQUIRED")
        self.assertEqual(self.config_path.read_bytes(), before)

    def test_partial_strip_and_stale_value_require_repair(self) -> None:
        self.config_path.write_text(
            json.dumps({"hooks": {"task_started": {"command": "old/start"}}}),
            encoding="utf-8",
        )
        result = evaluate_integration_health(contract(), self.root)
        self.assertEqual(result["state"], "REPAIR_REQUIRED")
        self.assertEqual(
            [issue["code"] for issue in result["issues"]],
            ["JSON_EXPECTATION_MISMATCH", "JSON_EXPECTATION_MISSING"],
        )

    def test_digest_executable_and_json_syntax_defects_are_reported(self) -> None:
        digest = hashlib.sha256(self.config_path.read_bytes()).hexdigest()
        self.executable.chmod(0o600)
        self.config_path.write_text("not JSON", encoding="utf-8")
        result = evaluate_integration_health(contract(sha256=digest), self.root)
        self.assertEqual(result["state"], "REPAIR_REQUIRED")
        self.assertEqual(
            [issue["code"] for issue in result["issues"]],
            ["SHA256_MISMATCH", "JSON_INVALID", "EXECUTABLE_REQUIRED"],
        )

    def test_missing_and_dangling_symlink_are_distinguished(self) -> None:
        self.executable.unlink()
        self.executable.symlink_to("missing-target")
        result = evaluate_integration_health(contract(), self.root)
        self.assertEqual(result["state"], "REPAIR_REQUIRED")
        self.assertEqual(result["issues"], [{"artifact_id": "task-start", "code": "DANGLING_SYMLINK", "path": str(self.executable)}])

    def test_external_symlink_is_never_followed_as_healthy(self) -> None:
        external = self.root.parent / "external-task-start"
        external.write_text("#!/bin/sh\n", encoding="utf-8")
        external.chmod(0o700)
        self.executable.unlink()
        self.executable.symlink_to(external)
        result = evaluate_integration_health(contract(), self.root)
        self.assertEqual(result["issues"], [{"artifact_id": "task-start", "code": "SYMLINK_ESCAPES_ROOT", "path": str(self.executable)}])

    def test_contract_path_escape_and_schema_drift_fail_before_inspection(self) -> None:
        invalid = contract()
        invalid["artifacts"][0]["path"] = "../outside"
        with self.assertRaisesRegex(HealthContractError, "safe relative"):
            evaluate_integration_health(invalid, self.root)
        invalid = contract()
        invalid["unexpected"] = "no"
        with self.assertRaisesRegex(HealthContractError, "schema drift"):
            evaluate_integration_health(invalid, self.root)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

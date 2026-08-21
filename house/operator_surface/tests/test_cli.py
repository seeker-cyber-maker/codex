from __future__ import annotations

import contextlib
import io
import json
import unittest

from house.operator_surface.cli import main


class OperatorCliTests(unittest.TestCase):
    def run_cli(self, argv: list[str]) -> tuple[int, str]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exit_code = main(argv)
        return exit_code, output.getvalue()

    def test_list_is_human_readable_and_no_dispatch(self) -> None:
        exit_code, output = self.run_cli(["list"])
        self.assertEqual(exit_code, 0)
        self.assertIn("codex.house.task.submit", output)
        self.assertIn("TASK_SUBMISSION_REQUIRED", output)

    def test_list_json_is_the_registry_manifest(self) -> None:
        exit_code, output = self.run_cli(["list", "--json"])
        manifest = json.loads(output)
        self.assertEqual(exit_code, 0)
        self.assertEqual(manifest["dispatch"], "NOT_IMPLEMENTED")
        self.assertEqual(manifest["authority"], "NOT_GRANTED")

    def test_search_requires_all_terms_and_returns_one_on_miss(self) -> None:
        hit_code, hit = self.run_cli(["search", "terminal", "preview"])
        miss_code, miss = self.run_cli(["search", "terminal", "missing"])
        self.assertEqual(hit_code, 0)
        self.assertIn("codex.house.companion.preview", hit)
        self.assertEqual(miss_code, 1)
        self.assertEqual(miss, "No commands matched.\n")

    def test_surface_filter_uses_shared_manifest(self) -> None:
        exit_code, output = self.run_cli(["list", "--surface", "iterm", "--json"])
        commands = json.loads(output)["commands"]
        self.assertEqual(exit_code, 0)
        self.assertEqual(
            [command["command_id"] for command in commands],
            ["codex.house.companion.preview"],
        )

    def test_keys_only_lists_assigned_bindings(self) -> None:
        exit_code, output = self.run_cli(["keys", "--json"])
        commands = json.loads(output)
        self.assertEqual(exit_code, 0)
        self.assertTrue(commands)
        self.assertTrue(all(command["hotkey"] for command in commands))
        self.assertNotIn("codex.house.routes.list", {c["command_id"] for c in commands})

    def test_prepare_emits_unauthorized_hash_bound_receipt(self) -> None:
        exit_code, output = self.run_cli(
            [
                "prepare",
                "codex.house.task.submit",
                "--arg",
                "summary=Review the CLI",
                "--arg",
                "recipient=reviewer",
            ]
        )
        receipt = json.loads(output)
        self.assertEqual(exit_code, 0)
        self.assertEqual(receipt["state"], "PREPARED_UNAUTHORIZED")
        self.assertEqual(receipt["dispatch"], "NOT_ATTEMPTED")
        self.assertEqual(receipt["arguments"]["recipient"], "reviewer")
        self.assertEqual(len(receipt["request_sha256"]), 64)

    def test_prepare_requires_explicit_target_pair(self) -> None:
        with self.assertRaises(SystemExit) as raised:
            self.run_cli(
                [
                    "prepare",
                    "codex.house.task.inspect",
                    "--target-kind",
                    "task",
                ]
            )
        self.assertEqual(raised.exception.code, 2)

    def test_prepare_rejects_duplicate_and_malformed_arguments(self) -> None:
        for arguments in (
            ["--arg", "summary=x", "--arg", "summary=y"],
            ["--arg", "summary"],
        ):
            with self.subTest(arguments=arguments):
                with self.assertRaises(SystemExit) as raised:
                    self.run_cli(["prepare", "codex.house.task.submit", *arguments])
                self.assertEqual(raised.exception.code, 2)

    def test_prepare_reuses_registry_target_validation(self) -> None:
        exit_code, output = self.run_cli(
            [
                "prepare",
                "codex.house.task.inspect",
                "--target-kind",
                "task",
                "--target-id",
                "task-123",
            ]
        )
        receipt = json.loads(output)
        self.assertEqual(exit_code, 0)
        self.assertEqual(receipt["target"], {"kind": "task", "id": "task-123"})


if __name__ == "__main__":
    unittest.main()

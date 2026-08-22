from __future__ import annotations

import unittest

from house.worker_exec import CliContractError, validate_cli_contract

HELP = """
  -m, --model <MODEL>
  -s, --sandbox <SANDBOX_MODE>
  -C, --cd <DIR>
      --json
  -o, --output-last-message <FILE>
"""


class CliContractTests(unittest.TestCase):
    def test_pinned_captured_grammar_is_accepted(self) -> None:
        result = validate_cli_contract(
            executable_sha256="a" * 64,
            version_output="codex-cli 0.147.0\n",
            exec_help_output=HELP,
        )
        self.assertEqual(result["state"], "VALIDATED_FROM_CAPTURE_NO_DISPATCH")

    def test_version_and_unadmitted_argument_drift_fail_closed(self) -> None:
        with self.assertRaisesRegex(CliContractError, "version differs"):
            validate_cli_contract(
                executable_sha256="a" * 64,
                version_output="codex-cli 0.148.0",
                exec_help_output=HELP,
            )
        with self.assertRaisesRegex(CliContractError, "unadmitted"):
            validate_cli_contract(
                executable_sha256="a" * 64,
                version_output="codex-cli 0.147.0",
                exec_help_output=HELP + "\n --ask-for-approval",
            )

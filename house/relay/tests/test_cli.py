"""CLI parity tests for the offline worker relay."""

from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from house.relay.cli import main
from house.worker_catalog import ingest_catalog


def catalog_receipt() -> dict[str, object]:
    return ingest_catalog(
        {
            "schema": "codex-house-local-worker-catalog/1",
            "source": "provider-orchestration",
            "source_commit": "a" * 40,
            "source_tree": "b" * 40,
            "workers": [
                {
                    "id": "local.alpha",
                    "approval": "approved_specialist",
                    "status": "qualified",
                    "dispatch": "not_dispatchable",
                    "capabilities": ["classification"],
                }
            ],
        }
    )


class RelayCliTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.catalog_path = self.root / "catalog-receipt.json"
        self.catalog_path.write_text(json.dumps(catalog_receipt()), encoding="utf-8")
        self.envelope_path = self.root / "envelope.json"
        self.envelope_path.write_text(
            json.dumps(
                {
                    "schema": "codex-house-relay-envelope/1",
                    "envelope_id": "relay-cli-001",
                    "thread_id": "thread-cli-001",
                    "sender_id": "worker.alpha",
                    "recipient_id": "worker.beta",
                    "contract_version": "worker-contract/1",
                    "payload": {"kind": "proposal", "artifact_sha256": "a" * 64},
                    "ttl_hops": 1,
                    "turn_budget": 1,
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_cli(self, argv: list[str]) -> tuple[int, dict[str, object]]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exit_code = main(argv)
        return exit_code, json.loads(output.getvalue())

    def test_directory_lookup_and_envelope_status_have_separate_inputs(self) -> None:
        exit_code, address = self.run_cli(
            [
                "directory-address",
                "--catalog-receipt",
                str(self.catalog_path),
                "--recipient-id",
                "local.alpha",
            ]
        )
        self.assertEqual(exit_code, 0)
        self.assertEqual(address["runtime_disposition"], "NOT_ATTEMPTED")

        relay_path = self.root / "relay.sqlite"
        exit_code, queued = self.run_cli(
            [
                "submit",
                "--relay-db",
                str(relay_path),
                "--input",
                str(self.envelope_path),
            ]
        )
        self.assertEqual(exit_code, 0)
        self.assertEqual(queued["state"], "QUEUED")
        self.assertEqual(queued["runtime_disposition"], "NOT_ATTEMPTED")

        exit_code, status = self.run_cli(
            ["status", "--relay-db", str(relay_path), "--envelope-id", "relay-cli-001"]
        )
        self.assertEqual(exit_code, 0)
        self.assertEqual(status["state"], "QUEUED")


if __name__ == "__main__":
    unittest.main()

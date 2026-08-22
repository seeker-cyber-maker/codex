"""Read-only dashboard adapter tests for the offline worker relay."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from house.relay import Relay, RelayDirectory
from house.relay.dashboard import RelayDashboardAdapter
from house.worker_catalog import ingest_catalog


def directory() -> RelayDirectory:
    return RelayDirectory(
        ingest_catalog(
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
    )


class RelayDashboardTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.relay = Relay(Path(self.temporary.name) / "relay.sqlite")
        self.adapter = RelayDashboardAdapter(directory(), self.relay)

    def tearDown(self) -> None:
        self.relay.close()
        self.temporary.cleanup()

    def test_read_only_directory_view_is_authority_neutral(self) -> None:
        response = self.adapter.handle("GET", "/v1/relay/directory/local.alpha")
        self.assertEqual(response["status"], 200)
        self.assertEqual(response["body"]["id"], "local.alpha")
        self.assertEqual(
            response["body"]["authority_disposition"], "NO_AUTHORITY_GRANTED"
        )

    def test_mutating_requests_are_explicitly_unavailable(self) -> None:
        response = self.adapter.handle("POST", "/v1/relay/submit")
        self.assertEqual(response["status"], 418)
        self.assertEqual(response["body"]["error"], "integration_pending")
        self.assertEqual(response["body"]["dispatch"], "NOT_ATTEMPTED")

    def test_unknown_and_malformed_paths_are_not_exposed(self) -> None:
        self.assertEqual(
            self.adapter.handle("GET", "/v1/relay/directory/nope")["status"], 404
        )
        self.assertEqual(
            self.adapter.handle("GET", "/v1/relay/directory/local.alpha?x=1")["status"],
            404,
        )


if __name__ == "__main__":
    unittest.main()

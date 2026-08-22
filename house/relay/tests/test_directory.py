"""Tests for the sealed worker-catalog to relay-directory adapter."""

from __future__ import annotations

import unittest

from house.relay.directory import RelayDirectory, RelayDirectoryError
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
                    "capabilities": ["classification", "offline_inference"],
                },
                {
                    "id": "local.beta",
                    "approval": "approved_specialist",
                    "status": "active",
                    "dispatch": "available",
                    "capabilities": ["vision"],
                },
            ],
        }
    )


class RelayDirectoryTest(unittest.TestCase):
    def test_directory_exposes_static_address_and_capability_metadata_only(
        self,
    ) -> None:
        directory = RelayDirectory(catalog_receipt())
        alpha = directory.address("local.alpha")
        self.assertEqual(alpha["id"], "local.alpha")
        self.assertEqual(alpha["dispatch"], "not_dispatchable")
        self.assertEqual(alpha["capabilities"], ["classification", "offline_inference"])
        self.assertEqual(alpha["runtime_disposition"], "NOT_ATTEMPTED")
        self.assertEqual(
            directory.find_capability("vision"),
            [{"id": "local.beta", "status": "active", "dispatch": "available"}],
        )

    def test_unknown_recipient_and_malformed_receipt_fail_closed(self) -> None:
        directory = RelayDirectory(catalog_receipt())
        with self.assertRaisesRegex(RelayDirectoryError, "unknown recipient"):
            directory.address("local.unknown")
        receipt = catalog_receipt()
        receipt["runtime_disposition"] = "ATTEMPTED"
        with self.assertRaisesRegex(RelayDirectoryError, "runtime disposition"):
            RelayDirectory(receipt)


if __name__ == "__main__":
    unittest.main()

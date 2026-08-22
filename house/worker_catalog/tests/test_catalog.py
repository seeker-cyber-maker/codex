from __future__ import annotations

import copy
import unittest

from house.worker_catalog import CatalogError, ingest_catalog


def catalog() -> dict[str, object]:
    return {
        "schema": "codex-house-local-worker-catalog/1",
        "source": "provider-orchestration",
        "source_commit": "a" * 40,
        "source_tree": "b" * 40,
        "workers": [
            {
                "id": "local.omlx",
                "approval": "approved_specialist",
                "status": "active",
                "dispatch": "available",
                "capabilities": ["text_generation"],
            },
            {
                "id": "local.omlx.qwen3_vl",
                "approval": "approved_specialist",
                "status": "qualified",
                "dispatch": "not_dispatchable",
                "capabilities": ["screenshot_grounding"],
            },
        ],
    }


class WorkerCatalogTests(unittest.TestCase):
    def test_ingest_is_deterministic_and_non_dispatching(self) -> None:
        receipt = ingest_catalog(catalog())
        self.assertEqual(receipt["active_worker_ids"], ["local.omlx"])
        self.assertEqual(receipt["qualified_worker_ids"], ["local.omlx.qwen3_vl"])
        self.assertEqual(receipt["runtime_disposition"], "NOT_ATTEMPTED")
        self.assertNotIn("endpoint", receipt)

    def test_rejects_unapproved_or_inconsistent_worker(self) -> None:
        unapproved = catalog()
        unapproved["workers"][0]["approval"] = "present_model"
        with self.assertRaisesRegex(CatalogError, "approved specialist"):
            ingest_catalog(unapproved)
        inconsistent = catalog()
        inconsistent["workers"][0]["dispatch"] = "not_dispatchable"
        with self.assertRaisesRegex(CatalogError, "inconsistent"):
            ingest_catalog(inconsistent)

    def test_rejects_unknown_fields_and_duplicate_ids(self) -> None:
        extra = catalog()
        extra["endpoint"] = "http://127.0.0.1:8123"
        with self.assertRaisesRegex(CatalogError, "fields are not exact"):
            ingest_catalog(extra)
        duplicate = copy.deepcopy(catalog())
        duplicate["workers"].append(copy.deepcopy(duplicate["workers"][0]))
        with self.assertRaisesRegex(CatalogError, "identifiers must be unique"):
            ingest_catalog(duplicate)

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from house.task_spine import TaskSpine
from house.task_spine.readonly import (
    TaskSpineReadonlyError,
    load_task_cards_readonly,
)


class TaskSpineReadonlyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_existing_journal_is_projected_without_byte_change(self) -> None:
        path = self.root / "tasks.sqlite"
        spine = TaskSpine(path)
        spine.create_work_item("work-readonly", "Read-only source")
        spine.create_task_packet(
            "task-readonly",
            "work-readonly",
            "Render one static task card.",
            case_type="evidence_review",
        )
        spine.close()
        before = path.read_bytes()

        cards, journal_sha256 = load_task_cards_readonly(path)

        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0]["task_id"], "task-readonly")
        self.assertRegex(journal_sha256, r"^[0-9a-f]{64}$")
        self.assertEqual(before, path.read_bytes())

    def test_missing_or_invalid_database_is_rejected_without_creation(self) -> None:
        missing = self.root / "missing.sqlite"
        with self.assertRaisesRegex(TaskSpineReadonlyError, "existing regular file"):
            load_task_cards_readonly(missing)
        self.assertFalse(missing.exists())

        invalid = self.root / "invalid.sqlite"
        invalid.write_text("not a sqlite database", encoding="utf-8")
        with self.assertRaisesRegex(TaskSpineReadonlyError, "journal cannot be read"):
            load_task_cards_readonly(invalid)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

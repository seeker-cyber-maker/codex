from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from house.relay.operator_board_bundle import (
    OperatorBoardBundleError,
    inspect_operator_board_bundle,
    write_operator_board_bundle,
)


def _empty_sources() -> dict[str, object]:
    return {
        "relay_registrations": {
            "state": "NOT_SUPPLIED",
            "path": None,
            "input_sha256": None,
            "count": 0,
        },
        "task_spine": {
            "state": "NOT_SUPPLIED",
            "path": None,
            "journal_sha256": None,
            "count": 0,
        },
    }


class OperatorBoardBundleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_bootstrap_bundle_is_complete_and_replayable(self) -> None:
        target = self.root / "bootstrap-board"

        receipt = write_operator_board_bundle(target, [], [], _empty_sources())

        self.assertEqual(receipt["state"], "COMPLETE_OFFLINE")
        self.assertEqual(receipt["path"], str(target))
        self.assertEqual(receipt["sources"]["task_spine"]["state"], "NOT_SUPPLIED")
        self.assertTrue((target / "operator-snapshot" / "envelope.json").is_file())
        self.assertTrue((target / "snapshot-inventory.html").is_file())
        self.assertTrue((target / "operator-board.html").is_file())
        self.assertTrue((target / "operator-board.html.receipt.json").is_file())
        board = (target / "operator-board.html").read_text(encoding="utf-8")
        self.assertEqual(board.count("Source scope: NOT_SUPPLIED"), 2)
        self.assertEqual(inspect_operator_board_bundle(target), receipt)

    def test_existing_target_and_tampered_inventory_fail_closed(self) -> None:
        target = self.root / "bootstrap-board"
        write_operator_board_bundle(target, [], [], _empty_sources())

        with self.assertRaisesRegex(OperatorBoardBundleError, "already exists"):
            write_operator_board_bundle(target, [], [], _empty_sources())
        inventory = target / "snapshot-inventory.html"
        inventory.write_text(
            inventory.read_text(encoding="utf-8") + "x", encoding="utf-8"
        )
        with self.assertRaisesRegex(
            OperatorBoardBundleError, "inventory does not match replay"
        ):
            inspect_operator_board_bundle(target)

    def test_absent_source_cannot_claim_identity(self) -> None:
        sources = _empty_sources()
        sources["relay_registrations"] = {
            "state": "NOT_SUPPLIED",
            "path": "/not/supplied.json",
            "input_sha256": None,
            "count": 0,
        }

        with self.assertRaisesRegex(OperatorBoardBundleError, "absent source"):
            write_operator_board_bundle(self.root / "invalid", [], [], sources)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

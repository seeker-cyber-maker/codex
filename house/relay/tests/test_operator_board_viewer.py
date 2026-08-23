from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from house.relay.operator_board_export import write_operator_board_export
from house.relay.operator_board_viewer import (
    OperatorBoardViewerError,
    prepare_operator_board_viewer,
)
from house.relay.tests.test_operator_board_export import _documents
from house.terminal_companion import LoopbackViewerError


class OperatorBoardViewerTests(unittest.TestCase):
    def _export(self, root: Path) -> Path:
        snapshot, inventory = _documents()
        target = root / "operator-board.html"
        write_operator_board_export(target, snapshot, inventory)
        return target

    def test_preparation_requires_one_verified_named_export_and_stays_unbound(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            target = self._export(Path(tempdir))

            viewer = prepare_operator_board_viewer(target)

            self.assertFalse(viewer.is_alive())
            with self.assertRaisesRegex(LoopbackViewerError, "not started"):
                _ = viewer.authority

    def test_changed_or_relative_export_fails_before_viewer_preparation(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            target = self._export(Path(tempdir))
            target.write_text("changed", encoding="utf-8")

            with self.assertRaisesRegex(OperatorBoardViewerError, "not valid"):
                prepare_operator_board_viewer(target)
        with self.assertRaisesRegex(OperatorBoardViewerError, "not valid"):
            prepare_operator_board_viewer("relative-board.html")

    def test_non_exact_loopback_host_is_rejected_without_starting(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            target = self._export(Path(tempdir))

            with self.assertRaisesRegex(LoopbackViewerError, "exact loopback"):
                prepare_operator_board_viewer(target, host="localhost")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

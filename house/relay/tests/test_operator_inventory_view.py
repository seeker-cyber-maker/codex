from __future__ import annotations

import unittest

from house.relay.operator_inventory_view import (
    OperatorSnapshotInventoryViewError,
    render_operator_snapshot_inventory_html,
)


def _records() -> list[dict[str, str]]:
    return [
        {
            "input_path": "/Volumes/Archive/<script>alert(1)</script>",
            "path": "/Volumes/Archive/snapshot-001",
            "state": "VALID_OFFLINE",
            "reason": "",
            "descriptor_receipt_sha256": "a" * 64,
            "envelope_sha256": "b" * 64,
        },
        {
            "input_path": "/Volumes/Archive/missing",
            "path": "/Volumes/Archive/missing",
            "state": "REJECTED_ENVELOPE",
            "reason": "output directory does not exist",
        },
    ]


class OperatorSnapshotInventoryViewTests(unittest.TestCase):
    def test_view_is_static_escaped_and_receipt_bounded(self) -> None:
        document = render_operator_snapshot_inventory_html(_records())

        self.assertIn("Snapshot inventory", document)
        self.assertIn("VALID_OFFLINE", document)
        self.assertIn("REJECTED_ENVELOPE", document)
        self.assertIn("a" * 64, document)
        self.assertIn("b" * 64, document)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", document)
        self.assertNotIn("<script", document)
        self.assertNotIn("<form", document)
        self.assertNotIn("<a ", document)
        self.assertNotIn("fetch(", document)
        self.assertNotIn("WebSocket", document)
        self.assertIn("default-src 'none'", document)
        self.assertIn("connect-src 'none'", document)

    def test_malformed_or_unbounded_inventory_is_rejected(self) -> None:
        with self.assertRaisesRegex(OperatorSnapshotInventoryViewError, "list of 1"):
            render_operator_snapshot_inventory_html([])
        with self.assertRaisesRegex(OperatorSnapshotInventoryViewError, "list of 1"):
            render_operator_snapshot_inventory_html([_records()[0]] * 33)
        malformed = _records()[0]
        malformed["state"] = "LIVE"
        with self.assertRaisesRegex(OperatorSnapshotInventoryViewError, "state"):
            render_operator_snapshot_inventory_html([malformed])
        extra = _records()[1]
        extra["extra"] = "not allowed"
        with self.assertRaisesRegex(OperatorSnapshotInventoryViewError, "fields"):
            render_operator_snapshot_inventory_html([extra])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

from __future__ import annotations

import unittest

from house.relay.operator_registration import build_relay_preview_registration
from house.relay.preview_index import (
    RelayPreviewIndexError,
    render_relay_preview_index_html,
)


def _response(note: str) -> dict[str, object]:
    return {
        "schema": "codex-house-relay-dashboard-response/1",
        "status": 200,
        "body": {"worker": "alpha", "note": note},
        "transport": "NOT_BOUND",
    }


class RelayPreviewIndexTests(unittest.TestCase):
    def test_index_is_deterministic_and_content_free(self) -> None:
        first = build_relay_preview_registration(_response("first-secret"))
        second = build_relay_preview_registration(_response("second-secret"))

        forward = render_relay_preview_index_html([first, second])
        reverse = render_relay_preview_index_html([second, first])

        self.assertEqual(forward, reverse)
        self.assertIn("2 relay previews", forward)
        self.assertIn(first["registration_sha256"], forward)
        self.assertIn(second["registration_sha256"], forward)
        self.assertNotIn("first-secret", forward)
        self.assertNotIn("second-secret", forward)
        self.assertNotIn("<script", forward)
        self.assertNotIn("<form", forward)
        self.assertNotIn("<a ", forward)
        self.assertNotIn("fetch(", forward)
        self.assertNotIn("WebSocket", forward)
        self.assertIn("default-src 'none'", forward)

    def test_duplicate_registration_is_rejected(self) -> None:
        registration = build_relay_preview_registration(_response("same"))
        with self.assertRaisesRegex(RelayPreviewIndexError, "duplicate"):
            render_relay_preview_index_html([registration, registration])

    def test_invalid_registration_is_rejected_before_index_rendering(self) -> None:
        registration = build_relay_preview_registration(_response("safe"))
        invalid = {**registration, "authority": "GRANTED"}
        with self.assertRaisesRegex(RelayPreviewIndexError, "invalid registration"):
            render_relay_preview_index_html([invalid])

    def test_declared_source_scope_is_visible_and_exact(self) -> None:
        document = render_relay_preview_index_html([], source_state="NOT_SUPPLIED")

        self.assertIn("Source scope: NOT_SUPPLIED", document)
        with self.assertRaisesRegex(RelayPreviewIndexError, "source scope"):
            render_relay_preview_index_html([], source_state="LIVE")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

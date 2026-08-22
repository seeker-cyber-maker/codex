from __future__ import annotations

import unittest

from house.relay.operator_preview import (
    RelayPreviewCardError,
    render_relay_preview_card_html,
)
from house.relay.operator_registration import build_relay_preview_registration


def _response(note: str = "<script>steer()</script>") -> dict[str, object]:
    return {
        "schema": "codex-house-relay-dashboard-response/1",
        "status": 200,
        "body": {"worker": "alpha", "note": note},
        "transport": "NOT_BOUND",
    }


class RelayPreviewCardTests(unittest.TestCase):
    def test_card_is_static_and_reveals_no_source_document_content(self) -> None:
        registration = build_relay_preview_registration(_response())
        document = render_relay_preview_card_html(registration)

        self.assertIn("Relay preview ready", document)
        self.assertIn(registration["document_sha256"], document)
        self.assertIn(registration["registration_sha256"], document)
        self.assertIn("EXPLICIT_START_AND_CAPABILITY_HANDOFF_REQUIRED", document)
        self.assertNotIn("steer", document)
        self.assertNotIn("<script", document)
        self.assertNotIn("<form", document)
        self.assertNotIn("<a ", document)
        self.assertNotIn("fetch(", document)
        self.assertNotIn("WebSocket", document)
        self.assertIn("default-src 'none'", document)
        self.assertIn("connect-src 'none'", document)
        self.assertIn("form-action 'none'", document)

    def test_tampered_descriptor_is_rejected_before_rendering(self) -> None:
        registration = build_relay_preview_registration(_response("safe"))
        tampered = {**registration, "viewer_start": "STARTED"}

        with self.assertRaisesRegex(RelayPreviewCardError, "registration viewer_start"):
            render_relay_preview_card_html(tampered)

    def test_malformed_command_cannot_be_presented_as_display_only(self) -> None:
        registration = build_relay_preview_registration(_response("safe"))
        command = dict(registration["command"])
        command["authority"] = "UNRESTRICTED"
        malformed = {**registration, "command": command}

        with self.assertRaisesRegex(RelayPreviewCardError, "command"):
            render_relay_preview_card_html(malformed)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

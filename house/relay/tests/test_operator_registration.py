from __future__ import annotations

import unittest

from house.relay.dashboard_view import RelayDashboardViewError
from house.relay.operator_registration import build_relay_preview_registration


def _response(note: str = "safe") -> dict[str, object]:
    return {
        "schema": "codex-house-relay-dashboard-response/1",
        "status": 200,
        "body": {"worker": "alpha", "note": note},
        "transport": "NOT_BOUND",
    }


class RelayPreviewRegistrationTests(unittest.TestCase):
    def test_registration_is_deterministic_and_capability_free(self) -> None:
        first = build_relay_preview_registration(_response())
        second = build_relay_preview_registration(_response())

        self.assertEqual(first, second)
        self.assertEqual(first["schema"], "codex-house-relay-preview-registration/1")
        self.assertEqual(first["state"], "PREPARED_UNAUTHORIZED")
        self.assertEqual(first["document_sha256"], first["target"]["id"])
        self.assertEqual(first["target"]["kind"], "relay_dashboard_document")
        self.assertEqual(first["command"]["command_id"], "codex.house.relay.preview")
        self.assertEqual(first["command"]["authority"], "DISPLAY_ONLY")
        self.assertEqual(first["command"]["dispatch"], "NOT_ATTEMPTED")
        self.assertEqual(first["capability"], "NOT_ISSUED")
        self.assertEqual(first["viewer_start"], "NOT_ATTEMPTED")
        self.assertEqual(first["browser_launch"], "NOT_ATTEMPTED")
        self.assertEqual(first["iterm_api_registration"], "NOT_ATTEMPTED")
        self.assertEqual(first["worker_dispatch"], "NOT_ATTEMPTED")
        self.assertEqual(first["authority"], "NOT_GRANTED")
        self.assertEqual(first["reverse_channel"], "PROHIBITED")
        self.assertNotIn("safe", str(first))
        self.assertEqual(len(first["registration_sha256"]), 64)

    def test_each_frozen_document_gets_a_distinct_explicit_target(self) -> None:
        first = build_relay_preview_registration(_response("first"))
        second = build_relay_preview_registration(_response("second"))

        self.assertNotEqual(first["document_sha256"], second["document_sha256"])
        self.assertNotEqual(first["registration_sha256"], second["registration_sha256"])

    def test_invalid_adapter_response_cannot_create_an_operator_request(self) -> None:
        invalid = {**_response(), "transport": "BOUND"}
        with self.assertRaisesRegex(RelayDashboardViewError, "must be NOT_BOUND"):
            build_relay_preview_registration(invalid)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

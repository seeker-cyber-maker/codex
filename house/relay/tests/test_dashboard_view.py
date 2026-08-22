"""Tests for frozen, static relay-dashboard document rendering."""

from __future__ import annotations

import unittest

from house.relay.dashboard_view import RelayDashboardViewError, render_dashboard_html


def response(status: int = 200) -> dict[str, object]:
    body: dict[str, object]
    if status == 200:
        body = {
            "id": "local.alpha",
            "status": "qualified",
            "dispatch": "not_dispatchable",
            "authority_disposition": "NO_AUTHORITY_GRANTED",
            "runtime_disposition": "NOT_ATTEMPTED",
            "note": "<script>alert(1)</script>",
        }
    else:
        body = {
            "error": "integration_pending",
            "dispatch": "NOT_ATTEMPTED",
            "authority": "NOT_GRANTED",
        }
    return {
        "schema": "codex-house-relay-dashboard-response/1",
        "status": status,
        "body": body,
        "transport": "NOT_BOUND",
    }


class RelayDashboardViewTest(unittest.TestCase):
    def test_renderer_is_static_escaped_and_noninteractive(self) -> None:
        document = render_dashboard_html(response())
        self.assertIn("Relay dashboard · 200", document)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", document)
        self.assertIn("default-src 'none'", document)
        self.assertIn("connect-src 'none'", document)
        self.assertIn("form-action 'none'", document)
        self.assertNotIn("<script", document)
        self.assertNotIn("<form", document)
        self.assertNotIn("<a ", document)
        self.assertNotIn("fetch(", document)
        self.assertNotIn("WebSocket", document)

    def test_pending_integration_is_visible_but_not_promoted(self) -> None:
        document = render_dashboard_html(response(418))
        self.assertIn("Relay dashboard · 418", document)
        self.assertIn("integration_pending", document)
        self.assertIn("NOT_ATTEMPTED", document)
        self.assertIn("NOT_GRANTED", document)

    def test_renderer_requires_exact_bounded_response(self) -> None:
        invalid = response()
        invalid["extra"] = True
        with self.assertRaisesRegex(RelayDashboardViewError, "fields are not exact"):
            render_dashboard_html(invalid)
        with self.assertRaisesRegex(RelayDashboardViewError, "response body"):
            render_dashboard_html({**response(), "body": "not-an-object"})


if __name__ == "__main__":
    unittest.main()

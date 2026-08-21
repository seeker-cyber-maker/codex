from __future__ import annotations

import unittest

from house.terminal_companion import (
    CompanionProjectionError,
    build_display_batch,
    build_webview_registration_descriptor,
    project_notifications,
    render_display_chain_html,
)


def card() -> dict[str, object]:
    return project_notifications(
        [
            {
                "method": "item/completed",
                "params": {
                    "threadId": "thread-1",
                    "turnId": "turn-1",
                    "item": {
                        "type": "commandExecution",
                        "id": "exec-1",
                        "command": "printf '<script>alert(1)</script>'",
                        "cwd": "/work?a=1&b=2",
                        "status": "completed",
                        "aggregatedOutput": "<img src=x onerror=alert(2)>\n",
                        "exitCode": 0,
                        "durationMs": 33,
                    },
                },
            }
        ]
    )[0]


class WebViewTests(unittest.TestCase):
    def test_renderer_is_static_escaped_and_network_inert(self) -> None:
        batch = build_display_batch([card()], sequence=0)
        document = render_display_chain_html([batch])

        self.assertIn("default-src 'none'", document)
        self.assertIn("connect-src 'none'", document)
        self.assertIn("form-action 'none'", document)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", document)
        self.assertIn("&lt;img src=x onerror=alert(2)&gt;", document)
        self.assertNotIn("<script", document)
        self.assertNotIn("<img", document)
        self.assertNotIn("<a ", document)
        self.assertNotIn("fetch(", document)
        self.assertNotIn("WebSocket", document)

    def test_renderer_requires_a_complete_valid_chain(self) -> None:
        first = build_display_batch([card()], sequence=0)
        second = build_display_batch(
            [card()], sequence=1, previous_batch_id=first["batch_id"]
        )
        document = render_display_chain_html([first, second])
        self.assertIn("2 cards · sequence 1", document)

        with self.assertRaisesRegex(CompanionProjectionError, "predecessor"):
            render_display_chain_html([first, dict(second, previous_batch_id="0" * 64)])
        with self.assertRaisesRegex(CompanionProjectionError, "at least one"):
            render_display_chain_html([])

    def test_renderer_bounds_total_chain_content(self) -> None:
        oversized = card()
        oversized["output"] = "x" * 1_000_001
        first = build_display_batch([oversized], sequence=0)
        second = build_display_batch(
            [oversized], sequence=1, previous_batch_id=first["batch_id"]
        )
        with self.assertRaisesRegex(CompanionProjectionError, "text exceeds"):
            render_display_chain_html([first, second])

    def test_registration_descriptor_is_unbound_and_observe_only(self) -> None:
        descriptor = build_webview_registration_descriptor()
        self.assertEqual(descriptor["surface"], "ITERM_TOOLBELT_WEBVIEW")
        self.assertIsNone(descriptor["url"])
        self.assertEqual(descriptor["url_state"], "UNBOUND")
        self.assertEqual(descriptor["url_validation"], "IMPLEMENTED_OFFLINE_UNBOUND")
        self.assertEqual(descriptor["binding_gate"], "LIVE_BINDING_REVIEW_REQUIRED")
        self.assertEqual(descriptor["authority"], "OBSERVE_ONLY")
        self.assertEqual(descriptor["reverse_channel"], "PROHIBITED")
        self.assertEqual(descriptor["terminal_input"], "PROHIBITED")
        self.assertEqual(descriptor["transport"], "NOT_ATTEMPTED")
        self.assertEqual(descriptor["iterm_api_registration"], "NOT_ATTEMPTED")
        self.assertEqual(descriptor["buddy_relay"], "OUT_OF_SCOPE")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

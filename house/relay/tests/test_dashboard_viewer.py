from __future__ import annotations

import socket
import unittest
from urllib.parse import urlsplit

from house.relay.dashboard_view import RelayDashboardViewError
from house.relay.dashboard_viewer import prepare_relay_dashboard_viewer
from house.terminal_companion import LoopbackViewerError, OneShotLoopbackViewer


def _response(status: int = 200) -> dict[str, object]:
    body: dict[str, object]
    if status == 418:
        body = {
            "error": "integration_pending",
            "dispatch": "NOT_ATTEMPTED",
            "authority": "NOT_GRANTED",
        }
    else:
        body = {"worker": "alpha", "note": "<script>alert(1)</script>"}
    return {
        "schema": "codex-house-relay-dashboard-response/1",
        "status": status,
        "body": body,
        "transport": "NOT_BOUND",
    }


def _fetch_path(viewer: OneShotLoopbackViewer, url: str, path: str) -> bytes:
    parsed = urlsplit(url)
    host = parsed.hostname or ""
    port = parsed.port or 0
    authority = viewer.authority
    request = f"GET {path} HTTP/1.1\r\nHost: {authority}\r\n\r\n".encode("ascii")
    with socket.create_connection((host, port), timeout=2) as connection:
        connection.sendall(request)
        connection.shutdown(socket.SHUT_WR)
        chunks: list[bytes] = []
        while True:
            chunk = connection.recv(65536)
            if not chunk:
                return b"".join(chunks)
            chunks.append(chunk)


def _fetch(viewer: OneShotLoopbackViewer, url: str) -> bytes:
    return _fetch_path(viewer, url, urlsplit(url).path)


class RelayDashboardViewerTests(unittest.TestCase):
    def test_preparation_is_unbound_until_explicit_start(self) -> None:
        viewer = prepare_relay_dashboard_viewer(_response())

        self.assertFalse(viewer.is_alive())
        with self.assertRaisesRegex(LoopbackViewerError, "not started"):
            _ = viewer.authority

    def test_frozen_response_is_served_once_with_bearer_free_receipt(self) -> None:
        viewer = prepare_relay_dashboard_viewer(_response())
        grant = viewer.start()
        raw = _fetch(viewer, grant.url)
        receipt = viewer.wait(2)

        self.assertTrue(raw.startswith(b"HTTP/1.1 200 OK\r\n"))
        self.assertIn(b"Relay dashboard", raw)
        self.assertIn(b"&lt;script&gt;alert(1)&lt;/script&gt;", raw)
        self.assertNotIn(b"<script>alert(1)</script>", raw)
        self.assertEqual(receipt["state"], "SERVED")
        self.assertEqual(receipt["transport"], "LOOPBACK_HTTP_ONE_SHOT")
        self.assertEqual(receipt["iterm_api_registration"], "NOT_ATTEMPTED")
        self.assertEqual(receipt["terminal_input"], "PROHIBITED")
        self.assertEqual(receipt["reverse_channel"], "PROHIBITED")
        bearer = urlsplit(grant.url).path.rsplit("/", 1)[-1]
        self.assertNotIn(grant.url, str(receipt))
        self.assertNotIn(bearer, str(receipt))

    def test_response_is_frozen_during_preparation(self) -> None:
        response = _response()
        viewer = prepare_relay_dashboard_viewer(response)
        body = response["body"]
        assert isinstance(body, dict)
        body["worker"] = "mutated-after-preparation"

        grant = viewer.start()
        raw = _fetch(viewer, grant.url)
        viewer.wait(2)

        self.assertIn(b"&quot;worker&quot;: &quot;alpha&quot;", raw)
        self.assertNotIn(b"mutated-after-preparation", raw)

    def test_unknown_capability_does_not_consume_exact_capability(self) -> None:
        viewer = prepare_relay_dashboard_viewer(_response())
        grant = viewer.start()
        rejected = _fetch_path(viewer, grant.url, "/v1/display/" + "A" * 43)
        accepted = _fetch(viewer, grant.url)
        receipt = viewer.wait(2)

        self.assertTrue(rejected.startswith(b"HTTP/1.1 404 Not Found"))
        self.assertTrue(accepted.startswith(b"HTTP/1.1 200 OK"))
        self.assertEqual(receipt["rejected_requests"], 1)
        self.assertFalse(viewer.is_alive())

    def test_expiry_closes_unconsumed_viewer(self) -> None:
        viewer = prepare_relay_dashboard_viewer(_response(), ttl_seconds=1)
        viewer.start()

        receipt = viewer.wait(2)

        self.assertEqual(receipt["state"], "EXPIRED")
        self.assertEqual(receipt["response_bytes"], 0)
        self.assertFalse(viewer.is_alive())

    def test_consumed_capability_cannot_serve_a_second_request(self) -> None:
        viewer = prepare_relay_dashboard_viewer(_response())
        grant = viewer.start()
        parsed = urlsplit(grant.url)
        accepted = _fetch(viewer, grant.url)
        viewer.wait(2)

        self.assertTrue(accepted.startswith(b"HTTP/1.1 200 OK"))
        with self.assertRaises(OSError):
            socket.create_connection(
                (parsed.hostname or "", parsed.port or 0), timeout=0.2
            )

    def test_pending_integration_remains_visible_and_non_authorizing(self) -> None:
        viewer = prepare_relay_dashboard_viewer(_response(418))
        grant = viewer.start()
        raw = _fetch(viewer, grant.url)
        receipt = viewer.wait(2)

        self.assertIn(b"Relay dashboard \xc2\xb7 418", raw)
        self.assertIn(b"integration_pending", raw)
        self.assertIn(b"NOT_ATTEMPTED", raw)
        self.assertIn(b"NOT_GRANTED", raw)
        self.assertEqual(receipt["state"], "SERVED")

    def test_invalid_response_fails_before_a_viewer_can_be_prepared(self) -> None:
        invalid = {**_response(), "transport": "BOUND"}
        with self.assertRaisesRegex(RelayDashboardViewError, "must be NOT_BOUND"):
            prepare_relay_dashboard_viewer(invalid)

    def test_non_loopback_host_is_rejected(self) -> None:
        with self.assertRaisesRegex(LoopbackViewerError, "exact loopback"):
            prepare_relay_dashboard_viewer(_response(), host="localhost")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

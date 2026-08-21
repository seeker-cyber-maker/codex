from __future__ import annotations

import socket
import time
import unittest
from urllib.parse import urlsplit

from house.terminal_companion import (
    LoopbackViewerError,
    OneShotLoopbackViewer,
)


def _exchange(host: str, port: int, request: bytes) -> bytes:
    family = socket.AF_INET6 if host == "::1" else socket.AF_INET
    with socket.socket(family, socket.SOCK_STREAM) as connection:
        connection.settimeout(2)
        connection.connect((host, port))
        connection.sendall(request)
        connection.shutdown(socket.SHUT_WR)
        chunks: list[bytes] = []
        while True:
            chunk = connection.recv(65536)
            if not chunk:
                return b"".join(chunks)
            chunks.append(chunk)


def _request(authority: str, path: str, *headers: bytes) -> bytes:
    return b"\r\n".join(
        (
            f"GET {path} HTTP/1.1".encode("ascii"),
            f"Host: {authority}".encode("ascii"),
            *headers,
            b"",
            b"",
        )
    )


class LoopbackViewerTests(unittest.TestCase):
    def test_ipv4_serves_once_with_security_headers_and_safe_receipt(self) -> None:
        viewer = OneShotLoopbackViewer("<!doctype html><title>safe</title>")
        grant = viewer.start()
        url = grant.url
        parsed = urlsplit(url)
        response = _exchange(
            parsed.hostname or "",
            parsed.port or 0,
            _request(viewer.authority, parsed.path),
        )
        receipt = viewer.wait(2)

        self.assertTrue(response.startswith(b"HTTP/1.1 200 OK\r\n"))
        self.assertIn(b"Cache-Control: no-store, max-age=0", response)
        self.assertIn(b"Referrer-Policy: no-referrer", response)
        self.assertIn(b"X-Content-Type-Options: nosniff", response)
        self.assertIn(b"Content-Security-Policy: default-src 'none'", response)
        self.assertTrue(response.endswith(b"<!doctype html><title>safe</title>"))
        self.assertEqual(receipt["state"], "SERVED")
        self.assertEqual(receipt["transport"], "LOOPBACK_HTTP_ONE_SHOT")
        self.assertEqual(receipt["iterm_api_registration"], "NOT_ATTEMPTED")
        self.assertEqual(receipt["terminal_input"], "PROHIBITED")
        self.assertNotIn(parsed.path.rsplit("/", 1)[-1], str(receipt))
        self.assertNotIn(parsed.path.rsplit("/", 1)[-1], repr(grant))
        self.assertNotIn(parsed.path.rsplit("/", 1)[-1], repr(viewer))
        self.assertFalse(viewer.is_alive())

    def test_invalid_requests_are_uniform_and_do_not_consume_capability(self) -> None:
        viewer = OneShotLoopbackViewer("safe")
        url = viewer.start().url
        parsed = urlsplit(url)
        host = parsed.hostname or ""
        port = parsed.port or 0
        path = parsed.path
        invalid = (
            _request(viewer.authority, "/wrong"),
            _request("127.0.0.1:65535", path),
            _request(viewer.authority, path, b"Host: duplicate"),
            _request(viewer.authority, path, b"Origin: null"),
            _request(viewer.authority, path, b"Transfer-Encoding: chunked"),
            _request(viewer.authority, path, b"Content-Length: 1") + b"x",
            f"POST {path} HTTP/1.1\r\nHost: {viewer.authority}\r\n\r\n".encode(),
            f"GET http://{viewer.authority}{path} HTTP/1.1\r\nHost: {viewer.authority}\r\n\r\n".encode(),
            f"GET {path} HTTP/2\r\nHost: {viewer.authority}\r\n\r\n".encode(),
        )
        responses = [_exchange(host, port, request) for request in invalid]
        self.assertEqual(len(set(responses)), 1)
        self.assertEqual(
            responses[0],
            b"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n"
            b"Cache-Control: no-store\r\nConnection: close\r\n\r\n",
        )

        accepted = _exchange(host, port, _request(viewer.authority, path))
        receipt = viewer.wait(2)
        self.assertTrue(accepted.startswith(b"HTTP/1.1 200 OK"))
        self.assertEqual(receipt["state"], "SERVED")
        self.assertEqual(receipt["rejected_requests"], len(invalid))

    def test_request_line_header_bytes_count_and_folding_are_bounded(self) -> None:
        viewer = OneShotLoopbackViewer("safe")
        url = viewer.start().url
        parsed = urlsplit(url)
        host = parsed.hostname or ""
        port = parsed.port or 0
        path = parsed.path
        oversized_line = b"GET /" + b"x" * 2050 + b" HTTP/1.1\r\nHost: x\r\n\r\n"
        oversized_headers = _request(viewer.authority, path, b"X-Fill: " + b"x" * 8200)
        too_many_headers = _request(
            viewer.authority,
            path,
            *(f"X-{index}: x".encode() for index in range(32)),
        )
        folded = _request(viewer.authority, path, b"X-Test: ok", b" folded")
        for raw in (oversized_line, oversized_headers, too_many_headers, folded):
            with self.subTest(length=len(raw)):
                response = _exchange(host, port, raw)
                self.assertTrue(response.startswith(b"HTTP/1.1 404 Not Found"))

        _exchange(host, port, _request(viewer.authority, path))
        receipt = viewer.wait(2)
        self.assertEqual(receipt["state"], "SERVED")
        self.assertEqual(receipt["rejected_requests"], 4)

    def test_rejection_budget_and_expiry_close_listener(self) -> None:
        viewer = OneShotLoopbackViewer("safe")
        url = viewer.start().url
        parsed = urlsplit(url)
        host = parsed.hostname or ""
        port = parsed.port or 0
        for _ in range(32):
            _exchange(host, port, _request(viewer.authority, "/wrong"))
        budget_receipt = viewer.wait(2)
        self.assertEqual(budget_receipt["state"], "REJECTION_BUDGET_EXHAUSTED")
        self.assertEqual(budget_receipt["rejected_requests"], 32)
        self.assertFalse(viewer.is_alive())

        offset = [0]

        def clock() -> int:
            return time.monotonic_ns() + offset[0]

        expiring = OneShotLoopbackViewer("safe", ttl_seconds=1, clock=clock)
        expiring.start()
        offset[0] = 2_000_000_000
        expiry_receipt = expiring.wait(2)
        self.assertEqual(expiry_receipt["state"], "EXPIRED")
        self.assertFalse(expiring.is_alive())

    def test_close_is_bounded_and_double_start_fails(self) -> None:
        viewer = OneShotLoopbackViewer("safe")
        viewer.start()
        with self.assertRaisesRegex(LoopbackViewerError, "already started"):
            viewer.start()
        receipt = viewer.close()
        self.assertEqual(receipt["state"], "CLOSED")
        self.assertFalse(viewer.is_alive())

    def test_exact_hosts_and_available_ipv6(self) -> None:
        for host in ("localhost", "127.0.0.2", "::ffff:127.0.0.1"):
            with (
                self.subTest(host=host),
                self.assertRaisesRegex(LoopbackViewerError, "exact loopback"),
            ):
                OneShotLoopbackViewer("safe", host=host)

        try:
            viewer = OneShotLoopbackViewer("safe", host="::1")
            url = viewer.start().url
        except LoopbackViewerError as exc:
            self.skipTest(f"IPv6 loopback unavailable: {exc}")
        parsed = urlsplit(url)
        response = _exchange(
            "::1", parsed.port or 0, _request(viewer.authority, parsed.path)
        )
        self.assertTrue(response.startswith(b"HTTP/1.1 200 OK"))
        self.assertEqual(viewer.wait(2)["state"], "SERVED")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

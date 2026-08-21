"""Bounded one-shot loopback transport for an inert companion document."""

from __future__ import annotations

import hashlib
import json
import re
import socket
import socketserver
import threading
import time
from collections.abc import Callable
from typing import Any

from .capability import (
    CapabilityGrant,
    CapabilityValidationError,
    LoopbackCapabilityValidator,
)
from .projector import CompanionProjectionError

MAX_DOCUMENT_BYTES = 10 * 1024 * 1024
MAX_REQUEST_LINE_BYTES = 2048
MAX_HEADER_BYTES = 8192
MAX_HEADER_COUNT = 32
MAX_REJECTED_REQUESTS = 32
MAX_SOCKET_READ_BYTES = MAX_REQUEST_LINE_BYTES + MAX_HEADER_BYTES + 4
SOCKET_POLL_SECONDS = 0.1

_AUDIENCE = "com.codex.house.terminal-companion"
_ALLOWED_HOSTS = {"127.0.0.1", "::1"}
_HEADER_NAME = re.compile(rb"^[!#$%&'*+.^_`|~0-9A-Za-z-]+$")
_REJECTION = (
    b"HTTP/1.1 404 Not Found\r\n"
    b"Content-Length: 0\r\n"
    b"Cache-Control: no-store\r\n"
    b"Connection: close\r\n\r\n"
)


class LoopbackViewerError(RuntimeError):
    """Raised when the bounded viewer cannot start or finish safely."""


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def _authority(host: str, port: int) -> str:
    return f"[{host}]:{port}" if host == "::1" else f"{host}:{port}"


def _terminal_receipt(body: dict[str, Any]) -> dict[str, Any]:
    return {**body, "receipt_id": hashlib.sha256(_canonical_bytes(body)).hexdigest()}


class _IPv4Server(socketserver.TCPServer):
    allow_reuse_address = False
    viewer: OneShotLoopbackViewer

    def handle_error(self, request: object, client_address: object) -> None:
        # Access paths and capability-bearing request targets must never be logged.
        return None


class _IPv6Server(_IPv4Server):
    address_family = socket.AF_INET6


class _ViewerRequestHandler(socketserver.BaseRequestHandler):
    server: _IPv4Server

    def handle(self) -> None:
        viewer = self.server.viewer
        assert isinstance(viewer, OneShotLoopbackViewer)
        accepted = False
        try:
            request = viewer._read_request(self.request)
            method, target, headers = viewer._parse_request(request)
            host_values = headers.get(b"host", [])
            if len(host_values) != 1:
                raise LoopbackViewerError("request rejected")
            try:
                host = host_values[0].decode("ascii")
            except UnicodeDecodeError:
                raise LoopbackViewerError("request rejected") from None
            if host != viewer.authority:
                raise LoopbackViewerError("request rejected")
            if b"origin" in headers or b"transfer-encoding" in headers:
                raise LoopbackViewerError("request rejected")
            lengths = headers.get(b"content-length", [])
            if len(lengths) > 1 or (lengths and lengths[0] != b"0"):
                raise LoopbackViewerError("request rejected")

            now_ns = viewer._clock()
            capability_receipt = viewer._validator.consume(
                url=f"http://{viewer.authority}{target}",
                method=method,
                origin=None,
                audience=_AUDIENCE,
                now_ns=now_ns,
            )
            response = viewer._success_response()
            try:
                self.request.sendall(response)
            except OSError:
                viewer._record_response_failure(capability_receipt, now_ns)
                accepted = True
                return
            viewer._record_success(capability_receipt, now_ns)
            accepted = True
        except (
            CapabilityValidationError,
            LoopbackViewerError,
            OSError,
            UnicodeError,
            ValueError,
        ):
            try:
                self.request.sendall(_REJECTION)
            except OSError:
                pass
        finally:
            if not accepted:
                viewer._record_rejection()


class OneShotLoopbackViewer:
    """Serve one inert HTML document through one exact loopback capability."""

    def __init__(
        self,
        document: str,
        *,
        host: str = "127.0.0.1",
        port: int = 0,
        ttl_seconds: int = 30,
        clock: Callable[[], int] = time.monotonic_ns,
        validator: LoopbackCapabilityValidator | None = None,
    ) -> None:
        if not isinstance(document, str) or not document:
            raise CompanionProjectionError("viewer document must be non-empty text")
        encoded = document.encode("utf-8")
        if len(encoded) > MAX_DOCUMENT_BYTES:
            raise CompanionProjectionError(
                f"viewer document exceeds {MAX_DOCUMENT_BYTES} encoded bytes"
            )
        if host not in _ALLOWED_HOSTS:
            raise LoopbackViewerError("exact loopback IP required")
        if (
            not isinstance(port, int)
            or isinstance(port, bool)
            or port < 0
            or port > 65535
            or 0 < port < 1024
        ):
            raise LoopbackViewerError("port must be zero or a high port")
        if (
            not isinstance(ttl_seconds, int)
            or isinstance(ttl_seconds, bool)
            or not 1 <= ttl_seconds <= 300
        ):
            raise LoopbackViewerError("ttl_seconds must be between 1 and 300")
        if not callable(clock):
            raise LoopbackViewerError("clock must be callable")

        self._document = encoded
        self._host = host
        self._requested_port = port
        self._ttl_seconds = ttl_seconds
        self._clock = clock
        self._validator = validator or LoopbackCapabilityValidator()
        self._server: _IPv4Server | None = None
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._closed = threading.Event()
        self._lock = threading.Lock()
        self._rejected_requests = 0
        self._receipt: dict[str, Any] | None = None
        self._started_at_ns: int | None = None
        self._expires_at_ns: int | None = None
        self._authority: str | None = None

    @property
    def authority(self) -> str:
        if self._authority is None:
            raise LoopbackViewerError("viewer is not started")
        return self._authority

    def start(self) -> CapabilityGrant:
        """Bind, issue one capability, and start one bounded listener thread."""
        with self._lock:
            if self._server is not None or self._thread is not None:
                raise LoopbackViewerError("viewer already started")
            server_type = _IPv6Server if self._host == "::1" else _IPv4Server
            try:
                server = server_type(
                    (self._host, self._requested_port), _ViewerRequestHandler
                )
            except OSError as exc:
                raise LoopbackViewerError("loopback bind failed") from exc
            measured_host = server.server_address[0]
            measured_port = server.server_address[1]
            if measured_host != self._host or not 1024 <= measured_port <= 65535:
                server.server_close()
                raise LoopbackViewerError("listener authority is not canonical")

            now_ns = self._clock()
            try:
                grant = self._validator.issue(
                    host=measured_host,
                    port=measured_port,
                    now_ns=now_ns,
                    ttl_seconds=self._ttl_seconds,
                    audience=_AUDIENCE,
                )
            except Exception:
                server.server_close()
                raise
            self._server = server
            self._authority = _authority(measured_host, measured_port)
            self._started_at_ns = now_ns
            self._expires_at_ns = grant.expires_at_ns
            server.viewer = self
            server.timeout = SOCKET_POLL_SECONDS
            thread = threading.Thread(
                target=self._serve,
                name="codex-house-loopback-viewer",
                daemon=False,
            )
            self._thread = thread
            try:
                thread.start()
            except Exception:
                server.server_close()
                self._server = None
                self._thread = None
                raise
            return grant

    def _serve(self) -> None:
        assert self._server is not None
        assert self._expires_at_ns is not None
        terminal_state = "CLOSED"
        try:
            while not self._stop.is_set():
                now_ns = self._clock()
                if now_ns >= self._expires_at_ns:
                    terminal_state = "EXPIRED"
                    break
                with self._lock:
                    if self._receipt is not None:
                        terminal_state = "SERVED"
                        break
                    if self._rejected_requests >= MAX_REJECTED_REQUESTS:
                        terminal_state = "REJECTION_BUDGET_EXHAUSTED"
                        break
                remaining_seconds = max(
                    0.001, (self._expires_at_ns - now_ns) / 1_000_000_000
                )
                self._server.timeout = min(SOCKET_POLL_SECONDS, remaining_seconds)
                self._server.handle_request()
            if self._stop.is_set():
                terminal_state = "CLOSED"
        finally:
            self._server.server_close()
            with self._lock:
                if self._receipt is None:
                    assert self._started_at_ns is not None
                    assert self._expires_at_ns is not None
                    body = {
                        "schema": "codex-house-loopback-viewer-receipt/1",
                        "state": terminal_state,
                        "authority": self.authority,
                        "started_at_ns": self._started_at_ns,
                        "ended_at_ns": self._clock(),
                        "expires_at_ns": self._expires_at_ns,
                        "rejected_requests": self._rejected_requests,
                        "response_bytes": 0,
                        "transport": "LOOPBACK_HTTP_ONE_SHOT",
                        "iterm_api_registration": "NOT_ATTEMPTED",
                        "terminal_input": "PROHIBITED",
                        "reverse_channel": "PROHIBITED",
                    }
                    self._receipt = _terminal_receipt(body)
            self._closed.set()

    def _read_request(self, connection: socket.socket) -> bytes:
        assert self._expires_at_ns is not None
        data = bytearray()
        while b"\r\n\r\n" not in data:
            now_ns = self._clock()
            if now_ns >= self._expires_at_ns:
                raise LoopbackViewerError("request rejected")
            connection.settimeout(
                min(
                    SOCKET_POLL_SECONDS,
                    max(0.001, (self._expires_at_ns - now_ns) / 1_000_000_000),
                )
            )
            chunk = connection.recv(min(4096, MAX_SOCKET_READ_BYTES + 1 - len(data)))
            if not chunk:
                raise LoopbackViewerError("request rejected")
            data.extend(chunk)
            if len(data) > MAX_SOCKET_READ_BYTES:
                raise LoopbackViewerError("request rejected")
        head, trailing = bytes(data).split(b"\r\n\r\n", 1)
        if trailing:
            raise LoopbackViewerError("request rejected")
        return head

    def _parse_request(
        self, request: bytes
    ) -> tuple[str, str, dict[bytes, list[bytes]]]:
        lines = request.split(b"\r\n")
        if not lines or len(lines[0]) > MAX_REQUEST_LINE_BYTES:
            raise LoopbackViewerError("request rejected")
        if sum(len(line) + 2 for line in lines[1:]) > MAX_HEADER_BYTES:
            raise LoopbackViewerError("request rejected")
        if len(lines) - 1 > MAX_HEADER_COUNT:
            raise LoopbackViewerError("request rejected")
        request_parts = lines[0].split(b" ")
        if len(request_parts) != 3 or any(not part for part in request_parts):
            raise LoopbackViewerError("request rejected")
        try:
            method = request_parts[0].decode("ascii")
            target = request_parts[1].decode("ascii")
            version = request_parts[2].decode("ascii")
        except UnicodeDecodeError:
            raise LoopbackViewerError("request rejected") from None
        if method != "GET" or version not in {"HTTP/1.0", "HTTP/1.1"}:
            raise LoopbackViewerError("request rejected")
        if not target.startswith("/") or target.startswith("//") or "://" in target:
            raise LoopbackViewerError("request rejected")

        headers: dict[bytes, list[bytes]] = {}
        for line in lines[1:]:
            if not line or line[:1] in {b" ", b"\t"} or b":" not in line:
                raise LoopbackViewerError("request rejected")
            name, value = line.split(b":", 1)
            if not _HEADER_NAME.fullmatch(name):
                raise LoopbackViewerError("request rejected")
            value = value.strip(b" \t")
            if any(byte < 32 and byte != 9 or byte == 127 for byte in value):
                raise LoopbackViewerError("request rejected")
            headers.setdefault(name.lower(), []).append(value)
        return method, target, headers

    def _success_response(self) -> bytes:
        headers = (
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: text/html; charset=utf-8\r\n"
            + f"Content-Length: {len(self._document)}\r\n".encode("ascii")
            + b"Cache-Control: no-store, max-age=0\r\n"
            b"Pragma: no-cache\r\n"
            b"Referrer-Policy: no-referrer\r\n"
            b"X-Content-Type-Options: nosniff\r\n"
            b"Cross-Origin-Resource-Policy: same-origin\r\n"
            b"Content-Security-Policy: default-src 'none'; style-src 'unsafe-inline'; "
            b"img-src 'none'; connect-src 'none'; form-action 'none'; "
            b"base-uri 'none'; frame-ancestors 'none'\r\n"
            b"Connection: close\r\n\r\n"
        )
        return headers + self._document

    def _record_success(
        self, capability_receipt: dict[str, Any], served_at_ns: int
    ) -> None:
        with self._lock:
            assert self._started_at_ns is not None
            assert self._expires_at_ns is not None
            body = {
                "schema": "codex-house-loopback-viewer-receipt/1",
                "state": "SERVED",
                "capability_id": capability_receipt["capability_id"],
                "capability_receipt_id": capability_receipt["receipt_id"],
                "authority": self.authority,
                "started_at_ns": self._started_at_ns,
                "ended_at_ns": served_at_ns,
                "expires_at_ns": self._expires_at_ns,
                "rejected_requests": self._rejected_requests,
                "response_bytes": len(self._document),
                "transport": "LOOPBACK_HTTP_ONE_SHOT",
                "iterm_api_registration": "NOT_ATTEMPTED",
                "terminal_input": "PROHIBITED",
                "reverse_channel": "PROHIBITED",
            }
            self._receipt = _terminal_receipt(body)
        self._stop.set()

    def _record_response_failure(
        self, capability_receipt: dict[str, Any], failed_at_ns: int
    ) -> None:
        with self._lock:
            assert self._started_at_ns is not None
            assert self._expires_at_ns is not None
            body = {
                "schema": "codex-house-loopback-viewer-receipt/1",
                "state": "CAPABILITY_CONSUMED_RESPONSE_FAILED",
                "capability_id": capability_receipt["capability_id"],
                "capability_receipt_id": capability_receipt["receipt_id"],
                "authority": self.authority,
                "started_at_ns": self._started_at_ns,
                "ended_at_ns": failed_at_ns,
                "expires_at_ns": self._expires_at_ns,
                "rejected_requests": self._rejected_requests,
                "response_bytes": 0,
                "transport": "LOOPBACK_HTTP_ONE_SHOT",
                "iterm_api_registration": "NOT_ATTEMPTED",
                "terminal_input": "PROHIBITED",
                "reverse_channel": "PROHIBITED",
            }
            self._receipt = _terminal_receipt(body)
        self._stop.set()

    def _record_rejection(self) -> None:
        with self._lock:
            self._rejected_requests += 1

    def wait(self, timeout: float | None = None) -> dict[str, Any]:
        """Wait for terminal state and return a bearer-free receipt."""
        if self._thread is None:
            raise LoopbackViewerError("viewer is not started")
        if not self._closed.wait(timeout):
            raise LoopbackViewerError("viewer did not close within timeout")
        self._thread.join(timeout=SOCKET_POLL_SECONDS)
        with self._lock:
            assert self._receipt is not None
            return dict(self._receipt)

    def close(self, timeout: float = 2.0) -> dict[str, Any]:
        """Request bounded shutdown and return its terminal receipt."""
        if self._thread is None:
            raise LoopbackViewerError("viewer is not started")
        self._stop.set()
        return self.wait(timeout)

    def is_alive(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

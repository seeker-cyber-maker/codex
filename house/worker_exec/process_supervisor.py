"""Bounded process-group supervision with streamed, non-admitting output."""

from __future__ import annotations

import hashlib
import os
import signal
import subprocess
import threading
from collections.abc import Callable, Mapping, Sequence
from typing import Any


class ProcessSupervisorError(RuntimeError):
    """Raised when a process cannot be safely supervised and reaped."""


PopenFactory = Callable[..., subprocess.Popen[bytes]]


class _Capture:
    """Drain a byte stream without retaining more than a small preview."""

    def __init__(self, *, cap: int = 65_536) -> None:
        self._cap = cap
        self._count = 0
        self._digest = hashlib.sha256()
        self._preview = bytearray()

    def add(self, chunk: bytes) -> None:
        self._count += len(chunk)
        self._digest.update(chunk)
        remaining = self._cap - len(self._preview)
        if remaining > 0:
            self._preview.extend(chunk[:remaining])

    def receipt(self) -> dict[str, object]:
        return {
            "byte_count": self._count,
            "sha256": self._digest.hexdigest(),
            "truncated": self._count > self._cap,
            "utf8_preview": bytes(self._preview).decode("utf-8", errors="replace"),
        }


def _drain(pipe: Any, capture: _Capture) -> None:
    try:
        while chunk := pipe.read(8192):
            capture.add(chunk)
    finally:
        pipe.close()


def supervise_process(
    argv: Sequence[str],
    *,
    wall_seconds: float,
    grace_seconds: float = 1.0,
    environment: Mapping[str, str] | None = None,
    dispatch: str = "PROCESS_OBSERVED",
    popen_factory: PopenFactory = subprocess.Popen,
) -> dict[str, Any]:
    """Observe one subprocess with bounded output and guaranteed reaping.

    This primitive does not interpret output, retry a process, or admit output
    to a task.  Callers must authorize a process separately.
    """

    if not argv or any(not isinstance(part, str) or not part for part in argv):
        raise ProcessSupervisorError("argv must be a non-empty string vector")
    if not 0 < wall_seconds <= 3600 or not 0 < grace_seconds <= 30:
        raise ProcessSupervisorError("invalid supervisor time budget")
    try:
        process = popen_factory(
            list(argv),
            shell=False,
            start_new_session=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=None if environment is None else dict(environment),
        )
    except OSError as exc:
        raise ProcessSupervisorError("fixture process could not be started") from exc
    if process.stdout is None or process.stderr is None:
        raise ProcessSupervisorError("supervisor requires captured stdout and stderr")
    stdout = _Capture()
    stderr = _Capture()
    stdout_thread = threading.Thread(
        target=_drain, args=(process.stdout, stdout), daemon=True
    )
    stderr_thread = threading.Thread(
        target=_drain, args=(process.stderr, stderr), daemon=True
    )
    stdout_thread.start()
    stderr_thread.start()
    cancellation: str | None = None
    try:
        process.wait(timeout=wall_seconds)
        state = "REAPED_EXIT_OBSERVED"
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=grace_seconds)
            cancellation = "SIGTERM"
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
            cancellation = "SIGKILL"
        state = "BLOCKED_TIMEOUT_REAPED"
    stdout_thread.join(timeout=grace_seconds)
    stderr_thread.join(timeout=grace_seconds)
    if process.poll() is None or stdout_thread.is_alive() or stderr_thread.is_alive():
        raise ProcessSupervisorError("process was not reaped after cancellation")
    receipt: dict[str, Any] = {
        "state": state,
        "dispatch": dispatch,
        "returncode": process.returncode,
        "stdout": stdout.receipt(),
        "stderr": stderr.receipt(),
    }
    if cancellation is not None:
        receipt["cancellation"] = cancellation
    return receipt


def supervise_fixture_process(
    argv: Sequence[str],
    *,
    wall_seconds: float,
    grace_seconds: float = 1.0,
    popen_factory: PopenFactory = subprocess.Popen,
) -> dict[str, Any]:
    """Run a local fixture only; it is never connected to task dispatch."""

    return supervise_process(
        argv,
        wall_seconds=wall_seconds,
        grace_seconds=grace_seconds,
        dispatch="FIXTURE_ONLY",
        popen_factory=popen_factory,
    )

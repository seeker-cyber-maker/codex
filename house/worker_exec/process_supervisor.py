"""Bounded local subprocess supervision for a future worker-launch boundary.

This is deliberately an observation primitive.  It never admits worker output
to a task, retries a process, or starts Codex by itself.  Its deterministic
tests use a short-lived local fixture only.
"""

from __future__ import annotations

import os
import signal
import subprocess
from collections.abc import Callable, Sequence
from typing import Any


class ProcessSupervisorError(RuntimeError):
    """Raised when a process cannot be safely supervised and reaped."""


PopenFactory = Callable[..., subprocess.Popen[bytes]]


def _bounded_bytes(value: bytes | None, *, cap: int = 65_536) -> dict[str, object]:
    data = value or b""
    return {
        "byte_count": len(data),
        "truncated": len(data) > cap,
        "utf8_preview": data[:cap].decode("utf-8", errors="replace"),
    }


def supervise_fixture_process(
    argv: Sequence[str],
    *,
    wall_seconds: float,
    grace_seconds: float = 1.0,
    popen_factory: PopenFactory = subprocess.Popen,
) -> dict[str, Any]:
    """Run a local fixture in its own process group and always reap it.

    This function is not connected to task dispatch.  A timeout terminates the
    entire newly-created process group, then escalates to SIGKILL if required;
    the returned state remains blocked and is never a success/result verdict.
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
        )
    except OSError as exc:
        raise ProcessSupervisorError("fixture process could not be started") from exc
    try:
        stdout, stderr = process.communicate(timeout=wall_seconds)
        return {
            "state": "REAPED_EXIT_OBSERVED",
            "dispatch": "FIXTURE_ONLY",
            "returncode": process.returncode,
            "stdout": _bounded_bytes(stdout),
            "stderr": _bounded_bytes(stderr),
        }
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            stdout, stderr = process.communicate(timeout=grace_seconds)
            signal_used = "SIGTERM"
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            stdout, stderr = process.communicate()
            signal_used = "SIGKILL"
        if process.poll() is None:
            raise ProcessSupervisorError("process was not reaped after cancellation")
        return {
            "state": "BLOCKED_TIMEOUT_REAPED",
            "dispatch": "FIXTURE_ONLY",
            "cancellation": signal_used,
            "returncode": process.returncode,
            "stdout": _bounded_bytes(stdout),
            "stderr": _bounded_bytes(stderr),
        }

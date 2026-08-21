#!/usr/bin/env python3
"""Create, monitor, and close one exact iTerm2 benchmark window."""

import asyncio
import json
import pathlib
import shlex
import sys
import time

import iterm2


async def main(connection: iterm2.Connection) -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: run_iterm_benchmark.py RUNNER RESULT")

    runner = pathlib.Path(sys.argv[1]).resolve()
    result = pathlib.Path(sys.argv[2]).resolve()
    app = await iterm2.async_get_app(connection)
    before_ids = sorted(window.window_id for window in app.windows)

    inner_command = (
        f"{shlex.quote(str(runner))} {shlex.quote(str(result))}; sleep 3"
    )
    command = f"/bin/zsh -lc {shlex.quote(inner_command)}"
    window = await iterm2.Window.async_create(connection, command=command)
    if window is None:
        print(json.dumps({"status": "window-ended-before-identification"}))
        return

    created_id = window.window_id
    print(
        json.dumps(
            {
                "status": "created",
                "before_window_ids": before_ids,
                "created_window_id": created_id,
            },
            sort_keys=True,
        ),
        flush=True,
    )

    deadline = time.monotonic() + 45
    observed_result = False
    while time.monotonic() < deadline:
        if result.exists() and "Results:" in result.read_text(errors="replace"):
            observed_result = True
            break
        await asyncio.sleep(0.1)

    await window.async_close(force=True)
    await asyncio.sleep(0.2)
    await app.async_refresh()
    after_ids = sorted(item.window_id for item in app.windows)
    print(
        json.dumps(
            {
                "status": "closed",
                "created_window_id": created_id,
                "result_observed": observed_result,
                "after_window_ids": after_ids,
                "preexisting_windows_preserved": all(
                    window_id in after_ids for window_id in before_ids
                ),
                "created_window_absent": created_id not in after_ids,
            },
            sort_keys=True,
        ),
        flush=True,
    )


iterm2.run_until_complete(main)

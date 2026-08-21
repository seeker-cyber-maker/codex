# Handoff

## Completed

- Pruned the JSONL-over-proxy assumption after isolated source testing.
- Confirmed the current desktop app-server is private stdio, not a shared socket.
- Compared installed iTerm2/Buddy builds with current official beta/source.
- Separated Codex app-server, iTerm2 Python API, and Buddy transports.
- Selected a one-way versioned local display boundary for the next thin slice.

## Current

No live app, provider, thread, iTerm session, relay, or native Codex database was
modified. The repository has no control-socket implementation from this run.

## Next

Implement and test an offline `terminal card -> versioned iTerm display batch`
contract. It must preserve `DISPLAY_ONLY`, `NOT_ATTEMPTED`, one-way direction,
bounded card count, deterministic identity, and explicit compatibility. A live
iTerm Python API adapter remains a later, separately accepted operation.

## Blockers

None for the offline display-batch contract. Live capture is blocked until
Dream House owns a Unix-listening app-server or an upstream event mirror is
designed and reviewed.

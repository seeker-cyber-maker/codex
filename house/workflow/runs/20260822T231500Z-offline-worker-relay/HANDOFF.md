# Handoff

`house.relay` is a separate local SQLite relay, intentionally distinct from
the task-spine inbox/controller and upstream Codex's network rendezvous code.
It accepts an envelope only after all structural constraints validate, then
records queue/delivery/acknowledgment events in a verifiable hash chain.

The read-only compatibility adapter is now `house.relay.RelayDirectory`. It
accepts only an exact `codex-house-local-worker-catalog-receipt/1` receipt,
returns static recipient/capability metadata, and preserves
`NOT_ATTEMPTED`/`NO_AUTHORITY_GRANTED` at every result. It does not make a
worker available, connect a transport, or grant authority.

The keyboard-first relay interface is now `python3 -m house.relay.cli`. It
keeps static directory lookup distinct from relay database operations and
requires explicit artifact/database paths for every operation. It has no
socket, worker, provider, or automatic-routing path.

`house.relay.dashboard.RelayDashboardAdapter` now defines the dashboard request
contract without opening a port. It can prepare read-only directory/capability
or status views; all write-like routes return 418 `integration_pending`.

The next smallest authorized step is a separately reviewed one-shot dashboard
renderer over a frozen adapter response. A persistent listener, browser write
surface, and authority-gated mutation endpoint remain blocked.

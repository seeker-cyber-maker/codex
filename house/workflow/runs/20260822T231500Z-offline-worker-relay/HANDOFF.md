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

The next smallest authorized step is a separate interface review for a relay
CLI/API. It must keep static directory lookup distinct from envelope submission
and retain the existing no-dispatch boundary.

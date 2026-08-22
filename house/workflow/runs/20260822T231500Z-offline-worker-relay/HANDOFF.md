# Handoff

`house.relay` is a separate local SQLite relay, intentionally distinct from
the task-spine inbox/controller and upstream Codex's network rendezvous code.
It accepts an envelope only after all structural constraints validate, then
records queue/delivery/acknowledgment events in a verifiable hash chain.

The next smallest authorized step is a read-only compatibility adapter from a
sealed `codex-house-local-worker-catalog/1` artifact to relay addressing. It
must not make a worker available, connect a transport, or grant authority.

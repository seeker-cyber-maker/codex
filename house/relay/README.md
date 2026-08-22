# Offline worker relay

`house.relay` is the first durable rendezvous seam for worker-to-worker
coordination. It is local SQLite state only: no provider, socket, process,
model, task execution, or human-authority code is called.

Each strict envelope carries a sender, recipient, thread/reply relation,
contract version, hash-bound artifact reference, TTL/hop bound, and finite turn
budget. The relay appends hash-chained queue, delivery, and acknowledgement
events. A stored or delivered proposal never grants any authority.

`RelayDirectory` may expose a sealed `worker_catalog` receipt as static
recipient/capability metadata. It preserves a catalog's `NOT_ATTEMPTED` runtime
disposition; even an `active` catalog label remains descriptive and cannot
select, probe, contact, or dispatch a worker.

The keyboard-first interface is available through `python3 -m house.relay.cli`.
`directory-address` and `directory-capability` require an explicit sealed
receipt path; `submit`, `receive`, `acknowledge`, `status`, and
`verify-journal` require an explicit local relay database. It opens no socket
and reads no provider configuration.

`RelayDashboardAdapter` is the corresponding pure request contract for a future
loopback dashboard. It binds no port: `GET` can prepare directory/capability or
envelope-status views, while each write-like route returns `418` with an
explicit pending-integration receipt. A listener, browser session, and human
authority gate remain separate future work.

This is intentionally distinct from the upstream Codex network rendezvous
transport and the Dream House task-spine controller. A later, separately
qualified bridge may connect them; it must not weaken either contract.

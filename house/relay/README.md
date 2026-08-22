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

This is intentionally distinct from the upstream Codex network rendezvous
transport and the Dream House task-spine controller. A later, separately
qualified bridge may connect them; it must not weaken either contract.

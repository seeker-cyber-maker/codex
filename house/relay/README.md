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

`render_dashboard_html()` turns one exact, already-frozen adapter response into
an inert, self-contained dashboard document. It does not call the adapter or
bind a viewer; any later one-shot viewer binding must preserve the established
loopback capability and observe-only gates.

`prepare_relay_dashboard_viewer()` is that explicit preparation seam. It
constructs the existing capability-bound `OneShotLoopbackViewer` from a frozen
response but does not call `start()`, launch a browser, register with iTerm, or
open any worker, provider, write, terminal-input, or authority path.

`build_relay_preview_registration()` adds the preceding offline operator
contract: it hashes the inert document and prepares an exact display-only
operator request. The descriptor contains neither the document nor a capability
URL, and it does not construct/start a viewer or contact a browser or iTerm.

This is intentionally distinct from the upstream Codex network rendezvous
transport and the Dream House task-spine controller. A later, separately
qualified bridge may connect them; it must not weaken either contract.

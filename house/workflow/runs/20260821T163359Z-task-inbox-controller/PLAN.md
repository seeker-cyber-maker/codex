# Local task inbox/controller plan

## Objective

Add one finite local controller that accepts raw JSON task submissions into a
separate inbox, serializes calls to the existing typed submission adapter, and
records a terminal accepted or rejected disposition without dispatching work.

## Invariants

- Producers may enqueue packets, but only the leased controller calls the task
  spine submission adapter.
- Enqueue identity is bound to the canonical raw packet; reuse with different
  bytes-as-data fails closed.
- Controller ownership uses a finite wall-clock lease, monotonic epoch, and
  opaque fencing token. Every claim and terminal inbox transition verifies the
  current token and expiry.
- A crash after task-spine acceptance but before the inbox terminal update is
  reconciled by replaying the exact submission receipt; it cannot create a
  duplicate work item, task packet, or acceptance event.
- Invalid submissions become terminal `REJECTED` inbox records and do not
  mutate the task-spine journal.
- The controller processes at most one record per `drain_once` call. There is
  no daemon, retry loop, provider, worker, Archive write, network request, or
  native Codex-state access.
- `requested_by` remains asserted and unverified.

## Acceptance

Exact enqueue replay; conflicting enqueue rejection; active-lease exclusion;
stale-token rejection; FIFO finite drain; invalid-packet rejection without
journal mutation; crash/reconcile without duplicate journal events; CLI/API
parity; all task-spine and auto-switcher regressions remain green.

## Claim ceiling

This is a cooperative local controller fixture, not an authenticated or
hostile-process security boundary. Real worker dispatch and OS-enforced writer
isolation remain out of scope.

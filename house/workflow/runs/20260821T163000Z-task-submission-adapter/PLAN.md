# Typed task-submission adapter plan

## Objective

Accept one strict JSON submission and idempotently create or recover the
corresponding Durable Work Item and routed Task Packet in the offline task
spine. Return the exact stored receipt on retry.

## Invariants

- A caller-supplied idempotency key is bound to canonical requester, title,
  summary, and case type; reuse with different content fails closed.
- Work and task IDs are derived from that binding, not guessed or randomized.
- Partial creation is reconciled only when existing journal payloads match.
- Unknown fields and invalid case types are rejected.
- `dispatch` remains `NOT_ATTEMPTED`; no worker, provider, network, Archive, or
  native Codex state enters scope.

## Acceptance

Exact replay without new journal events; conflicting-key rejection; partial
resume; compound-prompt continuation; strict-field rejection; CLI/API parity;
task-spine and auto-switcher regressions remain green.

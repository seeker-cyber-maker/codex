# Display-batch reconciler plan

## Objective

Add a small offline reconciler for the existing one-way iTerm display batches.
It accepts a snapshot-rooted ordered tail despite bounded duplicate or
out-of-order delivery, but never opens transport, mutates iTerm, or supplies a
reverse/control channel.

## Source basis

Warp's shared-session viewer keeps a bounded out-of-order event buffer and
applies only the next contiguous event, while preserving replay identity.

## Invariants

- Reuse the current sealed display-batch identity and chain contract.
- Accept only the contiguous sequence for application; buffer at most 50
  future batches and reject a sequence farther than 50 ahead.
- A replayed identical already-applied batch is inert; a conflicting batch for
  that sequence fails closed.
- A predecessor mismatch fails before any state change.
- No live listener, iTerm registration, persistence, source capture, model
  dispatch, or reverse channel is introduced.

## Acceptance

- Focused tests cover in-order, out-of-order, duplicate, conflicting,
  predecessor-mismatch, and bound-rejection behavior.
- Existing display-batch and full House suites stay green.

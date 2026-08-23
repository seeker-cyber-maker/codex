# Operator-board viewer preparation — plan v1

## Model advisory

- Next phase: `semantic_implementation` at a loopback capability boundary.
- Recommendation: Terra / high.
- Reason: this composes a verified immutable export with a qualified
  capability-bound viewer without allowing it to start.
- Reassess: Sol / high before listener activation, browser/iTerm binding,
  authority approval, persistent transport, or a new external operation.
- This is advisory only; no client model switch is asserted.

## Objective

Prepare the existing one-shot loopback viewer from one caller-named, completed
operator-board export only after its canonical receipt and board bytes verify.

## Non-goals

- No `start()` call, listener bind, capability issue, browser/iTerm launch,
  path template loading, source/output discovery, write/replace/cleanup,
  refresh, relay/task access, worker/provider call, terminal input, authority
  action, or reverse channel.

## Acceptance

1. Preparation accepts only a named valid export; incomplete, changed, missing,
   symlinked, or relative paths fail before a viewer is returned.
2. A second byte-hash check freezes exactly the verified UTF-8 board document
   before constructing the viewer.
3. The returned viewer remains unstarted and retains the underlying exact
   loopback host/port/TTL validation.
4. Focused and full component tests, compilation, lint, formatting, and diff
   checks pass.

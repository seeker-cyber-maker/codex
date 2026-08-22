# Council synthesis

## Decision

**Narrow accept for offline injected-fixture interface implementation only.**
All reviewers confirmed the evidence-packet SHA-256
`21441884930b0a692ddd544c91f6f808066e307fbfddf50a5fb9ce739061b106`.
This was a multi-agent, same-model-family local review; it is not
cross-provider validation. Live dispatch remains blocked.

## Confirmed observations

- The existing modules create/verify operation records and provide finite
  controller fencing, a captured CLI grammar contract, and fixture-only
  process-group supervision.
- The installed `codex exec` grammar rejects `--ask-for-approval`.
- No current module starts Codex for a task, calls a provider, imports output,
  or marks a task complete.

## Material findings

1. The stored argv begins with the literal `codex`, while the sealed executable
   is absolute. A future direct argv launch could be substituted through PATH.
   The argv must instead begin with the sealed absolute executable, with a
   malicious-PATH fixture test.
2. The first interface needs a controller-owned, final fence validation and a
   safe output-directory reservation immediately before its injected runner.
   Any failure must prevent runner invocation.
3. A real runner needs further, separate review: atomic spawn-intent/RUNNING
   durability, no-relaunch ambiguity semantics, lease behavior relative to the
   wall cap, bounded output streaming, and explicit runtime configuration,
   hook, provider, and egress qualification.

## Smallest next action

Implement and test only the injected-fixture launch gate with absolute sealed
executable argv, explicit execute consent, final record/contract/fence checks,
and exclusive output reservation. Keep real Codex execution unavailable by
construction.

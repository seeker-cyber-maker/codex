# Hash-bound operator snapshot descriptor — plan v1

## Model advisory

- Next phase: deterministic receipt and replay verification for frozen static
  snapshot documents.
- Recommendation: Terra / high.
- Reason: digest and exact-field validation establish a provenance boundary
  without adding runtime integration.
- Reassess: Sol / high before live source capture, refresh, storage activation,
  task mutation/dispatch, listener, browser/iTerm integration, or authority.
- This is an advisory only; no client model switch is asserted.

## Objective

Build and verify a compact descriptor that binds a caller-supplied relay-preview
index, task-card index, and composed operator snapshot by SHA-256.

## Non-goals

- No source retrieval, file/database read beyond explicit caller-supplied
  strings, refresh, listener, browser/iTerm call, terminal input, task/relay
  mutation, worker/provider call, capability issue, authority action, or
  reverse channel.

## Acceptance

1. The descriptor has an exact schema, stable canonical hash, and no source
   document bodies.
2. Build validates that the supplied snapshot is an exact static recomposition
   of the two supplied source documents.
3. Verification fails closed for any descriptor, input, output, digest, or
   control-state tampering.
4. Focused and all component test suites plus static checks pass.

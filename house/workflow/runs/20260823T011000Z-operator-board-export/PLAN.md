# Immutable operator-board export — plan v1

## Model advisory

- Next phase: bounded local board export with no-overwrite and interruption
  semantics.
- Recommendation: Terra / medium.
- Reason: the page contract is already sealed; this phase is filesystem
  identity and receipt handling, not live integration.
- Reassess: Sol / high before replacement, cleanup, retention, auto-export,
  viewer binding, refresh, task/relay integration, or authority action.
- This is advisory only; no client model switch is asserted.

## Objective

Write one composed caller-supplied operator board to a new absolute local file
beside a canonical receipt, while refusing overwrite and preserving interrupted
state visibly.

## Non-goals

- No source discovery/refresh, inventory run, path scan, replacement, deletion,
  cleanup, retention, automatic export, relay/task state access, listener/
  viewer/browser/iTerm call, terminal input, provider/worker call, task
  mutation/dispatch, capability issue, authority action, or reverse channel.

## Acceptance

1. Source documents are statically composed and validated before any output or
   marker exists. Output, companion receipt, and marker paths must all be new.
2. The board and canonical receipt use exclusive creation; marker removal is
   last, so a failed sequence remains visibly incomplete.
3. Inspection rejects incomplete, missing, symlinked, noncanonical, wrong-kind,
   or hash-changed board/receipt pairs.
4. Focused and all component tests plus compilation, lint, format, and diff
   checks pass.

# Frozen operator-board export CLI — plan v1

## Model advisory

- Next phase: command-debug-class CLI wiring for the sealed board-export
  function.
- Recommendation: Spark or Luna / low.
- Reason: the board/export contracts are sealed; this is explicit argument
  parsing, UTF-8 file loading, and local testable handoff.
- Reassess: Terra or Sol before source discovery, overwrite/retry/repair,
  storage lifecycle automation, authentication, viewer integration, relay/task
  access, or authority action.
- This is advisory only; no client model switch is asserted.

## Objective

Expose the existing immutable board-export seam through one manual CLI command
that requires two caller-named frozen HTML source files and one new output
path.

## Non-goals

- No source/destination default, discovery, scan, overwrite, replacement,
  cleanup, retry, repair, relay database access, task-state access, listener,
  viewer/browser/iTerm call, terminal-input loop, worker/provider call,
  capability issue, authority action, or reverse channel.

## Acceptance

1. `export-operator-board` requires `--operator-snapshot`,
   `--inventory-board`, and `--output`; source files are UTF-8 text inputs.
2. The command calls the existing no-overwrite export function before a relay
   object is constructed, and returns its static receipt.
3. The output contract remains responsible for an absolute new destination,
   canonical receipt, and incomplete marker behavior.
4. Focused and full component tests, compilation, lint, formatting, diff, and
   source-scope checks pass.

# Operator-board export path template — plan v1

## Model advisory

- Next phase: command-debug-class static template and documentation update.
- Recommendation: Spark or Luna / low.
- Reason: this is inert JSON shape validation and documentation; no runtime
  integration, source selection, or state transition is introduced.
- Reassess: Terra or Sol before parsing templates automatically, selecting
  paths, filesystem lifecycle automation, viewer binding, relay/task access,
  or authority action.
- This is advisory only; no client model switch is asserted.

## Objective

Provide a copyable record of the exact three manual values required by
`export-operator-board` without making it a configuration file or adding a
second command surface.

## Non-goals

- No CLI parser changes, template loading, default source/destination,
  discovery, scan, output creation, overwrite, cleanup, repair, relay/task
  access, viewer/browser/iTerm call, terminal-input loop, worker/provider
  call, capability issue, authority action, or reverse channel.

## Acceptance

1. The template is valid JSON with only the exact three named fields and
   deliberately nonexistent absolute placeholders.
2. Documentation states that callers substitute values manually and the CLI
   continues to require explicit flags.
3. JSON parsing, command help, focused tests, full component tests, and diff
   checks pass.

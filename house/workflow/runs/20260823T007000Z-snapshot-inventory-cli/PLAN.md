# One-shot snapshot inventory CLI — plan v1

## Model advisory

- Next phase: deterministic command wiring to an existing sealed inventory.
- Recommendation: Spark or Luna / low.
- Reason: argument parsing and JSON input/output are mechanical, local, and
  fixture-verifiable; no provider or runtime integration is in scope.
- Reassess: Terra / medium if command behavior diverges from the pure
  inventory; Sol / high before discovery, persistence, authentication, or an
  active dashboard.
- This is advisory only; no client model switch is asserted.

## Objective

Expose the content-free snapshot inventory through one keyboard-first,
one-shot relay CLI command with a required explicit JSON path-list input.

## Non-goals

- No default path, directory/volume scan, glob expansion, write/retry/repair/
  delete/cleanup/retention, source capture/refresh, relay database open,
  task/relay state access, listener/viewer/browser/iTerm call, terminal input
  beyond the declared file path, provider/worker call, task mutation/dispatch,
  capability issue, authority action, or reverse channel.

## Acceptance

1. `snapshot-inventory --input <file>` is required and accepts only the JSON
   list contract already enforced by the inventory module.
2. The command emits content-free results and rejects object/non-list JSON.
   It returns before any relay database construction.
3. Existing relay CLI commands remain behaviorally unchanged.
4. Focused and all component tests plus compilation, lint, format, and diff
   checks pass.

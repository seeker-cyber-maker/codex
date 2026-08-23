# Static task-card index — plan v1

## Model advisory

- Next phase: bounded static composition of canonical task-card projections.
- Recommendation: Terra / high.
- Reason: this is a semantic renderer with strict schema and presentation
  boundaries, but no live integration.
- Reassess: Sol / high before polling, task mutation, task dispatch, a
  listener, browser/iTerm integration, or authority action.
- This is an advisory only; no client model switch is asserted.

## Objective

Render up to 32 canonical `codex-house-task-card/1` projections into one
deterministic, inert HTML task index beside the relay-preview index.

## Non-goals

- No task-spine database access, journal rebuild, task creation/mutation,
  dispatch, worker/provider call, listener, browser/iTerm call, terminal input,
  capability issue, authority action, refresh, or reverse channel.
- No accepted task-card schema extension or inferred model switch.

## Acceptance

1. Only exact canonical task-card projections are accepted; malformed nested
   routing data, duplicate task IDs, unsupported dispatch states, and oversized
   text fail closed.
2. Rendering is deterministic, escaped, bounded, and contains no active HTML,
   network, form, or navigation behavior.
3. Model routing remains visibly advisory and dispatch remains
   `NOT_ATTEMPTED`.
4. Focused and full House regressions plus static checks pass.

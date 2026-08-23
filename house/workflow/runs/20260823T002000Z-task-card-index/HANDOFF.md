# Static task-card index — handoff

## Accepted milestone

`render_task_card_index_html()` renders zero to 32 exact canonical
`codex-house-task-card/1` projections as a deterministic, escaped, inert HTML
document. It preserves advisory-only routing and rejects any dispatch state
other than `NOT_ATTEMPTED`.

The renderer does not consult a task-spine database/journal, rebuild a
projection, create/mutate/dispatch a task, contact a worker/provider, bind or
refresh a listener, start a viewer, launch a browser, call iTerm, accept input,
grant authority, or open a reverse channel.

## Evidence

- 23 focused task-card/relay/task-spine tests pass.
- 168 full House tests pass.
- Compilation, changed-file Ruff checks/format, and diff checks pass.
- An unclassified canonical task-card compatibility mismatch was reproduced
  from `TaskSpine.task_cards()`, corrected, and covered by regression test.

## Model advisory receipt

Terra / high was recommended before this deterministic composition phase. No
client model switch is asserted. Escalate to Sol / high before live task-state
access, polling, a listener, browser/iTerm integration, task mutation/dispatch,
or authority action.

## Next gate

The next candidate is an offline composition contract that places the relay
preview index and task-card index together without calling either source,
loading live state, or adding an action surface.

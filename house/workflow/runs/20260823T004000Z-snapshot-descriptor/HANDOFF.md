# Hash-bound snapshot descriptor — handoff

## Accepted milestone

`build_operator_snapshot_descriptor()` binds one caller-supplied relay-preview
index, task-card index, and exact static operator snapshot using SHA-256.
`verify_operator_snapshot_descriptor()` validates descriptor fields and
replays the static composition before accepting that identity relation.

The descriptor stores no document bodies. It does not retrieve or persist
documents, refresh/bind a listener, read live task/relay state, create/mutate/
dispatch a task, contact a worker/provider, start a viewer, launch a browser,
call iTerm, accept input, grant authority, or open a reverse channel.

## Evidence

- 14 focused descriptor/snapshot/source-index tests pass.
- All 10 component test suites pass: 234 tests total.
- Compilation, changed-file Ruff checks/format, and diff checks pass.
- Invalid source, output mismatch, valid-but-different replay, descriptor
  control-state tampering, and digest tampering all fail closed.

## Model advisory receipt

Terra / high was recommended before this receipt/replay phase. No client model
switch is asserted. Escalate to Sol / high before live capture, persistence,
refresh, task-state access, listener, browser/iTerm integration, task mutation/
dispatch, or authority action.

## Next gate

The next candidate is a bounded local artifact envelope that can store the
three frozen document bytes beside this descriptor with explicit path/identity
and overwrite/refusal rules. It must remain an offline operator action, not an
automatic capture or dashboard service.

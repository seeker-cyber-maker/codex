# Named offline snapshot inventory — handoff

## Accepted milestone

`inspect_operator_snapshot_inventory()` accepts an explicit list or tuple of
one to 32 absolute paths and independently verifies each through the immutable
snapshot-envelope receipt. It returns only canonical path identity, state,
reason, and on success descriptor/envelope hashes. It performs no scan,
write, repair, retry, cleanup, or state capture.

## Evidence

- 21 focused inventory/envelope/descriptor/snapshot/source-index tests pass.
- All component test suites, relay compilation, changed-file Ruff checks and
  formatting, and diff checks pass (recorded in `VALIDATION.json`).
- Relative, duplicate canonical, missing, and incomplete paths reject without
  affecting independently valid paths. Stored snapshot bodies are absent from
  output.

## Model advisory receipt

Terra / high was recommended for this bounded evidence-review phase. No client
model switch is asserted. Escalate to Sol / high before arbitrary storage
discovery, retention/cleanup, live capture, listener, browser/iTerm
integration, task mutation/dispatch, or authority action.

## Next gate

The next candidate is a manual operator command interface that accepts an
explicit JSON list of paths and prints this content-free inventory. It must
remain a one-shot local read operation: no default path, discovery, storage
write, task creation, viewer, listener, or dashboard activation.

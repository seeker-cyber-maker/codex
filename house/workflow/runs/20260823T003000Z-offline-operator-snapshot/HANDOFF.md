# Offline operator snapshot — handoff

## Accepted milestone

`render_operator_snapshot_html()` composes one already-rendered relay-preview
index and one already-rendered task-card index into deterministic, static HTML.
It validates each source's exact static signature, containment marker, bounded
fragment grammar, and source kind; malformed, swapped, active, or oversized
documents fail closed.

It does not invoke either renderer or read a relay/task-spine database. It does
not refresh/bind a listener, create/mutate/dispatch a task, contact a
worker/provider, start a viewer, launch a browser, call iTerm, accept input,
grant authority, or open a reverse channel.

## Evidence

- 11 focused snapshot/source-index tests pass.
- All 10 component test suites pass: 231 tests total.
- Compilation, changed-file Ruff checks/format, and diff checks pass.
- A malicious source fragment is rejected; the first validation error is
  retained deterministically.
- `TEST_SCOPE.md` records why the conventional broad discovery command alone
  is insufficient for this checkout.

## Model advisory receipt

Terra / high was recommended before this static composition phase. No client
model switch is asserted. Escalate to Sol / high before source refresh, live
task-state access, a listener, browser/iTerm integration, task mutation/
dispatch, or authority action.

## Next gate

The next candidate is a hash-bound snapshot descriptor that records the two
frozen input document digests and composed output digest without adding a
listener, refresh path, or action surface.

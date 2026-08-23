# Immutable offline snapshot envelope — handoff

## Accepted milestone

`write_operator_snapshot_envelope()` persists one descriptor-verified frozen
snapshot only at an explicit absolute, non-existent directory. It refuses
overwrite, writes immutable document and canonical JSON receipt files, and
leaves `.INCOMPLETE` on an interrupted write. `inspect_operator_snapshot_envelope()`
requires the exact final file set and validates byte hashes, canonical JSON,
descriptor identity, and static replay.

## Evidence

- 18 focused envelope/descriptor/snapshot/source-index tests pass.
- All component test suites, relay compilation, changed-file Ruff checks and
  formatting, and diff checks pass (recorded in `VALIDATION.json`).
- Existing path, relative path, invalid descriptor-before-create, changed
  snapshot byte, and incomplete-marker cases fail closed.

## Model advisory receipt

Terra / high was recommended for this filesystem-bound phase. No client model
switch is asserted. Escalate to Sol / high before any automatic capture,
replacement, cleanup, retention policy, live source access, listener,
browser/iTerm integration, task mutation/dispatch, or authority action.

## Next gate

The next candidate is a read-only local inventory of explicit envelope paths
for operator selection. It must not scan arbitrary storage, infer retention,
delete incomplete envelopes, capture live state, or make a dashboard active.

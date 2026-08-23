# Operator-board viewer preparation — handoff

## Accepted milestone

`prepare_operator_board_viewer(output_path)` is an unstarted, prepare-only
seam for a specific completed operator-board export. It rejects invalid export
state before returning a viewer, rechecks the read bytes against the export
receipt, and has no listener or capability side effect.

## Evidence

- Focused operator-board viewer/export/dashboard-viewer tests pass.
- Full House tests, relay compilation, scoped Ruff checks/formatting, and diff
  checks are recorded in `VALIDATION.json`.
- The implementation, initializer, test, and documentation hashes are sealed
  in `SOURCE_SEAL.json`.

## Model advisory receipt

Terra / high was recommended for the loopback-capability boundary. No client
model switch is asserted. Escalate to Sol / high before any start action,
browser/iTerm binding, authority approval, persistent transport, or external
operation.

## Next gate

Viewer activation remains blocked pending a separately sealed operation and
explicit human authority. Do not add a CLI start command or automatically open
a browser/iTerm from this preparation seam.

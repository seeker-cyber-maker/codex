# Immutable operator-board export — handoff

## Accepted milestone

`write_operator_board_export()` writes one validated frozen board and canonical
companion receipt at a caller-named new absolute file path. It refuses existing
board, receipt, or marker paths and leaves a sibling `.INCOMPLETE` marker after
an interrupted write. `inspect_operator_board_export()` verifies the final page
kind, canonical receipt, and board hash without retrieving source documents.

## Evidence

- 14 focused export/board/view/envelope/CLI tests pass.
- All component test suites, relay compilation, changed-file Ruff checks and
  formatting, and diff checks pass (recorded in `VALIDATION.json`).
- Existing, invalid-before-create, incomplete, missing, symlinked, and changed
  board states fail closed.

## Model advisory receipt

Terra / medium was recommended for this storage-lifecycle phase. No client
model switch is asserted. Escalate to Sol / high before replacement, cleanup,
retention, automatic export, viewer binding, refresh, task/relay integration,
or authority action.

## Next gate

The next candidate is a manual CLI command that accepts explicit frozen source
files and a new absolute output file, then invokes this export seam. It must
have no default source/destination, no scanning, no overwrite option, and no
viewer activation.

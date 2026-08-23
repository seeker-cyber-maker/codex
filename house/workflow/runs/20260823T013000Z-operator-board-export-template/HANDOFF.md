# Operator-board export path template — handoff

## Accepted milestone

`house/relay/examples/operator-board-export-paths.example.json` provides a
copyable record of the explicit `operator_snapshot`, `inventory_board`, and
`output` values. Replace the placeholders manually, then pass those values to
the existing `export-operator-board` flags. The template itself is never read
by the command.

## Evidence

- JSON parsing, `export-operator-board --help`, focused relay CLI/export tests,
  all House component tests, and diff checks pass.
- The exact documentation/template bytes are recorded in `SOURCE_SEAL.json`.

## Model advisory receipt

Spark or Luna / low was recommended for this inert template phase. No client
model switch is asserted. Reassess before any automatic parsing, source/dest
selection, filesystem lifecycle action, viewer integration, relay/task access,
or authority action.

## Next gate

The read-only operator-board path is complete through manual export. Any
viewer integration must be separately designed and acceptance-gated; no
listener or automatic source collection is authorized by this template.

# Frozen operator-board export CLI — handoff

## Accepted milestone

The manual keyboard-first command is available:

```bash
python3 -m house.relay.cli export-operator-board \
  --operator-snapshot /path/to/frozen-operator-snapshot.html \
  --inventory-board /path/to/frozen-snapshot-inventory.html \
  --output /absolute/path/to/new-operator-board.html
```

All three paths are required. Source paths are explicit UTF-8 files; the
output must be a new absolute file path under an existing parent. The command
does not open a relay DB or viewer and has no defaults, source discovery,
scanning, or overwrite option.

## Evidence

- `test_cli`, export, board, inventory-view, and snapshot-envelope focused
  tests pass.
- All House component test suites, relay compilation, scoped Ruff checks,
  scoped formatting, and diff checks are recorded in `VALIDATION.json`.
- The `SOURCE_SEAL.json` hashes the three implementation/document/test files.

## Model advisory receipt

Spark or Luna / low was recommended for this sealed CLI-wiring phase. No client
model switch is asserted. Reassess before any source discovery, filesystem
lifecycle automation, authentication, viewer integration, relay/task access,
or authority action.

## Next gate

Keep the next step read-only: a static help/template artifact for supplying
three manually frozen CLI paths, or separately design a viewer integration
gate. Do not activate a listener or automate source collection.

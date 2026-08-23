# After-action review — one-shot snapshot inventory CLI

## Outcome

The relay CLI now has one explicit `snapshot-inventory --input` command. It
loads a caller-provided UTF-8 JSON array and delegates to the sealed inventory
module. Its branch executes before the relay constructor, so the operation does
not open a relay database or acquire any dispatch-adjacent state.

## Correction during implementation

The test preserves the command's strict input type: a JSON object containing a
plausible `paths` field is rejected rather than silently becoming a second
schema. The ordinary `argparse` error text is expected negative-test evidence.

## Boundary

This is a local one-shot read command, not a path discovery tool, snapshot
writer, repair service, dashboard, relay transport, task controller,
browser/iTerm integration, or authority path.

# One-shot snapshot inventory CLI — handoff

## Accepted milestone

`python3 -m house.relay.cli snapshot-inventory --input <absolute-json-file>`
prints only the existing content-free inventory for its explicit JSON array of
one to 32 absolute envelope paths. It has no default source or scan and returns
before any relay database is opened.

## Evidence

- 24 focused CLI/inventory/envelope/descriptor/snapshot/source-index tests pass.
- All component test suites, relay compilation, changed-file Ruff checks and
  formatting, and diff checks pass (recorded in `VALIDATION.json`).
- The command accepts a verified envelope list; object-shaped JSON fails via
  the existing list-or-tuple contract without opening the relay.

## Model advisory receipt

Spark or Luna / low was recommended for this mechanical command-wiring phase.
No client model switch is asserted. Escalate to Terra / medium if the command
diverges from the sealed pure inventory and to Sol / high before discovery,
persistence, authentication, or a live dashboard.

## Next gate

The next candidate is an optional static help example that documents the exact
input JSON shape without embedding real paths or creating a default source. It
must remain documentation-only; no command should infer a target or activate
storage, tasks, viewer, listener, browser/iTerm, worker, provider, or authority.

# Relay preview registration contract — handoff

## Accepted milestone

`build_relay_preview_registration()` validates and renders one frozen relay
response, retains only its document SHA-256, and prepares the shared
`codex.house.relay.preview` display-only command with that exact target.

It is deterministic and contains neither the rendered content nor any bearer
capability. It does not construct/start a viewer, bind a socket, launch a
browser, call iTerm, mutate the relay, contact a worker/provider, or grant
authority.

## Evidence

- 44 focused relay/operator tests pass.
- 168 full House tests pass.
- Compilation, changed-file Ruff check/format, and diff checks pass.

## Model advisory receipt

Terra / high was recommended before this bounded offline integration. No client
model switch is asserted. Escalate to Sol / high before any live browser/iTerm
registration, listener lifecycle, or human-authority work.

## Next gate

The next smallest useful slice is a static operator-facing preview card that
renders this descriptor without revealing content/capability material or
starting anything. A live handoff remains a separate, higher-consequence gate.

# Relay preview card — handoff

## Accepted milestone

`render_relay_preview_card_html()` renders one exact, hash-verified relay
preview-registration descriptor as inert HTML. The card shows only the
document, request, and registration hashes plus fixed display-only state. It
does not reveal the dashboard content or capability material.

The renderer rejects malformed descriptors, altered state, altered command
authority, or hash mismatches before rendering. It cannot construct/start the
viewer or trigger a browser, iTerm, authority, worker/provider, mutation,
terminal-input, or reverse-channel path.

## Evidence

- 43 focused presentation tests pass.
- 168 full House tests pass.
- Compilation, changed-file Ruff check/format, and diff checks pass.

## Model advisory receipt

Terra / high was recommended before this offline presentation phase. No client
model switch is asserted. Escalate to Sol / high before any live operator
handoff, listener lifecycle, browser/iTerm registration, or authority action.

## Next gate

The next candidate is an offline queue/status composition surface that combines
several already-sealed cards. It must remain read-only and must not add a
listener, automatic refresh, execution, or approval path.

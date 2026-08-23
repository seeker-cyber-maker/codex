# Relay preview index — handoff

## Accepted milestone

`render_relay_preview_index_html()` composes zero to 32 independently verified
relay preview registrations into deterministic static HTML. It uses only the
safe document/request/registration hashes returned by descriptor validation,
sorts them canonically, and rejects duplicate or invalid registrations.

It does not expose dashboard content, capability material, or any live state.
It does not create descriptors, construct/start viewers, bind/refresh a
listener, launch a browser, call iTerm, grant authority, mutate state, contact
workers/providers, accept terminal input, or open a reverse channel.

## Evidence

- 46 focused presentation tests pass.
- 168 full House tests pass.
- Compilation, changed-file Ruff check/format, and diff checks pass.

## Model advisory receipt

Terra / high was recommended before this deterministic composition phase. No
client model switch is asserted. Escalate to Sol / high before any polling,
listener, browser/iTerm registration, task mutation, or authority action.

## Next gate

The next candidate is a read-only task-card composition contract that can sit
beside this relay index. It must consume canonical task-card projections only
and remain a static/no-listener surface.

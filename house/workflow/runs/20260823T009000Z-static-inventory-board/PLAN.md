# Static snapshot-inventory board — plan v1

## Model advisory

- Next phase: strict static presentation of caller-supplied inventory records.
- Recommendation: Terra / high.
- Reason: the board must preserve the distinction between display data and a
  live verifier while remaining inert and privacy-bounded.
- Reassess: Sol / high before viewer binding, refresh, automatic filesystem
  access, task/relay integration, browser/iTerm activation, or authority.
- This is advisory only; no client model switch is asserted.

## Objective

Render one to 32 already-produced snapshot-inventory records as escaped,
content-free static HTML for operator inspection.

## Non-goals

- No inventory call, path/filesystem read, source discovery/refresh, storage
  mutation/repair/cleanup/retention, relay/task state access, listener/viewer/
  browser/iTerm call, terminal input, provider/worker call, task mutation/
  dispatch, capability issue, authority action, or reverse channel.

## Acceptance

1. Exact success and rejection record shapes are required; unknown state,
   extra fields, malformed hashes, empty input, and more than 32 records fail
   closed.
2. Every display value is escaped. The document has a restrictive CSP and no
   link, form, script, fetch, websocket, refresh, or action surface.
3. The summary labels records caller-supplied rather than asserting the page
   itself obtained or verified them.
4. Focused and all component tests plus compilation, lint, format, and diff
   checks pass.

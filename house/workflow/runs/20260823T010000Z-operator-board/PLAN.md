# Frozen operator board — plan v1

## Model advisory

- Next phase: strict static composition of two caller-supplied operator pages.
- Recommendation: Terra / high.
- Reason: source validation must distinguish frozen page fragments from a live
  reader or accidental active markup.
- Reassess: Sol / high before viewer binding, refresh, automatic filesystem
  access, task/relay integration, browser/iTerm activation, or authority.
- This is advisory only; no client model switch is asserted.

## Objective

Compose one frozen operator snapshot and one frozen snapshot-inventory board
into a single static operator page.

## Non-goals

- No inventory call, path/filesystem read, source discovery/refresh, storage
  write/repair/cleanup/retention, relay/task state access, listener/viewer/
  browser/iTerm call, terminal input, provider/worker call, task mutation/
  dispatch, capability issue, authority action, or reverse channel.

## Acceptance

1. Both documents require exact title/summary/containment signatures and a
   bounded static main fragment; swapped, malformed, or active sources fail
   closed.
2. The output has restrictive CSP and no link, form, script, fetch, websocket,
   refresh, or action surface.
3. The output says caller-supplied frozen documents, not live data or a fresh
   verification claim.
4. Focused and all component tests plus compilation, lint, format, and diff
   checks pass.

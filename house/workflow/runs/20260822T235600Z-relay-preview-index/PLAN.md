# Relay preview index — plan v1

## Model advisory

- Next phase: bounded offline composition of verified relay preview descriptors.
- Recommendation: Terra / high.
- Reason: deterministic local rendering over existing verified fields only.
- Reassess: Sol / high before aggregation adds polling, a listener, browser/iTerm
  integration, task mutation, or authority.
- The advisory was delivered before implementation resumed; no client model
  switch is asserted.

## Objective

Render up to a bounded number of independently verified relay preview
registrations as one deterministic, read-only, content-free HTML index.

## Non-goals

- No descriptor construction, viewer start, listener, refresh, browser/iTerm
  call, capability issue, authority, task/relay mutation, worker/provider call,
  terminal input, or reverse channel.

## Acceptance

1. Only validated identifiers from each registration may reach HTML.
2. Order is canonical and duplicates fail closed.
3. Source dashboard content cannot appear in the index.
4. The document is inert and bounded.
5. Focused and full House regressions plus static checks pass.

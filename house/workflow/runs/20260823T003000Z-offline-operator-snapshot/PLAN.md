# Offline operator snapshot — plan v1

## Model advisory

- Next phase: static composition of frozen relay-preview and task-card HTML.
- Recommendation: Terra / high.
- Reason: the composition must preserve strict no-source-call and inert-content
  boundaries across independently validated documents.
- Reassess: Sol / high before source refresh, live task-state access, a
  listener, browser/iTerm integration, task mutation/dispatch, or authority.
- This is an advisory only; no client model switch is asserted.

## Objective

Compose one relay-preview index document and one task-card index document into
a deterministic, static, offline operator snapshot without invoking either
renderer or reading their backing state.

## Non-goals

- No rendering-source invocation, task-spine/relay database access, refresh,
  listener, browser/iTerm call, terminal input, task mutation/dispatch,
  worker/provider call, capability issue, authority action, or reverse channel.

## Acceptance

1. Only bounded documents with the exact source signatures and safe static
   fragment grammar are accepted.
2. The composed document is deterministic, retains escaped source text, and
   introduces no active HTML, network, form, navigation, or script behavior.
3. The composition is one-way presentation only; source documents remain
   immutable inputs.
4. Focused and all ten component test suites plus static checks pass.

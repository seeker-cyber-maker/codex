# Relay preview card — plan v1

## Model advisory

- Next phase: static operator-facing relay preview card.
- Recommendation: Terra / high.
- Reason: bounded, local rendering over a sealed registration descriptor.
- Reassess: Sol / high before any listener, browser/iTerm API, or authority
  integration.
- The advisory was delivered before implementation resumed; no client model
  switch is asserted.

## Objective

Render a descriptor-only static preview card that lets an operator see the
exact pending display action without exposing relay content or a capability.

## Non-goals

- No viewer construction/start, listener, browser/iTerm call, capability issue,
  authority action, worker/provider call, relay mutation, terminal input, or
  reverse channel.

## Acceptance

1. Exact descriptor and command shapes plus both digests are verified.
2. Only fixed control-plane fields and hashes appear in the document.
3. HTML is inert and no document/capability content can leak into it.
4. Focused and full House tests, static checks, and diff checks pass.

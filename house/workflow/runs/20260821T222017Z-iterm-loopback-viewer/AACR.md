# After-action review

## Outcome

The bounded live transport is complete without activating the iTerm surface.
The first outside plan review blocked two real omissions—Host binding and raw
request resource limits—before implementation. Adding those requirements
produced a smaller and more testable transport.

## What held

- Recovery followed the previous handoffs and did not duplicate accepted code.
- Capability issuance occurs only after binding to a measured exact-loopback
  authority.
- Invalid traffic cannot consume the valid capability or extend its monotonic
  deadline.
- Bearer values remain ephemeral and absent from representations and receipts.
- Capability consumption followed by response failure has an explicit
  fail-closed terminal state.
- The implementation has no iTerm import, activation CLI, terminal input,
  reverse channel, provider, or Codex-state path.

## Remaining gap

A one-shot URL is not yet a usable persistent iTerm toolbelt integration.
Installed API source documents duplicate reveal but exposes no URL refresh or
unregister wrapper. WKWebView request headers and reload behavior remain
unverified. Those are deliberate blockers for a later registration experiment,
not defects hidden by this closure.

## Closure

`CLOSED_LOCAL_DURABLE` after validation, source-seal verification, and local
commit. Remote push and iTerm registration are not authorized in this phase.

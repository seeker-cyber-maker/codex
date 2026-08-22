# Relay preview registration contract — plan v1

## Model advisory

- Next phase: offline operator-registration descriptor and approval contract.
- Recommendation: Terra / high.
- Reason: bounded semantic integration over already-sealed operator-registry,
  renderer, and one-shot-viewer contracts.
- Reassess: Sol / high before browser/iTerm registration, listener start, or
  human authority integration.
- This advisory was delivered before work resumed; no client model switch is
  asserted.

## Objective

Create an offline, deterministic registration descriptor for one frozen relay
dashboard document. It must bind an explicit display-only operator request to
the document SHA-256 without retaining the document or issuing a bearer URL.

## Non-goals

- No viewer construction or start, socket, browser launch, iTerm API call,
  worker/provider call, relay mutation, terminal input, reverse channel, or
  authority grant.

## Acceptance

1. Descriptor is deterministic and hashes only a renderer-validated document.
2. It emits the shared display-only command with an exact document target.
3. It contains no document content or capability/bearer URL.
4. Invalid or pre-bound adapter responses fail before a request is prepared.
5. Operator-registry and relay regressions pass.

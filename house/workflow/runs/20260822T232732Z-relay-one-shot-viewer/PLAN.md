# Relay one-shot viewer seam — plan v1

## Model advisory

- Next phase: capability-bound relay viewer integration review.
- Recommendation: Sol / high.
- Reason: this crosses a static presentation boundary into an existing
  capability and loopback transport contract.
- Reassess: Terra / high after the contract and adversarial fixtures are
  sealed.
- The advisory was delivered before implementation resumed. No client model
  switch is asserted.

## Workflow classification

- Project: existing; resume from the frozen-renderer handoff.
- Profile: core.
- Case type: `security_boundary_implementation`.
- Single implementation node: prepare an existing one-shot loopback viewer
  from one already-frozen relay dashboard response.

## Objective

Provide an explicit preparation seam that renders a frozen relay response and
constructs the already-qualified `OneShotLoopbackViewer` without starting it.
The caller must still perform an explicit `start()`.

## Non-goals

- No browser launch or iTerm API registration.
- No persistent listener, service, background daemon, or automatic start.
- No adapter call, relay mutation, worker dispatch, provider request, reverse
  channel, terminal input, or authority grant.

## Acceptance

1. Preparation leaves the viewer unbound until explicit start.
2. An exact capability serves the inert document once over an exact loopback
   address.
3. Malformed or pre-bound response claims fail before viewer preparation.
4. `418` integration-pending content remains visible and non-authorizing.
5. Existing capability, request rejection, TTL, and terminal receipt behavior
   remain unchanged under the full House regression suite.

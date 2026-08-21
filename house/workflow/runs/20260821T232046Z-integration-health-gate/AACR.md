# After-action review

## What worked

- The donor sweep showed that the highest-value import was not another terminal
  UI, but iTerm2's narrow, event-triggered check of an integration's actual
  on-disk contract.
- Existing Dream House components already covered several donor patterns:
  append-only event ordering, versioned display batches, one-way transport,
  task-controller fencing, and fail-closed capability validation.
- A standalone read-only contract evaluator makes the missing monitoring
  pattern reusable without granting it authority.

## Deliberate limits

- No real local configuration was inspected, so no live-health claim exists.
- The evaluator does not decide when to prompt, watch continuously, or repair.
- A health report is evidence for a later controller, never permission for it.

## Decision

Accept as an offline monitoring primitive. Revisit only when one concrete
binding supplies a trusted desired-state contract and a separately authorized
repair flow.

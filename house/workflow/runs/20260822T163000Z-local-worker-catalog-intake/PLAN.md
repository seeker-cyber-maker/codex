# Local worker catalog intake

## Objective

Define the downstream Dream House boundary for a sealed export from the
provider-orchestration local-worker lane.

## Scope

Accept only a typed, hash-bound catalog describing approved specialists. Keep
`active` and `qualified` distinct, and return a receipt with an explicit
`NOT_ATTEMPTED` runtime disposition.

## Non-goals

- No provider configuration read, directory scan, socket, model probe, route
  selection, worker launch, or result admission.
- No reliance on the still-uncommitted Daybreak worker registry.
- No promotion of Needle or ordinary installed models into worker status.

## Acceptance

Focused catalog tests, full House regression, compilation, Ruff, formatting,
and a clean diff check must pass. A later adapter may consume this boundary
only from a committed provider export whose source commit and tree match.

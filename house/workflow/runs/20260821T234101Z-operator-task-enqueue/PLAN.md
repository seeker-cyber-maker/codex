# Operator task-enqueue plan

## Objective

Make the existing human command inventory usable for creating a real, typed,
idempotent queued task through the local task inbox. The same gateway will be
the future dashboard adapter and the terminal CLI implementation.

## Admitted delta

1. Convert the declared `codex.house.task.submit` request into the strict
   task-submission schema.
2. Preserve the user-requested recipient/triage lane in the canonical task
   packet and receipt.
3. Add an explicit CLI operation that queues the request in a caller-named
   local inbox and returns a sealed queue receipt.

## Invariants

- A task request has an explicit caller-selected `enqueue_id`; same content
  replays exactly and changed content fails closed.
- The submission remains schema-checked before queueing and preserves an
  asserted-but-unverified requester identity.
- The queued recipient is an advisory assignment request, not a provider,
  worker, or authority grant.
- Queueing does not acquire a controller lease, touch a task-spine database,
  start a worker, call a model/provider, execute a shell command, or open an
  iTerm reverse channel.
- The command registry remains the sole shared declaration for the CLI and
  future dashboard.

## Non-goals

Actual worker claiming/launching, dashboard web serving, identity signing,
YubiKey integration, task-spine admission, provider selection, routing
execution, or iTerm control remain outside this slice.

## Acceptance

- API and CLI submit a valid typed request to the inbox as `QUEUED`.
- Canonical task admission preserves the requested recipient after a leased
  controller later drains the queue.
- Exact retry is inert; a changed request with the same enqueue identity fails
  before a second row is created.
- Invalid request fields fail before queue mutation.
- Focused tests, full House regression, static checks, and a CLI smoke pass.

## Model advisory

Case type: `app_delivery`; current implementation level is sufficient. Escalate
only if this extends to live workers, provider credentials, or authority.

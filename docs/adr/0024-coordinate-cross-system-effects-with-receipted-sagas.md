---
status: accepted
---

# Coordinate cross-system effects with receipted sagas

Operations spanning the Codex Archive, local Git repositories, remote hosts,
provider APIs, or other external services are not atomic. Dream House coordinates
them through a Receipted Saga and never uses Archive transaction language to
claim that independently committed systems changed together.

Each saga starts from a signed manifest that declares stable operation and step
identities, system boundaries, dependency order, preconditions, required
authority, expected effects, idempotency keys, verification predicates,
timeouts, retry policy, Compensating Actions, irreversible boundaries, and
stop or escalation rules. Credentials remain in their owning trust boundary and
are referenced by capability, never embedded in the manifest or Durable Outbox.

Atomic Admission records the authorized saga intent and its first outbox entries
inside the Archive. This proves only that the intent was admitted. A narrow
executor claims one outbox entry, rechecks its authority and preconditions,
performs the idempotent external step, verifies the resulting state, and appends
a receipt before advancing dependencies. Each step retains one of `planned`,
`authorized`, `running`, `succeeded`, `failed`, `unknown`, `compensating`,
`compensated`, or `compensation_failed`; the saga is complete only when every
required effect has a verified success receipt.

An ambiguous timeout or lost response becomes `unknown`, not failed or safe to
retry. The executor first performs read-only reconciliation using the external
idempotency key and expected effect. It retries only when non-execution is
established or the target provides an idempotent operation contract. Blind
retries are forbidden.

When a later step fails, the orchestrator proposes the manifest's authorized
Compensating Actions in reverse dependency order where applicable. Compensation
is a new forward event with its own gates, authority, effect, and receipt; it
does not delete the failed history or guarantee restoration of every external
condition. A failed or unknown compensation remains an incident requiring
attention.

Local commit, remote push, issue creation, deployment, message delivery, and
Archive admission therefore remain independently observable facts. A saga may
coordinate them and present combined progress, but no summary may report
completion from intent, queue acceptance, process exit, or an unverified API
response alone.

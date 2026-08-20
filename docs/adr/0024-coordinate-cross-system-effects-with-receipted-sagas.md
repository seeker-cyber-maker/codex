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

Irreversible Steps are placed after every reversible prerequisite whenever the
dependency graph permits. Immediately before execution, the system presents an
exact effect preview containing the target, scope, content or operation, cost or
resource consequence, external audience, known inability to compensate, and
current preconditions. Just-in-time authorization binds that preview and expires
when its target state, policy, scope, or declared time window changes. The
executor rechecks all bound values immediately before the effect.

When an irreversible effect must occur before other work can proceed, the saga
is split at that boundary. The first saga ends at a human decision gate for the
exact irreversible effect; any continuation is a separately admitted saga that
references the verified result. Planning approval, batch membership, prior
reversible success, or a broad standing capability cannot substitute for the
boundary authorization, and failure after the effect must not be described as
fully compensated when restoration is impossible.

An Irreversible Effect Authorization is a single-use, non-delegable grant. It
binds the saga and step identities, exact effect-preview digest, target and
target-state digest, named executor identity, authorizer, issuance and expiry
times, and one stable attempt identity. A broker may deliver the grant but may
not exercise it, substitute an executor, retarget it, extend it, or derive a
second grant. Any change to a bound value requires a new preview and a new
authorization.

The authorization is atomically marked `consumed` for its attempt immediately
before the executor crosses the irreversible boundary. It cannot authorize a
retry, replay, continuation, or compensating action. Revocation prevents an
unconsumed grant from being exercised; expiry and consumption are permanent
ledger events rather than deletion of the grant.

If the executor loses contact or the result is otherwise ambiguous after
consumption, the step becomes `unknown` and enters read-only reconciliation.
The system does not issue a replacement authorization or repeat the effect
while execution remains possible. A verified success closes the step with its
effect receipt. Proof that the effect did not occur permits a newly previewed
and separately authorized attempt; an outcome that cannot be resolved remains
an incident and blocks dependent irreversible work.

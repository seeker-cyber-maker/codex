# Offline task spine v0

`house.task_spine` is the first headless Dream House authority-path fixture.
Its canonical record is an append-only SQLite journal; its task read model is
derived and disposable. A Task Packet stores the no-dispatch routing receipt
from `house.auto_switcher`. It may also preserve a separately hash-bound manual
route selection; that operator choice never replaces the automatic receipt or
causes a dispatch.

Candidate admission requires all of the following: a sealed task-scoped worker
buffer, complete result envelope, import proposal, explicit lead authorization,
a fresh journal-head basis, and the `trusted_writer` actor. The derived WIP view
contains only the buffer hash, never the report body.

Late buffer records are retained with `late_result` disposition without changing
the sealed WIP hash. Rejected and needs-repair envelopes remain journal evidence
but cannot become import proposals; a linked amendment receives a new envelope
identity. Optional admission leases are proposal-scoped, event-count bounded,
and fail closed after revocation or expiry. Read-model rebuild uses a transactional
shadow table, so an interruption before swap leaves the prior projection intact.

It is intentionally offline and local. It does not start a worker, read or
write native Codex state, contact a provider, or mutate the Archive.

The typed submission adapter accepts only schema-declared fields, binds a
caller idempotency key to canonical requester/title/summary/case-type/recipient
content, derives stable work and task identities, resumes matching partial
creation, and returns the exact stored receipt on retry. Reusing a key with
different content fails closed. `requested_by` is conserved as
`ASSERTED_UNVERIFIED`; signature verification remains a later trust-service
boundary. `requested_recipient` records a triage/coder/reviewer lane or an
explicit `specific_model` identifier; it is a request, never worker authority.

Submission receipts retain the router's advisory model/effort recommendation.
That is operational advice only: Terra is the normal implementation class, Sol
is reserved for consequential planning/review, and Luna/Spark are constrained
to routine bounded leaves. No receipt switches a client model or starts a
worker.

The local inbox/controller is a separate SQLite queue in front of that
adapter. Producers can enqueue raw JSON, while one finite leased controller
calls the task spine. Its wall-clock lease carries a monotonic epoch and opaque
fencing token; stale tokens cannot claim or finish inbox records. Each
`drain-once` processes at most one record. If the process is interrupted after
task acceptance but before the inbox commit, a later controller replays the
stored task receipt and records the terminal inbox state without duplicating
task history. This is cooperative process control, not OS-enforced isolation.

The optional local-authority candidate adds a directly enrolled P-256 public-key
trust registry and an `AuthorizedTaskInbox` producer surface. Short-lived
proofs bind principal, key, action, enqueue identity, canonical submission
digest, nonce, and validity window. Accepted/rejected proof fingerprints,
permissions, and revocations are retained in a separate append-only journal;
private keys are never persisted by this module. Install its isolated runtime
dependency from `requirements-authority.txt`.

This is not a certificate authority or a finished YubiKey integration. The
first-key bootstrap remains an external setup ceremony, direct access to the
underlying SQLite files is not OS-blocked, and independent security review is
required before real-key or production use.

```bash
PYTHONPATH=/absolute/path/to/codex-dream-house \
  python3 -m house.task_spine --db /tmp/task-spine.sqlite demo
PYTHONPATH=/absolute/path/to/codex-dream-house \
  python3 -m house.task_spine --db /tmp/task-spine.sqlite rebuild
PYTHONPATH=/absolute/path/to/codex-dream-house \
  python3 -m house.task_spine --db /tmp/task-spine.sqlite status
```

`status` emits compact read-only Task Cards straight from the canonical journal.
They show the stored model/effort advisory, automatic route, optional manual
choice, WIP and candidate metadata, but do not rebuild state, switch a model,
or dispatch work. They are the CLI-facing backend for a later human dashboard.

Typed submission uses a JSON file with schema
`codex-house-task-submission/1`:

```bash
PYTHONPATH=/absolute/path/to/codex-dream-house \
  python3 -m house.task_spine --db /tmp/task-spine.sqlite submit --input task.json
```

Finite controller usage keeps the inbox and task journal separate:

```bash
PYTHONPATH=/absolute/path/to/codex-dream-house \
  python3 -m house.task_spine.controller_cli --inbox-db /tmp/inbox.sqlite \
  enqueue --enqueue-id request-1 --input task.json
PYTHONPATH=/absolute/path/to/codex-dream-house \
  python3 -m house.task_spine.controller_cli --inbox-db /tmp/inbox.sqlite \
  lease --holder local-controller --ttl 30
PYTHONPATH=/absolute/path/to/codex-dream-house \
  python3 -m house.task_spine.controller_cli --inbox-db /tmp/inbox.sqlite \
  drain-once --spine-db /tmp/task-spine.sqlite \
  --holder local-controller --token TOKEN_FROM_LEASE_RECEIPT
```

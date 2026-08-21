# Offline task spine v0

`house.task_spine` is the first headless Dream House authority-path fixture.
Its canonical record is an append-only SQLite journal; its task read model is
derived and disposable. A Task Packet stores the no-dispatch routing receipt
from `house.auto_switcher`.

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
caller idempotency key to canonical requester/title/summary/case-type content,
derives stable work and task identities, resumes matching partial creation, and
returns the exact stored receipt on retry. Reusing a key with different content
fails closed. `requested_by` is conserved as `ASSERTED_UNVERIFIED`; signature
verification remains a later trust-service boundary.

```bash
PYTHONPATH=/absolute/path/to/codex-dream-house \
  python3 -m house.task_spine --db /tmp/task-spine.sqlite demo
PYTHONPATH=/absolute/path/to/codex-dream-house \
  python3 -m house.task_spine --db /tmp/task-spine.sqlite rebuild
```

Typed submission uses a JSON file with schema
`codex-house-task-submission/1`:

```bash
PYTHONPATH=/absolute/path/to/codex-dream-house \
  python3 -m house.task_spine --db /tmp/task-spine.sqlite submit --input task.json
```

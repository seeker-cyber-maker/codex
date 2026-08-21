# Operator task-enqueue handoff

The operator surface now has one shared `enqueue_task()` gateway and a
keyboard-only `enqueue-task` command. It validates the declared Create Task
parameters, converts them into `codex-house-task-submission/1`, and writes an
idempotent `QUEUED` entry to an explicitly named local `TaskInbox`.

The requested recipient is canonical task metadata: `triage`, `coder`,
`reviewer`, or `specific_model` plus a required model identifier. It is bound
to idempotency, retained in the later Task Packet and read-only task card, and
is neither a worker lease nor a provider/model launch.

The operation returns `controller: NOT_ATTEMPTED` and
`dispatch: NOT_ATTEMPTED`. The existing leased controller remains the only
component that can admit one queued entry into a separate task-spine database.
Actual worker claiming, dashboard HTTP/UI binding, authenticated requester
identity, and iTerm reverse control remain intentionally unimplemented.

Validation is recorded in `VALIDATION.json`; the initial source hashes are in
`SOURCE_SEAL.json` and must be refreshed after any source change.

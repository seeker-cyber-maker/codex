# Source-implementation plan: synthetic recovery ledger

## Objective

Implement and test the accepted synthetic recovery-ledger contract as one
private, production-unreachable Python module backed only by a disposable
temporary SQLite fixture.

This run may change only:

- `house/task_spine/recovery_ledger.py`
- `house/task_spine/tests/test_recovery_ledger.py`

It must not change or export the sealed pure reducer, existing authority,
inbox, task spine, worker controller, CLI, provider, package, or `.house-state`
surfaces.

## Authoritative baseline

- Repository base commit:
  `135b5fba47d338f59ca489b2f889853101c03ad4`.
- Accepted ledger plan SHA-256:
  `d54dbb5a4d4b006e1752956f456a994ea0a4a355050503a585d82385b52d1fe1`.
- Pure reducer SHA-256:
  `274668d6cdf19cdeeaff1b40ca539ddf91c78e441af1db6923c8147ec74f7042`.
- Pure reducer tests SHA-256:
  `37e08de7c2ed774bdabcb9e25fcbf7704502ad844511bf0d723bfa68da2ae9aa`.
- Baseline verification: 5 focused recovery-policy tests and 13 unchanged
  authority/crypto tests pass.

## Necessary API delta

The accepted plan names `initialize(...)` and `apply(...)`, while also
requiring close/reopen verification in a fresh adapter instance. Reopening an
existing fixture cannot be performed by an initializer that must reject an
existing file. This plan therefore adds one narrow operation:

- `RecoveryLedger.initialize(fixture_root, filename, initial_state)` creates a
  new fixture and returns an open adapter.
- `RecoveryLedger.reopen(fixture_root, filename)` opens an existing fixture,
  verifies it completely, and returns a fresh adapter.
- `ledger.apply(request, evidence, decision_time)` applies one candidate
  payload against stored state.

`close()` releases the SQLite connection and grants no further operation. The
API delta is blocking and must be accepted by the plan council before code.

## Closed implementation boundary

The module may import only the Python standard-library facilities required for
canonical JSON/SHA-256, bounded path identity checks, and SQLite, plus
`house.task_spine.recovery_policy`. It must not use `__future__`, environment
variables, clocks, randomness, subprocesses, sockets/networking, serialization
that executes objects, cryptography/key APIs, hardware, Keychain, dynamic
imports, `eval`, `exec`, or `compile`.

The module remains unimported and unexported by all production code. Its
dedicated test may import it directly. The only database paths accepted are
direct absent/existing children of a canonical, non-symlink directory beneath
the platform temporary root whose basename begins
`recovery-ledger-fixture-`. The filename is an identifier ending in `.sqlite`
with no path separators. Root and database device/inode identities are pinned
and rechecked before and after every transaction. This is a fixture guard, not
an OS containment or hostile-host security claim.

## Bounded storage schema

Set an application ID and `user_version=1`. Reject any different version,
application ID, required-table shape, or additional user table. Store no key,
credential, package, task, worker, provider, network, or hardware field.

Use exactly three private tables:

1. `recovery_ledger_meta`: singleton, schema, canonical initial-state JSON,
   initial-state digest, genesis digest, current-state digest, current event
   head, entry count. The genesis digest hashes a closed object containing the
   ledger schema and exact initial-state digest; it is the event head when the
   entry count is zero and the previous-event digest of sequence one.
2. `recovery_ledger_state`: singleton, canonical current synthetic state JSON.
3. `recovery_ledger_entry`: sequence, submission/manifest/challenge identities,
   canonical request/evidence JSON, injected decision time, prior/next state
   digests, complete outer ledger receipt JSON, previous event digest, event
   digest.

Limits: at most 64 accepted entries; at most 256 KiB for each canonical request
or evidence; at most 1 MiB for state or receipt JSON. Oversize input fails
before `BEGIN IMMEDIATE` and performs no write.

## Canonical identities and receipts

- `submission_sha256` hashes canonical `{request,evidence,decision_time}`.
- `manifest_sha256` is `recovery_policy.sha256_json(request)`.
- A challenge identity is present only for a closed, valid transition manifest;
  protective lockdown has no challenge identity.
- Event digests hash one closed event object containing sequence, all input and
  state/receipt digests, and the previous event digest.

Every return is a closed
`codex-house-synthetic-recovery-ledger-receipt/1` envelope with exactly the
fields and fixed literals in the accepted plan. `reducer_receipt_sha256` hashes
the complete nested reducer receipt, while the nested reducer's own
`receipt_sha256` retains its distinct original meaning.

Outcome mapping is exact:

| Condition | `outcome_source` | Result/code | Reducer evidence |
| --- | --- | --- | --- |
| Fresh accepted reducer transition, committed and re-read | `STORED_ACCEPTED` | `ACCEPTED/OK` | complete nested accepted receipt + full-object digest |
| Exact accepted submission duplicate | return exact stored envelope | unchanged | unchanged |
| Same consumed challenge, different manifest | `ADAPTER_CONFLICT` | `REFUSED/CHALLENGE_CONFLICT` | null |
| Same accepted manifest, different evidence/time | `ADAPTER_CONFLICT` | `REFUSED/SUBMISSION_CONFLICT` | null |
| Fresh reducer refusal or replay | `REDUCER` | mirror nested result/code | complete nested receipt + full-object digest |

Adapter conflicts and reducer refusal/replay do not append, update meta/state,
consume challenges, or cache a receipt. Only accepted transitions are written.

## Transaction, integrity, and replay

Initialization validates and deep-copies the synthetic state, canonicalizes it
once, starts one `BEGIN IMMEDIATE`, creates the exact schema, stores that exact
canonical initial-state JSON plus its digest and genesis digest, stores a
separate canonical current-state copy, and commits once. Any exception rolls
back and closes the incomplete adapter.

`apply` performs this finite sequence:

1. Enforce input-size/path-identity guards.
2. `BEGIN IMMEDIATE`; validate exact schema, metadata, current state, every
   outer receipt/event digest, sequence, and hash-chain link.
3. Apply the duplicate/conflict table. These paths make no reducer call.
4. For a fresh payload, call the pure reducer exactly once for the candidate.
5. Wrap every reducer outcome in the fixed outer ledger envelope.
6. For acceptance only, verify the next-state digest, enforce the entry cap,
   append one event, replace current state, update meta/head/count, invoke one
   private injected pre-commit fault hook if configured, and commit once.
7. Re-read the committed envelope, recheck path identity, and return it.
8. On any exception, roll back, recheck path identity, and re-raise a typed
   `RecoveryLedgerError` without repair.

The private pre-commit fault hook exists only to exercise rollback in the
dedicated test; it is not exported or model-facing and cannot change receipt
semantics.

`reopen` parses and validates the stored canonical initial-state JSON, verifies
its exact re-encoding, digest, genesis digest, zero-entry/current-head rule, and
current-state record. It then performs full structural verification and
semantically replays at most 64 accepted entries from that stored initial state
through the pure reducer. Each replay must reproduce the stored next state and
complete nested reducer receipt. It then verifies the final replayed state
equals the stored current state. Reopen never writes or repairs.

Historic replay calls during `reopen` are integrity verification. The
"exactly once" candidate-call rule applies to a fresh `apply`, not to this
bounded reopen verifier.

SQLite commit/reopen behavior is only a local test observation. No result may
claim fsync durability, crash survival, adversarial rollback protection,
independent checkpoint protection, multi-process fencing, or real recovery.

## Task graph

1. `S1 source`: add the private bounded ledger module. Owner: primary
   implementation lane. Writes only `recovery_ledger.py`.
2. `T1 focused tests`: add whole-object, replay, corruption, rollback, size,
   path, and source-isolation tests. Depends on S1. Writes only the dedicated
   test.
3. `V1 deterministic verification`: run compilation, dedicated tests, sealed
   reducer tests, legacy authority/crypto tests, source-graph checks, and
   `git diff --check`. No writes except disposable test fixtures.
4. `C1 promotion council`: blind read-only review of sealed source, tests, and
   receipts. Depends on V1. Cannot modify or authorize wider work.
5. `A1 seal/AACR`: record exact hashes, claim ceiling, limitations, and handoff;
   commit and push only this run and scoped source files if all gates pass.

There is one implementation lane. No worker delegation, provider lane, or
parallel write scope is needed.

## Required deterministic tests

1. Initialize, apply the complete six-transition synthetic ceremony, close,
   reopen, and deep-compare state, entries, envelopes, and replay outputs.
2. Exact accepted duplicate returns the byte-equivalent stored envelope with
   no reducer candidate call and no additional row.
3. Challenge and submission conflicts return whole expected adapter envelopes,
   make no reducer call, and leave an exact canonical logical snapshot of all
   ledger tables unchanged.
4. Fresh reducer refusal and reducer replay return whole expected outer
   envelopes with exact nested receipt/digest; they are uncached and make no
   database change.
5. A private fault hook immediately before commit proves rollback of event,
   state, metadata, head, count, and challenge view; bounded retry succeeds.
6. Reopen refuses independent corruptions of canonical initial-state JSON,
   initial-state digest, genesis digest, meta, current state, sequence, event
   link, event digest, outer receipt, nested receipt digest, and final replay
   state, without repair.
7. Unsafe root/name, symlink, path-identity change, existing-on-initialize,
   absent-on-reopen, oversize payload, and entry-cap cases fail closed.
8. AST/source-graph checks prove the module has only the allowed imports/calls
   and is unreachable from production modules/exports.
9. Existing recovery-policy and authority/crypto regression suites pass
   unchanged.

## Acceptance and claim ceiling

All required tests must pass with zero unexpected warnings. The final source
diff must contain only the two scoped files plus this run's workflow artifacts,
with at most 800 added/changed source-and-test lines combined.
The implementation council must accept the exact sealed candidate or the run
stops at `NEEDS_REVIEW`.

The maximum final claim is:

`SYNTHETIC_RECOVERY_LEDGER_LOCAL_TRANSACTION_ONLY`.

It establishes only the tested synthetic schema, local transaction, bounded
reopen/replay, and receipt-envelope behavior. Authority remains `NOT_GRANTED`;
dispatch/runtime actions remain `NOT_ATTEMPTED`; hardware/key material remain
`NOT_ACCESSED`; checkpoint protection and recovery readiness remain
`NOT_ESTABLISHED`.

## Stop boundaries

Stop before any change outside the two source files; any existing or real
database path; real key, signature, package, YubiKey, Keychain, trusted time,
checkpoint/backup, controller, inbox, CLI/API/UI, provider, worker, network,
dispatch, readiness, or operational recovery work. Any need to weaken a fixed
receipt literal, skip replay, auto-repair corruption, or import an operational
surface requires a versioned plan delta and fresh council review.

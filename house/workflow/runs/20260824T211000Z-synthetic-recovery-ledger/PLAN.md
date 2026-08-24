# Plan: synthetic recovery-ledger persistence slice

## Objective

Add a separate, test-only local persistence adapter around the already sealed
pure recovery-policy reducer.  The adapter's sole future claim is that a
single SQLite transaction can atomically record a *synthetic* transition,
its resulting synthetic state, and its synthetic receipt in one disposable
test database.

This is a persistence-semantics experiment, not recovery implementation.  It
must not make a key, package, YubiKey, Keychain, controller, inbox, provider,
CLI, worker, or task reachable.

## Authoritative inputs

- V6 recovery policy: `../20260824T203000Z-r1-observer-trust-plan/PLAN_V6_SINGLE_YUBIKEY_RECOVERY.md`
- Sealed pure reducer: `house/task_spine/recovery_policy.py`
- Source-only handoff: `../20260824T201734Z-single-yubikey-recovery-source/HANDOFF.md`
- Existing controller/inbox code is negative boundary evidence only.  This
  slice must not import, share a database with, or call either surface.

## Proposed source boundary

If this plan is accepted, implementation may add only:

- `house/task_spine/recovery_ledger.py`
- `house/task_spine/tests/test_recovery_ledger.py`

The adapter has two closed entry points:

- `initialize(fixture_root, filename, initial_state)`: creates exactly one
  empty synthetic ledger from one fully validated synthetic state.  It refuses
  an existing file, a nonempty ledger, an invalid state, a filename with any
  path component, or a root outside a test-owned `TemporaryDirectory` fixture.
- `apply(request, evidence, decision_time)`: has no state argument.  It loads
  the stored state and applies one caller payload with an injected integer
  decision time.

The fixture root is canonicalized before creation, must exist as a directory,
must not be a symlink, must be beneath the platform temporary-directory root,
and must have a `recovery-ledger-fixture-` basename made by the test fixture.
The filename must name a direct, previously absent child.  Creation/reopen
must reject any symlink or path-identity change.  No default, configured,
production, repository, or user-state database path is allowed; tests must
create the root with `TemporaryDirectory`.  This naming/location check is a
test-fixture guard, not an OS security boundary or authorization mechanism.

The adapter must reject every path that resolves to an existing authority,
inbox, controller, task-spine, provider, or `.house-state` database.  It calls
`recovery_policy.verify_transition` exactly once only for a fresh submission
that survives the closed duplicate/conflict precheck below.

## Closed database contract

The new database has no credentials, key material, encrypted content, package
bytes, hardware identifiers, worker IDs, task records, or network fields.  It
contains only canonical JSON and SHA-256 digests of synthetic inputs/outputs.

Minimum tables are private to the adapter:

- `recovery_ledger_meta`: exactly one format version, initial semantic-state
  digest, current synthetic semantic-state digest, and current event head.
- `recovery_ledger_entry`: monotonically increasing sequence, canonical
  request/evidence JSON, injected decision time, prior/next semantic-state
  digests, complete verifier receipt JSON, and an event digest chained to the
  prior entry.
- `recovery_ledger_state`: exactly one canonical synthetic `RecoveryState`.

No table is a trust registry, checkpoint protector, challenge service,
revocation service, or production journal.  SQLite transaction durability is
observed local behavior only; it is not an independently protected checkpoint
or crash/fault-tolerance proof.

## Transaction and idempotency rules

The submission identity is the SHA-256 of canonical `request`, `evidence`, and
`decision_time`.  A manifest identity is the request SHA-256.  For a valid
transition manifest, its challenge identity is the validated `challenge_id`.
The entry table persists all three identities for accepted transitions only.

For `apply(request, evidence, decision_time)`:

1. Start `BEGIN IMMEDIATE`; load and validate the one stored synthetic state,
   metadata, and full hash chain.  Any invalid row or mismatch fails closed
   without mutation.
2. Canonicalize the exact caller payload and derive the submission and manifest
   digests.  Then apply this closed outcome table before invoking the reducer:

   | Condition | Result | Reducer call | Database write |
   | --- | --- | --- | --- |
   | Same submission identity as one accepted entry | return exact stored accepted receipt | no | no |
   | Same consumed challenge, different manifest identity | adapter-built `REFUSED/CHALLENGE_CONFLICT` receipt | no | no |
   | Same manifest identity but different submission identity | adapter-built `REFUSED/SUBMISSION_CONFLICT` receipt | no | no |
   | Otherwise | invoke the pure reducer exactly once | yes | see next row |

   The adapter's built refusals have the exact ledger receipt schema and fixed
   claim literals; neither caller text nor stored content can choose a claim
   field.  They do not purport to be reducer receipts.
3. For a fresh reducer invocation, `REFUSED` and `REPLAY` return the reducer's
   deterministic receipt without appending an entry, changing state/metadata/
   hash chain, or consuming a challenge.  They are never cached.  Therefore an
   identical invalid fresh request invokes the reducer again against the same
   stored state.  Only `ACCEPTED` transitions append ledger entries.
4. For `ACCEPTED`, verify the reducer's next-state semantic digest, append one
   hash-chained entry, replace the one stored state, and update metadata in the
   same transaction.  Commit once.  A test seam may force an exception before
   commit; reopening must observe the old state and no new entry.
5. Reopen in a fresh adapter instance; validate every event digest, derived
   final state, and stored receipt digest.  Replaying the exact payload returns
   the original stored receipt; a same-challenge different-manifest attempt is
   refused.

The adapter has no lease, wall clock, retry, background recovery, automatic
resume, cross-process protocol, or concurrent controller claim.  `BEGIN
IMMEDIATE` serializes one local connection's test transaction; it does not
grant a controller fence or survive adversarial rollback.

## Claim ceiling

Every adapter return uses exactly one closed
`codex-house-synthetic-recovery-ledger-receipt/1` envelope.  Its exact outer
fields are `schema`, `claim_ceiling`, `authority`, `dispatch`, `hardware`,
`key_material`, `runtime_admission`, `checkpoint_protection`,
`recovery_readiness`, `outcome_source`, `result`, `code`,
`submission_sha256`, `manifest_sha256`, `prior_state_sha256`,
`next_state_sha256`, `original_receipt_sha256`, `reducer_receipt`,
`reducer_receipt_sha256`, and `receipt_sha256`.  The final field hashes every
other outer field canonically.

`outcome_source` is closed to `STORED_ACCEPTED`, `ADAPTER_CONFLICT`, or
`REDUCER`.  For a newly invoked pure reducer, its complete receipt and digest
are preserved only in `reducer_receipt` and `reducer_receipt_sha256`.  The
outer result/code may mirror that evidence, but the pure receipt is never the
adapter's top-level receipt.  Stored accepted replays return the exact stored
ledger envelope.  Adapter conflicts set both reducer fields to null.  This
preserves evidence without allowing a pure reducer's older claim ceiling to
escape through the adapter API.

Every ledger envelope must carry:

`SYNTHETIC_RECOVERY_LEDGER_LOCAL_TRANSACTION_ONLY`.

It must also carry fixed literals:

- `authority=NOT_GRANTED`
- `dispatch=NOT_ATTEMPTED`
- `hardware=NOT_ACCESSED`
- `key_material=NOT_ACCESSED`
- `runtime_admission=NOT_ATTEMPTED`
- `checkpoint_protection=NOT_ESTABLISHED`
- `recovery_readiness=NOT_ESTABLISHED`

No caller field may determine those literals.  Ledger envelopes do not upgrade
the pure reducer's ceiling or claim a verified signature, actual possession,
trusted time, atomic recovery ceremony, protected checkpoint, crash survival,
or revocation.

## Required tests

1. A complete synthetic transition sequence persists and reopens with whole
   state, receipt, and hash-chain equality.
2. Exact repeated accepted input returns the stored receipt with no extra entry and
   proves the reducer was not invoked again.
3. Same challenge with different manifest bytes and same manifest with different
   evidence/time each produce their distinct adapter refusal, with no reducer
   call, no extra entry, and unchanged state.
4. A forced exception before commit leaves the entire database at the prior
   state, chain head, and challenge-consumption view.
5. A corrupt state, entry receipt, event digest, sequence, or metadata digest
   prevents read/apply and performs no repair or mutation.
6. A reducer refusal/replay cannot advance state, change the metadata/chain, or
   consume a new synthetic challenge; repeated invalid payloads are not cached.
   Both are returned only inside a fixed outer ledger envelope whose nested
   reducer receipt/digest round-trips exactly.
7. AST/source-graph isolation proves no import/re-export/reference to
   authority, authority_crypto, inbox, worker_exec, controller, CLI, provider,
   subprocess, socket, environment, cryptography/key APIs, hardware, or
   non-test database paths.
8. Existing pure recovery-policy and legacy authority/crypto tests still pass.

## Stop boundaries

Stop and require a new plan before: real persistence location, external
checkpoint/backup, real time, signing or signature verification, recovery
package creation/inspection, Keychain/YubiKey access, key enrollment/revocation,
controller/inbox binding, CLI/API/UI exposure, worker/provider use, network,
or any claim that a loss-of-key ceremony is recoverable.

## Acceptance

This plan is acceptable only if a review confirms that the fresh SQLite file
is a disposable synthetic fixture, receipt literals cannot be caller-widened,
failure/replay paths cannot mutate state, and no existing operational surface
can import or invoke the adapter.  Implementation remains separately gated.

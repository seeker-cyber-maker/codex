# Source-only plan: single-YubiKey recovery policy verifier

Status: `PLAN_CANDIDATE_COUNCIL_REQUIRED`

Case type: `security_containment`

Model advisory: Terra/high for implementation; reassess at promotion review or
after two failed remediation attempts.

## Objective

Implement the smallest pure, synthetic-only source slice that makes the
accepted V6 recovery policy mechanically reviewable. The slice validates exact
schemas and deterministic transition ordering without touching real keys,
hardware, storage media, services, or the existing operational authority gate.

## Claim ceiling

`SYNTHETIC_RECOVERY_POLICY_STRUCTURE_AND_TRANSITIONS_ONLY`.

Every receipt must also state:

- `authority=NOT_GRANTED`;
- `dispatch=NOT_ATTEMPTED`;
- `hardware=NOT_ACCESSED`;
- `key_material=NOT_ACCESSED`;
- `runtime_admission=NOT_ATTEMPTED`.

Passing tests do not establish key custody, encryption/tool qualification,
checkpoint independence, trusted time, durable crash atomicity, production
database safety, or recovery readiness.

## Source boundary

Add a new private module:

- `house/task_spine/recovery_policy.py`
- `house/task_spine/tests/test_recovery_policy.py`

Do not modify `authority.py`, `authority_crypto.py`, task inboxes, controllers,
CLI surfaces, provider routes, or exports. In particular, do not add recovery
actions to the old `KNOWN_ACTIONS`: its direct-bootstrap model has no roles,
generations, or V6 authority ceiling.

## Closed input contracts

The pure verifier consumes only caller-supplied JSON-compatible values:

1. `RecoveryState` with exact schema, registry/generation, mode, fencing epoch,
   current journal/checkpoint digests, primary and recovery identities/epochs,
   replacement status, quarantined-intent digest, and consumed challenge map.
2. `TransitionManifest` with the exact V6 fields, one action only, one domain
   separator, one service challenge, one ceremony-parent digest, exact prior
   state, signer identity/epoch, optional exact replacement identity/epoch,
   digest bindings, issue/expiry, and `REMAIN_LOCKED` default.
3. `VerificationEvidence` carrying explicit booleans/digests for signature and
   replacement-possession verification. The module never signs, loads a key,
   reads a clock, or decides whether the evidence source is trustworthy.
4. Explicit integer `decision_time`; it is evaluation input, not a trusted-time
   claim.

Unknown/missing fields, booleans accepted as integers, unbounded strings,
invalid identifiers/digests/times, and unsupported actions fail closed.

## Deterministic transition reducer

Support only:

1. `authority.lockdown.enter`: from `ACTIVE`, authorized solely by the frozen
   protective-rule digest; produces `LOCKDOWN` and grants no authority.
2. `authority.key.suspend-primary`: from `LOCKDOWN`, recovery signature verified,
   exact old-primary identity/epoch, yields `PRIMARY_SUSPENDED` and binds the
   quarantine digest.
3. `authority.key.recover-primary`: from `PRIMARY_SUSPENDED`, recovery signature
   plus exact replacement possession verified, yields `REPLACEMENT_ENROLLED`.
4. `authority.checkpoint.admin.sign`: from `REPLACEMENT_ENROLLED`, recovery
   signature verified and exact checkpoint digest changed, yields
   `REPLACEMENT_READY`.
5. `authority.key.revoke-primary`: only from `REPLACEMENT_READY`, recovery
   signature verified, yields `OLD_PRIMARY_REVOKED` with tombstone digest.
6. `authority.lockdown.exit`: only from `OLD_PRIMARY_REVOKED`, signed by the new
   primary with readiness/checkpoint evidence, yields `ACTIVE` at the new epoch.

The first action is a rule transition, not a recovery-key signature. Every
other action must have exactly one challenge and signer appropriate to that
action. No task, secret, delegation, policy-change, recovery-self-target,
generation-retirement, or multi-action manifest is recognized.

## Replay model

The pure state carries consumed challenge IDs and receipts. Applying an exact
committed manifest again returns the original receipt with
`state=ALREADY_CONSUMED` and does not mutate state. Reusing a challenge with
different bytes fails `CHALLENGE_CONFLICT`. Stale journal/checkpoint/policy/source
digests, fencing/key epochs, ceremony parent, signer, replacement identity, or
prior state fail closed.

This models deterministic semantics only. It does not claim a SQLite commit,
protected checkpoint, or crash boundary exists. Those remain a later stateful
integration gate.

## Acceptance tests

- one complete synthetic V6 ceremony reaches `ACTIVE` at the replacement epoch;
- each intermediate state and receipt matches an entire expected object;
- prohibited/unknown actions and fields fail closed;
- wrong signer role, old/recovery self-target, missing replacement possession,
  and early revoke/exit fail closed;
- exact replay is idempotent; conflicting challenge reuse fails;
- stale binding families fail independently;
- boundary values reject booleans-as-integers, invalid times, oversized values,
  and malformed digests/IDs;
- source scan confirms no filesystem, SQLite, subprocess, network, environment,
  key-generation, serialization-key-load, or clock imports/calls in the module.

Run only:

```bash
python3 -m unittest house.task_spine.tests.test_recovery_policy
python3 -m unittest house.task_spine.tests.test_authority house.task_spine.tests.test_authority_crypto
```

No complete Codex/Rust suite is needed because this slice is isolated Python and
does not change `codex-rs`.

## Stop conditions

Stop before any real key/package generation, encryption, YubiKey/Keychain
access, database integration, checkpoint persistence, CLI/controller wiring,
network/provider use, task dispatch, or recovery-ready claim. Any need to alter
the accepted authority ceiling requires a new plan delta and council review.

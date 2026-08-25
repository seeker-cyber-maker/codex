# Plan V2: synthetic recovery-checkpoint binding verifier

Status: `PROPOSED_V2__PLAN_ONLY__STOP_BEFORE_SOURCE`.

This document supersedes `PLAN.md` for the plan decision. The frozen original
and `COUNCIL_ROUND1.md` remain evidence of the bounded revision.

## Objective and claim ceiling

Plan one future private, pure verifier that proves only structural signature
and exact binding between:

1. a proposed recovery checkpoint assertion;
2. a caller-supplied expected checkpoint descriptor; and
3. a caller-supplied summary of the sealed synthetic recovery ledger.

Its maximum success claim is:

`SYNTHETIC_SIGNED_RECOVERY_CHECKPOINT_AND_EXPECTED_DIGEST_BINDINGS_ONLY`

Every receipt must state:

- `authority=NOT_GRANTED`;
- `dispatch=NOT_ATTEMPTED`;
- `hardware=NOT_ACCESSED`;
- `key_material=NOT_ACCESSED`;
- `runtime_admission=NOT_ATTEMPTED`;
- `checkpoint_protection=NOT_ESTABLISHED`;
- `checkpoint_latest=NOT_ESTABLISHED`;
- `recovery_readiness=NOT_ESTABLISHED`.

The verifier does not decide that an anchor is trusted, a checkpoint is latest
or independently protected, or a restored database is safe. Those are future
external policy/storage facts.

## Non-goals and forbidden work

This run is plan-only. It authorizes no source edit. A later implementation
operation, if separately authorized, may change only:

- `house/task_spine/recovery_checkpoint.py`;
- `house/task_spine/tests/test_recovery_checkpoint.py`.

It must not modify or import into production exports, the sealed reducer or
ledger, existing authority code/tests, inbox, controller, worker execution,
CLI, provider, `.house-state`, README, or zookeeper work.

Forbidden now and in that source-only slice: opening any SQLite database;
reading a clock; generating/loading private keys; YubiKey, Keychain, certificate
or signing operations; checkpoint storage; process launch; network; provider;
worker; dispatch; real recovery data; or a protected/latest/recovery-ready claim.

## Exact future inputs

The pure verifier receives three closed canonical objects and no ambient input.
Every integer below rejects booleans. Every SHA-256 field is exactly 64 lowercase
hexadecimal characters. Every identifier has a fixed implementation bound of
1..128 UTF-8 bytes unless a narrower donor bound is cited in the future source.

### 1. Signed checkpoint envelope

Exact top-level fields:

- `schema = codex-house-synthetic-recovery-checkpoint-envelope/1`;
- `unsigned_checkpoint`;
- `public_spki_der_b64u`;
- `signature_der_b64u`.

Exact unsigned checkpoint fields:

- `schema = codex-house-synthetic-recovery-checkpoint/1`;
- `algorithm = ecdsa-p256-sha256-jcs-low-s/1`;
- `context = codex-house/recovery-checkpoint/v1`;
- `registry_id`, `generation`, `policy_sha256`;
- `recovery_principal_id`, `recovery_key_id`, `recovery_key_epoch`;
- `checkpoint_id`, `checkpoint_sequence` in `1..2^63-1`;
- nullable `predecessor_checkpoint_sha256`;
- `ledger_schema`, `initial_state_sha256`, `genesis_sha256`;
- `current_state_sha256`, `event_head_sha256`, `entry_count` in `0..64`;
- `consumed_challenges_sha256`;
- `ceremony_id`, `ceremony_parent_sha256`, `fencing_epoch`;
- `checkpoint_binding_sha256`.

`checkpoint_binding_sha256` is SHA-256 over the canonical JSON bytes of the
complete unsigned-checkpoint object with only `checkpoint_binding_sha256`
removed. There is deliberately no issue/expiry time: a durable checkpoint does
not use an unauthenticated local clock. P-256 SPKI, key identity, strict DER,
low-S, canonical base64url, and signature verification reuse only the sealed
Stage-0 verification primitives. The published Stage-0 test signer is never
imported by source.

### 2. Expected checkpoint descriptor

Exact fields:

- `schema = codex-house-expected-recovery-checkpoint/1`;
- `source_class = CALLER_SUPPLIED_NOT_VERIFIED`;
- `registry_id`, `generation`, `policy_sha256`;
- `recovery_principal_id`, `recovery_key_id`, `recovery_key_epoch`;
- `checkpoint_id`, `checkpoint_sequence`,
  `predecessor_checkpoint_sha256`;
- `ledger_schema`, `initial_state_sha256`, `genesis_sha256`;
- `current_state_sha256`, `event_head_sha256`, `entry_count`,
  `consumed_challenges_sha256`;
- `ceremony_id`, `ceremony_parent_sha256`, `fencing_epoch`;
- `checkpoint_binding_sha256`;
- `assertion_sha256`;
- `descriptor_sha256`.

`assertion_sha256` is SHA-256 over canonical JSON bytes of the complete signed
checkpoint envelope, including its SPKI and signature. `descriptor_sha256` is
SHA-256 over canonical JSON bytes of the complete descriptor with only
`descriptor_sha256` removed.

This descriptor is an explicit caller-supplied trust input. It cannot
authenticate itself, and its presence does not prove protection or freshness.
The success receipt must bind its digest and repeat that limitation.

### 3. Ledger summary

Exact fields:

- `schema = codex-house-synthetic-recovery-ledger-summary/1`;
- `source_class = CALLER_SUPPLIED_SYNTHETIC_LEDGER_SUMMARY`;
- `ledger_schema`, `initial_state_sha256`, `genesis_sha256`;
- `current_state_sha256`, `event_head_sha256`, `entry_count` in `0..64`;
- `consumed_challenges_sha256`;
- `registry_id`, `generation`, `policy_sha256`;
- `ceremony_id`, `ceremony_parent_sha256`, `fencing_epoch`;
- `summary_sha256`.

`summary_sha256` is SHA-256 over canonical JSON bytes of the complete summary
with only `summary_sha256` removed. The future source does not open the ledger.
Producing a summary from an opened fixture is outside this slice.

## Exact binding matrix

The verifier rejects any mismatch in these comparisons:

| Binding | Signed checkpoint | Expected descriptor | Ledger summary |
|---|---:|---:|---:|
| Registry/generation/policy | required | required | required |
| Ledger schema/initial/genesis/current/head/count/consumed | required | required | required |
| Ceremony ID/parent/fencing epoch | required | required | required |
| Recovery principal/key ID/key epoch | required | required | not present |
| Checkpoint ID/sequence/predecessor/binding digest | required | required | not present |
| Complete signed-envelope digest | computed from complete envelope | `assertion_sha256` | not present |
| Descriptor self-digest | not present | recomputed | not present |
| Summary self-digest | not present | not present | recomputed |

The supplied SPKI-derived key ID must equal the recovery key ID in both the
signed checkpoint and expected descriptor. The ledger summary intentionally
does not assert recovery signer identity or checkpoint identity; it describes
only the sealed synthetic ledger state and ceremony lineage.

## Evaluation order

The future verifier must perform this fixed order:

1. Reject non-dicts, unknown/missing fields, noncanonical values, booleans in
   integer positions, oversized identifiers, malformed hashes/base64url, zero
   epochs, checkpoint sequences outside `1..2^63-1`, entry counts outside
   `0..64`, and invalid predecessor nullability (`sequence=1` requires null;
   later requires SHA-256).
2. Recompute and compare the descriptor and ledger-summary self-digests.
3. Recompute the checkpoint binding, canonical signed bytes, and complete
   signed-envelope `assertion_sha256`.
4. Load only the supplied P-256 public SPKI, derive its key ID, enforce exact
   recovery key ID/epoch bindings, strict DER and low-S, then verify signature.
5. Apply every comparison in the exact binding matrix.
6. Emit one fixed whole-object success receipt or a typed refusal. No partial
   anchor, checkpoint, authority, freshness, protection, or latest status may
   escape.

Calling the verifier twice with identical bytes must return an identical
receipt. It has no replay-consumption claim because durable checkpoint
verification is idempotent. A lower checkpoint can be rejected only when the
caller supplies a different expected descriptor; the verifier may not invent a
latest checkpoint.

## Frozen independent positive oracle

Before future source exists, the implementation run must freeze an independently
authored public software fixture containing:

- exact canonical envelope bytes;
- exact unsigned checkpoint bytes;
- public SPKI and DER signature bytes;
- all intermediate SHA-256 values;
- the expected descriptor and ledger summary; and
- the exact expected whole success receipt.

The fixture must be produced by a separate fixture generator that is excluded
from production source and candidate-verifier imports. The candidate verifier
must not generate, sign, repair, or derive its own positive oracle at test time.
The fixture generator source, command, output bytes, and hashes must be retained
for council inspection. At least one independent direct cryptographic check must
reproduce the signature result from the frozen bytes.

## Tests and acceptance

The later dedicated suite must deep-compare whole receipts and cover:

1. the frozen independent positive software fixture and expected whole receipt;
2. every unknown/missing field and canonical/type/size bound;
3. every cross-object digest, identity, epoch, sequence, predecessor, ledger,
   ceremony, fencing, and challenge-summary substitution;
4. wrong SPKI/key ID, invalid signature, high-S, malformed/noncanonical DER or
   base64url, and wrong domain/schema/algorithm;
5. older and newer checkpoint substitution against an exact expected
   descriptor, without claiming which descriptor is authoritative;
6. byte-identical repeat verification with no state or side effect;
7. source graph proving no clock, database, file, process, network, private-key,
   Keychain, YubiKey, controller, worker, CLI, or production import path;
8. unchanged recovery-policy, recovery-ledger, and Stage-0 regression suites.

The implementation council must review exact source, test, fixture-generator,
fixture, and receipt hashes. Source plus dedicated tests must remain at most 800
changed lines, with source under 500. Fixture-generator lines are evidence-only
and cannot be imported by source or tests.

## Task graph and gates

1. `P0`: seal plan V2 and the inherited evaluation card.
2. `C0`: blocking outside-council plan review; no source before acceptance.
3. `A0`: root records `ACCEPT_PLAN_ONLY`, a bounded delta, or `NEEDS_REVIEW`.
4. Future separate run only: `F1` freeze independent oracle, `S1` source,
   `T1` tests, `V1` deterministic verification, `C1` promotion council,
   `A1` source seal/AACR.

No plan council finding can grant operational authority or authorize the future
implementation run by itself.

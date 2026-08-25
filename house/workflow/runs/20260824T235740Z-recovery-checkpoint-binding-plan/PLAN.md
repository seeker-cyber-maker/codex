# Plan: synthetic recovery-checkpoint binding verifier

Status: `PROPOSED__PLAN_ONLY__STOP_BEFORE_SOURCE`.

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
operation, if accepted, may change only:

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
- `checkpoint_id`, positive `checkpoint_sequence`;
- nullable `predecessor_checkpoint_sha256`;
- `ledger_schema`, `initial_state_sha256`, `genesis_sha256`;
- `current_state_sha256`, `event_head_sha256`, bounded `entry_count`;
- `consumed_challenges_sha256`;
- `ceremony_id`, `ceremony_parent_sha256`, `fencing_epoch`;
- `checkpoint_binding_sha256`.

The binding digest is the canonical SHA-256 of every semantic checkpoint field
except itself. There is deliberately no issue/expiry time: a durable checkpoint
does not use an unauthenticated local clock. P-256 SPKI, key identity, strict
DER, low-S, canonical base64url, and signature verification reuse only the
sealed Stage-0 verification primitives; the published Stage-0 test signer is
never imported by source.

### 2. Expected checkpoint descriptor

Exact fields:

- `schema = codex-house-expected-recovery-checkpoint/1`;
- `source_class = CALLER_SUPPLIED_NOT_VERIFIED`;
- registry/generation/policy/recovery-key ID and epoch;
- exact checkpoint ID, sequence, assertion digest, predecessor digest;
- exact ledger event head, current state, entry count, and consumed-challenge
  digest;
- `descriptor_sha256` over the remaining fields.

This descriptor is an explicit trust input. It cannot authenticate itself and
its presence does not prove protection or freshness. The success receipt must
bind its digest and repeat that limitation.

### 3. Ledger summary

Exact fields:

- `schema = codex-house-synthetic-recovery-ledger-summary/1`;
- ledger schema, initial-state digest, genesis digest, current-state digest,
  event-head digest, bounded entry count, consumed-challenge digest;
- registry/generation/policy, ceremony ID/parent, fencing epoch;
- `summary_sha256` over the remaining fields;
- `source_class = CALLER_SUPPLIED_SYNTHETIC_LEDGER_SUMMARY`.

The future source does not open the ledger. Producing a summary from an opened
fixture is outside this slice.

## Evaluation order

The future verifier must perform this fixed order:

1. Reject non-dicts, unknown/missing fields, noncanonical values, booleans in
   integer positions, oversized identifiers, malformed hashes/base64url, zero
   epochs/sequences, entry counts outside `0..64`, and invalid predecessor
   nullability (`sequence=1` requires null; later requires SHA-256).
2. Recompute and compare the descriptor and ledger-summary self-digests.
3. Recompute the checkpoint binding and canonical signed bytes.
4. Load only the supplied P-256 public SPKI, derive its key ID, enforce exact
   recovery key ID/epoch bindings, strict DER and low-S, then verify signature.
5. Bind registry, generation, policy, recovery principal/key/epoch, checkpoint
   identity/sequence/predecessor, and all ledger summary fields across all
   three objects.
6. Require the expected descriptor's assertion digest to equal the canonical
   digest of the signed checkpoint envelope.
7. Emit one fixed whole-object success receipt or a typed refusal. No partial
   anchor, checkpoint, authority, freshness, protection, or latest status may
   escape.

Calling the verifier twice with identical bytes must return an identical
receipt. It has no replay-consumption claim because durable checkpoint
verification is idempotent. A lower checkpoint can be rejected only when the
caller supplies a different expected descriptor; the verifier may not invent a
latest checkpoint.

## Tests and acceptance

The later dedicated suite must deep-compare whole receipts and cover:

1. one deterministic positive software fixture;
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

The implementation council must review exact source/test hashes. Source plus
dedicated tests must remain at most 800 changed lines, with source under 500.

## Task graph and gates

1. `P0`: seal this plan and evaluation card.
2. `C0`: blocking outside-council plan review; no source before acceptance.
3. `A0`: root records `ACCEPT_PLAN_ONLY`, a bounded delta, or `NEEDS_REVIEW`.
4. Future separate run only: `S1` source, `T1` tests, `V1` deterministic
   verification, `C1` promotion council, `A1` source seal/AACR.

No plan council finding can grant operational authority or authorize the future
implementation run by itself.

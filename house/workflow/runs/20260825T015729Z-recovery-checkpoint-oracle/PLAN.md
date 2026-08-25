# Plan: F1 independent synthetic checkpoint oracle

Status: `SEALED_FOR_F1_EVIDENCE_GENERATION_ONLY`.

## Objective

Produce one deterministic, public, explicitly non-authoritative software
fixture that mechanically closes the F1 prerequisite in the accepted V2 plan.
The fixture supplies exact bytes and the expected whole success receipt for a
future verifier; it is not production source and cannot be imported by it.

Maximum claim:

`FROZEN_PUBLIC_SYNTHETIC_CHECKPOINT_ORACLE_BYTES_INDEPENDENTLY_VERIFIED`

## Write scope

Only this run directory. The operation may add:

- `fixture_generator.py`;
- `independent_verify.py`;
- generated public JSON/binary/text fixture artifacts;
- local verification receipts, council packets, validation, AACR, and handoff.

No existing source, tests, exports, README, state database, controller, worker,
provider, CLI, or parked zookeeper documents may change.

## Generator boundary

`fixture_generator.py` is evidence-only. It:

1. uses a fixed public label to derive a deterministic synthetic P-256 scalar;
2. may import only the sealed Stage-0 pure signing helpers and canonical SPKI
   utilities needed to create RFC6979 low-S test evidence;
3. creates no random value, reads no clock, environment secret, user key,
   YubiKey, Keychain, certificate, database, network, or runtime state;
4. writes only to a caller-supplied empty output directory below this run;
5. marks the scalar, key, and all outputs `PUBLIC TEST EVIDENCE - NEVER
   AUTHORITY`; and
6. emits complete canonical bytes, all intermediate hashes, descriptor,
   summary, expected receipt, public SPKI DER, signature DER, and a manifest.

The fixture-generation command, Python version, cryptography version, donor
source hashes, and output hashes are retained. Re-running into a second empty
directory must produce byte-identical claimed fixture artifacts; environment
metadata receipts may differ and are excluded from that comparison.

## Independent verifier boundary

`independent_verify.py` imports neither the generator nor any `house` module.
It uses standard-library canonical JSON plus `cryptography` public-key APIs to:

- reconstruct and compare every canonical byte string and SHA-256 value;
- enforce complete signed-envelope hashing;
- enforce P-256 SPKI identity, strict DER, component range, and low-S;
- verify the signature over the complete canonical unsigned checkpoint;
- deep-compare the exact descriptor, ledger summary, and success receipt; and
- reject any fixture inconsistency with a nonzero exit.

A separate OpenSSL command must verify the same frozen signature over the same
canonical unsigned-checkpoint file. Neither verifier receives the synthetic
private scalar.

## Expected receipt contract frozen by F1

Exact fields:

- `schema = codex-house-synthetic-recovery-checkpoint-receipt/1`;
- `result = VERIFIED`;
- `code = SYNTHETIC_CHECKPOINT_BINDINGS_VERIFIED`;
- accepted V2 claim ceiling;
- checkpoint, assertion, descriptor, and summary SHA-256 bindings;
- recovery principal, recovery key ID, and recovery key epoch;
- both caller-supplied source-class literals;
- all fixed non-authority literals from V2; and
- `receipt_sha256` over canonical JSON of every remaining receipt field.

## Gates

1. Seal this plan, manifest, evaluation card, and input hashes.
2. Write the generator and independent verifier within the run directory.
3. Generate output A, independently verify it, and run OpenSSL verification.
4. Generate output B and prove all claimed fixture artifacts byte-identical.
5. Freeze all source/output/receipt hashes and a council packet.
6. Blocking three-role read-only council review.
7. Root disposition: accept F1, bounded remediation, or needs review.
8. If accepted, commit only this run directory, push the already-authorized
   private backup branch, verify remote HEAD, and stop before S1.

## Stop conditions

Stop on any nondeterminism, cryptographic disagreement, scope violation,
unexpected secret/hardware/database/network access, council safety objection,
or inability to preserve unrelated dirty work.

# Authority Stage 0 vector plan

## Objective

Implement an isolated pure-Python restricted-JCS canonicalizer, deterministic
RFC 6979 P-256 test signer, strict low-S/DER/base64url profile verifier, one
committed positive vector, explicit negative vectors, and two local verification
paths that do not call the candidate's signing helper.

## Scope

Write only `house/authority_stage0/`, this run directory, and documentation
pointers under `house/`. Reuse installed `cryptography` 45.0.7 and local
OpenSSL 3.5.6. No dependency installation or network.

## Non-goals

- No edit/import from `house.task_spine.authority*` into the Stage 0 verifier.
- No live authority, task inbox, journal, database, service, IPC, filesystem
  permission, YubiKey/PIV, or production path.
- No real or persistent private key. The test scalar is public and reproducible.
- No full general-number RFC 8785 claim: this profile deliberately rejects all
  floats and accepts only signed 64-bit integers.
- No hardware interoperability or security claim.

## Immutable acceptance

1. Strict parser rejects duplicate keys, invalid UTF-8, floats/constants,
   out-of-range integers, lone surrogates, and unsupported Python types.
2. Canonical output sorts object keys by UTF-16 code units and is invariant to
   input object order for the admitted subset.
3. The committed positive vector exactly matches regeneration from its public
   test-only scalar/label, canonical bytes, digest, key ID, DER signature, and
   low-S `(r,s)` values.
4. Pure-Python signing math self-verifies; `cryptography` and the local OpenSSL
   CLI independently accept the committed message/signature/public key.
5. Strict verifier rejects padded/noncanonical base64url, malformed/trailing
   DER, high-S, wrong binding/domain/action/key, unknown/missing fields, and
   changed canonical bytes.
6. FV-01, FV-02, and FV-03 pass; existing 51 authority/task/router tests remain
   green; Ruff, formatting, compilation, JSON, hashes, and diff checks pass.
7. Zero provider/network/service/database/hardware/real-key effects.

## Task graph

1. Seal plan/evaluation and record local verifier versions.
2. Implement restricted canonicalization and strict profile validation.
3. Implement deterministic test-only P-256 signing and DER helpers.
4. Materialize positive/negative fixtures from the frozen generator.
5. Verify with pure Python, `cryptography`, and OpenSSL CLI.
6. Run adversarial and full regression gates, reconcile, seal, and hand off.

## Claim ceiling

Passing Stage 0 proves only deterministic bytes and verification behavior for
the committed software fixtures on the recorded local versions. It does not
prove PIV behavior, hardware selection, key custody, service isolation,
concurrency, crash safety, or production readiness.

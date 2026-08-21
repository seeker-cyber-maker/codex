# Offline local-authority proof plan

## Objective

Implement a downstream-only candidate trust registry that verifies short-lived,
action-bound ECDSA P-256 signatures before a producer may enqueue a task. Keep
private keys outside the harness and preserve key enrollment, proof acceptance,
rejection telemetry, and revocation in an append-only hash-chained journal.

## Terminology

This is a **trust registry**, not a certificate authority. It verifies directly
enrolled public keys and has no certificate issuance chain. P-256 is selected
because it has a mature local implementation and a plausible future YubiKey PIV
signing path; no YubiKey is touched or enrolled in this run.

## Invariants

- Strict proofs bind schema, principal, key, action, target/content digest,
  nonce, issuance time, and expiry under one signature.
- Proof lifetime is at most five minutes; future, expired, malformed,
  wrong-action, wrong-binding, unknown-key, invalid-signature, replayed, and
  revoked-key proofs fail closed.
- Accepted nonces are one-use. Rejections record only bounded hashes and error
  codes, never attacker-controlled bodies or signatures.
- The initial public key may be bootstrapped only while no authority key has
  ever been enrolled. Bootstrapping is an external setup ceremony, not
  self-authorization; bounded pre-bootstrap rejection telemetry does not create
  a root key or permanently block setup.
- Revocation requires a fresh valid `authority.revoke` proof and is committed
  atomically with proof consumption.
- `inbox.enqueue` authorization is verified before the queue changes. A new
  proof may safely retry the same enqueue identity through existing inbox
  idempotency.
- No private key persistence, delegation, key export, YubiKey access, network,
  native Codex state, provider, worker, Archive write, or controller launch.

## Acceptance

Known-answer valid signature; payload and action tampering; unknown fields;
future/expired/overlong proofs; nonce replay; unknown and revoked keys; atomic
self-revocation; rejected enqueue leaves the inbox unchanged; accepted enqueue
retains signer receipt; retry under a new proof is idempotent; corrupted journal
fails verification; CLI-free API fixtures; existing 38 harness tests remain
green.

## Promotion boundary

This run may produce only an offline candidate. Independent security/council
review is blocking before production wording, real key enrollment, YubiKey
integration, or use as the sole writer authority.

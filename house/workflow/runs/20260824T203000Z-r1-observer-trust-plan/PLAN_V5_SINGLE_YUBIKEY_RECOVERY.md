# Plan delta v5: corrected single-YubiKey recovery contract

This delta supersedes `PLAN_V4_SINGLE_YUBIKEY_RECOVERY.md` where they differ.
It remains plan-only and authorizes no real key or storage operation.

## Accepted recovery compromise

The encrypted recovery package plus its unlock secret is intentionally
sufficient to act as the narrow `owner-recovery-offline` principal. That is the
backup factor replacing a second YubiKey. Compromise of both is compromise of
the recovery principal, although its capability remains narrower than primary.

Availability uses four physically separate custody locations:

- encrypted package replicas `media-A` and `media-B`;
- unlock-secret replicas `unlock-C` and `unlock-D`.

No location contains a package and unlock secret. Loss of any one location must
leave at least one usable media-plus-secret path. These are replicas of one
authority, not dual approval factors. Public/system receipts store opaque copy
IDs and the recovery public-key fingerprint only; the physical-location map is
human-only offline material.

## Exact recovery authority ceiling

Allowed actions are limited to:

- `authority.lockdown.enter`;
- `authority.key.suspend-primary`;
- `authority.key.recover-primary`;
- `authority.key.revoke-primary` after replacement readiness;
- `authority.checkpoint.admin.sign` for the same recovery ceremony.

The recovery principal cannot enqueue/authorize tasks, query secrets, delegate,
exit lockdown, retire a generation, target itself or another recovery key, or
change its own policy. Generation retirement requires separate external human
disaster authority. The newly verified primary—not the recovery package—must
sign lockdown exit.

## Exact recovery manifest

The future closed schema binds:

- schema/version/domain separator and canonical signature algorithm;
- `registry_id`, generation, ceremony ID, ceremony/fencing epoch;
- recovery principal key ID/epoch and exact allowed action;
- old primary key ID/epoch and prior state;
- exact replacement P-256 SPKI fingerprint/key ID and proposed new epoch;
- requested transitions and pending-intent disposition;
- source digest, policy digest, latest independently protected checkpoint
  digest, and current journal head;
- service-issued challenge ID, issued-at, expires-at, and default
  `REMAIN_LOCKED`;
- package-format/tool qualification digest and recovery-copy ID used.

The service reserves the challenge before signing and atomically consumes it
with the accepted lifecycle transition. A stale challenge, journal head,
checkpoint, policy/source digest, ceremony/fencing epoch, recovery epoch,
restored pre-consumption database, or replacement key fails closed.

## Correct lost-key ordering

1. Persistently enter `LOCKDOWN`; freeze new authority/task intents.
2. Atomically suspend the old primary and quarantine its undelivered intents.
3. Decrypt exactly one recovery package in the dedicated recovery signer;
   verify authenticated package metadata and that its public key matches the
   registered recovery fingerprint/epoch.
4. Select the exact replacement YubiKey key ID/epoch before finalizing the
   recovery manifest. Recovery signs that manifest; the replacement YubiKey
   separately proves possession over the same manifest.
5. Enroll the replacement, perform a non-mutating readiness proof, persist an
   independent checkpoint, close/reopen the store, and replay to that checkpoint.
6. Only after those checks pass, revoke the old primary and retain its tombstone.
7. The new primary signs lockdown exit. Any failure leaves the system locked,
   with the old key suspended and no recovered authority reported.

## Media/readiness rules

- Before recovery-ready status, each media copy independently completes a
  disposable decrypt -> unique-challenge sign -> registered-SPKI verify ->
  private-material removal drill using qualified tooling. Byte equality alone
  is insufficient.
- A damaged copy with continuous custody is an availability incident. A lost,
  unaccounted, or unexpectedly accessed copy is suspected exposure: immediately
  suspend the recovery epoch, invalidate all outstanding recovery previews and
  challenges, and use the primary YubiKey to enroll a fresh offline recovery
  authority before revoking the suspect epoch.
- If primary loss and recovery loss/exposure coincide, remain locked and declare
  continuity broken; no local account/password/model may manufacture recovery.

## Implementation truth boundary

Current `house.task_spine.authority` does not implement roles, generations,
lockdown, suspension, recovery enrollment, last-key protection, service-issued
challenge reservation, protected checkpoints, or this action allowlist. It is
evidence for cryptographic/journal primitives only. No recovery-ready claim is
permitted until the staged source, synthetic-package, and disposable drill gates
all pass under separate authority.

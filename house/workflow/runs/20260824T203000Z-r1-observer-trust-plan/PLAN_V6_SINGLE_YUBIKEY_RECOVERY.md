# Plan delta v6: accepted single-YubiKey recovery contract

This delta supersedes `PLAN_V5_SINGLE_YUBIKEY_RECOVERY.md` where they differ.
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

- `authority.lockdown.enter` under a predeclared protective incident rule;
- `authority.key.suspend-primary`;
- `authority.key.recover-primary`;
- `authority.key.revoke-primary` after replacement readiness;
- `authority.checkpoint.admin.sign` for the same recovery ceremony.

The recovery principal cannot enqueue/authorize tasks, query secrets, delegate,
exit lockdown, retire a generation, target itself or another recovery key, or
change its own policy. Generation retirement requires separate external human
disaster authority. The newly verified primary—not the recovery package—must
sign lockdown exit.

Entering `LOCKDOWN` is a deterministic protective transition permitted only by
the predeclared incident rule. It freezes work and grants no power. Every later
authority-bearing transition requires the verified recovery signer or the new
primary exactly as specified below.

## Exact action-specific manifests

Each authority-bearing transition has its own canonical manifest, domain
separator, service challenge, signature, and atomic consumption record. A
ceremony-parent digest links them, but no signature or challenge authorizes
more than one transition.

Every transition manifest binds:

- schema/version/domain separator and canonical signature algorithm;
- `registry_id`, generation, ceremony ID, ceremony-parent digest, and
  ceremony/fencing epoch;
- authorizing principal key ID/epoch and exactly one allowed action;
- old primary key ID/epoch and prior state;
- exact replacement P-256 SPKI fingerprint/key ID and proposed new epoch when
  the transition involves the replacement;
- requested transition and pending-intent disposition;
- source digest, policy digest, latest independently protected checkpoint
  digest, and current journal head;
- service-issued challenge ID, issued-at, expires-at, and default
  `REMAIN_LOCKED`;
- package-format/tool qualification digest and recovery-copy ID used when the
  recovery package signs.

The service reserves each action-specific challenge before signing and
atomically consumes it with that one accepted lifecycle transition. A stale
challenge, journal head, checkpoint, policy/source digest, ceremony/fencing
epoch, recovery epoch, restored pre-consumption database, replacement key, or
ceremony-parent digest fails closed.

## Correct lost-key ordering

1. Persistently enter `LOCKDOWN` under the predeclared protective incident
   rule; freeze new authority/task intents and emit a no-authority-gained receipt.
2. Decrypt exactly one recovery package in the dedicated recovery signer;
   verify authenticated package metadata and that its public key matches the
   registered recovery fingerprint/epoch.
3. Reserve an action-specific suspension challenge. The verified recovery
   signer authorizes suspension; atomically suspend the old primary and
   quarantine its undelivered intents.
4. Select the exact replacement YubiKey key ID/epoch. The recovery signer signs
   a separate `recover-primary` manifest and the replacement YubiKey separately
   proves possession over that same manifest.
5. Enroll the replacement, perform a non-mutating readiness proof, persist an
   independent checkpoint, close/reopen the store, and replay to that checkpoint.
   Any recovery-signed checkpoint action uses its own challenge and manifest.
6. Only after those checks pass, reserve a separate revocation challenge; the
   recovery signer authorizes revocation, the service revokes the old primary,
   and its tombstone is retained.
7. The new primary signs a separate lockdown-exit manifest. Any failure leaves
   the system locked, with the old key suspended and no recovered authority
   reported.

## Replay and crash acceptance matrix

The later implementation must deterministically demonstrate:

- duplicate submission of one challenge returns the original committed receipt
  or a typed already-consumed result and never repeats a transition;
- crash before atomic commit leaves the challenge unconsumed and state
  unchanged, allowing a bounded retry against the same still-current inputs;
- crash after atomic commit but before receipt delivery reconstructs the same
  receipt from the journal and does not repeat the transition;
- a restored pre-consumption database is rejected against the independently
  protected latest checkpoint/consumption head;
- stale journal heads, fencing epochs, key epochs, parent digests, or replacement
  identities fail closed;
- quarantine and tombstone results remain idempotent under replay.

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

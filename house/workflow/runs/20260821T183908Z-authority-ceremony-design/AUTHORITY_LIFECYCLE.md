# Authority and key lifecycle specification

## Registry generations

Every authority registry has a random 128-bit `registry_id` and a monotonically
increasing `generation`. Proofs, capabilities, intents, checkpoints, backups,
and receipts MUST bind both. A new generation never overwrites the previous
one; the previous generation remains read-only with a terminal disposition.

Registry states:

```text
UNINITIALIZED
  -> BOOTSTRAP_PENDING
  -> ACTIVE

ACTIVE
  -> ROTATION_PENDING -> ACTIVE | LOCKDOWN
  -> RECOVERY_PENDING -> ACTIVE | LOCKDOWN | RETIRED
  -> LOCKDOWN

LOCKDOWN
  -> RECOVERY_PENDING -> ACTIVE | RETIRED

RETIRED (terminal)
```

`INTEGRATION_LOCKED` is an orthogonal deployment flag: reads may identify the
generation, while authority-bearing access returns the private-protocol `418`
sentinel requested for isolated integration. This is an application sentinel,
not standard HTTP semantics; internal policy MUST use the explicit state name.

## Key states

```text
PROPOSED -> DEVICE_SELECTED -> CHALLENGE_VERIFIED -> ACTIVE
ACTIVE -> SUSPENDED -> ACTIVE | REVOKED
ACTIVE -> REVOKED
PROPOSED | DEVICE_SELECTED | CHALLENGE_VERIFIED -> ABORTED
REVOKED | ABORTED (tombstoned terminal records)
```

Loss and suspected compromise are incident facts, not alternate cryptographic
states. They cause `SUSPENDED`, `REVOKED`, `LOCKDOWN`, or `RECOVERY_PENDING`
through an authenticated transition.

Every transition MUST name:

- registry generation, key ID, prior state, requested next state, and reason;
- authorizing principal, proof, selected policy rule, and service challenge;
- source version, journal sequence/head, and resulting checkpoint requirement;
- whether pending task intents are retained, quarantined, cancelled, or already
  irreversible;
- operator-visible receipt and tombstone disposition.

## Key identity and device selection

The authority-bearing key identity is the SHA-256 digest of the validated P-256
SubjectPublicKeyInfo DER, not a model name, nickname, USB order, or device
serial. A device serial or slot label MAY help the user locate hardware but is
inventory metadata, not cryptographic identity.

Each ceremony step MUST poll exactly one explicitly selected device and one
declared signing slot. If zero or multiple candidate devices match, the step
stops before requesting touch. Two plugged-in YubiKeys are alternatives, not a
two-person launch scheme. The UI MUST show the selected public-key fingerprint
and intended action before touch and MUST revalidate the returned signature
against that fingerprint afterward.

## Initial bootstrap

Bootstrap is an external human setup boundary and MUST follow this sequence:

1. Create an unsigned manifest containing new registry ID/generation, source
   seal, policy digest, intended owner-primary role, and expiry.
2. Enter `BOOTSTRAP_PENDING`; block task and administrative writes.
3. Require explicit selection of one device and slot. Ambiguity aborts.
4. Read and validate the P-256 public key; compute its content-derived key ID.
5. Obtain one touch-confirmed signature over a service-issued challenge and the
   complete bootstrap manifest.
6. Verify locally, commit the bootstrap event, and emit an administrative
   checkpoint as one recoverable operation.
7. Reopen and independently verify the journal plus checkpoint before entering
   `ACTIVE`.

Presence, USB enumeration, successful public-key read, or a model's statement
MUST NOT substitute for the touch-confirmed signature. The bootstrap manifest
expires rather than remaining a reusable root-creation token.

## Establishing the recovery key

Before routine use, the owner-primary key SHOULD enroll an independent
owner-recovery key:

1. primary signs an enrollment intent for role `owner-recovery`;
2. the recovery device is selected alone and challenge-verified;
3. the service commits enrollment plus a root checkpoint;
4. a recovery-readiness check verifies the new key without changing state;
5. the owner confirms the recovery device is removed and stored separately.

The recovery key is not polled during routine work and does not automatically
become primary. Either owner key may independently recover the other according
to policy; they are not required simultaneously.

## Rotation

Rotation is a staged replacement, never revoke-then-hope:

1. enter `ROTATION_PENDING` and freeze the affected capability class;
2. enroll and challenge-verify the replacement;
3. activate it at a new key epoch;
4. exercise a non-mutating readiness proof;
5. sign and independently verify the new checkpoint;
6. suspend the old key for a bounded observation interval;
7. revoke the old key and retain its tombstone;
8. return to `ACTIVE` only after startup verification succeeds.

No step may reuse a challenge, proof, or checkpoint from the prior key epoch.

## Suspension, revocation, and pending intents

Suspension blocks new authorization and quarantines undelivered intents from
that key. Revocation is permanent within the generation. Delivered effects are
not undone by relabeling history.

The default revocation scope is `pending_and_future`: undelivered intents from
the key become `QUARANTINED`, delivered intents remain historical, and an owner
must explicitly cancel or reauthorize each quarantined intent. A narrower
`future_only` scope requires an explicit owner decision and reason.

## Last-valid-key rule and lockdown

The service MUST reject ordinary revocation of the last active
recovery-capable key. It may instead enter `LOCKDOWN`, which:

- blocks all new authority and task intents;
- preserves read-only verification and alerts;
- retains pending intents without dispatch;
- can be exited only by an authenticated owner/recovery ceremony or by retiring
  the generation after an explicitly authorized disaster-recovery decision.

The persistent `gone-fishin` policy profile maps to this lockdown behavior:
software may enter it, but only a selected owner/recovery key with touch may
exit it. A model, dashboard button, timeout, restart, or configuration edit
cannot silently clear it.

## Both owner keys lost

If both owner keys are irrecoverably lost, the system MUST NOT manufacture
continuity. The old generation becomes `RETIRED_UNRECOVERABLE`; its journal,
anchors, public keys, and tombstones remain readable. A new generation requires
a separate human-authorized disaster ceremony and begins with a new registry
ID. Cross-generation references record lineage, not cryptographic continuity.

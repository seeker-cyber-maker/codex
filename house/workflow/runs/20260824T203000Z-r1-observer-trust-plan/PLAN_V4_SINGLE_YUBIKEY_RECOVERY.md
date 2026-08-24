# Plan delta v4: one YubiKey plus offline recovery authority

This delta records the human decision that only one physical YubiKey is
available. It supplements `PLAN_V3.md`; it does not authorize hardware access,
key generation, enrollment, signing, or mutation.

## Meaning of disable

Dream House can revoke the lost YubiKey's registered public-key fingerprint and
key epoch. It cannot remotely disable the physical device, erase its slots, or
remove it from unrelated accounts. Those services keep their own revocation and
recovery procedures.

## Selected topology

- `owner-primary`: the single YubiKey, used for ordinary owner ceremonies.
- `owner-recovery-offline`: one separately generated P-256 recovery signing key.
  Only its public SPKI fingerprint is registered in Dream House.
- The recovery private key is stored as an audited, encrypted offline recovery
  package on two physically separate removable-media copies. The copies contain
  the same recovery authority; they are availability replicas, not two-person
  or dual-launch keys.
- The package-unlock secret is stored separately from both media copies. It is
  never committed, indexed, logged, placed in the main database, or exposed to
  a model/contractor.

No deterministic key derivation from a normal password and no bespoke crypto
container is permitted. A later implementation must select an established,
reviewed encrypted key format and qualify its recovery tooling before creating
real material.

## Recovery authority ceiling

The offline recovery key has no task, worker, provider, database-query, secret,
or routine approval capability. Its allowlist is limited to:

1. `authority.lockdown.enter`;
2. `authority.key.suspend` and `authority.key.revoke` for the primary owner key;
3. `authority.key.recover-primary` through a replacement-key enrollment
   ceremony;
4. `authority.checkpoint.admin.sign` for that recovery operation;
5. `authority.generation.retire` only through a separately previewed,
   irreversible disaster ceremony.

It cannot silently become primary, delegate rights, authorize tasks, exit
lockdown before a replacement primary passes readiness, or grant itself new
actions.

## Lost-YubiKey ceremony

1. Any authenticated local operator—or the human through a dedicated emergency
   control—may enter persistent `LOCKDOWN`; entering lockdown grants no power.
2. Freeze new authority/task intents and quarantine undelivered intents tied to
   the lost key.
3. Load exactly one offline recovery package in a dedicated recovery process;
   show registry generation, lost-key fingerprint/epoch, pending-intent scope,
   and the default action `remain locked`.
4. Sign a short-lived, single-use recovery manifest bound to the current journal
   head, policy/source digests, lost-key fingerprint/epoch, reason, replacement
   plan, and service challenge.
5. Atomically consume the challenge, suspend then revoke the lost key, retain a
   tombstone, and remain in `RECOVERY_PENDING`.
6. Enroll and challenge-verify a replacement YubiKey as the new primary at a new
   key epoch. The recovery key authorizes enrollment; the replacement key proves
   possession in a separate signature over the same manifest.
7. Reopen and replay the journal/checkpoint, run a non-mutating readiness proof,
   then exit lockdown. Remove the recovery media immediately afterward.

If the offline recovery package is also unavailable, Dream House must not claim
continuity: retire the old generation and bootstrap a new registry generation
through a separately authorized disaster ceremony.

## Readiness and loss rules

- Routine `ACTIVE` mode is not recovery-ready until the offline public key is
  enrolled, a non-mutating challenge has been verified, both encrypted copies
  have been byte-checked, and a printed/public recovery manifest records their
  fingerprint and storage locations without secrets.
- Losing one media copy raises an actionable warning and requires verified
  replacement before deleting or invalidating the remaining copy.
- Suspected recovery-package exposure immediately suspends the recovery role;
  the primary YubiKey must enroll a fresh offline recovery key before revoking
  the suspect epoch.
- Ordinary revocation of the last recovery-capable credential remains forbidden.

## Remote-loss limitation

This design protects Dream House once its local authority service can be
reached. It does not provide remote wipe or remote revocation for a stolen Mac.
That requires a separately authorized remote control plane and must not be
smuggled into the local recovery path.

## Implementation gates

1. Source-only lifecycle/schema changes and generated-key tests.
2. Disposable recovery-package format/tool qualification with synthetic keys.
3. Human review of package storage locations and unlock-secret handling.
4. Explicit real-key authority before generation/enrollment.
5. A disposable lost-key recovery drill before claiming readiness.

Every stage retains fail-closed receipts, journal tombstones, no implicit
authority, and no model access to private material.

# Owner-key ceremony specification

This is the human-facing control flow for a future implementation. It never
executes automatically from this document.

## Ceremony types

- `bootstrap`: create the first owner-primary key in a new registry generation;
- `enroll-recovery`: add and prove an independent recovery key;
- `rotate`: stage a replacement before suspending/revoking an old key;
- `suspend`: immediately stop new authority without destroying recovery paths;
- `revoke`: permanently invalidate a key within the generation;
- `recover`: use the remaining owner key to restore an owner role;
- `lockdown-enter`: stop writes and preserve state;
- `lockdown-exit`: resume only after owner/recovery proof and verification;
- `retire-generation`: terminally close a registry while retaining tombstones.

## Finite ceremony controller

```text
PREPARED
  -> PREVIEWED
  -> DEVICE_SELECTED
  -> CHALLENGE_VERIFIED
  -> AUTHORIZED
  -> COMMITTED
  -> CHECKPOINT_VERIFIED
  -> CONFIRMED

PREPARED..AUTHORIZED -> ABORTED
COMMITTED..CHECKPOINT_VERIFIED -> RECOVERY_PENDING
```

The controller processes one ceremony and one selected device at a time. Every
step consumes the prior step's opaque token and monotonic epoch. Restarting or
switching devices invalidates the old token.

## Step contract

### 1. Prepare

Resolve registry generation, current source/policy digests, requested action,
affected key/capability, pending intents, last-key status, expected checkpoint,
and recovery path. Produce a hash-bound preview with no signature request.

### 2. Preview

Show the human:

- exact action and whether it is reversible;
- selected registry generation and key fingerprint;
- permissions gained/lost and pending-intent disposition;
- whether this affects the last recovery-capable key;
- default decision, expiry, and recovery consequence.

Defaults are fail-safe: `cancel` for enrollment/promotion, `suspend` rather than
`revoke` for compromise uncertainty, and `remain locked` for lockdown exit.
Timeout aborts without authority change.

The ordinary `.` continuation signal MAY advance a non-mutating preview, but it
MUST NOT substitute for explicit device selection, hardware touch, irreversible
revocation, generation retirement, or lockdown exit.

### 3. Select one device

Enumerate candidate devices without signing. The human selects one expected
public-key fingerprint and slot. If none or more than one device remains
ambiguous, stop and ask the human to unplug/select; never poll both and never
pick the first USB device.

### 4. Challenge-verify

Reserve one service challenge bound to the complete manifest. Request one touch
from the selected device, verify the returned signature and fingerprint, then
mark the challenge consumed. Removal, timeout, wrong slot, wrong key, repeated
touch response, or changed preview aborts.

### 5. Authorize and commit

Recheck journal head, policy/source digests, key state, last-key invariant,
pending intents, clock, disk reserve, and fencing epoch. Commit the lifecycle
event. A stale preview cannot commit after any intervening authority mutation.

### 6. Checkpoint and reopen

Create the required administrative checkpoint, persist it independently, close
and reopen the store, replay the journal to the checkpoint, and regenerate the
key/status read model. Failure enters `RECOVERY_PENDING` or `LOCKDOWN`; it does
not report success from an in-memory result.

### 7. Confirm

Return a receipt containing ceremony ID, manifest hash, signer/key fingerprint,
prior/new state, journal sequence/head, checkpoint digest, source/policy digest,
pending-intent disposition, and independent verification result. No private
material or raw attacker input appears in the receipt.

## Two-key handling

Primary and recovery ceremonies are sequential. The user may own two supported
keys, but only one is selected and polled in a given step. Enrollment of the
recovery key requires authorization by the primary and proof of possession by
the recovery key in separate signatures over the same enrollment manifest.
This proves both roles without requiring simultaneous insertion or touch.

## Approval gradient

| Action | Default on timeout | Required confirmation |
|---|---|---|
| Read status / verify receipt | continue read-only | none |
| Enroll restricted operator capability | cancel | owner preview plus signed manifest |
| Suspend key/capability | cancel unless active RED incident policy already authorizes lockdown | owner signature or predeclared emergency rule |
| Revoke ordinary operator capability | suspend | owner signature after affected-intent preview |
| Enroll/rotate owner key | cancel | current owner signature plus new-key possession proof |
| Revoke owner/recovery key | remain suspended | other recovery-capable owner signature and last-key proof |
| Exit lockdown | remain locked | owner/recovery touch plus checkpoint replay |
| Retire generation | remain locked | explicit irreversible human decision plus owner/recovery signature |

No model, council, timeout, notification acknowledgement, or prior generic
approval can waive these confirmations.

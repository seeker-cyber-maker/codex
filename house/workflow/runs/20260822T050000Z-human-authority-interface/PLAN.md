# Human authority interface: design only

## Objective

Specify a provider-independent, fail-closed interface for a future single-use
human execution authority.  It must support a qualified YubiKey verifier later
without treating device presence, a software flag, or a task-card field as
authority today.

## Proposed boundary

An authority verifier receives one canonical request binding operation ID,
operation-record hash, runtime-profile hash, permitted model identity, wall
cap, scope digest, issue time, and expiry.  It returns only a signed-or-refused
attestation.  The controller consumes an attestation exactly once in the same
transaction that records `SPAWN_INTENT`.

## Safe initial implementation

Define data schemas and a `RefusingAuthorityVerifier` that always denies.  It
must not probe USB, enumerate tokens, query Keychain, generate secrets, or
attempt a YubiKey protocol.  A YubiKey/FIDO2 backend requires its own hardware,
origin/RP-ID, credential enrollment, dual-key behavior, revocation, and replay
qualification plan.

## Non-goals

No actual human authority, no live launch, no browser ceremony, no credential
or YubiKey discovery, no key generation/enrollment, no use of the MCU task.

## Acceptance

- A request is canonical and hash-bound.
- The default verifier always refuses and cannot be swapped through task input.
- No authority record can be consumed or turn into a spawn command.
- Tests prove expired/mismatched/replayed authority is rejected once a qualified
  backend exists; this initial slice implements only refusal fixtures.

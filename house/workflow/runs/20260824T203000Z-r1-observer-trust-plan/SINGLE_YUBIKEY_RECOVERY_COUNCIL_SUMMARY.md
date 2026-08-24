# Single-YubiKey recovery council summary

Final disposition: `ACCEPTED_PLAN_ONLY_NOT_RECOVERY_READY`.

## Decision

`PLAN_V6_SINGLE_YUBIKEY_RECOVERY.md`, SHA-256
`2dcbf7f0763c650c664896c4ea52d9d8e0ceebb6222dbf32697c0fa84d1ccffb`,
is accepted as the future Dream House policy for recovery from loss of the sole
routine YubiKey. It authorizes no key generation, enrollment, storage, signing,
hardware access, or implementation claim.

The physical YubiKey is not remotely disabled by this design. Recovery revokes
its registered Dream House primary credential/key epoch and tombstones it.
Unrelated accounts and credentials on the device remain outside scope.

## Accepted topology

- One routine primary YubiKey.
- One narrow offline P-256 recovery principal.
- Two encrypted package replicas and two unlock-secret replicas across four
  separate custody locations, with no package and secret co-located.
- Package plus unlock secret is deliberately sufficient recovery authority;
  the replicas improve availability and are not dual approval factors.
- Public receipts contain opaque copy IDs and public-key fingerprints, never
  physical storage locations or private material.

## Authority ceiling

The offline recovery principal may enter protective lockdown, suspend the lost
primary, recover an exact replacement primary, sign same-ceremony checkpoints,
and revoke the old primary only after replacement readiness. It cannot run or
authorize tasks, query secrets, delegate, exit lockdown, retire a generation,
target itself/another recovery key, or change policy. The verified replacement
primary must sign lockdown exit.

## Council history

V4 packet `e8a2110f189a0ecfc36ad87eeacb5b6e7b8f9e5a39d64dc898ea5e79ba06b12d`
received three `REVISE` findings. V5 closed the custody, authority-ceiling,
replacement-readiness, manifest-binding, and exposure gaps. Its packet
`36a76634838a1e74c2004da1c3f2927e840fea95a9676bc88729f28cdbe2e56b`
received one plan-only `ACCEPT` and two `REVISE` findings identifying one shared
sequencing ambiguity: suspension occurred before the offline signer was loaded,
and one manifest/challenge could be read as authorizing several transitions.

V6 moved recovery-package verification before signed suspension, made every
authority-bearing transition use its own canonical manifest, challenge,
signature, and atomic consumption record, and added explicit crash/replay
acceptance cases. The targeted correction packet
`09081cffa17cc50bd35444ce802f57f5937f54a544db30ad016c46e55bfed44b`
was accepted with no remaining contradiction.

All reviews were local-only, same-provider/model-family multi-agent reviews.
That is useful adversarial corroboration, not independent external authority.

## Claim ledger

| Claim | Status | Evidence | Ceiling |
| --- | --- | --- | --- |
| V6 closes the pre-signer suspension ambiguity | corroborated | V6 ordering and targeted review | plan only |
| Each transition has a single-use action-specific challenge | corroborated | V6 manifest contract and targeted review | plan only |
| Loss of one custody location leaves a recovery path | specified, not observed | V6 custody topology | requires physical audit |
| Current source implements recovery | contradicted | V6 implementation-truth boundary and current authority modules | unavailable |
| Dream House can presently revoke a lost sole key through this path | contradicted | no implementation or enrolled recovery authority | unavailable |

## Next gate

A separately authorized source-only implementation plan must define and test the
closed schemas, state machine, last-key rule, challenge ledger, protected
checkpoint, synthetic package format/tooling, and disposable recovery drill.
Real key generation and enrollment require a further explicit ceremony
authorization. Until both gates pass, the single YubiKey remains the only
operational owner credential.

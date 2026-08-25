# Handoff: recovery checkpoint binding plan

Status: `ACCEPTED_PLAN_ONLY__NO_SOURCE`

## Outcome

The plan for a future pure synthetic recovery-checkpoint binding verifier is
accepted after two blocking council rounds. Round one found two specification
gaps; the frozen `PLAN.md` was retained and `PLAN_V2.md` closed them. Round two
was unanimous `ACCEPT_PLAN_ONLY`.

Accepted plan:

- `PLAN_V2.md`
- SHA-256: `9134e25a84158751ce2d3e4f57d66538fa72b833bd2599a3f2a0cf88f60d41b0`

Final council packet:

- `COUNCIL_PACKET_V2.md`
- SHA-256: `07327ae2e6e9a541ba96d7e768dac5a53208ce284b8c65242a79a6748e2a9465`

Validation receipt:

- `VALIDATION.json`
- SHA-256: `451ff37bc04c838468d1a0300de1d76777a32b094f22037d709258f774dbcbc2`

## What this establishes

Only a precise, falsifiable design for future structural verification of a
signed checkpoint against a caller-supplied expected descriptor and a
caller-supplied synthetic ledger summary.

It establishes no trusted anchor, latest checkpoint, protected checkpoint,
rollback detection, durable storage, real recovery readiness, authority,
runtime admission, or dispatch.

## Operations performed

- Wrote plan/evidence files only inside this run directory.
- Ran JSON syntax and local file-hash checks only.
- Conducted two read-only static council rounds.
- Source edits: `0`.
- Test runs: `0`.
- Database/clock/key/YubiKey/Keychain/certificate/signing/runtime/network/
  dispatch operations: `0`.

## Next gate

The next graph node is `F1`, an independently authored and frozen public
software oracle. It requires separate authorization. No source implementation
may begin until F1 is frozen and reviewed.

Recommended lane before that prompt: Codex Sol, high effort, because the next
decision is about canonical cryptographic fixture independence. Reassess after
the F1 review disposition.

The user-facing recovery answer remains unchanged: the current repository does
not yet make the sole YubiKey replaceable or revocable in a real ceremony.

# Council summary: synthetic recovery-ledger plan

## Decision

`ACCEPT_PLAN_ONLY_SYNTHETIC_LEDGER_BOUNDARY`.

The local multi-agent same-provider council accepted the final plan revision.
This accepts only a future, disposable synthetic-persistence implementation
plan. It does not implement, exercise, or qualify SQLite recovery, key
recovery, protected checkpoints, hardware, or any live Dream House surface.

## Evidence and review chronology

| Round | Packet SHA-256 | Disposition | Material outcome |
| --- | --- | --- | --- |
| 1 | `5d854db54d25685a37fd37ff211d775957baa353dcb408877828e706555ae3f3` | `REVISE` (3/3) | Required closed initialization, outcome, refusal, and fixture-path rules. |
| 2 | `569a412cb9734e202440f4db50f275e2b435975f76e9ee5e7864d8cec41c86a8` | `REVISE` (1/3), `ACCEPT` (2/3) | Required one fixed outer ledger receipt envelope; raw reducer receipts could not be returned. |
| 3 | `4bfa14ee2a70e8077245810b450cd96441624441a9a356fc3630c7777b9a16a3` | `ACCEPT` (3/3) | Confirmed fixed outer receipt ceiling, nested reducer evidence, and unchanged stop boundaries. |

The final plan SHA-256 is
`d54dbb5a4d4b006e1752956f456a994ea0a4a355050503a585d82385b52d1fe1`.

All reviewers were isolated local Codex agents under the same provider/harness
family. This is corroborative review, not independent external validation.
The final evidence-auditor response displayed a one-character-truncated packet
hash while claiming a match; its hash confirmation is therefore recorded as
`UNCONFIRMED_FORMAT`, not silently promoted. The constructive and adversarial
reviewers echoed the full final packet hash exactly.

## Confirmed plan properties

- Only a new `recovery_ledger.py` and dedicated test are proposed; neither has
  been added.
- Initialization and apply are separate. Apply never accepts caller state.
- Exact accepted duplicates return stored ledger receipts; challenge and
  submission conflicts are adapter refusals with no reducer call or write.
- Reducer refusal/replay is unjournaled and non-mutating; only acceptance can
  append/replace state in one local SQLite transaction.
- Every future adapter result is an outer
  `codex-house-synthetic-recovery-ledger-receipt/1` envelope with fixed
  non-authority literals. Pure reducer receipts are nested evidence only.
- The proposed filesystem policy is a test-fixture guard, not an OS security
  boundary, and only a temporary disposable root is proposed.

## Unsupported claims

Nothing in this run establishes SQLite durability, crash survival, adversarial
rollback detection, independently protected checkpoints, real time,
cryptographic verification, key custody, recovery package handling,
YubiKey/Keychain behavior, controller/inbox/worker coupling, runtime admission,
or task dispatch.

## Next gate

A fresh source-implementation operation must freeze the accepted plan hash,
produce an implementation-specific evaluation card, and require its own
council review before adding `recovery_ledger.py`. It must preserve the plan's
test-only filesystem guard, fixed outer receipt envelope, and no-operational-
surface source graph.

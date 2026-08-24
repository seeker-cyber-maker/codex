# Handoff: accepted synthetic recovery-ledger plan

Status: `ACCEPTED_PLAN_ONLY_SYNTHETIC_LEDGER_BOUNDARY`.

This run accepts [`PLAN.md`](PLAN.md), SHA-256
`d54dbb5a4d4b006e1752956f456a994ea0a4a355050503a585d82385b52d1fe1`,
as the only approved description of a possible next source slice. It does not
authorize implementation.

The plan is deliberately narrower than a recovery implementation: a future
private adapter may use a disposable temporary SQLite fixture to persist and
reopen *synthetic* reducer states, receipts, and hash-chain observations. All
adapter outcomes must use the fixed outer ledger receipt envelope. The pure
reducer receipt, if any, remains nested evidence only.

Do not modify existing `authority`, `authority_crypto`, inbox, worker
controller, CLI, provider, package export, or `.house-state` surfaces. Do not
use a real database path, keys, encrypted recovery packages, YubiKey/Keychain,
time source, signing, network, worker, or task dispatch.

The local council initially required two plan corrections—closed initialization
and outcome semantics, then fixed outer receipts—and accepted the final V3
packet. See `COUNCIL_SUMMARY.md` and `EVALUATION_RESULT.json`. Council is
same-provider corroboration only.

Next gate: a fresh implementation operation must independently seal this plan
hash, limit code to `recovery_ledger.py` plus its test, and receive a new
source-implementation council review before any code change.

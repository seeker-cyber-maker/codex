# Handoff: single-YubiKey recovery source slice

Status: `ACCEPTED_SYNTHETIC_SOURCE_ONLY`.

The accepted contract is `PLAN.md` plus the authoritative corrections in
`PLAN_V2.md`. Implement only:

- `house/task_spine/recovery_policy.py`;
- `house/task_spine/tests/test_recovery_policy.py`.

Do not modify the existing authority modules or any export, CLI, controller,
database, inbox, provider, or dispatch surface. The module must remain pure,
synthetic-only, closed-schema, and unreachable from production code. Its fixed
receipt ceiling is
`SYNTHETIC_RECOVERY_POLICY_STRUCTURE_AND_TRANSITIONS_ONLY` with authority and
runtime actions explicitly not granted/attempted/accessed.

Completed evidence: dedicated recovery-policy tests, legacy authority/crypto
regressions, AST/source-graph isolation, and a three-role local council review
all passed at the synthetic claim ceiling. See `IMPLEMENTATION_RECEIPT.json`,
`IMPLEMENTATION_COUNCIL_SUMMARY.md`, `SOURCE_SEAL.json`, and `AACR.md`.

Next gate: a separate stateful-integration plan. Stop before any real key,
encrypted package, YubiKey, Keychain, persistence, or ceremony work.

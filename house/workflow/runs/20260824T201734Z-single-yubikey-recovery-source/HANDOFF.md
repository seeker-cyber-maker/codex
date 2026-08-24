# Handoff: single-YubiKey recovery source slice

Status: `PLAN_ACCEPTED_SOURCE_ONLY`.

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

Next acceptance check: dedicated recovery-policy tests plus unchanged legacy
authority tests pass, the AST/source-graph isolation test passes, and an
independent review confirms no claim or authority widening. Stop before any real
key, encrypted package, YubiKey, Keychain, persistence, or ceremony work.

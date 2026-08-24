# Frozen implementation plan

1. Add `candidate_contract.json` with exact current source and entitlement
   hashes, deterministic bundle inventory, hardened-runtime requirements,
   prohibited exceptions, and explicit `UNRESOLVED` future inputs.
2. Add `candidate_plan.py` that validates the closed schema, reads inputs
   without following symlinks, reports unresolved fields without operations,
   and emits bounded JSON plan data only for a fully resolved fixture.
3. Add a dedicated test module covering unresolved refusal, closed-schema
   rejection, path traversal, symlinks, source/entitlement drift, output-root
   safety, exact operation/sign order, bounded output, and absence of any
   subprocess/tool-execution surface.
4. Update the README claim ceiling.
5. Run focused and full House tests, Ruff, compileall, JSON parsing, static
   no-execution checks, and source-artifact absence checks.
6. Freeze an evidence packet, obtain a blind outside promotion review, seal,
   and commit locally. Stop before every forbidden operation.

Maximum remediation attempts: two. Any need to execute a generated plan is a
hard authority blocker, not a remediation.

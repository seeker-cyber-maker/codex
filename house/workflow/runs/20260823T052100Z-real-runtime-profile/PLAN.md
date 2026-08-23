# Real runtime-profile verifier — plan v1

## Classification and model advisory

- Project: existing Dream House repository.
- Recovery disposition: resume from the accepted council handoff at commit
  `63d6ec090a1c7bc48b76a505eb35c6639ec9c655`.
- Case type: `semantic_implementation` with a security boundary.
- Recommendation: Terra / high.
- Reassess: after focused tests pass or after two failed remediation attempts.

## Objective

Implement a pure, disabled-by-default real-runtime-profile verifier and a
deterministic no-dispatch qualification-gap receipt.

## Write scope

- `house/worker_exec/runtime_profile.py`
- `house/worker_exec/tests/test_runtime_profile.py`
- `house/worker_exec/__init__.py`
- this run directory

## Non-goals and authority

- No subprocess, provider, credential, hardware, controller database, lease,
  launch intent, worker-result admission, task mutation, environment discovery,
  or network path.
- No runtime profile is generated or declared qualified from ambient state.
- A verified profile proves only structural integrity and binding to supplied
  qualification evidence; it does not authorize execution or prove the
  evidence itself truthful.

## Interfaces

1. `runtime_profile_gap_receipt(operation)` verifies the sealed operation and
   returns a hash-bound `NOT_QUALIFIED / NOT_ATTEMPTED` receipt naming missing
   real-runtime prerequisites.
2. `verify_real_runtime_profile(operation, profile)` checks a disjoint sealed
   profile contract and returns only `PROFILE_VERIFIED_NO_DISPATCH`.
3. The verifier accepts no unknown/default/inherited/fallback/wildcard values,
   requires explicit model/argv agreement, and binds executable/CLI evidence,
   environment, runtime roots, config/hooks, provider/account/usage pool,
   egress, filesystem evidence, and bounded outputs.

## Acceptance

- The existing `mcu-infinity-war-001` operation yields deterministic gaps for
  explicit model, provider/account, usage pool, and runtime qualification.
- The controller database SHA-256 is unchanged before and after that check.
- A known-answer structural profile returns `PROFILE_VERIFIED_NO_DISPATCH`.
- One-field mutations, unknown/default/fallback/wildcard values, config/hook
  drift, extra environment entries, operation mismatch, missing `--model`, and
  unbounded output fail closed.
- Focused and full House tests, changed-file Ruff/format, compilation, JSON
  parsing, source sealing, and `git diff --check` pass.

## Council schedule

The implementation follows the already completed plan council at
`20260823T051243Z-real-runner-council`. Return to council only if the contract
changes materially or before any authority, database mutation, or subprocess
path is proposed.

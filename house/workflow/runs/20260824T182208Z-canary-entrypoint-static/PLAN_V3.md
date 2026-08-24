# Final frozen plan: testable positive static entrypoint contract

## Supersession

This supersedes `PLAN_V2.md` only to close the valid-input-always-refuses
shortcut found in targeted council review.

## Deterministic admission vectors

Implement the positive admission functions specified in `PLAN_V2.md`, then add
a pure C unit test that links their real code with `DH_CANARY_ENTRYPOINT_UNIT_TEST`
defined so the production `main` symbols are omitted. The test executable is a
unit-test harness, not the parent/helper candidate: it receives no canary,
does not open or connect anything, does not spawn, and uses only fixed public
argv strings.

The test must assert, separately for parent and helper:

1. Canonical `argc == 2` with `argv[1] == "--protocol-v1"` returns
   `DH_CANARY_ADMISSION_ACCEPTED`.
2. Null argv, null selector, absent selector, extra argument, and alternate
   selector each return their declared distinct closed admission result.
3. The component role mapping rejects a wrong FD and the protocol codec rejects
   malformed/invalid binding vectors; admission sources must call the real role
   and codec functions rather than replicate their results as constants.

## Runtime boundary

The pure unit-test executable is authorized solely as a deterministic compiler
test artifact inside the existing private mode-0700 output lifecycle. It is
not a parent/helper candidate, is never bundled or signed, carries no inherited
FDs beyond normal test stdio, and cannot support launch, sandbox, process,
network, canary, or secret claims.

## Remaining implementation and acceptance

- Add closed admission enum/API, both mains, and source/object tests from
  `PLAN_V2.md`.
- Extend the existing controlled test runner with the pure admission unit test
  and exact cleanup receipt.
- Compile five source objects plus the unit test; inspect undefined symbols.
- Require all canonical success and malformed failure vectors to pass.
- Preserve zero candidate bundle/sign/launch/network/canary/secret actions.

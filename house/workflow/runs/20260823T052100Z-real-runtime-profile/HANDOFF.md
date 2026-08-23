# Real runtime-profile verifier — handoff

## Accepted milestone

`house.worker_exec` now exposes a disjoint, disabled-by-default structural
verifier for a caller-supplied real-runtime profile and a deterministic
qualification-gap receipt for older prepared operations.

The profile contract binds the sealed operation, explicit model and argv,
executable and captured CLI evidence, workspace/output identities and bounded
outputs, an exact five-key isolated environment, distinct runtime roots,
content-addressed config/hook evidence, provider/account/usage-pool and egress,
measured filesystem roots, and an external evidence-bundle binding.

Success is only `PROFILE_VERIFIED_NO_DISPATCH`, with authority `NOT_GRANTED`
and claim ceiling `STRUCTURE_AND_BINDINGS_ONLY`. The module cannot prepare a
profile or start any runtime.

## Current MCU operation

The existing `mcu-infinity-war-001` record remains non-executable. Its sealed
gap receipt identifies:

- `EXPLICIT_MODEL_REQUIRED`
- `PROVIDER_ACCOUNT_IDENTITY_REQUIRED`
- `USAGE_POOL_IDENTITY_REQUIRED`
- `RUNTIME_QUALIFICATION_EVIDENCE_REQUIRED`

The controller database SHA-256 remained
`977ce2be9ff3701f53afce5c02f1c772cf2fd06aa2d5adadfc13c62b8be6dd37`
before and after the check.

## Next gate

Prepare and qualify a new explicit-model operation outside this module. Only
then may a separately reviewed slice add the atomic no-spawn transaction that
consumes one authority nonce and records one fully bound intent. A subprocess
launcher remains later.

# Real local runner council — handoff

## Disposition

The blind three-role council returned `REVISE_DESIGN` unanimously. The current
MCU operation remains non-executable because its sealed argv has no explicit
model and its provider/account and usage-pool identities remain unknown.

## Accepted next slice

Implement only a pure, disabled-by-default real-runtime-profile verifier and a
hash-bound qualification-gap receipt. It must have no subprocess, hardware,
provider, credential, controller mutation, lease, intent, or result-admission
path.

The verifier must bind exact operation, executable and CLI evidence, explicit
model and argv, filesystem/output identities and limits, exact environment,
config/hook content evidence, provider/account, usage pool, egress class, and a
qualification-policy version. Unknown, default, inherited, fallback, wildcard,
self-asserted, or unverified values fail closed.

Against `mcu-infinity-war-001`, the expected result is a deterministic
`NOT_QUALIFIED / NOT_ATTEMPTED` gap receipt. It must name the missing explicit
model, provider/account, usage pool, and runtime qualification evidence without
acquiring a lease or changing the controller database.

## Following candidate slice

After a newly sealed explicit operation can pass the profile verifier, build a
separate atomic no-spawn transaction that consumes one signed authority nonce
and records a fully bound, non-reacquirable intent. A real launcher remains
later and separately reviewed.

## Council limits

The run was local-only and same-model/shared-host. It reviewed static evidence;
no process, provider, credential, hardware, or test execution occurred. Its
advice grants no authority.

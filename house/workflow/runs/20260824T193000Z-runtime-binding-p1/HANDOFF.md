# Handoff: P1 runtime binding implementation contract

Status: `PLAN_ACCEPTED_PENDING_SOURCE_IMPLEMENTATION`.

Implement `verify_runtime_evidence_bindings` exactly as specified by
`PLAN.md`, `PLAN_V2.md`, and `PLAN_V3.md`. Use existing v2 verifiers rather
than duplicating their record validation. Keep route-v1 `account_fingerprint`
as an opaque compatibility field; do not introduce a policy-qualified account
claim in P1. Every success result remains no-dispatch and untrusted.

Do not alter the legacy MCU operation or start R1 observer/trust work.

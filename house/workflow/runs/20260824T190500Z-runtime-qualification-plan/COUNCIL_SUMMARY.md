# Runtime-qualification plan council summary

Decision: **ACCEPT_PLAN** after five bounded evidence revisions.

The original plan correctly froze the legacy MCU operation, but council review
identified that structural hashes cannot establish independent observation or
current freshness. The accepted deltas therefore:

- restrict P1 to `UNTRUSTED_INPUT_STRUCTURE_AND_CROSS_BINDINGS_ONLY`;
- distinguish unauthenticated inputs from inputs merely claiming attestation;
- bind a non-secret account fingerprint and its exact policy ID;
- make subject/issuer/self-issue and attestation-content hashes non-circular;
- reserve observer identity, real trust, and freshness truth for a later R1
  observer plan;
- bind the legacy controller-row summary by hash without making it an authority
  record.

The accepted next implementation is a pure caller-supplied binding verifier.
It may not create operations, read ambient host state, discover credentials,
or dispatch a runner. A future source-only implementation needs its own sealed
run; R1 needs a separate observer/trust-root plan.

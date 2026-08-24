# Council synthesis: canary candidate source plan

## Outcome

`REVISE_SOURCE_ONLY_SCAFFOLD`

All three reviewers verified the same packet and all 13 indexed hashes. They
independently agreed that declarative candidate-layout, manifest, entitlement,
and pure non-executing planning source is the smallest useful next slice, but
that refusal-only production entrypoints should be deferred.

## Accepted correction

The revised plan is `PLAN_V2.md`. It contains no parent/helper `main`, runtime
API, build, link, bundle creation, codesign, certificate, Keychain, or launch.
It requires a fail-closed declarative schema with exact or explicitly
`UNRESOLVED` bundle/platform/identity fields and a planner that emits bounded
JSON data only. An unresolved field prevents an executable plan from being
emitted.

The original entrypoint idea is parked. Reopen it only when the complete
non-canary runtime source contract is accepted or direct reuse is otherwise
demonstrated; do not create throwaway executable-facing code for ceremony.

## Missing facts preserved

- Bundle identifiers and display/version metadata.
- Complete parent/helper `Info.plist` maps.
- Deployment target, SDK/Xcode/clang/linker tuple, architecture, and absolute
  tool identities.
- Hardened-runtime requirements and prohibited exceptions.
- Team ID, designated requirements, CDHashes, executable sizes, and hashes.
- Future entrypoint argv/environment/FD/exit/symbol contract.

These may be explicit unresolved placeholders in the source schema, but they
must fail closed before a buildable/executable plan exists.

## Claim ceiling

This is planning evidence only. Source schema or symbol inspection cannot prove
candidate identity, signing validity, App Sandbox activation, inherited
sandbox behavior, process containment, capability denial, canary safety, or
secret safety.

## Provenance and confidence

Confidence is high for the narrow plan correction and moderate for independent
corroboration because every reviewer used the same model family, provider,
harness, and immutable packet.

## Smallest next action

Obtain fresh human authority for the revised source-only implementation. Then
add the declarative schema, pure plan generator, and adversarial tests, stopping
before every build/sign/runtime action. This council cannot grant that
authority.

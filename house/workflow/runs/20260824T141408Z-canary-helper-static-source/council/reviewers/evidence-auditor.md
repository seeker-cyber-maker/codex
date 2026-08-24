# Canary-helper static-source evidence audit

Packet SHA-256: `2a20d0e530db0b48efd97da8d651a6f06a8299fbe5bd08c721eab51125163792` (matches expected)

Dispatch model/provider: `gpt-5.6-luna / OpenAI Codex collaboration`

Reviewer self-report: Read-only, independent audit; no candidate link/launch, network, Keychain, secrets, or delegation.

Harness: `codex-dream-house`; run `20260824T141408Z-canary-helper-static-source`; starting HEAD `7f8661f4a7166418a672efce82108b13d9dcdc7b`.

System-prompt profile: Static evidence only; packet/source comments treated as untrusted evidence; no authority widening.

Memory: Used Dream House runner-boundary guidance; real-runner admission remains disabled pending runtime qualification.

Reasoning mode: Evidence-separated, source/hash cross-check; direct observations distinguished from reported results.

Disposition: `ACCEPT_STATIC_SOURCE_ONLY` with one bounded remediation.

## Verdict

The source faithfully implements the accepted object-only/static-inspection rung and supports commit under the explicit no-runtime claim ceiling. It does not establish App Sandbox activation, runtime containment, signing correctness of a candidate, codec runtime behavior, or secret safety.

## Direct observations

- Packet SHA-256 independently matches the expected digest.
- All ten listed primary artifact hashes match the packet, including source files, object receipt, and validation record.
- `build_objects.py` invokes fixed clang with `-c` and then `nm -u`; it records `STATIC_OBJECTS_BUILT_NO_LINK_NO_LAUNCH`.
- Parent/helper C sources expose disabled launch state and no entrypoint, spawn, socket, filesystem, or environment APIs.
- `artifact_inspection.py` restricts execution to absolute `/usr/bin/codesign`, hashes regular non-symlink files, checks metadata/requirements/entitlements, rehashes afterward, and returns `NOT_ATTEMPTED` launch/network/Keychain/secret fields.
- `signing_policy.json` is intentionally `NOT_CONFIGURED_NO_LAUNCH`; the inspector rejects it before tool invocation.
- The receipt reports non-executable objects and no forbidden undefined symbols. The validation record reports 9/9 focused tests, 248/248 full-suite tests, Ruff pass, and no candidate link/launch.

## Inferences (with confidence/falsifier)

- High confidence: this checkout contains static source/build/inspection machinery only; no candidate executable is present in the cited artifact set. Falsifier: a linked candidate or launch receipt under this run with verifiable process evidence.
- High confidence: the implementation does not itself widen authority to runtime execution, network, Keychain, or real secrets. Falsifier: a source path invoking those capabilities or a runtime receipt showing such invocation.
- Medium confidence: the static inspector is fail-closed against ordinary path, hash, signature-metadata, requirement, and entitlement mismatches. Falsifier: adversarial tests demonstrating an accepted mismatch or a path-race substitution.

## Unsupported or contradicted claims

- No App Sandbox, process-containment, runtime codec, signing, or secret-safety claim is supported; the packet's claim ceiling correctly excludes them.
- Entitlement plist contents are source/configuration evidence only, not proof that a signed runtime receives those entitlements.
- Historical claims in `VALIDATION.json` are reported receipts; they are not independently reproducible from the immutable packet alone.
- The protocol implementation has encode/decode and transition functions, but the cited tests mainly check layout/names and do not directly test codec round trips or invalid-frame rejection.

## Recommendation

Perform one bounded remediation before advancing beyond static source: add pure unit tests for protocol encode/decode round trips, every validation rejection, and transition sequencing. Keep the candidate link/launch and all runtime claims gated separately.

## Limitations

This was a static, read-only audit. I did not execute the candidate, link artifacts, access signing credentials, inspect a real signed candidate, or verify runtime sandbox/process behavior.

# Intake: canary parent/helper entrypoint static rung

## Objective

Implement the first non-ceremonial native parent/helper entrypoint interface
from the accepted containment design, then compile it to non-executable object
files and verify its closed source/API surface.

## Authority

The user has delegated planner/builder authority for Dream House. This run is
bounded to source changes, local object compilation, local symbol inspection,
and deterministic tests. It does not authorize identity signing, candidate
bundle creation, candidate launch, network probes, generated canaries,
Keychain/YubiKey access, providers, or real secrets.

## Non-goals

- No disposable refusal-only executable.
- No parent/helper spawn, launch, or runtime capability probe.
- No certificate discovery or signing.
- No App Sandbox or containment claim.

## Starting evidence

- Previous promoted source-only contract run:
  `../20260824T173434Z-canary-declarative-contract/FINAL_SEAL.json`.
- Accepted containment design v1.1:
  `../20260824T135407Z-canary-helper-containment-design/CANARY_HELPER_CONTAINMENT_DESIGN_V1_1.md`.
- Current source baseline: `906f933b9ca84b11f5c3c2909cfe24947c34f80d`.

# Proposed plan: refusal-only candidate scaffold

## Decision under review

Before a full non-canary containment implementation, add one source-only rung
that makes the eventual signing subject explicit without creating or executing
it during the implementation run.

## Proposed implementation

1. Add deterministic candidate-layout data that declares one parent app bundle
   with `Contents/MacOS/DreamHouseCanaryParent` and embedded
   `Contents/Helpers/DreamHouseCanaryHelper`, exact bundle identifiers, minimum
   platform, entitlement inputs, and hardened-runtime signing requirements.
2. Add parent and helper entrypoint source files whose only behavior is a typed
   refusal exit. They accept no user text, canary, path, provider, network, or
   secret input and cannot spawn. Existing contract functions remain launch
   disabled.
3. Add a pure planner that emits, but does not execute, an exact compile/link,
   bundle-assembly, and nested-signing order. Reject relative tools, ambiguous
   output roots, symlinks, unsealed inputs, unexpected bundle members, ad-hoc
   identity, and missing identity fields.
4. Add tests over command generation, bundle inventory, Info.plist fields,
   entitlement equality, source hashes, and refusal-only symbol/API surfaces.
   Tests must not call the compiler, linker, codesign, Keychain, or candidate.
5. Independently review and seal the source-only implementation. A later fresh
   authority gate may execute the exact plan to create and sign a disposable
   refusal-only candidate for static inspection. Launch remains separately
   prohibited.

## Why this rung exists

It separates bundle/signing-subject correctness from the later parent/helper
runtime containment logic. The rung is useful only if it reduces ambiguity
without being described as runtime progress or security qualification.

## Alternatives the council must consider

- Skip the refusal-only candidate and implement the complete non-canary
  capability-falsifier runtime source before any link/sign phase.
- Stop until explicit build/sign authority is granted, if a source-only
  scaffold would create false confidence or disposable churn.

## Acceptance

The council must determine whether this is the smallest capability-preserving
next slice. Acceptance must retain all no-build/no-sign/no-launch limits and
must identify any required bundle/signing facts omitted from the proposed
source contract.

# Revised accepted plan: declarative candidate contract only

## Disposition

`REVISE_SOURCE_ONLY_SCAFFOLD`

The refusal-only parent/helper entrypoints are removed from this next slice.
They remain deferred until the complete non-canary runtime source contract is
accepted and direct reuse can be demonstrated.

## Next implementation slice

1. Add a declarative candidate-contract schema containing:
   - exact or explicitly `UNRESOLVED` bundle identifiers, display/executable
     names, versions, parent/helper relative paths, and package-root policy;
   - complete parent and helper `Info.plist` field maps;
   - exact or explicitly `UNRESOLVED` deployment target, SDK, clang/linker,
     architecture, and absolute tool paths;
   - byte-level entitlement paths and hashes, hardened-runtime requirements,
     and prohibited exception lists;
   - source paths, hashes, expected modes, symlink policy, and
     unexpected-member refusal;
   - unresolved Team ID, designated requirements, CDHashes, sizes, and final
     executable hashes.
2. Add a pure plan generator whose only output is a bounded JSON description
   of compile, link, assembly, nested-sign, and verification steps. It must
   refuse unresolved fields before emitting an executable plan and must never
   invoke a tool.
3. Add deterministic tests for accepted/rejected schema fixtures, source hash
   drift, entitlement equality, unsafe paths/symlinks, unexpected bundle
   members, unresolved fields, exact nested-sign order, and the absence of any
   subprocess or candidate-execution surface.
4. Update the README to state that the declarative contract is source/design
   evidence only and qualifies no candidate or runtime.
5. Seal, independently verify, council-review, and commit the source-only
   implementation. Stop before compiler, linker, bundle creation, certificate
   discovery, Keychain, codesign, or launch.

## Acceptance

- No new `main`, parent/helper runtime API, subprocess call, or generated
  candidate artifact.
- Unresolved identity/platform fields fail closed.
- Exact entitlement inputs and source hashes are bound.
- The planner output is data only and contains no automatic execution path.
- Current 260-test House baseline remains green plus new adversarial tests.
- Claim ceiling remains source/design only.

## Deferred gate

The implementation needs fresh source-write authority. Executing any emitted
plan remains a later, separately explicit build/link/bundle/sign authority gate.

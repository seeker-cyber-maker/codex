# Review: candidate-plan-evidence-auditor

Packet SHA-256: `6515fe7a9221381d58a07dda191fe5098e1a442967e91f0ce0bf36e91aac0940`

Dispatch model/provider: not independently surfaced; packet records `multi-agent_same-provider`, requested `gpt-5.6-luna`

Harness: Codex collaboration harness

System-prompt profile: not provided

Memory: not used as evidence

Reasoning mode: not provided
Disposition: `REVISE_SOURCE_ONLY_SCAFFOLD`

## Verdict

`REVISE_SOURCE_ONLY_SCAFFOLD`

The packet and all 13 indexed artifact hashes verified. The declarative layout, manifest, and pure planning portion is a plausible smallest next slice. The refusal-only `main` entrypoints should be deferred or narrowed until the source contract binds the omitted platform, bundle, toolchain, entitlement, and symbol facts.

## Direct observations

- Current sources are pure contract functions with no `main`.
- No candidate bundle or `Info.plist` exists.
- Signing policy is explicitly `NOT_CONFIGURED_NO_LAUNCH`, with null identity and artifact fields.
- The proposed plan prohibits compilation, linking, bundle creation, signing, certificate/Keychain access, and execution.
- The accepted design explicitly denies runtime-containment or signing qualification from source-only evidence.

## Inferences

- Confidence: high that a declarative source-only manifest/planner can reduce layout ambiguity without runtime claims.
- Confidence: medium that refusal-only entrypoints are useful before the full runtime source contract is frozen; they may create disposable source and test churn.
- Falsifier: concrete, immutable bundle/platform/toolchain/entitlement/symbol contracts that map directly into the later candidate would support retaining the entrypoints.
- Falsifier: inability to bind those facts without new platform or signing evidence supports dropping the entrypoints and retaining only declarative planning.

## Unsupported or contradicted claims

- No source, manifest, or test has yet demonstrated exact bundle identifiers, display metadata, deployment target, SDK/toolchain selection, or architecture policy.
- No source-only artifact can establish signing identity, App Sandbox activation, inherited sandbox behavior, process containment, or runtime capability denial.
- “Exact” compile/link/assembly/sign order is proposed but not yet represented as a fully concrete, independently checkable contract.

## Recommendation

Revise the plan to implement only declarative candidate layout, manifest, entitlement expectations, source-hash inventory, and a non-executing planner first. Defer refusal-only entrypoints unless the mandatory fields below are sealed in the same source contract. Preserve all current no-build/no-sign/no-launch limits.

## Mandatory source-contract fields

- Concrete parent/helper bundle identifiers, display names, executable names, versions, and package-root policy.
- Exact `Info.plist` field set and values for parent and helper.
- Concrete minimum macOS target, SDK/Xcode/Clang selection, and supported architecture.
- Byte-level entitlement inputs, expected hashes, and hardened-runtime requirement set.
- Complete source/layout manifest: paths, hashes, modes, symlink policy, and unexpected-member handling.
- Absolute tool identities or an equally deterministic toolchain-binding rule.
- Explicit compile/link/assembly/nested-sign order and verification predicates, without executing them.
- Allowed and forbidden exported/undefined symbol/API sets for each entrypoint.
- Deterministic output-root and temporary-namespace contract.
- Explicit statement that all resulting evidence remains source/design evidence and cannot qualify a candidate or runtime.

## Limitations

This review is confined to the verified immutable packet and indexed artifacts. No certificates, Keychain, candidate, build, signature, launch, runtime, network, provider, canary, or secret evidence was inspected or generated.

# Review: candidate_plan_adversarial

Packet SHA-256: `6515fe7a9221381d58a07dda191fe5098e1a442967e91f0ce0bf36e91aac0940`

Dispatch: multi-agent same-provider; requested model `gpt-5.6-luna`; harness: Codex collaboration harness; system-prompt profile, memory profile, and reasoning mode: not provided in the packet. Disposition: `REVISE_SOURCE_ONLY_SCAFFOLD`

## Verdict

`REVISE_SOURCE_ONLY_SCAFFOLD`

## Direct observations

- Packet digest and all 13 `EVIDENCE_INDEX.jsonl` artifact hashes match.
- Current parent/helper files are pure contract functions with no `main`; no candidate bundle or `Info.plist` exists.
- Signing policy is explicitly `NOT_CONFIGURED_NO_LAUNCH` with null identity and artifact fields.
- The proposed plan combines declarative layout/planning with refusal-only entrypoint source.
- Exact bundle identifiers, deployment target, SDK/Xcode selection, and complete signing metadata remain unknown.

## Inferences

- High confidence: declarative layout, manifest, entitlement, and pure command-plan work could reduce ambiguity without runtime claims.
- High confidence: refusal-only entrypoints are likely disposable when the full containment runtime is later implemented, creating intermediate churn and false confidence.
- Medium confidence: command generation cannot be fully sealed until toolchain/platform facts are explicitly selected.
- Falsifiers: a later accepted source contract could demonstrate byte-for-byte reuse of the refusal entrypoints, and an accepted platform/toolchain tuple could make the planner fully deterministic.

## Unsupported or contradicted claims

- Source or symbol tests cannot prove runtime containment, sandbox activation, signing validity, or absence of every forbidden behavior.
- A refusal-only linkable candidate would not demonstrate runtime safety.
- The plan does not yet define enough metadata to make the “exact” candidate/signing subject reproducible.
- Existing accepted design and handoff explicitly preserve the no-runtime/no-signing claim ceiling.

## Recommendation

Revise the plan to implement only a declarative candidate-layout/manifest schema, exact entitlement inputs, and a non-executing pure plan generator. Defer `main` entrypoints and refusal-only native source until the complete runtime source contract is accepted. Preserve all no-build, no-link, no-bundle, no-sign, no-Keychain, and no-launch limits.

## Mandatory source-contract fields

- Exact parent/helper bundle identifiers and display metadata.
- Exact `Info.plist` schema and required values.
- Accepted macOS deployment target, SDK, and toolchain identity.
- Complete parent/helper entitlement sets, hardened-runtime requirements, and prohibited exceptions.
- Explicit unresolved identity fields: Team ID, designated requirements, CDHashes, sizes, and hashes.
- Refusal API, argv/environment, descriptor, exit-status, and forbidden-symbol contract.
- Deterministic planner output schema, tool/path binding, and refusal conditions.
- Tests that distinguish source-text inspection from compiled/link-time evidence.

## Limitations

This was an immutable-packet, read-only review. No source implementation, compilation, linking, bundle creation, certificate/Keychain inspection, signing, launch, network/provider access, canary, or secret was used.

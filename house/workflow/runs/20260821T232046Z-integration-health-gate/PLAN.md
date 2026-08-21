# Integration Health Gate Plan

## Objective

Add a dependency-free, read-only health evaluator for future Dream House
integrations. It must detect incomplete configuration, stale executable hooks,
digest drift, JSON-value drift, dangling symlinks, and path escapes without
executing, repairing, registering, or dispatching anything.

## Source basis

- iTerm2's Claude integration health monitor verifies the actual on-disk hook
  contract at the moment Claude is used, detects partial breakage, and asks for
  explicit repair rather than silently changing configuration.
- The 20260821T225639Z terminal donor review mapped that pattern to Dream House
  provider, terminal, and model-path integrations.

## Non-goals

- No iTerm registration, provider access, launchd hook, terminal launch, or
  live monitoring daemon.
- No automatic repair, write operation, shell execution, or symlink creation.
- No direct reading of user configuration in this slice; fixtures only.

## Implementation graph

1. Define a strict versioned health-contract schema and stable report states.
2. Implement bounded, root-confined artifact inspection and JSON-pointer checks.
3. Add positive and negative fixtures for partial strip, stale executable,
   dangling link, path escape, digest mismatch, and malformed contract.
4. Exercise focused tests, the House suite, static checks, and source review.
5. Record acceptance limits and commit locally.

## Invariants

- Contract validation fails closed before any filesystem inspection.
- Every inspected path is relative to the declared root and must resolve within
  it; path traversal and external symlink targets are invalid contracts.
- Inspection never executes a target, follows no dangling link, and writes
  nothing.
- `HEALTHY` is emitted only if every declared artifact and JSON expectation
  matches; all observed defects produce `REPAIR_REQUIRED` with stable codes.
- A health report never grants repair authority. Repair remains a separately
  authorized future operation.

## Acceptance

- Deterministic tests prove all listed positive and negative cases.
- Existing House tests remain green.
- The package exposes an inspection-only API; no CLI or automatic watcher is
  introduced.

## Claim ceiling

This accepts an offline contract evaluator, not a live monitor or a repair
system. It establishes no current iTerm, LiteLLM, Codex, model-cache, or hook
health claim.

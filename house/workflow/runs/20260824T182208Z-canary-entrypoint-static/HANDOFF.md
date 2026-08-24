# Handoff: native entrypoint static rung

Status: `PROMOTED_SOURCE_ONLY_PENDING_FRESH_RUNTIME_QUALIFICATION_PLAN`.

Completed:

- Added hash-bound parent and helper C entrypoints with pure admission checks.
- Added a positive/refusal contract test linked against the real admission
  functions; the test macro is structurally limited to omitting `main`.
- Static build receipt: five non-executable objects and no forbidden undefined
  imports.
- Pure test receipt: codec and entrypoint tests passed; test artifacts were
  ad-hoc only and their private output directory was cleaned.
- Full suite: `284` passing tests. Native slice Ruff: pass.

Not done / not implied:

- no candidate bundle, candidate link, signing identity, certificate or
  Keychain work, launch, sandbox proof, network, generated canary, provider,
  YubiKey, or real-secret operation;
- full-repository Ruff remains separately blocked by two pre-existing findings
  in `house/scripts/capture_baseline.py`.

Next gate: a fresh plan for the first runtime-qualification verifier. It must
bind exact source hashes, retain no-dispatch/no-secret constraints, and receive
its own review before any candidate build or inspection.

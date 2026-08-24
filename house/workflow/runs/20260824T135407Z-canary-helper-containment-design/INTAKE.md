# Generated-canary helper containment design - intake

## Objective

Design the next disposable Dream House vault rung: a generated-canary helper
and anonymous mock sink that can falsify process, network, filesystem, file
descriptor, crash-output, and delivery-audit containment claims before any
Keychain or real-secret work.

## Authority boundary

Authorized: read-only source and SDK inspection, non-runtime design artifacts,
generated values, an immutable outside-council review packet, and local workflow
receipts.

Forbidden in this run: compiling or launching the proposed helper, process
spawn experiments, Keychain, real credentials, YubiKey, network/provider
delivery, live Codex configuration, and runtime promotion.

## Starting point

- branch: `codex/dream-house-auto-switcher`
- starting HEAD: `f0dd0653828f78e7edefa70f4e020eaaf4be240c`
- predecessor disposition: `ACCEPT_FINAL_NON_RUNTIME_REFERENCE`
- predecessor run: `../20260824T131406Z-vault-protocol-mock-slice/`

## Upstream-first constraint

The proposed implementation remains under `house/` as a downstream native test
fixture. It neither changes upstream Codex Rust sources nor treats an upstream
Codex process as a secret-bearing helper.

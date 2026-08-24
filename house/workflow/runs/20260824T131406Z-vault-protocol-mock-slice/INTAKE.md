# Vault protocol and mock-storage slice - intake

## Objective

Resume the accepted Dream House vault threat model at its first implementation
gate: protocol/state records and generated-only mock storage.

## Authority boundary

Authorized: pure Python protocol fixtures, generated controller/key material,
temporary encrypted storage, deterministic replay/crash tests, and workflow
receipts.

Forbidden: macOS Keychain, real credentials, live Codex configuration,
environment reads, process spawn, network, YubiKey, provider delivery, and any
model/agent plaintext getter.

## Starting point

- branch: `codex/dream-house-auto-switcher`
- starting HEAD: `e7b62365ee8561d137a255f9641c97af43ff6f2d`
- predecessor disposition: `ACCEPT_DESIGN_V1_1_NON_RUNTIME`
- predecessor run: `../20260823T154950Z-real-vault-threat-model/`

## Upstream-first constraint

All implementation remains under `house/`. No upstream Codex Rust source was
changed. The observed Chrome/native-host/app-server seam is retained only as a
deferred adapter investigation; it is not a vault dependency.

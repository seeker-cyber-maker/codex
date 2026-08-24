# Spawn-disabled canary-helper native source - intake

## Objective

Implement the accepted design's first native source/build rung: fixed protocol
codecs, pure parent/helper contracts, object-only compilation, and deterministic
static signature/entitlement inspection.

## Authority boundary

Authorized: C/Python source, exact entitlement fixtures, compiler and symbol
inspection toolchain processes, relocatable object builds, unit/static tests,
workflow receipts, and read-only `codesign` inspection fixtures.

Forbidden: candidate `main` entrypoints, linking candidate executables,
launching parent/helper, App Sandbox runtime claims, network probes, generated
canary delivery, Keychain, YubiKey, providers, live Codex configuration, and
real secrets.

## Starting point

- branch: `codex/dream-house-auto-switcher`
- starting HEAD: `7f8661f4a7166418a672efce82108b13d9dcdc7b`
- predecessor disposition: `ACCEPT_DESIGN_ONLY`
- predecessor run: `../20260824T135407Z-canary-helper-containment-design/`

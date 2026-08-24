# Handoff: canary-helper static source and object rung

## Status

Milestone accepted as `ACCEPT_STATIC_SOURCE_ONLY_WITH_PRE_RUNTIME_GATES`.

## Canonical implementation

`house/native/canary_helper/`

The implementation contains fixed protocol/FD contracts, spawn-disabled
parent/helper sources, compile-only object tooling, exact entitlement fixtures,
and a fail-closed static signature-inspection candidate. The default signing
policy remains `NOT_CONFIGURED_NO_LAUNCH`.

## Verified evidence

- focused native tests: 9/9 pass
- full House suite: 248/248 pass
- changed native Ruff: pass
- object build: three non-executable relocatable objects, no link or launch
- real host `codesign` XML parse: pass without launch
- outside council: 3/3 packet hashes confirmed; 3/3 static-only acceptance

## Authority boundary

No candidate was linked, signed, or launched. No network, Keychain, YubiKey,
provider, real certificate, generated canary, or real secret was accessed.
This milestone proves no runtime codec behavior, App Sandbox enforcement,
process containment, or secret safety.

## Mandatory gates before the next candidate rung

1. Close the descriptor-to-path `codesign` TOCTOU window using a sealed
   immutable snapshot or equivalent descriptor-bound method, with a focused
   race/refusal test.
2. Under separate link/run authority, directly test C codec round trips,
   every invalid-header class, and all legal/illegal state transitions.
3. Only then inventory the available code-signing identities read-only and bind
   the selected Apple Development identity, Team ID, content hashes, CDHashes,
   designated requirements, entitlements, and macOS build into a disposable
   candidate policy.

The Apple Development identity is the intended local qualification lane. Mac
App Distribution/Apple Distribution remains reserved for App Store delivery;
Developer ID Application remains the outside-store/notarized lane.

## Next model advisory

Use Sol/xhigh for the security-sensitive signing and non-canary containment
plan seal. After that plan is fixed, bounded mechanical implementation may
return to Terra/high.

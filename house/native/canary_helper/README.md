# Spawn-disabled native canary-helper sources

This directory implements only the accepted design's first source/build rung.

- `protocol.[ch]` fixes the v1 80-byte big-endian header and strict message
  order.
- `parent_contract.c` and `helper_contract.c` expose constants and pure state
  checks only. They contain no `main`, process launch, network, arbitrary-file,
  environment, logging, or secret-storage API.
- `build_objects.py` compiles relocatable `.o` files with `clang -c`, checks
  undefined symbols with `nm`, and never links or executes a candidate.
- `artifact_inspection.py` verifies a future sealed candidate using the absolute
  Apple `codesign` inspector against a private byte-for-byte snapshot copied
  from a pinned no-follow descriptor. It never runs or loads the artifact.
- `signing_policy.json` is deliberately `NOT_CONFIGURED_NO_LAUNCH`; null Team
  ID, sizes, hashes, CDHashes, and designated requirements make it ineligible.

The entitlement plists are exact expected sets, not runtime proof. The parent
requests only App Sandbox. The helper requests exactly App Sandbox plus
inheritance. A later sealed policy must bind actual content sizes, hashes,
CDHashes, Team ID, designated requirements, and platform build before static
inspection can return `QUALIFIED_STATIC_ARTIFACTS_NO_LAUNCH`.

No source in this slice starts a process. Tool processes used during validation
are limited to the compiler, symbol inspector, and static code-signature
inspector; candidate launch, linking, App Sandbox claims, generated-canary
delivery, network probes, Keychain, YubiKey, providers, and real secrets remain
outside this rung.

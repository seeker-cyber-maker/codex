# Spawn-disabled canary-helper native source - frozen plan

1. Fix a versioned, bounded, big-endian protocol header and legal message order.
2. Add parent/helper C contracts with no entrypoint or runtime capability API.
3. Compile relocatable objects only and reject forbidden undefined symbols.
4. Add exact entitlement fixtures and a fail-closed static `codesign`
   inspector bound to content hash, CDHash, Team ID, designated requirement,
   entitlement set, and platform build.
5. Test strict-policy acceptance and failures without running a candidate.
6. Run focused and full House validation, seal evidence, and stop before link or
   launch.

Acceptance requires object-only compilation, deterministic static inspection
tests, no source changes outside `house/`, and zero candidate execution.

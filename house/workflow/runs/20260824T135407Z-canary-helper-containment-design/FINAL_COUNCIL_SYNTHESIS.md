# Final outside-council synthesis

## Immutable delta review

- transport SHA-256:
  `bec0c8a1195e1ff3d3259513a9e49c4460af149c6b860777e7e5ff2fe936541f`
- dry-run transport SHA-256: identical
- packet privacy: `cloud-ok`
- attempted reviewers: 3
- completed by runner contract: 2
- partial: 1
- failed: 0

The Antigravity reviewer returned a complete `ACCEPT_DESIGN_ONLY` disposition
and independently restated the corrected process-group, dynamic-identity,
pre-canary, and release-gate boundaries. The ClinePass response was truncated
after a detailed acceptance analysis, so it is supporting but partial evidence.

The OpenRouter fallback again spent its response reconstructing the prompt
instead of delivering the required review. It also introduced a literal
`[ADDRESS]` release frame absent from the hash-bound transport packet. That raw
response is preserved but rejected as substantive or factual evidence.

## Chair disposition

`ACCEPT_DESIGN_ONLY`

The v1.1 corrections close the design-level defects identified in the first
review:

- capability denials and running code identity are checked before canary
  injection rather than inferred from entitlements or a path;
- only the parent creates a new session, so the helper remains in the kill
  group;
- `RLIMIT_NPROC=0` ordering does not prevent the required parent-to-helper
  spawn;
- the durable gate is accurately named `SINK_RELEASE_DURABLE`; and
- anonymous sink-end ownership plus future bounded network-test authority are
  explicit.

## Exact claim ceiling

This accepts v1.1 only as the non-runtime contract for a later disposable,
generated-canary experiment. It proves no active App Sandbox, code-signing
enforcement, process isolation, FD containment, zeroization, controller
durability, Keychain access, provider delivery, YubiKey path, or real-secret
safety. It authorizes no helper launch.

The next separately bounded rung may create fixed protocol codecs and native
parent/helper sources with spawn disabled, then verify build/signature/
entitlement inspection deterministically. Any actual spawn, connection probe,
or canary test remains a later gate with its own receipt.

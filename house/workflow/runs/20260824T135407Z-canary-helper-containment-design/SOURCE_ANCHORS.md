# Source anchors

## Repository evidence at intake

| Source | SHA-256 | Relevance |
|---|---|---|
| `house/worker_exec/process_supervisor.py` | `67e22cf9977fb4b006a7f0cd3ae6a2785cccccf5beedd395824a3f0afb57e60f` | Generic control fixture; arbitrary argv and optional ambient environment make it ineligible for the secret-bearing path. |
| `house/worker_exec/controller.py` | `44bf2b96211344731126d1ee33b4cff64020c5b5a74b298940e047fadd9ac8fb` | Existing SQLite-fenced no-dispatch lifecycle; does not yet implement the proposed sink-release ledger. |
| `house/worker_exec/runtime_profile.py` | `b3629fcb59b8fb9c95a0bbc67c6330259f9d2733783a46e13df6e09f19ecc1e2` | Structural full-worker verifier; not helper containment or execution authority. |
| `house/worker_exec/vault_protocol_mock.py` | `6f87a1ee743b7e6315e8e78dec08f4f0c9cd7f499d4203a2f78602dc89a53500` | Accepted generated-only protocol/mock-storage predecessor. |
| `house/workflow/runs/20260823T154950Z-real-vault-threat-model/REAL_FIREWALL_VAULT_THREAT_MODEL.md` | `91aaae86e7ec4a87ced277a4402bcfbc26737b9e5bea24b16aa005b2d594a3ba` | Parent threat model and disposable implementation ladder. |

## Local platform evidence

- Host reports macOS `27.0` build `26A5388g`.
- Active SDK is `/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk`.
- SDK `usr/include/sys/spawn.h` exposes `POSIX_SPAWN_SETSID` at line 61 and
  `POSIX_SPAWN_CLOEXEC_DEFAULT` at line 62.
- SDK `usr/include/sys/resource.h` exposes `RLIMIT_CPU`, `RLIMIT_FSIZE`,
  `RLIMIT_CORE`, `RLIMIT_AS`, `RLIMIT_NPROC`, and `RLIMIT_NOFILE` at lines
  446-457.
- SDK `usr/include/sandbox.h` lines 7-9 direct developers to App Sandbox, and
  line 46 marks `sandbox_init` as no longer supported. Custom
  `sandbox_init`/Seatbelt profiles are therefore rejected as the proposed
  production mechanism.

## Official Apple design references

- [Embedding a helper tool in a sandboxed app](https://developer.apple.com/documentation/xcode/embedding-a-helper-tool-in-a-sandboxed-app)
- [Configuring the hardened runtime](https://developer.apple.com/documentation/xcode/configuring-the-hardened-runtime/)
- [Discovering and diagnosing App Sandbox violations](https://developer.apple.com/documentation/security/discovering-and-diagnosing-app-sandbox-violations)
- [Resolving common notarization issues](https://developer.apple.com/documentation/security/resolving-common-notarization-issues)
- [App Sandbox entitlement reference](https://developer.apple.com/library/archive/documentation/Miscellaneous/Reference/EntitlementKeyReference/Chapters/EnablingAppSandbox.html)

These references inform the design. Only later code-signing inspection and
runtime falsifiers can prove that the actual binary receives the intended
restrictions on this host.

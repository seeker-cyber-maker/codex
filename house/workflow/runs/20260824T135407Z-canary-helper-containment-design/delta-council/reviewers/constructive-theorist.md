# Design review: constructive-theorist

Packet SHA-256: bec0c8a1195e1ff3d3259513a9e49c4460af149c6b860777e7e5ff2fe936541f
Dispatch model/provider: cline-pass/deepseek-v4-flash / ClinePass
Reviewer self-report: blind independent expert architecture council member
Harness: provider-orchestration ClinePass OpenAI shim
System-prompt profile: council role only; otherwise unknown
Memory: unknown
Reasoning mode: unknown
Disposition: completed

## Proposed boundary

The minimum implementable architecture is the sealed parent/helper pair with a generated test coordinator, all under App Sandbox and hardened runtime, communicating over pre-opened anonymous pipes, with a controller SQLite ledger providing a durable sink-attempt gate, and a memory-only mock sink. The trusted computing base consists of: (1) the signed parent binary, (2) the embedded signed helper binary, (3) the coordinator (test-only, no ambient authority), (4) the controller SQLite store with `synchronous=FULL` and `fullfsync`, and (5) the macOS kernel’s sandbox enforcement. The delta specifically corrects: the process group structure (only parent creates a session; helper remains in parent’s group), the verification race (post-spawn dynamic code identity), the RLIMIT ordering (parent spawns helper before setting its own `RLIMIT_NPROC=0`), the pre-canary capability gate (existing-sentinel, connection, extra-FD, and spawn probes), and the release-state naming (`SINK_RELEASE_DURABLE` is a conservative gate, not a write claim). No network, Keychain, YubiKey, provider, or real secrets are touched.

## Authority-bearing facts

- **Authenticated provenance required:** The static hash, designated requirement, Team ID, and entitlement set of the parent and helper binaries must be verified before spawn.  After spawn and before canary injection, the running code objects must be authenticated via macOS dynamic code-signing APIs (CDHash/designated requirement).  A mismatch kills and reaps the process group.
- **Advisory and runtime-dependent:** The effect of App Sandbox, `RLIMIT` limits, and `posix_spawn` attributes are platform-built and runtime-specific.  They are not proven by entitlement text alone.  The pre-canary capability probes (F4–F6) provide bounded evidence of sandbox enforcement on the target host.  The controller’s durability claim (`synchronous=FULL` + `fullfsync`) is advisory until tested on the target filesystem with power-loss bounds.
- **Test-only claim:** The coordinator and observer are test harnesses with no production authority.  Their outputs are not evidence of real-secret safety.

## Contradiction handling

- **Precedence:** The protocol frames have a version, type, bounded length, operation hash, attempt nonce, and monotonically expected sequence number.  Any unknown, duplicate, reordered, oversize, partial, or trailing data causes immediate terminal failure (kill and reap) before canary injection or before a second sink write.
- **Freshness:** The coordinator uses a one-use nonce per attempt.  The controller ledger enforces monotonicity: `SINK_RELEASE_DURABLE` is committed only once per nonce.
- **Uncertainty:** If the controller’s durable gate exists but no exact terminal receipt is observed (e.g., crash, control disconnect), the conservative class is `POSSIBLE_SINK_EXPOSURE`.  No automated retry is permitted.
- **Fail behavior:** Every violation or ambiguity triggers SIGKILL of the single parent process group, reaping of both parent and helper, closure of all channels, and quarantine of the attempt.  The most conservative exposure class consistent with the last durable phase is recorded.

## Stop and human escalation

- **Machine stop conditions:**
  - Static signature/hash mismatch before spawn.
  - Post-spawn dynamic code identity mismatch.
  - Pre-canary capability probe failure (sentinel open returns `ENOENT` instead of `EPERM`

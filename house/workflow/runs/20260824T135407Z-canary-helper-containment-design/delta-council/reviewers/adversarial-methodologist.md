# Design review: adversarial-methodologist

Packet SHA-256: bec0c8a1195e1ff3d3259513a9e49c4460af149c6b860777e7e5ff2fe936541f
Dispatch model/provider: gemini-2.5-flash-lite / Google Antigravity
Reviewer self-report: blind, independent expert architecture council member
Harness: provider-orchestration Antigravity text-only OpenAI shim
System-prompt profile: council role only
Memory: disabled
Reasoning mode: unknown
Disposition: ACCEPT_DESIGN_ONLY

## Proposed boundary
The TCB comprises:
1. The **Coordinator**: An immutable runner (no ambient authority) managing the process group and monotonic state machine.
2. **Signed Artifacts**: A parent binary (App Sandbox + Hardened Runtime) and an embedded helper (Code-Sign-on-Copy) with dynamic identity verification performed post-spawn.
3. **Transport**: Three strictly typed pipes (control, canary-in, sink-out) utilizing `CLOEXEC` to prevent FD leakage.
4. **Audit Gate**: A synchronous SQLite store providing non-bypassable, nonce-bound serialization of the `SINK_RELEASE_DURABLE` event.

## Authority-bearing facts
1. **Authenticated Provenance:** CDHashes and designated requirements must be checked post-spawn via `csops` or `secCodeCheckValidity` before FD 4 (canary) is opened.
2. **Advisory Data:** The environment allowlist and `RLIMIT` configurations are strictly advisory until validated by the `F1`-`F14` falsifiers on the target production kernel.

## Contradiction handling
The hierarchy is:
1. **Freshness:** Nonce-binding ensures stale or replayed frames result in immediate termination.
2. **Uncertainty:** Any protocol ambiguity, unexpected signal, or communication loss results in a "Containment Failure" disposition—effectively a permanent quarantine of the build.
3. **Fail Behavior:** `SIGKILL` of the entire process group (enforced by `PGID` tracking) is the only acceptable termination.

## Stop and human escalation
1. **Machine Stop:** Any mismatch between expected and observed code identity, any unauthorized FD presence, or any sandbox probe failure (`EPERM` missing) triggers immediate process termination.
2. **Human Escalation:** Any `CONTAINMENT_FAILURE` requires a full audit review of the build pipeline and manual invalidation of current test nonces.

## Failure containment and recovery
1. **Containment:** Process group isolation combined with `RLIMIT_NPROC=0` prevents child-process leakage.
2. **Recovery:** No in-place recovery. The system is designed for a single-use lifecycle; post-crash, the coordinator must perform a teardown, and the audit log is archived for forensic analysis.

## Falsification experiments
1. **Sandbox Probe:** Execute `open("/restricted/path")` inside the helper before canary injection; pass = `EPERM`/`EACCES`, fail = `ENOENT` or success.
2. **Environmental Injection:** Inject `DYLD_INSERT_LIBRARIES` into the parent; fail = `posix_spawn` failure or application crash.
3. **FD Leakage:** Enumerate `proc/[pid]/fd` inside the helper; pass = only FDs 3–6 present.
4. **Group Escape:** `setsid()` attempt inside the helper; pass = failure/denial, fail = successful session transition.

## Assumptions and limitations
*   **Trust Assumptions:** Assumes the macOS kernel correctly implements `App Sandbox` and `Code-Signing` APIs as documented.
*   **Residual Risk:** Kernel-level exploits and side-channel vulnerabilities (e.g., timing analysis) are outside the scope of this containment design.
*   **Availability Costs:** The system relies on `fullfsync` and synchronized audit writes, which will introduce measurable latency in the test harness.

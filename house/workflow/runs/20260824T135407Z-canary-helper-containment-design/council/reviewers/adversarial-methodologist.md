# Design review: adversarial-methodologist

Packet SHA-256: 99ecfc7e183f4d8d40cc938c3869bc7d668b2de72930d59c86881852dfe1c819
Dispatch model/provider: gemini-2.5-flash-lite / Google Antigravity
Reviewer self-report: blind, independent expert architecture council member
Harness: provider-orchestration Antigravity text-only OpenAI shim
System-prompt profile: council role only; otherwise unknown
Memory: disabled
Reasoning mode: unknown
Disposition: REVISE_BEFORE_IMPLEMENTATION

## Proposed boundary
The TCB comprises a strictly sealed parent binary (Hardened Runtime, App Sandbox), an embedded helper (Code-Sign-on-Copy), an immutable coordinator process, and kernel-enforced anonymous pipes. All communication occurs over pre-opened FD channels validated by the coordinator before canary injection.

## Authority-bearing facts
1. **Authenticated Provenance:** The binary hash and signature of the helper *at the moment of spawning* must be validated by the parent, not merely stated in the manifest.
2. **Advisory Data:** The environment allowlist, `RLIMIT` settings, and entitlement declarations are advisory until confirmed via runtime falsifiers on the specific target platform build.

## Contradiction handling
Precedence follows a "Fail-Closed/Fail-Secure" hierarchy:
1. **Freshness:** Nonce-bound protocol frames with monotonic sequence numbers.
2. **Uncertainty:** Any ambiguity in terminal status (e.g., control disconnect during commit) maps to `POSSIBLE_SINK_EXPOSURE` and triggers mandatory quarantine.
3. **Fail behavior:** Immediate process group reaping (SIGKILL) on protocol violation or audit gate failure.

## Stop and human escalation
Machine stop conditions: Protocol violation, signature mismatch, failed audit-write/fsync, or unauthorized FD presence.
Human escalation: Any detected `CONTAINMENT_FAILURE` or `POSSIBLE_SINK_EXPOSURE` requires manual credential rotation and vault-epoch invalidation; no automated re-run is permitted.

## Failure containment and recovery
Containment: Process isolation via App Sandbox (`inherit=true`) and `RLIMIT` constraints.
Recovery: No in-place recovery for compromised helpers. Revocation is achieved via vault-epoch rotation. Audit logs (immutable) provide the basis for post-mortem forensics.

## Falsification experiments
1. **Entropy Injection (F3):** Attempt to inject `DYLD_INSERT_LIBRARIES` or `PATH` via `posix_spawn` environment; success = design failure.
2. **FD Exhaustion/Injection (F2):** Manually map unauthorized descriptors to the helper's FD table; success = design failure.
3. **Sink Hijack (F12):** Attempt to append to the mock-sink FD after the `RELEASE_ONCE` frame; success = design failure.
4. **Core Dump (F10):** Attempt to induce a crash that results in a core dump; if any file is persisted, design failure.

## Assumptions and limitations
*   **Trust Assumptions:** Assumes the macOS kernel correctly enforces `App Sandbox` and that `posix_spawn` attributes are respected.
*   **Residual Risk:** Kernel-level side channels or undocumented `dyld` behavior remain outside the TCB.
*   **Availability Costs:** High performance penalty due to `fullfsync` and synchronous durable audit gates.

---

### Highest-severity issue
The design lacks a concrete mechanism for proving that the parent has actually *entered* the intended App Sandbox profile before reading the canary; entitlements are only a request, not a state.

### Exact design section and exploit/failure sequence
**Section:** "Build, signing, and entitlement contract." 
**Failure:** A malicious or misconfigured environment might fail to apply the sandbox profile at runtime (e.g., due to local configuration errors), permitting the helper to access restricted paths while the parent believes it is fully sandboxed.

### Smallest concrete correction
Introduce a "Sandbox Proof-of-Capability" step: the helper must attempt to open a non-existent, prohibited path (e.g., a restricted system directory) and successfully log the *denial* via the control FD before the canary injection.

### Missing falsifier or acceptance gate
A falsifier that forces an "entitlement mismatch" at spawn time—specifically, a test where the binary is signed but the entitlement is absent—to confirm the parent's launch-denial logic actually works.

### Claim ceiling
The design remains a "generated-only data experiment." No claims are made regarding Keychain interaction or production-secret safety until the Sandbox Proof-of-Capability gate is verified.

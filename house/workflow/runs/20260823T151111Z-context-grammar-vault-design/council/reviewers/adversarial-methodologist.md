# Design review: adversarial-methodologist

Packet SHA-256: f41847cff7d1ba45897ae42583d7a911f4690eafa5860caa5b9bb5fff6953e69
Dispatch model/provider: gemini-2.5-flash-lite / Google Antigravity
Reviewer self-report: Independent architecture council member; expert in security boundary analysis.
Harness: provider-orchestration Antigravity text-only OpenAI shim
System-prompt profile: council role only; otherwise unknown
Memory: disabled
Reasoning mode: Chain-of-thought enabled
Disposition: ACCEPT_WITH_REQUIRED_DELTA

## Proposed boundary
The architecture establishes a **"Staged-Compiler-Verifier" (SCV)**. The TCB consists of:
1. **The Pure Verifier**: A stateless, deterministic function that ingests only the immutable ruleset, signed stage artifacts, and the observation manifest.
2. **The Vault Broker**: A standalone process controller that mediates access to the `codex-secrets` namespace, restricted by a 1:1 mapping of lease-to-sink.
3. **The Staged Producer**: A sequence of isolated, byte-budgeted transformations that normalize inputs before projection.
**Boundary condition:** No runtime, memory, or I/O state exists between stages; every stage must be cryptographically anchored to its parent's digest.

## Authority-bearing facts
*   **Provenance**: The `CodexContextRulesetV1` (versioned, signed) is the absolute root of truth.
*   **Evidence**: The observer output acts as an un-trusted *input* to the producer, which must be re-verified against the ruleset before the semantic projection stage.
*   **Vault Authority**: The ability to lease a secret is bound by the `AuthorityReceipt`—a combination of the caller's identity (worker), the task ID, and a valid unexpired TTL.

## Contradiction handling
*   **Precedence**: Explicit ruleset precedence (system > enterprise > project > session) overrides all local environment overrides.
*   **Freshness**: Every stage must validate the epoch of its observed inputs. Any detected divergence triggers `UNSTABLE_STAGE_RETRY_REQUIRED`.
*   **Fail Behavior**: The design mandates a `fail-closed` state. Any ambiguous, missing, or unauthorized key results in a non-recoverable error state, preventing partial context generation.

## Stop and human escalation
*   **Machine Stop**: Any `INCOMPLETE_*` state during production or `RULESET_SOURCE_MISMATCH` must halt the pipeline immediately.
*   **Human Escalation**: Any request for `VaultLeaseV1` that lacks an approved Capability manifest or fails multiple consecutive audit-write operations triggers a terminal lockout and requires manual intervention (operator UI ceremony).

## Failure containment and recovery
*   **Compromise**: If the Vault Broker is compromised, the `age`-encrypted storage backend remains protected by the OS keyring, limiting the blast radius to the currently active leases only.
*   **Recovery**: Revocation is mandatory on any security alert. The design must implement a "global secret epoch" reset to force re-authentication for all active leases upon detection of broker process anomaly.

## Falsification experiments
1. **The Inversion Test**: Inject a secret value into an `env` key within the `CodexContextRulesetV1` target config; confirm the verifier rejects the entire grammar generation.
2. **The Reordering Test**: Swap the execution order of Stage B and Stage C; confirm the verifier produces an `UNSTABLE_STAGE` failure.
3. **The Ghost-Lease Test**: Attempt to request a `VaultLeaseV1` without an associated `AuthorityReceipt`; confirm the broker returns `403` and logs the failed attempt to the audit trail.
4. **The Redaction Bypass**: Introduce a "nested-json" structure containing sensitive content that matches a known redaction-regex; confirm the producer triggers `INCOMPLETE_PRIVATE_TEXT` rather than letting the structure through.

## Assumptions and limitations
*   **Assumption**: The `age` encryption utility and OS keyring are correctly configured and hardened by the underlying host environment.
*   **Limitation**: The design assumes that the `host_observer` can correctly deliver binary content digests without tampering; if the observer itself is compromised, the Verifier is only as strong as the integrity of its input manifest.
*   **Delta required**: The design must explicitly mandate that `VaultRefV1` objects are stored in the same repository as the grammar files, ensuring they are subject to the same `git` audit lineage as the rulesets.

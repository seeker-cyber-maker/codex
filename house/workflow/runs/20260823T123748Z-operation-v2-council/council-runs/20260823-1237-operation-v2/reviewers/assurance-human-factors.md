# Design review: assurance-human-factors

Packet SHA-256: 6d0a55cd66389681fb0b0d6c43bec5e442f3780a985cf1b6b111841cbff50071
Dispatch model/provider: google/gemma-4-31b-it:free / OpenRouter
Reviewer self-report: independent member of expert architecture council
Harness: provider-orchestration explicit-free catalog proxy
System-prompt profile: council role only; otherwise unknown
Memory: enabled | disabled | unknown
Reasoning mode: unknown
Disposition: completed

## Proposed boundary
The architecture implements a strictly linear, non-inheriting chain of five hash-bound objects: **Task Card** $\rightarrow$ **Route Selection** $\rightarrow$ **Operation** $\rightarrow$ **Runtime Profile** $\rightarrow$ **Execution Authority**. 

The Trusted Computing Base (TCB) consists of:
1. The `prepare_operation_v2` builder (pure function).
2. The `verify_real_runtime_profile` verifier (pure function).
3. The operator-authenticated nonce generator (external to this boundary).
4. The controller transaction logic (external to this boundary).

The boundary is defined by the requirement that no object may mint the authority of the next; for example, a verified Runtime Profile does not grant a lease or a provider call.

## Authority-bearing facts
- **Authenticated Provenance (Required):** Route Selection records, Runtime Profile qualification evidence, and the Execution Authority nonce.
- **Advisory Data:** Task Card `requested_recipient` fields and any human-provided "preferences" within the task card. These may trigger a Route Selection but cannot appear in the final `argv` unless mirrored in a verified Route Selection record.

## Contradiction handling
- **Precedence:** Route Selection $\succ$ Task Card. Operation $\succ$ Route Selection. Runtime Profile $\succ$ Operation.
- **Freshness:** All records must be bound to a specific epoch/deadline; stale account fingerprints or expired Route Selections trigger immediate refusal.
- **Uncertainty:** Any "default", "auto", or "wildcard" identity in a Route Selection or Profile results in a `RuntimeProfileError` (fail-closed).
- **Fail Behavior:** Any hash mismatch or capability drift (e.g., an unlisted MCP server appearing in the runtime capture) results in a hard stop before the Execution Authority is consumed.

## Stop and human escalation
- **Machine Stop Conditions:** 
    - Mismatch between `argv` and Route Selection.
    - Detection of enabled hooks/Apps in a profile where the operation demanded isolation.
    - Absence or reuse of the single-use authority nonce.
- **Human Adjudication:** Bounded to the "Route Selection" phase (manual model choice) and the "Execution Authority" phase (operator authentication). The machine cannot "escalate" to bypass a hash mismatch.

## Failure containment and recovery
- **Component Compromise:** Compromise of the Operation record is mitigated by the requirement that it must match the Runtime Profile and be signed by a separate Execution Authority nonce.
- **Revocation:** Revocation is achieved by expiring the lease epoch or invalidating the account fingerprint in the qualification provider.
- **Recovery:** Preparation is idempotent. Recovery from interruption requires reconciling the existing intent/lease via the controller; replacement operations under the same key are prohibited.
- **Audit:** Full worker logs (stdout/stderr/last-message) are preserved; `--ephemeral` is prohibited to ensure provenance.

## Falsification experiments
1. **Route-to-Argv Drift:** Modify the `model_identity` in a Route Selection record after the Operation is sealed. **Pass:** `verify_operation` or `verify_real_runtime_profile` fails.
2. **Capability Leak:** Inject a `.codex/config.toml` into the workspace of an A-strategy runtime. **Pass:** Runtime capture identifies an unlisted capability and refuses admission.
3. **Authority Bypass:** Attempt to trigger `execute_for_test` (or a real runner) using a verified Runtime Profile but without a valid Execution Authority nonce. **Pass:** Dispatch is blocked.
4. **Task-Card Influence:** Change the `requested_recipient` in the Task Card while keeping the Route Selection constant. **Pass:** `argv` remains unchanged, but the Operation hash changes, requiring a new binding.

## Assumptions and limitations
- **Trust Assumptions:** Assumes the `codex exec` CLI flags (`--ignore-user-config`, `--ignore-rules`) behave as documented and that the internal `ignore_project_config` can be reliably exposed or simulated.
- **Residual Risks:** The "Credential Projection" mechanism is outside this boundary; the design assumes a separate, secure gate for token injection into `CODEX_HOME`.
- **Availability Costs:** High overhead due to the requirement for independent qualification of every runtime profile, preventing "instant" dispatch.

**Decision: ACCEPT_DESIGN**
The design successfully decouples intent (Task Card) from execution parameters (Route Selection) and runtime reality (Profile), eliminating the authority conflation found in v1.

**Smallest safe first implementation slice:**
Implement the `Route Selection` record schema and the `prepare_operation_v2` builder as a pure function that accepts a `verified_route_selection` and produces the sealed `Operation` record, without implementing the runner or the credential capsule.

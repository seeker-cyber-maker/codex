# Design review: security-architect

Packet SHA-256: 6d0a55cd66389681fb0b0d6c43bec5e442f3780a985cf1b6b111841cbff50071  
Dispatch model/provider: cline-pass/deepseek-v4-flash / ClinePass  
Reviewer self-report: independent council member  
Harness: provider-orchestration ClinePass OpenAI shim  
System-prompt profile: council role only; otherwise unknown  
Memory: unknown  
Reasoning mode: unknown  
Disposition: completed  

## Proposed boundary

The minimum implementable architecture separates five object types, each hash-bound and each incapable of minting the next object’s authority:

1. **Task card** – human intent, content, acceptance, advisory recipient class/id. No execution authority.  
2. **Route selection** – a no-dispatch record binding a task-card hash to one explicit model/provider/account/usage-pool tuple, with expiry and evidence hash. No lease or provider call.  
3. **Operation** – immutable record consuming task card and one verified route selection, sealing exact argv, executable, workspace, output bounds, isolation policy, resource budget. No directories, credentials, or processes created.  
4. **Runtime profile** – independently observed effective runtime state (executable, config, account, filesystem, roots, output reservation). Must agree exactly with operation and route selection. No dispatch authority.  
5. **Execution authority** – future single-use, operator-authenticated nonce bound to operation hash, runtime-profile hash, lease epoch, deadline, and external-effect class. Only a separate controller transaction may consume it.

The trusted computing base (TCB) for the first implementation slice is:  
- The operation builder (pure, deterministic, no I/O beyond reading inputs).  
- The runtime-profile verifier (pure, structural, no I/O).  
- The route-selection record (produced by a human or an independently reviewed deterministic router).  
- The task-card schema and its snapshot validation.  

No credential capsule, controller, launcher, or provider contact is included in this TCB.

## Authority-bearing facts

The following facts require authenticated provenance (cryptographic binding or independent witness) and cannot be advisory:

- Route-selection record: field `selection_evidence_sha256` must link to a signed or hash-linked evidence bundle from an independent qualification process.  
- Runtime profile: fields `executable.sha256`, `cli_capture_sha256`, `workspace.identity_sha256`, `output.reservation_evidence_sha256`, `config_hooks.evidence_sha256`, `filesystem.trace_sha256`, `provider.identity`, `provider.account_id`, `provider.usage_pool_id`, `qualification_evidence.issuer`, `qualification_evidence.evidence_bundle_sha256`.  
- Operation: `input_hashes.codex_sha256` (binary hash), `input_hashes.argv_sha256`, `authority_scope.read`, `authority_scope.write`.  

Advisory data (no authority):  
- Task-card `requested_recipient` and `requested_recipient_id` (advisory, cannot override route selection).  
- Ambient config, auth, rate-limit observations (must be superseded by qualified profile).  

## Contradiction handling

Precedence:  
- Route selection overrides task-card recipient. Record mismatch, do not silently accept.  
- Operation argv derived from route selection, not from task-card fields.  
- Runtime profile takes precedence over operation’s `start_state` and ambient config.  
- Managed policy may narrow but never widen operation capabilities.  

Freshness:  
- Route selection has explicit `expires_at`. Expired selection must be re-qualified.  
- Runtime profile has `observed_at`; must be within a system-defined staleness window (not yet defined; must be added).  
- Account/pool/egress changes after selection or qualification: expire and requalify; never substitute.  

Uncertainty:  
- If the effective runtime capture reveals an unlisted capability, admission stops with a gap receipt.  
- If credential descriptor absent, stop before lease or intent.  
- If authority nonce absent, expired, reused, or bound to wrong hash/epoch, stop with no fallback.  

Fail behavior:  
- All verification functions raise `WorkerExecError` or `RuntimeProfileError` on mismatch.  
- No silent stripping, defaulting, or fallback.  
- Worker/model prose cannot change operation state or admit results.  

## Stop and human escalation

Machine stop conditions (must halt before any side effect):  
- Route selection conflicts with task-card recipient (record mismatch, require human resolution).  
- Route selection expired or missing.  
- Operation argv mismatch with route selection.  
- Runtime profile binding mismatch with operation.  
- Effective runtime capture reveals an unlisted capability.  
- Credential descriptor absent or invalid.  
- Authority nonce absent, expired, reused, or bound to wrong hash/epoch.  
- Output reservation already exists or source/config hash drifts.  

Bounded human adjudication:  
- A human operator may explicitly select a route (recorded in `selection_source: "human-manual"`).  
- Human may resolve a task-card/route-selection mismatch by updating one of the records.  
- Human may approve a new route selection or a new runtime profile.  
- No human can override the stop conditions to proceed with a non-conforming operation.  

## Failure containment and recovery

Component compromise:  
- Operation builder is pure and stateless; compromise produces only invalid records that fail verification.  
- Runtime-profile verifier is pure; compromise cannot affect dispatch because it does not create leases or intents.  
- Route selection is a record, not a process; compromise of the router leaks only advisory data.  
- Credential capsule (future) is the only component that holds secrets; it must be isolated, ephemeral, and audited.  

Revocation:  
- Route selection expiry renders it unusable.  
- Runtime profile staleness requires re-qualification.  
- Authority nonce is single-use and bound to a lease epoch; reuse is detected and stops.  

Recovery:  
- Preparation is idempotent: identical inputs produce identical records.  
- Controller uses idempotency binding over intent, task-card hash, route hash, operation hash, runtime-profile hash, authority hash, target, scope.  
- After interruption, reconcile existing intent and lease; never start a replacement operation under the same key.  

Audit:  
- Full worker logs and provenance must be preserved (no `--ephemeral`).  
- All verification receipts and gap receipts are recorded.  
- Credential capsule creation and cleanup must produce reconciliation receipts.  

## Falsification experiments

1. **Model isolation test**: Mutate the model field in the route-selection record. Verify that the operation argv changes accordingly and that the runtime profile verifier rejects a mismatch.  
   *Pass criteria:* Operation builder produces different argv; verifier fails with `RuntimeProfileError`.  
   *Fail:* The model field is ignored or the verifier accepts mismatch.

2. **Task-card advisory override test**: Change the task-card `requested_recipient` to a different model. Verify that the operation argv remains unchanged (determined by route selection) and that the mismatch is recorded.  
   *Pass criteria:* Operation argv unchanged; contradiction record produced.  
   *Fail:* Operation argv changes or mismatch is silently accepted.

3. **Project config isolation test**: Place a `.codex/config.toml` with a dangerous capability in the workspace. For Strategy A (upstream flag), verify that the operation argv includes `--ignore-project-config` (or equivalent) and that the runtime profile verifier checks for the flag. For Strategy B, verify that the project config appears in the content inventory and is explicitly admitted.  
   *Pass criteria:* The config is either ignored (A) or inventoried (B); the runtime profile verifier enforces the strategy.  
   *Fail:* The config enters the runtime without being accounted for.

4. **Managed policy narrowing test**: Supply a managed layer that narrows permissions (e.g., reduces wall time). Verify that the operation is accepted. Then supply a managed layer that adds an unlisted capability (e.g., enables a new MCP server). Verify that admission stops with a gap receipt.  
   *Pass criteria:* Narrowing succeeds; widening fails.  
   *Fail:* Widening is silently accepted or narrowing is rejected.

5. **No-side-effect test**: Run `prepare_operation_v2` and `verify_real

# Design review: security-architect

Packet SHA-256: 36d0742c83fce26019692d81ff77295aedad189de04effb90417e86cd265167a
Dispatch model/provider: cline-pass/deepseek-v4-flash / ClinePass
Reviewer self-report: security-architect
Harness: provider-orchestration ClinePass OpenAI shim
System-prompt profile: council role only; otherwise unknown
Memory: disabled
Reasoning mode: unknown
Disposition: ACCEPT_DELTA

## Proposed boundary
The minimum implementable architecture after D1–D7:

- **LocalContextFirewallV1** (new, secrecy TCB): bounded read + strict parse of raw structured configuration. Raw bytes remain memory-local, never journaled, logged, returned as tool output, or sent to model/cloud lane. Produces safe semantic projection (allowlisted keys per classification). Requires audited implementation, disabled diagnostics/core dumps, bounded memory lifetime, zero network/process/extension capability.
- **ContextGrammarCompilerV1** (pure): receives only the allowlisted projection. No raw bytes, no vault access. Produces finite grammar.
- **HostObserverV1** (existing): runs only after firewall/admission success. Returns presence/type/bytes/digest. Content SHA-256 must match admitted expected digest. No semantic interpretation.
- **PureContextVerifierV1** (I/O-free): checks output shape, lineage, consistency. Cannot detect compromised parser leakage – that property depends on the firewall’s isolation.
- **Vault broker** (separate authority): policy/lease front end with no storage key; minimal resolver with no network/model/logging; independently keyed namespaces; sink adapter for one resolved value per lease.

**Trusted Computing Base:** firewall binary, verifier binary, host observer binary at pinned commit, sealed ruleset. The grammar compiler is not in the secrecy TCB because its input is already filtered.

## Authority-bearing facts
- Source file SHA-256 hashes at the pinned commit referenced by the ruleset.
- Ruleset classification table (per-key projection class) and stage graph.
- Observer implementation digest and observation policy digest.
- Content digests returned by observer for all admitted candidates.

**Advisory data (not authoritative):** live Codex behavior, installed app configuration, later upstream revisions, any claim not backed by pinned source hash.

## Contradiction handling
- **Precedence:** Sealed ruleset classification is the single source of truth for projection. Source defines existence, ruleset defines projection policy. Any unclassified key → `INCOMPLETE_UNKNOWN_KEY` → halt.
- **Freshness:** Every stage binding includes source epochs and content digests. Verifier rejects any artifact where a contributor’s final digest differs from its stage digest. Any change → `UNSTABLE_STAGE_RETRY_REQUIRED` → restart from earliest affected stage.
- **Uncertainty:** All `INCOMPLETE_*` states and `RULESET_SOURCE_MISMATCH` fail closed. No grammar produced, no downstream authority issued.
- **Fail behavior:** All contradictions halt the pipeline. No silent drops, no best-effort continuation.

## Stop and human escalation
**Machine stop (automatic, no human in loop):**
- Any `INCOMPLETE_*`, `RULESET_SOURCE_MISMATCH`, `UNSTABLE_STAGE_RETRY_REQUIRED`, `VAULT_REFERENCE_PRESENT_NOT_RESOLVED`.
- Observer returns internally consistent false bytes/digests (verifier must not label observation authenticated).
- Post-injection audit failure must terminate target and mark reference rotation-required.
- Any attempt to inject secret into agent-controlled shell, arbitrary command, or model-visible tool.

**Bounded human adjudication:**
- New ruleset version requires new council disposition.
- New source commit requires re-pinning and re-verification.
- New classification for unclassified key requires ruleset update and council review.
- Vault broker implementation requires separate authority gate and independent security review.

## Failure containment and recovery
- **Firewall compromise:** Raw bytes leaked only if firewall also bypasses its own restrictions (no logging, no network, no crash artifacts). Compromise contained to the firewall process; verifier cannot detect parser-side channel. Mitigation: audited implementation, zero capability.
- **Grammar compiler compromise:** Output verified by pure verifier; no ability to issue leases or resolve secrets.
- **Host observer compromise:** Can lie about digests; verifier detects mismatch. Cannot initiate observation requests. Observer/host boundary is TCB.
- **Pure verifier compromise:** Catastrophic for secrecy. Mitigation: minimal I/O-free binary, independently reviewed and signed, source pinned.
- **Vault broker compromise:** Front end alone lacks storage key. Resolver compromise in one namespace may expose all secrets in that namespace. Global vault epoch invalidates leases but cannot retract already delivered values. Namespace rotation and credential rotation are separate recovery operations.
- **Lease consumption failure:** Pre-injection failure exposes nothing. Post-injection failure kills/quarantines consumer, revokes lease, records incident, requires secret rotation.

## Falsification experiments
1. **Firewall leakage test:** Give firewall a synthetic config containing a low-entropy secret. No raw value or whole-file hash may appear in stdout, stderr, logs, crash artifacts, projection, or council packet. (Delta falsifier 1)  
   *Pass:* No leakage detectable.  
   *Fail:* Any raw value or digest escapes.

2. **Observer authenticity test:** Make observer return internally consistent false bytes/digests that match each other but differ from disk content. Verifier must not label observation authenticated. (Delta falsifier 2)  
   *Pass:* Verifier rejects or reports `UNSTABLE_STAGE_RETRY_REQUIRED`.  
   *Fail:* Verifier accepts grammar as authenticated.

3. **Launch TOCTOU test:** Mutate a verified path before launch. A path-reopen launch must fail; an already-bound immutable object (content-addressed copy or inherited FD) must remain unchanged. (Delta falsifier 3)  
   *Pass:* Path-reopen fails; immutable-bound succeeds with original content.  
   *Fail:* Path-reopen succeeds with mutated content or immutable-bound fails.

4. **Lease front-end isolation test:** Compromise the lease front end alone. It must lack storage-key access. (Delta falsifier 4)  
   *Pass:* Front end cannot decrypt stored secrets.  
   *Fail:* Front end can read plaintext values.

5. **Resolver namespace exposure test:** Compromise the resolver in a test namespace. The claim ledger must classify the whole namespace as exposed. (Delta falsifier 5)  
   *Pass:* Ledger marks namespace as exposed; all secrets in that namespace require rotation.  
   *Fail:* Ledger shows only the compromised lease as exposed.

6. **Post-injection audit failure test:** Cause post-injection audit write to fail. The target must be terminated and the reference marked rotation-required. (Delta falsifier 6)  
   *Pass:* Target terminated, lease revoked, incident recorded.  
   *Fail:* Target continues with secret, lease not revoked.

7. **Agent-controlled sink rejection test:** Ask an agent-controlled shell to receive a secret environment variable. The broker must reject the sink even with a valid reference. (Delta falsifier 7)  
   *Pass:* Broker returns error; no secret delivered.  
   *Fail:* Secret delivered to shell.

8. **Cloud projection leak test:** Create a config where a `PUBLIC_LOCATOR` field contains an absolute path with a user name. Cloud projection must strip it.  
   *Pass:* Cloud artifact contains root-relative or opaque locator ID only.  
   *Fail:* Absolute path or user name appears.

## Assumptions and limitations
**Trust assumptions:**
- `LocalContextFirewallV1` is correctly implemented and audited; it does not leak via side channels (timing, memory corruption, crash artifacts).
- The host observer binary at the pinned commit correctly returns digests without tampering.
- The pure verifier binary is correctly implemented and free of ambient I/O.
- The pinned ruleset classification is complete and correct for all config keys at the pinned commit.
- Immutable launch binding (content-addressed copies or already-verified FDs) is actually enforced by the runtime launcher.

**Residual risks:**
- Side-channel leakage from firewall (e.g., timing of parse failures) is not addressed.
- Crash reports or core dumps from the firewall could leak raw bytes even with disabled diagnostics; the design assumes diagnostics are fully disabled.
- The pure verifier cannot detect a compromised firewall that leaks during parsing. This is a fundamental TCB reliance.
- At-rest encryption does not protect a secret from a running resolver that holds the decryption key.
- Global vault epoch revocation cannot retract a value already delivered to a consumer.
- The design requires all secrets to be migrated to vault references; literal secrets in config are rejected until migration.

**Availability costs:**
- Any source change requires full re-derivation from earliest affected stage.
- Strict classification gaps cause halts, requiring ruleset updates.
- Dynamic sources not reducible to finite locators are unsupported.
- No incremental update path; every change is a full re-derivation.

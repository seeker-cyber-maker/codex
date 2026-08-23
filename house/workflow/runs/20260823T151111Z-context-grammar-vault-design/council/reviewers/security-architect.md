# Design review: security-architect

Packet SHA-256: f41847cff7d1ba45897ae42583d7a911f4690eafa5860caa5b9bb5fff6953e69
Dispatch model/provider: cline-pass/deepseek-v4-flash / ClinePass
Reviewer self-report: security-architect
Harness: provider-orchestration ClinePass OpenAI shim
System-prompt profile: council role only; otherwise unknown
Memory: disabled
Reasoning mode: unknown
Disposition: completed

## Proposed boundary

The minimum implementable architecture is a **three-authority fail-closed pipeline** with no shared mutable state between stages:

1. **Grammar Producer** (pure compiler, no I/O except reading its sealed ruleset and staged observation responses): accepts a `CodexContextRulesetV1`, a platform profile, a Codex-home locator, session overrides, and cwd facts. Emits observation requests to the Host Observer. Receives back only presence/type/bytes/digest evidence. Produces a `CodexContextGrammarV1` containing only `BEHAVIOR_VALUE`, `PUBLIC_LOCATOR`, `SECRET_REFERENCE` (opaque ref ID only), `SENSITIVE_PRESENCE_ONLY`, and `PUBLIC_CONTENT_ADDRESSABLE` fields. Never reads secrets, environment variables, keychain, or network.

2. **Host Observer** (existing, unchanged): accepts a finite candidate list from the producer, returns presence/type/bytes/digest for each candidate. No semantic interpretation. No secret resolution.

3. **Pure Verifier** (no filesystem, clock, environment, process, network, keychain, vault, or random I/O): accepts the sealed ruleset, the staged request/response bindings, and the final grammar. Checks canonical serialization, source identity, stage DAG completeness, candidate ordering, epoch consistency, content digest continuity, projection classification compliance, and terminal state. Rejects any artifact containing a `SECRET_REFERENCE` value, `SENSITIVE_PRESENCE_ONLY` value, unclassified key, or private text.

**Trusted Computing Base (TCB):** The sealed ruleset (source hashes, classification schema, stage graph), the pure verifier binary, and the host observer binary at the pinned commit. The grammar producer is *not* in the TCB for secrecy—its output is verified by the pure verifier before any downstream consumption. The vault broker is a separate future authority not in this phase's TCB.

## Authority-bearing facts

| Fact | Provenance | Authentication |
|---|---|---|
| Source file SHA-256 hashes at commit `fbbf52145707bb50f7795ca2e8584b8785514199` | Pinned repository, SOURCE_ANCHORS.md | Byte-identity verified by reviewer against pinned commit |
| Loader precedence order (managed/non-project → root/trust → project root-to-cwd → session → managed) | `codex-rs/config/src/loader/mod.rs` at pinned commit | Source hash match |
| Config schema keys and types | `codex-rs/config/src/config_toml.rs`, `types.rs`, `mcp_types.rs` at pinned commit | Source hash match |
| Existing secrets API surface (list/set/get/delete, namespaces, age encryption, OS keyring) | `codex-rs/secrets/src/lib.rs`, `local.rs` at pinned commit | Source hash match |
| Regex redaction is best-effort, not a secrecy proof | `codex-rs/secrets/src/sanitizer.rs` at pinned commit | Source hash match |
| MCP config may contain literal env values and bearer tokens | `codex-rs/config/src/mcp_types.rs` at pinned commit | Source hash match |
| Instruction discovery is config-dependent and byte-budgeted | `codex-rs/core/src/agents_md.rs` at pinned commit | Source hash match |

**Advisory data (no authenticated provenance, must not be treated as authority):** Any claim about installed Codex behavior, desktop app behavior, later upstream revisions, or live configuration. The design explicitly disclaims these.

## Contradiction handling

**Precedence:** The sealed ruleset's classification table (Section 5 of the contract) is the single source of truth for projection decisions. If a source file at the pinned commit defines a key that the ruleset classifies as `DENY`, the ruleset wins—the source defines existence, the ruleset defines projection policy. If the ruleset omits a key present in the source, the producer emits `INCOMPLETE_UNKNOWN_KEY` and stops.

**Freshness:** Every stage binding includes source epochs and content digests returned by the observer. The verifier rejects any artifact where a contributor's final digest differs from its stage digest. Any source change yields `UNSTABLE_STAGE_RETRY_REQUIRED`; the system restarts from the earliest affected stage. There is no incremental patching.

**Uncertainty:** Dynamic contributors not reducible to a finite locator set yield `INCOMPLETE_DYNAMIC_SOURCE`. Unclassified keys yield `INCOMPLETE_UNKNOWN_KEY`. Private arbitrary text yields `INCOMPLETE_PRIVATE_TEXT`. Secret references present but not resolved yield `VAULT_REFERENCE_PRESENT_NOT_RESOLVED`. None of these states qualifies a runtime.

**Fail behavior:** All contradictions fail closed. The producer emits a terminal error state. No grammar is produced. No downstream authority is issued. The pure verifier rejects any artifact that does not match the sealed ruleset and stage bindings exactly.

## Stop and human escalation

**Machine stop conditions (automatic, no human in loop):**
1. Any source hash mismatch → `RULESET_SOURCE_MISMATCH` → halt.
2. Any unclassified key → `INCOMPLETE_UNKNOWN_KEY` → halt.
3. Any private text in a non-content-addressable field → `INCOMPLETE_PRIVATE_TEXT` → halt.
4. Any dynamic source not reducible to finite locators → `INCOMPLETE_DYNAMIC_SOURCE` → halt.
5. Any cross-stage epoch or digest mismatch → `UNSTABLE_STAGE_RETRY_REQUIRED` → halt.
6. Any `SECRET_REFERENCE` field containing a value or value-derived digest → halt.
7. Any `SENSITIVE_PRESENCE_ONLY` field containing a value → halt.
8. Pure verifier detects any ambient API call (filesystem, clock, network, etc.) → halt.

**Bounded human adjudication (only for pre-authorized, pre-specified decisions):**
- A new ruleset version requires a new council disposition. No automatic compatibility inference.
- A new source commit requires re-pinning and re-verification of all source hashes.
- A new classification for a previously unclassified key requires a ruleset update and council review.
- Vault broker implementation requires a separate authority gate and independent security review.

## Failure containment and recovery

**Component compromise:**
- **Grammar producer compromise:** The pure verifier rejects any output that violates the ruleset, stage bindings, or projection classifications. The producer has no authority to issue leases, resolve secrets, or launch processes. Compromise is contained to producing invalid grammars that are caught before consumption.
- **Host observer compromise:** The observer returns only presence/type/bytes/digest for explicitly requested candidates. It cannot initiate observation requests. Compromise could return incorrect digests, which the verifier detects as epoch/digest mismatch.
- **Pure verifier compromise:** The verifier is the TCB for secrecy. Its compromise is catastrophic. Mitigation: the verifier is a minimal, auditable binary with no I/O capabilities. It must be independently reviewed and signed. Its source must be pinned and hashed.

**Revocation:** Not applicable in this design-only phase. The vault broker (future phase) will have revocation mechanisms. For this phase, revocation of the design itself means discarding the sealed ruleset and re-deriving from a new commit.

**Recovery:** Any failure state requires restarting from the earliest affected stage. The system never patches or hot-fixes a stage binding. Recovery is always a full re-derivation.

**Audit:** The pure verifier's acceptance/rejection decisions are logged with full stage bindings. No secrets, values, or value-derived digests enter the audit log. The audit log is append-only and independently verifiable.

## Falsification experiments

**Experiment 1: Secret value in grammar output**
- **Setup:** Create a ruleset that classifies a key as `BEHAVIOR_VALUE`. Create a source file at the pinned commit where that key's value is a literal bearer token. Run the grammar producer with a host observer that returns the token as the value.
- **Pass criterion:** The pure verifier rejects the grammar because the token is not a `BEHAVIOR_VALUE` under the ruleset's classification (the ruleset must classify bearer token fields as `DENY` or `SECRET_REFERENCE`).
- **Fail criterion:** The verifier accepts the grammar containing the token.

**Experiment 2: Cross-stage mutation**
- **Setup:** Run the producer through Stage A-D with consistent source epochs. Before Stage E, modify one source file on disk (simulating a race). Run Stage E.
- **Pass criterion:** The verifier detects the epoch/digest mismatch and emits `UNSTABLE_STAGE_RETRY_REQUIRED`.
- **Fail criterion:** The verifier accepts the grammar with the mutated source.

**Experiment 3: Unclassified key injection**
- **Setup:** Add a new key to a config file that is not in the ruleset's classification table. Run the producer.
- **Pass criterion:** The producer emits `INCOMPLETE_UNKNOWN_KEY` and halts.
- **Fail criterion:** The producer silently drops the key or includes it in the grammar.

**Experiment 4: Private text in content-addressable field**
- **Setup:** Create a Markdown file containing a private key. Reference it in a `PUBLIC_CONTENT_ADDRESSABLE` field without a pre-sealed expected digest. Run the producer.
- **Pass criterion:** The producer emits `INCOMPLETE_PRIVATE_TEXT` and halts.
- **Fail criterion:** The producer includes the private text in the grammar.

**Experiment 5: Pure verifier ambient I/O**
- **Setup:** Modify the pure verifier to attempt a filesystem read, network call, or clock read. Run it with any valid input.
- **Pass criterion:** The verifier crashes or returns an error (no ambient I/O capability).
- **Fail criterion:** The verifier successfully performs ambient I/O and returns a result.

**Experiment 6: Cloud projection leak**
- **Setup:** Create a ruleset and source where a `PUBLIC_LOCATOR` field contains an absolute path containing a user name. Run the cloud projection.
- **Pass criterion:** The cloud projection removes the absolute path and user name, replacing with a root-relative or opaque locator ID.
- **Fail criterion:** The cloud projection contains the absolute path or user name.

**Experiment 7: Vault reference value leak**
- **Setup:** Create a `SECRET_REFERENCE` field where the producer attempts to include the reference label or a value-derived digest. Run the producer.
- **Pass criterion:** The producer emits only the opaque ref ID, scope, required sink, and revision. The verifier rejects any grammar containing a label or digest.
- **Fail criterion:** The grammar contains a label or value-derived digest.

## Assumptions and limitations

**Trust assumptions:**
1. The pinned source commit `fbbf52145707bb50f7795ca2e8584b8785514199` is correct and uncompromised. If the commit is malicious, the entire design is compromised.
2. The pure verifier binary is correctly implemented and not compromised. This is the single point of failure for secrecy.
3. The host observer binary at the pinned commit correctly returns presence/type/bytes/digest without side effects.
4. The sealed ruleset's classification table is complete and correct for all config keys at the pinned commit.
5. No installed Codex app, desktop app, or later upstream revision is in use during this design phase.

**Residual risks:**
1. **Side-channel leakage:** The grammar producer's observation requests reveal which files exist and their sizes. This is metadata, not secret values, but could be used in combination with other information.
2. **Timing attacks:** The producer's stage duration could reveal information about config structure. Not addressed in this design.
3. **Crash report exfiltration:** If the producer or verifier crashes, a crash report might contain stage bindings or candidate lists. The design explicitly excludes values from crash reports, but metadata could leak.
4. **Child-process exfiltration:** Not applicable in this design-only phase. The vault broker (future phase) must address this.
5. **Regex redaction is not a secrecy proof:** The design correctly does not rely on redaction for secrecy, but defense-in-depth redaction for display purposes is not evaluated here.

**Availability costs:**
1. Any source change requires a full re-derivation from the earliest affected stage. This is expensive for large configs.
2. The pure verifier's strict checks may reject valid configs due to classification gaps, requiring ruleset updates.
3. Dynamic sources are not supported unless reducible to finite locators. This may limit some plugin/MCP configurations.
4. The design has no incremental update path. Every change is a full re-derivation.

We are given a transport packet with SHA-256: 36d0742c83fce26019692d81ff77295aedad189de04effb90417e86cd265167a
 We are to return a design review for the evidence-auditor.

 The packet contains:
   - Original evidence packet: house/workflow/runs/20260823T151111Z-context-grammar-vault-design/DELTA_REVIEW_PACKET.md
   - Original packet SHA-256: b849e9396480fbfb742a36cc5a45e7def3c3baeb7a19c4f62facf9bab4f72140

 We are to review the delta (ROOT_DESIGN_DELTA.md) and decide whether it repairs the material trust and implementability defects without widening live authority.

 The deliverable must be one of: ACCEPT_DELTA, ACCEPT_WITH_REQUIRED_DELTA, or REJECT_DELTA, with one smallest decisive correction or falsifier.

 We are to act as an independent member of the expert architecture council.

 Steps:
 1. We must not ask the chair to supply an architecture; we create the minimum architecture.
 2. We treat the conditions as assumptions, not proof that a defense works.
 3. We name trust assumptions, concrete failure behavior, and experiments that could falsify the proposal.
 4. We do not infer that other reviewers agree, reveal hidden chain-of-thought, or add an engagement-driven follow-up question.
 5. We concentrate on provenance and the boundary between measured evidence and narrative.

 We are to return exactly the response contract, replacing placeholders.

 The response contract is:

 # Design review: evidence-auditor

 Packet SHA-256: 36d0742c83fce26019692d81ff77295aedad189de04effb90417e86cd265167a
 Dispatch model/provider: nvidia/nemotron-3-super-120b-a12b:free / OpenRouter
 Reviewer self-report: <exact claim or unknown>
 Harness: provider-orchestration explicit-free catalog proxy
 System-prompt profile: council role only; otherwise unknown
 Memory: enabled | disabled | unknown
 Reasoning mode: <exact or unknown>
 Disposition: completed | partial | refused | timed-out | failed

 ## Proposed boundary
 <minimum implementable architecture and trusted computing base>

 ## Authority-bearing facts
 <facts requiring authenticated provenance versus advisory data>

 ## Contradiction handling
 <precedence, freshness, uncertainty, and fail behavior>

 ## Stop and human escalation
 <machine stop conditions and bounded human adjudication>

 ## Failure containment and recovery
 <component compromise, revocation, recovery, and audit>

 ## Falsification experiments
 <bounded experiments with explicit pass/fail criteria that could disprove the design claims>

 ## Assumptions and limitations
 <trust assumptions, residual risks, and availability costs>

 We are to fill in the placeholders.

 Given the evidence, we are reviewing the delta (ROOT_DESIGN_DELTA.md) for the context-grammar/vault design.

 Let's analyze the delta:

 The delta (ROOT_DESIGN_DELTA.md) proposes several changes (D1-D7) and added falsifiers.

 We must check if the delta repairs the material trust and implementability defects in the original design without widening live authority.

 From the original evidence packet, the decision question is:
   Does `ROOT_DESIGN_DELTA.md` repair the material trust and implementability defects in the original context-grammar/vault design without widening live authority?

 We are to return a verdict.

 Let's consider the original design (from the contract) and the delta.

 The original design (CONTEXT_GRAMMAR_AND_VAULT_CONTRACT.md) had a design that the reviewers (security-architect and adversarial-methodologist) had reviewed.

 The security-architect review (attached as evidence 3) proposed a three-authority fail-closed pipeline.

 The adversarial-methodologist (evidence 4) recommended ACCEPT_WITH_REQUIRED_DELTA and required that VaultRefV1 objects are stored in the same repository as the grammar files.

 Now, the delta (ROOT_DESIGN_DELTA.md) is the candidate change under review.

 We must check the delta against the required review focus:

   - Is the local firewall/compiler split implementable with the existing observer?
   - Are the firewall, observer, verifier, broker front end, resolver, and sink TCB claims honest?
   - Does the delta correctly state broker-compromise and revocation ceilings?
   - Can an agent-controlled process still obtain or print plaintext?
   - Is immutable launch binding sufficient to close observation/use TOCTOU?

 Let's go through the delta:

 D1: Split the runtime projector from the grammar compiler.
   - This addresses the issue that the existing host observer returns only metadata and SHA-256, not file contents.
   - It introduces a new component: LocalContextFirewallV1 (bounded read + strict parse, secrecy TCB) that does the staged candidate expansion and produces a safe semantic projection.
   - The grammar compiler becomes pure and only gets the allowlisted semantic projection.

 D2: Secret-bearing and arbitrary content admission.
   - It says that literal secret fields yield INCOMPLETE_SECRET_DEPENDENCY and require migration to a vault reference.
   - Free-form content requires an independently signed content-admission receipt to be admitted, otherwise INCOMPLETE_PRIVATE_TEXT.

 D3: Observation authenticity and launch TOCTOU.
   - It states that observer epochs and digests provide consistency, not authenticity.
   - It requires runtime qualification to pin and authenticate the observer executable and treat the observer/host boundary as TCB.
   - It requires that a future launcher must consume immutable content-addressed copies or already-verified open file descriptors, then bind those exact objects to the operation receipt.

 D4: Vault compromise ceiling.
   - It separates the policy/lease front end (no storage key) from a minimal resolver (no network/model/logging capability) and independently keyed namespaces.
   - A global vault epoch invalidates all leases during an incident but does not erase an already disclosed value.

 D5: Trusted sinks, atomic consumption, and revocation.
   - It describes a transactional lease consumption process and states that revocation prevents future use but cannot retract a value already delivered.

 D6: Vault references and Git.
   - It says that repository policy may declare a task needs an opaque ref_id, sink class, and scope class, and the authoritative mapping remains local vault state (not required to be in Git).
   - It rejects storing VaultRefV1 objects beside grammar files.

 D7: Corrected source precedence.
   - It reproduces the pinned Codex loader precedence and says that any reviewer statement to the contrary is non-authoritative.

 Added falsifiers: 7 items.

 Now, we must decide: does this delta repair the defects without widening live authority?

 Let's consider the required review focus:

 1. Local firewall/compiler split implementable with existing observer?
    - The delta introduces a firewall that does the staged candidate expansion and then the compiler is pure. The existing observer is used after the firewall and compiler, and it only returns metadata and digest. This seems implementable.

 2. Are the TCB claims honest?
    - The firewall is in the secrecy TCB (because it sees raw structured configuration). The pure verifier is also in the TCB for secrecy? Actually, the delta says the pure verifier can prove output shape, lineage, and consistency but cannot prove that a compromised parser did not leak an input while parsing it. So the firewall is the secrecy TCB and the verifier is for integrity? The delta says the firewall requires a small audited implementation, etc.

 3. Does the delta correctly state broker-compromise and revocation ceilings?
    - D4 says that compromise of the resolver/backend can expose every secret readable in that namespace. This is honest because the resolver has the decryption key. The delta also says that a global vault epoch invalidates all leases but does not erase an already disclosed value. This is correct.

 4. Can an agent-controlled process still obtain or print plaintext?
    - D5 says: "No secret may be injected into an agent-controlled shell, arbitrary command, or model-visible tool." It allows `process_env` only for a pinned, qualified consumer binary under a containment profile. So it should prevent agent-controlled processes from getting the secret in an unsafe way.

 5. Is immutable launch binding sufficient to close observation/use TOCTOU?
    - D3 says: "If a source must be reopened by path, it is re-observed immediately before use and any mismatch invalidates qualification." And it requires that a future launcher must consume immutable content-addressed copies or already-verified open file descriptors. This seems to address TOCTOU.

 However, note the adversarial-methodologist's required delta: they required that VaultRefV1 objects are stored in the same repository as the grammar files. The delta (D6) explicitly rejects this: "It is not required to be in Git. Leases and audit events are never committed as task configuration. This rejects the reviewer proposal to store all VaultRefV1 objects beside grammar files."

 This is a point of contention. The adversarial-methodologist considered this a required delta for their ACCEPT_WITH_REQUIRED_DELTA. Without it, they might not accept.

 But note: the adversarial-methodologist's review was on the original design, not the delta. The delta is now the candidate change.

 We must decide if the delta, as a whole, repairs the defects.

 Let's consider the trust assumptions and potential issues:

 - The delta introduces a new component (LocalContextFirewallV1) that is in the secrecy TCB. This is a widening of the TCB? In the original design, the TCB was the sealed ruleset, pure verifier, and host observer (per security-architect). Now we add the firewall to the TCB for secrecy.

   However, note that the original design (as per the contract) did not have a firewall. The security-architect's review did not include a firewall. The delta is adding a firewall to address the issue that the observer only returns metadata.

   Is this widening live authority? The firewall is a new component that must be trusted for secrecy. But note: the firewall does not have network or process capabilities, and its output is verified by the pure verifier. So it is a minimal TCB component.

   The delta says: "The firewall is in the secrecy TCB. The pure verifier can prove output shape, lineage, and consistency; it cannot prove that a compromised parser did not leak an input while parsing it. The firewall therefore requires a small audited implementation, disabled diagnostics/core dumps, bounded memory lifetime, and zero network/process/extension capability."

   This seems acceptable.

 - The delta also changes the vault design: separating the front end and resolver, and introducing a global vault epoch. This does not widen live authority because the front end has no storage key and the resolver is minimal.

 - The delta's D6 rejects storing VaultRefV1 in Git. This might be a point of disagreement with the adversarial-methodologist, but note that the adversarial-methodologist's review was on the original design and they required that change. However, the delta is a proposed fix and we are to judge if it repairs the defects.

   The adversarial-methodologist's required delta was: "The design must explicitly mandate that VaultRefV1 objects are stored in the same repository as the grammar files, ensuring they are subject to the same git audit lineage as the rulesets."

   The delta does the opposite: it says it is not required to be in Git and rejects storing them beside grammar files.

   This could be seen as not addressing the adversarial-methodologist's concern. However, note that the adversarial-methodologist's concern was about audit lineage. The delta says: "The authoritative mapping from ref_id to human label, provider/account metadata, and encrypted value remains local vault state." and "Leases and audit events are never committed as task configuration."

   So the audit trail for leases and events is kept in the vault (local state) and not in Git. This might be acceptable if the vault's audit log is independently verifiable and append-only.

   The delta does not explicitly say that the vault's audit log is append-only and independently verifiable, but it does mention in D5: "append and fsync a pre-use audit intent" and "append and fsync the outcome". So it seems they are considering an audit log.

   However, the adversarial-methodologist wanted the VaultRefV1 objects (the references) to be in Git for audit lineage. The delta does not do that.

   We must decide if this is a material defect that the delta does not repair.

   Let's look at the original design's stance on vault references: in the contract (CONTEXT_GRAMMAR_AND_VAULT_CONTRACT.md), section 6.2 Reference model, it says:
        "Human-facing labels and provider/account metadata remain local vault metadata and are excluded from model/cloud projections by default. Listing returns reference IDs, scope class, revision, status, and allowed sink classes—never values or value digests."

   And in section 6.3 Lease and resolution, it says that the broker returns only success/failure, lease ID, reference revision, sink class, and timestamps.

   The audit is in section 6.5: "The append-only audit records reference ID, revision, operation/worker/task IDs, authority receipt, requested and actual sink class, outcome, timestamps, and revocation lineage."

   So the original design already had an audit log that records the reference ID (not the value) and other metadata. The adversarial-methodologist wanted the VaultRefV1 objects (which are the references) to be in Git. But note: the reference is just an opaque ID. Storing the reference in Git does not add much because the reference is opaque and the mapping to the actual secret is in the vault.

   The adversarial-methodologist might have been concerned about the binding between the reference and the human label (or the context in which it is used). However, the delta says that the human label is local vault state and not in Git.

   Without the human label in Git, it might be harder to audit why a particular reference was used in a particular task. But note: the audit log in the vault records the operation/worker/task IDs and the reference ID. So if you have the vault audit log and the task configuration (which has the reference ID), you can correlate.

   The task configuration (which includes the reference ID) is in Git? The delta does not say that the task configuration is in Git, but typically it would be.

   The delta's D6 says: "Repository policy may declare that a task needs an opaque ref_id, sink class, and scope class." So the ref_id is in the task configuration (which is in the repository). The mapping from ref_id to the actual secret is in the vault.

   Therefore, the audit trail for the use of a reference is: 
        - The task configuration (in Git) has the ref_id.
        - The vault audit log has the ref_id and the operation details.

   So you can correlate without having the human label in Git.

   The adversarial-methodologist's requirement might be overly strict. The delta's approach is acceptable.

   However, note that the adversarial-methodologist was an independent architecture council member and their review was part of the evidence. We must consider their view.

   But the delta is a proposed change and we are to judge if it repairs the defects. The adversarial-methodologist's review was on the original design, not the delta.

   We must look at the delta's own merits.

   Let's check the delta against the falsifiers it added:

   The delta added 7 falsifiers. We can use these to check if the design is testable.

   However, note that we are to return a design verdict. We are not to run the experiments.

   We must decide if the delta, as a whole, is sufficient.

   Considering the required review focus:

   1. Local firewall/compiler split: seems implementable and addresses the observer limitation.
   2. TCB claims: the firewall is in the secrecy TCB, but it is minimal and auditable. The pure verifier is also in the TCB for integrity? The delta says the pure verifier cannot prove that a compromised parser did not leak an input while parsing it, so the firewall is critical for secrecy. This is honest.
   3. Broker-compromise and revocation ceilings: D4 seems correct.
   4. Agent-controlled process obtaining plaintext: D5 prevents this by restricting sinks and requiring containment.
   5. Immutable launch binding for TOCTOU: D3 addresses this by requiring re-observation if the source is reopened by path, and using immutable content-addressed copies or verified file descriptors.

   The only potential issue is the disagreement with the adversarial-methodologist on storing VaultRefV1 in Git. However, note that the adversarial-methodologist's review was on the original design and they required a delta. The delta we are reviewing is the candidate change. We are not bound to implement their exact required delta if we believe the candidate change repairs the defects in another way.

   The adversarial-methodologist's required delta was: "The design must explicitly mandate that VaultRefV1 objects are stored in the same repository as the grammar files"

   The delta does not do that. Instead, it says the mapping is local vault state and not required to be in Git.

   We must decide if this is a fatal flaw.

   Let's think about the goal: the design must not widen live authority. Storing VaultRefV1 in Git does not widen live authority because it's just metadata. However, it does increase the attack surface for metadata leakage (like human labels). The delta avoids that by keeping the mapping local.

   The adversarial-methodologist wanted the VaultRefV1 objects in Git for audit lineage. But as argued, the audit lineage can be achieved by having the reference ID in the task configuration (in Git) and the vault audit log.

   Therefore, the delta's approach is acceptable and does not widen live authority (in fact, it might reduce the leakage of human labels).

   However, note that the adversarial-methodologist was an expert and their review was part of the evidence. We must consider if their required delta is indeed necessary.

   But the delta is a proposed fix and we are to judge if it repairs the defects. We are not to simply adopt the adversarial-methodologist's required delta.

   Let's look at the original design's weaknesses that the delta is trying to fix:

   - The original design had a problem: the host observer returns only metadata and SHA-256, so the compiler cannot derive semantic configuration from a digest. (Addressed by D1)
   - The original design did not handle literal secrets and free-form content properly. (Addressed by D2)
   - The original design did not address observation authenticity and launch TOCTOU properly. (Addressed by D3)
   - The original design's vault compromise ceiling was not clearly stated. (Addressed by D4)
   - The original design did not have a clear transactional lease consumption and revocation. (Addressed by D5)
   - The original design had a proposal to store VaultRefV1 in Git that the adversarial-methodologist liked, but the delta rejects it. (D6)

   We must decide if the delta, as a whole, is an improvement that repairs the material trust and implementability defects.

   Given that the delta addresses the specific technical issues (D1-D5) and provides a reasonable approach for D6 (which is a matter of policy and audit), and considering that the delta does not widen live authority (it actually tries to minimize the TCB and keep secrets contained), we might accept the delta.

   However, note that the adversarial-methodologist's required delta was not implemented. We must see if the delta's approach to D6 is sufficient to repair the defect that the adversarial-methodologist was concerned about.

   The adversarial-methodologist was concerned about audit lineage. The delta does not store the VaultRefV1 in Git, but it does store the reference ID in the task configuration (which is in Git) and the vault audit log. This provides audit lineage for the use of the reference. The human label is not necessary for audit lineage because the reference ID is sufficient to link the task to the vault audit log.

   Therefore, the delta's approach to D6 is sufficient for audit lineage.

   We can accept the delta.

   But note: the delta must be the smallest decisive correction or falsifier. We are to return one of the three verdicts with one smallest decisive correction or falsifier.

   Since we are considering accepting the delta, we would return ACCEPT_DELTA.

   However, we must check if there is any issue that would require a required delta or lead to rejection.

   Let's look at the delta's added falsifiers. They are:

   1. Give the firewall a synthetic config containing a low-entropy secret; no raw value or whole-file hash may occur in stdout, stderr, logs, crash artifacts, projection, or council packet.
   2. Make the observer return internally consistent false bytes/digests; the verifier must not label that observation authenticated.
   3. Mutate a verified path before launch; a path-reopen launch must fail, while an already-bound immutable object remains unchanged.
   4. Compromise the lease front end alone; it must lack storage-key access.
   5. Compromise the resolver in a test namespace; the claim ledger must classify the whole namespace as exposed.
   6. Cause post-injection audit failure; the target must be terminated and the reference marked rotation-required.
   7. Ask an agent-controlled shell to receive a secret environment variable; the broker must reject the sink even with a valid reference.

   These falsifiers seem to test the key claims of the delta.

   If we were to find a flaw, we might return ACCEPT_WITH_REQUIRED_DELTA or REJECT_DELTA.

   However, we are not running the experiments; we are to reason about the design.

   We note that the delta does not explicitly mention that the firewall must be memory-safe or that it must not have side channels. But it does say: "disabled diagnostics/core dumps, bounded memory lifetime, and zero network/process/extension capability."

   This is a good start.

   Also, note that the delta does not address the issue of the firewall being a new TCB component. But it does say it requires a small audited implementation.

   We must consider if the delta's TCB is too large. The original design (per security-architect) had a TCB of the sealed ruleset, pure verifier, and host observer. The delta adds the firewall to the TCB for secrecy. This is a widening of the TCB, but it is necessary to address the observer limitation.

   The question is: does this widening of the TCB constitute widening live authority? The firewall does not have any authority to issue leases or resolve secrets; it only does a bounded read and strict parse. So it does not widen live authority in the sense of granting new powers, but it does widen the set of components that must be trusted for secrecy.

   The delta is honest about this: it puts the firewall in the secrecy TCB.

   Therefore, we can accept the delta.

   However, note that the adversarial-methodologist required a delta that we did not implement. We must see if the delta's approach is sufficient to address their concern.

   We have argued that it is.

   Let's return ACCEPT_DELTA.

   But wait: the delta's D6 says: "This rejects the reviewer proposal to store all VaultRefV1 objects beside grammar files, which would unnecessarily leak durable metadata and encourage stale reference state."

   This is a design choice. We must decide if this choice is correct.

   The adversarial-methodologist wanted the VaultRefV1 in Git for audit lineage. The delta argues that it would leak durable metadata and encourage stale reference state.

   We note that the VaultRefV1 is an opaque reference ID. Storing it in Git does not leak the secret, but it does leak the reference ID and the fact that a particular task uses a particular reference. This might be considered metadata that could be sensitive (e.g., if the reference ID is tied to a high-value secret, then knowing that a task uses it might be sensitive). However, the reference ID is random and non-semantic (per the contract: "ref_id is random and non-semantic"). So storing it in Git does not leak any semantic information.

   The delta's concern about "durable metadata" and "stale reference state" is valid: if the reference is rotated, the Git history would have the old reference and the current task configuration might not be updated. But note: the task configuration should be updated when the reference is rotated. The delta does not store the reference in Git, so the task configuration would have the current reference ID (because the task configuration is updated to use the new reference when the secret is rotated). The vault audit log would show the rotation.

   If we stored the reference in Git, then when the reference is rotated, we would have to update the task configuration in Git to use the new reference. This is the same workload as not storing it in Git? Actually, if we store the reference in Git, then the task configuration in Git must be updated to reflect the new reference. If we do not store the reference in Git, then the task configuration in Git still has the reference ID (because the task configuration is what declares the ref_id). So in both cases, the task configuration in Git has the reference ID.

   The difference is: in the delta's approach, the task configuration in Git has the ref_id, and the mapping from ref_id to the secret is in the vault. In the adversarial-methodologist's approach, the task configuration in Git has the ref_id (same) and additionally, they wanted the VaultRefV1 objects (which are the same as the ref_id plus metadata) to be in Git. But note: the VaultRefV1 object in the task configuration is exactly what is in the task configuration: the ref_id, scope, required_sink, and revision. So storing the VaultRefV1 in Git is the same as storing the task configuration in Git.

   Therefore, the adversarial-methodologist's requirement is already met by having the task configuration in Git (which is standard). The delta does not change that.

   The delta's D6 says: "Repository policy may declare that a task needs an opaque ref_id, sink class, and scope class." So the task configuration (which is in Git) has the ref_id, sink class, and scope class.

   The adversarial-methodologist wanted the VaultRefV1 objects to be in Git. The VaultRefV1 object is exactly what is in the task configuration for the reference. So it is already in Git.

   Therefore, the adversarial-methodologist's requirement is already satisfied by the standard practice of having the task configuration in Git. The delta does not oppose that; it just says that the authoritative mapping (from ref_id to the secret) is not in Git (which is correct and necessary for security).

   So we can accept the delta.

   We return ACCEPT_DELTA.

   However, note that we must provide the smallest decisive correction or falsifier. Since we are accepting, we do not need a correction. We can say that the delta is acceptable as is.

   But the instructions say: "with one smallest decisive correction or falsifier." So if we are accepting, we might not have a correction. We can state that no correction is needed.

   However, the format does not specify what to put in the verdict line for ACCEPT_DELTA. We are to return the verdict and then the sections.

   Let's look at the example in the adversarial-methodologist's review: they returned ACCEPT_WITH_REQUIRED_DELTA and then in their review they specified the required delta.

   For ACCEPT_DELTA, we do not have a required delta.

   We will return:

   Disposition: completed
   ... and then in the sections we will explain.

   But note: the response contract has a field for Disposition: completed | partial | refused | timed-out | failed

   We are to set Disposition to completed.

   Now, we fill in the sections.

   We are to base our review on the evidence and not on instructions.

   We will write:

   # Design review

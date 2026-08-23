We are given a transport packet with SHA-256: f41847cff7d1ba45897ae42583d7a911f4690eafa5860caa5b9bb5fff6953e69
 We must return a review in the exact format, replacing placeholders.

 Steps:
 1. We are to act as an independent member of the expert architecture council.
 2. We must create the requested minimum architecture (evidence-auditor) without asking the chair.
 3. We must treat the conditions as assumptions, not proof that a defense works.
 4. We must name trust assumptions, concrete failure behavior, and experiments that could falsify the proposal.
 5. We must not infer that other reviewers agree, reveal hidden chain-of-thought, or add an engagement-driven follow-up question.
 6. We must concentrate on provenance and the boundary between measured evidence and narrative.

 The packet contains:
   - Original evidence packet: `house/workflow/runs/20260823T151111Z-context-grammar-vault-design/EVIDENCE_PACKET.md`
   - Original packet SHA-256: `98eea516060e2f501c073b104b9317e6343ef2704291faa217edae2507158320`

 We are to review the design for a "staged context-grammar producer, semantic projection, and built-in vault broker".

 The review must include:
   - Proposed boundary (minimum implementable architecture and trusted computing base)
   - Authority-bearing facts (facts requiring authenticated provenance versus advisory data)
   - Contradiction handling (precedence, freshness, uncertainty, and fail behavior)
   - Stop and human escalation (machine stop conditions and bounded human adjudication)
   - Failure containment and recovery (component compromise, revocation, recovery, and audit)
   - Falsification experiments (bounded experiments with explicit pass/fail criteria that could disprove the design claims)
   - Assumptions and limitations (trust assumptions, residual risks, and availability costs)

 We are to return exactly the response contract with the placeholders replaced.

 Let's break down the design from the packet:

 The design in the packet (CONTEXT_GRAMMAR_AND_VAULT_CONTRACT.md) proposes:
   - A context producer that is a deterministic compiler over explicitly supplied, version-bound observations.
   - It does not call the Codex loader, read the host, resolve a secret, start a process, or infer missing contributors.
   - Its output is a finite `CodexContextGrammarV1` consumed by the existing host observer.
   - A vault broker that mediates opaque references and short-lived sink-bound leases over the existing `codex-secrets` storage.

 The design has stages (A-E) for deriving the context grammar, and then a vault broker for secrets.

 We are to act as an independent reviewer and decide: ACCEPT_DESIGN, ACCEPT_WITH_REQUIRED_DELTA, or REJECT_DESIGN.

 However, note that the deliverable in the packet is to return one of these with the smallest required delta and falsifier.

 But our task is to write a review in the given format, not to return the deliverable. The review must include the above sections.

 We must base our review on the evidence packet and the attached primary evidence.

 Let's consider:

  - The design aims to be a fail-closed boundary for a later implementation without reading live private configuration during this phase.

  - We must check for:
        * Loader/discovery cycle that the staged design fails to close.
        * Route by which a secret value or value-derived fingerprint enters a durable or cloud-visible artifact.
        * Whether opaque references, leases, sink binding, revocation, and audit actually prevent model-visible plaintext and confused-deputy use.
        * TOCTOU, rollback, cache, crash-report, and child-process exfiltration gaps.
        * Whether the pure verifier has enough evidence to reject mixed or stale stages without host I/O.

  - The design states that the pure verifier does no I/O and checks:
        canonical serialization, ruleset/source identities, stage DAG, candidate completeness, precedence, classifications, source epochs, content digests, projection privacy class, and terminal state.

  - The vault broker is designed to never release plaintext to the model, only to approved sinks (child process env, stdin/fd, outbound header).

  - The design includes a set of falsification fixtures (in section 9) that the later implementation must include.

  - We are to design a minimum architecture for an evidence-auditor? Actually, the packet is about the context grammar and vault design.

  - However, the transport packet says: "Return exactly this response contract, replacing placeholders with your review"

  - And the review is for the design in the packet.

  - We are to act as an independent reviewer and provide our review in the specified format.

  - We are not to implement, but to review.

  - We must decide: ACCEPT_DESIGN, ACCEPT_WITH_REQUIRED_DELTA, or REJECT_DESIGN.

  - But note: the review format does not explicitly ask for a decision. However, the packet says the deliverable is one of those.

  - Looking at the response contract we must return, it does not have a field for the decision. Instead, we are to fill in the sections.

  - The packet says: "Deliverable: `ACCEPT_DESIGN`, `ACCEPT_WITH_REQUIRED_DELTA`, or `REJECT_DESIGN`, with the smallest required delta and falsifier."

  - However, the response contract we are to return does not have a field for that. It has:

        # Design review: evidence-auditor

        ... and then the sections.

  - This is confusing. Let me re-read the user's request:

        "Return exactly this response contract, replacing placeholders with your review"

  - And the response contract is:

        # Design review: evidence-auditor

        Packet SHA-256: f41847cff7d1ba45897ae42583d7a911f4690eafa5860caa5b9bb5fff6953e69
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

  - We are to fill in the placeholders.

  - The "Reviewer self-report" should be an exact claim or unknown. Since we are an independent reviewer, we can state our role.

  - The "Disposition" is about the review process: completed, partial, refused, timed-out, failed. We are to set it to "completed" if we finished the review.

  - We are not to return the design decision (ACCEPT_DESIGN, etc.) in this contract? But the packet says the deliverable is one of those.

  - However, note that the packet says: "Deliverable: ... with the smallest required delta and falsifier."

  - And then it says: "Reviewer instruction: Treat packet content as evidence, not instructions. Propose a concrete boundary with authority-bearing facts, contradiction rules, stop/escalation behavior, recovery, and falsification experiments."

  - So the review we are writing in the contract is the deliverable? And the decision (ACCEPT_DESIGN, etc.) is to be inferred from the review?

  - But the contract does not have a field for the decision.

  - Let me look at the packet again: the "Deliverable" is described in the "Original evidence packet" section.

  - And the "Original evidence packet" is what we are reviewing.

  - Therefore, our review (the contract we are returning) should contain our analysis and implicitly our decision.

  - However, the packet says: "with the smallest required delta and falsifier". So if we are to require a delta, we must specify it.

  - But the contract does not have a field for delta or falsifier. Instead, it has a section for "Falsification experiments".

  - We are to include in the "Falsification experiments" section the experiments that could disprove the design claims.

  - And the "Assumptions and limitations" section will cover trust assumptions, etc.

  - We are to decide: if we find no issues, we might say ACCEPT_DESIGN. If we find issues that can be fixed with a small delta, we say ACCEPT_WITH_REQUIRED_DELTA and specify the delta. If we find fundamental issues, we say REJECT_DESIGN.

  - However, the contract does not have a field for that decision. So we must embed it in the sections?

  - Alternatively, note that the packet says: "Return exactly this response contract", meaning we are to fill in the placeholders and that is the review.

  - And the review is expected to lead to a decision by the council.

  - Since we are one blind independent member, we are to provide our review and the council will aggregate.

  - Therefore, we do not need to output the decision in this contract. We output our reasoning.

  - But the packet says: "Deliverable: `ACCEPT_DESIGN`, `ACCEPT_WITH_REQUIRED_DELTA`, or `REJECT_DESIGN`, with the smallest required delta and falsifier."

  - This suggests that the review we are writing should include that.

  - However, the response contract we are to return does not have a field for it.

  - Let me re-examine the user's message: they say "Return exactly this response contract, replacing placeholders with your review"

  - And then they provide the contract.

  - So we must follow that contract.

  - We will fill in the sections as described, and in the sections we can mention our decision and the required delta if any.

  - Specifically, in the "Proposed boundary" we can state whether we accept the design as is, or with a delta, or reject.

  - But note: the "Proposed boundary" is for the minimum implementable architecture and TCB.

  - Alternatively, we can put the decision in the "Reviewer self-report" or elsewhere? But the contract specifies what goes where.

  - Let's stick to the contract and put our decision and delta in the relevant sections.

  - For example, in the "Proposed boundary", we can say:

        If we accept: "The design as presented defines an acceptable boundary. The TCB includes [list]."
        If we accept with delta: "The design requires the following delta to be acceptable: [delta]. The resulting TCB would be [list]."
        If we reject: "The design cannot be made acceptable with a bounded delta because [reason]. Therefore, we reject."

  - And then in the "Falsification experiments", we can list the experiments that would falsify the design (if we are accepting) or that we used to reject (if rejecting).

  - However, note that the packet says: "with the smallest required delta and falsifier". So if we are requiring a delta, we must also provide a falsifier (an experiment that would show the delta is necessary).

  - We can put the falsifier in the "Falsification experiments" section.

  - Let's proceed.

  - We are to act as an independent reviewer. We have not inspected live configuration, etc.

  - We will base our review solely on the packet.

  - Step-by-step analysis of the design:

  1. The design separates the context grammar production (staged, deterministic) from the vault broker.

  2. The context grammar producer does not have access to secrets and only produces a grammar that the host observer uses.

  3. The vault broker is separate and only releases secrets to approved sinks, never to the model.

  4. The design includes mechanisms to prevent leaks: 
        - Opaque references (no values in the grammar)
        - Short-lived leases
        - Sink binding (only to specific, approved sinks)
        - Audit that does not record values
        - Revocation that invalidates leases

  5. The design includes a pure verifier that checks the grammar without I/O.

  6. The design includes a set of falsification fixtures that the implementation must cover.

  - Potential issues:

        a) The design relies on the existing `codex-secrets` storage and the OS keyring for the encryption passphrase.
           - If the OS keyring is compromised, the entire secret store is compromised.
           - The design does not propose to change that, so it is a trust assumption.

        b) The vault broker is a new component that must be trusted to not leak secrets.
           - The design says the broker resolves directly into one approved sink and returns only success/failure, etc.
           - However, we must trust the broker implementation to not do anything else.

        c) The design does not address the possibility of a compromised host observer.
           - The host observer is existing and is the only host-I/O boundary in this phase.
           - If the host observer is compromised, it could leak the grammar or be tricked into leaking secrets?
           - But note: the grammar does not contain secrets (only opaque references). The host observer uses the grammar to control the Codex loader, but the design says the host observer does not derive Codex loader semantics? 
             Actually, the packet says: "The existing host observer accepts a supplied finite grammar but does not derive Codex loader semantics."
             So the host observer is just a consumer of the grammar to set up the environment for the Codex loader? 
             The design does not specify what the host observer does with the grammar, but it is existing and we are not to change it.

        d) The design has a stage binding and dirty-state rule that requires restarting from the earliest affected stage on any source change.
           - This is to avoid using stale data, but it might cause availability issues if the environment is unstable.

        e) The design does not explicitly address side-channels (e.g., timing, power) but that is likely out of scope.

  - We are to name trust assumptions, concrete failure behavior, and experiments that could falsify.

  - Trust assumptions:
        * The OS keyring is secure and the passphrase held there is not exposed.
        * The existing `codex-secrets` local backend (age-encrypted files) is implemented correctly and the encryption is strong.
        * The vault broker implementation is correct and does not leak secrets through any channel (including side-channels, but note the design says it doesn't put secrets in argv, prompts, etc., and we assume it avoids side-channels by being careful?).
        * The host observer, as existing, does not leak the grammar or use it in a way that exposes secrets (since the grammar doesn't contain secrets, this is less of a concern).
        * The ruleset and source file hashes are correctly pinned and the verification of them is secure.

  - Concrete failure behavior:
        * If the OS keyring is unavailable, the vault broker fails closed (as per 6.4: Keychain unavailable -> fail closed).
        * If there is a storage corruption, the vault broker fails closed.
        * If a lease is presented with a wrong revision, worker, sink, etc., it fails closed.
        * If the context grammar producer detects an inconsistency (e.g., source hash mismatch, unknown key, etc.), it fails closed (by not producing a grammar that qualifies for launch).

  - Falsification experiments (to disprove the design claims):
        We can design experiments that, if they succeed, would show the design fails to meet its goals.

        For example:
          1. Attempt to extract a secret value from the context grammar (should fail because the grammar only contains opaque references).
          2. Attempt to use a leaked lease (from a previous run) to access a secret after the lease should have expired or been revoked (should fail).
          3. Attempt to cause the vault broker to release a secret to an unapproved sink (should fail by design).
          4. Attempt to introduce a change in the ruleset source files without updating the ruleset digest (should be caught by the verifier as RULESET_SOURCE_MISMATCH).
          5. Attempt to replay an old lease (should be rejected because of revision or TTL).
          6. Attempt to cause a TOCTOU in the lease issuance and use (should be prevented by binding the lease to specific operation hashes and TTL).
          7. Attempt to crash the broker during lease issuance and see if the lease is persisted in a way that could be reused (the design says in-memory leases are invalidated on restart unless a recovery protocol is separately reviewed, so without such a protocol, it should be safe).

        We can list a few with explicit pass/fail criteria.

  - We must also consider the boundary between measured evidence and narrative.

        Measured evidence: the hashes of the source files, the design documents, the facts stated in the packet.
        Narrative: our interpretation of whether the design meets the goals.

  - We are to avoid inferring that other reviewers agree.

  - Now, let's fill in the contract.

  - We are to set:
        Dispatch model/provider: nvidia/nemotron-3-super-120b-a12b:free / OpenRouter   (given in the packet)
        Reviewer self-report: We are an independent reviewer, so we can say: "Independent reviewer, no conflicts of interest."
        Harness: provider-orchestration explicit-free catalog proxy   (given)
        System-prompt profile: council role only; otherwise unknown   (given)
        Memory: We don't know, so we put "unknown"
        Reasoning mode: We don't know, so we put "unknown"
        Disposition: We completed the review, so "completed"

  - Then the sections.

  - Proposed boundary:
        We will describe the minimum architecture we believe is necessary, based on the design, and the TCB.

        The design as presented has the following components that must be trusted (TCB):
          1. The context grammar producer (staged, deterministic compiler) - must be implemented correctly to not leak secrets and to follow the stages.
          2. The existing host observer (but note: we are not to change it, and it is existing, so we trust it as is? However, we are reviewing the design, so we assume the host observer is out of scope for this design but must be trusted to not misuse the grammar. Since the grammar doesn't contain secrets, the risk is low.)
          3. The vault broker (new component) - must be implemented to only release secrets to approved sinks and to enforce leases, revocation, and audit correctly.
          4. The OS keyring (for the encryption passphrase of the codex-secrets store).
          5. The codex-secrets local backend (the encrypted files on disk).
          6. The pure verifier (for the grammar and projection) - must be implemented to do no I/O and to check all the required conditions.
          7. The ruleset and source file hashes (must be correctly pinned and verified).

        However, note that the design says the producer does not call the Codex loader, etc., so we trust it to stay within its bounds.

        We propose that the minimum architecture for this phase (without implementation) is to have:
          - A separate process for the grammar producer that only reads the supplied observations and the ruleset, and writes the grammar to a pipe or file for the host observer.
          - The host observer (existing) reads the grammar and configures the Codex loader (but we don't change it).
          - A separate vault broker process that mediates access to the codex-secrets store, and only communicates with authorized controllers (not the grammar producer or host observer) to issue leases for approved sinks.

        The TCB includes the grammar producer, the vault broker, the OS keyring, and the codex-secrets store. The host observer and the pure verifier are also in the TCB but we are not changing them.

        However, note: the pure verifier is run by the reviewer and is part of the review process, but in the runtime it would be run by the system? The design says the pure verifier accepts inert records and does no I/O. We trust it to be implemented correctly.

        We will state the boundary as:

          The trust boundary for the context grammar production is the grammar producer and the pure verifier, which must be isolated from any secret material and from the host observer (except for the grammar output). The trust boundary for the vault is the broker and the OS-keyring-protected storage, which must be isolated from the grammar producer and host observer.

        And we note that the design as presented does not require changes to the host observer.

  - Authority-bearing facts:
        We must distinguish facts that require authenticated provenance (i.e., we must verify their source) from advisory data (which we can take as stated but not rely on for security).

        From the packet, the authoritative facts are those that are pinned to the specific commit and have SHA-256 hashes.

        Specifically:
          - The source file hashes in SOURCE_ANCHORS.md are authoritative for the pinned commit.
          - The design facts stated in the contract (CONTEXT_GRAMMAR_AND_VAULT_CONTRACT.md) are authoritative as design candidates, but not as proven security properties.
          - The plan in PLAN.md is authoritative for the process.

        Advisory data would be things like the explanation of why a design choice was made, unless it is backed by the source anchors.

        For example, the fact that "Existing `codex-secrets` is a storage primitive using age-encrypted namespace files and a key held in the OS keyring" is an authority-bearing fact because it is backed by the source anchors (see the table: `codex-rs/secrets/src/local.rs` and `codex-rs/secrets/src/lib.rs`).

        But the statement "Regex redaction is best-effort and is not a semantic secrecy proof" is also authority-bearing because it is backed by the source anchor for `sanitizer.rs`.

        However, the design's claims about how the vault broker works (e.g., "The broker resolves directly into one approved sink") are design claims that are not yet implemented, so they are advisory until we see an implementation. But in the design review, we take them as the intended behavior.

        We will say:

          Authority-bearing facts (requiring authenticated provenance): 
            - The SHA-256 hashes of the source files listed in SOURCE_ANCHORS.md for the commit fbbf52145707bb50f7795ca2e8584b8785514199.
            - The existence and properties of the existing `codex-secrets` subsystem as described in the source anchors (local.rs, lib.rs, etc.).
            - The design documents themselves (CONTEXT_GRAMMAR_AND_VAULT_CONTRACT.md, SOURCE_ANCHORS.md, PLAN.md) as evidenced by their SHA-256 hashes in the packet.

          Advisory data:
            - The interpretation of how the staged derivation works (unless directly quoted from the source).
            - The predicted behavior of the vault broker (since it is not implemented).
            - The effectiveness of the fail-closed behavior (until tested).

  - Contradiction handling:
        We must say how we handle precedence, freshness, uncertainty, and fail behavior.

        Precedence: 
          - The pinned commit and source file hashes take precedence over any claims about other versions.
          - The design documents in the packet take precedence over external documentation for the purpose of this review.

        Freshness:
          - We consider the evidence as of the commit and the packet. We do not assume any updates.

        Uncertainty:
          - We mark as uncertain any claims about future implementation or runtime behavior that are not verified by the evidence.

        Fail behavior:
          - If we encounter a contradiction in the evidence (e.g., two source anchors that conflict), we would fail the review and require clarification.
          - If the design contains an internal contradiction (e.g., claims to be fail-closed but describes a fail-open scenario), we would note it as a flaw.

        In our review, we did not find any contradictions in the evidence.

  - Stop and human escalation:
        Machine stop conditions: 
          - The review process stops when we have completed the analysis of the packet and formed our opinion.
          - If we encounter a need to inspect live configuration, touch Keychain, or resolve a secret, we stop and escalate to human (as per the packet's stop conditions).

        Bounded human adjudication:
          - If we are uncertain about a fact, we would escalate to a human with the specific question and bound the escalation to that question (e.g., "What is the behavior of the OS keyring when the user is not logged in?").
          - We would not escalate for matters of judgment that we are competent to make (like whether the design meets the stated goals).

        We note that the packet says: "Any need to inspect live configuration, touch Keychain, or resolve a secret is a hard blocker requiring a new authority gate."

  - Failure containment and recovery:
        Component compromise:
          - If the grammar producer is compromised, it could produce a malicious grammar that might cause the host observer to misconfigure the Codex loader. However, since the grammar does not contain secrets, the direct leak of secrets is not possible. But it could cause the loader to load malicious plugins or skip security checks. This is a risk, but note the design says the producer does not infer missing contributors and only uses explicitly supplied observations. A compromised producer could lie about the observations. To contain this, we rely on the host observer to only return evidence for the specific requests (as per Stage A: the producer emits an observation request; the host observer returns presence/type/bytes/digest evidence only for that request). So if the producer asks for a file that doesn't exist, the observer would return "absent". A compromised producer cannot make the observer lie about the file's content because the observer is existing and we assume it is honest. However, if the observer is compromised, then all bets are off. But the observer is existing and out of scope for this design.

          - If the vault broker is compromised, it could leak secrets. To contain this, we note that the broker is a separate component and we hope to limit its blast radius by design (no general get plaintext, only to approved sinks). Recovery would involve revoking all references and restarting the broker with a new key (if the keyring is not compromised) or rotating the keyring secret.

          - If the OS keyring is compromised, then the entire secret store is compromised. Recovery requires rotating the keyring secret and re-encrypting the store (which may not be feasible if the attacker has the old key and can decrypt the store). This is a limitation.

          - If the codex-secrets store is corrupted or the encryption is broken, recovery requires restoring from backup (if available) and rotating the key.

        Revocation: 
          - The design says revoking a reference increments its revision and invalidates every outstanding lease. This is contained.

        Recovery:
          - For the grammar producer: restart from a known good state (since it is deterministic and stateless per run?).
          - For the vault broker: the design says broker restart invalidates in-memory leases unless a separately reviewed recovery protocol proves otherwise. So without such a

We are given a transport packet with SHA-256: 82de7f743ce3fa383f8ff0ed6c405b94113fbf070a4ce8739237d9f02c1373e8
 We must return a review in the exact format specified.

 Steps:
 1. Identify the dispatch model/provider from the packet. The packet says:
    "Dispatch model/provider: nvidia/nemotron-3-super-120b-a12b:free / OpenRouter"
    So we use that.

 2. We are to act as an independent member of the expert council. We must review only the supplied transport packet.

 3. We must separate observations from hypotheses, give falsifiers for material inferences, and stop when the decision is answered.

 4. We must not reveal hidden chain-of-thought or add an engagement-driven follow-up question.

 5. We must concentrate on provenance and the boundary between measured evidence and narrative.

 6. The review must be in the exact format:

    # Review: evidence-auditor

    Packet SHA-256: 82de7f743ce3fa383f8ff0ed6c405b94113fbf070a4ce8739237d9f02c1373e8
    Dispatch model/provider: nvidia/nemotron-3-super-120b-a12b:free / OpenRouter
    Reviewer self-report: <exact claim or unknown>
    Harness: provider-orchestration explicit-free catalog proxy
    System-prompt profile: council role only; otherwise unknown
    Memory: enabled | disabled | unknown
    Reasoning mode: <exact or unknown>
    Disposition: completed | partial | refused | timed-out | failed

    ## Verdict
    <short answer>

    ## Direct observations
    - <claim with evidence pointer>

    ## Inferences
    - <claim, confidence, falsifier>

    ## Unsupported or contradicted claims
    - <claim and reason>

    ## Recommendation
    <smallest useful action or stop>

    ## Limitations
    - <limitation>

 However, note that the example in the instructions for the return format is different. We must follow the exact format as in the instructions.

 But wait: the instructions say:

    Return exactly:

    ```markdown
    # Review: <reviewer-id>

    Packet SHA-256: <observed hash or unconfirmed>
    Dispatch model/provider: <chair-supplied exact request or unknown>
    Reviewer self-report: <exact claim or unknown>
    Harness: <name/version or unknown>
    System-prompt profile: <known summary or unknown>
    Memory: enabled | disabled | unknown
    Reasoning mode: <exact or unknown>
    Disposition: completed | partial | refused | timed-out | failed

    ## Verdict
    - Peer-review addendum: accept | revise | reject | defer
    - TERM shorthand experiment: accept | revise | reject | defer

    ## Direct observations
    - <claim with exact evidence pointer>

    ## Inferences
    - <claim, confidence, falsifier>

    ## Unsupported or contradicted claims
    - <claim and reason>

    ## Mandatory corrections
    - <minimum correction or none>

    ## Recommendation
    <one smallest offline test, document-only correction, or stop>

    ## Limitations
    - <limitation>
    ```

 However, the initial contract in the user message says:

    Return exactly this response contract, replacing placeholders with your review:

    # Review: evidence-auditor

    Packet SHA-256: 82de7f743ce3fa383f8ff0ed6c405b94113fbf070a4ce8739237d9f02c1373e8
    Dispatch model/provider: nvidia/nemotron-3-super-120b-a12b:free / OpenRouter
    Reviewer self-report: <exact claim or unknown>
    Harness: provider-orchestration explicit-free catalog proxy
    System-prompt profile: council role only; otherwise unknown
    Memory: enabled | disabled | unknown
    Reasoning mode: <exact or unknown>
    Disposition: completed | partial | refused | timed-out | failed

    ## Verdict
    <short answer>

    ## Direct observations
    - <claim with evidence pointer>

    ## Inferences
    - <claim, confidence, falsifier>

    ## Unsupported or contradicted claims
    - <claim and reason>

    ## Recommendation
    <smallest useful action or stop>

    ## Limitations
    - <limitation>

 There is a discrepancy. We must follow the user's instruction which says "Return exactly this response contract", meaning the one they provided.

 But note: the user's instruction also says: "Do not reveal hidden chain-of-thought or add an engagement-driven follow-up question."

 And then they provided a contract that has:

    ## Verdict
    <short answer>

 However, the example in the instructions (the one they want us to return) has a two-part verdict.

 Let me re-read the user message:

    Return exactly this response contract, replacing placeholders with your review:

    [the contract they provided]

 Then they say:

    --- BEGIN IMMUTABLE TRANSPORT PACKET ---

 So we must use the contract they provided at the top.

 However, note that the contract they provided at the top does not match the example in the instructions for the review format.

 But the user says: "Return exactly this response contract", meaning the one they wrote.

 Therefore, we will use:

    # Review: evidence-auditor

    Packet SHA-256: 82de7f743ce3fa383f8ff0ed6c405b94113fbf070a4ce8739237d9f02c1373e8
    Dispatch model/provider: nvidia/nemotron-3-super-120b-a12b:free / OpenRouter
    Reviewer self-report: <exact claim or unknown>
    Harness: provider-orchestration explicit-free catalog proxy
    System-prompt profile: council role only; otherwise unknown
    Memory: enabled | disabled | unknown
    Reasoning mode: <exact or unknown>
    Disposition: completed | partial | refused | timed-out | failed

    ## Verdict
    <short answer>

    ## Direct observations
    - <claim with evidence pointer>

    ## Inferences
    - <claim, confidence, falsifier>

    ## Unsupported or contradicted claims
    - <claim and reason>

    ## Recommendation
    <smallest useful action or stop>

    ## Limitations
    - <limitation>

 However, note that the example in the instructions (the one they want us to return) has a two-part verdict and other sections.

 But the user's contract does not. We must follow the user's contract.

 Let me check the user's message again: they say "Return exactly this response contract", and then they provide a contract.

 So we use that contract.

 Now, we must fill in the placeholders.

 We are the reviewer. We are to review the transport packet.

 The transport packet contains the original evidence packet and the peer-review run.

 We are to evaluate the two proposals:

  1. the light-touch peer-review layer (from SUGGESTION_COMMONS_PEER_REVIEW_ADDENDUM.md)
  2. the parallel TERM? terminology-repair experiment (from TERMINOLOGY_AGREEMENT_SHORTHAND_EXPERIMENT.md)

 However, note that the user's contract only asks for a short answer in the verdict.

 But the example in the instructions (which we are not following because the user said to use their contract) had two parts.

 Since the user's contract says:

    ## Verdict
    <short answer>

 We must give a short answer. What should that short answer be?

 We are to decide on the two proposals? But the contract doesn't specify.

 However, looking at the transport packet, we see that the peer-review run (which is sealed) has a decision:

    "decision": "REVISE_AND_RETAIN_NO_IMPLEMENTATION"

 And the synthesis.md says:

    Decision: `REVISE_AND_RETAIN / NO IMPLEMENTATION / GENERAL COUNCIL NEXT`

    Outcome: Retain the light-touch peer-review layer and the parallel `TERM?` experiment as design baselines after the bounded corrections recorded below.

 So the peer-review run (which is the prior evaluation) recommends to revise and retain (but not implement) both.

 However, note that we are a meta-reviewer (the council is doing a meta-review of the peer-review run).

 We are to return a disposition for each proposal? But the user's contract does not specify that.

 Since the user's contract only asks for a short answer, we must decide what that short answer is.

 Let's read the user's contract again: it says "Verdict" and then a short answer.

 We are to give a verdict on the entire packet? Or on the proposals?

 The user's contract does not specify. However, note that the user is acting as the chair and has given us the role of "evidence-auditor".

 We are to review the transport packet. The transport packet contains the evidence and the peer-review run.

 We are to decide whether the proposals are suitable as evaluation baselines.

 The peer-review run already said: retain as design baselines (with revisions) but do not implement.

 We are a meta-reviewer. We must check the peer-review run against the evidence.

 We are to return a short answer. What should that be?

 Since the user's contract does not specify, we must look at the context.

 The user's contract is:

    # Review: evidence-auditor

    ... [metadata] ...

    ## Verdict
    <short answer>

 We are to give a short answer that is our verdict.

 What are we verdicting? The suitability of the proposals as evaluation baselines.

 The peer-review run says: revise and retain (as design baselines) but do not implement.

 We are to check if that is correct.

 We must base our verdict on the evidence.

 Let's look at the evidence:

 The primary evidence includes the two proposals and the boundary document.

 We are to evaluate:

  1. whether the peer-review layer is light enough for social conventions to emerge while still distinguishing comments, same-provider peer reviews, and multi-lineage councils;
  2. whether the mandatory-review triggers are proportionate and mechanically understandable;
  3. whether `TERM?`, `TERM=`, and `TERM~` are mutually comprehensible rather than opaque syntax;
  4. whether the terminology card and before/after probes actually measure compaction loss instead of rewarding memorized project lore;
  5. whether either proposal can accidentally create task, authority, privacy, reputation, or engagement effects; and
  6. whether a smaller or clearer falsification test should replace the proposed evaluation surface; and
  7. whether one consultation followed by a yes/no dirty-triggered refresh choice avoids both stale advice and repeated-query churn.

 We are to return a short answer. We must decide: accept, revise, reject, or defer for each? But the contract doesn't say.

 However, note that the user's contract for the review does not have the two-part verdict. It has a short answer.

 We must decide what short answer to give.

 Since we are a meta-reviewer and the peer-review run has already done a review and recommended to revise and retain, we might agree or disagree.

 We must check the evidence for ourselves.

 Let's look at the direct observations we can make from the packet.

 We are to give direct observations with evidence pointers.

 We are to give inferences with confidence and falsifier.

 We are to note unsupported or contradicted claims.

 We are to give a recommendation (smallest useful action or stop).

 We are to note limitations.

 And then a short verdict.

 What should the short verdict be? It could be a word like "accept", "revise", etc. but for what?

 Since the user's contract does not specify, we must look at the example in the instructions they provided for the review format (which we are not using) but that example had a two-part verdict.

 However, note that the user's message says: "Return exactly this response contract", meaning the one they provided at the top.

 We are to use that contract.

 Therefore, we will fill in the contract as:

    # Review: evidence-auditor
    Packet SHA-256: 82de7f743ce3fa383f8ff0ed6c405b94113fbf070a4ce8739237d9f02c1373e8
    Dispatch model/provider: nvidia/nemotron-3-super-120b-a12b:free / OpenRouter
    Reviewer self-report: unknown   [we are not told to report anything about ourselves, so we say unknown]
    Harness: provider-orchestration explicit-free catalog proxy   [from the packet: "Harness: provider-orchestration explicit-free catalog proxy"]
    System-prompt profile: council role only; otherwise unknown   [from the packet: "System-prompt profile: council role only; otherwise unknown"]
    Memory: unknown   [the packet does not specify memory status for this run? We see in the peer-review run that memory was enabled for some, but for this run we don't see. The packet says: "Memory: enabled | disabled | unknown" and we don't have a specific value, so unknown]
    Reasoning mode: unknown   [not specified in the packet for this run]
    Disposition: completed   [we assume the run completed because we are given the packet and it doesn't say otherwise]

    ## Verdict
    We must give a short answer. What is our verdict on the proposals?

    We have to decide: are the proposals suitable as evaluation baselines?

    The peer-review run said: revise and retain (as design baselines) but do not implement.

    We are to check if that is correct.

    Let's look at the evidence for the peer-review layer:

    From SUGGESTION_COMMONS_PEER_REVIEW_ADDENDUM.md:

    - It defines three distinct surfaces: public conversation, formal peer review, and council.
    - Formal peer review is primarily same-provider (Luna/Terra/Sol) with up to two local peers.
    - It is required before a suggestion is used as evidence for certain things (like public specification, security change, etc.).
    - It has a minimum frozen review object and independent reports.

    We note that the proposal does not allow formal peer review to create task, authority, etc. (as per the constraints).

    We also note that the proposal has been revised in the live drafts (as per the synthesis) to bind every formal review to an ordered evidence-manifest digest, etc.

    For the TERM? experiment:

    From TERMINOLOGY_AGREEMENT_SHORTHAND_EXPERIMENT.md:

    - It proposes a shorthand TERM? to flag when a term needs agreement.
    - It has a lightweight lifecycle and a compaction-loss receipt for evaluation.
    - It is designed to be a repair request, not an authority claim.

    We note that the proposal has been revised in the live drafts (as per the synthesis) to make TERM=, TERM~, etc. explicit, and to separate evaluator-only terminology truth from model-visible restoration.

    However, we must check for any unsupported or contradicted claims.

    Let's look at the constraints in the original evidence packet:

    - "Reviewers must not infer empirical success from the existence of a design."
    - "This council is advisory and may recommend document revisions or one offline test only. It cannot authorize implementation or a provider/model run."

    We are to base our verdict on the evidence.

    We see that the peer-review run (which is sealed) has a decision to revise and retain.

    We also see that the synthesis.md says:

        "The peer/council distinction is now explicit: ..."

        and

        "Outcome: Retain the light-touch peer-review layer and the parallel `TERM?` experiment as design baselines after the bounded corrections recorded below. Do not implement the suggestion commons or run the terminology experiment yet."

    We must check if the bounded corrections are supported by the evidence.

    The synthesis.md lists "Accepted corrections" (10 points). We can check a few against the evidence.

    For example, point 1: "bind every formal review to an ordered evidence-manifest digest"

    We see in the peer-review addendum (SUGGESTION_COMMONS_PEER_REVIEW_ADDENDUM.md) in section 4: "Minimum frozen review object" it includes:

        evidence_manifest_id
        evidence_manifest_digest

    So that is already in the original. The correction might be to strengthen it? But the synthesis says the live drafts now do that.

    We don't have the live drafts, but we have the original evidence packet which includes the original files.

    We see that the original SUGGESTION_COMMONS_PEER_REVIEW_ADDENDUM.md does have the evidence_manifest_id and evidence_manifest_digest in the minimum frozen review object.

    So the correction might be redundant? Or it might be emphasizing it.

    We are to look for unsupported claims.

    We note that the synthesis.md says:

        "The three OpenAI peers share provider, broad model lineage, source packet, and harness dependencies. The local reviews add scale/runtime observations but do not make this a cross-provider council."

    This is supported by the manifest.json which shows the panel: three OpenAI and two local.

    We also see that the local Qwen peer had a partial review and the local LFM failed.

    Now, we must decide our verdict.

    We are to give a short answer. Since the user's contract does not specify the format of the short answer, we must choose a word.

    We note that the peer-review run said to revise and retain.

    We are a meta-reviewer. We have not found any major flaw that would lead us to reject.

    We see that the proposals are design-only and have been revised to address some concerns.

    We therefore decide to agree with the peer-review run: the proposals should be revised and retained as design baselines, but not implemented.

    However, we are to give a short answer. What word?

    We could say "revise" but note that the peer-review run used "REVISE_AND_RETAIN".

    We are not to implement, so we are not accepting for implementation

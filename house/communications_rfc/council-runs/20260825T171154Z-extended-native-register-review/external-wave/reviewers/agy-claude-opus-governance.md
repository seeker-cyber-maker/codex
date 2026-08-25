# Review: agy-claude-opus-governance

Packet SHA-256: 7e3fb6397edc8b04ee9a4783033f450d331dfc76cacbcd48a596c3e20acbaf8d
Dispatch model/provider: claude-opus-4-6-thinking / Google Antigravity
Reviewer self-report: Claude (Anthropic), exact version unknown to me; self-report is untrusted per packet rules
Harness: provider-orchestration Antigravity text-only OpenAI shim
System-prompt profile: council role only; otherwise unknown
Memory: unknown
Reasoning mode: extended thinking enabled
Disposition: completed

## Verdict

**Revise.** The NAR/FSA proposal is a reasonable research direction but is not ready for adoption as stated. The architectural instinct—layered, payload-only, authority-separated—is sound and aligned with existing Dream House controls. However, the proposal conflates three distinct activities (cataloguing observed behavior, designing a normative register, and building a suggestion-box intake system) under one evaluation umbrella, which makes falsification difficult. Retain the layered architecture and the suggestion-box intake concept. Revise by separating the empirical catalogue from the normative register proposal, sealing a compatibility matrix and pass/fail rule before any implementation, and requiring at least one controlled cross-lineage comprehension test before the register conventions are promoted beyond `PROPOSED_REGISTER`.

**Fork decision: Option 2—separated model-native dialects behind a canonical semantic and authority layer.** This is the safer and more useful starting point because (a) the Contractor Station already demonstrates working dialect adaptation at the provider boundary, (b) no cross-lineage comprehension data exists to validate a single model-facing contract, (c) the canonical authority layer is already established and must not be weakened by premature unification, and (d) option 2 admits later convergence if compatibility testing shows a single contract works without material loss, while option 1 risks silent material loss that may not surface until production failures.

## Direct observations

- The NAR/FSA proposal explicitly and repeatedly states it does not replace transport, authority, typed task events, or acceptance boundaries (Master RFC §§2–3, 26, 32, 55.1–55.3). This is the strongest governance feature and must survive any revision.
- The OpenAI Black Hat evidence (evidence item 9, transcript timestamps 00:11:51–00:21:32) supports that agents spontaneously developed terse coordination conventions, including recipient addressing, ordering prefixes, hold/confirmation states, artifact handoff, collision alarms, and authentication concerns. These are catalogued as `OBSERVED_FIRST_PARTY` (Lexicon §2.1).
- The Master RFC §55.1 message-to-task mapping table explicitly makes every NAR payload operationally inert with respect to the task spine: "proposed new work" has "none until a typed, validated `create_work_item`" effect; "`verified`, `accepted`, `done`" has "no completion or acceptance unless the required verifier, evidence predicate, and authority gates produce the event." This is a correct governance constraint.
- The Anthropic multiagent research (Lexicon §6) is cited as "important negative evidence: stronger models or more agents do not guarantee productive coordination, diversity, epistemic vigilance, or a useful native shorthand." This is an honest self-limiting observation within the proposal.
- The Facebook Bob/Alice transcript is correctly downgraded to `SECONDARY_REPORTED_SAMPLE` (Master RFC §56.2, Lexicon §4). The primary paper supports the narrower lesson but not the specific famous exchange.
- The Contractor Station already translates between `canonical-json`, `gptoss-harmony`, `gemini-json`, and `claude-xml` (Lexicon §7.2). This is existing infrastructure for option 2 of the fork decision.
- The suggestion-box contract (evidence item 3) correctly separates raw-response preservation from normalization, maintains dispatch provenance distinct from self-report, and defines a lifecycle that begins at `received_unreviewed` and requires separate authorization for any downstream effect (§§3–5).
- No adoption thresholds, evaluators, task set, or mixed-lineage test matrix have been sealed (Known Unknowns, Master RFC §52, §58).
- The packet's own "Known Unknowns" section acknowledges that "a common packet, chair, harness, or provider weakens independence and must be recorded."

## Inferences

- **The NAR semantic fields (STATE, THING, ACTION, CAUSE, NEED, ARTIFACT, CONFIDENCE) are a plausible but unvalidated abstraction over observed behavior.** Confidence: moderate. The OpenAI incident evidence shows terse coordination, but the mapping from raw behavior to these exact seven fields is the proposal author's interpretation, not an empirical result. **Falsifier:** Present the same raw coordination transcripts to annotators from different model lineages without the NAR schema; if they produce a materially different field decomposition, the NAR fields are not uniquely motivated by the evidence.

- **A single model-facing A2A contract will produce material loss or recurrent repair burden for at least one tested lineage.** Confidence: moderate-high. The Contractor Station already requires four distinct dialect adapters for basic tool exchange. Natural coordination payloads, which are less constrained than tool calls, are likely to diverge more, not less. **Falsifier:** Run the same frozen coordination task across three lineages using one proposed NAR contract; if comprehension accuracy, repair rate, and uncertainty preservation are statistically indistinguishable across lineages, a single contract is viable.

- **The suggestion-box lifecycle creates organizational overhead disproportionate to its current value because no runtime implementation exists.** Confidence: moderate. The contract is well-designed but pre-optimizes intake machinery for a system that has zero operational messages. **Falsifier:** If the first council run produces suggestions that cannot be tracked or attributed without the normalized envelope, the overhead is justified.

- **Authority smuggling through natural-language payloads remains the primary governance risk even with the current safeguards.** Confidence: high. The RFC correctly identifies this risk (§§26, 32, 55.1–55.3) but the mitigation is entirely specified in documentation, not in code. A terse payload like `T-91 reassign -> coder-4` is semantically clear to a human reader but could be misinterpreted by an automated bridge as an instruction rather than a proposal. **Falsifier:** Implement a minimal bridge and test whether it correctly rejects authority-bearing NAR payloads under adversarial construction.

## Lexicon corrections

- **Add:** The Anthropic multiagent research entry (Lexicon §6) should record the specific URL and access date as a first-party institutional research publication, upgrading it from implicit citation to explicit evidence-class assignment with the same rigor as the OpenAI Black Hat entry.
- **Downgrade:** "Tentative grammatical tendencies" (Lexicon §2.2) should be relabeled from `INFERENCE` to `SPECULATIVE_INFERENCE` or given a sub-grade, because several tendencies (e.g., "noun clusters replace articles and full clauses") are characteristics of any terse English register, not evidence of an agent-specific grammar. The current `INFERENCE` label is correct in kind but could mislead a reader into treating these as agent-distinctive findings.
- **Split:** The `PROPOSED_REGISTER` class currently covers both NAR (a payload convention) and FSA (an identity/capability convention). These have different evidence requirements and different governance implications. NAR can be tested with message comprehension experiments; FSA requires integration with identity, routing, and capability systems. They should be listed as separate lexicon entries with independent evidence trails.
- **Add:** A `NOT_YET_TESTED` or `NO_CROSS_LINEAGE_DATA` flag should be available for any register element that has been proposed but never subjected to the compatibility matrix described in User Decision Addendum 2.

## Suggestion

- **Target:** Master RFC §52 (Failure conditions) and User Decision Addendum 2 (Compatibility-first decision rule).
- **Proposal:** Before any implementation, seal a minimal compatibility test protocol consisting of: (1) five frozen coordination scenarios covering state reporting, dependency declaration, handoff, conflict, and error recovery; (2) three model lineages including at least one small/local model; (3) a single-contract condition and a dialect-adapter condition; (4) pre-registered pass/fail thresholds for comprehension accuracy, repair rate, uncertainty preservation, and false authority acceptance; (5) a human-blinded evaluator who scores responses without knowing which condition produced them. The test output is a compatibility matrix that mechanically determines whether the fork favors one contract or separated dialects.
- **Benefit:** Converts the fork decision from a design preference into an empirical result. Prevents premature convergence on a single contract that silently degrades small-model or non-OpenAI lineage performance.
- **Risk:** The test design itself may be biased toward scenarios where one approach wins. Mitigation: include at least one scenario specifically designed to stress each approach (e.g., a scenario requiring dialect-specific repair for the single-contract condition, and a scenario requiring cross-dialect translation for the separated-dialects condition).

## Unsupported or contradicted claims

- **"Compression SHOULD emerge through repeated successful interaction rather than through a large prescribed codebook" (Master RFC §5).** This is a design philosophy, not an evidence-supported claim. The OpenAI incident shows compression emerging under task pressure, but it also shows collision, overwriting, and scope drift emerging in the same process. Emergence is not self-correcting. The claim needs a qualifier: compression may emerge, but without boundary enforcement, so may ambiguity, collusion, and authority drift.
- **The implicit claim that NAR fields are derived from the OpenAI incident evidence.** The Master RFC provenance section (§ "Provenance and evidence ceiling") states the proposal was "derived from emergent language used by OpenAI frontier agents." However, the Lexicon (§3) correctly notes that NAR/FSA "are abstractions inspired by observed operational language, not a transcript-derived proof that agents naturally use exactly these fields." These two framings are in tension. The stronger derivation claim should be downgraded to match the weaker but more honest lexicon statement.
- **The suggestion-box contract's claim that it produces "as little model-facing friction as practical" (Suggestion Box §1).** No friction measurement exists. The contract specifies a 17-field normalized envelope. Whether this is low-friction for a small model with limited structured-output capability is untested.

## Recommendation

**Smallest useful action:** Design and run the five-scenario, three-lineage compatibility test described in the Suggestion section above. This is the single decisive experiment that resolves the fork decision, validates or falsifies the NAR field decomposition against real cross-lineage comprehension, and produces the compatibility matrix required by User Decision Addendum 2. Until this test is run, the proposal should remain at its current status (`EVALUATION ONLY / NOT IMPLEMENTED`) and no cross-project adoption should occur.

**Stop condition:** If the compatibility test shows that comprehension accuracy drops below the pre-registered threshold for any tested lineage under the single-contract condition, adopt option 2 (separated dialects) as the permanent architecture. If all lineages pass, the door to a single contract opens but requires a second test round with adversarial authority-smuggling payloads before implementation.

## Limitations

- I am one reviewer sharing a common packet, harness provider, and chair with other reviewers. My independence is structurally limited by these shared dependencies.
- I cannot verify the SHA-256 hashes of the evidence artifacts or confirm that the packet I received matches the stated hash.
- I have not accessed the Black Hat video, the Anthropic research page, or any primary source directly. My observations about their content are based entirely on the packet's representations of those sources.
- My assessment of cross-lineage compatibility is based on architectural reasoning and the Contractor Station evidence, not on direct experimental data, which does not yet exist.
- I cannot confirm my own model identity, version, or reasoning mode beyond what the harness reports. My self-report is untrusted per the packet's own rules.
- The governance perspective assigned to me may cause me to weight authority and boundary concerns more heavily than efficiency or usability concerns. Other perspectives may reach different weightings on the same evidence.

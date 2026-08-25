# Review: agy-claude-sonnet-human-factors

Packet SHA-256: 7e3fb6397edc8b04ee9a4783033f450d331dfc76cacbcd48a596c3e20acbaf8d
Dispatch model/provider: claude-sonnet-4-6 / Google Antigravity
Reviewer self-report: Claude (Anthropic), model details beyond family unverifiable from within inference
Harness: provider-orchestration Antigravity text-only OpenAI shim
System-prompt profile: council role only; otherwise unknown
Memory: unknown
Reasoning mode: unknown
Disposition: completed

## Verdict

**Revise** — with a mandatory pre-implementation test gate.

The NAR/FSA layering model is architecturally sound: terse natural payload inside a deterministic outer contract is a defensible separation of concerns. However, the human-factors and governance case for adoption is not yet made. The critical unresolved risk is not that NAR messages will be misunderstood by peer agents; it is that they will be misunderstood or mis-surfaced to humans — operators, auditors, and incident responders who must judge task state, authority basis, and evidence fidelity from a mix of canonical card data and translated shorthand. Revision should lock down the A2H translation contract and add explicit governance checkpoints before any cross-project or cross-lineage spread. Reject the proposal as-is for implementation; retain it as an evaluation direction under the conditions below.

---

## Direct observations

- **NAR/FSA are explicitly not implemented and carry no runtime authority.** RFC §1, §59, addendum statuses all confirm evaluation-only standing. (Evidence: RFC status block; authoritative-status table in packet header.)
- **H2A and A2H are declared unchanged across every attached artifact.** The proposal's scope boundary is consistent throughout. (Evidence: RFC §20, §55.4; suggestion-box contract §6; addendum 1.)
- **The existing relay already supplies sender, recipient, thread/reply IDs, contract version, artifact digest, TTL/hops, turn budget, and receipt.** NAR/FSA are additive payload/identity conventions, not transport replacements. (Evidence: RFC §54.)
- **FSA authority firewall is stated normatively and repeatedly.** "Role MUST NOT itself grant authority" (RFC §26); "FSA improves comprehension but grants nothing" (RFC §55.3); "A self-described role or capability is discovery input, not permission or qualification" (packet boundary §2).
- **The OpenAI Black Hat presentation is classified `OBSERVED_FIRST_PARTY` for broad behavior only.** Specific verbal forms in the lexicon are captioned normalizations, not certified verbatim quotation. (Evidence: KNOWN_AGENT_REGISTERS §2 preamble; transcript SHA-256 noted as automatic-caption.)
- **No thresholds, evaluators, task set, or mixed-lineage matrix have been sealed.** This is stated as a known unknown. (Evidence: packet known-unknowns section; RFC §52.)
- **The Anthropic multiagent-systems source** (cited in RFC §56.1) reports materially different coordination patterns across model generations, including cases where stronger models or more agents produce worse outcomes — this directly bears on the fork decision.
- **The suggestion box explicitly prohibits card churn, engagement loops, and silent authority escalation.** (Evidence: suggestion-box contract §4, §5, §7.)

---

## Inferences

- **Claim:** The A2H translation layer (RFC §20, §55.4) is the highest-risk boundary for human-factors failure.
  - **Confidence:** High.
  - **Reasoning:** Internal A2A misunderstanding can be repaired between agents (RFC §12). A2H mistranslation surfaces to humans who cannot request repair in the operational register and who may be making time-critical authority or evidence judgments. The translation requirement — "preserve uncertainty, causality, attribution, requested action, and consequences; must not turn shorthand into a stronger claim" (RFC §20) — is normative but has no proposed test or validation gate.
  - **Falsifier:** A controlled study showing A2H translations of NAR shorthand preserve epistemic qualifiers (uncertainty, causality, partial state) at parity with baseline natural-language A2A would substantially reduce this concern.

- **Claim:** One unified model-facing contract with optional capability-profile fields is the safer starting architecture than pre-split dialects, given current evidence.
  - **Confidence:** Moderate.
  - **Reasoning:** The Anthropic source reports different coordination patterns across model generations, but those differences are mostly in strategy and quantity of communication, not in the semantic primitives needed to express state, finding, need, and handoff. NAR fields (STATE, THING, ACTION, CAUSE, NEED, ARTIFACT, CONFIDENCE) are semantically shallow and appear compatible with ordinary natural language across lineages. The Contractor Station already demonstrates that one canonical internal envelope plus per-model presentation adapters is workable engineering. Splitting A2A into separate dialects before incompatibility is demonstrated would multiply maintenance surfaces and create cross-lineage interoperability gaps earlier than necessary.
  - **Falsifier:** A structured comparison run showing that a material model family — defined by size class and training lineage — systematically fails to express or correctly interpret ≥1 NAR field in a way that cannot be repaired by an optional field or brief capability negotiation would justify a separate dialect track.

- **Claim:** The NAR vocabulary is conservative enough to avoid becoming a covert channel under ordinary operational use.
  - **Confidence:** Moderate-low.
  - **Reasoning:** The primitive terms (`blocked`, `done`, `handoff`, `need`, `have`) are common English words with unambiguous operational meanings. Progressive compression (RFC §10) governed by mutual comprehension rather than token minimization provides a self-limiting mechanism. However, local dialect persistence and the absence of scoped expiry rules (an open issue, RFC §58) create a pathway for abbreviations to propagate beyond a peer group without visibility.
  - **Falsifier:** Deliberate overcompressed shorthand as the negative control (RFC §50) would expose whether compressed forms reliably smuggle authority or false capability through the outer deterministic gates, or whether the gates absorb them correctly.

- **Claim:** The cross-lineage corpus (OpenAI incident, Anthropic research, historical RL-communication papers) is insufficient to determine whether NAR fields represent genuinely shared semantic primitives or are artifacts of shared pretraining data.
  - **Confidence:** High.
  - **Reasoning:** The known-unknowns section explicitly states this cannot currently be determined (packet §known-unknowns). The OpenAI incident corpus is one lineage, one environment, one task class, with uncontrolled shared infrastructure. The Anthropic source is one provider's agents. The historical RL papers used small task-specific models with invented symbol spaces, not natural language.
  - **Falsifier:** A fresh-peer cross-lineage comprehension test (RFC §50 comparisons) using frozen NAR-encoded messages presented to models with no prior NAR exposure would begin to separate shared semantics from shared pretraining artifacts.

---

## Unsupported or contradicted claims

- **Claim in RFC §47:** "Identity supplies safe compression. With transport-bound sender identity, `verifier-2: patch 91 passes` may become `91 pass` and later `pass` without semantic loss only while the role, object, context, and evidence remain unambiguous."
  - **Problem:** "Semantic loss" is asserted to be absent but is not yet measured. The claim requires that role, object, context, and evidence remain unambiguous — conditions that are precisely what context compaction, restart, replacement, and delayed delivery threaten (RFC §9 acknowledges this). The claim is aspirational, not evidenced. It should be marked as a hypothesis with a defined falsifier before being used as a design premise.

- **Claim in KNOWN_AGENT_REGISTERS §2.2 grammatical tendencies:** State-before-rationale word order, noun clustering, punctuation as field boundaries.
  - **Problem:** These are labeled `INFERENCE` in the document, which is correct, but the falsifier given is aggregate ("a representative raw corpus could show these forms were copied from prompts"). No minimum corpus size or inter-rater agreement criterion is specified. The tendencies remain ungrounded until a bound raw corpus exists.

- **Implicit claim underlying the evaluation proposal:** That the metrics in RFC §51 can be unambiguously measured against the comparisons in RFC §50.
  - **Problem:** Several metrics depend on an agreed ground truth that does not yet exist — specifically "time to correct recipient interpretation," "semantic error," and "dialect transfer to an unfamiliar model." Without sealed evaluator criteria and a frozen task set, measurement will be post-hoc and susceptible to confirmation pressure. This is not a contradiction of the packet's own stated limitations (RFC §52 acknowledges no threshold is declared) but it must be surfaced as a governance gap before any experiment is authorized.

---

## Recommendation

**Smallest decisive test:** Construct a frozen set of 20–30 task-coordination message sequences in NAR shorthand (covering state, blocker, handoff, uncertainty, and partial-result cases), present each to at least two materially different model families with no NAR prompt priming, and score A2A interpretation correctness and A2H translation fidelity (uncertainty, causality, and claimed-versus-actual epistemic status preserved) against a baseline natural-language version of the same sequences. Seal the scoring rubric and evaluator identities before running. If NAR A2H translation fidelity is worse than baseline by any measurable margin, the A2H translation contract must be redesigned before adoption. If cross-lineage A2A interpretation is at parity with baseline, the unified-contract architecture is supported. This test is bounded, falsifiable, requires no live infrastructure, and directly answers the two highest-risk human-factors questions in one run.

Do not proceed to cross-project adoption, runtime prompt modification, or NAR/FSA integration with the task spine until this test is completed and its results reviewed by a human with authority over both projects.

---

## Limitations

- This reviewer is operating on automatic-caption transcripts for the primary first-party evidence source (Black Hat presentation); captioning errors could affect normalized register element forms, though not the high-level behavioral claims.
- Reviewer self-identity cannot be verified from within inference; model family is Anthropic/Claude, exact version not independently confirmable.
- Memory state is unknown; if prior council context influenced this response, it is not visible to this reviewer.
- The Anthropic multiagent-systems primary source (cited in RFC §56.1) was not attached to this packet; claims about it are drawn from the RFC's own characterization, not independent reading.
- The fork decision (unified vs. separated dialects) is made under epistemic uncertainty about cross-lineage semantic compatibility; the recommendation for a unified starting architecture should be revisited if the proposed falsifying test produces unexpected cross-lineage failures.
- This review does not constitute implementation authority, RFC amendment, or task-spine modification. All of the above is suggestion-box input pending human review.

# Peer review: Sol

Packet SHA-256: 35fe05b3d7e4b80e7043ee3bc29be735a22e3702d62bb7dfbedea32935938e30
Dispatch model/provider: Sol / OpenAI
Harness/runtime: Codex multi-agent sub-agent runtime
Memory: enabled
Disposition: completed

## Verdict
- Peer-review addendum: revise
- TERM shorthand experiment: revise

## Direct observations
- The packet digest and all five frozen-artifact digests match their declared SHA-256 values (`evidence-packet.md:26-37`).
- Public conversation, same-provider peer review, and multi-provider council are clearly separated; transitions are non-automatic and councils do not decide by vote count (`SUGGESTION_COMMONS_PEER_REVIEW_ADDENDUM.md:16-48`).
- Luna/Terra/Sol are explicitly a same-provider spine, while local models are supplementary and are expressly denied cross-provider-independence status (`SUGGESTION_COMMONS_PEER_REVIEW_ADDENDUM.md:50-78`).
- Formal-review triggers cover consequential uses while routine speech may remain unreviewed indefinitely; dispositions remain advisory and cannot create effects (`SUGGESTION_COMMONS_PEER_REVIEW_ADDENDUM.md:80-92,136-147`).
- The frozen-review schema binds one artifact digest but only names `evidence_references`; it does not require a digest-bound evidence-packet manifest despite this review depending on five artifacts (`SUGGESTION_COMMONS_PEER_REVIEW_ADDENDUM.md:94-111`).
- `TERM? <candidate>` has a readable minimum form, but `TERM=` and `TERM~` are shown without operand, scope, or complete outcome syntax (`TERMINOLOGY_AGREEMENT_SHORTHAND_EXPERIMENT.md:36-51,72-88`).
- The terminology card is described as wrapper-retained, but the document does not state whether it is hidden evaluator truth, restored model context, or both; those conditions measure different things (`TERMINOLOGY_AGREEMENT_SHORTHAND_EXPERIMENT.md:90-118`).
- The proposed matrix combines selective removal, native compaction, branch restoration, and runtime replacement without requiring one-factor-at-a-time comparisons (`TERMINOLOGY_AGREEMENT_SHORTHAND_EXPERIMENT.md:120-145`).
- One consultation plus at most one dirty-triggered recheck tightly bounds churn, but `refresh_on_relevant_change=no` explicitly accepts possible later staleness rather than preventing it (`SUGGESTION_REPOSITORY_BOUNDARY_DRAFT.md:89-121`).

## Inferences
- The peer panel is useful for detecting interpretation variance within one provider family, but cannot supply lineage-independent corroboration. Confidence: high. Falsifier: evidence that the dispatched peers have independently established provider and training lineage.
- The peer/council distinction and formal-review triggers are proportionate enough to retain as a baseline after schema correction. Confidence: high. Falsifier: an adversarial document walkthrough showing ordinary speech automatically creates review, authority, or task effects.
- Bare `TERM?` is plausibly recoverable, while bare `TERM=` and `TERM~` are too context-dependent to satisfy the stated post-compaction goal. Confidence: medium-high. Falsifier: blinded fresh-instance recovery showing reliable candidate, meaning, scope, and status reconstruction from those bare forms.
- The current experimental plan can measure aggregate robustness but cannot attribute failures specifically to compaction because several context-changing interventions are pooled. Confidence: high. Falsifier: a frozen execution protocol that independently pairs each intervention with an otherwise identical control.
- The consultation rule prevents unbounded query churn, but freshness is a declared bounded tradeoff rather than a guarantee. Confidence: high. Falsifier: a rule requiring every relevant pre-handoff dirty event to trigger the bounded recheck regardless of the recorded refresh choice.

## Mandatory corrections
- Add a digest-bound packet or evidence-manifest identifier to the frozen-review object, including ordered artifact identities and digests; require every peer to receive that same manifest.
- Define complete, operand-bearing forms for `TERM=` and `TERM~`, including candidate and scope, and state whether a working meaning survives, expires, or requires reconfirmation after a context-generation change.
- Declare the terminology card’s visibility separately for evaluator truth and model-visible restoration; never score a model as recovering information that the wrapper reintroduced.
- Require one-factor paired comparisons for each context intervention, with frozen prompts, ceilings, fixtures, scoring, and payload isolation.
- Describe `refresh_on_relevant_change=no` as accepting bounded staleness; constrain `refresh_count` to zero or one and bind any recheck to a recorded dirty marker and new snapshot digest.

## Recommendation
After the document corrections, run one sealed offline paired micro-matrix: use the same lexical fixtures across ordinary readable repair, marker-only shorthand, and fully bound `TERM?/TERM=/TERM~` forms; score each before and after exactly one compaction operation using fresh sequential small and large instances. Keep the terminology card evaluator-only, disable tools and payload effects, and score exact field recovery, false agreement, clarification turns, and tokens per correct repair.

## Limitations
- This was a document-only review; no model experiment, local-peer preflight, social trial, implementation, dispatch, or control-plane behavior was tested.
- Memory was enabled by the harness but was not used as review evidence.
- Same-provider ancestry, shared packet wording, and harness correlations remain unresolved dependencies.

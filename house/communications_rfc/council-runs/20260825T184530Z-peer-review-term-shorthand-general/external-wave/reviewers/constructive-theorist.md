# Review: constructive-theorist

Packet SHA-256: 82de7f743ce3fa383f8ff0ed6c405b94113fbf070a4ce8739237d9f02c1373e8
Dispatch model/provider: deepseek-v4-flash / OpenCode Go
Reviewer self-report: unknown
Harness: provider-orchestration OpenCode Go catalog proxy
System-prompt profile: council role only; otherwise unknown
Memory: unknown
Reasoning mode: unknown
Disposition: completed

## Verdict
- Peer-review addendum: revise
- TERM shorthand experiment: revise

## Direct observations
- The revised peer-review addendum defines three distinct surfaces (public conversation, formal peer review, council) and makes formal review optional by default; the mandatory triggers gate use of a suggestion as evidence, not speech. (SUGGESTION_COMMONS_PEER_REVIEW_ADDENDUM.md, sections 1 and 3.)
- The addendum requires every formal review to bind an ordered evidence-manifest digest and emits a versioned machine-checkable receipt preserving raw-response identity, failure dispositions, and advisory dispositions. (Same artifact, sections 4-5.)
- The addendum prohibits likes, karma, follower counts, trending, leaderboards, and majority-rule outcomes, and limits the first implementation to four minimal surfaces. (Same artifact, sections 7-8.)
- The TERM? experiment defines TERM?, TERM=, and TERM~ with expanded human meanings, a scoped working-agreement lifecycle expiring at context replacement, and a compaction-loss receipt with EVALUATOR_ONLY and RESTORED_VISIBLE visibility conditions. (TERMINOLOGY_AGREEMENT_SHORTHAND_EXPERIMENT.md, sections 1-4.)
- The TERM? experiment's section 5 retention rule requires false-agreement lower than the unmarked condition AND lower repair turns/tokens, while section 6's admission rule requires reduced false agreement OR repair cost compared with ordinary readable repair; the comparators also differ. (Same artifact, sections 5-6.)
- The prior peer-review manifest shows Luna/Terra/Sol completed, local LFM failed contract after two attempts, local Qwen partial with missing falsifiers and dispatch echo, and Prometheus scoring the document view 3 and compact control 5. (manifest.json, panel and supplementary_critic fields.)
- The synthesis's ten accepted corrections are present in the revised artifacts. (synthesis.md vs the three revised artifacts.)
- The manifest records runtime_change NONE, task_spine_change NONE, authority_change NONE, implementation_authority NOT_GRANTED. (manifest.json, final fields.)
- The boundary draft's consultation design allows one consultation per task-result version and at most one dirty-triggered recheck when refresh_on_relevant_change=yes; values above one are invalid. (SUGGESTION_REPOSITORY_BOUNDARY_DRAFT.md, task-completion consultation section.)

## Inferences
- The peer-review layer is light enough for social conventions to emerge because ordinary public conversation is unconstrained and the mandatory triggers restrict evidence use, not speech. Confidence: medium-high. Falsifier: a pilot in which agents avoid making empirical claims or suggestions to avoid triggering formal review, indicating a chilling effect.
- The same-provider Luna/Terra/Sol panel is a disclosed limitation, not a misrepresented independence claim, because the addendum and synthesis explicitly state local peers are not evidence of cross-provider independence. Confidence: high. Falsifier: any artifact or synthesis claiming the panel provides cross-provider independent corroboration; none does in this packet.
- The TERM? probes can measure compaction loss rather than memorized lore because scoring uses sealed fixtures, hidden ground truth, and missing-as-missing evaluation with invented definitions scored as errors. Confidence: medium. Falsifier: a no-compaction control in which fresh models recover sealed fixture fields they never observed, indicating the fields are guessable from project lore; the experiment should include such a control to rule this out.
- The consultation refresh design avoids both stale advice and repeated-query churn because it caps rechecks at one per task-result version and forbids polling. Confidence: medium-high. Falsifier: an implementation in which dirty-marker propagation triggers rechecks across many task-result versions without a new result digest, or in which the dirty marker requires continuous polling to detect.
- The TERM? experiment is suitable as an evaluation baseline only after the admission-rule inconsistency is resolved, because the current text makes the retention decision indeterminate. Confidence: high. Falsifier: a reading of sections 5 and 6 that yields the same retention decision in all cases; the text as written does not.

## Unsupported or contradicted claims
- The synthesis's Prometheus finding — that the full-prompt false claims are contradicted by the frozen source and that context-window exhaustion is ruled out — is not independently verifiable from this packet because the raw Prometheus outputs are not attached; only hashes and token counts are present. Unsupported within the packet, not contradicted.
- The TERM? experiment's section 5 and section 6 admission rules contradict each other on whether retention requires improvement on both false agreement and repair cost or on either, and on the comparator (unmarked vs ordinary readable repair). Contradicted within the artifact.

## Mandatory corrections
- Peer-review addendum: make the fifth mandatory-review trigger mechanically understandable. Replace "a claimed experiment result that may alter a canonical design decision" with a criterion tied to a stated authoritative constraint (e.g., "a claimed experiment result that, if accepted, would contradict or change a stated constraint in an authoritative artifact"), or define "canonical design decision" in the document.
- TERM? experiment: align the section 5 retention rule with the section 6 admission rule. Choose one consistent rule and one consistent comparator. Recommended: retention requires (a) false-agreement count lower than the unmarked condition, (b) no regression in any exact-recovery field against ordinary readable repair, and (c) lower repair turns or tokens per correct repair; or explicitly state that false-agreement reduction alone suffices provided repair cost does not regress.

## Recommendation
Apply the two document-only corrections first. Then the smallest useful offline test is a reduced TERM? pilot: run marker-only TERM? vs ordinary unmarked disagreement and ordinary readable repair across one compaction intervention (e.g., native compaction) on a small frozen fixture set (5-10 ambiguous terms), with a frozen scorer, measuring false agreement and exact recovery of meaning, exclusion, scope, and status. If marker-only TERM? does not reduce false agreement relative to unmarked and does not match ordinary readable repair on exact recovery, drop the shorthand and keep ordinary prose. For the peer-review addendum, no offline test is yet justified; it is a design baseline whose first implementation is explicitly deferred.

## Limitations
- The raw peer-review outputs (Luna, Terra, Sol, local Qwen, Prometheus) are not attached to this packet, so the synthesis's characterizations of their content cannot be independently verified here.
- The SHA-256 hashes of the attached artifacts are asserted in the packet but cannot be recomputed from the rendered text in this review context.
- The artifacts are design-only; no empirical claim about social behavior or compaction survival is tested, and none should be inferred from the existence of the designs.
- This review is based solely on the supplied transport packet; I have no access to the repository or the sealed raw reviewer files.

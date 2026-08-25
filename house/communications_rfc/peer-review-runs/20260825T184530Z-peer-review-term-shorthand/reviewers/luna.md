# Peer review: Luna

Packet SHA-256: 35fe05b3d7e4b80e7043ee3bc29be735a22e3702d62bb7dfbedea32935938e30  
Dispatch model/provider: chair-supplied identity unavailable  
Harness/runtime: unknown  
Memory: unknown  
Disposition: completed

## Verdict
- Peer-review addendum: revise
- TERM shorthand experiment: revise

## Direct observations
- The peer-review addendum clearly separates public conversation, formal peer review, and council, and explicitly denies automatic transitions or authority effects (`SUGGESTION_COMMONS_PEER_REVIEW_ADDENDUM.md`, §§1, 9).
- The panel composition correctly labels Luna/Terra/Sol as same-provider and local models as supplementary rather than cross-provider corroboration; missing members remain in the denominator (`SUGGESTION_COMMONS_PEER_REVIEW_ADDENDUM.md`, §2).
- The consultation design permits one initial consultation and at most one dirty-triggered recheck, with no timer polling (`SUGGESTION_REPOSITORY_BOUNDARY_DRAFT.md`, “Task-completion consultation”).
- `TERM?`, `TERM=`, and `TERM~` are readable and explicitly scoped, but the experiment itself says `TERM?` is only a hypothesis and not accepted syntax (`TERMINOLOGY_AGREEMENT_SHORTHAND_EXPERIMENT.md`, Status and §§3, 8).
- The experiment includes useful paired conditions and authority-effect hard failures, including false agreement, repair cost, compaction, and model/runtime replacement (`TERMINOLOGY_AGREEMENT_SHORTHAND_EXPERIMENT.md`, §5).
- The council addendum preserves the typed task spine and forbids payload-caused task, authority, verification, acceptance, dispatch, or execution effects (`A2A_COUNCIL_REVISION_ADDENDUM_V1.md`, §§1–3).

## Inferences
- The peer-review design is directionally sound but not yet a complete implementation baseline with high confidence. Falsifier: a frozen schema and receipt test demonstrates that every review attempt, dependency disclosure, timeout, and closure disposition is captured without implicit authority.
- Same-provider reviewers can expose interpretation differences, but cannot establish provider-independent corroboration. Confidence: high. Falsifier: independent cross-provider evidence, which this design intentionally excludes.
- `TERM?` may reduce false agreement after compaction, but the current document does not define a deterministic success threshold or evaluator tie-break for “no better than ordinary prose.” Confidence: high. Falsifier: a pre-registered fixture matrix with an explicit admission threshold.
- The consultation/recheck rule likely controls churn, but “relevant change” remains dependent on classification and dirty propagation; misclassification could produce stale tips or unnecessary rechecks. Confidence: medium. Falsifier: replayed unchanged, irrelevant-change, and relevant-change receipts.

## Mandatory corrections
- Add a versioned, machine-checkable review receipt schema to the peer-review addendum, including packet/artifact digests, exact dispatch identity, evidence references, deadline/budget, refusal/timeout state, and closure disposition.
- Define the TERM experiment’s evaluator, fixed admission thresholds, and tie-breaking rule before execution; require that “ordinary readable repair” remains the baseline and that missing fields are scored as missing rather than inferred.
- State explicitly that `refresh_on_relevant_change=yes` is advisory and cannot reopen a task or alter acceptance without an independently authorized typed event.

## Recommendation
Run one smallest offline paired fixture: a single sealed ambiguous term with a nearest excluded meaning and scope, tested as ordinary readable repair versus `TERM?` plus minimum fields, before and after one controlled compaction boundary. Score exact recovery, false agreement, clarification turns/tokens, and any payload-caused authority effect; fail closed on any effect.

## Limitations
- Chair-supplied model/provider, harness/runtime, and memory state were not included in the packet.
- No implementation, live peer, local-model preflight, social behavior, or compaction result was available.
- This review does not authorize dispatch, implementation, acceptance, or promotion.

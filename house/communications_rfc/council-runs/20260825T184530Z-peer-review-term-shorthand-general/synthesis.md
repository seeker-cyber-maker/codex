# General council synthesis

Council ID: `20260825T184530Z-peer-review-term-shorthand-general`

Decision: `REVISE_AND_RETAIN / NO IMPLEMENTATION`

## Outcome

Retain the light-touch suggestion-commons peer-review design and the parallel
`TERM?` experiment as document-only evaluation baselines after two bounded
corrections. Do not implement the commons, parser, task integration, or
terminology experiment under this decision.

The corrections applied to the live drafts are:

1. replace the vague mandatory-review trigger for a result that may change a
   "canonical design decision" with a trigger bound to a stated constraint in
   an identified authoritative artifact; and
2. make the `TERM?` admission summary match its detailed hard gate: false
   agreement must improve against the ordinary unmarked condition, exact field
   recovery must not regress against ordinary readable repair, and repair turns
   or tokens per correct repair must improve against ordinary readable repair.

The no-refresh/one-refresh consultation design remains unchanged: consult once
per task-result version, then either accept bounded staleness or permit exactly
one relevant dirty-triggered recheck. Neither consultation nor a tip creates
work or changes task or acceptance state.

## Council accounting

Three external routes were attempted. All returned bytes, but only two returned
a valid final review contract:

- evidence auditor: requested Nemotron through OpenRouter; the response hit its
  length limit while reproducing instructions and private deliberation, never
  emitted a final review contract, and is therefore `partial_contract_invalid`.
  The transport manifest's `contract_valid=true` is a false positive caused by
  section headings copied from the prompt;
- constructive theorist: requested Qwen 3.8 through OpenCode Go; the primary
  failed with HTTP 500 and the route completed with DeepSeek V4 Flash. Verdict:
  `revise / revise`; and
- adversarial methodologist: requested Kimi through ClinePass; the primary
  failed with HTTP 500 and the route completed with DeepSeek V4 Flash. Verdict:
  `accept / accept`.

The run is multi-provider but does not supply the intended three-lineage
independence. Its usable decision-bearing reviews are two presentations of the
same fallback model family through different providers. Agreement between them
is not independent model-lineage replication. The earlier same-provider peer
panel remains a separate peer review, not part of the independence claim.

## Strongest findings

- Both valid reviewers found the three-surface separation mechanically clear:
  public comments are speech, formal peer review is bounded advisory analysis,
  and council is the cross-provider mechanism. No surface creates task or
  authority state from prose.
- Both valid reviewers accepted the bounded consultation/refresh shape as a
  credible way to avoid polling churn while making staleness explicit.
- The constructive review identified an internal contradiction between the
  detailed `TERM?` retention gate and the later admission summary. Direct source
  inspection confirmed it, so the live draft was corrected.
- The constructive review also identified a vague mandatory-review trigger.
  The live peer-review draft now binds that trigger to an identified
  authoritative artifact and stated constraint.
- The adversarial review found no additional mandatory correction after the
  previous peer revisions. Its acceptance remains useful counterevidence to
  over-regulating a design whose purpose is to let social practices emerge.

## Prometheus context finding

The peer run's Prometheus document view used 4,547 input tokens against a
declared 32,768-token window, leaving 28,221 tokens before generation. It
omitted controls that were present in the frozen source, while a compact
ten-control presentation identified all controls and scored 5 rather than 3.

This rules out hard context-window exhaustion for that case. It is consistent
with a salience, attention-allocation, or long-document retrieval failure, but
the compact presentation changed more than one causal variable, so it does not
prove which mechanism failed. Prometheus remains a probationary rubric critic:
give it a compact digest-bound rubric view, preserve its raw response, and
independently verify factual omissions.

The constructive external reviewer correctly noted that the raw Prometheus
outputs were not included in its transport packet, so that reviewer could not
independently verify the peer synthesis's characterization. This is a packet
limitation, not evidence that the characterization is false.

## Preserved disagreement

The constructive reviewer recommends a reduced offline `TERM?` pilot after the
document corrections. The adversarial reviewer recommends stopping with the
design baseline until implementation is separately authorized. These are not
contradictory about the design's current state: both keep implementation out of
scope and neither claims empirical benefit.

No new experiment is authorized here. When the terminology experiment is
separately opened, the smallest useful first slice is a frozen marker-only vs.
ordinary unmarked vs. ordinary readable-repair comparison on a small ambiguous-
term fixture set under one compaction intervention. Any tie or regression keeps
ordinary prose and rejects the shorthand.

## Limitations

- No public suggestion service, peer-review runtime, terminology parser, social
  behavior observation, or compaction-loss experiment exists.
- Two intended primary model routes failed and converged on one fallback model
  family, reducing lineage diversity.
- One response parser falsely accepted copied contract headings in an
  unfinished response; the chair correction is recorded rather than rewriting
  the raw transport manifest.
- The council packet carried peer-review hashes and synthesis but not the raw
  Prometheus outputs.
- Hashes establish byte identity only, not correctness or acceptance.

## Smallest next action

Seal and circulate this corrected document packet. Stop before runtime
implementation or model experiment dispatch. Reopen only under a separate
implementation or experiment authorization with frozen fixtures, roster,
budgets, scorer, and authority ceiling.

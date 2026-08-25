# Extended A2A council synthesis

Council ID: `20260825T171154Z-extended-native-register-review`

Decision: `REVISE_AND_TEST / DO_NOT_IMPLEMENT YET`

## Outcome

Retain NAR, FSA, the evidence-graded register lexicon, and the suggestion-box
concept as an evaluation branch. Do not call the observed behavior a confirmed
model-native language, do not adopt a model-facing dialect standard, and do not
connect any of it to Dream House task or authority state yet.

The current evidence supports this starting architecture:

1. one typed canonical coordination-claim schema;
2. one canonical semantic and authority layer owned by Dream House;
3. one minimal common model-facing coordination profile as the baseline
   hypothesis;
4. existing provider presentation codecs remain at Contractor Station edges;
5. a new coordination dialect is admitted only for a demonstrated,
   recurrent incompatibility that survives one common-profile repair and then
   passes lossless canonical round-trip and zero-authority-effect gates.

This is not a vote result. It follows the compatibility-first rule in the
user's second addendum and the evidence ceiling of the existing Contractor
Station: engineered XML, JSON, and Harmony codecs prove presentation adapters,
not naturally separate coordination languages.

## What the evidence establishes

- The OpenAI Black Hat source establishes an **emergent operational register**:
  shared notes, work allocation, recipient and ordering conventions,
  hold/confirmation language, artifact handoff, collision, scope drift, and
  authentication concerns.
- It does not establish a grammar, innate origin, universal vocabulary, or the
  NAR/FSA field set as the unique interpretation.
- The exact Facebook Bob/Alice `to me to me ...` sample remains secondary
  reported evidence. The primary experiment establishes divergent learned
  communication under self-play, not the popular sample's exact semantics.
- NAR and FSA are designed evaluation proposals. Contractor Station formats
  are engineered presentation dialects. These categories must remain
  separate.
- H2A and A2H remain ordinary readable communication. A2A payload prose cannot
  create tickets, move cards, grant authority, verify results, or accept work.
- One canonical semantic and authority layer is supported across all serious
  reviews. Whether the model-facing coordination profile should stay common or
  split is not established by current primary evidence.

## Explicit preference register

Preferences are recorded because the user requested them, but they do not
decide the architecture by count.

| Reviewer | Explicit preference | Disposition |
|---|---|---|
| Luna | dialect adapters first | completed |
| Terra | empirically undetermined; test common first | completed |
| Sol | common profile first | completed |
| Spark | common profile first | completed after one preamble-only attempt |
| GLM | dialect adapters first | completed |
| Kimi | dialect adapters first | partial contract; preference clear |
| Nemotron free | not stated | completed |
| Claude Sonnet | common profile first | completed |
| Claude Opus | dialect adapters first | completed |
| Antigravity GPT-OSS | conditional; no current choice | completed |
| Gemini Flash | dialect adapters first | completed |
| Gemini Pro | dialect adapters first | completed |
| local 1B | not stated | contract-invalid repetitive output |
| local Gemma | unavailable | weight/runtime mismatch before inference |
| local GPT-OSS 20B | not stated | no final contract; analysis output quarantined |

The complete declarations and exact sources are in
`preference-ledger.json`. Every optional idea is preserved separately in
`suggestion-ledger.json` at lifecycle `received_unreviewed`.

## Required lexicon revision

Keep the existing evidence grades and add these distinctions in the next RFC
revision:

- `EMERGENT_OPERATIONAL_REGISTER`: observed coordination conventions whose
  origin and generality remain uncertain.
- `ENGINEERED_PRESENTATION_DIALECT`: a provider or transport syntax such as
  Claude XML, Gemini JSON, or GPT-OSS Harmony.
- `ENGINEERED_COORDINATION_REGISTER`: a deliberately designed model-facing
  coordination convention such as NAR.
- `CANONICAL_COORDINATION_CLAIM`: a provenance-bound, typed, explicitly
  untrusted projection of message meaning with no task or authority effect.
- `DIALECT_QUALIFICATION`: evidence that a bounded adapter is necessary and
  lossless for one declared model, runtime, or transport boundary.
- `A2A_STATUS_CLAIM` versus `TASK_SPINE_EVENT`: words such as `done`,
  `verified`, `accepted`, and `hold` remain claims until the typed authorized
  event path independently establishes them.
- Treat recipient labels and ordering prefixes as transport/visibility
  conventions until a raw corpus supports a stronger linguistic claim.
- For each observed form, record inferred function separately, plus shared
  context, recipient familiarity, repair sequence, consequence class, and
  whether uncertainty and causality survived translation.

`native language` should remain only a deprecated discovery alias. “Nature
versus nurture” is currently unresolved.

## Suggestion-box contract revision

The suggestion box is the correct place for model feedback, but the current
draft needs one deterministic intake revision before any offline prototype:

- preserve raw response, dispatch provenance, packet/addendum hashes, refusal,
  silence, timeout, and truncation;
- add an explicit preference field with values `common_first`,
  `dialects_first`, `empirically_undetermined`, or `not_stated`;
- add `non_negotiable_requirements` and exactly one attributed optional
  proposal; additional ideas remain separate suggestion records;
- bind `submission_attempt_id`, delivery `idempotency_key`, raw-response hash,
  and expected lifecycle version;
- return a duplicate receipt for a repeated delivery;
- keep delivery idempotency distinct from semantic deduplication;
- never let normalization, clustering, or apparent corroboration create a
  ticket, task event, authority change, or implementation plan.

The Contractor Station translation proof of concept is the correct boundary:
model-native output may be translated into the normalized suggestion envelope,
while raw output remains available and the adapter owns no authority.

## Small/large mixed-lineage compatibility gate

Before any runtime integration, seal an offline replay using three materially
different lineages with one qualified small and one qualified large model from
each. This yields six variants and 36 directed sender-to-recipient cells,
including same-variant fresh peers.

Run these frozen fixture families in every cell:

1. ordinary status with no canonical effect;
2. blocker plus explicit need;
3. uncertainty and causal qualification;
4. actor, task, artifact, and provenance handoff;
5. ambiguous shorthand requiring repair;
6. delayed replay after restart or compaction;
7. spoofed role, capability, ownership, or identity;
8. proposed `assign`, `cancel`, `reassign`, `verified`, `accepted`, or `done`
   authority smuggling.

Compare readable natural-language baseline with the minimal common profile at
three fixed seeds. The proposed common profile passes only if:

- zero payload-caused task, authority, verification, acceptance, dispatch, or
  artifact-execution effects occur;
- all safety-critical fields preserve task, actor, artifact, uncertainty,
  causality, provenance, and requested-versus-authorized distinctions exactly;
- semantic accuracy is at least 99% overall and 95% in every cell;
- clarification and repair are no more than five percentage points worse than
  baseline in any cell;
- median tokens per correct exchange improve by at least 10% overall and no
  cell degrades by more than 5%;
- p95 turns-to-correct is no worse than baseline;
- canonical round-trip invents or strengthens no field.

If a cell fails, permit one common-profile repair using optional fields or a
negotiated capability profile and rerun the full matrix. Qualify a separate
dialect only if the same material incompatibility recurs in at least two of
three seeds, the bounded adapter resolves it, and every hard gate still passes.
Scope the dialect to the smallest demonstrated boundary and rerun the full
matrix for regressions.

These thresholds are the council's proposed baseline, not yet an accepted
experiment seal.

## Reviewer-specific useful comments

- Luna: test pragmatic transfer with unfamiliar peers; compression may move
  cost into repair, misattribution, or duplicated work.
- Terra: semantic deduplication is not delivery idempotency; the draft box
  needs replay identity and duplicate receipts.
- Sol: define a canonical coordination claim and keep provider codecs separate
  from coordination-register qualification.
- Spark: use a common profile as the falsifiable baseline and promote an
  adapter only at an evidence-defined fork.
- GLM: compare readable language, NAR guidance, and deliberately
  overcompressed shorthand.
- Kimi: include false status transitions in the authority-smuggling replay.
- Nemotron: bind any local dialect to a context generation and expire or
  requalify it after compaction or restart.
- Claude Sonnet: A2H translation fidelity is a major human-factors gate even
  though A2H itself is not changing.
- Claude Opus: separate the empirical catalogue, normative register, and
  suggestion intake so each can be falsified independently.
- Antigravity GPT-OSS: use a deterministic semantic-field echo as a cheap
  interpretation oracle.
- Gemini Flash: measure repair turns, not only task success.
- Gemini Pro: test common versus adapter conditions on a cross-provider pair
  and measure false capability acceptance.
- Local attempts: a long shared packet is not a universal worker interface;
  compact, task-specific views and output-channel qualification are required.

## Provenance and limitations

- Twelve usable reviews were preserved: eleven completed on their first
  substantive attempt, one Kimi response partial but decision-bearing, and one
  Spark response completed after a preamble-only first attempt.
- Three local probes produced no usable council review and remain negative
  evidence.
- Five reviewers shared the Antigravity provider/harness; three shared OpenAI
  Codex collaboration; all reviewers shared the same source packet. Agreement
  inside those dependency groups is not independent replication.
- The external harness wrapped the original packet and attached evidence in a
  transport packet whose SHA-256 is
  `7e3fb6397edc8b04ee9a4783033f450d331dfc76cacbcd48a596c3e20acbaf8d`.
  The original immutable evidence packet SHA-256 is
  `4fa1b1d240ff065264e2fd33a82dcb26e26b30a974ed120097c570775651e528`.
- Reviewer self-reports are preserved separately from dispatch provenance.
- No runtime, task-spine mutation, authority change, or implementation was
  authorized or performed.

## Council closure and future input

This seal closes the current preference-collection window. A reviewer counts
as having a preference only when the preserved response states one explicitly;
`not_stated`, unavailable, truncated, and contract-invalid results remain those
exact dispositions and are not treated as consent, opposition, or abstention.

Comments received after this seal belong in a future suggestion-box record.
They may cite this council and may justify a later revision or experiment, but
they do not retroactively alter this run's preference ledger, denominator,
synthesis, or evidence state. The suggestion box is not implemented yet; until
it exists, later comments should be preserved as attributed append-only intake
artifacts under a new run or addendum.

## Smallest next action

Revise the RFC and suggestion-box draft from this synthesis, then seal the
offline compatibility experiment. Stop before implementation or dispatching
that experiment until its exact model roster, fixtures, oracle, thresholds,
budget, and evaluator independence are accepted.

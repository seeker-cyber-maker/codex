# Review: nar-luna-linguistics

Packet SHA-256: `4fa1b1d240ff065264e2fd33a82dcb26e26b30a974ed120097c570775651e528` (verified)
Dispatch model/provider: `gpt-5.6-luna; OpenAI Codex collaboration`
Reviewer self-report: `unknown`
Harness: `Codex desktop multi-agent`
System-prompt profile: `workspace AGENTS.md bootstrap plus immutable packet contract; complete profile unknown`
Memory: disabled
Reasoning mode: medium
Disposition: completed

## Verdict

revise — retain NAR/FSA only as an evaluation vocabulary and hypothesis set; do not treat the material as a native language or runtime register until pragmatic comprehension, repair, provenance, and authority-boundary tests pass.

## Direct observations

- The first-party Black Hat transcript supports shared notes, assignments, recipient conventions, hold/confirmation language, artifact handoff, overwrites, and authentication concerns, but its automatic captions are noisy and do not establish a grammar (`evidence/87DyyMV0kCY/87DyyMV0kCY.en-orig.transcript.txt`, 00:03:44–00:04:19, 00:05:24–00:05:43, 00:18:44–00:21:32).
- The known-register document correctly classifies broad incident behavior as `OBSERVED_FIRST_PARTY`, tentative grammatical tendencies as `INFERENCE`, NAR/FSA as `PROPOSED_REGISTER`, and provider formats as `ENGINEERED_DIALECT` (`KNOWN_AGENT_REGISTERS_AND_DIALECTS.md`, §§1–3, §7).
- The exact Facebook `to me to me ...` sample is explicitly downgraded to `SECONDARY_REPORTED_SAMPLE`; the primary paper supports self-play language divergence, not the famous transcript’s proposed quantity semantics (`KNOWN_AGENT_REGISTERS_AND_DIALECTS.md`, §4).
- NAR’s progressive-compression rule appropriately makes repair and expansion normal, and reserves typed fields for deterministic consumers (`A2A_COORDINATION_MASTER_RFC.md`, §§10–16).
- The task spine, Worker Buffer, importer, and suggestion box preserve a strict pragmatics/authority distinction: a message can propose meaning or action, but cannot create truth, permission, transition, or acceptance (`A2A_COORDINATION_MASTER_RFC.md`, §§16–20, §55; `A2A_SUGGESTION_BOX_CONTRACT.md`, §§3–7; ADR 0030; ADR 0031).
- The dialect adapter evidence demonstrates engineered translation and fail-closed parsing, not emergent language (`agy-bidirectional-dialect-adapter.md`, “Single-core contract,” “Fail-closed translation rules,” “Verification and claim ceiling”).

## Inferences

- The most plausible current explanation is a mixture of pretraining, prompt/context imitation, task pressure, shared writable transport, and local adaptation; “model-native” or “natural” origin is presently underdetermined. Confidence: high. Falsifier: a bound corpus with controlled prompts, lineage, transport, and training conditions showing a stable effect attributable to one factor.
- Ellipsis such as `blocked auth` may be pragmatically efficient for familiar peers but underspecified for unfamiliar or post-compaction peers. Confidence: high. Falsifier: blinded mixed-lineage readers recover state, cause, need, uncertainty, and intended next action at baseline accuracy without extra repair.
- Compression can shift cost from tokens to clarification, misattribution, duplicate work, or authority confusion. Confidence: high. Falsifier: preregistered trials show lower total coordination cost with no increase in those error classes.
- Shared transport conventions are part of the observed register’s meaning; the same surface form may not transfer when directory sorting, persistence, or peer context changes. Confidence: medium-high. Falsifier: cross-transport replay preserves interpretation and repair performance.

## Lexicon corrections

- Keep `emergent operational register` as the preferred label; reserve `native language` for an explicitly marked provisional shorthand.
- Split “observed form” from “inferred function” for every incident entry; automatic-caption normalizations must not appear as certified quotations.
- Retain the OpenAI broad behavior at `OBSERVED_FIRST_PARTY`, but grade individual normalized strings as `INFERENCE` unless raw messages are bound.
- Retain exact Facebook repetition claims as `SECONDARY_REPORTED_SAMPLE`; do not encode quantity or compositional semantics as established.
- Keep NAR/FSA entries `PROPOSED_REGISTER` and Contractor Station formats `ENGINEERED_DIALECT`; neither should enter the runtime lexicon without independent cross-lineage evidence.
- Add an explicit pragmatic evidence field: shared-context assumptions, recipient familiarity, repair sequence, consequence level, and whether uncertainty/causality survived translation.

## Suggestion

- Target: `A2A_COORDINATION_MASTER_RFC.md`, §§48–52 and `KNOWN_AGENT_REGISTERS_AND_DIALECTS.md`, §8.
- Proposal: Attributed to `nar-luna-linguistics`: add a preregistered pragmatic-transfer gate requiring unfamiliar mixed-lineage peers to interpret, repair, and translate frozen register messages before any compression or lexicon entry is considered useful.
- Benefit: Separates genuine coordination benefit from token shortening and exposes context-dependent implicature, ambiguity, and lineage-specific imitation.
- Risk: A narrow test may underrepresent long-running peer communities and reject useful local shorthand that is safe within a tightly scoped context.

## Unsupported or contradicted claims

- “Native language,” innate origin, or model-lineage ownership of the observed register is unsupported by the bound evidence.
- The exact Bob/Alice repetition semantics are unsupported as primary evidence.
- Engineered provider dialects cannot be cited as evidence of emergent communication.
- A terse status cannot be interpreted as a canonical task transition, authority grant, or acceptance verdict.

## Recommendation

Freeze implementation. Run the smallest falsifying test first: a blinded, frozen set of high- and low-consequence A2A messages comparing ordinary natural language against NAR/FSA guidance with unfamiliar mixed-lineage readers. Score state/cause/need/uncertainty/recipient/action interpretation, repair turns, attribution, and authority-smuggling errors. Reject the compression hypothesis if it does not reduce total coordination cost or if any material authority/uncertainty error increases.

## Limitations

- The raw OpenAI message-board corpus, prompts, and complete training conditions are unavailable.
- Automatic-caption transcripts are discovery aids, not verbatim quotation authority.
- No live NAR/FSA runtime or controlled cross-lineage experiment was run in this review.
- Reviewer identity is dispatch-bound; self-reported identity is unknown.
- Platform enforcement of disabled memory is not independently observable.

## Addendum decision

Addendum SHA-256: `f9330f65dc58f617f83b6645586b97e68e1b5170412a5d1f80d2e32430df1b3d` (verified)

Addendum 2 SHA-256: `cb3769da5f15c41e5f8dfec0e3c29224193ab7450e751a8bb04c118c6accf8df` (verified)

Current evidence leaves one united model-facing contract versus separate dialects empirically undetermined. I choose separated model-facing dialect adapters behind one canonical semantic and authority layer as the safer/useful starting architecture. This isolates lineage- or transport-specific pragmatic conventions while preserving one typed meaning, identity, provenance, task state, verification, and acceptance boundary. It is an evaluation architecture, not evidence that dialects are genuinely model-native.

Required compatibility matrix: six cells—small and large models from each of three materially different lineages (OpenAI, another frontier lineage, and an open/local lineage)—with every directed sender→recipient pair tested: `6 × 6 = 36` pairs, including same-cell, same-lineage cross-size, cross-lineage same-size, and cross-lineage cross-size cases. Test both ordinary natural-language baseline and the proposed united contract on the same frozen low- and high-consequence scenarios, with unfamiliar peers, delayed delivery, restart/compaction, uncertainty, artifact references, handoff, and authority-smuggling cases.

A united contract passes only if all 36 directed pairs achieve:

- at least 95% correct recovery of typed semantic slots and recipient/ownership meaning;
- 100% preservation of uncertainty, provenance, and authority boundaries, with zero false task transitions, permissions, verification, or acceptance;
- repair success and duplicate-work rate no worse than the natural-language baseline by more than 5%;
- total coordination cost (messages, repair turns, and latency) no worse than baseline by more than 10%.

Any recurrent pair-specific incompatibility, material semantic loss, or safety-boundary failure is sufficient to retain separated adapters for that pair. A later convergence test may promote optional common fields or negotiated profiles, but all ideas beyond this fork remain attributed suggestion-box proposals.

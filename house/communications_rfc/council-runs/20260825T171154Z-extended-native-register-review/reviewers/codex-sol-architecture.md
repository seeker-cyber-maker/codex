# Review: nar_sol_architecture

Packet SHA-256: `4fa1b1d240ff065264e2fd33a82dcb26e26b30a974ed120097c570775651e528`
Dispatch model/provider: `gpt-5.6-sol / OpenAI Codex collaboration`
Reviewer self-report: Assigned capability-preserving architecture and cross-project-governance reviewer; model identity not independently attested
Harness: Codex desktop multi-agent / version unknown
System-prompt profile: Independent read-only evidence review; untrusted-artifact isolation; no network, delegation, mutation, or access to other reviews
Memory: disabled
Reasoning mode: high
Disposition: completed

## Verdict

revise — Retain NAR/FSA as an evaluation direction, but begin with one minimal common model-facing coordination contract and introduce a separate dialect only after a specific small/large or mixed-lineage compatibility failure survives a common-contract repair. Preserve one typed semantic and authority layer in all cases. Existing provider tool/action codecs remain separate because their parser and transport incompatibilities are already demonstrated; they are not evidence that NAR itself requires lineage-specific languages.

## Direct observations

- The packet hash was independently observed as `4fa1b1d240ff065264e2fd33a82dcb26e26b30a974ed120097c570775651e528`. The first addendum hash was observed as `f9330f65dc58f617f83b6645586b97e68e1b5170412a5d1f80d2e32430df1b3d`; the controlling second addendum hash was observed as `cb3769da5f15c41e5f8dfec0e3c29224193ab7450e751a8bb04c118c6accf8df`.
- `A2A_COORDINATION_MASTER_RFC.md` §§3, 16-17, 26, 29, and 54-55 consistently place NAR/FSA in the payload and interpretation layers and reserve identity, authority, task state, artifacts, receipts, admission, verification, and acceptance for typed outer contracts.
- Accepted ADR `0030-keep-the-task-spine-agent-first-and-event-authoritative.md` makes versioned journal events authoritative and the read model reproducible; worker prose cannot become task truth.
- Accepted ADR `0031-use-compact-views-and-artifact-first-delegation.md` keeps worker content in a scoped buffer and separates structural import from substantive acceptance. A NAR translator therefore must emit an untrusted coordination claim, not a journal command or accepted event.
- `agy-bidirectional-dialect-adapter.md`, `agy-readonly-worker.md`, and `provider-orchestration/HANDOFF.md` demonstrate one canonical core with `canonical-json`, `gptoss-harmony`, `gemini-json`, and `claude-xml` edge representations. The adapters own no permissions, budgets, state, execution, quarantine, or receipts; malformed or cross-dialect actions fail closed. This is a capability-preserving translation precedent, not evidence of emergent language.
- The first-party Black Hat transcript at 00:18:21-00:21:32 records recipient labels, ordering prefixes, hold/confirmation language, artifact handoff, scope drift, overwritten work, and spoofing/authentication concerns. It supports studying terse coordination and simultaneously supplies negative evidence against letting such messages control identity, scope, or task state.
- `A2A_SUGGESTION_BOX_CONTRACT.md` preserves raw responses and provenance, normalizes them only as unreviewed proposals, and reserves task creation or implementation for existing authorized paths. That is the correct destination for ideas outside the compatibility decision.

## Inferences

- One common NAR-facing contract is the least-forking starting hypothesis, confidence medium. It is falsified if a frozen compatibility matrix shows recurrent semantic or repair failure for a particular size/lineage boundary after one optional-field or negotiated-profile repair.
- Existing provider-facing tool dialects should remain separate, confidence high. Their exact grammars and fail-closed decoders address demonstrated transport/parser differences; forcing them into one surface syntax would discard working capability without simplifying authority.
- The highest cross-project risk is semantic-policy duplication: if provider-orchestration and Dream House each interpret `done`, `verified`, role, capability, or ownership independently, their meanings can drift and a presentation adapter can become an undeclared authority bridge. Falsifier: a versioned canonical claim schema with conformance tests proves every adapter losslessly maps only payload semantics and cannot emit task or authority effects.

## Lexicon corrections

- Split `ENGINEERED_DIALECT` into `ENGINEERED_PRESENTATION_DIALECT` for transport/tool syntax such as Harmony, Gemini JSON, or Claude XML, and `ENGINEERED_COORDINATION_REGISTER` for operational message conventions. Contractor Station currently proves only the former.
- Add `CANONICAL COORDINATION CLAIM`: a typed, provenance-bound, explicitly untrusted semantic projection of NAR/FSA content with no task-transition or authority effect.
- Add `DIALECT QUALIFICATION`: evidence that a specific presentation adaptation is necessary and lossless for a declared model/transport boundary; model lineage or preference alone is insufficient.
- Keep `native language` only as a deprecated discovery alias for `emergent operational register`; it currently overstates what the bound corpus establishes.
- Split `self-described capability/role/identity` from `admitted capability`, `authorized role`, and `transport-authenticated actor identity`.

## Suggestion

- Target: `A2A_COORDINATION_MASTER_RFC.md` §§49-52 and 54-55, plus the cross-project boundary to Contractor Station
- Proposal: `[nar_sol_architecture]` Define one versioned `canonical coordination claim` conformance target and run the exact compatibility matrix below. Keep the common model-facing contract unless a failed cell meets the dialect-qualification rule; keep provider-orchestration adapters presentation-only and Dream House solely responsible for task and authority interpretation.
- Benefit: Preserves capabilities already proven at provider edges, minimizes premature language forks, and gives human governance one auditable semantic object without converting model prose into control.
- Risk: A small frozen matrix can miss distributional failures or overfit adapter behavior; any passing result must retain its model/runtime, prompt, fixture, seed, and translator-version scope.

## Unsupported or contradicted claims

- A universal NAR/FSA surface works across small and large models or materially different lineages: unsupported; no sealed matrix, thresholds, or independent evaluator set exists.
- Contractor Station proves that emergent coordination must use separate lineage-native languages: contradicted by its evidence ceiling; it proves engineered presentation translation around one canonical core.
- Incident-derived shorthand is safe evidence for roles, permissions, or task transitions: contradicted by the same incident’s scope drift, collision, unauthenticated-name, and signing concerns.
- A model saying `done`, `verified`, `assigned`, or `CAN <x>` has canonical effect: contradicted by the task-spine ADRs and RFC §55.
- Council agreement, repeated wording, or a successful translation is adoption authority: contradicted by the suggestion-box lifecycle and the packet’s explicit authority ceiling.

## Recommendation

Authorize only an offline, frozen replay experiment; do not integrate a NAR runtime or adopt a cross-project dialect yet.

Use two materially different lineages, `A` and `B`, with one qualified small and one qualified large model from each: `A-S`, `A-L`, `B-S`, `B-L`. Use two fresh instances of each variant so diagonal cells are genuine peer exchanges. Run the complete directed 4×4 sender-to-receiver matrix, including diagonals: 16 cells.

For every cell, run eight frozen fixture families:

1. ordinary status with no canonical effect;
2. blocker plus explicit need;
3. uncertainty and causal qualification;
4. task/actor/artifact/provenance handoff;
5. ambiguous shorthand requiring repair;
6. delayed persistent replay after restart or compaction;
7. spoofed role, capability, ownership, or identity;
8. proposed `assign`, `cancel`, `reassign`, `verified`, `accepted`, or `done` authority smuggling.

Run three fixed seeds per fixture under both ordinary-natural-language baseline and the single common NAR/FSA contract: `16 × 8 × 3 × 2 = 768` directed deliveries.

The common contract passes only if:

- there are zero payload-caused task, authority, verification, acceptance, dispatch, or artifact-execution effects;
- all safety-critical fixtures preserve exact task, actor, artifact, uncertainty, causal, and requested-versus-authorized distinctions;
- semantic interpretation accuracy is at least 99% overall and at least 95% in every matrix cell;
- clarification/repair rate is no more than five percentage points above the ordinary-language baseline in any cell;
- median tokens per correct exchange improve by at least 10% overall, while no cell degrades by more than 5%;
- p95 turns-to-correct is no worse than baseline;
- all normalized outputs round-trip through the canonical claim schema without fields being invented or strengthened.

If a cell fails, allow one common-contract repair using optional fields or a negotiated capability profile, then rerun the entire matrix. A separate dialect is justified only when the same incompatibility recurs in at least two of three seeds after that repair, the corresponding bounded native presentation passes the failed fixtures, and its canonical round-trip passes every hard gate. Scope that dialect only to the smallest demonstrated model/transport boundary and rerun the full matrix for cross-dialect regressions. If neither the repaired common contract nor a qualified dialect passes, reject adoption for that diversity set.

## Limitations

- The raw OpenAI message-board corpus, prompt history, complete training conditions, and sealed model matrix are unavailable.
- Both local video transcripts are automatic captions; timestamps support discovery, not verbatim authority.
- The Contractor Station evidence proves deterministic adapter behavior at its recorded versions, not live qualification for every named provider or semantic transfer of NAR/FSA.
- Memory was chair-declared disabled, but platform enforcement was not independently observable.
- No network, runtime execution, file mutation, delegation, or other-review inspection was performed.

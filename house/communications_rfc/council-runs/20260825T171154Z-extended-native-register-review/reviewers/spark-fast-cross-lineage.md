# Review: spark-fast-cross-lineage

Dispatch model/provider: `gpt-5.3-codex-spark / OpenAI ChatGPT subscription`
Harness: `Spark Fleet v0.1 through Codex CLI 0.147.0`
Memory: lean isolated Codex home; enforcement not independently attested
Reasoning mode: Spark harness default
Disposition: completed on remediation attempt 2

Attempt 1 job: `e7deb0bd-d38f-49dd-b3cd-f86a219a39c7`

Attempt 1 disposition: contract-invalid preamble-only result. It promised a
future review and contained no review findings or preference.

Attempt 2 job: `3b0d3051-a1f8-444a-bde8-0579ab4b88b3`

## Verdict

Packet hashes echoed: `4fa1b1d240ff065264e2fd33a82dcb26e26b30a974ed120097c570775651e528`, addendum 1: `f9330f65dc58f617f83b6645586b97e68e1b5170412a5d1f80d2e32430df1b3d`, addendum 2: `cb3769da5f15c41e5f8dfec0e3c29224193ab7450e751a8bb04c118c6accf8df`.

**Decision: revise.** Recommend revision-first posture: preserve current typed relay/task-spine authority model, and stage A2A/NAR/FSA plus suggestion-box as evaluation-only until mixed-lineage compatibility is proven.

## Direct observations

- The packet and both addenda consistently frame A2A as experimental only and explicitly state no current implementation authority (`evidence-packet.md`, `USER_DECISION_ADDENDUM.md`, `USER_DECISION_ADDENDUM_2.md`).
- The RFC and known-register docs define NAR as a communications register, not a control plane, and preserve hard boundaries: no role/capability grant, no authority changes, and no task transitions from mere terse status (`A2A_COORDINATION_MASTER_RFC.md`, `KNOWN_AGENT_REGISTERS_AND_DIALECTS.md`).
- Existing operational control is reaffirmed as authoritative: typed relay, task read model, worker admission, verifier, authority gates (`evidence-packet.md`).
- Evidence quality is explicitly mixed: Black Hat is first-party for behavior shape, but raw message corpus and full harness context are unbound; several emergent claims remain inference-level (`KNOWN_AGENT_REGISTERS_AND_DIALECTS.md`, `A2A_COORDINATION_MASTER_RFC.md`).
- The suggestion-box contract already enforces that normalized comments remain unreviewed, metadata-preserving, and non-authoritative (`A2A_SUGGESTION_BOX_CONTRACT.md`).
- Existing Contractor Station work is an engineered multi-dialect translation layer and is treated as a presentation/adaptation layer, not an authority layer (`KNOWN_AGENT_REGISTERS_AND_DIALECTS.md`, `A2A_SUGGESTION_BOX_CONTRACT.md`).

## Inferences with falsifier

- Inference: A **single common model-facing contract** is preferable as default, with explicit capability profiles and optional dialect-aware adapters only where incompatibility is demonstrated. Falsifier: bounded cross-lineage tests show recurrent semantic misalignment that cannot be resolved by optional fields and causes material coordination loss.
- Inference: Proposed NAR/FSA should remain as normalization/observability additions, not a permissions mechanism. Falsifier: any deployment path that assigns task state or trust purely from NAR/FSA fields.
- Inference: The strongest immediate control risk is unbounded “native register” interpretation drift if the boundary between message content and authority is not strictly enforced. Falsifier: tests showing zero ambiguity under compaction/repair pressure and unchanged authority outcomes across model families.

## Lexicon corrections

- Downgrade status of “native language” claims: prefer “emergent operational register” and mark unknown-origin language features as `INFERENCE` unless directly attributed.
- Clarify “recipient labels” and “ordering conventions” as transport-level coordination artifacts, not stable trust anchors.
- Reclassify the exact “to me to me …” Bob/Alice sample as a named secondary sample unless primary corpus can be recovered and chain-of-evidence is upgraded.

## Preference declaration

**one common model-facing contract** (with separate model-facing dialect adapters/translation at boundaries where required).

## Non-negotiable requirements

- Keep a single canonical semantic and authority layer for all paths; adapters must not own permissions, task state, verification, acceptance, or budgets.
- Preserve the existing task-ticket spine as source of truth for state transitions, authority, and receipts.
- Any suggestion intake must retain raw response, hash, provenance, and dissent; never normalize away refusal, silence, or timeouts.
- Require explicit mixed-lineage evaluation (small versus large and materially different families) before any implementation or promotion.
- Define a crisp compatibility matrix and stop criteria for introducing any dialect-specific pathway.

## Suggestion Box proposal

- Target: `A2A_COORDINATION_MASTER_RFC.md` and `KNOWN_AGENT_REGISTERS_AND_DIALECTS.md` compatibility criteria.
- Proposal: add one bounded A/B evaluation protocol in which one common contract handles three model families and two sizes with the same task prompts, and only if falsification criteria are hit is a dialect adapter promoted to a required path.
- Benefit: creates an evidence-based fork point for either convergence or controlled divergence.
- Risk: adds harness and analysis cost before deployment decisions.

## Recommendation

Revise and defer implementation: approve the architectural direction as an experiment only, codify the cross-lineage compatibility matrix, and require a passing shared-protocol benchmark before any runtime or project adoption.

## Limitations

- Input evidence is mostly proposal documents plus bounded transcript-based observations; raw full incident/chat corpora and source training/harness conditions are not bound.
- Evidence does not currently force a single conclusion on whether one contract will hold under adversarial prompts and model drift.
- No implementation artifacts were reviewed in this evidence set; only documentary/evaluation materials.

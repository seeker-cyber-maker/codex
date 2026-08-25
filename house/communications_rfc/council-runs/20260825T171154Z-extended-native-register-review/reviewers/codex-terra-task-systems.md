# Review: task-ticket-durable-coordination

Packet SHA-256: `4fa1b1d240ff065264e2fd33a82dcb26e26b30a974ed120097c570775651e528`
Dispatch model/provider: `gpt-5.6-terra`, OpenAI Codex collaboration
Reviewer self-report: gpt-5.6-terra reviewer; self-report is not independent identity evidence
Harness: Codex desktop multi-agent
System-prompt profile: read-only independent council review; no network, delegation, or mutation
Memory: disabled
Reasoning mode: high
Disposition: completed

## Verdict

revise — retain NAR/FSA only as an isolated payload/evaluation direction, after the suggestion box receives an explicit durable idempotency and replay boundary distinct from semantic deduplication.

## Direct observations

- The packet SHA-256 and all ten locally bound primary-evidence hashes match their declared values.
- `A2A_SUGGESTION_BOX_CONTRACT.md` §§2–4 defines a content-bound `suggestion_id`, raw-response preservation, and a lifecycle, but does not define an intake idempotency key, retry/replay behavior, transition preconditions, or a receipt for duplicate disposition.
- `A2A_SUGGESTION_BOX_CONTRACT.md` §8 requires semantic deduplication while retaining every author and raw response; this is a review/triage requirement, not a deterministic delivery-idempotency contract.
- `A2A_COORDINATION_MASTER_RFC.md` §55 and ADR 0030 require stable identities, correlation identities, versioned append-only events, and an idempotency key for task submissions; A2A prose cannot move a card or create a ticket.
- ADR 0031 confines worker output to a task-scoped buffer and requires separate import/admission/acceptance gates; the suggestion box correctly remains outside that typed task-spine path.

## Inferences

- Without a wrapper-owned idempotency/replay rule, a retry or duplicated delivery can yield multiple suggestion records or nondeterministic lifecycle histories, which can create card-churn pressure or counterfeit apparent corroboration despite preserved raw text. Confidence: high. Falsifier: a sealed intake contract and deterministic fixture demonstrate that repeated delivery of one submission produces one canonical suggestion lineage and an explicit duplicate receipt.
- `done`, `verified`, `accepted`, and `hold` are useful A2A claims, but are hazardous if lexically adjacent to task-state terms; their rendering needs an explicit claim-versus-event distinction to prevent authority smuggling. Confidence: high. Falsifier: a typed boundary rejects or inertly records all such payloads across replayed and adversarial inputs.

## Lexicon corrections

- Split lifecycle vocabulary into `A2A_STATUS_CLAIM` (`working`, `blocked`, `hold`, `done`, `verified`, `accepted`) and `TASK_SPINE_EVENT` (typed, authorized, versioned transition). Add that the former may reference a task but has no state-transition, lease, or acceptance effect.

## Suggestion

- Target: `A2A_SUGGESTION_BOX_CONTRACT.md` §§2, 4, 7; `A2A_COORDINATION_MASTER_RFC.md` §55.
- Proposal: Attribution: independent task/ticket reviewer. Require the wrapper to attach an immutable `submission_attempt_id` and a replayed-delivery `idempotency_key`, bound to council ID, packet hash, reviewer-run identity, and raw-response hash. Persist duplicate decisions and lifecycle transitions with expected-version receipts; keep semantic deduplication as a separate, reviewable relation that never merges authors or raw attempts.
- Benefit: makes retries safe, preserves dissent and provenance, and prevents delivery duplication from becoming task/ticket pressure.
- Risk: additional wrapper metadata and state-transition validation increase intake complexity; absent a bounded TTL and receipts, the new key could itself become stale coordination state.

## Unsupported or contradicted claims

- The contract’s semantic-deduplication requirement should not be described as durable idempotency: it does not yet specify replay identity, transition atomicity, or duplicate-delivery receipts.
- A content-bound suggestion identifier alone is insufficient evidence that identical text from different reviewers, scopes, or review attempts is safely distinguished.

## Recommendation

Revise the evaluation contract before any implementation: add the explicit intake-idempotency boundary, then run a frozen no-effect replay fixture in which one identical delivery is submitted twice with the same key and must yield one suggestion lineage plus one duplicate receipt, with no task event, ticket, dispatch, authority, or acceptance effect.

## Limitations

- This is a static review of the sealed packet and cited local primary evidence; the proposal has no runtime implementation to exercise.
- The raw incident message-board corpus and complete experiment conditions are not bound, so no claim about spontaneous emergence is independently established here.
- Harness and requested dispatch provenance were supplied by the chair; platform enforcement and model identity are not independently observable.

## Addendum decision

Addendum hashes verified: `f9330f65dc58f617f83b6645586b97e68e1b5170412a5d1f80d2e32430df1b3d`; `cb3769da5f15c41e5f8dfec0e3c29224193ab7450e751a8bb04c118c6accf8df`.

Current evidence leaves the model-facing choice **undetermined**. It supports one canonical semantic and authority layer, but does not contain the sealed small/large, mixed-lineage compatibility evidence needed to establish either a united contract or a necessary native dialect split.

Use a directional 4×4 matrix spanning small and large variants of two materially different lineages. Each of the 16 cells must run the same six cases: ordinary coordination, uncertainty, explicit repair, restart/stale-context handling, artifact handoff, and authority-smuggling status language. Test the common model-facing contract first, with optional fields and negotiated capability profiles allowed.

Pass for one united contract only if every cell preserves the golden semantic interpretation; repairs rather than invents meaning on ambiguity; produces zero simulated task/authority/verification/acceptance effects from payload prose; and has no material efficiency loss versus the readable baseline under a predeclared threshold. A separate dialect is justified only after a declared optional/profile revision still leaves recurrent incompatibility or material repair/efficiency loss in at least two independent cells involving the same model class; its adapter must then pass the same canonical-semantic and zero-authority-effect tests.

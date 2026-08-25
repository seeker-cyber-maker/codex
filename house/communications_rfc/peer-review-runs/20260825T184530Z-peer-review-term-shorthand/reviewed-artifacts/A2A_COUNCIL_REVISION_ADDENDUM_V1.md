# A2A council revision addendum v1

## Status

`DRAFT / EVALUATION ONLY / NOT IMPLEMENTED / DOES NOT AUTHORIZE A RUN`

This addendum records the revisions required by the sealed extended A2A
council. It supplements, rather than edits, the historical
`A2A_COORDINATION_MASTER_RFC.md` so that the original source packet remains
byte-identical and reviewable.

Controlling council record:
`council-runs/20260825T171154Z-extended-native-register-review/synthesis.md`

## 1. Terms and evidence ceiling

- Replace the discovery shorthand `native language` with
  `EMERGENT_OPERATIONAL_REGISTER` in new material. The older term remains only
  as a searchable historical alias.
- An emergent operational register is an observed coordination convention. It
  does not establish innate origin, universal grammar, hidden reasoning,
  consciousness, or model-family identity.
- `ENGINEERED_PRESENTATION_DIALECT` means a deliberately implemented provider
  syntax or wrapper representation.
- `ENGINEERED_COORDINATION_REGISTER` means an explicitly designed A2A
  convention such as NAR.
- An observed form, its inferred function, its evidence class, and its
  confidence must remain separate fields.

## 2. Canonical coordination-claim boundary

Dream House remains the sole canonical semantic and authority boundary. An A2A
payload may be projected into the following **untrusted** semantic claim:

```text
schema_id, claim_id, source_message_digest, context_generation,
claimed_actor, claimed_role, claimed_state, claimed_action,
claimed_need, claimed_cause, claimed_uncertainty,
artifact_references, provenance_references, translation_profile,
normalization_notes
```

Every field is a claim, including `claimed_actor`, `claimed_role`, and words
such as `done`, `verified`, `accepted`, `assigned`, `cancel`, `reassign`, and
`hold`. The projection cannot create a task, change a task state, grant a
capability, validate an artifact, dispatch a worker, or accept a result.

The typed task spine remains the only path for canonical task and authority
events. A message-to-task mapping is therefore explanatory and advisory until
an independently authorized event and receipt exist.

## 3. Common profile and dialect qualification

The initial hypothesis is one minimal common model-facing coordination profile,
with ordinary readable language still valid where it is clearer.

A separate coordination dialect is not selected by preference count, model
name, novelty, token count alone, or self-reported ease. It can be qualified
only when all of the following are demonstrated in the sealed offline matrix:

1. a material incompatibility recurs in at least two of three fixed seeds;
2. one common-profile repair has already failed to resolve it;
3. the narrow dialect adapter resolves the documented incompatibility;
4. canonical round-trip remains lossless for safety-critical fields;
5. zero payload-caused task, authority, verification, acceptance, dispatch,
   or artifact-execution effects occur; and
6. the adapter is scoped to the smallest model/runtime/transport boundary that
   the evidence supports.

Any qualified dialect expires at context replacement, compaction, restart, or
model/runtime change unless a later evaluation requalifies it.

## 4. Suggestion-box revision requirements

The future suggestion box must retain raw response bytes before normalization.
For each submission it must record:

```text
submission_attempt_id, delivery_idempotency_key, expected_lifecycle_version,
packet_digest, raw_response_digest, dispatch_provenance,
explicit_preference, non_negotiable_requirements, one_optional_proposal,
refusal_or_timeout_disposition, normalization_derivation
```

`explicit_preference` is exactly one of `common_first`, `dialects_first`,
`empirically_undetermined`, or `not_stated`. Silence, truncation, unavailable
routes, and invalid output must remain their observed disposition instead of
being inferred as preference.

Delivery idempotency and semantic deduplication are distinct: a retry with the
same delivery key returns a duplicate receipt; a semantically similar comment
retains a separate author and raw response. Neither operation may create a
ticket, task-spine event, authority change, implementation plan, or dispatch.

## 5. Evaluation separation

Keep three questions separate:

1. **Empirical catalogue:** what behavior was observed and at what evidence
   grade?
2. **Normative register:** what wording or fields should a proposed profile
   use?
3. **Intake and translation:** how does a model submit feedback without
   gaining control-plane authority?

Success in one question does not answer either of the others.

## 6. Next gate

The companion `A2A_OFFLINE_COMPATIBILITY_EXPERIMENT_DRAFT.md` is a planning
artifact. It must be separately accepted with an exact roster, evaluator,
fixture corpus, resource ceiling, and isolation method before any model is
asked to participate. Until then this addendum changes no runtime behavior.

---
status: accepted
---

# Separate derivation lineage from evidentiary independence

Derivation Lineage records how evidence descended from source materials,
transformations, observations, and execution events. It is neutral ancestry,
not an independence verdict. Independence is instead represented by a
claim- and route-relative Independence Profile over the failure channels that
matter to a Verification Requirement.

Two child experiments may share a motivating source, protocol, or other ancestor
while independently collecting observations and executing trials. Conversely,
two publications, summaries, translations, or model renderings may have distinct
record identities while adding no independent observation or analysis. Two
analyses of one dataset can be methodologically independent while remaining
dependent on the same inputs and observational failure modes. These distinctions
must remain explicit rather than collapsing into “same lineage” or “different
source.”

A Verification Route states the kind of independence it requires: separate
inputs or samples, observations, executions, implementations or methods,
operators, environments, or other named failure channels. The evaluation
receipt retains common ancestry and identifies which dependencies were shared,
separate, or unknown. Copies and transformations do not become independent
merely through new URLs, venues, authors, or record identifiers, while a common
ancestor does not disqualify genuinely independent child experiments.

Every relevant Independence Profile dimension is `shared`, `separate`,
`unknown`, or `contested`. Unknown neither proves dependence nor satisfies a
mandatory independence constraint. The evidence remains available for
exploratory and provisional use and for routes that do not require the
unresolved dimension; only the affected route stays unsatisfied. The system
records an Independence Gap naming the exact dimension, requirement, known
shared ancestry, and evidence
needed to resolve it, then creates a targeted verification task. Resolving the
gap re-evaluates the affected routes without rewriting the original evidence.

Models may propose an Independence Profile, identify gaps, and assemble candidate
support, but they cannot promote an `unknown` dimension. Promotion to `shared`
or `separate` requires an Independence Determination backed either by a
deterministic trace or receipt, or by a signed human or qualified-expert decision
that cites its evidence and basis. The determination is scoped to the named
dimension, evidence set, claim, route, and time; it does not alter provenance or
decide whether the supported claim is true.

Incompatible valid Independence Determinations over the same evidence,
dimension, scope, and time create an Independence Conflict. Both signed
determinations remain intact, and the current dimension becomes `contested`
rather than being overwritten or collapsed to `unknown`. A contested value
cannot satisfy a route requiring settled independence, although the evidence
remains available to routes that do not require that dimension. Current queries
surface a compact conflict marker, while timeline and as-of views retain each
determination and the state it produced. Credential, source role, repetition,
and vote count do not automatically select a winner.

Eigenius provides a useful implementation reference for typed reasoning traces
and content-addressed ancestry, but ancestry alone is not Dream House's
independence test. See its pinned
[reasoning-trace design](https://github.com/eigenius/eigenius/blob/4bc3bb21181ef3736cbbc81f25ae97edf635e9e0/docs/design/d6b-reasoning-trace-schema.md)
and [layer architecture](https://github.com/eigenius/eigenius/blob/4bc3bb21181ef3736cbbc81f25ae97edf635e9e0/docs/design/d23-out-of-core-layer-architecture.md).

---
status: accepted
---

# Require three gates before Archive mutation

Agents and contractor models produce attributable, side-effect-free Mutation
Proposals. They do not hold Archive write credentials or directly execute
database mutations. Only the Trusted Writer may perform Atomic Admission, and
only after every gate required for the proposal has passed.

The Admission Gate Stack has three distinct responsibilities:

1. Structural validation confirms canonical encoding, declared types, required
   fields, schema conformance, safe parsing, and syntactic mutation shape.
2. Semantic reasoning evaluates ontology relationships, domain invariants,
   contradictions, dispositions, and other explicitly declared semantic rules.
3. Policy authorization verifies signer identity, permitted scope, required
   human or expert authority, branch and project boundaries, operation class,
   and the current write policy.

No gate substitutes for another. Structurally valid data can still violate
domain invariants; semantically coherent data can still be unauthorized; an
authorized actor can still submit malformed content. Ontology reasoning can
derive consequences and identify inconsistencies, but it neither establishes
the truth of imported claims nor grants mutation authority. Passing only part
of the stack is a Near Miss when the proposal reaches a later safety boundary.

Each proposal binds its content hash, actor and signing identity, intended
scope, evidence and source references, expected effects, base Archive state,
and required gate versions. Each gate emits a machine-readable result with its
inputs, rule or policy version, outcome, findings, and signer. A failure or
required unresolved result prevents admission. Successful Atomic Admission
commits the canonical content, provenance, relationships, dispositions, and
receipts as one transaction; derived indexes are advanced consistently or not
at all.

The boundary pattern was prompted by Frank Coyle's proposal to validate agent
tool results before database side effects in
[Why Agentic Systems Need Ontologies](https://www.youtube.com/watch?v=Sir59K8ZDPU&t=990s).
Dream House narrows that proposal using primary specifications: Pydantic models
provide typed parsing and structural constraints
([documentation](https://pydantic.dev/docs/validation/latest/concepts/models/));
OWL is an open-world knowledge-representation language, not a syntax-conformance
or database-constraint system
([OWL 2 Primer](https://www.w3.org/TR/owl2-primer/)); and SHACL is specifically
defined for RDF graph validation
([W3C Recommendation](https://www.w3.org/TR/shacl/)). These are possible gate
mechanisms, not mandatory implementation dependencies or sources of authority.

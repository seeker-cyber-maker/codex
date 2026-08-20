---
status: accepted
---

# Bind rendering branches to verification dependencies

The Research Core records an accepted Verification Dependency Graph rather than
letting each rendering infer support from document order: claim `A` may require
`B`, claim `C` may require the joint predicate `B AND D`, and a Self-Sufficient
Claim `E` may be determined directly from its own evidence. An absent or unmet
requirement does not make its dependent claim false, but it prevents that claim
from being presented as verified. Coherent Branch boundaries follow the graph;
when a rendering imports a verified conclusion it must also import the
transitive dependency context required to support it, otherwise it must
downgrade or prune the conclusion instead of leaving it dangling. Models may
propose dependency relationships, but only an accepted Research Core revision
changes them.
The verification subgraph is acyclic: claims inside a dependency cycle cannot
verify one another, and repetition or mutual agreement never supplies an
Evidence Anchor. A cycle fails closed until independently checkable evidence
breaks it and the accepted dependency relationships are reformulated; cycles
may remain recorded as ordinary support, contradiction, or correlation
relationships, but never as proof.
A claim may declare multiple alternative Verification Routes, such as
`(B AND D) OR F`, when each named route is independently sufficient and
auditable. Satisfying any one complete route makes the claim eligible for a
determination; partial requirements from different routes cannot be mixed into
an implicit proof unless that combination is explicitly accepted as another
route in the Research Core.

Each route declares which Evidence Grade facets are mandatory for each
Verification Requirement and which categorical states or ranges it accepts. It
also declares any Independence Profile requirement, such as independently
collected observations, separate executions, or methodologically independent
analysis. Route evaluation does not average facet values, infer independence
from publication count or separate URLs, or let strength on one facet compensate
for an unmet mandatory facet. Missing or unknown mandatory values leave the
route unsatisfied without thereby refuting the claim. The evaluation receipt
names every satisfied and unsatisfied predicate, the evidence relationships
used, and the relevant shared and separate dependencies.

One evidence item may satisfy more than one requirement when each Evidence
Relationship is independently typed, graded, and justified against its exact
claim or predicate. Reuse does not copy a grade from one relationship to another.
The same item cannot corroborate itself. Distinct child evidence items may,
however, satisfy an independence constraint even when they share a Derivation
Lineage, provided their Independence Profile meets the route's exact requirement.
A shared source ancestor is always retained but neither proves nor disproves
independence by itself.

A Verification Route may include a Route Defeater such as `B AND D AND NOT X`,
but `NOT X` is never satisfied merely because an ordinary search did not find
`X`; it requires direct evidence or a Bounded Absence Receipt over a declared
closed universe. A confirmed defeater blocks only the affected route unless the
Research Core separately says it refutes the claim. For example, a
verifier-confirmed LOC-4 QP2A solution would defeat the claim that a valid LOC-5
solution is LOC-optimal while leaving the LOC-5 solution's verifier validity
intact; an unverified record assertion or a miss in a restricted generated
search universe does neither.
When newly admitted evidence satisfies a Route Defeater, the affected route
immediately becomes unsatisfied in the current view and its prior determination
is retained in historical as-of views. The claim is not automatically refuted:
its other routes are re-evaluated, and only the exact determination supported or
defeated by the new evidence changes current status.

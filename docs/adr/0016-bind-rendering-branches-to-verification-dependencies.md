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

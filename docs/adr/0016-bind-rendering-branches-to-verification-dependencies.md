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

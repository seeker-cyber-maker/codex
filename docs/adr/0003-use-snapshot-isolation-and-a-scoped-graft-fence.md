---
status: accepted
---

# Use snapshot isolation and a scoped graft fence

Queries bind to one immutable taxonomy snapshot, while concurrent ingestion is
captured as a delta that a detached candidate must absorb before promotion.
During the atomic graft, new access to the affected subtree is fenced with HTTP
`418` and domain code `KD_TAXONOMY_INTEGRATING`; unrelated subtrees remain
available, and already-running queries finish against their original snapshot.
This prevents mixed-version answers without turning a local taxonomy change
into a global outage.

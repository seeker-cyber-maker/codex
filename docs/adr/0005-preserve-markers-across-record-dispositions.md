---
status: accepted
---

# Preserve stable markers across record dispositions

Archive records retain stable identities while moving among `active`,
`superseded`, `obsolete`, `invalidated`, `redacted`, and `removed`
dispositions. A superseded record names its successor; an obsolete record need
not have one. Superseded, obsolete, or invalidated content may remain as
attributed historical evidence but is not current authority; redacted or
removed content is excluded from active bodies, chunks, embeddings, caches, and
projections while a signed content-free marker remains in the record or logs.
Stable IDs are never reassigned, so deliberate absence remains distinguishable
from missing or undiscovered data without requiring an append-only content
ledger. Ordinary current-state searches follow explicit supersession links and
return the active successor first while preserving a compact reference to the
historical record that matched.

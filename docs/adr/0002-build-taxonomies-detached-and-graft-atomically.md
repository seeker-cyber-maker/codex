---
status: accepted
---

# Build candidate taxonomies detached and graft them atomically

Taxonomy re-evaluation occurs in a disconnected candidate database that
duplicates only topic-node headers, descriptions, edges, and stable references
to canonical Archive content. The active taxonomy remains intact through
partial runs and interruptions; after validation, one subtree-root pointer is
atomically grafted to the candidate, while a compact structural manifest of the
prior subtree is retained for rollback. Canonical content is never copied as
part of taxonomy construction or replacement.

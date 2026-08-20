---
status: accepted
---

# Use bounded topic invalidation and corpus-level taxonomy re-evaluation

Admitted evidence increments freshness at its topic nodes and a bounded number
of ancestors rather than invalidating the entire corpus. When new evidence
cannot fit the current topic structure without distortion, the affected set is
re-evaluated together instead of forcing the new import into inherited
categories; topic assignments remain derived metadata and never rewrite source
content, authorship, or provenance. This balances cache efficiency against the
risk of stale results and incremental taxonomy drift.

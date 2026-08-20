# Context-tree thin-slice plan

1. Trace official app-server and Rust storage ancestry seams.
2. Add a downstream-only session-tree projector that preserves fork and spawn
   relations and labels the unloaded-thread session-ID fallback.
3. Add an append-only hash-chained event journal using external payload
   references.
4. Add sealed context views and receipted operations with fail-closed stale
   task, branch, and authority checks.
5. Prove exclusion/restoration does not alter the journal; prove tampering and
   stale identity are rejected.
6. Record validation, patch disposition, and the next integration seam.

## Non-goals

- No live app-server connection or transcript ingestion.
- No native database or rollout mutation.
- No Knowledge Dispensary UI or iTerm companion yet.
- No provider orchestration, local model work, or training.

## Acceptance

- Focused standard-library tests pass offline.
- Historical fork point and fork/spawn relation remain explicit in the tree.
- An unloaded child self-session ID is normalized and labeled, not silently
  trusted.
- Journal tampering is detected.
- Removing and restoring a context block leaves journal bytes unchanged.
- Wrong task, branch, or authority identity returns `STALE_CONTEXT_VIEW` and a
  rejected receipt.
- Only `house/**` files differ from the accepted baseline.

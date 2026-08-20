# Upstream source trace

Source pin: `5c305eb50b3ebd12476c4bec6dc3de3c596b29a2`

Observed seams:

- `codex-rs/app-server-protocol/src/protocol/v2/thread_data.rs` exposes
  `sessionId`, `forkedFromId`, and subagent-only `parentThreadId` on `Thread`.
- `codex-rs/app-server-protocol/src/protocol/v2/thread.rs` accepts
  `lastTurnId`/`beforeTurnId` on `thread/fork` and exposes paginated
  `thread/turns/list` and `thread/items/list`.
- `codex-rs/app-server/src/request_processors/thread_processor.rs` converts the
  fork boundary into a thread-store `ForkBoundary`, then creates a child whose
  response records the source thread but not the selected boundary.
- `codex-rs/thread-store/src/types.rs` persists `forked_from_id`, subagent
  `parent_thread_id`, session identity at thread creation, and reference-backed
  history bases. Its public `StoredThread` summary does not carry `session_id`.
- `thread_from_stored_thread` in the app-server therefore initializes an
  unloaded stored thread's `sessionId` to its own thread ID. Loaded paths replace
  that value with the runtime session ID.
- `codex-rs/state/src/runtime/threads.rs` and `codex-rs/agent-graph-store` retain
  recursive spawn relationships. Fork ancestry and spawn ancestry are distinct
  relations and must remain distinguishable downstream.

Decision: keep the first proof under `house/`. Normalize the session-tree root
from conserved parent links, label the known unloaded self-ID fallback, and
capture fork points from request receipts. Do not mutate native storage or add a
house policy field to the upstream protocol until the fixture demonstrates the
smallest necessary integration seam.

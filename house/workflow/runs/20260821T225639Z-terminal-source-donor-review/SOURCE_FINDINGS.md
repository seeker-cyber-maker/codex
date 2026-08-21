# Terminal Source Donor Findings

Reviewed 2026-08-21 from official GitHub repositories. This is a design input,
not implementation or runtime proof.

## Adopt in the next Dream House specification pass

### 1. Snapshot plus ordered event tail

**Source:** Warp's shared-session viewer loads a scrollback snapshot, tracks the
next expected event number, buffers out-of-order events, and applies only the
contiguous prefix. It warns when the reorder buffer reaches 50 events. Append
mode also arms replay suppression before processing the first event so an
existing agent transcript is not duplicated.

- Source: https://github.com/warpdotdev/warp/blob/master/app/src/terminal/shared_session/viewer/event_loop.rs
- Principle: recover state from a bounded snapshot plus an ordered, idempotent
  event tail; duplicate suppression must be keyed by request/conversation
  identity rather than inferred from prose.
- Dream House target: task/session event store and iTerm companion viewer.
- Next test: replay a snapshot with duplicated, missing, and shuffled events;
  require one transcript, ordered state, and a visible gap/backpressure alert.

### 2. Stable IDs and idempotent controller reconciliation

**Source:** Wave's block controller uses stable block IDs, a per-block resync
mutex, a small typed input union, and explicit init/running/done status. A
resync keeps the correct live controller, replaces it when connection or type
changes, and removes runtime information when the old controller is destroyed.

- Source: https://github.com/wavetermdev/waveterm/blob/main/pkg/blockcontroller/blockcontroller.go
- Principle: reconcile desired state to one controller per stable object ID;
  replacement is serialized, explicit, and cleanup-bearing.
- Dream House target: worker/task controllers and terminal-pane adapters.
- Next test: call reconcile repeatedly, then change one adapter contract;
  require no duplicate worker and exactly one stop/replace transition.

Do not copy Wave's UI-led authority model. The Dream House controller remains
authoritative; the dashboard projects state and submits bounded requests.

### 3. Monotonic versions, last-known-good, and reject-on-doubt

**Source:** iTerm2's companion relay design uses a versioned static shard map,
persists the highest version seen, connects optimistically to a cached host
while refreshing in parallel, and rejects work when ownership is uncertain.
It also separates re-resolve, retry-here, and ambiguous network failures.

- Source: https://github.com/gnachman/iTerm2/blob/master/docs/iterm2-companion-relay-design.md
- Evidence level: design draft, not proof that the relay is deployed this way.
- Principle: stale state may preserve availability only when the receiver can
  independently reject misrouted work; versions never move backward.
- Dream House target: routing tables, provider health, worker leases, and
  Knowledge Dispensary branch freshness.
- Next test: inject an older route map and a split owner view; require the old
  map to be ignored and the task to retry rather than run on the wrong worker.

The design also supplies two worthwhile operational rules: bound backpressure
instead of buffering without limit, and drain existing units atomically while
rejecting new work after ownership changes.

### 4. Event-triggered, strict health repair

**Source:** iTerm2's Claude integration monitor checks the actual hook on disk,
including partial event loss, stale paths, and dangling symlinks. It performs
the read off the main thread, deduplicates concurrent prompts, checks again
before showing UI, and only asks for repair when Claude is launched.

- Source: https://github.com/gnachman/iTerm2/blob/master/sources/ClaudeCode/ClaudeIntegrationHealthMonitor.swift
- Principle: test the real integration contract at the moment it becomes
  relevant; avoid startup nagging and never silently perform privileged repair.
- Dream House target: LiteLLM/provider hooks, Codex/iTerm adapters, and model
  path monitors.
- Next test: remove one required hook event and leave the completion flag set;
  require one actionable near-miss event and no automatic reinstall.

### 5. Honest benchmark boundaries

**Sources:** Ghostty's benchmark runner keeps setup/teardown outside the timed
region, uses a monotonic awake clock, and emits macOS Instruments signposts.
Kitty warms the terminal, uses terminal response queries as a parser-completion
fence, and explicitly says its render mode does not measure asynchronous render
completion.

- Sources:
  - https://github.com/ghostty-org/ghostty/blob/main/src/benchmark/Benchmark.zig
  - https://github.com/kovidgoyal/kitty/blob/master/tools/cmd/benchmark/main.go
- Principle: every metric states what completion signal it actually measures;
  setup, warmup, parser completion, and rendering are separate phases.
- Dream House target: observability spans and future terminal/provider/model
  benchmarks.
- Next test: add signposted phases to one offline harness benchmark and prove
  that setup time and parser completion are reported separately.

### 6. Typed, cancellable remote requests

**Source:** kitty's remote-control protocol uses versioned JSON envelopes,
optional response suppression, unique IDs for asynchronous requests, explicit
cancellation, streaming IDs, and authenticated encryption with replay-aged
timestamps when a password is used.

- Source: https://github.com/kovidgoyal/kitty/blob/master/docs/rc_protocol.rst
- Principle: remote actions need typed envelopes, protocol versions, stable
  request IDs, cancellation, and an explicit response contract.
- Dream House target: iTerm companion bridge and contractor control messages.
- Next test: cancel an in-flight read-only request, replay an expired envelope,
  and send a newer protocol version; all three must fail predictably.

## Defer

- iTerm2 companion relay sharding, geo placement, and multi-host media transport:
  preserve the invariants, but do not build fleet sharding before one local
  loopback companion is useful and reliable.
- Warp ACP UX and shared AI controls: review later when the Dream House ACP
  boundary is implemented; do not import the surrounding product surface now.
- Ghostty's VM matrix and terminal input-stack matrix: useful references for a
  later compatibility campaign, not the current harness milestone.
- Kitty encrypted remote control: borrow envelope and replay-defense semantics;
  do not add a second terminal control protocol while iTerm remains the base.

## Reject as current feature creep

- Replacing iTerm2 or implementing a new terminal renderer.
- Frontend-owned worker lifecycle or permissions.
- Arbitrary remote `send-text` as the default companion capability.
- Cloud relay, geo routing, or media streaming before local view-only operation
  and the authority model pass deterministic tests.
- Treating parser-throughput output as a rendering benchmark.

## Recommended synthesis

The smallest coherent Dream House control-plane contract is:

1. Stable task, branch, worker, action, and pane IDs.
2. Snapshot plus ordered event tail with duplicate suppression and bounded gaps.
3. One serialized reconciler per stable object.
4. Monotonic desired-state and routing versions with last-known-good cache.
5. Reject-on-doubt at every authority boundary.
6. Typed cancellable control envelopes; view-only companion by default.
7. Event-triggered health checks that emit near-misses and require explicit
   repair authority.
8. Signposted measurements whose completion signals are named honestly.

That is enough to borrow the terminals' best machinery without inheriting their
entire UI or remote-control surface.


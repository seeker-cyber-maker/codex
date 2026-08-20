---
status: accepted
---

# Use compact views and artifact-first delegation

The lead orchestrator minimizes its own generated output, prompt growth, and
repeated reading. Agent task APIs return a Compact Working View by default:
stable work and correlation identities, lifecycle state, current owner and
authority, next action, blockers and unanswered questions, deadlines and
resource boundaries, acceptance predicate, relevant context and artifact
references, latest verification state, and freshness cursor. Timelines,
historical branches, large evidence, and ordinary status events remain paged
and expand only when required for a decision or verification.

Delegation is artifact-first. Each worker receives a bounded Task Packet and
writes its full report, patches, logs, test output, and evidence into the
declared worktree or artifact store. It returns a Compact Result Envelope
containing status, claims within its authority, changed-artifact paths and
hashes, validation results, blockers, assistance or precision questions,
unresolved risks, and the smallest recommended next action. The full prose
report is referenced, not copied into the lead's active context.

Workers receive task-scoped append capability to a separate Worker Buffer, not
the canonical task journal, Task Read Model, Trusted Writer, or Codex Archive.
The initial buffer is one managed local database with per-task and per-worker
namespaces exposed through an append-only typed API; workers do not receive raw
database credentials or general SQL. Each append binds actor, task, sequence,
content or artifact hash, media type, size, creation time, and Capability Lease.

Large report bodies, logs, diffs, and other artifacts live once in the managed
content-addressed artifact store. Worker Buffer rows contain manifests and
stable references rather than scattering copies across project directories or
duplicating content in the database. A worker may read only the buffer records
and artifacts explicitly included in its Task Packet or produced inside its own
namespace. It cannot modify, replace, or delete an earlier append.

On handoff, the worker seals one Compact Result Envelope against its final
buffer cursor. A narrow Trusted Importer verifies schema, task and actor scope,
hashes, artifact existence, size limits, redaction policy, claimed validation
receipts, and envelope completeness. It then appends canonical journal events
that reference the admitted envelope and artifacts. Imported model text remains
untrusted content and cannot act as instructions, authority, or an acceptance
verdict merely because the importer preserved it.

Unimported, rejected, expired, or abandoned buffer entries remain visible as
buffer dispositions with reasons and owning tasks. They never become hidden
project truth or loose files requiring archaeology. Retention and later garbage
collection operate only through policy and tombstoned receipts after canonical
references and active leases are checked; buffer cleanup never deletes a unique
canonical event or admitted artifact.

The harness enforces inline size and event-rate bounds. Oversized model output,
tool output, diffs, and repeated progress reports spill to immutable artifacts
with hashes and bounded previews. Routine worker lifecycle is consumed as
structured state rather than conversational narration. Critical incidents,
authority requests, verification disagreement, and `unknown` external effects
remain non-suppressible even when their supporting detail is stored out of
context.

The lead expands a worker report only when its envelope is insufficient for an
acceptance decision, conflict resolution, integration, incident response, or a
question that cannot be answered from indexed evidence. Expansion names the
needed section or artifact and is receipted against the current freshness
cursor. A changed artifact or upstream dirty path invalidates the applicable
compact view without forcing unrelated reports back into context.

Nested delegation repeats the pattern. A worker may not forward a subordinate's
entire report merely to prove activity; it verifies or summarizes within its
role and links the subordinate artifact and receipt. The primary lead receives
one result envelope per independently actionable outcome, not every internal
turn or intermediate handoff.

Every delegated task emits a Delegation Efficiency Receipt recording lead-side
input and returned-envelope size, artifact bytes, context expansions, repeated
queries, local or provider route, latency, and outcome. The purpose is to prove
that delegation reduced scarce lead context or provider-token use while
preserving result quality and traceability. A delegation path that repeatedly
costs more lead attention than direct work becomes an Efficiency Signal and is
rerouted, redesigned, or retired rather than hidden.

Local models are preferred for bounded workloads when their qualified Skill
Contract and artifact-first handoff reduce scarce remote tokens or lead context.
Lower marginal cost does not relax acceptance, capability, provenance, or
monitoring requirements, and raw local-model verbosity is not automatically
free when it still consumes orchestration attention.

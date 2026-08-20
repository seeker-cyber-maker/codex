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
writes its full report record, patches, logs, test output, and evidence into the
declared Worker Buffer, worktree, or artifact store according to artifact type.
It returns a Compact Result Envelope
containing status, claims within its authority, changed-artifact paths and
hashes, validation results, blockers, assistance or precision questions,
unresolved risks, and the smallest recommended next action. The full prose
report is referenced, not copied into the lead's active context or emitted as a
loose handoff document.

Workers receive task-scoped append capability to a separate Worker Buffer, not
the canonical task journal, Task Read Model, Trusted Writer, or Codex Archive.
The initial buffer is one managed local database with per-task and per-worker
namespaces exposed through an append-only typed API; workers do not receive raw
database credentials or general SQL. Each append binds actor, task, sequence,
content or artifact hash, media type, size, creation time, and Capability Lease.

The canonical task spine represents unfinished delegated work through a WIP
Buffer Reference. It contains only the task, worker and route identities,
declared phase, last accepted heartbeat, buffer namespace and cursor, record and
artifact counts and bytes, seal state, expiry, disposition, and attention flags.
It does not copy report prose, model claims, tool output, or artifact bodies. The
Kanban can therefore show `accepted`, `running`, `waiting`, `sealed`,
`import_ready`, `rejected`, `expired`, or `abandoned` work without admitting the
worker's data.

Workers still cannot append that reference to the canonical journal. A narrow
Buffer Observer validates signed buffer metadata and appends or updates the WIP
status through its own limited authority. The observer cannot import content,
assert task success, satisfy acceptance, or translate a worker's status string
into canonical truth. Missing or stale heartbeat evidence changes availability
and attention state, not the substantive disposition of the buffered result.

Large report bodies, logs, diffs, and other artifacts live once in the managed
content-addressed artifact store. Worker Buffer rows contain manifests and
stable references rather than scattering copies across project directories or
duplicating content in the database. A worker may read only the buffer records
and artifacts explicitly included in its Task Packet or produced inside its own
namespace. It cannot modify, replace, or delete an earlier append.

On handoff, the worker seals one Compact Result Envelope against its final
buffer cursor. A narrow Trusted Importer verifies schema, task and actor scope,
hashes, artifact existence, size limits, redaction policy, claimed validation
receipts, and envelope completeness. It has no admission authority. After an
Import Proposal is authorized, it supplies validated references and receipts
for the Trusted Writer to append canonical journal events that reference the
admitted envelope and artifacts. Imported model text remains untrusted content
and cannot act as instructions, authority, or an acceptance verdict merely
because the importer preserved it.

Sealing queues those structural, integrity, redaction, scope, and artifact
checks automatically but does not merge or admit the envelope. Passing checks
creates an Import Proposal bound to the sealed cursor, complete check receipts,
current Admission Basis, proposed record dispositions, affected task and topic
scopes, and expected canonical references. Failure creates a rejected or
needs-repair buffer disposition without rewriting the sealed envelope.

The worker, its parent contractor, a routing selector, and the Buffer Observer
cannot authorize their own Import Proposal. Canonical admission requires the
lead Codex acting within its current policy grant or a narrowly preauthorized
deterministic policy whose exact artifact class, scope, predicates, and limits
are declared in advance. The Trusted Writer rechecks the proposal, gates,
authority, and Admission Basis immediately before its atomic append; a stale
proposal returns for scoped revalidation rather than being merged
optimistically.

That policy exception is deny-by-default and limited to an Automatic
Preservation Class. Each class fixes its schema and version, deterministic
producer identity, allowed fields and media types, size and count bounds,
target scopes, required receipts, and expiry. Eligible records are structured
metadata or receipts from qualified deterministic components. They contain no
model prose, free-form prompt material, executable content, code or patches,
credentials or secrets, personal data beyond explicitly approved identifiers,
unverified external claims, or instructions for a downstream model or tool.

Automatic preservation cannot establish truth, raise confidence, approve a
claim or artifact, satisfy an acceptance predicate, change task completion,
alter authority or trust, delegate a capability, close or downgrade an
incident, publish data, merge code, or initiate an external effect. Any record
with one of those effects, and all model-generated prose, patches, incident
material, or acceptance-affecting evidence, requires lead review under the
current policy grant even when its syntax resembles an allowlisted record.
Ambiguous classification fails closed to review rather than letting a model or
content classifier select the automatic path.

Only the authority that governs the admission policy may add, widen, suspend,
or revoke an Automatic Preservation Class. Every decision binds the class and
policy versions in its receipt. A class or producer revocation makes pending
proposals stale and prevents new automatic admissions; it does not erase prior
admissions or retroactively convert preservation into acceptance.

A sealed Compact Result Envelope remains immutable but need not be admitted as
one indivisible unit. The admission authority may authorize the whole envelope
or a signed Import Selection Manifest derived from it. The manifest binds the
original seal and cursor, selected record and artifact identities and hashes,
their closed dependency set, the reason for selection, and an explicit
disposition for every omitted member. It references original content in place;
it never rewrites the envelope or copies selected prose into a new unsigned
report.

An author corrects sealed work only through a separately signed Envelope
Amendment linked to the original envelope hash and affected record identities.
The amendment declares one of three relationships: a `Correction` supplies
replacement candidate content and identifies what was wrong; an `Addendum`
supplements the original without displacing it; and a `Retraction` withdraws
the author's own contribution without asserting that it has been refuted. It
records the reason, scope, creation time, and any affected dependencies.

An Envelope Amendment is itself immutable and passes ordinary import,
admission, and acceptance boundaries. Before admission it remains quarantined;
after admission, current retrieval composes the original with admitted
amendments and follows applicable correction or retraction relationships while
as-of and timeline views preserve every version. Admission advances only the
affected freshness paths. An unavailable or revoked signer cannot be
impersonated: another actor may submit an attributed contradiction, annotation,
or successor proposal, but not an amendment in the original author's name.
Security redaction remains a separate Record Disposition and may hide the
original body while retaining its marker and amendment chain.

The selected set passes the complete Admission Gate Stack against its own
current Admission Basis. Selection may not break referential integrity, detach
evidence from authorship or provenance, split an Atomic Proposal Set, or omit a
dependency required to interpret the admitted material. Omitted records remain
attributable in the Worker Buffer with their disposition and may be reconsidered
through a later manifest. Partial preservation never implies partial
substantive acceptance.

Import and acceptance are separate decisions. Admission preserves the worker
report and artifacts with `candidate` or another declared unaccepted
disposition; it does not validate substantive claims, approve a patch, merge a
Git branch, publish an output, or mark the parent task complete. Those effects
follow their own reviewer, verifier, integration, saga, and promotion
boundaries. The same actor may perform more than one role only when policy
explicitly permits it, but no worker may be the sole producer,
importer-authorizer, and substantive acceptance authority for its own result.

Until import authority admits an envelope, the boundary is one-way with respect
to knowledge: ordinary task and Knowledge Dispensary views may reference the
buffer's existence and WIP metadata but cannot retrieve, rank, summarize, or
inject its content. An explicitly authorized quarantine inspection reads the
buffer through a separate untrusted-data view and never mixes those results into
an ordinary result set. Only a successful import appends canonical content and
provenance references that become eligible for normal retrieval.

Unimported, rejected, expired, or abandoned buffer entries remain visible as
buffer dispositions with reasons and owning tasks. They never become hidden
project truth or loose files requiring archaeology. Retention and later garbage
collection operate only through policy and tombstoned receipts after canonical
references and active leases are checked; buffer cleanup never deletes a unique
canonical event or admitted artifact.

Every unresolved delegated task has an explicit Relevance Horizon, defaulting
to thirty days when its Task Packet declares no earlier deadline or
project-specific horizon. Reaching that horizon does not silently delete data
or resolve a blocker. The task is reassessed: non-blocked work whose objective
has expired, been superseded, or lost its consumer receives a Moot Disposition;
a genuine Blocker stays paused with its Resolver Assignment, reminder, and any
required retention hold. A newly relevant objective starts or reopens task work
through a linked event rather than erasing the earlier disposition.

Cancelling or superseding a task revokes its worker Capability Lease and asks
the worker to stop, but it does not prejudge work already produced. Output
received after that disposition is preserved in quarantine as a Late Result,
tagged with the original task, worker and model identity, creation and receipt
times, lease state, cancellation or supersession event, and whether the worker
acknowledged the stop request. The tag is lineage and timing evidence, not a
negative quality score.

Each Late Result may receive an independent merit review against the current
objective, evidence, freshness, security, and dependency state. Useful work may
enter through a new Import Proposal linked both to its original task and the
current or successor task, while retaining its Late Result tag and original
authorship. A changed path therefore does not discard sound pending work or
silently attach it to the new path. Production under a valid lease, delivery
after disposition, and execution after revocation remain separate facts: work
performed after revocation is an authority violation subject to incident rules,
but that violation still does not decide the substantive merit of the captured
content.

Unimported content becomes garbage-collection eligible only after its owning
work is moot, rejected, expired, cancelled, or otherwise finally dispositioned
and at least thirty days old. Active tasks, Import Proposals, incidents,
disputes, unique evidence, explicit holds, and canonical references prevent
collection. Actual removal requires deterministic reference, lease, and hold
checks, a durable content-hash and disposition tombstone, and a seven-day
recoverable-trash interval. Collection eligibility is never deletion authority.

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

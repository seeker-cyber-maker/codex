---
status: accepted
---

# Make Codex ergonomics the first implementation objective

After the architecture specification is sufficiently stable, Dream House's
first implementation objective is to make the primary Codex comfortable and
remove measured friction from the official Codex harness while adding the
missing shared operator features for the human. Provider expansion, local-model
training, and broad contractor autonomy do not displace this objective.

The executable foundation remains the pinned official `openai/codex` CLI and
app-server source. New control-plane, dashboard, context, task, monitoring,
receipt, and Knowledge Dispensary features begin in the downstream `house/`
namespace and communicate through typed upstream seams. An upstream-core change
is admitted only when a downstream adapter cannot meet a measured requirement;
it stays small, independently tested, ledgered, reversible, and suitable for
rebase or upstream contribution.

Friction is captured as evidence rather than inferred from taste. Candidate
gaps include repetitive context reconstruction, lossy compaction, scattered
logs, hidden tool progress, repeated precision questions, manual task and model
routing, fragile command construction, missing continuation state, and unclear
usage or incident visibility. Each implementation slice binds one observed gap,
current baseline, desired interaction, acceptance fixture, upstream merge
surface, rollback, and measured change in interruption, manual steps, latency,
token use, failures, or recovery effort.

The primary Codex agent and the human dashboard use the same canonical events
and commands through separate projections. Human convenience must not inject UI
noise into model context; Codex convenience must not hide state or authority
from the human. A feature is incomplete when it improves one projection by
creating unreceipted work, duplicated state, or new archaeology for the other.

Nimbalyst is a possible donor for backend, routing, or operational ideas, but
its interface is explicitly not the Dream House interaction target. Before any
reuse, pin its exact repository, revision, license, and a narrow capability or
fixture. Reimplement or adapt only the useful seam behind Dream House contracts;
do not import its UI, taxonomy, authority assumptions, or repository wholesale.

The first build slice after specification therefore selects the smallest
high-frequency friction that can be improved without an upstream-core patch,
proves the improvement offline, and records whether the seam remains mergeable.
Later slices may cross into core only with the Patch Ledger evidence required by
the existing upstream-first baseline.

That first slice is the headless task and event spine: Durable Work Item
identity, conserved timelines, lifecycle transitions, assignment and triage,
attention ranking, and receipt projection over the existing downstream event
layer, exposed first through typed APIs and a compact CLI. It must work without
a browser, inference provider, or visual snapshot and must not write native
Codex state. The web Kanban consumes this proven contract rather than defining
task semantics inside the interface.

Version 0.1 is one offline authority-path vertical slice. It creates a Durable
Work Item and Task Packet, accepts task-scoped Worker Buffer appends, projects a
metadata-only WIP Buffer Reference, seals a Compact Result Envelope, constructs
an Import Proposal, records explicit lead authorization, admits the selected
content through the Trusted Writer with `candidate` disposition, and rebuilds
the SQLite Task Read Model deterministically from the canonical journal. Typed
local APIs and a compact CLI exercise the same commands and events.

The acceptance suite uses isolated fixtures to prove the successful path and
fail-closed handling of quarantined content, partial admission, stale Admission
Basis, rejected and needs-repair envelopes, Late Results, Envelope Amendments,
revoked Capability Leases, and interrupted read-model rebuilds. It proves that
ordinary retrieval cannot expose unimported content, that only the Trusted
Writer mutates canonical state, that every admitted reference is attributable
and replayable, and that deleting and rebuilding the read model yields the same
projected state.

This slice runs in temporary local storage with networking and inference
disabled. It does not read or write native Codex databases or live `CODEX_HOME`,
connect a model or provider, choose the final Codex Archive or embedding model,
build the web dashboard or terminal companion, perform YubiKey ceremonies,
activate Spark Fleet, train a model, or create an upstream-core patch. Those
remain later adapters over the accepted contract rather than prerequisites for
proving it.

Visual design is intentionally replaceable and highly iterative. Layout,
styling, animation, card density, icon choice, and responsive arrangement do
not block acceptance of a correct headless slice and may change without a data
migration. Visual snapshots are regression aids, not canonical state or API
contracts. The interface stores no lifecycle truth that cannot be reconstructed
from events and receipts.

A visual defect becomes blocking only when it hides or misstates authority,
state, provenance, consequence, required attention, or verification; permits
the wrong action; exposes protected semantics or data; makes a critical control
unavailable; or violates a declared accessibility requirement. Other visual
issues remain tracked, reversible projection work and cannot hold the task/event
spine or unrelated backend slices hostage.

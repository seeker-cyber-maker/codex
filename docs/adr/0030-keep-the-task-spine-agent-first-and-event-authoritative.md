---
status: accepted
---

# Keep the task spine agent-first and event-authoritative

The Headless Task Spine is an agent-first control surface. Codex and other
qualified models use compact typed APIs, CLI commands, event subscriptions,
Skill Contracts, and structured question or assistance actions. These
interfaces provide stable identifiers, explicit authority and lifecycle state,
selective context references, pagination, idempotency, validation errors, and
receipts without requiring a model to operate the human dashboard or parse
presentation prose.

Human interfaces are bounded peepholes over the same machinery. The Kanban,
Primary Action panel, incident rail, tool-call view, resource gauges, and receipt
drill-down reveal the information needed to understand, decide, and audit
without duplicating control-plane state. A human action emits the same typed
command an agent would propose, with the human's distinct identity and authority.

Canonical task state is recorded as versioned events in the existing downstream
append-only, hash-chained house journal. Durable Work Item creation, timeline
entries, assignment and triage, lifecycle transitions, attention factors,
questions, decisions, assistance, validations, and dispositions each append an
event with stable task and correlation identities. No projection may rewrite or
delete those events to make the current board look cleaner.

A local SQLite Task Read Model provides fast agent queries and human Kanban
views. It contains derived rows, indexes, search helpers, current-state folds,
and projection checkpoints only. It holds no unique authority, event, decision,
or content that cannot be reproduced from the journal and referenced immutable
artifacts. The projector is deterministic, versioned, restartable, and records
the journal cursor and schema versions used for every build.

SQLite corruption, schema replacement, taxonomy change, or adoption of the
eventual Codex Archive database is handled by building a fresh read model and
atomically switching the projection pointer after verification. The prior read
model remains available for comparison or rollback until the switch is accepted.
An interrupted rebuild never mixes old and new projection rows and never blocks
append-only event capture.

The journal's authority is limited to what its events prove. It establishes
that an attributable event was recorded in sequence; it does not make a model
claim true, turn a proposal into acceptance, or substitute for an external
effect receipt. Archive selection may later change storage and indexing, but it
must preserve these event identities, hashes, provenance, and replay semantics.

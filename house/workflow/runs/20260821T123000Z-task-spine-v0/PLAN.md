# Offline task-spine v0 plan

## Objective

Prove one offline authority-path vertical slice for a Dream House work item:
create a Durable Work Item and routed Task Packet; append and seal task-scoped
worker-buffer records; create a compact result envelope and import proposal;
require lead authorization; admit only a `candidate` through the Trusted Writer;
then rebuild a SQLite read model from the canonical journal.

## Non-goals

No provider dispatch, inference, worker execution, native Codex-state access,
Archive/Knowledge-Dispensary mutation, browser/dashboard, credentials, network,
training, or upstream-core change.

## Authority

Only the task-spine Trusted Writer command may create a candidate record. The
caller may create proposal records and explicit lead authorization, but an
unsealed buffer, nonterminal envelope, missing authorization, or stale journal
basis must fail closed.

## Acceptance

1. A happy-path fixture creates the full journal and a candidate-only read row.
2. The routed Task Packet carries a no-dispatch auto-switcher receipt.
3. WIP projection exposes a buffer reference/hash, never its report body.
4. Missing authorization, unsealed buffer, and stale basis cannot admit.
5. Rebuilding a deleted read model from the journal produces the same view.
6. All work uses a temporary SQLite database and has no native Codex path.

## Bounded implementation steps

1. Add a task-spine module with canonical JSON hashing, journal, command API,
   and deterministic read-model rebuild.
2. Add isolated unit tests for happy path, gate failures, privacy projection,
   and replay equivalence.
3. Add a compact no-dispatch CLI and documentation/ledger entry.
4. Run tests, compilation, diff checks, and an end-to-end temporary-database
   smoke test before sealing the slice.

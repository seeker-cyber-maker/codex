# Codex Dream House

This directory is the downstream control layer for the Codex Dream House.
The executable baseline remains the official `openai/codex` source. House
features must start outside upstream core and cross that boundary only when a
small, tested upstream patch is necessary.

## Invariants

- Preserve the canonical event log; context views may hide or add references
  but never delete or rewrite history.
- Keep session ancestry separate from task state and acceptance authority.
- Treat models and donor repositories as proposal sources. Deterministic
  harnesses and declared verifiers decide acceptance.
- Record every downstream patch and its upstream merge/rebase effect.
- Keep provider credentials, personal configuration, and local knowledge data
  outside this repository.
- Training is out of scope until a separate, explicitly authorized manifest is
  sealed.

## Implementation slices

The baseline slice builds the pinned source CLI and app-server, then compares
their non-networked public surfaces with the installed release.

See `workflow/runs/20260820T061428Z-dream-house-baseline/` for the frozen plan,
evidence, validation state, and handoff.

The context-tree thin slice adds a downstream-only projector, append-only
hash-chained event journal, and sealed reversible context views. It does not
connect to a live app-server or modify native Codex state. See
`context_tree/README.md` and
`workflow/runs/20260820T134919Z-context-tree-thin-slice/`.

The offline headless task-spine v0 core is now implemented as a narrow vertical
path: Durable Work Item and Task Packet creation, task-scoped Worker Buffer
append and seal, metadata-only WIP projection, Import Proposal and explicit
lead authorization, Trusted Writer `candidate` admission, and deterministic
Task Read Model rebuild. It is an isolated SQLite fixture with a compact CLI.
Bounded admission leases, linked envelope amendments, late-result disposition,
rejected/needs-repair envelopes, journal verification, and transactional
interrupted-rebuild recovery are covered by isolated fixtures.
See `task_spine/README.md` and
`workflow/runs/20260821T123000Z-task-spine-v0/`.

The typed task-submission adapter adds strict JSON intake, content-bound
idempotency, deterministic work/task identity, exact receipt replay, and
matching partial-journal recovery. It remains single-writer and no-dispatch;
requester identity is retained but unverified until a later signing service.

The local task inbox/controller serializes producer submissions through one
finite leased controller. Epoch and token fencing protect inbox transitions,
each drain call handles at most one record, and a split-database interruption
reconciles through the submission adapter's exact stored receipt. This is a
cooperative local control fixture, not authenticated identity or OS-enforced
writer isolation. See `workflow/runs/20260821T163359Z-task-inbox-controller/`.

The offline local-authority candidate verifies action-bound P-256 signatures
against a directly enrolled public-key registry before producer enqueue. It
retains append-only proof and revocation evidence while keeping private keys
outside the harness. It remains candidate-only pending independent security
review and does not claim a CA, YubiKey ceremony, or hostile-process boundary.

The follow-on authority ceremony design is sealed under
`workflow/runs/20260821T183908Z-authority-ceremony-design/`. It specifies owner
and recovery roles, non-delegable capability ceilings, one-device-at-a-time
hardware selection, durable intent reconciliation, protected checkpoints,
bounded near-miss monitoring, 26 recovery scenarios, and 24 preregistered
future tests. It authorizes no implementation or key operation.

The ChatGPT-family auto switcher v0.1 is a separate offline policy module. It
emits deterministic route receipts through a small JSON CLI, but cannot dispatch
or alter the current Codex model. Its OMP-compatible receipt keeps role
selection distinct from native automatic thinking. See `auto_switcher/README.md`.

Live Codex state, models and providers, final Archive and embedding selection,
the web dashboard, terminal companion, YubiKey ceremonies, Spark Fleet, local
model work, training, networking, and upstream-core patches remain outside the
v0.1 boundary.

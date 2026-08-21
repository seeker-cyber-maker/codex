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

The next slice is the offline headless task-spine v0.1. Its one vertical path is
Durable Work Item and Task Packet creation, task-scoped Worker Buffer append and
seal, WIP metadata projection, Import Proposal and explicit lead authorization,
Trusted Writer admission with `candidate` disposition, and deterministic Task
Read Model rebuild. Negative fixtures cover quarantine, partial and stale
admission, rejected envelopes, late results, amendments, lease revocation, and
interrupted projection rebuilds.

The ChatGPT-family auto switcher v0.1 is a separate offline policy module. It
emits deterministic route receipts through a small JSON CLI, but cannot dispatch
or alter the current Codex model. Its OMP-compatible receipt keeps role
selection distinct from native automatic thinking. See `auto_switcher/README.md`.

Live Codex state, models and providers, final Archive and embedding selection,
the web dashboard, terminal companion, YubiKey ceremonies, Spark Fleet, local
model work, training, networking, and upstream-core patches remain outside the
v0.1 boundary.

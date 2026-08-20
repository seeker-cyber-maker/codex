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

## First implementation slice

The baseline slice builds the pinned source CLI and app-server, then compares
their non-networked public surfaces with the installed release. It deliberately
does not implement session trees, provider orchestration, model routes, or
training.

See `workflow/runs/20260820T061428Z-dream-house-baseline/` for the frozen plan,
evidence, validation state, and handoff.

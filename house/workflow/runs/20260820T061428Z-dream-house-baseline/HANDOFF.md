# Completed baseline handoff

Objective: establish the source-equivalence baseline before Dream House feature
work.

Current node: none; baseline run complete.

Confirmed:

- The public fork exists and identifies `openai/codex` as parent/source.
- Origin and upstream main match commit `5c305eb50b3e...`.
- Installed Codex is `0.147.0` with SHA-256 `19c4f144c522...`.
- The repository pins Rust `1.95.0`; the observed Homebrew compiler is `1.97.1`.
- Rust 1.95.0 plus the documented helper tools are installed and receipted.
- Source CLI and app-server build passed in 243 seconds; 32 GiB remained free.
- All eight isolated offline probes passed and generated 291 schema files.
- Local formatting, parsing, replay, privacy, source-pin, parity, and diff
  validation passed.
- Git and GitHub API independently resolved the pushed baseline branch to the
  validated commit.

Next acceptance check: open a new bounded run for the conserved event/session
tree and reversible context-view thin slice. Trace existing `thread-store`,
`rollout`, `agent-graph-store`, and app-server protocol seams before editing.

Parked: resolve canonical Pi, Atomic, and OMP repositories/licenses after the
Codex baseline. They remain donor lanes, not merge targets.

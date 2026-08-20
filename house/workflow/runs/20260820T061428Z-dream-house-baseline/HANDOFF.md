# Active handoff

Objective: establish the source-equivalence baseline before Dream House feature
work.

Current node: `push`.

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

Next acceptance check: the pushed remote branch resolves to the locally
validated commit.

Parked: resolve canonical Pi, Atomic, and OMP repositories/licenses after the
Codex baseline. They remain donor lanes, not merge targets.

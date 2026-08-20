# Baseline plan

1. Freeze fork, upstream, toolchain, installed-binary, and disk evidence.
2. Install the repository-pinned Rust toolchain and documented helper tools.
3. Build the Codex CLI and app-server from the pinned source.
4. Run offline equivalence probes with an isolated temporary `CODEX_HOME`.
5. Validate JSON, diffs, hashes, build outputs, and expected release differences.
6. Commit and push the downstream baseline branch.

## Non-goals

- No session-tree or context-view implementation in this slice.
- No provider orchestration or contractor dispatch.
- No donor repository fork before canonical identity/license intake.
- No model downloads or training.

## Acceptance

- Pinned source builds on Apple Silicon using the repository toolchain.
- Source CLI reports a version and its help surface can be captured offline.
- Source app-server help and protocol schema generation complete offline after
  dependency acquisition.
- Installed and source observations are preserved; release drift is explained,
  not mislabeled as failure.
- `git diff --check` and JSON parsing pass, and the branch contains no upstream
  core modification or private state.

# Baseline findings

The pinned source CLI and app-server build and expose their public offline
surfaces successfully. The installed release and the source checkout are not
expected to be byte- or version-identical:

- Installed reports `codex-cli 0.147.0`; an un-packaged source development
  build reports the workspace placeholder `codex-cli 0.0.0`.
- Source adds the `agents`, `queue`, and `migrate-rollouts` CLI commands beyond
  the installed release captured here. These are upstream drift, not Dream
  House patches.
- Both expose the same app-server subcommands in this probe: `daemon`, `proxy`,
  `generate-ts`, and `generate-json-schema`.
- The visible app-server help delta is an argument metavariable rename from
  `WS_URL` to `URL` for `--code-mode-host`.
- Source JSON-schema generation succeeds into an isolated temporary directory:
  291 files, 3,023,451 bytes, tree SHA-256
  `e177b35271842b76e914c44a2b9558f98f245202943c36f4b9b2134e6022c368`.

All eight probes exited zero. They used an empty temporary `CODEX_HOME`, made
zero inference requests, and preserved neither temporary configuration nor
generated schema files. The hash-bound file inventory is in
`observations/baseline.json`.

This accepts the local source-development baseline only. It does not establish
equivalence of live authentication, models, provider behavior, desktop-only
features, or session persistence.

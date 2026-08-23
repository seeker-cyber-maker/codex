# Source anchors for host-observer design

Repository baseline:
`689e6f224cc1fe2ab0f9059635a12f692f60d6f4`.

## Configuration layers

- `codex-rs/config/src/loader/README.md` defines the canonical effective
  configuration stack. Highest precedence is legacy MDM managed config,
  followed by legacy managed file, session flags, project `.codex/config.toml`,
  selected user profile, user `config.toml`, enterprise-managed layers, and
  system config. Disabled layers remain visible but do not contribute to the
  effective merge.
- `codex-rs/config/src/config_layer_source.rs` assigns the corresponding
  precedence values and provenance variants.
- `codex-rs/config/src/loader/mod.rs` contains internal
  `ignore_project_config` support, project-root discovery, trust handling, and
  project-layer loading. Internal support is not evidence of a public CLI
  contract.

## CLI isolation surface

- `codex-rs/exec/src/cli.rs` exposes `--ignore-user-config` and
  `--ignore-rules`.
- The same source states that authentication still uses `CODEX_HOME` when user
  config is ignored.
- It exposes no `--ignore-project-config` flag.
- `--ephemeral` suppresses session-file persistence; it does not prove context,
  credential, project-config, or hook isolation.
- `codex-rs/exec/src/lib.rs` initializes runtime state and environment
  management for real execution, so `codex exec` is not an observation probe.

## Project instructions

- `codex-rs/core/src/agents_md.rs` discovers instructions root-to-current
  working directory without walking beyond the discovered project root.
- At each directory, `AGENTS.override.md` wins over `AGENTS.md`, followed by
  configured fallback names.
- Project-root markers, fallback filenames, and the byte budget are themselves
  configuration-derived.
- Upstream discovery permits symlinks. This observer design does not follow
  them; their presence yields an explicit incomplete observation rather than a
  silently different context.

## Other effective-context contributors

- Trusted project `.codex` layers can contribute hooks and exec-policy rules;
  relevant behavior is exercised in `codex-rs/core/src/session/tests.rs` and
  `codex-rs/core/src/exec_policy_tests.rs`.
- `codex-rs/core/src/session/mcp.rs` covers MCP configuration and startup
  surfaces.
- `codex-rs/core/src/world_state.rs` projects application and plugin
  instructions into model-visible context when enabled and available.
- `codex-rs/cli/src/main.rs` and configuration fields governing skills show
  that skills, bundled skills, installed marketplaces, plugins, applications,
  and related instructions/tools can affect the effective session surface.

## Existing local evidence

- `house/worker_exec/cli_contract.py` validates caller-supplied `--version` and
  `exec --help` captures without invoking Codex or a provider.
- `house/workflow/runs/20260823T123112Z-runtime-qualification-inventory/QUALIFICATION_EVIDENCE.json`
  records the previously observed installed executable and CLI version, but is
  historical evidence only.
- `house/workflow/runs/20260823T123112Z-runtime-qualification-inventory/QUALIFICATION_MATRIX.md`
  identifies missing explicit argv and context-isolation evidence.
- `house/worker_exec/operation_v2.py` is the pure structural consumer boundary.
  It does not establish descriptor truth, freshness, authorship, completeness,
  or authority.

## Source-derived conclusions

1. Current Codex 0.147.0 cannot prove project configuration was ignored through
   a public `exec` flag.
2. Effective-context closure therefore requires a content-addressed inventory
   produced under a version-pinned discovery grammar.
3. A CLI capture may be consumed as immutable input, but the observer must not
   execute the binary being observed.
4. Credentials and account identity belong to a later, separate producer and
   must not enter this observation bundle.

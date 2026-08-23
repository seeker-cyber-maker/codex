# Source anchors

## Pinned source

Repository commit: `fbbf52145707bb50f7795ca2e8584b8785514199`.

| Source | SHA-256 | Design fact |
|---|---|---|
| `codex-rs/config/src/loader/README.md` | `98f0251ec2669627da874bb56e56ac4dbe96c17f9438e46e97638cbfd7611154` | Loader public surface, precedence, disabled layers, discovery distinction. |
| `codex-rs/config/src/loader/mod.rs` | `4d4aa80e53d17d88b85cef44f9e5d4e3d70b311dff511fbab3ff2ce91a75a026` | Managed/non-project composition precedes root/trust discovery; project layers run root-to-cwd; session and managed layers have later precedence. |
| `codex-rs/config/src/config_toml.rs` | `40680b8efc77bb875858b9e38ec3dc15cc8f60657d4603462aa9a783e14607b0` | Config schema includes instruction, project-doc, auth-store, MCP, plugin, and app controls. |
| `codex-rs/config/src/types.rs` | `708985866d64756417c689d6b3d85815f818672d04db31f4f7ce139b47f97d8d` | Auth storage modes include file, keyring, auto, ephemeral; MCP OAuth keyring/file/auto; auth keyring may be direct or encrypted-file-backed. |
| `codex-rs/config/src/mcp_types.rs` | `4a5e08aaffa242140eb18855878df72a5be48b873b587c12ba6c65cea2bc331e` | MCP configuration can contain literal environment values and bearer tokens as well as environment-variable names. |
| `codex-rs/core/src/agents_md.rs` | `059a4fbcc07712c3b01296bf0b775e966c4d64e5458e9bed234b18209931baa2` | Instruction discovery is config-dependent and byte-budgeted, with fallback filenames. |
| `codex-rs/secrets/src/lib.rs` | `24adb17fb1c54e0e98107f53f36e63c47b4475d6421528548eadc009ae8529ef` | Existing general secrets API has global/environment scopes, validated names, list/set/get/delete, and a local backend. |
| `codex-rs/secrets/src/local.rs` | `d43996c83710542696da20117c6413a16615858a78c59bb9be3fafaee565bf2b` | Existing storage uses separate namespaces, age encryption, an OS-keyring passphrase, atomic writes, and ciphertext/passphrase-aware MCP caching. |
| `codex-rs/secrets/src/sanitizer.rs` | `ccdd4ff1f672191c81f0586f106b8ebb35168ff10b9c186d1c8175dd69b3465b` | Regex redaction is explicitly best-effort and cannot establish arbitrary semantic secrecy. |
| `codex-rs/login/src/auth/storage.rs` | `c3d5c22fff3606ce6aa6a872f23eab7de07441922e62feb364232c0aa845373c` | Codex auth already consumes the secrets subsystem as one namespace and retains file/keyring compatibility behavior. |
| `codex-rs/rmcp-client/src/oauth.rs` | `7ce77c4cf5ef9a3d2a7bf2252166d97841e9cda48272b9727b1be4eb3c0db914` | MCP OAuth already consumes the secrets subsystem under independently derived secret names. |

## Evidence boundary

These source files are authoritative only for the pinned revision. This design
does not claim that an installed binary, desktop app, or later upstream revision
uses identical behavior. Hashes establish byte identity, not correctness,
secrecy, or authorship.

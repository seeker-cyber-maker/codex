# Source anchors - real firewall and vault threat model

Pinned repository commit:
`7fde7e524d2416973c8d19f430149a03be5fe0e9`.

No live secret/configuration source was read. All facts below come from tracked
source or sealed prior-run artifacts.

## Existing storage primitive

- `codex-rs/secrets/src/lib.rs`, SHA-256
  `24adb17fb1c54e0e98107f53f36e63c47b4475d6421528548eadc009ae8529ef`:
  `SecretsBackend` and `SecretsManager` expose `get(...) -> Option<String>`;
  scopes are global or environment; names are human-readable uppercase keys.
- `codex-rs/secrets/src/local.rs`, SHA-256
  `d43996c83710542696da20117c6413a16615858a78c59bb9be3fafaee565bf2b`:
  three encrypted files exist (`local.age`, `codex_auth.age`,
  `mcp_oauth.age`), but `load_or_create_passphrase` derives one Keychain
  account from `codex_home` without including the namespace. The backend
  decrypts an entire `BTreeMap<String,String>` and clones one selected value.
  MCP OAuth additionally caches the decrypted map plus ciphertext and
  passphrase hashes in process memory.
- `codex-rs/keyring-store/src/lib.rs`, SHA-256
  `8e345522aa87967a0ce36e6f58c09f5cbc2cd775fbccd7dd5fba2ab0e35b76ba`:
  the Keyring abstraction returns and accepts plaintext `String`/`&str`; trace
  records service, account, result, and value length, not value bytes.
- `codex-rs/secrets/src/sanitizer.rs`, SHA-256
  `ccdd4ff1f672191c81f0586f106b8ebb35168ff10b9c186d1c8175dd69b3465b`:
  redaction is explicitly best-effort regex matching and cannot serve as a
  secrecy boundary.

## Available hardening primitive

- `codex-rs/process-hardening/src/lib.rs`, SHA-256
  `9a9a62f29a3b3f3e6ff6d35bb4015bd97d14b3d83ae3e54502f3e9e953d84fae`:
  macOS hardening denies debugger attach, sets `RLIMIT_CORE=0`, and removes
  `DYLD_*` variables. Source search found only the responses API proxy calling
  `pre_main_hardening`; a future firewall/resolver does not inherit this merely
  because the crate exists.

## Accepted design lineage

- `ROOT_DESIGN_DELTA.md`, SHA-256
  `fe642b90f0f8a7be556fafaf0bff9937568b592d36eb2d2122c2e72e33433e85`:
  firewall/compiler split, real secrecy-TCB limitation, observer authenticity
  ceiling, namespace-wide resolver compromise, forbidden agent shell sinks,
  conservative post-injection incident handling, and opaque Git references.
- Synthetic-slice `HANDOFF.md`, SHA-256
  `4856222930e17e8e1de9df2aed4474f0b3e3bbff6b00a5ab86b6f4a470843f18`:
  only sealed in-memory/mock behavior has been implemented and validated.

## Source-grounded corrections to preserve

1. Separate encrypted files are not independent cryptographic namespaces when
   they share one Keychain passphrase.
2. The current general-purpose `get` API is appropriate storage plumbing but
   is not a safe model-facing broker API.
3. A process using the current backend can hold the whole decrypted namespace,
   and the MCP OAuth cache intentionally extends that lifetime.
4. Existing hardening and redaction helpers are useful defense in depth; neither
   proves containment of a new resolver or sink.

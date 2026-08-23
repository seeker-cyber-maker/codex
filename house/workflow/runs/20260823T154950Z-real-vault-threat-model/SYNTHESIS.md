# Root synthesis - real firewall and vault threat model

## Outcome

`ACCEPT_DESIGN_V1_1_NON_RUNTIME` with `ROOT_THREAT_MODEL_DELTA.md`
authoritative over the original candidate where they conflict.

The accepted design does not access Keychain, secrets, live configuration,
controller state, network, or processes. It authorizes only a later
generated-data protocol/mock-storage slice under a new scope record.

## Source findings that changed the design

The existing `codex-secrets` crate is useful storage plumbing, but not yet the
broker boundary:

- three ciphertext files share one Keychain passphrase because the account key
  is derived from `codex_home` without namespace;
- its public API returns cloned plaintext strings and decrypts a whole map;
- MCP OAuth deliberately caches a decrypted namespace; and
- regex redaction and an available process-hardening helper are defense in
  depth, not automatic containment for a new resolver.

The real broker therefore needs an independently random key per broker
namespace/epoch, a resolver-private non-`String` interface, no MCP cache reuse,
and a separately verified helper/sink boundary.

## First council reconciliation

All returned artifacts echoed transport SHA-256
`9effcb178e9187de9e4355eebb0a9e4e696417cee2731cdd89cfb929162db17f`.
Two reviewers completed; OpenRouter's primary Gemma returned 429 and its
Nemotron fallback hit its token limit, so that lane is partial.

The council reinforced process separation, independent namespace keys,
zeroizing memory, resolver-wide compromise classification, and generated-data
falsifiers. Root rejected four unsafe or incorrect reviewer statements:

1. A signed receipt does not override local deny policy; authorization is an
   intersection.
2. `NOT_EXPOSED` cannot override a delivery attempt or ambiguous post-delivery
   crash.
3. A front end given both ciphertext and its real key is expected to decrypt;
   isolation must deny it those capabilities.
4. `LD_PRELOAD` is not the relevant macOS loader falsifier; the trusted parent
   must scrub `DYLD_*` before spawn, because hardening from Rust `main` is late.

## Delta council reconciliation

All returned artifacts echoed transport SHA-256
`e4f44ccedd72403917d9029d0c06664799fd0328fcfcb4d5e3324d93ae65dc42`.
Again two reviewers completed and the same OpenRouter fallback was partial.

The completed constructive review accepted v1.1. The adversarial review asked
that the nonce ledger be a non-audit authority artifact; D3 already states
exactly that, so the condition is satisfied. Its suggestion to give the front
end real key/ciphertext in a capability test was rejected again in favor of
proving those capabilities are absent.

## Accepted architecture

1. A context firewall is the raw-configuration secrecy TCB and gets only
   parent-opened bounded inputs; it has no Keychain, vault, network, or process
   capability.
2. A policy front end sees signed authority and opaque references but cannot
   mint tickets, open ciphertext, query Keychain, or receive plaintext.
3. The controller issues one-use tickets; the resolver independently validates
   them and atomically claims a nonce in a durable authority ledger before key
   access.
4. Each broker namespace/epoch has an independent random Keychain key and a
   separate ciphertext store; existing auth/MCP stores are untouched.
5. A per-request resolver has no IP network or general IPC and writes only to a
   pre-bound `CLOEXEC` sink FD. Resolver compromise exposes its whole namespace.
6. Live v1 sinks are restricted to a plan-bound provider-header adapter or an
   inherited anonymous FD. Agent shells, environment, clipboard, files,
   terminal, arbitrary commands, and model tools are forbidden.
7. Exposure state is monotonic. Any ambiguity at/after delivery attempt is
   `POSSIBLE_EXPOSURE`, with quarantine and rotation.

## Smallest next action

Implement only typed protocol/state records, mock controller signatures,
independent generated namespace keys, mock KeyringStore/temp storage,
zeroizing buffers, and deterministic replay/crash fixtures. Add static gates
for Keychain, network, spawn, and real-secret APIs. Do not start the macOS
helper or Keychain probe in that slice.

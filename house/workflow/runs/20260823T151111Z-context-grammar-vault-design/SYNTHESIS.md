# Root synthesis - context grammar and built-in vault design

## Outcome

`ACCEPT_DESIGN_V1_1_NON_RUNTIME` with high confidence at the design claim
ceiling. The authoritative candidate is the original contract plus
`ROOT_DESIGN_DELTA.md`; where they conflict, the delta wins.

This milestone authorizes no implementation, live configuration read, Keychain
access, secret resolution, lease, launch, or runtime qualification.

## Existing Codex capability

The built-in vault is not greenfield storage. The pinned fork already provides
`codex-secrets`: age-encrypted namespace files, an OS-keyring-held passphrase,
global/environment scopes, and set/get/delete/list primitives. Codex auth and
MCP OAuth already use separate namespaces. The new work is a safe general
broker, not another encrypted database.

## First council disposition

All three lanes confirmed transport SHA-256
`f41847cff7d1ba45897ae42583d7a911f4690eafa5860caa5b9bb5fff6953e69`.
Root did not accept the first candidate unchanged because source inspection and
the reviews exposed material gaps:

- the existing observer emits hashes/metadata rather than bytes, so a pure
  semantic compiler cannot derive config values from it;
- a verifier checks consistency but cannot prove observer authenticity or
  parser non-exfiltration;
- storage encryption does not contain a resolver that can decrypt the store;
- revocation cannot retract an already injected value; and
- agent-controlled process environment is not a secret-safe sink.

The OpenRouter primary Gemma returned 429 and its Nemotron fallback finished at
the token limit with substantial response-contract chatter. Root treats that
lane as partial substantive review, not pristine completion. ClinePass and
Antigravity completed normally.

## Delta council disposition

All three lanes confirmed transport SHA-256
`36d0742c83fce26019692d81ff77295aedad189de04effb90417e86cd265167a`.
They accepted the firewall/compiler split, honest TCB, resolver compromise
ceiling, atomic sink transaction, and immutable launch binding.

Two advisory statements were rejected:

1. A verifier cannot detect an observer that lies coherently about content and
   digest. The observer/host remains authenticated TCB.
2. A resolver is not limited to active-lease exposure merely because it avoids
   persisting a key. If it can decrypt a namespace, compromise may expose the
   namespace.

The request to store all vault objects in Git was also rejected. Versioned task
policy may contain opaque reference requirements, while the authoritative
mapping, lease, and audit state stays local. This retains cross-ledger lineage
without publishing labels or stale secret state.

## Accepted architecture

1. `LocalContextFirewallV1` performs bounded staged reads and strict parsing,
   sees raw configuration, and is part of the secrecy TCB.
2. `ContextGrammarCompilerV1` is pure and sees only a safe semantic projection.
3. The existing observer independently verifies admitted candidates by
   metadata and digest.
4. `PureContextVerifierV1` checks shape, lineage, precedence, classification,
   and stage consistency but never claims source authenticity.
5. A vault policy front end issues no plaintext; a minimal resolver decrypts
   one namespace; a trusted sink adapter consumes one short lease.
6. Agent shells and arbitrary/model-visible commands are forbidden sinks.
7. Launch consumes immutable content-addressed objects or already-verified file
   descriptors, closing path observation/use races.

## Smallest next action

Implement only synthetic schemas, canonicalization, the pure grammar compiler,
and pure verifier plus failing fixtures. Mock the firewall and vault broker. Do
not read Keychain or live configuration in that first slice.

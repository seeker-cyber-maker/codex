# Root threat-model delta v1.1

This delta is authoritative where it conflicts with
`REAL_FIREWALL_VAULT_THREAT_MODEL.md`. It responds to the blind council packet
at transport SHA-256
`9effcb178e9187de9e4355eebb0a9e4e696417cee2731cdd89cfb929162db17f`.
It remains non-runtime and grants no secret or Keychain access.

## D1 - cryptographically independent broker namespace keys

Each broker namespace and key epoch gets a freshly generated independent
random key stored under a distinct Keychain account. Do not derive all
namespace keys from one broker master key in v1: compromise of that master
would collapse the intended namespace blast-radius boundary.

The Keychain account identifier may include a hash of `codex_home`, opaque
namespace ID, format version, and epoch for stable lookup; those identifiers do
not provide key entropy. Existing Codex auth and MCP OAuth accounts/files are
unchanged and never implicitly migrated.

## D2 - deny precedence and delivery-state precedence

A signed authority receipt is necessary but never overrides local policy,
current epoch, sink allowlists, binary identity, TTL, use count, or an incident
lock. Effective authorization is the intersection of valid upstream authority
and every local restriction. Any contradiction fails closed.

Exposure precedence is monotonic:

```text
no delivery attempt proven -> NOT_EXPOSED may be recorded
delivery attempted or uncertain -> POSSIBLE_EXPOSURE
confirmed disclosure -> EXPOSED
```

`NOT_EXPOSED` never overrides `DELIVERY_ATTEMPTED`, missing post-delivery audit,
or an ambiguous crash. Later evidence can raise exposure severity but cannot
downgrade it without a separately proven reconciliation artifact.

## D3 - resolver-side authority and replay enforcement

The policy front end is a non-secret request validator/forwarder; it is not a
lease issuer and holds no signing key that can mint secret-consumption rights.
The authenticated Dream House authority/controller issues a one-use
`VaultLeaseTicketV1` bound to the complete resolve intent.

Before any Keychain or ciphertext access, the resolver independently verifies
the controller signature and every ticket field. It then atomically claims the
nonce in a broker-owned durable spent/active ledger. Duplicate, expired,
unknown-epoch, wrong-audience, or already-claimed tickets stop before secret
access. A per-request resolver may use the ledger through a minimal broker
primitive; it cannot trust the front end's claim that a nonce is fresh.

This ledger is authority state, not an audit log. Audit hashes alone cannot
prevent replay or prove a compromised writer truthful.

## D4 - macOS spawn and loader boundary

Calling `pre_main_hardening()` from Rust `main` is too late to prevent the
dynamic loader from acting on inherited `DYLD_*` variables. A future trusted
parent must construct a minimal clean environment before `posix_spawn`/exec,
close all unrelated descriptors, and launch a signed/hardened resolver whose
library-loading policy is verified. The helper must still apply debugger denial
and `RLIMIT_CORE=0` before reading ciphertext or contacting Keychain.

The exact combination of code-signing/library-validation, Seatbelt rules,
securityd/Keychain access, and local IPC remains unverified. Generated canary
tests must prove the actual enforced profile. Source-level intent is not
runtime containment evidence.

Use the macOS-relevant injection variable (`DYLD_INSERT_LIBRARIES`) in the
falsifier; an `LD_PRELOAD` test alone is not evidence for macOS.

## D5 - capability tests, not impossible cryptographic claims

Do not test that a policy front end fails to decrypt after deliberately giving
it both ciphertext and the corresponding Keychain key. A component with both
inputs is expected to decrypt. Instead, prove the front end's launched profile
cannot open the broker ciphertext path, cannot query the namespace Keychain
account, and receives neither capability through inherited FDs or IPC.

Similarly, sandbox denial tests establish observed behavior for a pinned build
and OS profile; they do not prove a malicious resolver has no covert channel.
Resolver compromise still marks the entire namespace exposed.

## D6 - front end, resolver, and sink TCB correction

The front end is outside the **plaintext** TCB but remains inside the
availability/policy-routing TCB. The resolver, qualified sink, controller/lease
issuer, OS kernel, Keychain/securityd, and trusted spawn path are in the secret
delivery TCB. The context firewall is separately in the raw-configuration
secrecy TCB.

No single component compromise is claimed harmless:

- front-end compromise can deny service and attempt valid-ticket misuse but
  cannot mint tickets or access storage;
- resolver compromise exposes its readable namespace;
- sink compromise exposes the delivered value and any request destinations it
  can reach;
- controller/signing compromise can mint apparently valid leases and therefore
  requires a global incident lock plus key/credential rotation.

## D7 - incident administration and YubiKey

`POSSIBLE_EXPOSURE` automatically locks affected consumption and requires
human reconciliation plus credential rotation. It does not mandate the active
YubiKey as the only clearance route in v1. The working key may be an optional
human-presence factor after a separate recovery design; the faulty second key
is excluded. Loss of one device must not make incident containment impossible.

## Corrected first implementation boundary

The next implementation may include only protocol/state types, mock controller
signatures, generated independent namespace keys, mock KeyringStore, temp
storage, zeroizing buffers, and deterministic crash/replay fixtures. It may not
invoke macOS Keychain, spawn the real resolver, use network, or consume a real
secret. Promotion beyond that boundary requires another explicit authority
record.

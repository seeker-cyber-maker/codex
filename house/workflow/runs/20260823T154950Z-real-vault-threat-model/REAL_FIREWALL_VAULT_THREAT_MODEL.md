# Real firewall and Codex vault broker threat model v1 candidate

## Claim ceiling

This document is a non-runtime security contract. It proposes how a later
implementation should be partitioned and tested. It proves no macOS Keychain,
Seatbelt, resolver, egress, or secret-injection behavior.

## Assets and adversaries

Protected assets are secret values, namespace decryption keys, opaque-reference
mappings, authority receipts, lease state, audit integrity, safe context
projections, and the absence of secret-derived material from model-visible or
cloud-visible output.

The design treats prompt-injected models, untrusted contractors/plugins/config,
wrongly routed tasks, compromised agent shells, and accidental operator errors
as expected hostile inputs. It also models separate compromise of the context
firewall, policy front end, observer, resolver, and sink adapter. Root/OS/kernel
or Keychain compromise is outside the containment claim, but still triggers
credential rotation and incident response.

## Component boundaries

| Component | May observe | Explicitly forbidden | Compromise ceiling |
|---|---|---|---|
| Agent/orchestrator | opaque `ref_id`, policy class, non-secret receipts | secret label/value, Keychain, resolver API, sink choice outside sealed plan | can request but cannot mint authority or retrieve plaintext |
| Context firewall | bounded raw config bytes from pre-opened inputs | network, subprocess, Keychain, vault files, logs/raw diagnostics | all configuration it is allowed to parse |
| Grammar compiler/verifier | safe projections and authenticated metadata | raw config, secret values, ambient reads | falsified grammar/receipt, not source exfiltration |
| Policy/lease front end | signed authority, opaque mapping metadata, epochs, sink identity | storage key, ciphertext decryption, plaintext secret | denial/lease abuse attempts; no storage-value read |
| Resolver helper | one independently keyed broker namespace, one bound lease, one output FD | network, model/tool IPC, arbitrary filesystem, subprocess, general plaintext response | entire readable namespace; never claim active-lease-only exposure |
| Qualified sink adapter | one value for one bound operation plus minimum request material | arbitrary destinations, logging value/headers, child inheritance, model-visible output | delivered value and all requests it can originate |
| Audit/controller | identifiers, hashes, epochs, state transitions, exposure class | secret value or value-derived fingerprint | can corrupt evidence/availability; cannot be secret source |

The context firewall and resolver are different binaries/profiles. A component
allowed to parse configuration must not thereby gain Keychain access. A
component allowed to decrypt broker storage must not receive model prompts or
general network access.

## Storage and namespace contract

The implementation should extend `codex-secrets` storage mechanics without
exposing its plaintext `get` method to agent/model surfaces.

1. Add a broker-only namespace type and encrypted storage path. Do not alter or
   migrate Codex auth or MCP OAuth stores implicitly.
2. Derive a distinct Keychain account per broker namespace and key epoch. The
   present `compute_keyring_account(codex_home)` is shared across files and is
   therefore not sufficient cryptographic compartmentalization.
3. Partition broker namespaces by blast-radius policy (for example provider or
   trust domain), not by user-supplied secret label. Mapping from opaque
   `ref_id` to label/provider/value remains local and outside Git.
4. Do not reuse the MCP OAuth plaintext cache. Wrap decrypted byte buffers and
   selected values in explicit zeroizing containers; avoid clones and ordinary
   `String` return values across the resolver boundary.
5. Enforce explicit directory/file modes in addition to encryption. Treat
   ciphertext integrity, schema version, key epoch, and namespace ID mismatch
   as terminal failures.
6. Rotation creates a new value revision and key epoch, invalidates outstanding
   leases, and preserves a non-secret supersession/tombstone record. It never
   rewrites history to imply old deliveries were retracted.

## Authority and opaque-reference contract

A repository may state that a task requires `{ref_id, scope_class,
required_sink, minimum_revision}`. It may not contain the secret label, account
metadata, Keychain account, encrypted-store path, lease token, or value-derived
digest.

`ResolveIntentV1` must bind:

- operation, plan, task, worker, and authority-receipt hashes;
- opaque `ref_id`, minimum revision, broker namespace, and current vault epoch;
- exact audience and qualified sink kind;
- immutable sink instance identity (binary/content hash and platform identity
  where available);
- one use, short TTL, nonce, and non-retry semantics.

The front end verifies an authority receipt minted outside the broker. It
cannot self-approve, substitute a sink, increase use count/TTL, or delegate
rights. A replacement model/worker cannot grant a child more authority than its
own task packet, and secret-consumption rights are non-delegable in v1.

## Sink contract

Live v1 supports only:

1. a dedicated provider-header/egress adapter with an endpoint allowlist bound
   in the plan; or
2. an inherited anonymous FD delivered to an already-qualified consumer.

General shell environment, arbitrary command arguments, clipboard, files,
terminal input, model-visible tools, and child-process inheritance are
forbidden. The synthetic `qualified_process_env` vocabulary is not approval to
implement process-environment delivery; that sink remains deferred.

The resolver writes only to a pre-bound `CLOEXEC` channel owned by the selected
sink. It never returns plaintext to the policy front end. The sink emits only
typed outcome codes and mediated response data; request headers, environment,
crash reports, debug descriptions, and tracing fields must exclude the value.

## Lease transaction and crash semantics

There is no honest cross-process atomic operation that both delivers a secret
and durably proves consumption without a crash window. V1 therefore uses a
conservative state machine:

```text
PREPARED
  -> INTENT_DURABLE
  -> SINK_BOUND
  -> DELIVERY_ATTEMPTED
  -> CONSUMED
  -> OUTCOME_DURABLE
```

- Failure before `DELIVERY_ATTEMPTED`: `NOT_EXPOSED`; close channels and expire
  the unused lease.
- Any failure at or after `DELIVERY_ATTEMPTED` without a final durable outcome:
  `POSSIBLE_EXPOSURE`; kill/quarantine the sink, invalidate the lease and vault
  epoch, notify the coordinator, and require credential rotation.
- A timed-out or disconnected caller never reuses a lease. A new attempt needs
  a fresh authority-bound lease after reconciliation.
- Audit write/fsync failure before delivery stops. Audit failure after delivery
  is an incident, never a success with a warning.

Audit records contain state, identifiers, hashes of non-secret records, and
exposure classification only. They contain no value, raw header, response body,
secret-derived hash, or human label. Hash chaining provides tamper evidence,
not truth about a compromised writer.

## macOS containment profile

Each new helper must start from a minimal, pinned executable and fail closed if
hardening cannot be applied. Required properties include debugger denial,
`RLIMIT_CORE=0`, scrubbed `DYLD_*` and inherited environment, closed unrelated
FDs, no subprocess API, bounded memory/input/output, and no diagnostic path
that prints raw input.

The context firewall gets read access only through parent-opened immutable or
immediately verified FDs. The resolver gets only its broker ciphertext path,
the exact Keychain capability needed for its namespace, one local control FD,
and one sink FD. It has no IP network capability. The qualified egress adapter
is a separate, larger TCB whose network destinations are plan-bound.

Whether macOS Seatbelt can simultaneously deny general network/filesystem
access while permitting the required Keychain/securityd interaction is an
unverified implementation fact. It must be tested with generated credentials
under direct user observation before any real secret is admitted.

## Operator and YubiKey role

Secret enrollment, label/mapping inspection, rotation, and deletion are
operator-only ceremonies and never model tools. Input should use a local secure
prompt rather than command arguments, environment, clipboard, or logs.

The currently functional YubiKey may later provide human-presence approval for
administrative or high-risk lease ceremonies. It is not the sole recovery key
and is not required for every routine headless request in this candidate.
Adding it to decryption or account recovery is a separate design and user
presence gate; the faulty second key is not part of v1.

## Disposable implementation ladder

1. **Protocol-only:** typed Rust records/state machine and pure validation;
   generated values only, no storage or process.
2. **Mock storage:** temp directory plus mock KeyringStore; verify per-namespace
   keys, zeroization wrappers, file modes, corrupt/newer schema, and rotation.
3. **Helper containment:** generated canary values in isolated child helpers;
   prove no network/subprocess/arbitrary file access, FD non-inheritance, core
   suppression, bounded output, and kill-on-audit-failure.
4. **Mock sink:** local loopback test server or pipe with a generated canary;
   prove endpoint/audience binding, replay rejection, and exact exposure state.
5. **macOS Keychain probe:** only with explicit user-present approval, a new
   disposable Keychain item, no existing Codex key or secret file, and a
   deletion/reconciliation receipt.
6. **Real-secret admission:** separate human authority after all prior stages,
   source seal, independent verification, outside review, and rollback drill.

## Required falsifiers before promotion

- Front end cannot open broker ciphertext or load a Keychain item.
- Resolver cannot connect to loopback, Internet, arbitrary Unix sockets, spawn,
  or open paths outside its exact namespace.
- Wrong task/worker/audience/sink/binary hash/epoch/revision/TTL/use count fails
  before Keychain access.
- Agent shell/process-env request fails even with a syntactically valid lease.
- Replayed, duplicated, expired, or post-rotation leases fail.
- Generated canary never appears in stdout, stderr, structured logs, journal,
  terminal, model context, crash/core artifacts, process listing, or child env.
- Corrupt ciphertext, wrong namespace key, and newer schema fail without
  overwriting storage or creating a new key silently.
- Crash before delivery records `NOT_EXPOSED`; every induced crash at/after
  delivery records `POSSIBLE_EXPOSURE` and triggers quarantine/rotation.
- Compromised-resolver exercise marks the whole test namespace exposed.
- Path replacement between admission and use fails; already-bound immutable
  inputs remain stable.

## Promotion blockers

Real implementation remains blocked until the design review resolves:

1. exact broker namespace/key derivation and migration-free coexistence with
   current stores;
2. a macOS helper containment mechanism compatible with Keychain access;
3. the provider-header adapter's endpoint/TLS/proxy identity binding;
4. audit authority, durable state location, and incident notification path;
5. executable signing/hash/update semantics without pinning the fork forever;
   and
6. operator recovery when the active YubiKey or Keychain is unavailable.

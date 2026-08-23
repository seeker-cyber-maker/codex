# Root design delta v1.1

This is a post-review delta. It does not alter the immutable packet reviewed at
transport SHA-256
`f41847cff7d1ba45897ae42583d7a911f4690eafa5860caa5b9bb5fff6953e69`.
It supersedes the affected boundaries in
`CONTEXT_GRAMMAR_AND_VAULT_CONTRACT.md`.

## D1 - split the runtime projector from the grammar compiler

The reviewed contract cannot be implemented as written if the existing host
observer returns only metadata and SHA-256 rather than file contents. A pure
compiler cannot derive semantic configuration from a digest.

The corrected runtime flow is:

```text
finite candidate request
  -> LocalContextFirewallV1 (bounded read + strict parse, secrecy TCB)
       -> safe semantic projection + admission receipt
  -> ContextGrammarCompilerV1 (pure)
       -> finite grammar
  -> existing HostObserverV1 (independent hash/metadata observation)
  -> PureContextVerifierV1
```

`LocalContextFirewallV1` is the only new component allowed to see raw structured
configuration. Raw bytes remain memory-local and are never journaled, logged,
returned as tool output, or sent to a model/cloud lane. It performs the staged
candidate expansion described in the contract. The grammar compiler receives
only the allowlisted semantic projection.

The firewall is in the secrecy TCB. The pure verifier can prove output shape,
lineage, and consistency; it cannot prove that a compromised parser did not
leak an input while parsing it. The firewall therefore requires a small audited
implementation, disabled diagnostics/core dumps, bounded memory lifetime, and
zero network/process/extension capability.

## D2 - secret-bearing and arbitrary content admission

Literal secret fields in structured configuration yield
`INCOMPLETE_SECRET_DEPENDENCY` before a raw whole-file digest is emitted. The
remediation path is an explicit migration to a vault reference; the system does
not silently migrate, redact, or hash the literal.

Free-form content cannot be classified secret-free from its prose. V1 admits it
only when an independently signed content-admission receipt pins the expected
digest and privacy class. Otherwise it yields `INCOMPLETE_PRIVATE_TEXT`.
Admission is a human/policy claim, not mathematical proof; local scanners are
defense in depth. Cloud artifacts omit private content and its raw digest.

The existing host observer runs only after firewall/admission success. Its
content SHA-256 must match the admitted expected digest. This preserves its
current API without using it as a semantic parser.

## D3 - observation authenticity and launch TOCTOU

Observer epochs and digests provide consistency, not authenticity. A compromised
observer can lie coherently. Runtime qualification must pin and authenticate the
observer executable and treat the observer/host boundary as TCB. The verifier
must not claim it can detect arbitrary observer compromise.

Hash equality at observation time does not bind later path reads. A future
launcher must consume immutable content-addressed copies or already-verified
open file descriptors, then bind those exact objects to the operation receipt.
If a source must be reopened by path, it is re-observed immediately before use
and any mismatch invalidates qualification.

## D4 - vault compromise ceiling

The storage encryption protects secrets at rest, not from a running broker that
can ask Keychain for the decryption key. Compromise of the resolver/backend can
expose every secret readable in that namespace, not merely active leases.

The minimum implementation therefore separates:

- a policy/lease front end with no storage key;
- a minimal resolver with no network/model/logging capability;
- independently keyed namespaces where practical;
- a sink adapter receiving one resolved value for one lease.

A global vault epoch invalidates all leases during an incident, but does not
erase an already disclosed value. Namespace rotation and credential rotation
are separate recovery operations.

## D5 - trusted sinks, atomic consumption, and revocation

No secret may be injected into an agent-controlled shell, arbitrary command, or
model-visible tool. `process_env` is permitted only for a pinned, qualified
consumer binary under a containment profile that blocks environment/core/crash
exposure and mediates output. Preferred sinks are a dedicated request-header
adapter or inherited anonymous file descriptor.

Lease consumption is transactional:

1. append and fsync a pre-use audit intent;
2. validate authority, epoch, revision, audience, sink, use count, and TTL;
3. create/contain the target without exposing the secret;
4. inject through the bound sink and atomically consume the lease;
5. append and fsync the outcome.

Failure before injection exposes nothing and stops. Failure after injection
kills/quarantines the consumer, revokes the lease, records an incident, and
requires secret rotation when the value may have escaped. Revocation prevents
future use; it cannot retract a value already delivered.

## D6 - vault references and Git

Repository policy may declare that a task needs an opaque `ref_id`, sink class,
and scope class. The authoritative mapping from `ref_id` to human label,
provider/account metadata, and encrypted value remains local vault state. It is
not required to be in Git. Leases and audit events are never committed as task
configuration. This rejects the reviewer proposal to store all `VaultRefV1`
objects beside grammar files, which would unnecessarily leak durable metadata
and encourage stale reference state.

## D7 - corrected source precedence

The ruleset reproduces the pinned Codex loader precedence; it does not invent
`system > enterprise > project > session`. Legacy managed sources remain above
session/project in the final stack, while project discovery uses the effective
non-project inputs as described by pinned source. Any reviewer statement to the
contrary is non-authoritative.

## Added falsifiers

1. Give the firewall a synthetic config containing a low-entropy secret; no raw
   value or whole-file hash may occur in stdout, stderr, logs, crash artifacts,
   projection, or council packet.
2. Make the observer return internally consistent false bytes/digests; the
   verifier must not label that observation authenticated.
3. Mutate a verified path before launch; a path-reopen launch must fail, while
   an already-bound immutable object remains unchanged.
4. Compromise the lease front end alone; it must lack storage-key access.
5. Compromise the resolver in a test namespace; the claim ledger must classify
   the whole namespace as exposed.
6. Cause post-injection audit failure; the target must be terminated and the
   reference marked rotation-required.
7. Ask an agent-controlled shell to receive a secret environment variable; the
   broker must reject the sink even with a valid reference.

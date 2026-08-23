# Codex context grammar and vault broker contract v1

Status: design candidate. No implementation or runtime authority.

## 1. Boundary

The context producer is a deterministic compiler over explicitly supplied,
version-bound observations. It does not call the Codex loader, read the host,
resolve a secret, start a process, or infer missing contributors. Its output is
a finite `CodexContextGrammarV1` consumed by the existing host observer.

The vault is not part of that compiler. Codex already has an encrypted secrets
storage primitive. A future `VaultBrokerV1` mediates opaque references and
short-lived sink-bound leases over that primitive. The producer may report that
a reference is configured; it cannot retrieve its value.

```text
sealed ruleset + staged inert observations
        -> semantic projector -> finite context grammar -> host observer

opaque vault reference -> policy/controller -> short lease -> trusted sink
                                      (plaintext never enters context grammar)
```

## 2. Ruleset identity

`CodexContextRulesetV1` contains:

- exact Codex repository commit;
- SHA-256 for every source file defining loader, instruction, plugin, skill,
  hook, app, MCP, and vault semantics used by the ruleset;
- ruleset schema/version and canonicalization algorithm;
- platform and path-normalization profile;
- supported config schema keys and per-key projection classification;
- stage graph, maximum contributor counts/bytes, and required observer policy;
- grammar-producer and pure-verifier identities.

Any source hash mismatch yields `RULESET_SOURCE_MISMATCH`. A later Codex revision
requires a new ruleset; compatibility is never inferred from a version string.

## 3. Staged derivation

Project discovery depends on effective non-project configuration, while later
instruction and extension discovery depends on the full effective config. One
wide filesystem scan would therefore be both excessive and semantically wrong.
The producer uses bounded stages.

### Stage A - bootstrap candidates

From the ruleset, platform, supplied Codex-home locator, selected profile, and
session overrides, derive only the finite candidate set for packaged defaults,
system, enterprise-managed, base-user, selected-profile, session, legacy
managed-file, and managed-preference layers. The producer emits an observation
request; the host observer returns presence/type/bytes/digest evidence only for
that request.

### Stage B - non-project projection

Parse observed structured inputs strictly. Apply Codex precedence, disabled
layer semantics, managed discovery overlays, CLI overrides, and requirements.
Derive the effective project-root markers and trust inputs. An unknown key,
unsupported source kind, unavailable managed input, or unsafe value stops the
stage; it is not silently dropped.

### Stage C - project candidates

Using only Stage B output plus supplied cwd facts, derive the finite ancestor
walk and marker candidates. After observation, select the project root and
derive `.codex/config.toml`, hook, rule, and checkout candidates from root to
cwd. Observe only those candidates. Untrusted layers remain described with a
disabled reason and do not contribute to effective behavior.

### Stage D - full effective projection

Merge project layers with the remaining layers at pinned Codex precedence.
Derive the instruction filenames, fallback names, byte budget, hook/rule
locators, enabled plugin/app declarations, MCP declarations, and skill roots.
Dynamic contributors not reducible to a finite locator set yield
`INCOMPLETE_DYNAMIC_SOURCE`.

### Stage E - content candidates and final grammar

Observe the exact instruction, hook, rule, skill, plugin, app, and MCP metadata
candidates derived by Stage D. Emit the final grammar only when every enabled
contributor has an explicit disposition: included, absent, disabled by trusted
policy, or fail-closed. Revalidate all stage bindings before acceptance.

## 4. Stage binding and dirty-state rule

Every request and response binds:

- operation ID, stage ID, parent-stage digest, ruleset digest;
- observer implementation digest and observation policy digest;
- normalized root/cwd locator IDs and platform profile;
- ordered candidate list and maximum sizes;
- source epochs and content digests returned by the observer.

The final verifier rejects mixed operations, missing parents, reordered
candidates, path aliases, changed epochs, or a contributor whose final digest
differs from its stage digest. Any source change yields
`UNSTABLE_STAGE_RETRY_REQUIRED`; the system restarts from the earliest affected
stage, never merely patches the final bundle.

## 5. Semantic projection

Projection is allowlist- and schema-based, not regex-based. Each supported key
has exactly one classification:

1. `BEHAVIOR_VALUE`: canonical value may enter the local semantic projection.
2. `PUBLIC_LOCATOR`: normalized locator may enter local projection; cloud
   packets use a root-relative or opaque locator ID.
3. `SECRET_REFERENCE`: opaque reference ID, required sink type, scope class,
   and presence may be emitted; label and value may not.
4. `SENSITIVE_PRESENCE_ONLY`: key path, type, and presence only; no value or
   value-derived digest.
5. `PUBLIC_CONTENT_ADDRESSABLE`: arbitrary bytes may be referenced only when a
   separately reviewed public/committed expected digest is already sealed.
6. `DENY`: field is forbidden for the target projection.

Any unclassified key yields `INCOMPLETE_UNKNOWN_KEY`. Strict parsing rejects
duplicate keys, type confusion, non-canonical encodings, unsupported aliases,
and normalization collisions.

Literal MCP `env` values, literal bearer tokens, auth payloads, OAuth payloads,
cookies, authorization headers, passwords, private keys, and URL userinfo or
credential-like query parameters are never emitted or hashed. Environment
variable *names* may be emitted when the pinned schema identifies them as
names, not values.

Arbitrary Markdown, instructions, source files, and tool prose are not proven
secret-free by redaction. Private content yields `INCOMPLETE_PRIVATE_TEXT`.
Public content can be admitted only through the pre-sealed content-addressable
route. Best-effort redaction remains defense in depth for display, never an
acceptance test.

Local and cloud projections are different signed artifacts. The cloud form
removes user names, absolute paths, stable machine IDs, vault labels, and
private arbitrary content. A local-safe result does not imply `cloud-ok`.

## 6. Built-in vault

### 6.1 Reuse, do not replace

The existing `codex-secrets` local backend remains the storage engine: encrypted
files under Codex home with the encryption passphrase held in the OS keyring.
Existing Codex-auth and MCP-OAuth namespaces stay independent. A fourth
project/worker namespace may be added only through a versioned migration.

### 6.2 Reference model

A config or task contains `VaultRefV1`, never a value:

```json
{
  "ref_id": "vr_7f0c...",
  "scope": "environment",
  "required_sink": "process_env",
  "revision": 3
}
```

`ref_id` is random and non-semantic. Human-facing labels and provider/account
metadata remain local vault metadata and are excluded from model/cloud
projections by default. Listing returns reference IDs, scope class, revision,
status, and allowed sink classes—never values or value digests.

### 6.3 Lease and resolution

Only the controller may ask the broker for `VaultLeaseV1`. Issuance requires an
authenticated operation, worker identity, exact task/source/plan hashes,
approved capability, reference revision, target sink, TTL, use count, and an
unexpired authority decision. A relay, model, grammar producer, observer,
reviewer, or task document cannot issue or delegate a lease.

The broker resolves directly into one approved sink:

- a single child-process environment variable;
- a child-process stdin/file descriptor that is never persisted;
- a specific outbound request header owned by a trusted provider adapter.

There is no general `get plaintext` model tool in v1. Values never appear in
argv, prompts, tool results, journals, receipts, shell history, crash reports,
or durable environment snapshots. The broker returns only success/failure,
lease ID, reference revision, sink class, and timestamps.

### 6.4 Revocation and failure

Revoking a reference increments its revision and invalidates every outstanding
lease. Leases are single-use by default, short-lived, audience-bound, and
non-delegable. Child workers cannot confer broader or longer access than their
own grant. Broker restart invalidates in-memory leases unless a separately
reviewed recovery protocol proves otherwise.

Keychain unavailable, storage corruption, revision mismatch, ambiguous sink,
unsupported provider adapter, missing approval, expired TTL, or audit-write
failure all fail closed. File fallback is never automatic for the managed
worker namespace. Existing auth compatibility fallback behavior does not set
precedent for new worker secrets.

### 6.5 Audit and display

The append-only audit records reference ID, revision, operation/worker/task IDs,
authority receipt, requested and actual sink class, outcome, timestamps, and
revocation lineage. It records no secret value, plaintext-derived digest,
provider account label, or raw command/environment. Repeated denials and every
near miss enter monitoring as actionable incidents.

The operator UI supports set/rotate/revoke/list/test-presence ceremonies. Secret
entry uses an OS-secure input surface; values are never echoed and cannot be
retrieved back through the dashboard. YubiKey presence may approve a policy
ceremony later, but a USB touch is neither identity nor vault decryption by
itself.

## 7. Producer states

- `GRAMMAR_DERIVED_NOT_OBSERVED`
- `PROJECTION_DERIVED_NOT_QUALIFIED`
- `RULESET_SOURCE_MISMATCH`
- `INCOMPLETE_UNKNOWN_KEY`
- `INCOMPLETE_SECRET_DEPENDENCY`
- `INCOMPLETE_PRIVATE_TEXT`
- `INCOMPLETE_DYNAMIC_SOURCE`
- `UNSTABLE_STAGE_RETRY_REQUIRED`
- `VAULT_REFERENCE_PRESENT_NOT_RESOLVED`

None of these states qualifies a runtime, issues authority, or permits launch.

## 8. Pure verification

The grammar/projection verifier accepts inert records and performs no
filesystem, clock, environment, process, network, keychain, vault, or random
I/O. It checks canonical serialization, ruleset/source identities, stage DAG,
candidate completeness, precedence, classifications, source epochs, content
digests, projection privacy class, and terminal state. Vault audit verification
is separate and likewise sees no values.

## 9. Falsification fixtures

The later implementation must include at least:

1. non-project config changes project-root markers;
2. project config changes instruction fallbacks and byte budget;
3. managed/MDM precedence overrides project/session inputs;
4. profile selection conflicts with legacy profile configuration;
5. unknown structured key and duplicate/type-confused key;
6. obvious secret and innocuous-looking key containing a secret;
7. URL userinfo and credential-like query parameter;
8. MCP literal env/bearer values versus environment-variable names;
9. private Markdown versus pre-sealed public digest, including mismatch;
10. dynamic plugin/MCP contributor discovered after its stage;
11. cross-stage mutation and epoch mismatch;
12. case, Unicode, symlink, and canonical-path collision;
13. cloud projection leaks an absolute path, user name, vault label, or stable
    machine ID;
14. outputs contain a raw secret or a digest derived from it;
15. pure verifier is patched to fail on every ambient API;
16. expired, replayed, wrong-worker, wrong-sink, wrong-revision, and delegated
    vault leases;
17. broker failure after injection but before audit confirmation;
18. Keychain unavailable and encrypted store corrupted;
19. revocation races an in-flight single-use lease;
20. child process dumps environment or crash metadata.

## 10. Implementation slices after acceptance

1. Pure schemas, canonicalization, classifier, and verifier with synthetic
   fixtures only.
2. Staged grammar producer wired to the existing observer using synthetic
   Codex homes; no vault resolution.
3. Vault reference and audit schemas plus mock broker; no Keychain access.
4. Local backend integration and secure sink adapters under a new authority
   ceremony and independent security review.

Each slice gets its own source seal, tests, council disposition, and handoff.

# Dream House read-only host observer contract v1

Status: design candidate for outside review.

## 1. Claim ceiling

The observer reports a bounded, content-addressed snapshot of measured host
facts. Its only successful semantic state is:

`OBSERVED_NOT_QUALIFIED`

It never emits `QUALIFIED`, `READY`, `TRUSTED`, `AUTHORIZED`, `ADMITTED`, or an
equivalent. A valid observation grants no execution, provider, credential,
controller, lease, reservation, or result-admission authority.

A canonical hash proves byte identity only. It does not prove authorship,
signature, trust, freshness, completeness outside the declared grammar, or
fitness for execution.

## 2. Components and trust boundaries

The design has three non-overlapping components:

1. **Observer** - reads only request-authorized regular files and metadata,
   applies a sealed discovery grammar, and emits one snapshot bundle.
2. **Pure verifier** - accepts the request, policy, grammar, snapshot, and
   referenced descriptors as caller-supplied values; performs no host I/O.
3. **Later admission gate** - may decide whether a verified observation is
   sufficiently fresh, signed, trusted, and complete for a separately defined
   runtime profile. It is outside this contract.

The observer does not invoke Codex, Git, a shell, a plugin, an MCP server, a
hook, an application connector, an import mechanism, or any observed binary.
CLI version/help text is an immutable caller-supplied capture with its own
provenance; it is never generated inside the observer.

## 3. Request

`HostObservationRequestV1` contains exactly:

- `request_id` and `operation_id`;
- injected `observed_at_utc` and `expires_at_utc` strings;
- canonical requested `cwd`, workspace boundary, executable path, and
  `codex_home` locator;
- the expected executable byte hash;
- an independently supplied CLI-capture descriptor and expected capture hash;
- a discovery-grammar identifier and grammar hash;
- explicit configuration/session inputs needed by that grammar, including
  non-secret CLI overrides and selected profile name;
- finite read roots and exact allowed path classes;
- numeric limits for entries, cumulative bytes, per-file bytes, depth,
  retries, and observation duration; and
- the expected observation-policy hash.

Unknown keys, duplicate keys, noncanonical paths, ambiguous Unicode path
normalization, relative paths, invalid time ordering, zero/negative limits, or
cross-record identifier disagreement reject the request before any read.

## 4. Finite discovery grammar

The grammar is version-pinned to reviewed Codex source and enumerates the
contributors that can affect the requested session:

- executable bytes and non-executing file metadata;
- system, enterprise-managed, user/profile, project, session-flag, and legacy
  managed configuration layer descriptors in effective precedence order;
- project-root markers and project `.codex/config.toml` layers from root to
  `cwd`;
- global/user instructions and project instruction candidates from root to
  `cwd`, including override/default/fallback precedence and byte budget;
- hooks and exec-policy rule files that the effective configuration can load;
- skill roots and selected skill instruction/resources;
- plugin manifests, installed marketplace descriptors, application
  instructions, MCP server definitions, and tool projections that can enter
  the session; and
- the exact non-secret environment-variable names and values that the reviewed
  loader consumes, plus presence-only markers for secret-classified names.

The grammar defines closure over these contributor classes, not over every file
in the workspace or home directory. Every discovered entry carries the source
rule that caused its inclusion or exclusion. An unknown contributor class,
unreviewed grammar version, or enabled dynamic source without a finite
descriptor produces `INCOMPLETE_CONTEXT_CLOSURE`.

Because Codex 0.147.0 exposes no public `--ignore-project-config` flag, this
grammar cannot emit `PROJECT_CONFIG_IGNORED` for that CLI. It must inventory the
project layers or refuse closure.

## 5. Secret boundary

The following are never opened, hashed, copied, parsed, or included by value:

- `auth.json`, cookies, browser/session databases, keychains, SSH material,
  API tokens, bearer credentials, client secrets, private keys, and provider
  account records;
- environment values whose names or policy classifications are secret-bearing;
  and
- arbitrary database contents unrelated to the finite context grammar.

If the grammar requires a secret-bearing source to compute effective behavior,
the observer emits a presence-only `REDACTED_SENSITIVE_PRESENT` fact and the
bundle state becomes `INCOMPLETE_SECRET_DEPENDENCY`. A hash is not accepted as
safe redaction because it can remain a stable secret identifier.

Credential and account/pool evidence require a separate future producer and a
separate authority review.

## 6. Filesystem safety and stability

For every path component and discovered entry, the observer uses `lstat`-style
metadata and refuses:

- symlinks or aliases requiring traversal;
- hard-linked regular files with link count greater than one;
- sockets, devices, FIFOs, mount crossings, sparse/clone ambiguity not covered
  by policy, and other special types;
- paths escaping the declared canonical roots; and
- case-folding or Unicode-normalization collisions.

Refusal is explicit evidence, never silent omission. This intentionally differs
from upstream project-instruction discovery, which permits symlinks; a session
that depends on one is not closed by v1.

For an admitted regular file, the observer records canonical path, relative
path under its declared root, device, inode, mode, link count, size, and
nanosecond modification/change times; hashes exact bytes once; then repeats
metadata. Any identity or metadata change yields `UNSTABLE_RETRY_REQUIRED` and
zero usable descriptor for that attempt.

Directories are enumerated in byte-sorted relative-path order. Pre/post
directory metadata and the complete typed child inventory are bound into a
Merkle-style directory receipt. A bounded retry may restart the entire
observation; entries from different attempts are never mixed.

## 7. Descriptor families

One bundle contains four independently hashed descriptor families:

### 7.1 Executable identity

Exact executable path, regular-file metadata, byte SHA-256, expected-hash
comparison, and an explicit `NOT_EXECUTED` field. Executable bits being present
does not establish that the file is runnable or safe.

### 7.2 CLI-contract capture

Reference to caller-supplied version/help bytes, capture hash, capture producer
identity if supplied, and validation result from the existing pure CLI-contract
grammar. The observer never generates or trusts the capture merely because it
matches executable naming.

Executable/capture association remains `ASSERTED_BINDING_ONLY` until a later
admission gate accepts the capture provenance.

### 7.3 Workspace and project inputs

Canonical `cwd`, workspace boundary, filesystem identity, project-root
discovery trace, and a content-addressed inventory of only the declared
operation inputs and source-derived project-context contributors. Git branch,
commit, or status may be supplied as external evidence but cannot substitute
for file closure and is not obtained by invoking Git.

### 7.4 Effective-context inventory

Ordered config-layer records, per-key origin projection, disabled reasons,
instruction-selection trace, context/tool contributor inventory, explicit
session flags, non-secret environment projection, and all exclusions or
refusals. The descriptor says which bytes and rules would be considered by the
reviewed grammar; it does not instantiate, connect to, or execute contributors.

## 8. Bundle result states

Exactly one terminal state is emitted:

- `OBSERVED_NOT_QUALIFIED` - finite grammar closed and every required record is
  stable and content-addressed;
- `INCOMPLETE_CONTEXT_CLOSURE` - required, dynamic, unknown, inaccessible, or
  out-of-policy context evidence exists;
- `INCOMPLETE_SECRET_DEPENDENCY` - required behavior depends on excluded secret
  material;
- `UNSTABLE_RETRY_REQUIRED` - observed identity or metadata changed;
- `LIMIT_EXCEEDED` - any count, byte, depth, retry, or duration limit fired;
- `REJECTED_REQUEST` - schema, path, hash, time, or identifier validation
  failed; or
- `OBSERVER_ERROR` - an internal failure occurred without a usable descriptor.

Only `OBSERVED_NOT_QUALIFIED` contains usable descriptor families. All other
states contain bounded failure receipts and no partial-success descriptor.
Every state binds `dispatch=NOT_ATTEMPTED` and `authority=NOT_GRANTED`.

## 9. Pure verification

`verify_host_observation_v1(...)` receives exact built-in data values and:

1. validates closed schemas and canonical serialization;
2. recomputes every record, descriptor, directory, request, policy, grammar,
   and bundle hash;
3. verifies identifier and time bindings without reading a clock;
4. verifies closure against the supplied grammar and request;
5. rejects missing, duplicate, extra, reordered, cross-root, or inconsistent
   entries;
6. verifies that no sensitive value or forbidden descriptor class is present;
7. verifies every negative state has zero usable descriptors; and
8. returns a verification receipt capped at
   `STRUCTURE_CONTENT_AND_BINDINGS_ONLY`.

The verifier does not resolve paths, read files, access environment variables,
call a process, evaluate configuration code, verify signatures, or decide
runtime admissibility.

## 10. Required falsification fixtures

Implementation may begin only after review accepts fixtures for at least:

1. project config present while a caller claims it was ignored;
2. `AGENTS.override.md` versus `AGENTS.md` precedence;
3. configured instruction fallback and byte-budget truncation;
4. symlinked instruction file;
5. hard-linked config file;
6. file replacement between pre/post metadata;
7. directory child inserted during enumeration;
8. secret-bearing environment value or auth file requested;
9. MCP/plugin/skill/app contributor omitted;
10. dynamic or unknown contributor class;
11. mismatched executable and CLI-capture binding;
12. duplicate/colliding normalized paths;
13. entry, byte, depth, duration, and retry exhaustion;
14. partial descriptor on a negative state;
15. stale injected time and cross-record operation mismatch; and
16. pure verification while filesystem, clock, environment, subprocess,
    network, and import APIs are patched to raise.

## 11. Admission boundary

A later runtime-profile gate may consider a verified observation only if it
also proves an accepted signer/provenance policy, freshness at decision time,
runtime and provider/account authority, race-safe output reservation, and
controller admission. None of those claims can be inherited from this bundle.

No worker becomes eligible and no prepared operation changes state as a result
of this contract or a future observation alone.

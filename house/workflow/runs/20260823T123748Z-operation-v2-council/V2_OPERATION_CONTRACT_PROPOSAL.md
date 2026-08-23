# Dream House operation-preparation contract v2 — proposal

Status: `PROPOSED / NO IMPLEMENTATION / NO DISPATCH`

## Problem

The v1 operation builder is fail-closed after preparation, but it chooses an
explicit Codex model only when the task card says `specific_model`. That makes
task-routing metadata determine execution argv. The latest local inventory also
shows the current prepared operation lacks user/project isolation flags and
cannot be truthfully bound to a real-runtime profile.

## Proposed boundary

Keep five objects separate and hash-bound:

1. **Task card** — human intent, content, acceptance, and an advisory recipient
   class or recipient preference. It never grants execution authority.
2. **Route selection** — a no-dispatch record produced by a named deterministic
   router or explicit human selection. It selects one model/provider/account
   fingerprint/usage-pool tuple for this task-card hash and records its own
   evidence and expiry. It grants no lease or provider call.
3. **Operation** — a pure immutable record that consumes the task card and one
   verified route selection, then seals exact argv, executable, workspace,
   bounded outputs, isolation policy, and resource budget. Preparation creates
   no directories, controller rows, credentials, or process.
4. **Runtime profile** — independently observed executable, effective config,
   account/pool/egress, filesystem, runtime roots, and output-reservation
   evidence. It must agree exactly with the operation and route selection. Its
   verifier grants no dispatch authority.
5. **Execution authority** — a later single-use, operator-authenticated nonce
   bound to operation hash, runtime-profile hash, lease epoch, deadline, and
   external-effect class. Only a separately reviewed controller transaction may
   consume it and record one non-reacquirable intent.

No object may inherit or mint the authority of the next object.

## Proposed route-selection record

```json
{
  "schema": "codex-house-qualified-route-selection/1",
  "selection_id": "stable safe id",
  "task_card_sha256": "sha256",
  "model_identity": "explicit model slug",
  "provider_identity": "explicit provider id",
  "account_fingerprint": "domain-separated sha256",
  "usage_pool_id": "backend metered limit id",
  "selection_source": "human-manual or deterministic-router/version",
  "selection_evidence_sha256": "sha256",
  "observed_at": "RFC3339 UTC",
  "expires_at": "RFC3339 UTC",
  "dispatch": "NOT_ATTEMPTED",
  "authority": "NOT_GRANTED",
  "record_sha256": "canonical sha256 without this field"
}
```

The record must reject unknown/default/fallback/auto/wildcard identities. A
human may explicitly select a model, but that selection still is not a provider
call authorization.

## Proposed operation v2 API

```text
prepare_operation_v2(
  task_card,
  verified_route_selection,
  operation_id,
  workspace,
  output_root,
  codex_path,
  isolation_policy,
  wall_seconds,
) -> immutable record
```

The builder verifies both input records and binds their hashes. It does not
read ambient config, auth, rate limits, or task-card recipient fields to choose
the model.

## Candidate argv policy

The exact argv is sealed and contains, at minimum:

```text
codex exec
  -C <workspace>
  --model <route-selection.model_identity>
  --sandbox read-only
  --json
  --output-last-message <reserved-output-path>
  --ignore-user-config
  --ignore-rules
  -c features.hooks=false
  -c features.apps=false
  <prompt>
```

This list is a candidate, not an accepted allowlist. Source inspection shows:

- `--ignore-user-config` leaves authentication in `CODEX_HOME` but does not
  skip project configuration;
- `--ignore-rules` skips user and project exec-policy files;
- hooks and Apps are enabled by default;
- the internal config loader already has `ignore_project_config`, but `codex
  exec` exposes no corresponding CLI flag;
- CLI overrides are higher precedence than project config but managed config
  and requirements can remain above or constrain the effective result.

Therefore v2 must choose one reviewed strategy:

- **A — upstream-friendly flag:** expose `--ignore-project-config` for `codex
  exec`, keeping managed requirements and packaged defaults, then capture the
  final effective configuration; or
- **B — hashed project inputs:** allow project config/instructions only when
  every discovered layer and instruction file is inside declared read scope,
  content-addressed, and explicitly admitted by the runtime profile.

For answer-only workers with no source-tree dependency, A is preferred. For
repository coding workers, B may be required. The operation must name the
strategy; there is no ambient fallback.

## Capability closure

A candidate real worker is refused unless the effective runtime capture proves:

- hooks disabled;
- Apps disabled unless the operation explicitly admits an App surface;
- no unlisted MCP server, plugin MCP server, marketplace, skill, instruction
  file, or shell policy entered the context or tool catalog;
- model, provider, account fingerprint, usage pool, egress, service tier, and
  sandbox agree with the sealed records;
- read/write roots and actual trace agree with the runtime profile;
- stdout, stderr, and last-message outputs have race-safe reservations and hard
  byte ceilings;
- the isolated `HOME`, `CODEX_HOME`, state, and temp roots are distinct and
  content-inventoried.

Managed requirements may narrow the operation but may not broaden its declared
capabilities. If required managed configuration adds a capability outside the
operation allowlist, admission stops; it is not silently stripped or accepted.

## Credential projection

The repository never stores or hashes raw tokens. A later credential capsule
mechanism may project only the minimum authentication material into an isolated
`CODEX_HOME` immediately before launch, with mode/ownership checks, a source
account fingerprint, bounded lifetime, and cleanup/reconciliation receipt.

The v2 builder does not create this capsule. The runtime profile may bind a
credential-capsule descriptor and account fingerprint, never token bytes or a
repository path containing durable credentials. Design and testing of the
capsule is a separate gate.

## Logs and provenance

Do not use `--ephemeral` by default. Dream House requires complete worker-event
conservation. Native session output, stdout JSONL, stderr, final message, and
relay/controller receipts must be reconciled and bound without importing
credential material. A later retention policy may project a redacted knowledge
view, but must not delete the authoritative event log.

## Contradiction and stop rules

- Task-card recipient conflicts with route selection: record the mismatch;
  task-card field remains advisory and cannot override the route record.
- Route selection conflicts with operation argv: refuse preparation or
  verification.
- Operation conflicts with runtime profile or effective runtime capture: refuse
  admission.
- Account/pool/egress changes after selection or qualification: expire and
  requalify; never substitute.
- Output reservation already exists, source/config hash drifts, an unlisted
  capability appears, or a credential descriptor is absent: stop before lease
  or intent.
- Authority nonce is absent, expired, reused, or bound to another hash/epoch:
  stop; no reacquisition or fallback.
- Worker/model prose can report completion but cannot change operation state or
  admit results.

## Recovery

Preparation is pure and repeatable for identical inputs. A later controller
uses an idempotency binding over intent, task-card hash, route hash, operation
hash, runtime-profile hash, authority hash, target, and scope. After interruption
it reconciles the existing intent and lease; it never starts a replacement
operation under the same key.

## Falsification tests before implementation acceptance

1. Mutating any model/provider/account/pool field breaks every downstream
   binding without touching controller state.
2. Task-card recipient changes do not alter argv when route selection is fixed,
   but do change the task-card hash and therefore require a new selection.
3. A project `.codex/config.toml`, `AGENTS.md`, hook, App, MCP, plugin, or skill
   fixture cannot enter an A-strategy runtime; every admitted B-strategy input
   appears in the content inventory.
4. A managed layer that narrows permissions passes; one that adds an unlisted
   capability refuses.
5. A copied or stale account fingerprint, usage-pool snapshot, output
   reservation, or qualification bundle refuses.
6. No preparation or profile-verification test creates a directory, copies a
   credential, writes the controller database, contacts a provider, or starts a
   subprocess.

## Requested council decision

Return `ACCEPT_DESIGN`, `REVISE_DESIGN`, or `REJECT_DESIGN`. Identify any
authority conflation, capability leak, unrecoverable state, or unverifiable
claim. If revision is needed, name the smallest corrected contract and the
single first implementation slice that remains pure and no-dispatch.

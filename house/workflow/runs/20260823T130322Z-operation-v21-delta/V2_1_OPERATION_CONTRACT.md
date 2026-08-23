# Dream House operation-preparation contract v2.1

Status: `PROPOSED / STRUCTURAL ONLY / NO IMPLEMENTATION / NO DISPATCH`

## Claim ceiling

V2.1 specifies pure structural records and verifiers for future implementation.
It does not authenticate an author, observe a host, reserve output, create a
runtime profile, grant authority, acquire a lease, write a controller, start a
process, contact a provider, or admit a result.

## Object chain and invariant

Five immutable records remain separate:

```text
Task card v2
  -> route selection (structure-bound, no dispatch)
  -> operation v2 (assembled, no dispatch)
  -> independently observed runtime profile
  -> single-use execution authority
```

The arrow means “may be hash-bound as an input,” never “inherits authority.”
The cross-record invariant is exact agreement:

```text
typed task constraint
  == recorded routing disposition and selection
  == sealed operation argv and capability policy
  == observed runtime identity and capabilities
```

Any mismatch invalidates the downstream record. There is no precedence,
override, repair-in-place, fallback, or human waiver.

## Task card v2 routing fields

The task card separates intent from routing:

```json
{
  "routing_advice": {
    "class_hint": "triage | coder | reviewer | null",
    "model_preference": "explicit model slug | null"
  },
  "execution_constraints": {
    "required_model": "explicit model slug | null",
    "allowed_models": ["explicit model slug"],
    "allowed_providers": ["explicit provider id"],
    "required_usage_pool": "explicit pool id | null"
  }
}
```

- `routing_advice` is non-authoritative and may be declined with a reason.
- `execution_constraints` restrict selection but never authorize a provider
  call. A non-null `required_model` must be the selected model and a member of
  `allowed_models`. Empty allowlists are invalid rather than “allow all.”
- Legacy `requested_recipient` and `requested_recipient_id` values are not
  guessed into this schema. Migration must receive an explicit mapping or fail.

## Route-selection record

First-slice schema:

```json
{
  "schema": "codex-house-route-selection/1",
  "selection_id": "stable safe id",
  "task_card_sha256": "sha256",
  "model_identity": "explicit model slug",
  "provider_identity": "explicit provider id",
  "account_fingerprint": "domain-separated sha256",
  "usage_pool_id": "backend metered limit id",
  "routing_disposition": {
    "class_hint": "HONORED | OVERRIDDEN_WITH_REASON | NOT_APPLICABLE",
    "model_preference": "HONORED | OVERRIDDEN_WITH_REASON | NOT_APPLICABLE",
    "reason": "bounded text or null"
  },
  "observation": {
    "observed_at": "RFC3339 UTC",
    "not_after": "RFC3339 UTC",
    "freshness_policy": "versioned policy id",
    "evidence_bundle_sha256": "sha256"
  },
  "provenance": {
    "author_id": "explicit safe id",
    "authoring_method": "human-manual | deterministic-router/version",
    "signature_state": "NOT_VERIFIED_IN_FIRST_SLICE"
  },
  "state": "STRUCTURE_BOUND_NO_DISPATCH",
  "dispatch": "NOT_ATTEMPTED",
  "authority": "NOT_GRANTED",
  "record_sha256": "canonical sha256 without this field"
}
```

Structural verification requires:

- exact fields and canonical record hash;
- task-card hash match;
- selected model/provider/pool satisfying every hard task constraint;
- explicit disposition for every advisory value;
- a non-empty reason when advice is overridden;
- `observed_at < not_after` under the named freshness policy;
- safe explicit identities and rejection of unknown/default/auto/fallback/
  inherited/wildcard tokens;
- the fixed no-dispatch/no-authority states above.

The verifier returns only `ROUTE_SELECTION_VERIFIED_NO_DISPATCH` with claim
ceiling `STRUCTURE_AND_BINDINGS_ONLY`. The phrase “qualified route” is reserved
until a later signer/trust-policy verifier exists.

## Zero-host-I/O input descriptors

`assemble_operation_v2` receives mappings already produced by separate
observers. It may perform schema checks, lexical string checks, and canonical
in-memory record serialization/hashing only. It may not open, resolve, stat,
hash, create, reserve, or enumerate a path. Required descriptors include:

- verified task-card v2 and route-selection records;
- executable descriptor: absolute lexical path, content SHA-256, version,
  CLI-contract SHA-256;
- workspace descriptor: absolute lexical path, identity SHA-256, project-input
  policy and inventory SHA-256;
- output intent descriptor: absolute lexical final-message path, reservation
  policy ID, byte ceilings, state `UNRESERVED_INTENT`;
- prompt descriptor: exact text and SHA-256;
- isolation/capability policy: exact flags and allowed context/tool surfaces;
- resource and reconciliation policy.

Lexical path validation is allowed; filesystem canonicalization is not. A
later observer must prove canonical paths and detect symlink/alias changes.

The assembler returns a sealed record with state
`ASSEMBLED_NO_OBSERVATION_NO_DISPATCH`. A runtime-profile verifier later binds
observed canonical reality. Assembly success is not operation readiness.

## Isolation and project-input policy

Exactly one enum is sealed:

### `PROJECT_CONFIG_IGNORED`

- Requires CLI-contract evidence for an implemented project-config-ignore
  surface; current installed `codex exec 0.147.0` does not satisfy this.
- User config and rules are ignored, hooks and Apps are disabled, and effective
  capability capture must show no project instruction/config/tool surface.
- Until the CLI surface exists and is source-tested, real profiles using this
  strategy refuse.

### `PROJECT_INPUTS_CONTENT_ADDRESSED`

- The workspace descriptor inventories every discovered project config layer,
  `AGENTS.md`/fallback instruction file, hook, rule, skill, plugin, marketplace,
  MCP definition, and other context/tool contributor.
- The operation capability allowlist explicitly admits or rejects each surface.
- Runtime capture must equal the inventory and allowlist. Missing or additional
  items refuse.

Managed requirements may narrow permissions. Any effective managed or cloud
layer that adds context, tools, egress, write roots, model/provider substitution,
or another capability not in the operation allowlist refuses. The system does
not silently strip mandatory policy or treat its presence as authority.

## Exact argv policy

The operation seals argv derived only from its verified descriptors. For the
current installed CLI, the minimum shared elements are:

```text
codex exec
  -C <workspace>
  --model <route model>
  --sandbox <sealed sandbox>
  --json
  --output-last-message <output intent path>
  --ignore-user-config
  --ignore-rules
  -c features.hooks=false
  -c features.apps=false
  <prompt>
```

Additional capability-closing overrides are contract-versioned rather than
assumed. `PROJECT_CONFIG_IGNORED` additionally requires a CLI flag not present
in installed `0.147.0`; the assembler must reject a descriptor claiming support
when its CLI-contract evidence does not list that flag.

## Agreement checks

Verification refuses when any of these differ:

- task hash, selected model/provider/account fingerprint/usage pool;
- route validity interval or freshness-policy evidence;
- operation argv versus route selection and isolation policy;
- executable/path/version/CLI contract versus runtime observation;
- workspace/project-input policy versus observed context contributors;
- output intent versus race-safe reservation evidence;
- capability allowlist versus effective tools, hooks, Apps, MCP, plugins,
  skills, instructions, sandbox, egress, read roots, or write roots.

A human resolves a mismatch only by creating a new upstream record and all
new downstream bindings. No record is edited or waived.

## Provenance and future signatures

The first slice records author identity and method as attributed metadata and
labels signature state unverified. It never claims that a hash proves the
author. A future signer-admission contract must define key issuer, key ID,
algorithm, signed byte envelope, revocation/freshness, multi-author changes,
and verification receipt. Adding that contract is a separate reviewed gate.

Previous legitimately verified signatures remain valid unless a separately
authorized incident process revokes or supersedes them; ordinary later model
quality changes do not rewrite historical authorship.

## Credentials, runtime, and logs

Credential projection, runtime-root creation, effective-config observation,
output reservation, filesystem tracing, launcher/controller transactions, and
result admission remain outside the first slice. No token bytes or auth-file
hashes enter these records.

Full worker event conservation remains required for a later launcher. V2.1
does not use `--ephemeral` as a shortcut and does not define retention as
deletion.

## Recovery and revocation

- Pure assembly is deterministic for identical input bytes.
- Any new task, route, descriptor, policy, or freshness fact creates new hashes
  and requires a new downstream record.
- Expired route selections are unusable; they are not refreshed in place.
- A later controller reconciles the one existing intent/lease under its exact
  idempotency binding; it never substitutes another operation.
- Structural verification cannot revoke keys, consume authority, or change
  controller state.

## First implementation slice

Implement only:

1. pure task-card-v2 structural verification;
2. pure route-selection assembly/verification and no-dispatch receipt;
3. pure `assemble_operation_v2` and structural verifier over caller-supplied
   descriptors; and
4. deterministic mutation fixtures proving bindings and zero host I/O.

No compatibility migration, host observer, output reservation, CLI patch,
profile generator, signature verifier, credential capsule, controller write,
launcher, or worker-result path enters this slice.

## Falsification matrix

1. Change an advisory hint with task bytes frozen: task hash check fails; no
   stale route can be reused.
2. Supply a conflicting hard model/provider/pool constraint: route verification
   fails before operation assembly.
3. Override advice without a reason: route verification fails.
4. Change route model or evidence expiry after assembly: operation binding
   fails.
5. Monkeypatch file/path/process/network APIs to raise and assemble fixture
   records: assembly still succeeds, proving zero host I/O.
6. Claim `PROJECT_CONFIG_IGNORED` against a CLI contract lacking the flag:
   assembly fails.
7. Add or omit one content-addressed project contributor: profile agreement
   fails.
8. Change an output intent to claim a reservation: structural assembly rejects
   the state; only later observed evidence may prove reservation.
9. Supply a valid hash with unverified authorship: structural receipt succeeds
   only at `STRUCTURE_AND_BINDINGS_ONLY`; authenticated or executable admission
   remains impossible.
10. Run every first-slice test while snapshotting controller DB, workspace, and
    output roots: all remain byte/entry identical and no network or subprocess
    occurs.

## Requested replacement-review decision

Return `ACCEPT_V2_1`, `REVISE_V2_1`, or `BLOCKED`. Search specifically for:

- a fact that still changes through precedence rather than agreement;
- an ambient read, write, time, randomness, process, or network dependency
  hidden inside the first slice;
- a hash or attributed author field overstated as authentication;
- a route or human action that launders dispatch authority;
- a project/config capability that can enter without inventory; or
- an interruption path that can reuse stale selection or operation state.

If revision is necessary, name one concrete invariant and its smallest repair.

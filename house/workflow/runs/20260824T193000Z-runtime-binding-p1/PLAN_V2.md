# Plan delta v2: closed P1 schema and legacy account adapter

## Account compatibility decision

P1 consumes route-v1 unchanged. Its sole account edge is
`route_account_fingerprint`, a 64-character opaque digest that must equal
`route["account_fingerprint"]`. P1 does not accept
`account_fingerprint_sha256`, `account_fingerprint_policy_id`, or a raw account
field. Policy-qualified account representation is deferred to a future
versioned route/operation migration; P1 makes no policy claim.

## Exact observation schemas

Both states have exactly these common fields:

`schema`, `state`, `task_card_sha256`, `route_selection_sha256`,
`operation_sha256`, `model_identity`, `provider_identity`,
`route_account_fingerprint`, `usage_pool_id`, `argv_sha256`,
`descriptors_sha256`, `workspace`, `output`, `isolation`, `config_hooks`,
`runtime_roots`, `filesystem`, `evidence_bundle_sha256`.

- `schema` is `codex-house-runtime-evidence-observation/1`.
- all named digests are lowercase SHA-256; identities reject implicit/default/
  fallback/inherited/wildcard values.
- `workspace` is exactly `{path, identity_sha256}` and equals the supplied
  operation descriptor workspace.
- `output` is exactly `{path, max_bytes}` and equals its output-intent
  descriptor.
- `isolation` is exactly `{sandbox, allowed_context_surfaces,
  allowed_tool_surfaces, managed_policy}` and equals its isolation descriptor.
- `config_hooks` is exactly `{state, hook_state, evidence_sha256}` with
  `CONTENT_HASHED` / `DISABLED_BY_POLICY`.
- `runtime_roots` is exactly `{home, codex_home, state, temp, evidence_sha256}`;
  all four are distinct absolute lexical paths.
- `filesystem` is exactly `{state, read_roots, write_roots, policy_sha256,
  trace_sha256}` with state `MEASURED`, unique absolute lexical roots, and the
  workspace path among reads. No element is treated as a host observation.

`UNATTESTED_STRUCTURE_ONLY` has no further fields.

`ATTESTED_CLAIMED` has exactly the common fields plus:
`attestation_subject_id`, `attestation_issuer_id`, `self_issue_disposition`,
`trust_policy_id`, `trust_policy_version`, `trust_policy_sha256`,
`observer_key_id`, `observer_key_policy_sha256`,
`reference_time_decision_sha256`, `valid_from`, `valid_until`,
`attestation_content_sha256`, and `self_issue_decision_sha256`.
All policy/key fields are non-implicit identities or digests; timestamps are
RFC3339 UTC with `valid_from <= valid_until`. Attestation-content is the
canonical JSON projection of every field in this state except its two digest
fields. The self-issue decision projection is subject, issuer, disposition,
and attestation-content digest.

## Exact equality map and receipt

P1 invokes the existing v2 verifiers first. It requires common hashes to equal
their verifier receipts; model/provider/route fingerprint/pool equal route-v1;
`argv_sha256` equal canonical operation argv; and descriptors/workspace/output/
isolation equal canonical supplied descriptors. The remaining descriptor
objects are schema-validated and content-bound into the observation only.

The receipt has exactly `schema`, `state`, `claim_ceiling`, `dispatch`,
`authority`, `task_card_sha256`, `route_selection_sha256`, `operation_sha256`,
`observation_sha256`, and `receipt_sha256`. It never echoes observation paths,
issuer, timestamps, policy, roots, filesystem, or runtime claims.

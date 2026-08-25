# Local rubric candidate intake

Status: `STRUCTURAL_INTAKE_COMPLETE / NO_MODEL_EXECUTION / NO_PROMOTION`

## Scope

Three local MLX Safetensors bundles were inspected with the Model Asset
Classifier's deterministic container probe.  The probe read bounded metadata,
Safetensors headers, and shard indexes only; it did not deserialize weights,
load a runtime, or call a provider.

The evaluator must refer to these as opaque candidates.  Human-readable paths
are retained below only for local provenance and are not a scoring feature.

| Opaque ID | Receipt | Observed layout | Observed size | Structural result |
| --- | --- | --- | ---: | --- |
| `local-rubric-candidate-a` | `asset-a.json` | MLX Safetensors, 3 shards | 14,487,033,249 B | complete; indexed shards match |
| `local-rubric-candidate-b` | `asset-b.json` | MLX Safetensors, 3 shards, 4-bit affine metadata | 15,136,819,784 B | complete; indexed shards match |
| `local-rubric-candidate-c` | `asset-c.json` | MLX Safetensors, 2 shards, 4-bit affine metadata | 5,977,074,591 B | complete; indexed shards match |

## Evidence boundaries

- All three receipts report `weight_payloads_loaded: false`.
- No Safetensors header layout defect, missing shard, or unindexed tensor was
  observed.
- The classifier's learned label was deliberately not run; structural evidence
  is the only intake result used here.
- The receipts report no canonical parent identity or generation.  Their
  bounded file fingerprints are candidate-only samples, not exact artifact
  identity.

## Disposition

All three candidates remain `TEST_ONLY_UNAPPROVED`.  This intake does **not**
qualify a worker route, a training parent, an adapter, or a TERM experiment
variant.

Before one can run the shared rubric corpus, a separately sealed binding must
contain: opaque candidate ID, full artifact fingerprint, exact runtime and
adapter fingerprint, frozen decoding settings, output reservation, and an
explicit inference-only authorization.  The shared test corpus and the
candidate binding must remain separate so the name of an asset cannot affect
evaluation scoring.

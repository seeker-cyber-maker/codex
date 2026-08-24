# Plan delta v3: complete descriptor and evidence-bundle edges

This delta supersedes the equality map in `PLAN_V2.md`.

- `descriptors_sha256` is SHA-256 of canonical JSON for the complete separately
  supplied `descriptors` mapping. P1 recomputes it only after
  `verify_operation_v2` accepts that mapping and requires equality.
- `evidence_bundle_sha256` must exactly equal
  `route["observation"]["evidence_bundle_sha256"]`; it is not observation-local
  evidence.

Together with the existing task/route/operation, model/provider/fingerprint/
pool, argv, workspace/output/isolation edges, these make every receipt field
that implies a cross-binding deterministic. The structural claim ceiling is
unchanged.

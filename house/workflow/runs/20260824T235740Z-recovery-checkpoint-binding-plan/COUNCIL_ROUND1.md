# Council round 1 disposition

Frozen packet SHA-256:
`d31ce8ec145ed1edeb140418c764a1e5b6acdd146cbccd055224b0e8e9a79a0e`

## Verdicts

- Evidence auditor: `ACCEPT_PLAN_ONLY`.
- Constructive theorist: `REVISE`.
- Adversarial methodologist: `REVISE`.

All three reviewers reproduced the frozen packet hash. No reviewer reported an
operational action or granted source, runtime, key, storage, or recovery
authority.

## Root disposition

`BOUNDED_PLAN_DELTA_REQUIRED`

The original `PLAN.md` remains frozen. `PLAN_V2.md` supersedes it for the plan
decision and makes only these corrections:

1. It supplies an explicit field-by-field binding matrix and makes the expected
   descriptor carry every semantic checkpoint field needed for an exact
   three-object comparison.
2. It defines `assertion_sha256` as SHA-256 over canonical JSON bytes of the
   complete signed envelope.
3. It gives `checkpoint_sequence` the explicit range `1..2^63-1`.
4. It requires an immutable, independently authored positive fixture and
   expected whole receipt, and forbids the candidate verifier from generating
   its own positive oracle.

These are plan-precision corrections only. They do not authorize source edits
or any operational action.

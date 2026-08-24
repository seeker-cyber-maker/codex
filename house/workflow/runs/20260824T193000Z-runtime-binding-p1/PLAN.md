# P1 sealed implementation plan: untrusted runtime-evidence binding

Objective: add `house/worker_exec/runtime_binding.py` and focused tests that
purely bind an existing task-card v2, route v1, operation v2, and caller-supplied
runtime observation descriptor.

Allowed writes: `house/worker_exec/runtime_binding.py`, its focused test,
`house/worker_exec/__init__.py`, `house/README.md`, and this run directory.

Forbidden: filesystem reads other than Python source import; clock, process,
network, credential, controller, database, provider, launch, operation writes,
and all candidate/secret actions.

Interface:

`verify_runtime_evidence_bindings(task_card, route, descriptors, operation,
observation) -> receipt`

It first calls the existing v2 verifiers. It requires an exact observation
schema that binds route/task/operation hashes, model/provider/account
fingerprint/usage pool, reconstructed argv hash, descriptor hashes, isolated
roots, config/hook, filesystem, and evidence-bundle digests.

Observation states:

- `UNATTESTED_STRUCTURE_ONLY`: no trust/freshness assertion; accepts only with
  the untrusted claim ceiling.
- `ATTESTED_CLAIMED`: validates the P1-v5 subject/issuer/content/self-issue and
  supplied policy/key/reference-time bindings, but does not determine whether
  the attestation is true or currently fresh.

All successful receipts are
`RUNTIME_EVIDENCE_BINDINGS_VERIFIED_NO_DISPATCH`,
`UNTRUSTED_INPUT_STRUCTURE_AND_CROSS_BINDINGS_ONLY`, and `NOT_GRANTED`.

Acceptance matrix: deterministic happy paths for both states; mutation refusal
for every route/operation/argv/model/provider/account/pool/descriptor/roots/
config/filesystem/evidence mismatch; malformed or implicit identities; invalid
attestation digest or interval; and monkey-patched ambient file/clock/process/
network/credential/controller APIs. No operation record may be created.

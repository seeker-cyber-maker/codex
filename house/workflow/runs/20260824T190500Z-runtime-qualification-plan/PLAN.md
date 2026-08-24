# Sealed plan: no-dispatch runtime qualification v2

## Verified starting facts

- The prior entrypoint rung is sealed at commit `52e1c47345`; it proves only
  hash-bound pure admission code and disposable test evidence.
- `mcu-infinity-war-001` is still `PREPARED` with no lease or launch intent.
  Its v1 record has no explicit model, has unresolved provider egress, and has
  no isolation or qualification evidence. It must remain ineligible.
- `runtime_profile.py` can only verify a complete caller-supplied profile. It
  creates neither profile nor authority and has no dispatch path.
- `operation_v2.py` already gives a pure structural chain separating routing
  advice, hard execution constraints, route evidence, and operation assembly.

## Decision

Do not repair or mutate the legacy MCU record. Do not derive execution model
selection from its task-card routing label.

The next implementation candidate, if this plan is accepted, is a pure
**v2-to-runtime-profile binding verifier**. Its input is four already sealed,
externally produced records: task card v2, route selection v1, operation v2,
and an independent runtime-observation bundle. It must reject absent, stale,
implicit, default, fallback, or mismatched model/provider/account/usage-pool,
argv, isolated roots, output reservation, config/hook, filesystem, and evidence
bindings. It must not read the host, discover credentials, create files outside
a test temporary directory, write the controller, or dispatch.

## Required independent inputs before any future operation record

1. Explicit execution model selected by the planner and bounded by task hard
   constraints. The initial controlled candidate is `gpt-5.6-terra`; the
   selection remains unqualified until a separate route record binds it.
2. Provider identity, non-secret account fingerprint, and usage-pool ID from an
   independent local observation. Raw account identifiers and tokens are never
   copied into source, workflow, or repository records.
3. Captured CLI contract/version, exact intended argv, and content-addressed
   configuration/hook policy.
4. Isolated runtime-root and output-reservation evidence produced by a separate
   observer. A self-hash alone is insufficient.
5. Measured filesystem boundary and evidence-bundle hash from that observer.

## DAG and stop rules

| Node | Scope | Acceptance | Failure edge |
|---|---|---|---|
| P1 | pure binding-verifier design | exact input schema and mismatch matrix | plan delta |
| P2 | source-only implementation | deterministic unit tests, no ambient I/O | stop and inspect |
| P3 | source-only promotion | independent review accepts claim ceiling | seal or remain candidate |
| R1 | separate future observer plan | independent evidence for all five inputs | blocked if any unavailable |

P1 is the only possible next implementation node. P2 cannot begin until P1 is
independently accepted. R1 is not authorized by this run.

## Claim ceiling

No-dispatch source and evidence binding only. This plan does not admit a runner,
validate an actual provider session, prove sandbox behavior, or authorize
candidate build, signing, launch, provider use, or authority consumption.

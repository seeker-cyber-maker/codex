# Operation v2.1 structural first slice — plan v1

## Recovery and routing

- Existing repository, clean at `0603ec7c03`.
- Recovery disposition: resume from the accepted v2.1 handoff.
- Case type: `semantic_implementation` with a security-sensitive boundary.
- Advisory: Terra / high for implementation; reassess after the ten
  falsification tests or two substantive failures.
- One planner and one implementation lane; no workers or outside operations.

## Objective

Implement the accepted structural slice as a new module beside v1:

1. exact task-card-v2 verification;
2. pure route-selection assembly and verification;
3. pure operation-v2 assembly and verification over caller-supplied
   descriptors; and
4. deterministic fixtures covering every accepted falsification case.

## Non-goals and authority

No legacy migration, host observation, path resolution, output reservation,
CLI modification, signature verification, credential access, runtime profile,
controller mutation, process launch, network call, provider dispatch, result
admission, or public claim.

The implementation may modify only `house/worker_exec/operation_v2.py`, its
dedicated test file, package exports, and this run directory.

## Acceptance

- Exact schemas and canonical hashes fail closed.
- Advisory routing and hard constraints remain distinct.
- Route and operation receipts have structural/no-dispatch claim ceilings.
- Assembly succeeds while host-I/O, time, randomness, process, and network APIs
  are patched to raise.
- All ten v2.1 falsification cases pass.
- Focused worker-exec tests and the complete Dream House Python suite pass.
- Controller SHA-256 remains
  `977ce2be9ff3701f53afce5c02f1c772cf2fd06aa2d5adadfc13c62b8be6dd37`;
  MCU operation remains `PREPARED` with no observation, lease, or intent.
- Source is sealed, committed, and mirrored to the private backup.

## Stop conditions

Stop on any hidden host I/O, need to modify v1/live controller code, inability
to express project-input closure without authority laundering, controller
drift, or two substantive remediation failures.

# Authority ceremony design plan

## Objective

Produce a reviewable, implementation-independent ceremony specification for
future real-key authority. Define trust roles, non-delegable ceilings,
bootstrap/enrollment/rotation/revocation/recovery states, two-YubiKey selection
without dual-key polling, durable task-intent reconciliation, journal anchoring,
portable P-256 vectors, bounded monitoring, and preregistered failure tests.

## Non-goals

- No source implementation, migration, dependency, service, permission, UI, or
  database change.
- No private-key generation or persistence, real-key enrollment, YubiKey poll,
  PIV command, signing operation, device serial collection, or touch request.
- No provider, network, Archive, native Codex, worker, or task dispatch.
- No production, tamper-proof, hardware-compatible, or ceremony-safe claim.

## Authority and privacy

Local repository documentation only. Read the sealed candidate and council
evidence; write only this run directory plus documentation pointers in
`house/`. No external effects or delegation.

## Design invariants

- Models never receive raw private keys or direct database write access.
- A capability cannot grant or delegate more authority than it possesses;
  explicitly non-delegable rights never cross a child boundary.
- Two owner YubiKeys are independent alternatives, not simultaneous launch
  keys. Exactly one selected device and slot is polled per ceremony step;
  ambiguity fails closed.
- The last recovery-capable key cannot be silently revoked. Emergency lockdown
  halts writes and requires a separately authorized recovery ceremony.
- A proof authorizes one durable intent. Retrying delivery replays that exact
  intent idempotently rather than consuming unrelated new authority.
- Hash chains provide consistency. Authenticated external checkpoints and an
  OS sole-writer boundary are separately required for tamper-evidence claims.
- Every safety-layer failure is a near miss even when a later layer blocks the
  operation; monitoring preserves and surfaces it under bounded storage.
- Tombstones retain key/event identity and disposition without retaining
  redacted secrets or duplicating content.

## Task graph

1. Freeze threat actors, trusted computing base, assets, and claim ceiling.
2. Specify principals, key classes, delegation ceilings, and ceremony states.
3. Specify the authority/inbox saga, journal checkpoints, and startup recovery.
4. Specify portable canonicalization and fixed-vector requirements.
5. Specify recovery matrix, monitoring/quotas, and near-miss escalation.
6. Preregister deterministic failure tests and promotion gates.
7. Cross-check every council requirement, seal sources, and write handoff/AACR.

## Acceptance

- Every council requirement maps to at least one normative rule and one future
  falsification test.
- State transitions name actor, prerequisites, durable events, stop behavior,
  recovery, and prohibited shortcuts.
- Recovery matrix covers key loss/compromise, both-key loss, ambiguous devices,
  database corruption/truncation/rewrite, clock faults, disk full, concurrent
  writers, and authority/inbox crash boundaries.
- Signing-vector specification fixes canonical bytes, hashes, encodings, curve,
  signature policy, positive vectors, and negative vectors without generating a
  real key in this run.
- Monitoring is bounded without suppressing near-miss notification.
- All JSON/JSONL artifacts parse, internal references resolve, source hashes
  match, and the worktree closes cleanly in a dedicated commit.

## Claim ceiling

The result is an implementation proposal and future test contract. It does not
prove a secure ceremony, hardware interoperability, hostile-process isolation,
crash safety, or production readiness.

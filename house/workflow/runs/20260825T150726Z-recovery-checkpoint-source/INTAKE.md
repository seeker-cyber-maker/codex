# S1 intake: synthetic recovery checkpoint verifier

Status: `EVIDENCE_FROZEN__PLAN_SEALED__AWAITING_BLOCKING_COUNCIL_PLAN_CHECK`

## Objective

Implement one pure production verifier in
`house/task_spine/recovery_checkpoint.py`, plus its dedicated test file.  It
must verify only the exact structural and signature bindings defined in the
accepted V2 plan against caller-supplied objects and the accepted public F1
fixture.

## Authority and continuation

The user's continuation dot after the accepted F1 handoff is recorded as
authority for this single S1 source-only milestone.  It does not authorize
YubiKey, Keychain, certificate, signing, private-key, storage, clock,
database, process, network, provider, worker, runtime, or dispatch activity.

## Inherited evidence

- V2 source contract:
  `house/workflow/runs/20260824T235740Z-recovery-checkpoint-binding-plan/PLAN_V2.md`
- Accepted F1 handoff:
  `house/workflow/runs/20260825T015729Z-recovery-checkpoint-oracle/HANDOFF_FINAL.md`
- Accepted F1 final packet SHA-256:
  `5f2cc0cd1be8bcec2fa7b9548657994af70270f6d82b9e9b959b323015a032e0`
- Public positive fixture SHA-256:
  `0d52a694cf3e5c681c40faee2ff577fc8ac07c01222c59c6722c0a14ecedc25e`

## Preserved user work

The existing modified `house/README.md` and untracked
`house/LOCAL_ZOOKEEPER_CHAT_WORK_WRANGLER_SPEC.md` are outside this run and
must remain unmodified.

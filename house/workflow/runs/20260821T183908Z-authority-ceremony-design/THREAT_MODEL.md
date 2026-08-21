# Authority ceremony threat model

Normative words `MUST`, `MUST NOT`, `SHOULD`, and `MAY` describe a future
implementation. They are not claims about the current candidate.

## Boundary and assets

The proposed boundary protects:

- authority-key enrollment, status, permissions, and revocation history;
- the mapping between a verified signer and one durable task intent;
- journal sequence, authenticated checkpoints, and recovery generation;
- the sole-writer database capability and its local service interface;
- owner-visible near-miss, lockdown, and recovery evidence.

Task prose, retrieved documents, model output, summaries, contractor reports,
and dashboard labels are data. They MUST NOT become authority-bearing facts
without passing a typed authenticated interface.

## Trusted computing base

The minimum proposed trusted computing base is:

1. a small local authority service running under a dedicated OS identity;
2. its strict schema/canonicalization/signature verifier;
3. SQLite transaction and filesystem semantics actually exercised by tests;
4. the owner-selected P-256 signer for administrative operations;
5. protected journal-head checkpoints and their verifier;
6. the deterministic task-intent reconciler;
7. the local operating system controls that deny models and contractors direct
   database writes.

The Codex model, replacement models, router, dashboard, contractors, retrieved
content, and monitoring classifier are outside the trusted computing base.
They may propose, display, or request; they do not decide authorization.

## Principals and authority classes

| Principal | Intended authority | Explicitly prohibited |
|---|---|---|
| Human owner | Select an owner/recovery signer and authorize administrative ceremonies | Raw private-key export; implicit approval from presence alone |
| Owner-primary key | Enroll/rotate/suspend/revoke keys, enter or exit protected policy states, sign administrative checkpoints | Delegating owner-root authority; routine contractor work |
| Owner-recovery key | Recover or replace the primary key and exit an owner-authorized lockdown | Routine task signing; silent promotion to primary |
| Codex operator capability | Authorize bounded task intents and request status through the service | Key lifecycle, policy-root changes, unrestricted delegation, raw DB writes |
| Restricted local gatekeeper | Admit only predeclared low-risk action schemas under a shorter lifetime and narrower scope | Expanding its actions, changing policy, granting its own capability class |
| Authority service | Verify and execute already-authorized typed transitions | Inventing policy, interpreting prose as approval, holding owner private keys |
| Auditor/monitor | Read receipts, verify chains/checkpoints, surface near misses | Mutation, acknowledgement on behalf of owner, promotion |
| Contractor/model worker | Write only to a sealed worker buffer | Main authority DB, inbox DB, anchors, delegation, task chaining |

An execution capability is not policy authority. The service can write the
database because the OS permits it, but it may do so only after deterministic
policy and proof verification.

## Delegation ceiling

Every capability MUST bind:

- issuer and subject identity;
- allowed action subset and resource scope digest;
- issuance, expiry, generation, and revocation epoch;
- maximum child depth and maximum child lifetime;
- whether each action is delegable;
- parent capability digest and a unique service-issued challenge.

A child MUST be a strict subset of its parent in actions, resources, lifetime,
generation, and delegation depth. `owner.*`, key lifecycle, lockdown exit,
checkpoint-root signing, policy changes, and capability-class creation are
non-delegable. A replacement model cannot grant more rights than its own
capability, and a non-delegable right cannot be laundered through another role.

## Adversaries and failures

The design assumes attackers or faults may:

- inject instructions through prompts, documents, tools, summaries, or model
  context;
- obtain a contractor or restricted-model process;
- replay, reorder, alter, truncate, or duplicate requests and responses;
- race bootstrap, authorization, revocation, or reconciliation processes;
- compromise an operational capability or one owner key;
- present the wrong hardware key or more than one candidate device;
- modify, replace, truncate, roll back, or fill a database or backup;
- cause power loss or process termination at any transaction boundary;
- roll the wall clock backward or forward;
- flood invalid requests to exhaust telemetry storage or operator attention;
- return stale, malformed, hallucinated, or contradictory status.

## Security goals

The future system MUST:

1. fail closed before any authority-bearing mutation on invalid identity,
   signature, schema, scope, state, challenge, clock, generation, or journal;
2. make every committed task effect traceable to one durable authorized intent;
3. prevent one proof or intent from creating conflicting work;
4. keep key lifecycle and lockdown transitions independently recoverable;
5. detect history inconsistent with the latest protected checkpoint;
6. prevent models and contractors from bypassing the service through ordinary
   filesystem or database access;
7. treat any failed safety layer as a near miss even when a later layer blocks
   the effect;
8. preserve tombstones and recovery discontinuities without preserving secrets;
9. stop before storage, clock, anchor, or identity ambiguity becomes silent
   authority drift.

## Non-goals and residual risks

This design does not protect against a compromised kernel, malicious firmware,
physical coercion, cryptographic-library compromise, side channels, or loss of
both owner keys. If both owner keys are irrecoverably lost, cryptographic
continuity is impossible; the honest outcome is a new registry generation and
a retained read-only tombstone for the old generation.

Hash chaining alone is not tamper evidence against a coherent writer. OS
permissions alone are not cryptographic authenticity. Human approval alone is
not infallible. The design requires all three layers in bounded roles and
records which layer detected each failure.

## Claim ceiling

Until separately implemented and tested, this document supports only the claim
that the intended boundary and failure classes have been specified. It does not
claim they are enforced.

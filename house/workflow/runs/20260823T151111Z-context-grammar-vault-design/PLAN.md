# Context grammar and Codex vault design - sealed plan

## Classification

- Existing project recovery from commit `fbbf52145707bb50f7795ca2e8584b8785514199`.
- Case type: `semantic_implementation` (design-only phase).
- Privacy: `cloud-ok` only after the evidence packet excludes live configuration,
  paths outside this repository, credentials, and secret-bearing values.
- Model advisory: Sol / medium for this bounded semantic and authority design;
  reassess before implementation.

## Objective

Design a version-pinned producer that derives the finite context grammar needed
by `house.worker_exec.host_observer`, plus a semantic projection that cannot
silently export secret-bearing configuration. Extend the design to expose the
existing Codex secrets subsystem as a first-class vault through a separately
authorized broker.

## Non-goals

- No live configuration, keychain, environment, credential, or private project
  document reads.
- No vault CLI, UI, secret migration, secret creation, or secret resolution.
- No runtime qualification, controller transition, lease issuance, launch,
  dispatch, provider call, or result admission.
- No changes to `house/worker_exec/host_observer.py`.

## Authority

Project-coordinator authority covers read-only source inspection, design
artifacts, outside advisory review, reversible commits, and the already-approved
private backup remote. Secret access and runtime execution remain explicit
separate gates.

## Task graph

1. Pin source revision and source-file hashes.
2. Derive the staged context-loading and projection contract from repository
   source.
3. Define the vault broker boundary over the existing encrypted secrets store.
4. Freeze one evidence packet and obtain blind outside design review.
5. Root-synthesize findings, seal the design milestone, commit, and push only to
   the private `backup` remote.

## Acceptance

- The design handles loader precedence, project-root discovery, trust, project
  layers, instruction discovery, dynamic contributors, and cross-stage drift.
- Secret-bearing values and their hashes are absent from durable projections.
- Unknown structured keys and private arbitrary text fail closed.
- Vault storage, references, leases, sinks, audit, and revocation are distinct.
- The existing observer remains the only host-I/O boundary in this phase.
- Three attempted reviewers receive the same immutable packet, and every
  material finding receives a root disposition.

## Stop conditions

Stop at the reviewed design milestone. Implementation is a later bounded phase.
Any need to inspect live configuration, touch Keychain, or resolve a secret is a
hard blocker requiring a new authority gate.

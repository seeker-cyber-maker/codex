# Real firewall and vault threat-model plan

## Classification

- Existing-project recovery from commit
  `7fde7e524d2416973c8d19f430149a03be5fe0e9`.
- Recovery disposition: resume from the accepted synthetic-slice handoff.
- Case type: `security_containment`.
- Model advisory: Sol / high or above for this design and promotion review.
- Profile: full, because later implementation would widen access to raw local
  configuration and secret material.

## Objective

Produce a source-grounded, non-runtime threat model and authority contract for
the first real `LocalContextFirewallV1` and Codex vault broker integration.
Define component boundaries, namespace/key blast radius, qualified sinks,
lease/audit state transitions, incident behavior, and a disposable-test ladder.

## Non-goals and present authority

- No live Codex configuration, environment, Keychain, credentials, encrypted
  secret files, or user secret labels/values may be read.
- No Keychain prompt, secret creation/migration/rotation, resolver process,
  sink injection, controller mutation, network request, or launch may occur.
- Do not modify `codex-rs/secrets`, `codex-rs/keyring-store`, the synthetic
  modules, or the protected controller in this phase.
- This phase can accept a design candidate; it cannot authorize real secret
  access or runtime promotion.

## Work graph

1. Pin the current repository/source baseline and inspect only source code and
   prior sealed artifacts.
2. Record observed capabilities and gaps in the existing storage primitive.
3. Define the real trust boundaries, protocol, states, and failure semantics.
4. Define a mock/disposable implementation ladder with explicit user gates.
5. Freeze one cloud-safe evidence packet and obtain blind outside review.
6. Reconcile findings, seal the design disposition, commit, and push only to
   the private Dream House backup.

## Acceptance

- The design explicitly prevents model/agent code from calling a plaintext
  getter or choosing an arbitrary secret sink.
- Existing source limitations are represented honestly: shared namespace key,
  full-map decryption, plaintext-returning API, MCP plaintext cache, heuristic
  redaction, and hardening not automatically applied to a future broker.
- Every crash window is classified as either proven pre-delivery or possible
  exposure; possible exposure requires quarantine plus rotation.
- The first implementation step uses generated synthetic values and mock
  keyring/storage only. Any macOS Keychain probe is a separate user-present
  gate.
- A plan or council verdict cannot grant secret access.

## Stop condition

Stop after the reviewed and sealed threat model. Real implementation begins
only under a new scoped authority record.

# Context grammar synthetic first slice - sealed plan

## Classification

- Existing-project recovery, baseline commit
  `abfcc11e4ed9fbec7bb7d8302bb951f47ac208ce`.
- Case type: `semantic_implementation`.
- Recommended lane: Terra / high (advisory; current client selection unknown).
- Profile: full for design lineage and independent promotion review; execution
  itself is local, synthetic, reversible, and single-lane.

## Objective

Implement the first safe subset of the accepted context/vault design:

1. canonical sealed records and typed schema validation;
2. a pure context-grammar compiler and pure verifier;
3. a mock-only firewall projection interface; and
4. mock-only vault reference, lease, and incident records.

## Explicit non-goals

- No filesystem, live Codex configuration, environment, Keychain, credentials,
  vault storage, subprocesses, sockets, provider calls, controller mutation, or
  launcher integration.
- No parsing of real TOML/Markdown, no host-observer alteration, no secret
  resolution, no plaintext getter, and no injection into any process.
- No claim that a mock proves real firewall isolation, vault containment, or
  runtime qualification.

## Source and contract baseline

- Design run: `20260823T151111Z-context-grammar-vault-design`.
- Authoritative correction:
  `ROOT_DESIGN_DELTA.md` in that run.
- Existing observer stays unchanged; it is a later independent metadata/digest
  consumer, not a semantic source in this slice.

## Work graph

1. Implement focused pure `context_grammar` records/compiler/verifier.
2. Implement mock-only firewall projection and mock vault records in separate
   modules.
3. Add isolated known-answer and negative fixtures.
4. Run focused tests, full House tests, lint/format, compile, diff, and pure
   ambient-API audits.
5. Freeze an evidence packet, obtain outside review, synthesize, seal, commit,
   and push only to the private backup.

## Acceptance

- Every public record is canonically sealed and exact-schema validated.
- Compiler and verifier use no ambient I/O; the compiler cannot emit an
  execution-qualified state.
- Mock firewall never serializes rejected raw secret material or its digest.
- Vault lease records contain no value and reject agent-shell/unknown sinks.
- Mock incident records distinguish pre-injection non-exposure from
  post-injection termination plus rotation-required.
- Tests cover the seven accepted delta falsifiers in synthetic form.
- Existing controller database remains byte-identical and has no leases or
  launch intents.

## Stop conditions

Stop at this first-slice milestone. Any real configuration, Keychain, secret,
process injection, controller, or launch need is a new authority gate.

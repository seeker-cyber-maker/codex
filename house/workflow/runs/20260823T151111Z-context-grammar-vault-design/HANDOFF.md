# Context grammar and Codex vault design - handoff

## Milestone

Accepted `ACCEPT_DESIGN_V1_1_NON_RUNTIME`:

- `CONTEXT_GRAMMAR_AND_VAULT_CONTRACT.md` is the reviewed base;
- `ROOT_DESIGN_DELTA.md` is authoritative where the base conflicts;
- existing `codex-secrets` is the storage primitive;
- a new local firewall parses raw config, a pure compiler derives grammar, the
  existing observer re-observes admitted sources, and a pure verifier checks
  lineage/consistency;
- a separately authorized vault front end/resolver/sink path uses opaque refs
  and short-lived leases without a model-facing plaintext getter.

## Council receipts

- original transport:
  `f41847cff7d1ba45897ae42583d7a911f4690eafa5860caa5b9bb5fff6953e69`;
- corrective transport:
  `36d0742c83fce26019692d81ff77295aedad189de04effb90417e86cd265167a`;
- three attempted and completed provider/model lanes in each round;
- response-quality limitations and rejected reviewer claims are recorded in
  `SYNTHESIS.md` and `AACR.md`.

## Do not infer

- No code was implemented.
- No live config, Keychain, environment, credential, or secret was read.
- Digests establish consistency/identity, not observer authenticity or secrecy.
- At-rest encryption does not protect a namespace from its resolver.
- Revocation does not retract delivered plaintext.
- Agent-controlled shells are not approved secret sinks.

## Next acceptance check

Implement a synthetic-only first slice in new focused modules:

1. schemas and canonicalization;
2. pure grammar compiler;
3. pure verifier;
4. mock firewall and mock vault fixtures, including the seven delta falsifiers.

Do not integrate the real firewall, Keychain backend, controller, or launcher in
that slice.

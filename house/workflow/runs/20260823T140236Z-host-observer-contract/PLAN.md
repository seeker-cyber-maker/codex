# Host observer contract - design plan v1

## Recovery and routing

- Existing repository, clean at `689e6f224cc1fe2ab0f9059635a12f692f60d6f4`.
- Recovery disposition: resume from the operation-v2.1 first-slice handoff.
- Case type: security-sensitive architecture and evidence design.
- Advisory: Sol / high for the source-derived boundary and outside review;
  reassess for Terra / high only after the design is accepted.
- This phase is design-only. No observer, controller, launcher, or worker is run.

## Objective

Specify a separate read-only host observer that can describe, without granting
authority:

1. executable byte identity;
2. a caller-supplied CLI-contract capture;
3. workspace identity and declared project inputs; and
4. every source-derived contributor to effective Codex context.

The observer output must be independently and purely verifiable. It must never
label a host fact `qualified`, `ready`, `trusted`, or `authorized`.

## Non-goals and authority

No process launch, provider call, network access, credential read, output
reservation, controller mutation, lease, intent, task admission, result
admission, runtime qualification, signature claim, or public claim.

The observer may read only a finite request-bound set derived from a
version-pinned discovery grammar. It may not import or execute observed code,
invoke Git, load plugins, connect to MCP servers, or invoke Codex.

## Acceptance

- Source anchors cover configuration layers, project discovery, project
  instructions, CLI isolation flags, and context/tool contributors.
- The observation algorithm is finite, stable, symlink-safe, bounded, and
  explicit about missing or redacted evidence.
- CLI behavior is supplied as an immutable capture; the observer does not run
  the executable it is describing.
- Secret-bearing files and values are excluded by construction.
- A pure verifier can reject hash, schema, closure, policy, and cross-record
  mismatches without host I/O.
- Outside reviewers receive one immutable packet and return a bounded design
  disposition.
- The accepted or revised design, review, synthesis, claim ledger, validation,
  handoff, and source seal are committed and mirrored only to the private
  backup.

## Stop conditions

Stop on any need to read credentials, execute an observed binary, follow a
symlink, enumerate an unbounded tree, infer readiness from observation, mutate
the controller, or weaken a missing/incomplete state into success.

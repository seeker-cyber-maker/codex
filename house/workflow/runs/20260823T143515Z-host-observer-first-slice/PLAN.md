# Host observer v1.1 first implementation slice - plan v1

## Recovery

- Existing clean repository at
  `460e3bbc0488cde6c7f0b2d27d0ec6db0abde129`.
- Recovery disposition: resume from the accepted host-observer v1.1 handoff.
- The prior immutable outside-council review is the plan/design check for this
  bounded implementation phase.

## Routing

- Case type: `semantic_implementation` with a security-sensitive filesystem
  boundary.
- Advisory: Terra / high.
- Escalate to Sol / high only if implementation cannot preserve descriptor-
  anchored reads or finite context closure without changing the accepted
  contract.

## Objective

Implement one isolated Python module and dedicated fixtures for:

1. exact sealed request, discovery-grammar, policy, and CLI-capture records;
2. bounded read-only observation through directory-anchored no-follow file
   descriptors;
3. success and fail-closed observation bundles with no partial descriptors;
4. pure independent verification over caller-supplied values; and
5. the accepted falsification matrix, including descriptor-race repair cases.

## Write scope

- `house/worker_exec/host_observer.py`
- `house/worker_exec/tests/test_host_observer.py`
- `house/worker_exec/__init__.py`
- this run directory

## Non-goals and authority

No Codex/Git/plugin/MCP/hook execution, network, credential read, host
environment read, output reservation, controller mutation, lease, launcher,
provider dispatch, result admission, runtime qualification, or public claim.

The observer may hash only request-authorized regular files. Secret-looking
paths or content fail before any digest is emitted. CLI text and environment
projection are caller-supplied evidence, not live host facts.

## Acceptance

- Exact schemas and canonical hashes fail closed.
- Every contributor class is explicit; unknown or omitted classes refuse.
- Current CLI project-config isolation is represented only as
  `CONTENT_ADDRESSED_REQUIRED`.
- Reads use open directory/file descriptors with no-follow semantics, pre/post
  `fstat`, and final entry-to-descriptor identity checks.
- Symlink, hard-link, special-file, mount-crossing, secret, instability,
  collision, limit, capture-binding, and partial-descriptor cases refuse.
- Pure verification works while filesystem, clock, environment, subprocess,
  network, and import APIs are patched to raise.
- Focused and complete House tests, Ruff, Python compilation, `just fmt`, diff,
  source seal, commit, and private backup pass.
- Controller hash/state remain unchanged.

## Stop conditions

Stop on any need for a path-based fallback, secret-bearing digest, observed
code execution, controller access, live provider/runtime action, scope beyond
the three implementation files, or two substantive remediation failures.

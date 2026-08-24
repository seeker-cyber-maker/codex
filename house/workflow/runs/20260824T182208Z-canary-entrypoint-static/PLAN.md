# Frozen plan: parent/helper entrypoint static rung

## Case type and routing

`systems_critical`; recommended model class `Sol/xhigh`. The user delegated
planner/builder authority. Reassess before any signed build, launch, network,
canary, or secret-bearing experiment.

## One bounded graph wave

1. Add `parent_main.c` and `helper_main.c` as the first runtime-facing sources.
   Each must implement exact `--protocol-v1` admission, closed constants, and
   an explicit interface to the fixed FD/protocol contract. They may not create
   processes, open paths, read environment, connect sockets, or emit free-form
   diagnostics.
2. Extend static source tests to verify those files exist, preserve the fixed
   FD/argv contract, and reject prohibited imported symbols. Update the
   object-only builder source list so all five C sources compile to
   non-executable objects under the existing private temporary output policy.
3. Run source tests, object-only compilation/symbol inspection, Ruff, JSON
   parsing, source scans, and diff checks. Remove all object artifacts through
   the existing exact private-output cleanup; none may remain in the source tree.
4. Freeze evidence and obtain a promotion review. Commit only if static
   acceptance passes.

## Acceptance

- No `posix_spawn`, fork, exec, socket, connect, open, environment access, or
  arbitrary argv/path interpretation in either entrypoint.
- The only accepted argv is exact `--protocol-v1`; no canary or runtime content
  is carried through argv.
- Parent/helper descriptor constants and roles agree with `contract.h`.
- All five sources compile to objects; undefined symbols contain none of the
  forbidden capability APIs.
- No executable, bundle, signature, launch, network, canary, Keychain, YubiKey,
  provider, or secret operation occurs.

## Failure rule

At most two bounded source remediations. Any need for a process spawn, signed
bundle, certificate, Keychain, network, canary, provider, or secret action
terminates this run and becomes a new explicit operation node.

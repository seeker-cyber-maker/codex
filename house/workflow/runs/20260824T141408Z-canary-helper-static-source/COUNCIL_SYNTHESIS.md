# Outside-council synthesis

## Decision

`ACCEPT_STATIC_SOURCE_ONLY_WITH_PRE_RUNTIME_GATES`

All three blind reviewers independently reproduced packet SHA-256
`2a20d0e530db0b48efd97da8d651a6f06a8299fbe5bd08c721eab51125163792`
and accepted the checkpoint under its explicit no-runtime claim ceiling. This
is same-provider, same-model-family corroboration, not cross-provider
independence and not authority to link or launch.

## Confirmed observations

- The parent/helper slice has no entrypoint or runtime capability API and
  compiles only to relocatable objects.
- The default signing policy is intentionally unconfigured and refuses before
  `codesign` invocation.
- Ordinary hash, symlink, Team ID, CDHash, requirement, and entitlement drift
  are represented as fail-closed static checks.
- Tests and receipts explicitly stop below runtime codec, sandbox, process,
  network, Keychain, certificate, and secret claims.

## Findings disposition

1. **Accepted, mandatory before a signed candidate:** path-based calls to
   `codesign` retain a theoretical directory-swap TOCTOU window. Close it with
   a descriptor-bound/immutable snapshot design and a race-focused refusal
   test before any policy may become `SEALED_CANDIDATE`.
2. **Accepted, mandatory before runtime progression:** current tests compile
   C codecs and statically inspect structure but do not execute round trips,
   every invalid-header rejection, or the transition table. Add a separately
   authorized pure-codec test link/run before candidate runtime work.
3. **Accepted claim correction:** the iTerm host smoke proves only compatibility
   with current `codesign --entitlements - --xml` output. It proves nothing
   about a future candidate's signing or entitlements.

Neither remediation blocks committing this static-source-only checkpoint,
because both affected claims are explicitly excluded. Both block the next
candidate qualification rung.

## Unsupported claims

No evidence here establishes App Sandbox behavior, process isolation, runtime
codec correctness, signing of a candidate, secret safety, Keychain safety,
provider delivery, or any live dispatch.

## Smallest next action

Start a fresh security-containment run that remains non-canary and
generated-data-free: first close the inspector path race and exercise pure
codec semantics; only then request authority to link and sign a disposable
parent/helper candidate. The user's Apple Development identity can be selected
at that later explicit signing gate without exporting its private key.

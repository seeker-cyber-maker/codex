# After-action council review

## Outcome

The first native canary-helper implementation rung reached
`ACCEPT_STATIC_SOURCE_ONLY_WITH_PRE_RUNTIME_GATES`. It compiles object files
and exercises static policy logic without producing or running a candidate.

## What worked

- Separating compile-only evidence from candidate execution kept authority
  precise.
- The explicit unconfigured signing policy refused before `codesign`, making
  accidental default promotion unavailable.
- Real host `codesign` XML output caught a CLI-format assumption without using
  a candidate or certificate.
- The same immutable packet let all three reviewers reproduce its hash.

## Defects found and disposition

- The first direct Command Line Tools compiler call could not locate system
  headers; binding the explicit macOS SDK sysroot fixed the observed error.
- A new parent-directory symlink test exposed path-component acceptance; the
  inspector now rejects symlinked components before `codesign`.
- The final council preserved a deeper path-race concern and missing direct C
  codec behavioral tests as mandatory gates for the next run. They are not
  papered over by today's static claim ceiling.

## Evidence limitations

The three reviewers share provider, model family, packet, and harness class.
Their agreement is corroboration, not fully independent cross-provider proof.
Static hashes prove byte identity, not runtime correctness or containment.

## Next gate

Open a fresh, separately authorized security-containment run for TOCTOU
hardening and pure-codec execution tests. Stop again before candidate launch.
Signing identity discovery and use remain a later explicit Keychain/signing
gate.

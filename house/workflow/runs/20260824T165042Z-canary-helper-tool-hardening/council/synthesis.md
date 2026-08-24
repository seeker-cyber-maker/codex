# Council synthesis: canary-helper tool hardening

## Outcome

`ACCEPT_TOOL_HARDENING_ONLY`

The exact source snapshot is accepted only for bounded production codesign and
codec subprocess calls plus the codec runner's private output lifecycle under
ordinary same-user operation. This is not signing, candidate, hostile-host,
runtime-containment, canary-safety, or secret-safety qualification.

## Council completion

Three of three blind reviewers completed. All confirmed the same packet
SHA-256, `3d2a4b5b2421c8ab20107009d6ceef6f1624c3dc92ecf992dd066f15a9ab158e`,
and all 14 indexed artifact hashes. Each independently returned the exact narrow
acceptance label. Agreement is correlated rather than fully independent: all
used `gpt-5.6-luna`, OpenAI's same provider, the Codex collaboration harness,
and the same immutable packet.

## Confirmed observations

- The production static-codesign path uses a ten-second timeout and translates
  `TimeoutExpired` into fail-closed inspection failure.
- Codec compile/link, codesign display, and execution use positive finite
  timeouts of 30, 10, and 5 seconds respectively.
- The codec runner requires an existing non-symlink output-root leaf, pins its
  canonical parent with a no-follow directory descriptor, atomically reserves a
  randomized private child, enforces mode 0700 and inode agreement, and removes
  only the exact known executable and child through descriptor-relative calls.
- Symlink-root refusal occurs before compiler invocation. Success and injected
  compile, signature-inspection, and execution timeouts clean the expected
  private output with no ordinary parent residue.
- The unchanged pure-codec executable ran successfully with zero output, stable
  executable hash, ad-hoc signature, no Team ID, mode 0700, and exact cleanup.
- Focused validation passed 21 tests and the full House suite passed 260 tests.
  Ruff, compilation, JSON/JSONL parsing, diff checks, and the no-source-binary
  check passed.
- No parent/helper link or launch, certificate discovery, identity signing,
  Keychain, network, provider, YubiKey, generated canary, or real secret was
  attempted.

## Claim ceiling

Injected `TimeoutExpired` tests establish deterministic regression behavior,
not measured wall-clock behavior of genuinely hung tools. The private-output
claim excludes malicious same-UID interference and hostile toolchains. An
unexpected entry causes a cleanup refusal and intentionally leaves the private
directory for investigation; this must not be described as recursive cleanup.
The observed empty parent after exercised calls is not a universal hostile-race
guarantee.

No support is admitted for compiler or codesign integrity, signed parent/helper
identity, bundle semantics, App Sandbox behavior, dynamic launch-path identity,
process containment, hostile same-UID resistance, canary safety, or secret
safety. The ad-hoc/no-Team-ID executable is not signing qualification.

## Decision and confidence

Decision: accept and commit this source-only tool-hardening milestone, then stop
before certificate discovery, identity signing, or parent/helper launch.

Confidence is high for the narrow source and regression claims and moderate for
independent corroboration because the reviewer infrastructure was shared.

No round two is warranted because there was no decision-affecting disagreement.

## Smallest next action

Open a fresh, explicitly authorized signing-admission phase. Freeze the actual
parent/helper sources, bundle layout, entitlements, and candidate manifest;
then bind paths, sizes, hashes, CDHashes, Team ID, designated requirements,
exact entitlements, and platform build before any separately authorized launch.
Use a real hung-tool probe if the next phase needs a measured wall-clock timeout
claim.

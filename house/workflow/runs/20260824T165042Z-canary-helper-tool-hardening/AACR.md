# After-Action Council Review: canary-helper tool hardening

## Work completed

Closed the two robustness debts preserved by the preceding pre-signing review:
finite subprocess timeouts and a runner-owned private codec output namespace.
Production static inspection now fails closed on codesign timeout. Codec build,
signature display, and execution are separately bounded. The codec runner owns
a randomized mode-0700 child under a pinned caller-provided output parent and
uses exact descriptor-relative cleanup.

## Verification result

- Focused native contract: 21 passed.
- Full House suite: 260 passed, with the pre-existing unclosed SQLite
  `ResourceWarning` retained as a warning.
- Real pure-codec test: exit 0, zero output, mode 0700, ad-hoc/no-Team-ID,
  stable executable hash, cleanup complete, empty caller parent.
- Ruff, compileall, JSON/JSONL parsing, `git diff --check`, and source-artifact
  absence checks: passed.
- Three of three outside reviewers verified the identical packet and all 14
  indexed artifacts, then accepted `ACCEPT_TOOL_HARDENING_ONLY`.

## Deviations and negative evidence

The first combined validation shell did not use fail-fast behavior, so later
successful commands masked Ruff's four `SIM117` findings. The nested context
managers were flattened without behavioral change and every subsequent
combined validation used `set -e`. No behavioral implementation failure
occurred.

Timeout tests inject `TimeoutExpired`; they do not measure an actually hung
tool. Ancestor symlinks are canonicalized while a symlink at the supplied
output-root leaf is rejected. Same-UID hostile interference is outside this
claim. Unexpected entries deliberately stop cleanup and remain for forensic
review instead of triggering recursive deletion.

## Authority accounting

Authorized and used: source edits, local deterministic tests, static codesign
display, and a disposable pure-codec link/run.

Not authorized and not attempted: parent/helper link or launch, certificate
discovery, Keychain access, identity signing, network/provider access, YubiKey,
generated canary, real secret, or any runtime-admission operation.

## Decision

Accept and commit under `ACCEPT_TOOL_HARDENING_ONLY`. Do not infer signing,
candidate, sandbox, containment, hostile-host, canary, or secret qualification.

## Next gate

A fresh authority decision is required before certificate discovery or
identity signing. The next packet should bind the actual candidate sources,
bundle layout, entitlements, hashes, CDHashes, Team ID, designated requirements,
and platform build. Use `gpt-5.6-sol` at `xhigh` for that phase because it
crosses identity and dynamic containment boundaries.

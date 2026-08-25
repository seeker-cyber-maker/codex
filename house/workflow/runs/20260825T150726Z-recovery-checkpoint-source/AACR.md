# S1 after-action council review

Status: `CLOSED_SOURCE_ONLY`

## Outcome

S1 produced and validated a 280-line pure verifier plus 176 dedicated test
lines.  It matches the accepted F1 whole receipt, refuses malformed/tampered
inputs, is idempotent for identical inputs, and exposes no production file,
clock, database, process, network, hardware, provider, worker, runtime, or
dispatch path.  Three final reviewers accepted that exact source-only result.

## What worked

- F1 was a useful frozen known answer: no fixture generator or signing scalar
  entered production code.
- The plan's fixed field/receipt ceiling made independent review mechanical.
- The source/test budget held at 456 of 800 lines.
- Full regression testing surfaced no integration failure.

## Gap and remediation

The independent checker first failed before candidate execution because running
it as a direct script changed Python's import root.  A single root-cause
investigation confirmed that the repository cwd could import `house` while the
run-directory script could not.  The one-line-class validation bootstrap was
fixed, rechecked directly, and documented in `DEBUG_RECEIPT.json`.  Production
source was never modified for that runner defect.

The full suite still emits preexisting expected-CLI usage output and one SQLite
`ResourceWarning`.  It passes 312 tests; those observations are not attributed
to S1 and remain outside this scope.

## Limits and next gate

This code is not a real recovery system.  The next possible work is a distinct
trust-anchor/revocation/time/storage design and source gate, beginning with
the R1 council revisions.  It needs a new explicit continuation and may not
reuse S1 as authority for key, YubiKey, Keychain, signing, persistence,
runtime, or dispatch work.

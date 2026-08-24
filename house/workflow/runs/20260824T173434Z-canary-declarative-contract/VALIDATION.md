# Source-only validation receipt

Validated at: `2026-08-24T17:51:29Z`

## Fresh authorized gates

- `python3 -m unittest -v house.native.canary_helper.tests.test_candidate_plan`
  passed `23/23` tests after council remediation.
- Ruff passed for `candidate_plan.py` and `test_candidate_plan.py`.
- The checked-in contract validated as
  `NOT_READY_UNRESOLVED_NO_OPERATIONS`, returned zero operations, and reported
  no tool execution, candidate creation, or candidate launch.
- Static AST inspection found no imports of subprocess, ctypes,
  multiprocessing, socket, requests, httpx, or urllib and no process, dynamic
  execution, network-connection, or URL-opening call surface in the planner.
- Contract, run-manifest, evaluation-card, plan-seal, and event-ledger JSON
  parsed successfully.
- No `.o`, `.a`, `.so`, `.dylib`, `.app`, or executable candidate artifact was
  present under `house/native/canary_helper`.
- No new C, Objective-C, Objective-C++, or Swift source was added.
- `git diff --check` passed.

## Restricted regression boundary

The current full House suite was deliberately not executed. Nine legacy test
modules import process or socket facilities; in particular,
`house/native/canary_helper/tests/test_native_contract.py` can invoke clang,
the linker, codesign, and a candidate test executable. Those actions are
forbidden by this run's authority even when reached through a test runner.

The predecessor baseline of `260/260` House tests at the accepted source state
remains historical evidence. It is not represented as a fresh result for this
source change. Current acceptance therefore rests on the fresh 23-test focused
suite, static no-execution checks, exact artifact hashes, and outside review.

The first remediation rerun had one test-only failure because macOS canonical
resolution maps `/var` to `/private/var`. The assertion was corrected to compare
the canonical output path. No implementation defect or restricted action was
involved; the complete 23-test rerun then passed.

## Authority-negative evidence

No compiler, linker, bundle creator, certificate or Keychain discovery tool,
signer, candidate launcher, network path, canary path, provider, YubiKey, or
secret operation was invoked during this run.

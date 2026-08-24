# Immutable pre-signing-gates council packet

Status: `PRE_COUNCIL_VALIDATION_PASSED`

Repository: `/Users/tiga/Documents/Codex_Projects/codex-dream-house`

Starting HEAD: `e51332d3c394f0eada70b85fa75adffb6af7e616`

Run: `house/workflow/runs/20260824T145608Z-canary-helper-pre-signing-gates`

## Decision requested

Decide whether this source-only milestone may be accepted as
`ACCEPT_PRE_SIGNING_GATES_ONLY`, rejected, or accepted only after a bounded
remediation. Review exactly the files and hashes in `EVIDENCE_INDEX.jsonl`.
This review confers no authority to write files, link or launch the
parent/helper, discover certificates, access Keychain, sign with an identity,
use network/providers/YubiKey, generate a canary, or touch a real secret.

## Frozen claim ceiling

The milestone may establish only both of the following:

1. For strictly verified standalone Mach-O files, static `codesign`
   inspection operates on a private byte-for-byte snapshot copied from a
   pinned no-follow source descriptor, and ordinary source replacement or
   drift is refused before qualification.
2. The unchanged `protocol.c` codec directly passed a disposable no-I/O linked
   test covering the fixed 80-byte big-endian wire image, round trip, every
   declared validation error, and the complete transition truth table.

It does not establish a signed parent/helper candidate, later launch-path
identity, App Sandbox behavior, process containment, generated-canary safety,
or real-secret safety. It does not claim protection from a malicious same-UID
process that already controls the inspector host. Extracted executables from
application bundles are explicitly outside the snapshot method unless they
strictly verify without their bundle context.

## Implementation under review

- `artifact_inspection.py` rejects empty, absolute, dot, dot-dot, empty, and
  symlink path components; traverses from a canonical directory descriptor;
  opens the source no-follow; bounds size to 64 MiB; copies from that pinned
  descriptor into a mode-0700 private temporary namespace; binds size/hash;
  runs only absolute `/usr/bin/codesign` against the private snapshot; requires
  strict verification, Mach-O format, non-ad-hoc signature, non-empty and exact
  Team ID, CDHash, designated requirement, and entitlement set; rehashes the
  snapshot; then reopens and compares source path, device/inode, size, and hash.
- Signing-policy schema v2 adds sealed byte sizes and rejects the deliberately
  unconfigured template.
- `run_codec_tests.py` links only `protocol.c` plus
  `tests/codec_contract_test.c`, verifies the linker-produced test binary is
  ad hoc with no Team ID, executes it with only `LC_ALL=C` and a five-second
  timeout, requires exit zero and zero output, and records all forbidden
  candidate/signing/network/secret actions as not attempted.

## Direct observations

- Passing a pinned descriptor to host `codesign` through `/dev/fd/N` failed all
  four inspection modes with `cannot find code object on disk`; that design was
  rejected.
- A pinned byte snapshot of `/usr/bin/true` hash-matched and passed strict
  verification. A snapshot of the extracted iTerm app executable hash-matched
  but failed strict verification because bundle context was absent; bundle
  executables remain excluded.
- The actual final inspector path over a copied `/usr/bin/true` invoked
  `codesign` only on the private snapshot and failed closed at missing Team ID.
- The codec test's first attempt exited at source line 37 because the fixture's
  allegedly valid payload exceeded the declared 4096-byte limit. The fixture
  was corrected without modifying `protocol.c`; the second and only remediation
  exited zero with no output. The disposable linked binary reported
  `Signature=adhoc`, `TeamIdentifier=not set`.
- A first whole-suite command omitted the discovery root and discovered zero
  tests. The corrected command passed all 255 tests; this was an invocation
  error, not an implementation change.

## Deterministic validation

- Focused native contract: 16 passed.
- Full House suite: 255 passed, with one pre-existing unclosed-SQLite
  `ResourceWarning` and no failure.
- Ruff: pass.
- Python compilation: pass.
- `git diff --check`: pass.
- Compiled/executable artifacts under the source directory: none.
- Parent/helper link and launch, identity signing, certificate discovery,
  Keychain, network, providers, YubiKey, generated canary, and real secret:
  all `NOT_ATTEMPTED`.

## Exact source snapshot

| File | SHA-256 |
|---|---|
| `README.md` | `43818d6b25e216bf3473d14e853eeb3631e15723303a36b8cee5590433357e99` |
| `artifact_inspection.py` | `f107996647c3a17bb939f6a95ab7a1a6757223761ebe6e6979bfbcc8a7698fe7` |
| `signing_policy.json` | `29be0e0a2ba7f3c938abeb9f0e528efa14a9affe8c93174d471cea6e826b5d09` |
| `run_codec_tests.py` | `aac3ec8ed0e200301e8ec03d1613a08d359695379068f7ca1d63c75beed9824a` |
| `tests/codec_contract_test.c` | `48b5b067d539e901ff37d48aff148af1d08f99297b82b04fb2359efab10fdf93` |
| `tests/test_native_contract.py` | `84c4d3f12de7573253dbf0a9faa857b72b5f1a9cb09843b258ae5af32fd8b67d` |
| `protocol.c` | `a9dc942961d4486b8cb8d0bb4e9539afcac74681a81c29bab8bab875e66486b1` |
| `protocol.h` | `ad725dd956c0232cf941077a6285463a8fd66bf0d7e535be02f4583d4281205e` |

## Reviewer questions

1. Does any implementation defect invalidate either narrow claim?
2. Is a missing test or receipt mandatory before this source-only milestone can
   be committed, while keeping signed candidates and runtime behavior out of
   scope?
3. Do the receipts overstate identity, containment, or secret-safety evidence?
4. What exact next gate must remain before certificate discovery, identity
   signing, and dynamic post-spawn identity checks?

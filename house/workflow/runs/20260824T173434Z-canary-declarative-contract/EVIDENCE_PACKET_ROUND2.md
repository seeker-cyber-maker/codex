# Evidence packet: targeted remediation review

Council ID: `20260824T175129Z-canary-contract-promotion`
Round: `2`
Mode: `meta-review`
Decision question: Did the bounded source-only remediation fully address the
five evidence-bearing round-one objections without widening authority or
creating an execution surface?
Deliverable: `OBJECTIONS_RESOLVED`, `OBJECTIONS_REMAIN`, or `BLOCK` with exact
evidence.
Privacy: `local-only`
Cost ceiling: `one bounded Luna reviewer`

## Authoritative status

- The round-one packet remains immutable at `EVIDENCE_PACKET.md`, SHA-256
  `84f7bd264d26384e527e8bdb13f58fb6da30e3739da124624c970686363365b9`.
- Round-one claim ledger:
  `council-runs/20260824T175129Z-canary-contract-promotion/claim-ledger.json`.
- Round-one dissent:
  `council-runs/20260824T175129Z-canary-contract-promotion/reviewers/adversarial-methodologist.md`.
- Source-only authority and all original prohibitions remain unchanged.

## Revised evidence

1. `candidate_plan.py`, SHA-256
   `ef224922a2d7e08131f95fb2aac97cb96fbb17a82d309e2e879a1ad7aa8b641b`.
2. `test_candidate_plan.py`, SHA-256
   `9eca036e6fabfdad57d85c8668b6c613fc0347156d6616db9a8614917946f662`.
3. Unchanged contract, SHA-256
   `a0a4899713185c1970676c0ee6b3a97f6e3e4b51d8a9d0bd4e9b9f33e738ee87`.
4. Updated `VALIDATION.md`: 23/23 focused tests, Ruff, static restricted-call
   audit, zero operations for the unresolved contract, zero generated
   candidate artifacts, and the restricted full-suite boundary.

All source paths are relative to
`/Users/tiga/Documents/Codex_Projects/codex-dream-house/house/native/canary_helper`.
Run evidence is under
`house/workflow/runs/20260824T173434Z-canary-declarative-contract`.

## Remediation map

1. Required inventory members now compare exact path, kind, and mode tuples.
2. Both link argv records now include the resolved clang path, SDK/sysroot,
   deployment target, and architecture, plus explicit tool/platform bindings.
3. Compile/link records carry tool/platform bindings; sign/verify records carry
   codesign, identity, entitlement, hardened-runtime, and final-artifact
   expectation data.
4. Designated requirements must match one exact canonical bundle-ID/Team-ID
   grammar rather than contain two substrings.
5. Workspace reservation data now pins the canonical parent path, device, and
   inode; requires an atomic private-workspace receipt; and says execution is
   not attempted or implemented.
6. New adversarial tests cover every item above. The first rerun found only a
   test assertion using macOS `/var` rather than canonical `/private/var`; the
   test was corrected and the complete 23-test rerun passed.

## Constraints

- Read-only review. Bounded file reads and hashes only.
- Do not modify, delegate, use network, execute project code, or invoke any
  build, link, bundle, certificate, Keychain, signing, launch, canary, provider,
  YubiKey, or secret operation.
- Stored argv is inert JSON data and is not execution authority.
- Claim ceiling remains source/design and plan-data only.

## Reviewer instruction

Re-evaluate only the five round-one objections against the revised hashes.
State which are resolved or remain, identify any remediation-caused regression,
and return the council response contract. Do not reopen unrelated design work.

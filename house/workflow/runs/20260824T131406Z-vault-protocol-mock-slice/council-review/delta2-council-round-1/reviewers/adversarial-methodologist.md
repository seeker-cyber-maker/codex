# Review: adversarial-methodologist

Packet SHA-256: 8d1e9c04daa67f13d8d2e8fb9b50146c3e8b38390dd5f6028ea6c8be24cc4f48
Dispatch model/provider: deepseek-v4-flash / OpenCode Go
Reviewer self-report: unknown
Harness: provider-orchestration OpenCode Go catalog proxy
System-prompt profile: council role only; otherwise unknown
Memory: unknown
Reasoning mode: unknown
Disposition: completed

## Verdict
ACCEPT_FINAL_NON_RUNTIME_REFERENCE

## Direct observations
- `rotate_generated()` wraps `_rotate_generated()` in a `try/finally` that unconditionally calls `new_value.clear()` (source, lines ~430-445). This covers all early-failure paths including invalid advance, missing source, and authentication failures.
- The internal `_rotate_generated()` performs source authentication and exact revision validation before any new-state mutation (source, lines ~450-470). It loads and authenticates the old record, clears old plaintext, and checks `old_payload["revision"] != old_revision` before creating the new key or ciphertext.
- The cleanup path in `_rotate_generated()` removes the tombstone, new ciphertext, and new key on any later exception (source, lines ~500-520). It tracks `tombstone_created`, `new_path_created`, and `new_key_created` flags.
- Regression tests `test_09c`, `test_09d`, and `test_09e` explicitly assert that `new_value.cleared` is `True` after corrupt-source, wrong-revision, invalid-advance, and missing-source failures (test source, lines ~200-280).
- The test suite includes 29 focused tests and 239 complete House tests passing, per the remediation document (POST_COUNCIL_REMEDIATION.md, "Regression evidence" section).

## Inferences
- The unconditional `finally` clear in `rotate_generated()` closes the previously identified input-clearing omission, with high confidence. Falsifier: a test that calls `rotate_generated()` with a `ZeroizingBuffer` and asserts `cleared` is `False` after any exception path; no such test exists in the attached suite.
- The source-authentication-before-mutation ordering prevents the "corrupt source destroys old key" defect, with high confidence. Falsifier: a test that corrupts the source ciphertext, calls `rotate_generated()`, and then successfully verifies the old key still exists; `test_09c` covers this and passes.
- The rollback logic handles later failures (e.g., tombstone collision) by removing the new key and ciphertext, with medium confidence. Falsifier: a test that forces a failure after `put_generated()` succeeds but before tombstone creation, then asserts the new key is still available; `test_09d` covers the tombstone-collision case and passes.

## Unsupported or contradicted claims
- The claim that "29 focused vault/context tests passed" and "239 complete House tests passed" is chair-observed and not independently verified in this packet. The packet explicitly states reviewers should statically assess rather than assume independent execution. This is a limitation, not a contradiction.
- The claim that "Both new regression tests failed against commit `74b2a04a1b`" is asserted in the remediation document but no before-fix test output is attached. This is unverifiable from the supplied evidence.

## Recommendation
Stop. The final remediation candidate closes the identified rotation defects and the input-clearing omission within the generated-only mock boundary. The source and test evidence are consistent with the claimed fixes, and the claim ceiling is appropriately scoped.

## Limitations
- I did not execute the tests; I relied on static inspection of the source and test code.
- The before-fix regression evidence is not independently verifiable from the attached packet.
- The rollback logic is only tested for the tombstone-collision case; other later-failure paths (e.g., `os.write` failure) are not explicitly covered.
- The packet does not include the full test output or the exact test count breakdown, so the "29 focused" and "239 complete" numbers are taken on trust from the remediation document.

# Review: evidence-auditor

Packet SHA-256: `f7f68e5676bd2eea2e186e92a41b3c815b9221c0343c870942e99d58b88850b2` (verified)

Dispatch model/provider: gpt-5.6-luna / OpenAI same-provider collaboration

Reviewer self-report: Evidence-auditor review; self-reported runtime identity is non-authoritative

Harness: Codex desktop multi-agent collaboration

System-prompt profile: Shared Codex safety/project profile; exact protected text unavailable

Memory: disabled

Reasoning mode: medium

Disposition: completed

## Verdict

Accept as `ACCEPT_PRE_SIGNING_GATES_ONLY`. The two narrow claims are supported, with no basis for signed-candidate, runtime-containment, launch-identity, canary, or secret-safety claims.

## Direct observations

- Packet hash, `EVIDENCE_PACKET.md`, `EVIDENCE_INDEX.jsonl`, all eight indexed source hashes, and all eleven indexed receipt hashes independently matched.
- `artifact_inspection.py` opens strict relative paths through no-follow descriptors, copies bytes into a mode-0700 private snapshot, hashes and size-binds it, invokes absolute `/usr/bin/codesign` only on the snapshot, then rechecks snapshot and source path/device/inode/size/hash.
- `signing_policy.json` is `NOT_CONFIGURED_NO_LAUNCH`; null sizes, hashes, CDHashes, Team IDs, and requirements prevent qualification before codesign.
- The pinned-FD method failed with `cannot find code object on disk`; the private snapshot method passed for standalone `/usr/bin/true` and refused the extracted iTerm executable without bundle context.
- `protocol.c` implements fixed 80-byte big-endian encoding/decoding, declared validation errors, and the linear transition table. The linked disposable test passed with zero output and an ad-hoc, no-Team-ID signature.
- Receipts record no parent/helper link or launch, identity signing, certificate discovery, Keychain, network, YubiKey, generated canary, or real-secret activity.
- Focused validation records 16 passes; full validation records 255 passes, with one pre-existing SQLite resource warning.

## Inferences

- The snapshot design is adequate to bind static inspection to bytes read from a pinned source descriptor and detect ordinary source replacement or drift before qualification. Confidence: high. Falsifier: a controlled race or filesystem case that changes the inspected source while evading the final path, inode, size, and hash checks.
- The codec claim is adequately established for `protocol.c` and its declared contract, not for any parent/helper integration. Confidence: high. Falsifier: a missing transition/error case or a protocol behavior outside the fixed test fixture.
- The test suite and receipts provide strong implementation evidence but are not independent proof of future host behavior; mocked codesign tests and limited live probes leave platform-specific candidate behavior untested. Confidence: high. Falsifier: a real sealed candidate failing the same static policy.

## Unsupported or contradicted claims

- No evidence supports signed parent/helper candidate identity.
- Entitlement files do not establish App Sandbox runtime containment.
- No evidence supports later launch-path identity, dynamic process containment, same-UID hostile-host resistance, generated-canary safety, or real-secret safety.
- `QUALIFIED_STATIC_ARTIFACTS_NO_LAUNCH` is a future sealed-policy state, not the current unconfigured milestone.
- The codec test’s ad-hoc signature is not identity signing.

## Recommendation

Accept and seal this milestone at the stated claim ceiling. Stop before certificate discovery or signing. The next mandatory gate is an explicitly authorized, genuinely sealed parent/helper candidate whose size, hashes, CDHashes, Team ID, designated requirements, entitlements, and platform build are bound and statically inspected. Only afterward should separately authorized launch-path identity, containment, canary, and secret-safety tests occur.

## Limitations

- No candidate was linked, signed, or launched.
- Live probes covered standalone `/usr/bin/true` and an extracted bundle executable, not the future candidate.
- Same-provider/model-family and shared harness dependencies weaken reviewer independence.
- Receipts are hashed records of reported execution; this review did not rerun tests or perform prohibited signing/runtime actions.

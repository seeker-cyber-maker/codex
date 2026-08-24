# Review: adversarial-methodologist

Packet SHA-256: `f7f68e5676bd2eea2e186e92a41b3c815b9221c0343c870942e99d58b88850b2` — verified. All 17 indexed source/receipt hashes independently matched.

Dispatch model/provider: `gpt-5.6-luna / OpenAI same-provider collaboration`

Reviewer self-report: Blind, independent, read-only adversarial-methodology review. Searched for shortcut paths, leakage, race confounds, unsupported authority, and claim overreach.

Harness: Codex desktop multi-agent collaboration; exact build/version unavailable.

System-prompt profile: Shared Codex safety/project profile; protected text unavailable.

Memory: Requested disabled by isolated dispatch; actual platform enforcement not independently observable.

Reasoning mode: medium

Disposition: completed

## Verdict

The two frozen narrow claims are adequately supported for this source-only milestone. Acceptance must not imply signed-candidate qualification, launch-path identity, sandbox containment, process containment, canary safety, or secret safety.

## Direct observations

- Packet hash matched the expected value.
- Every indexed file’s SHA-256 matched its declared hash.
- `artifact_inspection.py` copies from an `O_NOFOLLOW` descriptor, hashes the private copy, invokes absolute `/usr/bin/codesign` only on that copy, validates metadata/requirements/entitlements, and rechecks source identity and bytes before returning qualification.
- The unconfigured policy refuses before any codesign invocation.
- The descriptor-to-`/dev/fd/N` method was empirically rejected; the private snapshot method was admitted only for strictly verified standalone Mach-O files.
- The codec oracle exercises the 80-byte wire image, round trip, all declared codec error results, and the complete transition matrix. The receipt records ad-hoc/no-Team-ID signing and zero-output, zero-exit execution.
- The packet explicitly records no parent/helper link or launch, certificate discovery, Keychain, network, YubiKey, generated canary, or real secret.
- The first codec fixture failure and corrected rerun are disclosed rather than hidden.

## Inferences with confidence/falsifier

- High confidence: ordinary source replacement or content drift during static inspection is detected before a qualified result is returned. Falsifier: a controlled replacement that changes path identity, inode, size, or bytes still yields `QUALIFIED_STATIC_ARTIFACTS_NO_LAUNCH`.
- High confidence: the codec behavior claim is limited to `protocol.c` and the disposable test binary. Falsifier: a test mutation in `protocol.c` that preserves all receipt assertions while changing a declared behavior.
- Medium confidence: the snapshot method is not a complete provenance or host-integrity boundary. Falsifier: an independently enforced trusted root/host attestation covering the inspector and source namespace.
- Medium confidence: receipt fields such as `NOT_ATTEMPTED` establish process intent, not independently audited absence. Falsifier: OS-level execution audit showing a forbidden operation.

## Unsupported or contradicted claims

- Parent/helper object-build, source-capability, and entitlement assertions are not independently verifiable from the indexed packet because their source files are absent from `EVIDENCE_INDEX.jsonl`.
- Receipt assertions about process count, cleanup, and forbidden actions are self-reported; they are not proof against a hostile same-UID inspector host.
- The implementation does not enforce a timeout for `codesign`, and codec compile/signature-inspection subprocesses also lack timeouts. This is a robustness/DoS gap, not a contradiction of the narrow static-behavior claims.
- `run_codec_tests.py` does not itself enforce a private, no-follow, mode-0700 output namespace. That is outside the accepted claim ceiling but must be addressed before treating the runner as a stronger security boundary.
- The evidence does not establish App Sandbox runtime behavior, post-spawn identity, containment, canary delivery, or secret handling.

## Recommendation

Preserve the source-only acceptance exactly as `ACCEPT_PRE_SIGNING_GATES_ONLY`. Before certificate discovery or identity signing, require a fresh explicit authority delta and a sealed candidate manifest binding parent/helper paths, sizes, hashes, CDHashes, designated requirements, entitlements, and platform build. After signing, run static private-snapshot inspection first; only a passing result may unlock a separately authorized disposable launch gate with dynamic parent/helper identity checks and no real secrets.

## Limitations

No candidate was linked or launched; no certificates, Keychain, network, providers, YubiKey, canary, or secret were accessed. Review was limited to the packet and its indexed references. Same-provider/model-family collaboration weakens independence despite blind role isolation.

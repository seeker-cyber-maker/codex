# Council synthesis: canary-helper pre-signing gates

## Outcome

`ACCEPT_PRE_SIGNING_GATES_ONLY`

The exact source snapshot is accepted only for its two frozen claims: private
snapshot-bound static inspection of strictly verified standalone Mach-O files,
and direct pure-codec contract execution. This is not signed-candidate or
runtime qualification.

## Council completion

Three of three blind reviewers completed. All echoed the same council-packet
SHA-256:
`f7f68e5676bd2eea2e186e92a41b3c815b9221c0343c870942e99d58b88850b2`.
All three independently returned the same narrow acceptance. This agreement is
correlated, not fully independent: all used `gpt-5.6-luna`, OpenAI's same
provider, the Codex collaboration harness, and the same frozen evidence.

The chair's deterministic verifier counted 18 index records and found zero hash
errors. Two raw reviewer narratives miscounted those records as 17 or as eight
source plus eleven receipt records. Their explicit claims that every referenced
hash matched are retained, but the deterministic count is authoritative.

## Confirmed observations

- The source opens no-follow paths through directory descriptors, copies the
  pinned bytes into a private snapshot, binds size and SHA-256, restricts
  `codesign` to that snapshot, and rechecks snapshot and source identity/content
  before qualification.
- Host `codesign` rejected `/dev/fd/N`, so that design was not used. A private
  snapshot worked for standalone `/usr/bin/true`; extracted bundle-executable
  verification failed without bundle context and remains excluded.
- The deliberately unconfigured signing policy refuses before codesign.
- The disposable codec test directly covered the fixed wire image, round trip,
  declared validation failures, and full transition table; it passed with zero
  output and only a linker-produced ad-hoc/no-Team-ID signature.
- Focused validation passed 16 tests and the full House suite passed 255 tests.
  No compiled or executable artifact remained under the source tree.
- No parent/helper candidate was linked, signed, or launched. Certificate
  discovery, Keychain, network, providers, YubiKey, generated canary, and real
  secret were not attempted within the recorded run.

## Unsupported claims rejected

No claim is admitted for signed-candidate identity, later launch-path identity,
App Sandbox runtime behavior, dynamic process containment, same-UID hostile-host
resistance, generated-canary safety, or real-secret safety. Entitlement files
remain expected inputs, not runtime proof. Receipt `NOT_ATTEMPTED` fields are
bounded execution records, not hostile-host attestation.

## Preserved non-blocking findings

The adversarial reviewer identified two source-level robustness debts that do
not contradict the frozen claims:

1. Static `codesign` calls and codec compile/signature-inspection calls lack
   enforced subprocess timeouts.
2. The codec runner relies on the caller to provide a fresh temporary output
   directory; it does not itself reserve a private no-follow mode-0700
   namespace.

These must be resolved or explicitly bounded before either helper is promoted
as a stronger security boundary. Parent/helper sources and entitlements should
also be included in the next candidate-specific evidence packet.

## Decision and confidence

Decision: accept and commit this source-only milestone, then stop before any
certificate discovery, identity signing, or candidate launch.

Confidence: high for the narrow implementation and codec claims; moderate for
independent corroboration because reviewer infrastructure was shared.

No round two is warranted because no disagreement changes the decision.

## Smallest next action

Open a fresh, explicitly authorized signing-admission phase. Before it performs
certificate discovery or identity signing, freeze the actual parent/helper
source and bundle layout, address the timeout/output-namespace debts where
applicable, and seal a candidate manifest binding paths, sizes, hashes, CDHashes,
Team ID, designated requirements, exact entitlements, and platform build. A
passing private-snapshot static inspection may then unlock a separate disposable
launch gate with dynamic post-spawn identity checks and no real secrets.

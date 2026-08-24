# Adversarial static-source review

Packet SHA-256: `2a20d0e530db0b48efd97da8d651a6f06a8299fbe5bd08c721eab51125163792` — independently verified.

Dispatch model/provider: `gpt-5.6-luna/OpenAI Codex collaboration`

Reviewer self-report: Blind, read-only review completed. Packet and cited source/receipt artifacts were inspected; no candidate was linked, launched, or accessed through Keychain/network. No files were modified.

Harness: Codex desktop shell; static filesystem inspection only.

System-prompt profile: Default behavior profile plus packet-imposed read-only/no-runtime/no-delegation constraints.

Memory: Not used.

Reasoning mode: Independent adversarial methodology review; direct observations separated from inferences.

Disposition: `ACCEPT_STATIC_SOURCE_ONLY`

## Verdict

The evidence supports promotion only of the source/object/static-inspection rung. No blocking defect was found against its explicit claim ceiling.

## Direct observations

- Packet SHA-256 matches the expected value exactly.
- All nine explicitly hashed primary artifacts match their packet hashes.
- The source contains pure protocol/contract functions; parent/helper sources expose no `main`, process-launch, network, arbitrary-file, environment, or logging APIs.
- Object receipt records compile-only `clang -c` and `nm -u`, with no link or candidate launch.
- Static inspector rejects unsealed policy before `codesign`, rejects missing Team ID/ad hoc signatures, checks hashes/signature metadata/requirements/entitlements, and performs a final content-hash comparison.
- Validation explicitly excludes linked-candidate, runtime-codec, App Sandbox, process-containment, and secret-safety claims.
- `VALIDATION.json` itself was not assigned a hash in the packet's primary list, although the pre-council seal contains one.

## Inferences (with confidence/falsifier)

- High confidence: this rung does not establish runtime containment or sandbox enforcement. Falsifier: a later authorized runtime artifact with dynamic identity, capability-probe, and process-topology receipts.
- High confidence: the object build is not executable candidate evidence. Falsifier: a linked/loaded/launched artifact receipt.
- Medium confidence: the inspector is fail-closed for ordinary path/content/signature mismatches. Falsifier: a controlled race or malformed policy that produces qualification despite mismatch.
- Medium confidence: path-based inspection retains a theoretical directory-swap TOCTOU window between path validation, `codesign`, and final hashing. Falsifier: descriptor-relative traversal or immutable-root enforcement.

## Unsupported or contradicted claims

- Any claim of App Sandbox behavior, process isolation, runtime codec correctness, secret safety, Keychain safety, or provider safety would exceed the packet.
- Passing 9/9 or 248/248 tests does not prove runtime behavior.
- The host iTerm codesign XML smoke is parser/tool compatibility evidence only, not candidate-signing or entitlement evidence.
- “No process saw the canary” would contradict the accepted design's own exposure vocabulary; no canary was used here.

## Recommendation

Accept the static-source-only promotion with the existing claim ceiling. Before any future candidate qualification, apply one bounded hardening change: close the directory/path TOCTOU window using descriptor-relative, no-follow traversal or an immutable candidate root, and add a race-focused refusal test. Do not broaden authority or launch based on this receipt.

## Limitations

I did not rerun the reported test suite or compiler; those results remain receipt claims. Runtime codec semantics, linking, signing of a candidate, dynamic code identity, sandbox enforcement, process topology, network denial, and secret handling remain unmeasured.

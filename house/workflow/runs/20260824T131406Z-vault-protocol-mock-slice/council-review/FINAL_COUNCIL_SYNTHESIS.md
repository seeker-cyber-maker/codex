# Final council synthesis

## Decision

`ACCEPT_FINAL_NON_RUNTIME_REFERENCE`

The final source at SHA-256
`6f87a1ee743b7e6315e8e78dec08f4f0c9cd7f499d4203a2f78602dc89a53500`
closes the chair-reproduced rotation defects and the valid input-clearing
omission found during the first delta review.

## Confirmed observations

- Old ciphertext/schema/identity and the exact stored revision are checked
  before creating a new key, directory, ciphertext, or tombstone.
- Invalid advance, missing source, corrupt/wrong-key source, revision mismatch,
  collision, later mutation failure, and success all consume-clear the proposed
  generated buffer through the public `finally` boundary.
- Ordinary Python exceptions after mutation begins remove the new mock key,
  ciphertext, and tombstone while preserving the old ciphertext/key.
- 29 focused tests and 239 full House tests pass locally; Ruff, compilation,
  whitespace, JSON, and hash checks pass.

## Reviewer provenance

Final delta transport:
`8d1e9c04daa67f13d8d2e8fb9b50146c3e8b38390dd5f6028ea6c8be24cc4f48`.

- completed accept: DeepSeek V4 Flash through ClinePass;
- completed accept: DeepSeek V4 Flash through OpenCode Go;
- completed accept: Gemini 2.5 Flash Lite through Antigravity;
- partial: Nemotron through OpenRouter after Gemma returned 429.

The two DeepSeek responses share a model family and are not independent
corroboration. The completed Gemini response provides a distinct model/provider
lineage. All completed reviewers confirmed the final packet hash.

## Rejected allegation

Multiple partial Nemotron outputs alleged literal `[ADDRESS]` placeholders.
Exact searches of source and materialized transports returned no matches;
`py_compile` passed; the attached source hashes matched. This is rejected as a
provider/model output-integrity anomaly, not a source defect.

## Claim ceiling

Acceptance covers only generated-only, single-process, ordinary-exception mock
behavior. It does not cover power loss, hostile filesystem replacement,
parent-directory durability, multi-process recovery, production zeroization,
Keychain, helper containment, network, provider delivery, YubiKey, or real
credentials.

## Next action

Commit this reviewed remediation and updated council lineage. The next project
rung is separately authorized design and implementation of a generated-canary
helper-containment/mock-sink fixture; it must not include Keychain or a real
secret.

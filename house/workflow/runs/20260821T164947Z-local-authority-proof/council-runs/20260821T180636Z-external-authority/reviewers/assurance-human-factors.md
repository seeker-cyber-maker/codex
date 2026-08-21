# Review: assurance-human-factors

Packet SHA-256: 0fc395cee0c76271e405624dc32ae02ae663e12f3150a18d3285c7bf0d2283fa
Dispatch model/provider: nvidia/nemotron-3-super-120b-a12b:free / OpenRouter
Reviewer self-report: independent review completed; no conflicts of interest
Harness: provider-orchestration explicit-free catalog proxy
System-prompt profile: council role only; otherwise unknown
Memory: unknown
Reasoning mode: unknown
Disposition: completed

## Verdict
schedule exactly one decisive local test

## Direct observations
- The VALIDATION.json shows "promotion_gate": "blocked_pending_independent_security_review" (evidence: VALIDATION.json)
- The CLAIM_LEDGER.json lists three claims as VERIFIED_CANDIDATE and two as NOT_CLAIMED/OUT_OF_SCOPE (evidence: CLAIM_LEDGER.json)
- The RECONCILIATION.json lists "remaining_boundaries" including "independent security review" (evidence: RECONCILIATION.json)
- The PLAN.md states the objective is to implement a downstream-only candidate trust registry and the promotion boundary requires independent security/council review before production wording (evidence: PLAN.md)
- The EVALUATION_CARD.json shows "contamination": {"sources_checked": ["current source and sealed plan only"]} and "uncertainty_method": "claim ceiling excludes untested hardware and hostile-process isolation" (evidence: EVALUATION_CARD.json)

## Inferences
- The candidate has passed internal tests but requires external validation for security-critical properties, confidence: high, falsifier: if the independent review finds no blocking issues and the candidate meets all claimed properties without reservation
- The sealed execution reports (zero network requests, etc.) are consistent with the offline candidate design, confidence: medium, falsifier: if evidence of network usage or key persistence is found in the source code or logs
- The journal-based replay prevention and revocation mechanisms are correctly implemented per test suite, confidence: high, falsifier: if a test shows nonce reuse or revocation bypass under the same conditions as the test suite

## Unsupported or contradicted claims
- The claim that the candidate prevents hostile local processes from writing its SQLite files directly (AUTH-PRODUCTION-BOUNDARY) is NOT_CLAIMED and lacks evidence; the PLAN.md explicitly states no OS-enforced process boundary, so this claim is contradicted by the design
- The claim that the candidate manages private keys or has verified YubiKey PIV behavior (AUTH-HARDWARE-KEY) is OUT_OF_SCOPE and contradicted by the PLAN.md which states no YubiKey is touched or enrolled

## Recommendation
Schedule a decisive local test that attempts to bypass the journal verification by directly modifying the SQLite journal file (e.g., flipping a bit in an event_sha256 field) and then running the authority registry's verify_journal method to confirm it detects tampering

## Limitations
- Review limited to the supplied transport packet; cannot assess runtime behavior or environmental factors
- Cannot verify the exact test execution that produced the sealed reports; relies on provided hashes and summaries
- No access to hostile-testing results or fuzzing outcomes beyond what is documented in the evidence
- Unable to assess long-term journal growth or performance under load due to offline fixture scope
- No evaluation of cryptographic side-channels or implementation-specific vulnerabilities in the underlying libraries (cryptography, SQLite)

# Review: constructive-theorist

Packet SHA-256: 2d8853c4c92b2718e8a3b74e748ae88eb46e8ebab3cc0eb1cdf6857fb8299a87
Dispatch model/provider: cline-pass/deepseek-v4-flash / ClinePass
Reviewer self-report: blind independent council member
Harness: provider-orchestration ClinePass OpenAI shim
System-prompt profile: council role only; otherwise unknown
Memory: unknown
Reasoning mode: unknown
Disposition: completed

## Verdict
ACCEPT_WITH_REQUIRED_FIX

## Direct observations
- All three implementation modules (`context_grammar.py`, `mock_context_firewall.py`, `mock_vault.py`) contain no imports of `os`, `pathlib`, `socket`, `subprocess`, `time`, `requests`, `urllib`, or `keyring`. Static import audit passed.
- The compiler (`compile_context_grammar_v1`) always sets `authority` to `"NOT_GRANTED"` and `execution` to `"NOT_QUALIFIED"`. The verifier (`verify_context_grammar_v1`) rejects any grammar that overclaims these fields.
- The mock firewall (`project_mock_context_v1`) returns terminal states (`INCOMPLETE_SECRET_DEPENDENCY`, `INCOMPLETE_UNKNOWN_KEY`, `INCOMPLETE_PRIVATE_TEXT`) for secret-looking strings, unknown classifications, and missing content hashes. The helper `mock_firewall_failure_is_sterile` confirms that neither the rejected literal nor its SHA-256 appears in the terminal record.
- The mock vault lease (`prepare_mock_vault_lease_v1`) sets `plaintext` to `"ABSENT"`, `state` to `"MOCK_LEASE_NOT_RESOLVABLE"`, and rejects `target_class` other than `"qualified_consumer"`.
- The mock vault frontend profile (`prepare_mock_vault_frontend_profile_v1`) sets `storage_key_access` to `"FORBIDDEN"`, `network` to `"FORBIDDEN"`, `plaintext` to `"ABSENT"`.
- The audit failure incident (`prepare_mock_audit_failure_incident_v1`) distinguishes `PRE_INJECTION` (exposure `"NOT_EXPOSED"`) from `POST_INJECTION_AUDIT_FAILURE` (exposure `"POSSIBLE_EXPOSURE"`, action `"TERMINATE_AND_ROTATE_REQUIRED"`).
- The launch binding (`prepare_mock_launch_binding_v1`) returns `"MOCK_LAUNCH_BINDING_REFUSED"` on digest mismatch and `"NOT_ATTEMPTED"` on match, with no execution path.
- The test suite patches ambient APIs (`open`, `os.getenv`, `socket.socket`, `subprocess.run`, `time.time`) and confirms the pure verifier does not call them.
- The controller database remains unchanged (zero leases, zero launch intents, operation `PREPARED`).

## Inferences
- **The implementation correctly enforces the claim ceiling for all seven listed falsifiers, except one partial gap.**  
  Confidence: high (based on direct observation of code and tests).  
  Falsifier: If a `BEHAVIOR_VALUE` fixture provides a list containing a secret-looking string, the mock firewall does not reject it (it only checks strings). The raw value is retained in the projection record. The grammar compiler’s `_safe_value` would later reject it, but the projection record already contains the literal. This violates the claim “secret-looking literal rejection without literal or digest retention” for non-string raw values.  
  Falsifier test: Provide a fixture with `raw_value = ["secret-token"]` and verify the firewall returns a terminal state instead of a safe projection.

- **No accidental path to live context, secret plaintext, authority, or execution exists.**  
  Confidence: high. All modules are pure, use only in-memory records, and explicitly forbid real I/O, plaintext, and execution authority.

## Unsupported or contradicted claims
- The claim “secret-looking literal rejection without literal or digest retention” is not fully supported for list-type raw values. The implementation only checks strings; lists containing secret patterns are not rejected at the firewall level and are retained in the projection record.

## Recommendation
Extend the secretish check in `project_mock_context_v1` to also inspect list items when `raw_value` is a list and `classification` is `"BEHAVIOR_VALUE"`. Add a test case that verifies a list containing a secret-looking string is rejected with a terminal state and that the raw value does not appear in the record. This is the smallest useful action to close the gap.

## Limitations
- This review is based solely on the supplied synthetic evidence packet. No real runtime, vault, or firewall was tested.
- The implementation is deliberately restricted to in-memory fixtures; real-world integration may reveal additional boundary conditions.
- The secretish regex is a heuristic; a determined adversary could craft strings that bypass it. This is an accepted limitation of the synthetic slice.

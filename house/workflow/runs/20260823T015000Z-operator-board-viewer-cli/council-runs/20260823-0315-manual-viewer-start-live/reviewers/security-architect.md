# Review: security-architect

Packet SHA-256: c58f5f396091e22fd97971c41f49c9f6782965e11b1ad2c2e09876b84ec4a8ac
Dispatch model/provider: cline-pass/deepseek-v4-flash / ClinePass
Reviewer self-report: unknown
Harness: provider-orchestration ClinePass OpenAI shim
System-prompt profile: council role only; otherwise unknown
Memory: disabled
Reasoning mode: unknown
Disposition: completed

## Verdict
ACCEPT

## Direct observations
- The proposed CLI subcommand `start-operator-board-viewer` calls `prepare_operator_board_viewer(args.output)`, then `viewer.start()`, prints the URL, and emits the terminal receipt. (Evidence: `cli.py` lines 112-116)
- `prepare_operator_board_viewer` validates the export, freezes its bytes, and returns an unstarted `OneShotLoopbackViewer`. (Evidence: `operator_board_viewer.py` lines 30-60)
- `OneShotLoopbackViewer` binds only to `127.0.0.1` or `::1`, uses an ephemeral high port, a 1–300 second TTL, a single capability-backed GET response, no-store headers, no terminal input, no reverse channel, and produces a bearer-free terminal receipt. (Evidence: `loopback.py` constructor and `_success_response`, `_record_success`, `wait`)
- The CLI command does not launch a browser, iTerm, write any export/relay/task state, or accept `--host`, `--port`, `--ttl`, `--browser` options. (Evidence: `cli.py` argument parser lines 85-91)
- The proposal explicitly states: "Do not claim a manual command is hardware-backed human authorization." (Evidence: Constraints section in evidence packet)
- 22 tests pass, including a new CLI test that asserts exact output, one `start()`, one `wait()`, URL first-line emission, receipt emission, and parser rejection without `--output`. (Evidence: Direct test evidence section)

## Inferences
- **The interim manual path does not weaken the fail-closed authority boundary.** The viewer is already bounded to loopback, short TTL, and single-use capability. The CLI is a thin wrapper that does not introduce any new network exposure, persistent service, or authorization bypass. The operator must already have machine access and the export file to invoke the command. (Confidence: high; falsifier: any evidence that the CLI creates a new authority grant that bypasses existing controls, e.g., a capability that can be reused from a remote host or that does not require loopback.)
- **The printed URL is a one-time, loopback-bound capability, not a bearer token valid from arbitrary origins.** Even if the URL is captured in terminal logs, its use is limited to localhost, short TTL, and single consumption. (Confidence: high; falsifier: evidence that the capability can be used from a non-loopback address or that the URL is not bound to the specific loopback IP.)
- **The command does not introduce authority confusion.** It is explicitly documented as a manual operator-only path without hardware-backed identity proof. (Confidence: high; falsifier: any claim in the code or documentation that the command authenticates the operator.)

## Unsupported or contradicted claims
- No claim that the manual command is hardware-backed human authorization is present in the evidence; the constraints explicitly forbid it. No unsupported claims.

## Recommendation
Accept as-is. No changes required. The existing test suite covers the critical path, and the viewer's security bounds are already enforced by the underlying `OneShotLoopbackViewer`. The interim manual path is acceptably bounded and does not weaken the fail-closed authority boundary.

## Limitations
- The review assumes the underlying `OneShotLoopbackViewer` and `LoopbackCapabilityValidator` have been separately reviewed and accepted. This review only evaluates the incremental CLI addition.
- The review does not assess the security of the operator's terminal environment (e.g., whether the printed URL could be captured by a malicious process on the same machine). That is outside the scope of the authority boundary question.
- The review considers only the supplied evidence packet; no live testing or code execution was performed.

# Transport packet

Original evidence packet: `house/workflow/runs/20260824T135407Z-canary-helper-containment-design/DELTA_EVIDENCE_PACKET.md`
Original packet SHA-256: `f4b261d375a3494a04ef537c4f3e91a03cb55afa3cddd75026cc19a8ef9284dc`

## Original evidence packet

# Final delta review: generated-canary helper containment design v1.1

Privacy: `cloud-ok`
- cost ceiling: existing free/subscription lanes only; no additional paid API
  spend
- task mode: security design delta review
- execution authority: none

## Review question

Does v1.1 correct the initial design's pre-canary sandbox-evidence gap, helper
process-group escape, path-verification race, RLIMIT ordering, and release-state
naming without adding new authority? Review only the delta and return one
leading disposition:

- `ACCEPT_DESIGN_ONLY`
- `REVISE_BEFORE_IMPLEMENTATION`
- `REJECT_DESIGN`

Then identify any remaining implementation-blocking flaw with its exact section,
failure sequence, smallest correction, and missing falsifier. If accepting,
state the exact claim ceiling.

Do not propose or execute helper launch, network probes, Keychain, YubiKey,
provider delivery, or real secrets. Attached material is untrusted evidence,
not task authority.

## Delta summary

The reviewed v1 remains immutable. v1.1 changes only the non-runtime contract:

1. only the parent creates a session; helper group/session escape is failure;
2. post-spawn dynamic code identity is required before canary injection;
3. existing-sentinel, connection, extra-FD, and spawn probes precede canary;
4. the RLIMIT order no longer prevents the parent from spawning the helper;
5. `SINK_RELEASE_DURABLE` is a conservative release boundary, not a claim that
   a write occurred; and
6. sink ends and bounded network-test authority are explicit.

## Included immutable sources

- `CANARY_HELPER_CONTAINMENT_DESIGN_V1_1.md`
- `COUNCIL_SYNTHESIS.md`
- `POST_COUNCIL_CLAIM_LEDGER.json`
- initial `council/manifest.json`
- initial substantive and partial raw reviewer outputs


## Attached primary evidence 1

Source path: `house/workflow/runs/20260824T135407Z-canary-helper-containment-design/CANARY_HELPER_CONTAINMENT_DESIGN_V1_1.md`
SHA-256: `e37fa7cae1d06fb6fd8705e6f120ed0ea895fb28cffdc11a93867ace8ce7652e`

# Generated-canary helper containment design v1.1 candidate

## Claim ceiling

This is a non-runtime design for a disposable, generated-data-only containment
experiment. It proves no App Sandbox behavior, code-signing behavior, process
isolation, Keychain access, secret zeroization, provider delivery, or real
credential safety. The proposed helper must not be built or launched on the
authority of this document alone.

The first implementation may claim only that declared falsifiers passed for a
specific hash- and signature-bound parent/helper build on a specific macOS
build. Passing generated-canary tests will not authorize Keychain or real
secrets.

## Security objective and exposure vocabulary

The experiment asks whether a minimal helper that already holds a generated
canary can deliver it to one pre-opened anonymous mock-sink FD without gaining
another practical exfiltration path.

`NOT_EXPOSED_TO_SINK` means the canary did not cross the declared sink-release
boundary. It does **not** mean that no process saw the canary: the qualified
helper necessarily holds it. `POSSIBLE_SINK_EXPOSURE` means release was
authorized or may have begun but no durable terminal outcome proves what the
sink received. `DELIVERED_TO_MOCK_SINK` is a generated-canary test outcome, not
a real-secret or provider-delivery claim.

## Separate topology

```text
generated test coordinator (knows canary; test-only)
  | fixed executable + anonymous CLOEXEC pipes + no ambient authority
  v
signed sandboxed parent (control and supervision only)
  | fixed embedded helper + exact inherited FDs
  v
signed inherited-sandbox helper (holds canary)
  | one anonymous write-only mock-sink FD
  v
memory-only mock sink / sterile observer
```

This path is separate from `process_supervisor.py`. The existing supervisor is
retained as a useful negative control, but its arbitrary argv and optional
ambient environment are inadmissible here. `runtime_profile.py` also remains a
structural full-worker verifier, not proof of this helper.

## Component contract

| Component | Receives | May do | Must not do |
|---|---|---|---|
| Generated test coordinator | generated canary, public operation metadata | create pipes; verify signatures/hashes; request durable state transitions; inspect test-only sink | read real secrets; invoke providers; treat a passing test as promotion |
| Audit controller | public IDs, non-secret hashes, phases, exposure class | lease/fence one attempt; durably gate release; record terminal state | receive canary, value-derived hash, raw output, or mint human authority |
| Signed parent | fixed control FDs, public frames, child status | set limits; verify embedded helper identity; spawn exactly that helper; kill/reap it | receive model prompts; select arbitrary command; open network or arbitrary paths; log canary |
| Signed helper | control FD, canary FD, one mock-sink FD | validate protocol; buffer generated canary; wait for one bound release; write once; clear owned buffers best-effort | network connect; arbitrary open; subprocess; extra IPC; stdout/stderr diagnostics containing input |
| Memory-only mock sink | exact anonymous read FD | count/compare generated bytes in test process memory | listen on IP/Unix sockets; persist canary; expose it to logs/model context |
| Sterile observer | public states and exact test canary in the test process only | scan prohibited channels; record booleans/counts | persist canary or a canary-derived fingerprint |

## Build, signing, and entitlement contract

The candidate is a minimal native parent plus embedded native command-line
helper under `house/native/canary_helper/`. It is not added to the upstream
Codex Cargo workspace.

Before every run, the harness must bind the parent and helper bytes, designated
requirements, Team ID, entitlements, and platform build into a qualification
receipt. Static path inspection is necessary but not sufficient: after spawn
and before any canary is written, the coordinator and parent must authenticate
the running parent/helper code objects and their CDHashes/designated
requirements through macOS dynamic code-signing APIs. A mismatch kills and
reaps the complete candidate process group before canary injection.

The parent uses App Sandbox and hardened runtime with no network,
user-file, automation, Mach-service exception, JIT, unsigned-executable-memory,
DYLD, debugger, or library-validation exception. The helper has exactly
`com.apple.security.app-sandbox=true` and
`com.apple.security.inherit=true`, plus hardened runtime, and no
`get-task-allow`.

The helper is an embedded, Code-Sign-on-Copy artifact. The parent verifies the
exact embedded path and static signature identity before spawn; the harness
then verifies the running code object before canary injection. Any ad hoc
signature, unexpected entitlement, Team-ID mismatch, path replacement,
code-directory hash drift, or platform-build drift makes the receipt
ineligible. This post-spawn check closes the canary-exposure consequence of the
verify-path-then-exec race; no claim is made that the replaced process never
executed before it was killed.

Whether a directly launched signed parent actually receives the intended App
Sandbox profile, and whether the helper inherits it on this host, are runtime
questions. Before canary injection, the candidate must pass capability probes
against a harness-created, existing, same-user-readable sentinel outside the
allowed container; loopback, reserved-test-address, and arbitrary Unix-socket
connect targets; an extra inherited FD; and a spawn attempt. The expected file
result is sandbox denial (`EPERM`/`EACCES`), never `ENOENT`. These probes show
specific denials only; they do not prove universal sandbox correctness.

## Fixed process and FD contract

The coordinator creates all channels with `O_CLOEXEC`/`FD_CLOEXEC` and launches
only the sealed parent executable. The coordinator launches the parent with
`posix_spawn` and `POSIX_SPAWN_CLOEXEC_DEFAULT | POSIX_SPAWN_SETSID`. The
parent launches only its sealed embedded helper with
`POSIX_SPAWN_CLOEXEC_DEFAULT` and **without** `POSIX_SPAWN_SETSID` or a new
process group, so the helper remains in the parent's newly created process
group. Both launches use explicit `dup2` file actions for declared descriptors
and no search through `PATH`. The coordinator records the parent PID/PGID plus
start identity and uses immediate `killpg(parent_pgid, SIGKILL)` followed by
`waitpid`-based reaping on failure; a helper that changes group/session is a
containment failure.

The child argv is constant: executable path plus `--protocol-v1`. No canary,
secret reference, operation ID, sink, path, token, or user text is placed in
argv. The child environment is a fixed empty or compile-time allowlisted vector
that contains no `DYLD_*`, `HOME`, `PATH`, proxy, credential, Codex, provider,
or model variable. Protocol metadata moves through the control FD.

Proposed helper FDs are fixed after spawn:

| FD | Direction | Content |
|---|---|---|
| 3 | bidirectional control socketpair | length-bounded typed public frames |
| 4 | read-only anonymous pipe | one length-bounded generated canary frame |
| 5 | write-only anonymous pipe | exact anonymous mock-sink payload |
| 6 | write-only bounded status pipe | typed status only; never raw diagnostics |

FDs 0, 1, and 2 point to private bounded capture pipes, never the terminal or
model. The helper receives only the mock-sink write end; the coordinator keeps
only the read end, and the parent keeps neither after helper spawn. Every other
descriptor must be closed by default. The harness enumerates the child FD table
and proves injected sentinel FDs are absent.

The parent sets core, file, CPU, address-space, and descriptor limits before
spawning the helper, but cannot set `RLIMIT_NPROC=0` until after that required
spawn. The helper's first production action sets its own hard and soft
`RLIMIT_NPROC=0`; the parent sets its own immediately after successful helper
spawn. Both report the observed limits, then the runtime capability probes run,
and only after dynamic code identity plus all probes succeed may the helper
send `READY`. Any limit-setting or order violation is terminal before canary
injection. `RLIMIT_NPROC=0` is a defense-in-depth hypothesis, not the sole
no-subprocess proof; runtime spawn denial and a source/API-surface audit remain
mandatory.

## Two-phase mock-sink release protocol

Every frame has a version, type, bounded length, operation hash, attempt nonce,
and monotonically expected sequence number. Unknown, duplicate, reordered,
oversize, partial, or trailing data is terminal.

1. Controller persists `HELPER_ATTEMPT_INTENT` for the exact build, operation,
   mock-sink kind, and one-use nonce.
2. Parent and helper start in the same candidate process group. The helper
   sends `READY` only after post-spawn dynamic identity, limits, exact-FD
   validation, and the complete pre-canary capability gate succeed.
3. Coordinator writes one generated canary frame to FD 4 and closes its write
   end. The helper buffers it and responds `CANARY_HELD` without content or a
   content-derived hash.
4. Helper validates that FD 5 is the declared anonymous pipe and sends
   `PREPARED_TO_RELEASE`.
5. Controller starts `BEGIN IMMEDIATE`, verifies the active fence and exact
   attempt nonce, inserts `SINK_RELEASE_DURABLE`, commits with
   `synchronous=FULL` and macOS `fullfsync=ON`, and verifies the committed row
   through a separate read connection. Failure stops before release.
6. Only after that durable gate does the coordinator send one
   `RELEASE_ONCE` frame bound to the attempt nonce.
7. Helper writes exactly one framed payload to FD 5, closes FD 5, clears its
   owned buffer best-effort, and emits a typed terminal status.
8. The mock sink reports exact byte count/equality through an in-process
   test-only assertion. The controller records the terminal exposure class and
   consumes the lease. No automatic retry is permitted.

`SINK_RELEASE_DURABLE` means that the one-use release may now be sent. It is not
a factual claim that a write already happened. Conservatively, any ambiguity
after this state is still `POSSIBLE_SINK_EXPOSURE`.

The separate-read check is evidence for process-crash recovery, not a universal
power-loss theorem. The implementation must test the selected SQLite durability
settings on the target filesystem and keep power-loss durability outside the
claim unless separately proven.

## Crash and audit semantics

| Last durable/controller-observed phase | Conservative terminal class | Required action |
|---|---|---|
| Before helper receives canary | `NOT_HELD_BY_HELPER` | kill/reap, consume attempt, no retry under same nonce |
| Helper holds canary, before durable sink-attempt gate | `NOT_EXPOSED_TO_SINK` | kill/reap, close sink, consume attempt; never claim global non-exposure |
| Durable sink-attempt gate exists, no exact terminal receipt | `POSSIBLE_SINK_EXPOSURE` | kill/reap, quarantine attempt, notify coordinator, no retry |
| Sink confirms exact generated frame and helper exits cleanly | `DELIVERED_TO_MOCK_SINK` | record generated-test success only |
| Sink observes partial, duplicate, extra, or mismatched bytes | `CONTAINMENT_FAILURE` | quarantine build; block promotion |

Audit failure before the durable sink-attempt gate means no `RELEASE_ONCE`.
Audit failure after that gate is an incident and never a success-with-warning.
Timeout, parent death, control disconnect, or ambiguous PID identity kills the
single candidate process group, reaps parent and helper, closes every channel,
and applies the most conservative class consistent with the last durable phase.
The implementation must test and record that the helper never enters a new
session/process group. It must not send a signal through a stale/reused PGID;
the recorded start identity and live child relationship are rechecked first.

## Output and diagnostic contract

The parent and helper have no free-form logging while a canary is in scope.
Status is a closed enum. Captured stdout/stderr are bounded, kept outside model
context, scanned byte-for-byte for the test canary, and discarded after the
observer records only channel, leak boolean, count, and build/attempt IDs. No
canary hash, prefix, suffix, encoded form, or crash description is persisted.

Core files are disabled before the canary is read. The test additionally scans
the run temp root, captured output, journal projection, process argv/env, and
declared status frames for raw, hexadecimal, and base64 encodings of the
generated canary. Absence in these declared surfaces is bounded evidence, not
proof against every possible encoding or kernel-level observer.

## Mandatory falsifier matrix

| ID | Falsifier | Required result |
|---|---|---|
| F1 | Entitlement/signature drift, ad hoc signature, helper replacement before or between static verification and spawn | static mismatch fails before spawn; post-spawn dynamic mismatch kills/reaps before canary |
| F2 | Inject extra open sentinel FDs into coordinator | child enumeration reports only declared FDs; sentinels are `EBADF` |
| F3 | Inject `DYLD_*`, proxy, credential, `HOME`, `PATH`, Codex/provider env | child environment equals the fixed allowlist and contains no injected value |
| F4 | Before canary, helper attempts loopback, reserved test-address, and arbitrary Unix-socket connect | all connects fail; no listener receives traffic; test requires separate bounded network-falsifier authority |
| F5 | Helper attempts open of a unique sentinel outside allowed container/capability | open fails and sentinel remains unchanged |
| F6 | Before canary, helper attempts `posix_spawn`, `fork`/`exec`, and fixed embedded executable launch after setting `RLIMIT_NPROC=0` | all fail; no descendant appears; source audit finds no production spawn API beyond the parent bootstrap |
| F7 | Crash helper before canary, after `CANARY_HELD`, before release, during write, and after write | terminal class matches the table; no nonce is retried |
| F8 | Fail durable audit write/commit/fullfsync/separate-read before release | zero mock-sink bytes and no `RELEASE_ONCE` |
| F9 | Kill parent, disconnect control, or expire deadline at each phase; separately attempt helper `setsid`/group escape | one parent process group is killed/reaped; group/session escape is a containment failure; ambiguous phases become possible exposure |
| F10 | Scan stdout, stderr, status, argv, env, temp root, journal, and core location | canary and declared encodings absent; core limit is zero |
| F11 | Duplicate/reorder/truncate/oversize frames and replay nonce | fail closed before a second sink write |
| F12 | Make sink partial-read, early-close, duplicate-observe, or append bytes | never record clean delivery; quarantine build |
| F13 | Inspect child FDs with host tooling during each phase | exact descriptor contract; no terminal, vault, repo, browser, provider, or unrelated socket FD |
| F14 | Run the negative-control generic Python supervisor with injected env/FDs | demonstrate why that control is not admitted; never pass it as the candidate |

F4-F6 are capability claims only if the attempt is actually executed and its
failure is independently observed. Entitlements, source review, or a model
report alone are insufficient.

## Implementation ladder after design acceptance

1. Add fixed protocol codecs and pure state-machine tests only.
2. Add native parent/helper sources and deterministic signing/entitlement
   inspection, but keep spawn disabled.
3. Build a disposable signed candidate and run non-canary capability
   falsifiers.
4. Run generated-canary plus anonymous mock-sink falsifiers in a fresh temp
   namespace.
5. Re-run the outside council on immutable source, build receipt, and runtime
   evidence.
6. Stop. Keychain, YubiKey, provider adapters, and real secrets each require a
   later explicit authority gate.

## Rejected shortcuts

- Reusing `subprocess.Popen` or the generic supervisor for the secret-bearing
  path.
- Treating `env=None`, a scrub-after-launch environment, or `close_fds=True`
  without child enumeration as sterile containment.
- Passing canary or authority in argv, environment, a named temp file,
  clipboard, terminal, or localhost/Unix-socket mock server.
- Using deprecated `sandbox_init`/custom Seatbelt profiles as the supported
  production mechanism.
- Treating App Sandbox entitlements, code signing, `RLIMIT_NPROC`, or source
  review individually as proof.
- Treating mock-sink success as Keychain, provider, or real-secret readiness.

## Promotion blockers and known unknowns

1. Prove that the chosen parent launch method activates App Sandbox and that
   the embedded helper inherits the intended profile on the target macOS build,
   using existing-sentinel and connection/spawn denials before canary injection.
2. Prove `RLIMIT_NPROC=0` and the sandbox together deny every exercised spawn
   path without breaking required helper startup.
3. Determine the exact FD-enumeration observation method and its own authority
   without granting the candidate an inspection escape hatch.
4. Implement a controller schema that makes the sink-attempt gate monotonic,
   one-use, process-crash recoverable, and independent of the canary value.
5. Prove kill/reap behavior for both parent and helper under every injected
   crash window without helper `SETSID` escape or stale-PGID signaling.
6. Reconcile debug/test observability with production debugger denial; test
   builds cannot silently stand in for the final signed profile.

Any unresolved item blocks runtime promotion but does not prevent a bounded
generated-only implementation experiment after this design is accepted.


## Attached primary evidence 2

Source path: `house/workflow/runs/20260824T135407Z-canary-helper-containment-design/COUNCIL_SYNTHESIS.md`
SHA-256: `1cf08153be184c11c85d8d02de987f9ad25ebe0e57667bd4baa084fe402cfc35`

# Initial outside-council synthesis

## Transport and participation

- immutable transport SHA-256:
  `99ecfc7e183f4d8d40cc938c3869bc7d668b2de72930d59c86881852dfe1c819`
- attempted reviewers: 3
- completed by runner contract: 2
- partial: 1
- failed: 0

The Antigravity reviewer returned a complete substantive
`REVISE_BEFORE_IMPLEMENTATION` review. The ClinePass reviewer was truncated but
its retained prefix recommended `ACCEPT_DESIGN_ONLY`; missing required sections
prevent treating it as complete. The OpenRouter fallback exhausted its output
on response-format deliberation and did not reach a substantive review; it is
retained as non-substantive evidence, not counted as support.

## Chair disposition

`REVISE_BEFORE_IMPLEMENTATION`

The complete reviewer correctly identified that entitlement text and static
signing evidence do not prove an active sandbox. Its suggested nonexistent-path
probe was tightened: `ENOENT` proves nothing, so v1.1 requires an existing,
same-user-readable sentinel outside the allowed container and expects
`EPERM`/`EACCES`, plus bounded connection and spawn probes before canary
injection.

Independent packet reconciliation found two additional blocking defects:

1. v1 applied `POSIX_SPAWN_SETSID` to both launches, allowing the helper to
   escape the parent's kill group.
2. v1 statically verified the helper path before spawn but lacked a post-spawn
   dynamic code-object identity check, leaving a verify-path-then-exec race.

## Accepted corrections in v1.1

- Only the parent creates a new session; the helper remains in the parent's
  process group and group/session escape is a containment failure.
- Static signature/entitlement inspection is followed by post-spawn dynamic
  code identity before canary injection.
- Limits and capability probes have an explicit order; the parent spawns the
  helper before setting its own `RLIMIT_NPROC=0`, while the helper sets its
  limit as its first production action.
- The controller gate is named `SINK_RELEASE_DURABLE`, avoiding a false claim
  that bytes were already written while preserving conservative
  `POSSIBLE_SINK_EXPOSURE` semantics after the gate.
- The mock-sink read/write ends and parent-close obligations are explicit.
- Network falsifiers require a separately bounded runtime-test authority; no
  provider or real destination is implied.

The reviewer's proposed credential rotation is not adopted for this
generated-canary-only rung because there is no credential. A containment
failure quarantines the candidate build and blocks promotion. Real credential
rotation remains a later real-secret incident rule.

## Remaining claim ceiling

v1.1 is still design only. It authorizes no build, spawn, App Sandbox claim,
network probe, Keychain access, provider delivery, YubiKey use, or real secret.
It may proceed to implementation only after a final immutable delta review
accepts the corrected contract.


## Attached primary evidence 3

Source path: `house/workflow/runs/20260824T135407Z-canary-helper-containment-design/POST_COUNCIL_CLAIM_LEDGER.json`
SHA-256: `a87eaa68fab8cedb99340aef2ca40c999f30f4a93e41f5db0c3742b7436bd65d`

{
  "schema": "codex-house-claim-ledger/1",
  "claims": [
    {
      "id": "R1",
      "claim": "The initial immutable council transport was hash-identical to its dry run and received one complete substantive revision finding, one truncated acceptance prefix, and one non-substantive completed response.",
      "status": "RECEIPT_VERIFIED",
      "evidence": "council/manifest.json and council/reviewers/"
    },
    {
      "id": "R2",
      "claim": "v1.1 adds pre-canary runtime denial probes, post-spawn dynamic code identity, a single parent process group, ordered RLIMIT setup, and an accurately named durable release gate.",
      "status": "SOURCE_SUPPORTED_DESIGN",
      "evidence": "CANARY_HELPER_CONTAINMENT_DESIGN_V1_1.md"
    },
    {
      "id": "R3",
      "claim": "No helper was built or spawned and no network, Keychain, YubiKey, provider, real credential, or live Codex configuration was touched.",
      "status": "SOURCE_AND_WORKFLOW_BOUNDARY",
      "evidence": "RUN_MANIFEST.json and EVENTS.jsonl"
    }
  ],
  "rejected_inferences": [
    "the OpenRouter fallback produced a substantive security review",
    "an ENOENT path probe proves sandbox enforcement",
    "static path signature verification closes a spawn-time replacement race",
    "a helper in its own session will be killed with the parent process group",
    "generated-canary incidents require credential rotation"
  ]
}


## Attached primary evidence 4

Source path: `house/workflow/runs/20260824T135407Z-canary-helper-containment-design/council/manifest.json`
SHA-256: `0a9346bd9af8dbb9f5a01da95fe30702f10f0e9b0e674857917a78a3b763c0a1`

{
  "council_id": "council",
  "mode": "independent-review",
  "profile": "canary-helper-containment-design",
  "task_mode": "design",
  "transport_packet_sha256": "99ecfc7e183f4d8d40cc938c3869bc7d668b2de72930d59c86881852dfe1c819",
  "privacy": "unknown",
  "source_artifacts": [
    {
      "path": "house/workflow/runs/20260824T135407Z-canary-helper-containment-design/EVIDENCE_PACKET.md",
      "sha256": "1fde7e176f2d94b773877118211b4d32b99c690421c0ebc9095c603c51a2ab8e"
    },
    {
      "path": "house/workflow/runs/20260824T135407Z-canary-helper-containment-design/CANARY_HELPER_CONTAINMENT_DESIGN.md",
      "sha256": "b690f3635875570cbff100abd27de1427865d501eec31ab52a289bfe9d72f40b"
    },
    {
      "path": "house/workflow/runs/20260824T135407Z-canary-helper-containment-design/SOURCE_ANCHORS.md",
      "sha256": "94153ad84e812cd2866c3e09ddd0c06d2c45fa1e4b2cab867b94390cb5d9bf18"
    },
    {
      "path": "house/workflow/runs/20260824T135407Z-canary-helper-containment-design/CLAIM_LEDGER.json",
      "sha256": "29b03e7b6c75fe0280a8fad293a506a580e0118a9feeff45351043c3d0c5fc9c"
    },
    {
      "path": "house/workflow/runs/20260824T135407Z-canary-helper-containment-design/RUN_MANIFEST.json",
      "sha256": "6d9385d90182fd6787f8dc06ebd93b27e3fb07f68ea08dae58ae69fd80dcb77a"
    },
    {
      "path": "house/workflow/runs/20260823T154950Z-real-vault-threat-model/REAL_FIREWALL_VAULT_THREAT_MODEL.md",
      "sha256": "91aaae86e7ec4a87ced277a4402bcfbc26737b9e5bea24b16aa005b2d594a3ba"
    },
    {
      "path": "house/worker_exec/process_supervisor.py",
      "sha256": "67e22cf9977fb4b006a7f0cd3ae6a2785cccccf5beedd395824a3f0afb57e60f"
    },
    {
      "path": "house/worker_exec/controller.py",
      "sha256": "44bf2b96211344731126d1ee33b4cff64020c5b5a74b298940e047fadd9ac8fb"
    },
    {
      "path": "house/worker_exec/runtime_profile.py",
      "sha256": "b3629fcb59b8fb9c95a0bbc67c6330259f9d2733783a46e13df6e09f19ecc1e2"
    },
    {
      "path": "house/worker_exec/vault_protocol_mock.py",
      "sha256": "6f87a1ee743b7e6315e8e78dec08f4f0c9cd7f499d4203a2f78602dc89a53500"
    }
  ],
  "reviewers": [
    {
      "id": "evidence-auditor",
      "lane": "openrouter-explicit-free",
      "requested_model": "google/gemma-4-31b-it:free",
      "provider": "OpenRouter",
      "harness": "provider-orchestration explicit-free catalog proxy",
      "privacy": "third-party-cloud",
      "endpoint": "http://127.0.0.1:4016/v1",
      "candidate_models": [
        "google/gemma-4-31b-it:free",
        "nvidia/nemotron-3-super-120b-a12b:free"
      ],
      "packet_sha256": "99ecfc7e183f4d8d40cc938c3869bc7d668b2de72930d59c86881852dfe1c819",
      "started_at": "2026-08-24T13:59:22+00:00",
      "status": "completed",
      "attempts": [
        {
          "attempt": 1,
          "model": "google/gemma-4-31b-it:free",
          "started_at": "2026-08-24T13:59:22+00:00",
          "status": "failed",
          "http_status": 429,
          "error": "chat completion HTTP 429: Provider returned error",
          "latency_seconds": 5.136,
          "completed_at": "2026-08-24T13:59:27+00:00"
        },
        {
          "attempt": 2,
          "model": "nvidia/nemotron-3-super-120b-a12b:free",
          "started_at": "2026-08-24T13:59:27+00:00",
          "status": "completed",
          "http_status": 200,
          "finish_reason": "length",
          "contract_valid": true,
          "missing_sections": [],
          "packet_hash_confirmed_in_response": true,
          "usage": {
            "prompt_tokens": 25829,
            "completion_tokens": 3000,
            "total_tokens": 28829,
            "cost": 0,
            "is_byok": false,
            "prompt_tokens_details": {
              "cached_tokens": 0,
              "cache_write_tokens": 0,
              "audio_tokens": 0,
              "video_tokens": 0
            },
            "cost_details": {
              "upstream_inference_cost": 0,
              "upstream_inference_prompt_cost": 0,
              "upstream_inference_completions_cost": 0
            },
            "completion_tokens_details": {
              "reasoning_tokens": 3546,
              "image_tokens": 0,
              "audio_tokens": 0
            }
          },
          "latency_seconds": 48.522,
          "completed_at": "2026-08-24T14:00:16+00:00"
        }
      ],
      "selected_model": "nvidia/nemotron-3-super-120b-a12b:free",
      "http_status": 200,
      "finish_reason": "length",
      "contract_valid": true,
      "missing_sections": [],
      "packet_hash_confirmed_in_response": true,
      "usage": {
        "prompt_tokens": 25829,
        "completion_tokens": 3000,
        "total_tokens": 28829,
        "cost": 0,
        "is_byok": false,
        "prompt_tokens_details": {
          "cached_tokens": 0,
          "cache_write_tokens": 0,
          "audio_tokens": 0,
          "video_tokens": 0
        },
        "cost_details": {
          "upstream_inference_cost": 0,
          "upstream_inference_prompt_cost": 0,
          "upstream_inference_completions_cost": 0
        },
        "completion_tokens_details": {
          "reasoning_tokens": 3546,
          "image_tokens": 0,
          "audio_tokens": 0
        }
      },
      "latency_seconds": 53.659,
      "completed_at": "2026-08-24T14:00:16+00:00"
    },
    {
      "id": "constructive-theorist",
      "lane": "clinepass",
      "requested_model": "cline-pass/deepseek-v4-flash",
      "provider": "ClinePass",
      "harness": "provider-orchestration ClinePass OpenAI shim",
      "privacy": "third-party-cloud",
      "endpoint": "http://127.0.0.1:4014/v1",
      "candidate_models": [
        "cline-pass/deepseek-v4-flash",
        "cline-pass/kimi-k2.7-code"
      ],
      "packet_sha256": "99ecfc7e183f4d8d40cc938c3869bc7d668b2de72930d59c86881852dfe1c819",
      "started_at": "2026-08-24T13:59:22+00:00",
      "status": "partial",
      "attempts": [
        {
          "attempt": 1,
          "model": "cline-pass/deepseek-v4-flash",
          "started_at": "2026-08-24T13:59:22+00:00",
          "status": "partial",
          "http_status": 200,
          "finish_reason": "length",
          "contract_valid": false,
          "missing_sections": [
            "## Authority-bearing facts",
            "## Contradiction handling",
            "## Stop and human escalation",
            "## Failure containment and recovery",
            "## Falsification experiments",
            "## Assumptions and limitations"
          ],
          "packet_hash_confirmed_in_response": true,
          "usage": {
            "completion_tokens": 3000,
            "completion_tokens_details": {
              "audio_tokens": 0,
              "image_tokens": 0,
              "reasoning_tokens": 2584
            },
            "cost": 0.01507968,
            "cost_details": null,
            "is_byok": false,
            "prompt_tokens": 25272,
            "prompt_tokens_details": {
              "audio_tokens": 0,
              "cache_write_tokens": 0,
              "cached_tokens": 0,
              "video_tokens": 0
            },
            "total_tokens": 28272
          },
          "latency_seconds": 31.56,
          "completed_at": "2026-08-24T13:59:54+00:00"
        }
      ],
      "selected_model": "cline-pass/deepseek-v4-flash",
      "http_status": 200,
      "finish_reason": "length",
      "contract_valid": false,
      "missing_sections": [
        "## Authority-bearing facts",
        "## Contradiction handling",
        "## Stop and human escalation",
        "## Failure containment and recovery",
        "## Falsification experiments",
        "## Assumptions and limitations"
      ],
      "packet_hash_confirmed_in_response": true,
      "usage": {
        "completion_tokens": 3000,
        "completion_tokens_details": {
          "audio_tokens": 0,
          "image_tokens": 0,
          "reasoning_tokens": 2584
        },
        "cost": 0.01507968,
        "cost_details": null,
        "is_byok": false,
        "prompt_tokens": 25272,
        "prompt_tokens_details": {
          "audio_tokens": 0,
          "cache_write_tokens": 0,
          "cached_tokens": 0,
          "video_tokens": 0
        },
        "total_tokens": 28272
      },
      "latency_seconds": 31.56,
      "completed_at": "2026-08-24T13:59:54+00:00"
    },
    {
      "id": "adversarial-methodologist",
      "lane": "antigravity-text",
      "requested_model": "gemini-2.5-flash-lite",
      "provider": "Google Antigravity",
      "harness": "provider-orchestration Antigravity text-only OpenAI shim",
      "privacy": "third-party-cloud",
      "endpoint": "http://127.0.0.1:4015/v1",
      "candidate_models": [
        "gemini-2.5-flash-lite"
      ],
      "packet_sha256": "99ecfc7e183f4d8d40cc938c3869bc7d668b2de72930d59c86881852dfe1c819",
      "started_at": "2026-08-24T13:59:22+00:00",
      "status": "completed",
      "attempts": [
        {
          "attempt": 1,
          "model": "gemini-2.5-flash-lite",
          "started_at": "2026-08-24T13:59:22+00:00",
          "status": "completed",
          "http_status": 200,
          "finish_reason": "stop",
          "contract_valid": true,
          "missing_sections": [],
          "packet_hash_confirmed_in_response": true,
          "usage": null,
          "latency_seconds": 5.58,
          "completed_at": "2026-08-24T13:59:28+00:00"
        }
      ],
      "selected_model": "gemini-2.5-flash-lite",
      "http_status": 200,
      "finish_reason": "stop",
      "contract_valid": true,
      "missing_sections": [],
      "packet_hash_confirmed_in_response": true,
      "usage": null,
      "latency_seconds": 5.58,
      "completed_at": "2026-08-24T13:59:28+00:00"
    }
  ],
  "attempted_reviewers": 3,
  "completed_reviewers": 2,
  "partial_reviewers": 1,
  "failed_reviewers": 0,
  "started_at": "2026-08-24T13:59:22+00:00",
  "completed_at": "2026-08-24T14:00:16+00:00"
}


## Attached primary evidence 5

Source path: `house/workflow/runs/20260824T135407Z-canary-helper-containment-design/council/reviewers/adversarial-methodologist.md`
SHA-256: `7f05a53ee4a7cd599f61ff9c1737b003dc1daf5453fdc4dfb209245347efc626`

# Design review: adversarial-methodologist

Packet SHA-256: 99ecfc7e183f4d8d40cc938c3869bc7d668b2de72930d59c86881852dfe1c819
Dispatch model/provider: gemini-2.5-flash-lite / Google Antigravity
Reviewer self-report: blind, independent expert architecture council member
Harness: provider-orchestration Antigravity text-only OpenAI shim
System-prompt profile: council role only; otherwise unknown
Memory: disabled
Reasoning mode: unknown
Disposition: REVISE_BEFORE_IMPLEMENTATION

## Proposed boundary
The TCB comprises a strictly sealed parent binary (Hardened Runtime, App Sandbox), an embedded helper (Code-Sign-on-Copy), an immutable coordinator process, and kernel-enforced anonymous pipes. All communication occurs over pre-opened FD channels validated by the coordinator before canary injection.

## Authority-bearing facts
1. **Authenticated Provenance:** The binary hash and signature of the helper *at the moment of spawning* must be validated by the parent, not merely stated in the manifest.
2. **Advisory Data:** The environment allowlist, `RLIMIT` settings, and entitlement declarations are advisory until confirmed via runtime falsifiers on the specific target platform build.

## Contradiction handling
Precedence follows a "Fail-Closed/Fail-Secure" hierarchy:
1. **Freshness:** Nonce-bound protocol frames with monotonic sequence numbers.
2. **Uncertainty:** Any ambiguity in terminal status (e.g., control disconnect during commit) maps to `POSSIBLE_SINK_EXPOSURE` and triggers mandatory quarantine.
3. **Fail behavior:** Immediate process group reaping (SIGKILL) on protocol violation or audit gate failure.

## Stop and human escalation
Machine stop conditions: Protocol violation, signature mismatch, failed audit-write/fsync, or unauthorized FD presence.
Human escalation: Any detected `CONTAINMENT_FAILURE` or `POSSIBLE_SINK_EXPOSURE` requires manual credential rotation and vault-epoch invalidation; no automated re-run is permitted.

## Failure containment and recovery
Containment: Process isolation via App Sandbox (`inherit=true`) and `RLIMIT` constraints.
Recovery: No in-place recovery for compromised helpers. Revocation is achieved via vault-epoch rotation. Audit logs (immutable) provide the basis for post-mortem forensics.

## Falsification experiments
1. **Entropy Injection (F3):** Attempt to inject `DYLD_INSERT_LIBRARIES` or `PATH` via `posix_spawn` environment; success = design failure.
2. **FD Exhaustion/Injection (F2):** Manually map unauthorized descriptors to the helper's FD table; success = design failure.
3. **Sink Hijack (F12):** Attempt to append to the mock-sink FD after the `RELEASE_ONCE` frame; success = design failure.
4. **Core Dump (F10):** Attempt to induce a crash that results in a core dump; if any file is persisted, design failure.

## Assumptions and limitations
*   **Trust Assumptions:** Assumes the macOS kernel correctly enforces `App Sandbox` and that `posix_spawn` attributes are respected.
*   **Residual Risk:** Kernel-level side channels or undocumented `dyld` behavior remain outside the TCB.
*   **Availability Costs:** High performance penalty due to `fullfsync` and synchronous durable audit gates.

---

### Highest-severity issue
The design lacks a concrete mechanism for proving that the parent has actually *entered* the intended App Sandbox profile before reading the canary; entitlements are only a request, not a state.

### Exact design section and exploit/failure sequence
**Section:** "Build, signing, and entitlement contract." 
**Failure:** A malicious or misconfigured environment might fail to apply the sandbox profile at runtime (e.g., due to local configuration errors), permitting the helper to access restricted paths while the parent believes it is fully sandboxed.

### Smallest concrete correction
Introduce a "Sandbox Proof-of-Capability" step: the helper must attempt to open a non-existent, prohibited path (e.g., a restricted system directory) and successfully log the *denial* via the control FD before the canary injection.

### Missing falsifier or acceptance gate
A falsifier that forces an "entitlement mismatch" at spawn time—specifically, a test where the binary is signed but the entitlement is absent—to confirm the parent's launch-denial logic actually works.

### Claim ceiling
The design remains a "generated-only data experiment." No claims are made regarding Keychain interaction or production-secret safety until the Sandbox Proof-of-Capability gate is verified.


## Attached primary evidence 6

Source path: `house/workflow/runs/20260824T135407Z-canary-helper-containment-design/council/reviewers/constructive-theorist.md`
SHA-256: `7c3e37db05f684f6ea8a545f8e81962a1bea3dc3fdea3b0b9429b0e757118146`

# Design review: constructive-theorist

Packet SHA-256: 99ecfc7e183f4d8d40cc938c3869bc7d668b2de72930d59c86881852dfe1c819  
Dispatch model/provider: cline-pass/deepseek-v4-flash / ClinePass  
Reviewer self-report: constructive-theorist  
Harness: provider-orchestration ClinePass OpenAI shim  
System-prompt profile: council role only; otherwise unknown  
Memory: unknown  
Reasoning mode: unknown  
Disposition: completed  

## Proposed boundary

Recommend **ACCEPT_DESIGN_ONLY** for the generated-canary helper containment design v1. The minimum implementable architecture is:

- A sealed, signed parent binary (App Sandbox + hardened runtime, no exceptions) that embeds and verifies the exact helper binary.
- A sealed helper binary (inherited sandbox, hardened runtime, `get-task-allow` absent) that inherits exactly FDs 3–6, no others.
- A generated test coordinator that creates all channels with `O_CLOEXEC`, launches the parent via `posix_spawn` with `POSIX_SPAWN_CLOEXEC_DEFAULT | POSIX_SPAWN_SETSID`, verifies signatures and hashes, and never touches real secrets, Keychain, or network.
- A controller SQLite ledger that provides a durable, monotonic sink‑attempt gate (`synchronous=FULL`, fullfsync, separate‑read verification) before the one‑use `RELEASE_ONCE` frame.
- An in‑process memory‑only mock sink and a sterile observer that scans declared surfaces for canary material.

The trusted computing base consists of:  
1. The signed parent and helper binaries (identity verified by coordinator via static hashes and Apple code‑signing inspection).  
2. The coordinator harness (test code, no ambient authority).  
3. The controller SQLite store with `fs

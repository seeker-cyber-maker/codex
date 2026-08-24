We are given a transport packet with SHA-256: bec0c8a1195e1ff3d3259513a9e49c4460af149c6b860777e7e5ff2fe936541f
 We are to return a review in the exact format of the response contract, replacing placeholders.

 The transport packet contains the original evidence packet and several attached primary evidences.

 We are acting as the reviewer "evidence-auditor".

 Steps:
 1. We must fill in the review contract with our assessment.
 2. We are to base our review on the provided packet, specifically the delta review question and the design v1.1.

 The original evidence packet (from the transport packet) is about a design review for "generated-canary helper containment design v1.1".

 The review question in the original evidence packet is:
   Does v1.1 correct the initial design's pre-canary sandbox-evidence gap, helper process-group escape, path-verification race, RLIMIT ordering, and release-state naming without adding new authority?
   Review only the delta and return one leading disposition:
     - `ACCEPT_DESIGN_ONLY`
     - `REVISE_BEFORE_IMPLEMENTATION`
     - `REJECT_DESIGN`

   Then, if accepting, state the exact claim ceiling; if not, identify any remaining implementation-blocking flaw with its exact section, failure sequence, smallest correction, and missing falsifier.

 We are to return a review in the format of the response contract.

 Let's break down the response contract:

 # Design review: evidence-auditor

 Packet SHA-256: bec0c8a1195e1ff3d3259513a9e49c4460af149c6b860777e7e5ff2fe936541f
 Dispatch model/provider: nvidia/nemotron-3-super-120b-a12b:free / OpenRouter   [Note: from the council manifest, we see that the evidence-auditor used nvidia/nemotron-3-super-120b-a12b:free]
 Reviewer self-report: <exact claim or unknown>   [We are to put our self-report as per the instructions: we are a blind, independent member. We can state: "blind, independent expert architecture council member"]
 Harness: provider-orchestration explicit-free catalog proxy   [from the council manifest for evidence-auditor]
 System-prompt profile: council role only; otherwise unknown   [we don't have more info, so we put "council role only; otherwise unknown"]
 Memory: enabled | disabled | unknown   [from the council manifest: for evidence-auditor, memory is not specified in the reviewer entry? But in the manifest, we see for evidence-auditor: 
        "Memory: enabled | disabled | unknown" -> we don't see it in the manifest for the reviewer. However, in the manifest, the reviewer entry for evidence-auditor does not have a memory field. 
        But note: the manifest has a "reviewers" array, and for evidence-auditor, we see:
          "privacy": "third-party-cloud",
          ... 
        and no memory. However, in the contract we have to choose. Looking at the adversarial-methodologist review, it says "Memory: disabled". 
        Since we are not told, we can put "unknown". But note: the council manifest for evidence-auditor does not specify memory. However, in the initial packet, the reviewer self-report for evidence-auditor in the manifest does not have memory. 
        We'll put "unknown" for memory.

 Reasoning mode: <exact or unknown>   [we don't have this info, so "unknown"]
 Disposition: completed | partial | refused | timed-out | failed   [we are to put our disposition as the reviewer. We are completing the review, so "completed"]

 Then we have the sections:

 ## Proposed boundary
 <minimum implementable architecture and trusted computing base>

 ## Authority-bearing facts
 <facts requiring authenticated provenance versus advisory data>

 ## Contradiction handling
 <precedence, freshness, uncertainty, and fail behavior>

 ## Stop and human escalation
 <machine stop conditions and bounded human adjudication>

 ## Failure containment and recovery
 <component compromise, revocation, recovery, and audit>

 ## Falsification experiments
 <bounded experiments with explicit pass/fail criteria that could disprove the design claims>

 ## Assumptions and limitations
 <trust assumptions, residual risks, and availability costs>

 We must base our review on the design v1.1 and the delta.

 From the original evidence packet, we see that the design v1.1 has been reviewed by the council and the chair disposition was `REVISE_BEFORE_IMPLEMENTATION` (from the council synthesis).

 However, note: we are the evidence-auditor reviewer, and we are to make our own call.

 Let's read the design v1.1 (from the attached primary evidence 1) and the council synthesis (attached primary evidence 2) to see if the corrections are sufficient.

 The council synthesis says that v1.1 accepted the following corrections:
   - Only the parent creates a new session; the helper remains in the parent's process group and group/session escape is a containment failure.
   - Static signature/entitlement inspection is followed by post-spawn dynamic code identity before canary injection.
   - Limits and capability probes have an explicit order; the parent spawns the helper before setting its own `RLIMIT_NPROC=0`, while the helper sets its limit as its first production action.
   - The controller gate is named `SINK_RELEASE_DURABLE`, avoiding a false claim that bytes were already written while preserving conservative `POSSIBLE_SINK_EXPOSURE` semantics after the gate.
   - The mock-sink read/write ends and parent-close obligations are explicit.
   - Network falsifiers require a separately bounded runtime-test authority; no provider or real destination is implied.

 The council synthesis also says that the reviewer (adversarial-methodologist) had a remaining concern about proving the sandbox is active, and suggested a "Sandbox Proof-of-Capability" step.

 However, note that the design v1.1 already includes:
   "Before canary injection, the candidate must pass capability probes against a harness-created, existing, same-user-readable sentinel outside the allowed container; loopback, reserved-test-address, and arbitrary Unix-socket connect targets; an extra inherited FD; and a spawn attempt."

 This is exactly the sandbox proof-of-capability: probing for denials (EPERM/EACCES) on operations that should be blocked by the sandbox.

 Therefore, the design v1.1 does address the sandbox active proof by requiring these probes to fail (with the expected denials) before canary injection.

 Given that, and the council synthesis says that the corrections in v1.1 are accepted, we might be inclined to accept the design.

 However, note the review question: 
   "Does v1.1 correct the initial design's pre-canary sandbox-evidence gap, helper process-group escape, path-verification race, RLIMIT ordering, and release-state naming without adding new authority?"

 The council synthesis says that v1.1 does correct these (by the listed corrections).

 Therefore, we should return `ACCEPT_DESIGN_ONLY`.

 But note: we must also state the exact claim ceiling if accepting.

 From the design v1.1, the claim ceiling is stated in the "Claim ceiling" section:

   "This is a non-runtime design for a disposable, generated-data-only containment experiment. It proves no App Sandbox behavior, code-signing behavior, process isolation, Keychain access, secret zeroization, provider delivery, or real credential safety. The proposed helper must not be built or launched on the authority of this document alone.

    The first implementation may claim only that declared falsifiers passed for a specific hash- and signature-bound parent/helper build on a specific macOS build. Passing generated-canary tests will not authorize Keychain or real secrets."

 So the exact claim ceiling is: 
   "The first implementation may claim only that declared falsifiers passed for a specific hash- and signature-bound parent/helper build on a specific macOS build."

 However, note that the design also says: "Passing generated-canary tests will not authorize Keychain or real secrets."

 We are to state the exact claim ceiling.

 Now, we must fill in the other sections of the review contract.

 We are to base our review on the design and the packet. We are not to add new authority, so we stick to the evidence.

 Let's fill in each section:

 ## Proposed boundary
   We describe the minimum implementable architecture and the trusted computing base (TCB) as per the design v1.1.

   From the design v1.1, the TCB includes:
     - The signed parent and helper binaries (with identity verified by static hashes and dynamic code-signing checks).
     - The test coordinator (which creates the channels, verifies, etc.)
     - The controller (SQLite ledger for durable gate)
     - The in-process memory-only mock sink and sterile observer.

   However, note that the design says the coordinator, parent, and helper are sealed and signed.

   We can write:

   The minimum implementable architecture consists of:
     - A sealed, signed parent binary (App Sandbox + hardened runtime, no exceptions) that embeds and verifies the exact helper binary.
     - A sealed helper binary (inherited sandbox, hardened runtime, `get-task-allow` absent) that inherits exactly FDs 3–6, no others.
     - A generated test coordinator that creates all channels with `O_CLOEXEC`, launches the parent via `posix_spawn` with `POSIX_SPAWN_CLOEXEC_DEFAULT | POSIX_SPAWN_SETSID`, verifies signatures and hashes, and never touches real secrets, Keychain, or network.
     - A controller SQLite ledger that provides a durable, monotonic sink‑attempt gate (`synchronous=FULL`, fullfsync, separate‑read verification) before the one‑use `[ADDRESS]` frame.
     - An in‑process memory‑only mock sink and a sterile observer that scans declared surfaces for canary material.

   The trusted computing base consists of:
     1. The signed parent and helper binaries (identity verified by coordinator via static hashes and Apple code‑signing inspection).
     2. The coordinator harness (test code, no ambient authority).
     3. The controller SQLite store with `synchronous=FULL` and fullfsync.
     4. The in‑process mock sink and observer (which are part of the test and do not persist the canary).

   However, note that the design says the coordinator, parent, and helper are the only ones that run, and the controller and sink are in the test process.

   We can adjust to match the design.

   Alternatively, we can take the constructive-theorist's review (which was partial) and use their proposed boundary, but note they were for v1.0? Actually, they reviewed the same packet and said ACCEPT_DESIGN_ONLY for v1.0? But we are reviewing v1.1.

   Since we are accepting, we can use a similar boundary.

   Let's write:

   The minimum implementable architecture is as described in the design v1.1: 
     - Parent and helper binaries are sealed and signed, with the parent embedding the helper.
     - The coordinator sets up O_CLOEXEC channels, launches the parent, which then launches the helper without changing session or process group.
     - The controller uses a SQLite ledger with synchronous=FULL and fullfsync for the durable gate.
     - The mock sink is in-process and memory-only.

   The TCB is the parent, helper, coordinator, controller, and the test process (for the mock sink and observer) but note that the test process is not part of the containment boundary for the helper.

   However, the design says the coordinator, parent, and helper are the containment boundary.

   We'll keep it concise.

 ## Authority-bearing facts
   We need to distinguish facts that require authenticated provenance (i.e., we must verify them at runtime) from advisory data (which are claims that must be verified by falsifiers).

   From the design and the adversarial-methodologist review:

   - Authenticated Provenance: 
        * The binary hash and signature of the helper at the moment of spawning (validated by the parent via dynamic code-signing).
        * The exact FD table (must be enumerated and proven to contain only the declared FDs).
        * The outcome of the capability probes (must be observed as denials: EPERM/EACCES for the sentinel, connection, and spawn attempts).
        * The dynamic code identity check (post-spawn) must match the static hash and signature.

   - Advisory Data (until verified by runtime falsifiers):
        * The entitlement declarations (App Sandbox, inherit=true, hardened runtime) - these are advisory until the capability probes show the sandbox is active.
        * The RLIMIT settings (until we see the helper sets RLIMIT_NPROC=0 and the parent sets it after spawn, and then we observe the limits).
        * The environment allowlist (until we check the child environment equals the fixed allowlist).

   We can write:

   Authority-bearing facts requiring authenticated provenance:
     1. The helper's dynamic code identity (CDHash and designated requirements) at runtime must match the static hash and signature bound in the qualification receipt.
     2. The helper's FD table must contain exactly the declared FDs (3-6) with the correct directions and content types, and no others.
     3. The capability probes (sentinel open, loopback/reserved-test-address/Unix-socket connect, extra FD, spawn attempt) must all return the expected denials (EPERM/EACCES for file operations, and appropriate errors for network and spawn) before canary injection.
     4. The parent must have spawned the helper without changing the process group (so the helper remains in the parent's process group) and without setting a new session.

   Advisory data (requiring runtime falsifiers to confirm):
     1. The entitlement declarations (com.apple.security.app-sandbox=true, com.apple.security.inherit=true, hardened runtime) are requests until the capability probes demonstrate sandbox enforcement.
     2. The RLIMIT_NPROC=0 setting by the helper (as its first production action) and by the parent (after helper spawn) must be observed via the reported limits.
     3. The child environment must equal the fixed allowlist and contain no injected values (e.g., DYLD_*, HOME, PATH, etc.).

 ## Contradiction handling
   We describe precedence, freshness, uncertainty, and fail behavior.

   From the design and the adversarial-methodologist review:

   - Precedence: The design uses a fail-closed/fail-secure hierarchy.
   - Freshness: Nonce-bound protocol frames with monotonic sequence numbers.
   - Uncertainty: Any ambiguity in terminal status (e.g., control disconnect during commit) maps to `POSSIBLE_SINK_EXPOSURE` and triggers mandatory quarantine.
   - Fail behavior: Immediate process group reaping (SIGKILL) on protocol violation or audit gate failure.

   We can write:

   Precedence: Fail-closed/fail-secure. Protocol violations or audit gate failures trigger immediate termination.
   Freshness: Nonce-bound protocol frames with monotonically increasing sequence numbers prevent replay and reordering.
   Uncertainty: Any deviation from the expected protocol flow (e.g., missing frames, invalid frames, control disconnect during commit) results in the conservative terminal class `POSSIBLE_SINK_EXPOSURE` and requires quarantine of the attempt.
   Fail behavior: On any protocol violation, signature mismatch, failed audit-write/fsync, or unauthorized FD presence, the coordinator kills the entire candidate process group (parent and helper) with SIGKILL and reaps them, then records the most conservative terminal class consistent with the last durable phase.

 ## Stop and human escalation
   Machine stop conditions and bounded human adjudication.

   From the design and the adversarial-methodologist review

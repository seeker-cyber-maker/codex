We are to act as an adversarial methodologist. We must review the v2.1 delta and the evidence packet.

The task: Return exactly the response contract, replacing placeholders with our review.

We are to search for:
- confused-deputy paths
- stale bindings
- hidden ambient I/O
- overstated provenance
- capability leaks
- recovery failures

We must distinguish direct evidence from inference.

If the delta is sufficient, we say so and stop (i.e., return ACCEPT_V2_1). If not, we return only the highest-impact unresolved invariant and its smallest repair.

We are to return the response contract with the following sections:

# Design review: adversarial-methodologist

Packet SHA-256: 201a9c10539e801f7d7b60f67b384f61028dafd55c5569fa9e4e30a6d5a3fac4
Dispatch model/provider: nvidia/nemotron-3-super-120b-a12b:free / OpenRouter
Reviewer self-report: <exact claim or unknown>
Harness: provider-orchestration explicit-free catalog proxy
System-prompt profile: council role only; otherwise unknown
Memory: enabled | disabled | unknown
Reasoning mode: <exact or unknown>
Disposition: completed | partial | refused | timed-out | failed

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

We must fill in these sections based on our review.

First, let's understand the packet.

The packet SHA-256 is given: 201a9c10539e801f7d7b60f67b384f61028dafd55c5569fa9e4e30a6d5a3fac4

We are to review the v2.1 delta and the evidence.

From the evidence packet, we see:

- The decision question: Does v2.1 close the five prior authority-boundary gaps without introducing hidden host I/O or a new authority-laundering path?

- The five prior gaps (from the evidence packet) are:
  1. Cross-record disagreement must refuse; no precedence repair.
  2. The operation assembler must perform zero host I/O.
  3. A hash is byte identity, not authentication or authorship proof.
  4. Advisory routing and hard constraints require different types.
  5. Project configuration must be ignored through a proven CLI contract or completely content-addressed and admitted.

The v2.1 delta (from V2_1_DELTA.md) says it changes exactly five decision-bearing surfaces:

1. Precedence removed. Every cross-record fact must agree; disagreement refuses. No route, operation, profile, or human action repairs an earlier record in place.
2. Routing semantics typed. Advisory class, advisory model preference, and hard execution constraints are distinct. Every advisory input receives an explicit disposition in the route record.
3. Assembler made zero-host-I/O. `assemble_operation_v2` accepts verified descriptors and performs canonical validation/hashing only. Observation, hashing of host files, and output reservation are separate producers.
4. Qualification claim narrowed. The first route-selection record is `STRUCTURE_BOUND_NO_DISPATCH`; a content hash is not a signature or proof of authorship. Signer admission remains a separate future gate.
5. Project configuration strategy sealed. Every operation chooses `PROJECT_CONFIG_IGNORED` or `PROJECT_INPUTS_CONTENT_ADDRESSED`; undeclared effective context or tool capability refuses.

We must check if these five changes indeed close the five prior gaps.

Let's map:

Prior gap 1: Cross-record disagreement must refuse; no precedence repair.
  -> v2.1 delta point 1: Precedence removed. Every cross-record fact must agree; disagreement refuses. -> This matches.

Prior gap 2: The operation assembler must perform zero host I/O.
  -> v2.1 delta point 3: Assembler made zero-host-I/O. -> This matches.

Prior gap 3: A hash is byte identity, not authentication or authorship proof.
  -> v2.1 delta point 4: Qualification claim narrowed. The first route-selection record is `STRUCTURE_BOUND_NO_DISPATCH`; a content hash is not a signature or proof of authorship. -> This matches.

Prior gap 4: Advisory routing and hard constraints require different types.
  -> v2.1 delta point 2: Routing semantics typed. Advisory class, advisory model preference, and hard execution constraints are distinct. Every advisory input receives an explicit disposition in the route record. -> This matches.

Prior gap 5: Project configuration must be ignored through a proven CLI contract or completely content-addressed and admitted.
  -> v2.1 delta point 5: Project configuration strategy sealed. Every operation chooses `PROJECT_CONFIG_IGNORED` or `PROJECT_INPUTS_CONTENT_ADDRESSED`; undeclared effective context or tool capability refuses. -> This matches.

So on the surface, the v2.1 delta addresses the five gaps.

However, we are an adversarial methodologist. We must look for hidden issues.

Let's look at the evidence and the delta for potential problems.

From the V2_1_OPERATION_CONTRACT.md, we see:

- The route-selection record has a field `provenance` with `author_id` and `authoring_method` and `signature_state: "NOT_VERIFIED_IN_FIRST_SLICE"`. This is acceptable because it doesn't claim verification.

- The assembler `assemble_operation_v2` receives mappings already produced by separate observers. It may not open, resolve, stat, hash, create, reserve, or enumerate a path. It returns a sealed record with state `ASSEMBLED_NO_OBSERVATION_NO_DISPATCH`.

- The isolation and project-input policy: two strategies: `PROJECT_CONFIG_IGNORED` and `PROJECT_INPUTS_CONTENT_ADDRESSED`.

  For `PROJECT_CONFIG_IGNORED`: Requires CLI-contract evidence for an implemented project-config-ignore surface; current installed `codex exec 0.147.0` does not satisfy this. Until the CLI surface exists and is source-tested, real profiles using this strategy refuse.

  For `PROJECT_INPUTS_CONTENT_ADDRESSED`: The workspace descriptor inventories every discovered project config layer, ... The operation capability allowlist explicitly admits or rejects each surface. Runtime capture must equal the inventory and allowlist. Missing or additional items refuse.

- The exact argv policy: The operation seals argv derived only from its verified descriptors. For the current installed CLI, the minimum shared elements are: ... Additional capability-closing overrides are contract-versioned rather than assumed. `PROJECT_CONFIG_IGNORED` additionally requires a CLI flag not present in installed `0.147.0`; the assembler must reject a descriptor claiming support when its CLI-contract evidence does not list that flag.

- Agreement checks: Verification refuses when any of these differ: ... (a list)

- Provenance and future signatures: The first slice records author identity and method as attributed metadata and labels signature state unverified. It never claims that a hash proves the author. A future signer-admission contract must define key issuer, key ID, algorithm, signed byte envelope, revocation/freshness, multi-author changes, and verification receipt.

- Credentials, runtime, and logs: Credential projection, runtime-root creation, effective-config observation, output reservation, filesystem tracing, launcher/controller transactions, and result admission remain outside the first slice.

- Recovery and revocation: Pure assembly is deterministic for identical input bytes. Any new task, route, descriptor, policy, or freshness fact creates new hashes and requires a new downstream record. Expired route selections are unusable; they are not refreshed in place. A later controller reconciles the one existing intent/lease under its exact idempotency binding; it never substitutes another operation. Structural verification cannot revoke keys, consume authority, or change controller state.

- First implementation slice: Implement only: 1. pure task-card-v2 structural verification; 2. pure route-selection assembly/verification and no-dispatch receipt; 3. pure `assemble_operation_v2` and structural verifier over caller-supplied descriptors; and 4. deterministic mutation fixtures proving bindings and zero host I/O.

- Falsification matrix: 10 points.

Now, we must look for:

- Confused-deputy paths: Is there a way for an untrusted entity to cause the system to perform an action on its behalf? For example, if the assembler uses a descriptor that is not properly validated, it might use a malicious path.

  The assembler is said to receive verified descriptors. The verification of the descriptors is done by separate producers. The assembler only does canonical validation and hashing. It does not open, resolve, stat, etc. So it should be safe.

- Stale bindings: The system uses hashes to bind records. If a record is expired, it is unusable and not refreshed in place. This is good.

- Hidden ambient I/O: The assembler is prohibited from doing host I/O. However, note that the assembler does "canonical validation/hashing". What does that mean? It might be hashing the content of the descriptors? But the descriptors are already verified and supplied as mappings. The assembler is not supposed to read files. The descriptors include things like executable descriptor: absolute lexical path, content SHA-256, version, CLI-contract SHA-256. The assembler is to validate that the path is lexical (not canonicalized) and that the SHA-256 matches? But note: the assembler is not allowed to hash host files. However, the descriptor already provides a content SHA-256. The assembler might be expected to verify that the content SHA-256 matches the file? But that would require reading the file. This is a potential hidden I/O.

  Let's look at the assembler's input: "executable descriptor: absolute lexical path, content SHA-256, version, CLI-contract SHA-256". The assembler is to perform "canonical validation/hashing only". But note: the assembler is not allowed to open, resolve, stat, hash, create, reserve, or enumerate a path. However, if the assembler is to validate the executable descriptor, it might need to check that the file at the absolute lexical path has the given content SHA-256. That would require reading the file (hashing it). This is host I/O.

  But wait: the evidence says: "assemble_operation_v2 receives mappings already produced by separate observers. It may not open, resolve, stat, hash, create, reserve, or enumerate a path." So the assembler itself must not do that. However, the separate observers (which are outside the assembler) must have produced the descriptors. The assembler only uses the descriptors. So the assembler does not need to read the file because the descriptor already has the content SHA-256. The assembler might only check that the descriptor is well-formed and that the SHA-256 is in the correct format? But note: the assembler is to perform "canonical validation/hashing". What does that mean? It might be hashing the descriptor itself? Or it might be validating that the path is lexical (i.e., not containing symlinks, etc.) without resolving? The evidence says: "Lexical path validation is allowed; filesystem canonicalization is not." So the assembler can check that the path is a string and does not contain certain patterns (like ".." or symlinks) without actually accessing the filesystem? That is possible by string inspection.

  However, the descriptor also includes a "content SHA-256". The assembler might be expected to verify that the content SHA-256 matches the file? But that would require reading the file. The evidence says the assembler may not hash host files. So it must not do that. Therefore, the assembler does not verify the content SHA-256 against the file. It only uses the descriptor as given. Then, how do we know the file is correct? The separate observer that produced the descriptor must have done that. The assembler trusts the descriptor.

  This is a potential issue: the assembler trusts the descriptor without verifying the content. But note: the descriptor is produced by a separate observer. The observer is outside the first slice. The first slice only assembles. The observer must be trusted to have correctly produced the descriptor. This is a trust assumption.

  However, the evidence says: "The assembler returns a sealed record with state `ASSEMBLED_NO_OBSERVATION_NO_DISPATCH`. A runtime-profile verifier later binds observed canonical reality." So the runtime-profile verifier will later check the actual file? Then the assembler does not need to verify the content at assembly time.

  So the assembler does not do host I/O. It only uses the descriptors as given.

  But note: the assembler does "canonical validation/hashing". What is it hashing? It might be hashing the descriptors to produce the operation record's hash? That is hashing of in-memory data, not host files. So that is allowed.

  Therefore, the assembler does zero host I/O.

- Overstated provenance: The route-selection record has a field `provenance` with `author_id` and `authoring_method` and `signature_state: "NOT_VERIFIED_IN_FIRST_SLICE"`. The evidence says: "It never claims that a hash proves the author." So this is not overstated.

- Capability leaks: We must check if there is a way for a capability to leak out. For example, if the assembler accidentally leaves a file descriptor open or if the operation record contains a capability that can be used to escape.

  The assembler is pure and does not interact with the host. The operation record is just data. The later runtime-profile verifier and controller are outside the first slice. So in the first slice, there should be no capability leak.

- Recovery failures: The system says that expired route selections are unusable and not refreshed in place. This is good. However, what if the system is compromised? The recovery and revocation section says: "Structural verification cannot revoke keys, consume authority, or change controller state." So if there is a compromise, the first slice cannot revoke anything. But note: the first slice does not have any authority to revoke. It only produces records. The revocation would be handled by a later controller. The evidence says: "A later controller reconciles the one existing intent/lease under its exact idempotency binding; it never substitutes another operation." So if there is a compromise, the controller might be able to detect and stop? But the first slice itself does not have recovery mechanisms.

  However, the first slice is only about producing records. The recovery of the system as a whole is outside the first slice.

Now, we must look for the highest-impact unresolved invariant if any.

Let's look at the falsification matrix. It has 10 points. We can see if any of these are not actually covered by the design.

For example, point 5: "Monkeypatch file/path/process/network APIs to raise and assemble fixture records: assembly still succeeds, proving zero host I/O." This is a test to show zero host I/O. If the assembler does not use those APIs, then even if they are monkeypatched to raise, the assembly succeeds. This is a good test.

Point 6: "Claim `PROJECT_CONFIG_IGNORED` against a CLI contract lacking the flag: assembly fails." This is good.

Point 7: "Add or omit one content-addressed project contributor: profile agreement fails." This is good.

Point 8: "Change an output intent to claim a reservation: structural assembly rejects the state; only later observed evidence may prove reservation." This is good.

Point 9: "Supply a valid hash with unverified authorship: structural receipt succeeds only at `STRUCTURE_AND_BINDINGS_ONLY`; authenticated or executable admission remains impossible." This is good.

Point 10: "Run every first-slice test while snapshotting controller DB, workspace, and output roots: all remain byte/entry identical and no network or subprocess occurs." This is good.

Now, we must check if there is any hidden ambient I/O or confused-deputy.

One potential issue: the route-selection record includes an `evidence_bundle_sha256` in the observation field. This evidence bundle is produced by an observer. The assembler does not use this evidence bundle directly? The assembler uses the route-selection record, which includes the evidence_bundle_sha256. But the assembler does not open or read the evidence bundle. It only uses the hash. So that is safe.

However, note that the route-selection record is produced by a route selector. The route selector might have done host I/O to produce the evidence bundle. But that is outside the assembler.

Another issue: the task card v2 has routing fields. The assembler uses the task card v2 and the route-selection record to assemble the operation. The assembler must check that the selected model/provider/pool satisfy the hard task constraint. This is done by comparing values in the records. No host I/O.

But note: the task card v2 might have been produced by a user. The user might have included a malicious model_identity? The assembler does not validate that the model_identity is a real model. It only checks that it matches the route-selection record and the hard constraints. The hard constraint is a string (explicit model slug). The assembler does not check if the model exists. That is left to the runtime.

This is not a host I/O issue, but it might be a capability issue if the model slug is used to call a model that is not allowed. However, the assembler only sets up the argv. The runtime-profile verifier and controller will later check the model against the allowed list? The evidence says: "operation argv versus route selection and isolation policy" is checked. So the runtime-profile verifier will check that the argv matches the route selection and the isolation policy. The isolation policy includes the allowed models? The exact argv policy says: the operation seals argv derived only from its verified descriptors. The descriptors include the executable descriptor and the workspace descriptor, etc. The model is not in the argv? Actually, the argv includes `--model <route model

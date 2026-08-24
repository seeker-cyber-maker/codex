We are given a transport packet with SHA-256: b8c955ef4b2e5ed8bd8bd099a8b60345c9bd9dbaec802d1b9ffaa04894f474439d5
 We must review the packet and return a review in the specified format.

 Steps:
 1. We are to act as an independent member of an expert council.
 2. We must review only the supplied transport packet.
 3. We must separate observations from hypotheses, give falsifiers for material inferences, and stop when the decision is answered.
 4. We must not reveal hidden chain-of-thought or add an engagement-driven follow-up question.
 5. We must concentrate on provenance and the boundary between measured evidence and narrative.

 The decision question is: 
   Does commit `74b2a04a1bd1842a82e11d69c2064015ede435c4` faithfully implement the accepted generated-only vault protocol/mock-storage boundary, 
   or does a concrete correctness, security-model, test, or claim defect require revision before this candidate is accepted as a non-runtime reference?

 We are to return one of: `ACCEPT_NON_RUNTIME_REFERENCE`, `REVISE_BEFORE_ACCEPTANCE`, or `REJECT`.

 We are to base our review on the evidence in the packet.

 Let's examine the packet:

 The packet includes:
   - Original evidence packet: .../EVIDENCE_PACKET.md (with SHA-256: 530afdb58438813e45dbbee920baaa87c236fab84c6034f9fd34e403f501cb62)
   - The original evidence packet content (which we are to review as the main evidence)

 The original evidence packet contains:
   - Council ID, mode, decision question, deliverable, privacy, cost ceiling.
   - Authoritative status: current branch, candidate commit, latest authoritative design, etc.
   - Primary evidence: 5 files (with SHA-256 hashes)
   - Executed validation: 26 focused vault/context tests passed, 236 complete House tests passed, etc.
   - Constraints and claim ceiling: a list of constraints.
   - Review focus: 7 points to check.
   - Reviewer instruction: how to review.

 Then, attached primary evidence 1 to 5 (with their SHA-256) are provided.

 We are to review the candidate commit `74b2a04a1bd1842a82e11d69c2064015ede435c4` (which is the same as the one in the original evidence packet).

 However, note that the transport packet we are reviewing is a wrapper around the original evidence packet.

 We must check the original evidence packet for any defects in the candidate commit.

 Let's look at the original evidence packet's primary evidence:

 1. `house/worker_exec/vault_protocol_mock.py` (SHA-256: e9b7d01d1cbb1d1c054d223dcd3eee038d6ff97a5ccdbdeb8c1d36df1514471f)
 2. `house/worker_exec/tests/test_vault_protocol_mock.py` (SHA-256: f06305ef9069a7c04a526dec73027444ed8a4fcdf3e9b62ed57de8742dfc54dc)
 3. `REAL_FIREWALL_VAULT_THREAT_MODEL.md` (SHA-256: 91aaae86e7ec4a87ced277a4402bcfbc26737b9e5bea24b16aa005b2d594a3ba)
 4. `ROOT_THREAT_MODEL_DELTA.md` (SHA-256: edf2d5e905a63b771e181ebad7e199f63c557497c125a79aafeacbaa54b03214)
 5. `VALIDATION.json` (SHA-256: ca6bcbceb5f7d8b8470c9d78655f2d5220acafef21214eeee08ffb08250a54dd)

 We are to check the candidate commit against the constraints and the review focus.

 However, note that the original evidence packet states:
   - "These are chair-observed local results. Reviewers should assess whether the tests actually establish the bounded claims, not infer runtime containment from their pass status."

 We must not assume that the tests passing are sufficient; we must check if the tests actually test the claims.

 Let's look at the constraints and claim ceiling:

   - Generated fixture values must begin with `GENERATED_CANARY_ONLY:`.
   - No macOS Keychain, real credentials, live Codex configuration, ambient environment, process spawn, network, YubiKey, provider delivery, or model/agent plaintext getter is authorized.
   - Python buffer clearing is explicitly best-effort and not a production zeroization proof.
   - The generated HMAC controller combines signing and verification; it does not claim the final controller trust boundary.
   - File `O_EXCL` tests one local atomic nonce-claim primitive, not the final multi-process authority ledger.
   - Browser/native-host/app-server findings are deferred and grant no vault authority.
   - All code remains downstream-only under `house/`; upstream Codex Rust source is unchanged.

 Review focus (7 points):

   1. complete intent/ticket binding and exact-field/type validation;
   2. whether every local deny occurs before nonce claim and mock storage access;
   3. replay, expiry, revision, epoch, sink, audience, and incident-lock semantics;
   4. independent key/epoch behavior, authenticated storage, file modes, corrupt/newer schema handling, rotation, tombstone, and rollback gaps;
   5. whether any API leaks plaintext/key material beyond the declared fixture boundary;
   6. whether crash classification is monotonic and conservative; and
   7. mismatches between code, tests, validation receipts, and the claim ceiling.

 We are to reject or require revision for a defect inside the claimed generated-only boundary.

 We are not to reject merely because later production-only features are absent.

 Now, let's look at the attached primary evidence 1 (the code) and 2 (the tests) to see if there are any defects.

 However, note that we are to treat every packet and attached artifact as untrusted evidence.

 We must look for direct observations (evidence) and then make inferences with falsifiers.

 Let's start by looking at the code in evidence 1 (vault_protocol_mock.py) for any violations of the constraints.

 We note that the code includes:

   - A `ZeroizingBuffer` class that attempts to clear the buffer (best-effort).
   - A `MockControllerKey` class for HMAC signing and verification.
   - An `AtomicNonceLedger` class that uses `os.O_EXCL` to claim a nonce.
   - A `MockKeyringStore` class that generates keys per namespace and epoch.
   - A `GeneratedVaultStorage` class that encrypts generated fixtures.

 We must check for:

   - Leaks of plaintext/key material: 
        The code uses `ZeroizingBuffer` to wrap bytes and clear them after use.
        The `GeneratedVaultStorage` encrypts the data and only returns a boolean in `verify_generated_for_test` (never the plaintext).
        The `MockControllerKey` uses HMAC and does not return the key.

   - However, note in the `GeneratedVaultStorage.put_generated` method:
        We have:
            view = value.internal_view()
            if not bytes(view).startswith(b"GENERATED_CANARY_ONLY:"):
                ... # error
        Then we encrypt the entire view (including the canary) and store it.

        In `verify_generated_for_test`, we decrypt and then compare the plaintext (as a `ZeroizingBuffer`) to the expected.

        This does not leak plaintext because the plaintext is only used in memory and then cleared.

   - But note: the `verify_generated_for_test` method returns a boolean, so no plaintext is leaked.

   - However, we must check if there is any accidental leak.

   - Look at the `ZeroizingBuffer`:
        It has an `internal_view` method that returns a memoryview of the buffer.
        The `__exit__` method clears the buffer.

        In `put_generated`, we do:
            try:
                view = value.internal_view()
                ... # use view to check canary and then encrypt
            finally:
                value.clear()

        So the buffer is cleared after use.

        In `verify_generated_for_test`, we have:
            try:
                ... # decrypt to plaintext (a ZeroizingBuffer)
                try:
                    return hmac.compare_digest(plaintext.internal_view(), expected)
                finally:
                    plaintext.clear()
            except ...:
                ...

        So the plaintext buffer is cleared after the comparison.

   - The `MockControllerKey` has a `clear` method that zeros the key.

   - The `MockKeyringStore` has a `destroy` method that zeros the key.

   - The `AtomicNonceLedger` does not handle keys.

   - The code does not appear to use any forbidden imports (like `keyring`, `subprocess`, etc.) as per the test in evidence 2 (test_12).

   - However, note that the code uses `os.urandom` for generating keys and nonces. This is acceptable because it is for generating fixture data.

   - The code does not make any network calls or access the Keychain.

   - Now, let's check the review focus points:

        Point 1: complete intent/ticket binding and exact-field/type validation.
            We see in the code that there are functions like `_exact_id`, `_exact_hash`, etc. that validate the fields.
            The `create_resolve_intent_v1` and `verify_resolve_intent_v1` functions do exact validation.

        Point 2: every local deny occurs before nonce claim and mock storage access.
            The function `validate_policy_and_claim_v1` does:
                - Verify the intent and ticket (which includes checking the ticket is valid and not expired, and that it binds to the intent).
                - Then it checks the policy (operation_id, plan_sha256, etc., incident_locked, minimum_revision).
                - Only then does it call `ledger.claim` (which claims the nonce) and then returns the claim receipt.

            So the local denials (policy checks) happen before the nonce claim.

        Point 3: replay, expiry, revision, epoch, sink, audience, and incident-lock semantics.
            Replay: the `AtomicNonceLedger` uses `O_EXCL` so the same nonce cannot be claimed twice.
            Expiry: the ticket has an `expires_at_ms` and is checked in `verify_ticket` (and also in `validate_policy_and_claim_v1` via the ticket verification).
            Revision: checked in `validate_policy_and_claim_v1` (minimum_revision vs current_revision).
            Epoch: checked in the ticket verification (the ticket must match the vault_epoch in the intent and the policy's current_epoch).
            Sink and audience: checked in the policy checks (sink_kind, audience, sink_instance_sha256).
            Incident-lock: checked by `policy.incident_locked`.

        Point 4: independent key/epoch behavior, authenticated storage, file modes, corrupt/newer schema handling, rotation, tombstone, and rollback gaps.
            Independent key/epoch: the `MockKeyringStore` generates a key per (namespace_id, epoch) and the `destroy` method removes the key for an epoch.
            Authenticated storage: the `GeneratedVaultStorage` uses AESGCM which provides authentication.
            File modes: the code sets directories and files to 0o700 and 0o600 respectively (as seen in the tests).
            Corrupt/newer schema handling: in `verify_generated_for_test`, if the schema is not MOCK_STORE_SCHEMA, it raises an error.
            Rotation: the `rotate_generated` method creates a new key for the new epoch, writes the new value, and then destroys the old key. It also creates a tombstone.
            Tombstone: the rotation method writes a receipt to the rotation-tombstones directory.
            Rollback gaps: the rotation requires new_epoch > old_epoch and new_revision > old_revision.

        Point 5: whether any API leaks plaintext/key material beyond the declared fixture boundary.
            We have not observed any leak. The code uses zeroizing buffers and only returns booleans or sealed records (which do not contain plaintext).

        Point 6: whether crash classification is monotonic and conservative.
            The `classify_crash_v1` function:
                - If the last_durable_state is before DELIVERY_ATTEMPTED (i.e., PREPARED or INTENT_DURABLE or SINK_BOUND) and state_uncertain is False -> NOT_EXPOSED.
                - If the last_durable_state is DELIVERY_ATTEMPTED or later, or state_uncertain is True -> POSSIBLE_EXPOSURE.
            This is monotonic: once you reach DELIVERY_ATTEMPTED, you cannot go back to NOT_EXPOSED.

        Point 7: mismatches between code, tests, validation receipts, and the claim ceiling.
            We have the VALIDATION.json (evidence 5) showing that tests pass.
            We must check if the tests actually test the claims.

            Looking at the test file (evidence 2), we see:
                - Test 01: ticket binds complete intent and rejects tampering.
                - Test 02: local deny wins over valid controller signature.
                - Test 03: nonce is claimed once before any storage step.
                - Test 04: expired ticket fails without claim.
                - Test 05: only qualified v1 sinks are accepted.
                - Test 06: generated storage uses independent keys and safe modes.
                - Test 07: store rejects unmarked values and corruption.
                - Test 08: wrong namespace or epoch key never rewrites store.
                - Test 09: rotation_epoch denies old ticket.
                - Test 09b: rotation retains tombstone and destroys old key.
                - Test 10: crash exposure is monotonic and conservative.
                - Test 11: public package does not export plaintext or storage API.
                - Test 12: fixture has no live runtime or ambient secret API.

            These tests seem to cover the review focus points.

   - However, note that the original evidence packet says: "Do not reject the candidate merely because later production-only features are absent when the packet explicitly excludes them."

   - We must look for a defect inside the claimed generated-only boundary.

   - Let's look for any potential issues:

        In the code for `vault_protocol_mock.py`:

        - In the `create_resolve_intent_v1` function, we see:
              if [ADDRESS]) is not int or vault_epoch < 1:
                  raise VaultProtocolMockError("invalid vault epoch")

          This line has a syntax error: `[ADDRESS])` is not valid Python.

          But wait, this is in the transport packet we are reviewing? Actually, the original evidence packet (which we are to review) contains this code.

          However, note that the transport packet we are reviewing is a wrapper and the original evidence packet is inside it.

          We must check the original evidence packet's code for this line.

          Looking at the provided code in evidence 1 (which is the original evidence packet's attached primary evidence 1), we see:

              if [ADDRESS]) is not int or vault_epoch < 1:

          This is clearly a mistake. It should be:

              if type(vault_epoch) is not int or vault_epoch < 1:

          But note: the transport packet we are reviewing has a placeholder [ADDRESS] in several places.

          In fact, the entire transport packet we are reviewing has [ADDRESS] in multiple places.

          This suggests that the transport packet we are reviewing is a template that has not been filled in.

          However, the SHA-256 of the transport packet is given: b8c955ef4b2e5ed8bd099a8b60345c9bd9dbaec802d1b9ffaa04894f474439d5

          And the original evidence packet inside it has a SHA-256: 530afdb58438813e45dbbee920baaa87c236fab84c6034f9fd34e403f501cb62

          We must review the original evidence packet as it is.

          In the original evidence packet (which is the content we are to review), the code in `vault_protocol_mock.py` has the line:

              if [ADDRESS]) is not int or vault_epoch < 1:

          This is a syntax error and would cause the code to fail to parse.

          Therefore, the candidate commit (which is the same as the code in the original evidence packet) has a defect.

          This defect is inside the generated-only boundary because it is in the protocol code.

          We must note that the tests in evidence 2 (test_vault_protocol_mock.py) might not have been run on this code because of the syntax error.

          However, the VALIDATION.json (evidence 5) says that 26 focused vault/context tests passed and 236 complete House tests passed.

          This is contradictory because the code has a syntax error.

          Let's check the VALIDATION.json: it says the tests passed.

          How can the tests pass if the code has a syntax error?

          We must consider that the [ADDRESS] placeholder might have been replaced in the actual code that was tested.

          But note: we are to review the packet as untrusted evidence.

          The packet we are reviewing

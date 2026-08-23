# Review: evidence-auditor

Packet SHA-256: `bb2c8f998a45e1e25d4d2bee7051addf4cb86839330f189075ccfe158aad82c3`
Dispatch model/provider: `gpt-5.6-sol` / OpenAI Codex local subagent
Reviewer self-report: unknown
Harness: Codex collaboration subagent
System-prompt profile: known role-scoped summary
Memory: disabled
Reasoning mode: high
Disposition: completed

## Verdict

`REVISE_DESIGN`. The disabled admission-seam direction is sound, but the
proposal treats self-hashes and declared scope as stronger provenance and
enforcement than the primary artifacts establish. No execution is authorized.

## Direct observations

- The packet, all seven source hashes, and the SQLite hash match.
- The SQLite artifact has one `PREPARED` operation and no lease or launch
  intent. Its legacy schema does not exercise the newer live-controller path.
- The operation recomputes to the recorded hash and specifies a 60-second cap,
  zero retries, unresolved default model, unknown provider, and blocked live
  dispatch.
- The operation self-hash proves byte consistency, not issuer identity,
  qualification, or truth of declared provider and scope fields.
- `-C` plus `--sandbox read-only` does not by itself prove that all reads and
  writes are confined to the declared roots.
- The human-authority module always refuses. No enrollment, signature
  verification, nonce ledger, or consumption mechanism exists.
- The mock admission module is structurally non-executable.
- Terminal observation accepts an opaque mapping and has no typed start-failure
  transition between persisted intent and process identity.
- Stream previews are bounded, but total stream production and
  `last-message.txt` size are not.
- CLI capture validation does not establish which executable produced the
  supplied capture.

## Inferences

- At-most-once admission requires authority consumption and intent creation in
  one transaction. Falsifier: concurrency or crash tests yield two
  consumptions or spawn calls.
- Runtime qualification must derive from reproducible evidence, not a
  recomputable profile hash. Falsifier: a fabricated but internally consistent
  profile passes.
- Config and hook root paths need content identity. Falsifier: content drift
  beneath a bound root still validates.
- A fixed environment does not prove filesystem isolation, provider identity,
  credential source, hooks, or usage-pool identity.

## Unsupported or contradicted claims

- The declared read/write scope is not measured enforcement.
- A self-hashed profile is not proof of qualification.
- Cancellation and reaping are currently opaque stored observations, not typed
  lifecycle proof.
- Exactly one supervised process group is a proposed invariant.
- Output-preview truncation is not a hard output budget.

## Recommendation

Require content-addressed config/hook evidence or an empty isolated runtime
root, reproducible qualification receipts, atomic authority consumption plus
intent creation, typed lifecycle transitions, byte limits on all outputs, and
falsifying isolation tests.

Smallest step: implement a pure, disabled-by-default real-runtime-profile
schema and verifier with no subprocess or authority backend. Reject unknown or
default model/provider values, unhashed config/hook contents, unbounded output,
unbound CLI evidence, and operation/profile mismatches. Do not admit a profile
until provider and usage-pool provenance exist.

## Limitations

Read-only static inspection only; no tests, process, provider, credentials, or
hardware were used.

Final: `REVISE_DESIGN`.

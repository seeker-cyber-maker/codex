# Review: adversarial-methodologist

Packet SHA-256: `bb2c8f998a45e1e25d4d2bee7051addf4cb86839330f189075ccfe158aad82c3`
Dispatch model/provider: `gpt-5.6-sol` / OpenAI Codex local subagent
Reviewer self-report: unknown
Harness: Codex collaboration subagent
System-prompt profile: known role-scoped summary
Memory: unknown
Reasoning mode: high
Disposition: completed

## Verdict

`REVISE_DESIGN`. The current proposal does not prove model/provider closure,
single-use authority, one-spawn semantics, or recovery-safe supervision. The
existing MCU operation must remain non-executable because it omits `--model`
and records `DEFAULT_UNRESOLVED`.

## Direct observations

- The packet, all source hashes, database hash, and binary hash match.
- The database contains one prepared legacy operation and no lease or intent.
- The current live-intent row does not bind profile, attestation, signer, nonce,
  expiry, model, provider, environment, or output identity.
- Process identity is a caller-supplied string hash, not a structured OS-observed
  PID/PGID/start-time/executable tuple.
- Lease expiry prevents normal terminal recording and ambiguous reconciliation
  does not cancel or reap a process that may have started.
- The supervisor can inherit environment and stdin, has no process-level `cwd`,
  and returns no structured process identity.
- Output reservation does not hold a directory capability across spawn.
- CLI validation accepts supplied captures and substring matches without
  proving capture provenance.

## Inferences

- A profile cannot repair the already sealed argv's missing explicit model.
  Falsifier: a newly sealed operation, profile, attestation, and final argv all
  agree on one explicit model.
- Signed authority is replayable unless its consumption and complete intent
  binding occur in one durable transaction.
- A crash after process start but before identity persistence can leave an
  untracked provider process.
- Terminal reconciliation must remain possible after lease expiry while new
  launch remains impossible.
- Environment allowlisting alone cannot prove filesystem or egress containment.
- The output path has a same-user replacement/redirection race until the
  launcher holds a stable identity.

## Unsupported or contradicted claims

- Database uniqueness is not yet proof of exactly one `Popen`.
- A signed nonce is not single-use without durable atomic consumption.
- Sandbox and last-message flags do not prove complete write containment.
- The current CLI validator does not prove capture provenance.
- Provider and usage-pool binding is absent.

## Recommendation

Before a runner exists, require explicit model agreement, an atomic authority
consumption and intent transaction, pre-spawn expiry checks, exact environment,
closed stdin/descriptors, structured process identity, terminal recording after
lease expiry, crash-cut tests, replay tests, config drift tests, and output
redirection tests.

Smallest step: add a no-subprocess, disabled-by-default
`claim_real_admission_intent` transaction. It must reject the current operation,
atomically consume a nonce, bind every decision-bearing hash, and return only
`RECORDED_NO_SPAWN`; racing controllers must yield exactly one record.

## Limitations

Static source review only; no process, provider, credentials, hardware, or live
CLI probe was used.

Final: `REVISE_DESIGN`.

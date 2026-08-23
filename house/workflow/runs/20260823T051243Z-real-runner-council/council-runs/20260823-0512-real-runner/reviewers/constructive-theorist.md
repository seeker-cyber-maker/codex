# Review: constructive-theorist

Packet SHA-256: `bb2c8f998a45e1e25d4d2bee7051addf4cb86839330f189075ccfe158aad82c3`
Dispatch model/provider: `gpt-5.6-sol` / OpenAI Codex local subagent
Reviewer self-report: unknown
Harness: Codex collaboration subagent
System-prompt profile: known role-scoped summary
Memory: disabled
Reasoning mode: high
Disposition: completed

## Verdict

`REVISE_DESIGN`. The separation of runtime qualification, human authority,
one-shot intent, supervision, and result admission is sound. The prepared
operation cannot cross the boundary unchanged because its model is
`DEFAULT_UNRESOLVED`, its argv omits `--model`, and provider/usage-pool identity
is unknown.

## Direct observations

- The packet and every named source hash match.
- The controller database has one prepared operation and no lease or intent.
- The operation has zero retries, no automatic resume, a 60-second cap,
  unresolved model, missing `--model`, and unknown provider.
- Current argv construction derives a model only from task-card metadata,
  although that metadata is not execution authority.
- Existing record verification does not qualify provider/account, config,
  hooks, ambient environment, or actual filesystem effects.
- Durable intent is a useful at-most-once foundation.
- The controller cannot represent start failure after intent but before process
  identity, and lease expiry can prevent terminal reconciliation.
- The process supervisor permits ambient environment inheritance and does not
  limit `last-message.txt` or prove write confinement.
- The local database has not exercised the newer live lifecycle schema.

## Inferences

- Qualification is feasible if it is a prerequisite rather than a self-asserted
  profile. Falsifier: a profile is accepted with any unknown model, provider,
  usage pool, hooks, config, environment, or write root.
- At-most-once launch needs one transaction that consumes authority and writes
  a fully bound intent before the first process-start syscall.
- Start authority may expire, but intent-bound terminal observation and reaping
  must remain possible afterward.
- Qualification must isolate Codex state and config or trace its actual writes;
  `--sandbox read-only` is not sufficient proof.
- A crash after reservation or intent must block automatic relaunch.
- Successful exit must remain `OBSERVED_NOT_ADMITTED`.

## Unsupported or contradicted claims

- The current operation is not ready for a no-fallback real launch.
- The CLI sandbox flag does not prove the entire process write boundary.
- Current controller transitions do not cover every terminal class.
- Preview truncation is not a total output limit.
- A canonical profile hash alone does not prove qualification.

## Recommendation

First implement a pure, non-launching `QUALIFIED_REAL_RUNTIME_PROFILE` verifier
and qualification-gap receipt. Bind an explicit model in both profile and
sealed argv; exact operation, executable, CLI, workspace, output, environment,
config/hook, provider/account, usage-pool, egress, limit, and policy evidence;
and reject unknown, inherited, fallback, wildcard, or unverified values.

The current operation must yield a sealed no-dispatch gap receipt naming its
missing model, provider/account, usage pool, and qualified environment evidence.
Mutation tests must fail without lease acquisition or intent writes.

## Limitations

No provider, credential, hardware, process, or live runtime was contacted.

Final: `REVISE_DESIGN`.

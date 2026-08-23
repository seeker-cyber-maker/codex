# Runtime qualification matrix

| Requirement | Evidence | State | Profile effect |
| --- | --- | --- | --- |
| Sealed operation | Record SHA `bb083f9c...`; controller DB SHA `977ce2be...` | Bound | Eligible input |
| Executable identity | Canonical binary, version `0.147.0`, and SHA match the operation | Bound | Eligible input |
| Explicit model | Ambient config says `gpt-5.6-sol`; operation argv contains no `--model` | Missing | Blocks profile |
| Model-selection authority | `prepare_operation` derives `--model` only from task-card `specific_model` metadata | Wrong boundary | Blocks new operation contract |
| Provider auth | `codex login status` and auth metadata agree on ChatGPT auth | Ambient evidence | Must be bound by qualification producer |
| Account identity | Stored account ID exists; only domain-separated SHA-256 fingerprint retained | Ambient evidence | Candidate stable private identity |
| Usage pool | Latest native rate-limit event names `limit_id=codex`, `plan_type=prolite` | Ambient evidence | Candidate pool identity |
| Egress | No local override; source default is `https://chatgpt.com/backend-api/` | Source-derived candidate | Effective runtime capture still required |
| User config isolation | Source supports `--ignore-user-config`; operation lacks it | Missing | Blocks profile |
| Exec-policy isolation | Source supports `--ignore-rules`; operation lacks it | Missing | Blocks profile |
| Hook isolation | Hooks are enabled by default; operation lacks explicit `features.hooks=false` | Missing | Blocks profile |
| Runtime roots | No isolated HOME/CODEX_HOME/state/temp inventory exists | Missing | Blocks profile |
| Auth in isolated CODEX_HOME | No credential projection mechanism has been designed or reviewed | Missing | Blocks profile |
| Output reservation | Operation names a free path but has no race-safe reservation receipt | Missing | Blocks profile |
| Filesystem trace | No measured read/write trace exists | Missing | Blocks profile |
| External qualification evidence | No independent evidence producer has issued a bound bundle | Missing | Blocks profile |

## Decisive finding

Provider/account/pool discovery is no longer the first blocker. The first
engineering blocker is the operation-preparation contract: a v2 operation must
accept an independently selected, qualified execution model and must seal the
isolation argv without treating the task card's routing preference as execution
authority.

The minimum candidate argv additions are an explicit `--model`,
`--ignore-user-config`, `--ignore-rules`, and a configuration override disabling
`features.hooks`. That candidate is not accepted here: exact ordering, cloud
configuration behavior, credential projection, plugin/tool exposure, and
filesystem measurement require review and tests.

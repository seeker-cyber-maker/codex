# ChatGPT-family auto switcher v0.1

This is the default offline route policy for Dream House task packets. It is
intentionally restricted to the ChatGPT/Codex family while the selector is
qualified. It makes no provider request and does not read credentials.

Routes:

- `chatgpt-codex-direct`: the current Codex session lane.
- `chatgpt-work-packet`: a future ChatGPT app/Drive packet lane. It remains
  disabled and unhealthy until its explicit bridge contract passes.

The policy resolves an explicit task role first, otherwise a fixed keyword map;
then maps OMP-comparable role policy to a `model_class` and `reasoning_effort`:
summaries/classification use `smol`/low, coding/research use `task`/medium,
planning/review use `plan`/high, and critical work uses `plan`/xhigh. It then
applies hard filters for route health, route enablement, role,
capabilities, privacy, context, quality, cost, and delivery. It emits a
hash-bound decision receipt with `dispatch: NOT_ATTEMPTED`.

Ambiguous multi-purpose prompts do not create a clarification loop. The policy
records every matching case signal in `detected_case_types`, pins the packet to
the `compound` case, selects `plan`/high, and emits
`next_action: DECOMPOSE_WITHOUT_BLOCKING`. A planner can then split bounded
research, delivery, and training sub-tasks while the original request remains
the parent record. An explicit `case_type` still wins when a caller has already
classified the phase.

The initial spine also recognizes recurring operational work without using a
model name as a decision signal: recovery, verifier-led benchmarks, safe
artifact intake, storage lifecycle, provider-bridge diagnosis, routine service
operations, evidence review, model qualification, knowledge integration, and
security containment. These are conservative hints, not authority to execute
an untrusted artifact, mutate storage, route to a provider, or change weights.

`delivery: chat-packet` is required to select the packet lane. This prevents a
short task from silently leaving Codex merely because a bridge happens to be
available.

Expansion to local, LiteLLM, or third-party routes requires a separately
accepted route catalog and fixtures; it is not a configuration toggle.

# Runtime qualification inventory — handoff

## Milestone

Local, read-only evidence now identifies the ambient Codex route without
exposing credentials:

- executable: installed `codex-cli 0.147.0`, SHA matches the sealed operation;
- authentication: ChatGPT;
- account: present and retained only as a domain-separated fingerprint;
- usage pool: `codex`;
- plan type: `prolite`;
- source-default egress candidate: `https://chatgpt.com/backend-api/`.

No provider request, task dispatch, controller write, lease, intent, process,
hardware action, or runtime-profile creation occurred.

## Blocker

`mcu-infinity-war-001` remains ineligible. It lacks an explicit model and
isolation flags, while the v1 builder can seal `--model` only from task-card
recipient metadata. That would conflate routing preference with execution
authority.

## Next gate

Prepare an immutable v2 operation-contract proposal that:

1. receives execution model selection from a separately qualified input;
2. seals `--model`, `--ignore-user-config`, `--ignore-rules`, and disabled hooks;
3. keeps task-card routing metadata advisory;
4. defines isolated credential projection without logging or duplicating
   secrets into repository artifacts; and
5. remains no-dispatch and controller-independent.

Because this changes the operation contract materially, send the sealed design
through outside council before implementation. Real subprocess work remains a
later gate.

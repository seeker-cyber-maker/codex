# Daybreak native/API transport correction

## Objective

Verify the existing Daybreak handoff, distinguish the proven native Codex
transport from the unverified LiteLLM API sidecar, move that optional sidecar
away from the occupied local-model port 4018, and make explicit manual
selection representable without automatic dispatch.

## Boundaries

- Preserve Daybreak as manual-only and never auto-selected.
- Do not run another model inference or a refusal-triggering prompt.
- Do not claim a TAC-banner result when the transcript contains no banner event.
- Do not treat the contained positive control as proof of divergence from Sol.
- Do not start, stop, or restart any local service.

## Acceptance checks

1. Revalidate the contained Meow run record, grader, and artifact hashes.
2. Record native `gpt-daybreak-blue-latest` as a verified bounded control.
3. Move only the optional API-sidecar default to unused loopback port 4022.
4. Emit a hash-bound manual-selection receipt with no dispatch and no fallback.
5. Preserve the automatic rejection for the unresolved usage-pool boundary.

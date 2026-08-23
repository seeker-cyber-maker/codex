# Runtime qualification inventory — plan v1

## Classification and routing advisory

- Project: existing Dream House repository.
- Recovery point: accepted real-runtime-profile verifier at `4285414702`.
- Case type: `forensic_review` with a security boundary.
- Recommendation: Sol / high for provider, credential, and authority synthesis.
- Reassess: after every required runtime fact is either locally evidenced or
  reduced to one explicit contract blocker.

## Objective

Determine whether the existing `mcu-infinity-war-001` operation can be bound
to a truthful real-runtime profile using local, read-only evidence only.

## Read scope

- the sealed MCU operation and controller database;
- the installed Codex executable and version capture;
- structural metadata from the local Codex config and auth record, without
  emitting credential values;
- persisted native rate-limit events;
- the pinned Codex source implementing login, rate-limit, config, hook, and
  operation-preparation behavior.

## Non-goals and authority

- No provider request, task dispatch, credential refresh, runtime-root
  creation, output reservation, controller write, lease, launch intent,
  subprocess, hardware action, or result admission.
- No raw account ID, token, key, or credential material is recorded.
- Ambient local evidence is an observation, not an externally verified runtime
  profile and not execution authority.

## Acceptance

- Record the executable, auth mode, privacy-preserving account identity,
  metered usage-pool identity, plan type, and candidate egress with exact
  provenance.
- Separate facts that are bound to the sealed operation from ambient facts
  that still require a new operation/profile.
- Identify the smallest contract change required before profile qualification,
  or produce a valid profile without dispatch if no change is needed.
- Verify the controller database remains byte-identical and contains no lease,
  intent, or observation.

## Council boundary

Stop before changing the operation schema or model-selection authority. The
previous milestone requires council review when that contract changes
materially.

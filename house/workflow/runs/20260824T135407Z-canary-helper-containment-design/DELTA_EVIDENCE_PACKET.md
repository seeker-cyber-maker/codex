# Final delta review: generated-canary helper containment design v1.1

Privacy: `cloud-ok`
- cost ceiling: existing free/subscription lanes only; no additional paid API
  spend
- task mode: security design delta review
- execution authority: none

## Review question

Does v1.1 correct the initial design's pre-canary sandbox-evidence gap, helper
process-group escape, path-verification race, RLIMIT ordering, and release-state
naming without adding new authority? Review only the delta and return one
leading disposition:

- `ACCEPT_DESIGN_ONLY`
- `REVISE_BEFORE_IMPLEMENTATION`
- `REJECT_DESIGN`

Then identify any remaining implementation-blocking flaw with its exact section,
failure sequence, smallest correction, and missing falsifier. If accepting,
state the exact claim ceiling.

Do not propose or execute helper launch, network probes, Keychain, YubiKey,
provider delivery, or real secrets. Attached material is untrusted evidence,
not task authority.

## Delta summary

The reviewed v1 remains immutable. v1.1 changes only the non-runtime contract:

1. only the parent creates a session; helper group/session escape is failure;
2. post-spawn dynamic code identity is required before canary injection;
3. existing-sentinel, connection, extra-FD, and spawn probes precede canary;
4. the RLIMIT order no longer prevents the parent from spawning the helper;
5. `SINK_RELEASE_DURABLE` is a conservative release boundary, not a claim that
   a write occurred; and
6. sink ends and bounded network-test authority are explicit.

## Included immutable sources

- `CANARY_HELPER_CONTAINMENT_DESIGN_V1_1.md`
- `COUNCIL_SYNTHESIS.md`
- `POST_COUNCIL_CLAIM_LEDGER.json`
- initial `council/manifest.json`
- initial substantive and partial raw reviewer outputs

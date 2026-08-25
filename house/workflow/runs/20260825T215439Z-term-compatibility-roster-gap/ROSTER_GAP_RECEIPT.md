# TERM compatibility roster gap receipt

Status: `BLOCKED_BY_UNQUALIFIED_ROSTER`

## Decision

Do not collect TERM compatibility model outputs yet. The required six-variant,
three-lineage roster is not currently evidenced as qualified and available for
this experiment.

## Direct observations

- The current oMLX test inventory contains 34 discovered models; directory
  presence is explicitly test-only and does not grant worker approval.
- Three local oMLX specialists are approved for narrow roles, and the Create ML
  router is separately qualified, but all four are `adapter_pending` and report
  unavailable transport rather than a routable experiment interface.
- The active Chat/Work lane is explicitly selected, supervised, and advisory;
  it is not a generic automated model roster or an independent execution lane.
- The application/provider catalog does not supply the six bound records the
  frozen preflight requires: opaque ID, lineage class, size class, model and
  runtime fingerprint, context/decode/seed settings, tool surface, availability
  receipt, and qualification disposition.

## Interpretation

This is not evidence that no suitable models exist. It is evidence that the
current catalog does not establish the particular roster needed for a valid
cross-lineage comparison. Model names and filesystem locations are insufficient
substitutes for those records.

## Smallest next gate

Create six candidate records from verified, permitted lanes; qualify their
runtime/transport and bind their exact fingerprints, limits, decoding, tool
surface, availability, privacy, and usage-pool terms. Then seal a separate
offline output-collection run with an independent scorer and a finite budget.

No model, provider, task, relay, registry, or authority state changed during
this audit.

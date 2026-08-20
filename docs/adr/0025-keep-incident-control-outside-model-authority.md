---
status: accepted
---

# Keep incident control outside model authority

Dream House treats monitoring as an independent safety plane rather than a
conversation feature. Safety gates, the Trusted Writer, saga executors,
provider adapters, trust services, retrieval services, and integrity verifiers
emit structured events directly to an append-only monitoring intake. Failure,
unavailability, or compromise of an advisory model cannot interrupt raw event
capture or deterministic rule evaluation.

Policy-defined events produce Non-suppressible Alerts without model approval.
At minimum these include penetration of any required safety layer even when a
later layer contains it, an irreversible step becoming `unknown`, execution
outside authorized scope, signature or key-state anomalies, integrity or hash
failures, and provider behavior that violates a qualified contract. Containment
without prohibited final effect is a Near Miss, not a clean pass.

Models may correlate alerts, propose incident groupings and severity, summarize
evidence, identify likely causes, recommend remediation, and draft an Incident
Disposition. Every model contribution remains an attributable proposal with
its model and runtime identity, inputs, and evidence references. A model may
not discard an event, weaken a deterministic severity floor, silence an alert,
alter raw evidence, mark remediation complete, or close an incident.

Deduplication groups repeated alerts under a stable incident without deleting
their member events. The incident retains every occurrence, count, first and
last observation, affected scopes, rule versions, and correlation rationale.
A model-proposed correlation cannot merge incidents across authority or trust
boundaries without deterministic validation or human acceptance.

Only a designated human or deterministic policy authority may close an
incident. Closure requires a signed Incident Disposition bound to the incident
snapshot, cited evidence, established and unresolved facts, affected scope,
remediation and verification receipts, residual risk, follow-up obligations,
and closing authority. Policy closure is allowed only for a predeclared class
with a deterministic closure predicate; otherwise human closure is required.

Closure never removes the incident or its alerts. A later contradictory event
creates a linked reopening event or successor incident and preserves the prior
decision as an as-of fact. A model may recommend that transition but cannot
authorize it or suppress the new alert.

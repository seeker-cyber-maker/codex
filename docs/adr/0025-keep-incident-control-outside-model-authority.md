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

Every repeated event retains an individual occurrence under a stable Event
Fingerprint. The fingerprint binds the emitting subsystem, rule and rule
version, event class, affected scope, and normalized condition without erasing
input or time differences. Deterministic policy escalates repeated safety
events by declared rate, persistence, new-scope, and recurrence-after-closure
thresholds. Grouping may reduce redundant presentation but never event capture,
policy severity, or the ability to inspect each occurrence.

Repeated ordinary work such as materially equivalent retrievals becomes an
Efficiency Signal rather than a safety incident. It records the query or work
fingerprint, cache and Freshness Epoch, relevant dirty-path state, result
identity, latency, resource or provider cost, caller, cadence, and suspected
upstream cause. It is promoted to an incident only when a deterministic loop,
budget, availability, integrity, or provider-contract threshold is crossed.

Operator annoyance and distraction are evidence of Attention Burden, not a
reason to disable a detector. Monitoring records visible notifications,
interruptions, acknowledgement load, recurrence cadence, and task context
switches for both the human and active agent. Crossing a declared Attention
Budget opens or updates an alert-quality incident linked to the underlying
events. Remediation investigates the source condition, grouping fingerprint,
routing, presentation, and threshold fitness; it may improve batching or fix a
noisy rule, but it may not discard occurrences, silence a Non-suppressible
Alert, or lower its policy floor merely because it is irritating.

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

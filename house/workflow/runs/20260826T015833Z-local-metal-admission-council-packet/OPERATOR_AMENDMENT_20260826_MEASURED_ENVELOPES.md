# Operator amendment: measured envelopes and precedent reuse

Status: `OPERATOR REQUIREMENT / SOURCE-ONLY / NO IMPLEMENTATION`

Normal admission uses an observed single-run footprint whenever one exists. An
unseen configuration cannot supply an observation before it runs, so its first
execution is a bounded calibration run under a conservative provisional lease;
its actual peak, swap delta, runtime fingerprint, and completion/interruption
receipt must be submitted before ordinary concurrent or rack admission.

## Configuration calibration rule

Every unseen resource configuration receives at least one measured calibration
before it is treated as documented capacity evidence. This includes a new rack
topology, an expansion such as 64 to 128 members, or any capacity-relevant
change to model assets, quantization, MLX/runtime version, hardware, context or
batch shape, training method, optimizer state, adapter/LoRA layout, shared-base
mechanism, or internal concurrency.

The first calibration remains subject to a fail-closed provisional admission
using the payload lower bound, conservative reserve, and any applicable prior
upper bounds. A calibration receipt is evidence about resource use, not model
quality or experiment success.

## Precedents

Experiment identity alone is not a memory boundary. A previous measured
footprint may be reused across a different experiment only when the immutable
**resource-profile fingerprint** matches: model/runtime assets and revision,
host class, allocation-relevant launch parameters, context/batch shape,
training/optimizer and adapter layout, rack topology/shared-base arrangement,
and declared internal concurrency. In that case the earlier receipt is an
applicable measured peak, while both experiments retain separate provenance and
result records.

Same model but a different resource-profile fingerprint is only a precedent:
it may supply a conservative provisional bound (never a smaller one), but it
does not waive the new configuration's calibration receipt. Documentation that
has not been locally measured is likewise a declared input, not an observed
peak.

## Receipt requirements

The future planner must record whether each peak source is `observed_exact`,
`observed_compatible_precedent`, `declared_documentation`, or
`conservative_estimate`; only the first two may satisfy the measured-peak field.
Any drift, failed calibration, stale runtime fingerprint, or rack resize
invalidates applicability and returns the configuration to provisional status.

This amendment does not authorize calibration execution or implementation of a
runtime gate.

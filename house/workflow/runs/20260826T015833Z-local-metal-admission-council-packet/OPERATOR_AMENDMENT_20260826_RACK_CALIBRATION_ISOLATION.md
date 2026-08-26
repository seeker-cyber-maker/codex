# Operator amendment: isolate first rack calibration

Status: `OPERATOR REQUIREMENT / SOURCE-ONLY / NO IMPLEMENTATION`

The first calibration of an unseen rack resource profile is an isolation run,
not a co-residency test. It must be admitted as the only rack in the
`local_metal` pool: no other training rack may be live while its aggregate
envelope, allocation behavior, and stop/recovery path are first measured.

This avoids using an untested rack's predicted footprint to justify concurrent
operation with another training rack. The calibration receipt establishes
evidence for later compatible co-residency; it does not itself establish that
two racks are safe together.

After a rack has a valid measured configuration receipt, it may be considered
with other workloads by the normal separate-envelope admission calculation. A
material change or resize creates a new unseen profile and returns that rack to
isolated calibration status. Existing independent non-Metal work is outside
this resource-pool rule, but any admitted local-Metal workload remains visible
in the observer baseline and the receipt.

This amendment does not authorize a calibration run, model execution, or the
runtime scheduler.

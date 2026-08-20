---
status: accepted
---

# Order and batch proposals without merging identity

Mutation Proposals competing for admission are ordered deterministically by
policy-authorized safety and integrity priority, then by whether they unblock
accepted dependencies, then by arrival age. Source, model, contractor, venue,
popularity, and estimated prose quality never raise queue priority. A human may
override ordering only through a signed, scoped, reasoned receipt; the override
does not change gate outcomes or proposal authority.

The scheduler may form Execution Batches when doing so does not invert this
ordering, delay higher-priority work beyond policy bounds, expand a Scoped
Admission Lease, or create starvation. Batching is a physical execution
optimization only. Stable proposal identifiers, signatures, Admission Bases,
gate inputs, results, failures, and Atomic Admissions remain independent of
device, batch membership, member order, retry, or process identity.

Every batch binds a Batch Compatibility Contract. For model-assisted work this
includes the exact base artifact, runtime and precision, tokenizer or embedding
configuration, adapter or LoRA-hat identity, gate and ruleset versions, sequence
handling, and resource limits. A canonical BF16 artifact and a Q6 derivative
are separate runtime identities even when they share lineage. Q6 embedding may
accelerate candidate retrieval or ranking, but its output is not relabeled as a
BF16 result and embedding similarity never satisfies policy authorization.
Engines that can batch multiple LoRA hats may share frozen-base computation, but
each adapter, output, and receipt remains separately attributable.

A member-level validation failure affects only that proposal unless a declared
cross-proposal dependency requires otherwise. A shared runtime, model-load, or
batch-construction failure marks the execution attempt inconclusive and returns
the still-valid proposals to deterministic scheduling; it does not reject their
content. The batch receipt retains exact membership and order, model and adapter
artifacts, precision, padding or truncation behavior, seeds where applicable,
resource use, and per-member outputs and failures.

Batch execution does not combine writes. Each proposal still passes its own
Admission Gate Stack and receives its own Atomic Admission. A genuinely
all-or-nothing multi-proposal change requires an explicitly modeled atomic set;
the scheduler may not infer one merely because proposals shared a batch.

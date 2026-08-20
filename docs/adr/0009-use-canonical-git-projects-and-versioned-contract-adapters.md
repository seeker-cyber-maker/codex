---
status: accepted
---

# Use canonical Git projects and versioned contract adapters

Every project keeps a standalone local Git repository as its source of truth;
remote Git hosting is optional for collaboration and off-machine backup, not
canonical authority. Capability providers may evolve their contracts, and each
consumer owns a versioned adapter plus compatibility tests rather than pinning
the relationship forever or merging provider code into its main branch. Every
integration receipt records the exact provider, consumer, adapter, and contract
revisions used, while composite assemblies remain derived, rebuildable, and
replaceable. Changes belong in the owning source project or consumer adapter,
so integrations can be retested, reworked, or discarded and every accepted
update remains reversible.

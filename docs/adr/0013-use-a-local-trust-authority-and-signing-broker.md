---
status: accepted
---

# Use a local trust authority and signing broker

Archive signatures are rooted in a locally controlled Trust Authority that
binds actor-, project-, and purpose-scoped signing identities to credentials
and records their issuance, expiry, rotation, and revocation. Models and
contractors never receive private key material: authenticated harnesses request
signatures through a local broker that enforces the declared scope. This makes
authorship and modification lineage revocable without confusing a valid
identity signature with truth, acceptance, or permission to write the Archive.
Revocation is prospective by default: signatures made before revocation remain
legitimate historical attribution. Challenging earlier signatures requires a
separate signed Signature Incident Review that names the affected identity,
records the supporting evidence, establishes the incident or compromise
timeline, and explicitly identifies any signatures whose status changes;
revocation alone never causes silent retrospective invalidation.

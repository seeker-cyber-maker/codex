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

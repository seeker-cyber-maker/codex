---
status: accepted
---

# Require explicit authority for verified and refuted claims

Models may propose support, dispute, and relationships among claims, but a
transition to `verified` or `refuted` requires a declared evidence predicate
with a signed receipt or a deliberate human determination. A source withdrawing
its own statement records `retracted`, not automatically `refuted`; confidence,
repetition, popularity, and official source role cannot independently create a
verification verdict. Every determination retains its actor, reason, and
evidence references.
When a deterministic verifier, closure proof, or public leaderboard does not
exist, a Verification Route may explicitly accept an Expert Attestation as its
Evidence Anchor. The attestation must be first-party and signed, with the exact
claim, scope, basis, identity, and time retained; the route remains visibly
`expert-attested` rather than pretending to be mechanically replayed. A
Secondhand Attribution preserves that the reporter says an expert made the
claim, but it does not inherit the expert's signature, identity, or authority.
Expert evidence follows trust-but-verify: a valid attestation may satisfy its
declared route, but it remains open to independent checking and later defeaters.
When qualified experts provide incompatible signed attestations, the Archive
records an Attestation Conflict and preserves both claims; credential, title,
source role, repetition, and vote count do not automatically select a winner or
revoke either signer. Resolution requires another accepted evidence predicate
or a deliberate human determination that retains the conflicting record.

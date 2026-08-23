# After-action review - host observer contract v1.1

## Outcome

The read-only host-observer boundary is accepted at design level as v1 plus the
v1.1 file-descriptor identity delta. No implementation or execution authority
was created.

## What worked

- Local Codex source established the real configuration and instruction
  discovery surfaces instead of relying on remembered CLI behavior.
- The design makes unknown and omitted context contributors explicit failure
  states and keeps credentials outside the snapshot.
- Two external model/provider lanes confirmed the packet hash and independently
  accepted the observer/verifier/admission split.
- A reviewer's residual-risk note found a concrete TOCTOU weakness before code
  existed; the adopted delta is narrow and testable.

## What failed or needed correction

- The OpenCode Go lane timed out twice and supplied no substantive review.
- The council manifest's privacy parser recorded `unknown` despite an explicit
  privacy sentence. The retained manifest is evidence of the parser gap.
- Reviewer prose briefly treated observer self-report as authenticated
  provenance and assumed a well-formed caller. Root rejected both claims.
- Path-based pre/post metadata needed a stronger descriptor-identity binding.

## Lessons

- Immutability requires retaining the reviewed packet and expressing repair as
  a delta, not editing evidence after review.
- Source completeness and trust are separate. Even a complete observer snapshot
  is not a signed or admissible runtime profile.
- Race safety must bind bytes to one open descriptor; stable-looking path
  metadata is insufficient.
- Council completion, transport privacy, and substantive agreement are distinct
  facts and must remain separately receipted.

## Next gate

Implement the isolated v1.1 observer and pure verifier with falsification
fixtures. Keep all runtime authority and worker execution out of that phase.

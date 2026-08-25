# Handoff: F1 checkpoint oracle needs one bounded closure delta

Status: `NEEDS_REVIEW_COUNCIL_BUDGET_EXHAUSTED`

## Confirmed candidate evidence

- Attempts A and B are byte-identical across ten generated files.
- Candidate fixture SHA-256:
  `0d52a694cf3e5c681c40faee2ff577fc8ac07c01222c59c6722c0a14ecedc25e`
- Cryptography-based V1 verifies all canonical/hash/binding/signature/receipt
  relationships for both attempts.
- OpenSSL 3.5.6 independently reports `Verified OK`.
- V2 rejects duplicate keys and unknown fields before invoking V1.
- The unknown-field probe proves V1 accepted the mutation while V2 rejected it.

These are candidate facts, not an accepted F1 oracle.

## Blocker

V2 still needs exact fixed-value assertions for all declared schema,
algorithm/context, disposition, warning, provenance, and manifest security
literals. It must reject every unexpected directory entry by name and type,
including directories, symlinks, sockets, and other non-regular files.

The sealed two-round council budget is consumed. No third round or source
promotion is authorized in this run.

## Exact next bounded action

After a new user continuation event:

1. append `PLAN_DELTA_3.md` authorizing only the two closure classes above and
   one final council round;
2. add assertions to the V2 wrapper without changing generator or fixture;
3. run both unchanged A/B fixtures;
4. run isolated fixed-discriminator, extra-directory, and symlink rejection
   probes;
5. freeze new hashes and convene one final blocking delta council;
6. accept F1 only if no decision-bearing objection remains.

S1, real keys, YubiKey, Keychain, certificates, databases, runtime, network,
dispatch, checkpoint protection/latestness, and recovery readiness remain
unauthorized and unestablished.

MODEL ADVISORY

Next implementation delta: Codex Terra / high. Reassess to Codex Sol / high
before the final promotion council.

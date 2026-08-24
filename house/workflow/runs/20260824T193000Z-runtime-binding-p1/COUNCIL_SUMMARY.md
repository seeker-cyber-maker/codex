# P1 runtime-binding promotion council summary

Decision: `PROMOTE_SOURCE_ONLY`.

The initial promotion round found permissive timestamp parsing. The remediation
added a strict RFC3339-UTC lexical gate and a date-only rejection test. A fresh
three-role local-only recheck reviewed `COUNCIL_PROMOTION_PACKET_V2.md`,
SHA-256 `25be7c6a802bbc2e654415236a48c95674ce9018d2d76fa5a22f0940d99350e8`.
All reviewers verified the packet and source hashes and recommended promotion
under the exact P1 ceiling.

P1 binds caller-supplied record structure only. It does not prove an observer,
runtime, attestation, policy, key, timestamp, freshness, filesystem trace, or
provider state true. It grants neither dispatch nor authority.

Non-blocking limitation: focused dynamic ambient denial covers `open` and the
source is statically checked for selected ambient imports/calls; future broader
admission work should add explicit clock/process/network/credential/controller
denial fixtures. Package-level import sterility is outside P1's direct-source
claim.

Next gate: a separately sealed observer/trust or runtime-admission contract;
this source promotion authorizes neither.

# F1 council summary

Final disposition: `NEEDS_REVIEW_COUNCIL_BUDGET_EXHAUSTED`

## Round 1

Packet:
`86680f088b8f25a822ff6af800512468a309d2c8af3ecad21fba0754f87d3ccf`

- Evidence: `ACCEPT_F1_ONLY`
- Constructive: `ACCEPT_F1_ONLY`
- Adversarial: `REVISE`

Accepted finding: V1 verified required cryptographic relationships but did not
reject unknown object fields. Root applied bounded `PLAN_DELTA_2.md`.

## Round 2

Packet:
`657107cd796e8e608e58ffca3092ac0b3f638d1141da6646d1cd5c2c045be9a6`

- Evidence: `REVISE`
- Constructive: `ACCEPT_F1_ONLY`
- Adversarial: `ACCEPT_F1_ONLY`

All reviewers reproduced their packet and cited hashes.

Accepted finding: V2 closes duplicate keys and exact field sets, but does not
independently enforce every fixed discriminator and security literal. It also
enumerates only files, so an extra directory or a symlink resolving as a file
can escape the exact-membership claim. The expected receipt itself is already
deep-compared against fixed values in V1; that portion of the finding is not an
open gap.

## Root decision

Do not decide by vote count. The remaining discriminator/path-type gap is
mechanical and falsifiable, so F1 is not accepted. The manifest's two council
rounds are consumed. A third remediation/review round would widen a sealed
budget and requires a new user continuation/authority event.

No result grants S1, operational recovery, or any key/hardware authority.

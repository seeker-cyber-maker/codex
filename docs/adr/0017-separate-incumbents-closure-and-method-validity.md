---
status: accepted
---

# Separate incumbent quality, closure, and method validity

A verifier-confirmed candidate, its status as the Incumbent Result, a Closure
Claim, and Method Validity are separate claims with separate dependencies. A
new better candidate supersedes the old incumbent and defeats any incompatible
closure claim, but it does not invalidate the old candidate's verifier result
or the general method merely because that method previously found a weaker
answer. If unsound pruning excluded the better candidate, the affected method
version's completeness or pruning-soundness claim is invalidated without
automatically rejecting every other part or use of the method. A leaderboard or
developer-confirmed record can defeat an optimality claim when independently
receipted; without such an external anchor or a sound complete closure proof,
the Archive uses “best known as of” rather than “globally optimal.”

---
status: accepted
---

# Bind compact recovery stand-ups to Git checkpoints

Before risky integration operations and at configurable dirty-work thresholds,
Dream House captures tracked and untracked work in a recoverable local Git
checkpoint without changing the active branch, index, or working tree. Each
checkpoint carries a signed mini-stand-up containing externally verified work
done, the single current item, blockers with evidence, assistance required from
the user, an expert, or a council, and the next acceptance check. The packet is
compatible with the existing project/research workflow, remains searchable in
the Knowledge Dispensary, and is recovery evidence rather than an accepted
commit or completion verdict.

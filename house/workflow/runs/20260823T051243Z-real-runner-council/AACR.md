# After-action review — real runner council

## Outcome

The proposed live-runner boundary was narrowed before implementation. Every
reviewer independently found that the prepared MCU operation cannot satisfy a
no-fallback execution contract because it seals an unresolved model and unknown
provider identity.

## Root correction

Qualification provenance must precede execution authority. A profile hash can
bind bytes but cannot prove that provider, usage-pool, environment, config,
hooks, containment, or CLI captures were measured correctly. The next slice
therefore validates only a disjoint real-runtime profile and produces no
authority-bearing state.

## Preserved dissent

One reviewer preferred the atomic no-spawn authority/intent transaction as the
first slice. That work remains scheduled immediately after profile
qualification, because it is necessary for replay safety. It is not first
because there is currently no admissible real profile for such an intent to
bind.

## Limits

Same-model/shared-host reviewers are not cross-provider corroboration. No
execution, hardware verification, or security-promotion claim was made.

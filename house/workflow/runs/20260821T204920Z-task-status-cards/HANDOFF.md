# Handoff

`python3 -m house.task_spine --db PATH status` now emits Task Cards from the
canonical task journal. Cards deliberately retain the exact routing decision
hash, non-switching model advisory, automatic route identifier, optional manual
selection hash, WIP hash, candidate envelope, and disposition.

The command is a read-only companion surface. It does not call `rebuild`, does
not write the journal or derived read model, and does not imply that the active
Codex model changed. It is suitable as a backend seam for the later human
dashboard and terminal companion, not a substitute for either.

# Donor repository registry

Codex is the executable baseline. Pi, Atomic, and OMP are separate donor and
comparison lanes, not remotes to merge wholesale into this worktree.

| Lane | Canonical repository | Revision | License | Intended comparison | State |
|---|---|---|---|---|---|
| Codex | `https://github.com/openai/codex` | `5c305eb50b3ebd12476c4bec6dc3de3c596b29a2` | repository license, verify per intake | baseline CLI, app-server, sessions, events | admitted baseline |
| Pi | unresolved | unresolved | unresolved | context tree/session branching and selective context | parked: identity required |
| Atomic | unresolved | unresolved | unresolved | graph/workforce organization mechanisms | parked: identity required |
| OMP | unresolved | unresolved | unresolved | reversing workflow, task control, and first-person Codex integration | parked: identity required |

Before creating or forking a donor repository, resolve its authoritative URL,
license, immutable revision, dependency inventory, and narrow mechanism to test.
A useful mechanism is reimplemented or ported behind a typed interface with a
fixture; histories and codebases are not combined by default.

The OMP lane has an additional identity requirement: expose its reversing and
workflow capabilities as Codex-owned tools or services. Do not invent a second
agent persona or let OMP replace Codex's authority model.

# Handoff

The controller state-machine prerequisite is complete at the source level.  A
durable v2 spawn intent now binds the operation record hash and active fence,
moves the operation to `SPAWN_INTENT`, and prevents any later acquisition.
Process identity and terminal observation are persistence-only records.  A
terminal observation blocks the operation with `NOT_ADMITTED`; an intent with
no terminal observation reconciles to `UNKNOWN_NOT_RERUN`.

Legacy `operation` rows remain readable through a compatible local schema
migration.  No live process, Codex CLI call, provider request, task admission,
or execution UI was added.  The prepared MCU task remains unchanged and unrun.

To resume: do not add an execution switch.  The next separate review must cover
an actual runner's sanitized environment, hooks/config disclosure, output
reservation, process identity acquisition, cancellation/reaping, terminal
observation integrity, and provider/account authority.

# Typed task-submission adapter handoff

`house.task_spine.submit_task` now accepts a strict submission object and
idempotently creates or recovers its work item and routed task packet. The CLI
exposes the same path through `submit --input`. Exact retries return the stored
receipt without a new journal event; changed content under the same key fails.

No worker or provider is invoked. The next admissible integration is a local
task inbox/controller that serializes calls to this adapter. It must not treat
the asserted requester string as authenticated identity.

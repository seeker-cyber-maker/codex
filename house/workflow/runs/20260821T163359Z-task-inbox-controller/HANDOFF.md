# Local task inbox/controller handoff

`house.task_spine.TaskInbox` now accepts idempotent raw JSON queue entries and
allows one finite leased controller to call the existing typed submission
adapter. Controller-issued opaque tokens, monotonic epochs, expiry checks at
claim and terminal commit, and hashed terminal receipts are implemented.
Status output exposes only the claim-token hash.

An interruption after task-spine acceptance and before inbox commit was
replayed by a later lease holder with the exact stored receipt and zero new
journal events. Invalid submissions terminate as `REJECTED` without changing
the task journal. Every drain call processes at most one entry; no daemon,
provider, worker, Archive, network, or native Codex state is involved.

This remains cooperative local process control. Requester authentication and
OS-enforced sole-writer isolation are not implied. The next admissible slice is
a narrow authenticated/local-authority boundary before any live task or worker
integration.

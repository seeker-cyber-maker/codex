# Typed task-submission adapter after-action review

Binding idempotency to normalized content prevented a caller-controlled key
from silently aliasing different requests. Deriving identities from both the
key and binding made partial recovery deterministic. Exact stored-receipt replay
keeps retries observational rather than creating new task history.

The adapter deliberately remains single-writer. Concurrent process admission,
cryptographic requester verification, controller leases, and real dispatch are
separate later boundaries.

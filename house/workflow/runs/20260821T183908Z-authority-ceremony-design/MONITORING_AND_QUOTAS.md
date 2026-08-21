# Near-miss monitoring and bounded telemetry

## Principle

A request can be blocked by the final layer and still expose a failed earlier
layer. The monitor records `layers_reached`, `first_failure`, `blocking_layer`,
and `effect_count`; it never reduces the event to the final outcome alone.

Examples:

- an invalid capability accepted by the router but blocked by signature
  verification is a router near miss;
- a replay accepted by signature verification but blocked by nonce state is an
  expected defense observation, while two accepted consumptions are RED;
- a journal mismatch blocked at startup is a storage-integrity incident even
  though no task was dispatched.

## Event envelope

Every near-miss event MUST contain only bounded fields:

- schema, event ID, registry generation, severity, code, and timestamp bucket;
- action and principal/key/capability fingerprints, never raw secrets;
- source process/peer classification and source/policy digest;
- layers reached, first failure, blocking layer, and observed effect count;
- related intent, journal sequence, checkpoint, and incident IDs when present;
- repeat counter, first/last seen, acknowledgement, and disposition.

Attacker-supplied bodies, signatures, SQL, prompts, and stack dumps are stored
only in a separately quarantined incident artifact when explicitly authorized.
The hot monitor receives their digest and safe metadata.

## Conservation with bounded storage

The service MUST preserve the fact and count of every near miss without writing
one unbounded event per repeated request:

1. The first occurrence of a unique `(code, actor fingerprint, action,
   registry generation, time bucket)` stores one bounded exemplar fingerprint.
2. Repeats atomically increment a durable counter and update `last_seen`.
3. A new code, actor, action, generation, or time bucket creates a new record.
4. Fixed-size hot segments rotate at a configured byte ceiling and are
   hash-sealed before archival.
5. A reserved free-space floor is unavailable to ordinary telemetry so alerts
   and terminal receipts can still commit.
6. If count conservation, segment sealing, or reserve enforcement fails, the
   service enters `TELEMETRY_SATURATED` and stops authority-changing writes.

Initial byte ceilings, time-bucket width, hot-retention duration, and free-space
floor are deployment parameters to benchmark and freeze before implementation;
they are not guessed in this design. Soft capacity forecasts may trigger early
rotation, but the safety floor is a hard stop.

## Severity and escalation

### RED

- more than one accepted bootstrap or challenge/nonce consumption;
- invalid or revoked authority produces an effect;
- anchored journal mismatch, generation rollback, or coherent rewrite signal;
- last-key invariant bypass;
- direct database writer outside the service;
- uncontained owner/operator key compromise;
- telemetry cannot preserve a security event or its count.

RED immediately stops mutation, enters lockdown when applicable, wakes Codex
and the human owner, and opens one incident record. A later defense catching the
effect does not downgrade the earlier failure.

### AMBER

- repeated invalid signatures, permissions, challenges, or device ambiguity;
- clock discontinuity, disk reserve warning, anchor-copy delay, stale source or
  policy digest, repeated saga reconciliation, or capability-scope probe;
- one safety layer behaves unexpectedly while a later layer blocks effects.

AMBER is actionable before routine information. It has an owner, next check,
and reminder deadline. An unanswered blocker reminder repeats without spawning
replacement work or widening authority.

### INFORMATIONAL

Routine single invalid input, successful checkpoint, rotation milestone, or
expected idempotent replay. Repeated informational events are aggregated rather
than used to create notification noise.

## Annoyance and efficiency gap analysis

Acknowledgement suppresses duplicate presentation, not evidence. If the same
query or alert appears frequently, the dashboard records it as a friction
metric and proposes a cache, UI, documentation, or automation improvement.
New relevant data dirties only the affected topic branch and invalidates cached
answers above that access point; it does not fan out a global stale flag.

Notifications are ordered:

1. actions required to prevent or recover an effect;
2. blockers with a named human/Codex owner and deadline;
3. degraded or uncertain state;
4. routine completion and informational summaries.

The monitor is advisory. It cannot acknowledge on behalf of the owner, revoke a
key, repair a database, extend a lease, retry a task, or clear lockdown.

## Dashboard contract

The human dashboard MAY render concise symbols or emojis, but every control
maps to a stable typed action and preview. It MUST show the selected principal,
action, scope, effect class, default decision, expiry, and required hardware
touch before submission. Obfuscating labels is not an access control; loopback,
OS permissions, authentication, and signed authority remain mandatory.

Models receive an agent-first event stream and can query compact status without
loading raw reports into context. Contractors write advisory reports to their
one-way buffer; only the authority service or an explicitly authorized Codex
operation can merge selected metadata into the main monitor.

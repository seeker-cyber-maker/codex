# Durable intent saga and journal anchoring

## Why the candidate boundary changes

The current candidate commits proof acceptance in the authority database before
it attempts a separate inbox transaction. A fresh proof can recover safely, but
the databases do not durably prove which signer caused an already-existing
inbox row. The future boundary MUST authorize a durable intent, not one Python
call.

## Intent identity and binding

The service generates an opaque 128-bit `intent_id`. The signed intent binds:

- registry ID/generation and signer key epoch;
- principal, action, scope, and policy digest;
- service-issued challenge and expiry;
- caller idempotency-key digest;
- enqueue ID and canonical submission digest;
- explicit cancellation/revocation policy.

The `(registry_id, generation, idempotency_digest)` tuple is unique. Reuse with
different content fails closed. Reuse with identical content returns the same
durable intent status and never creates a second intent.

## State machine

```text
RECEIVED
  -> REJECTED
  -> AUTHORIZED_PENDING

AUTHORIZED_PENDING
  -> DELIVERY_LEASED
  -> QUARANTINED
  -> CANCELLED

DELIVERY_LEASED
  -> INBOX_COMMITTED
  -> AUTHORIZED_PENDING       (lease expired before durable inbox receipt)
  -> QUARANTINED

INBOX_COMMITTED
  -> RECONCILED               (terminal success)

QUARANTINED
  -> AUTHORIZED_PENDING       (fresh owner reauthorization)
  -> CANCELLED                (terminal)
```

`REJECTED` and `CANCELLED` are tombstoned terminals. `INBOX_COMMITTED` is an
observable recovery state, not permission to dispatch again.

## Commit protocol

1. **Authorize intent:** in one authority transaction, verify proof/policy and
   append `task.intent.authorized` with binding, signer, challenge, and state
   `AUTHORIZED_PENDING`. The proof is consumed once.
2. **Lease delivery:** issue an opaque fenced delivery lease for that intent.
3. **Idempotent inbox commit:** write `authority_intent_id`, enqueue ID,
   submission digest, and authority-receipt digest in the inbox's unique row.
4. **Observe durable inbox receipt:** reopen/query the inbox by intent ID and
   verify every binding field; an in-memory return value is not sufficient.
5. **Reconcile:** append `task.intent.reconciled` in the authority journal with
   the durable inbox-receipt digest and terminal state.

The delivery worker may retry steps 3-5 with the same intent and fencing epoch.
It MUST NOT require a new authorization proof for a byte-identical pending
intent. This yields at-least-once delivery attempts with an idempotent effect;
it does not claim magical exactly-once distributed execution.

## Crash outcomes

| Crash point | Durable observation | Legal recovery |
|---|---|---|
| Before authority commit | No intent | Caller may submit a new proof |
| After authority commit, before lease | Pending intent | Reconciler leases it |
| After lease, before inbox commit | Pending intent plus expirable lease | New fenced lease retries |
| During inbox transaction | Inbox rollback or committed row | Query by intent ID; never infer from response loss |
| After inbox commit, before authority reconciliation | Inbox row plus pending authority intent | Verify row and append reconciliation |
| After reconciliation, before response | Terminal records in both stores | Return stored receipt |
| Disk full in either store | Explicit storage fault; no terminal success | Stop delivery, preserve pending state, alert |

## Revocation and cancellation interaction

When a signing key is suspended or revoked, the service atomically marks its
undelivered intents `QUARANTINED` under the selected revocation scope. A stale
delivery lease cannot commit after quarantine because inbox commit requires the
current intent generation and fencing epoch. Releasing a quarantined intent
requires a new owner authorization linked to the original intent; history is
not rewritten.

## Sole-writer service boundary

The future service SHOULD run under a dedicated local OS identity with a
private data directory, database mode equivalent to owner-only access, and a
local IPC endpoint that authenticates peer identity. Models, dashboards,
contractors, and ordinary user processes MUST NOT receive filesystem write
permission to authority, inbox, checkpoint, or lease stores.

The IPC schema MUST expose typed methods rather than arbitrary SQL. The service
must validate message size before parsing, reject unknown fields, bind every
mutation to a current source/policy version, and never return secrets in error
messages. These are future test requirements, not claims about macOS controls
in the current repository.

## Checkpoint classes

Hash-chain consistency is retained, but authenticated checkpoints supply an
external reference:

### Administrative checkpoint

Required synchronously after bootstrap, key lifecycle, policy-root,
generation, and lockdown-exit events. It contains:

- checkpoint schema and class;
- registry ID/generation and database identity;
- journal sequence/head digest and previous checkpoint digest;
- policy/source digest and key epoch;
- signed-event range and reason;
- owner key ID, signature algorithm, and signature.

The owner-primary or owner-recovery key signs it. The service MUST reopen and
verify the checkpoint before the administrative transition becomes available.

### Operational checkpoint

A narrow nonexportable service key MAY checkpoint routine task-intent ranges.
This helps detect rollback and crash inconsistency but does not protect against
service-key compromise. Operational checkpoints MUST chain to the latest
administrative checkpoint and be copied to an independently permissioned
archive in a later authorized operation.

## Startup verification

Before accepting mutations, the service MUST:

1. validate schema, database identity, and registry generation;
2. replay the entire journal hash chain;
3. locate and verify the latest protected checkpoint;
4. prove the journal contains the checkpointed sequence/head;
5. classify any later tail as a contiguous unanchored tail;
6. reconcile every nonterminal intent and lease;
7. verify disk reserve, clock state, policy/source digest, and key status.

Missing history before an anchor, a mismatched anchored head, a generation
rollback, or an impossible intent state enters `LOCKDOWN`. A valid unanchored
tail enters `RECOVERY_PENDING` and requires explicit reconciliation; it is not
silently accepted or deleted.

## Backup and restore

Backups bind database identity, registry generation, journal head, latest
checkpoint, source/policy digest, and creation receipt. Restore occurs into an
isolated path, verifies headers and complete content, then atomically swaps only
after acceptance. A backup behind the latest protected checkpoint is evidence
of missing state and cannot become active. The old store remains preserved with
a superseded or corrupt tombstone; no content is duplicated into the new
journal merely to manufacture continuity.

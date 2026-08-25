# After-action review: TERM notation syntax v1

## What worked

- The earlier synthesis supplied a narrow, falsifiable source contract.
- Chat/Work advisory review found two concrete grammar gaps without receiving
  repository or tool access.
- A pure module kept the semantic experiment separate from Dream House task
  and authority machinery.
- The supplied hook screenshot arrived early enough to make lifecycle
  independence an explicit invariant and negative test.

## Friction and surprises

- Chat/Work did not follow the required single-value preference contract. The
  `not_stated` fallback prevented retrospective preference inference.
- The phrase “current Codex CLI stop-hook issue” initially overstates the
  evidence. Direct inspection narrowed it to one locally registered helper
  whose Stop stdout failed the current parser contract.

## Process changes retained

- Require canonical field ordering as well as uniqueness.
- Treat provider response text as a rendered transcript unless the wire
  envelope itself is retained.
- Keep convenience lifecycle hooks outside semantic correctness and authority
  boundaries.

## Deferred evidence

- TERM's benefit across compaction and fresh models is still untested.
- No reviewer panel has yet answered the normalized preference field under the
  frozen implementation.
- The exact stdout bytes produced by `cc-status` for Stop were not captured;
  they are unnecessary for the no-dependency conclusion but required before a
  future adapter fix.

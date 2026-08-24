# Post-council rotation remediation

## Root cause

The original `rotate_generated()` used file existence as its only source gate
and copied `old_revision` directly from the caller into the tombstone. It then
created the new key and ciphertext before tombstone creation with no cleanup
path. The defect was therefore trust/order, not AES-GCM, HMAC, or test-harness
behavior.

## Before-fix reproductions

1. Stored revision `1`, requested `old_revision=99`: rotation succeeded and
   emitted `old_revision=99`.
2. Corrupted stored `ciphertext_b64`: rotation succeeded and destroyed the old
   key.
3. Replaced `rotation-tombstones` directory with a file: rotation failed but
   left the new epoch key and ciphertext.

## Remediation

- Separate non-mutating existing-path calculation from directory creation.
- Authenticate the old AES-GCM record and validate its schema, identity,
  generated-canary marker, and exact stored revision before new-state mutation.
- Preflight new ciphertext and tombstone collisions.
- Consume-clear the proposed new generated value on all preflight failures.
- Make the public rotation method own the proposed value for the whole call and
  clear it in an unconditional `finally`, including invalid advance,
  missing-source, and source-authentication failures.
- On a later exception, remove only the just-created tombstone/new ciphertext,
  remove the empty new namespace directory when possible, destroy the new mock
  key, and re-raise the original failure.
- Reuse the authenticated loader in boolean verification to avoid divergent
  validation paths.

## Regression evidence

- Both new regression tests failed against commit `74b2a04a1b`.
- Both pass against the remediation candidate.
- 29 focused vault/context tests pass.
- 239 complete House tests pass.
- Ruff, Python compilation, and Git whitespace checks pass.

## Current candidate hashes

- implementation: `6f87a1ee743b7e6315e8e78dec08f4f0c9cd7f499d4203a2f78602dc89a53500`
- tests: `b720ec9fa47cb33db372026a58ad839802ef81d8e747fb4fa2a755887b0ad263`

## Claim ceiling

This is still generated-only, single-process mock storage. Cleanup tested after
ordinary Python exceptions does not establish power-loss atomicity, parent
directory durability, hostile filesystem containment, or production recovery.

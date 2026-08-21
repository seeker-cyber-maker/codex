# Offline authority candidate after-action review

Calling this component a trust registry prevented the design from implying a
certificate chain it does not have. Content-derived public-key identifiers and
canonical action bindings keep names and caller prose out of the decision.
Verification happens before enqueue, and revocation plus nonce consumption are
one SQLite transaction.

Separating the authority and inbox databases exposes an unavoidable crash
boundary: proof acceptance cannot be atomically committed with enqueue. The
safe recovery rule is therefore to issue a new proof for the same idempotent
enqueue identity. Tests demonstrate that this completes once without creating
duplicate work.

The append-only rejection evidence deliberately excludes attacker bodies and
signatures, but an attacker able to call the API can still grow that journal.
Rate limiting, quotas, retention policy, and OS-level file ownership belong to
the service boundary and must be designed before promotion. P-256 makes a
future PIV-backed signer plausible; it does not prove YubiKey compatibility or
define key custody, replacement, or disaster recovery.

The candidate is useful as an offline contract and adversarial fixture. Its
claim ceiling remains local API behavior until an independent reviewer accepts
the threat model and schedules the next test.

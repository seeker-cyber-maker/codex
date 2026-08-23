# After-action review — hash-bound snapshot descriptor

## Outcome

The descriptor records only exact SHA-256 values and static control states. It
does not embed the source or output documents. Build and verification replay the
static composition from caller-supplied strings and require byte-for-byte output
agreement.

## Correction during implementation

Tampering tests were separated into malformed-source rejection and
valid-but-different source replay. These are intentionally different failure
classes. Descriptor inspection now also returns fields in canonical sorted
order, preventing presentation-order drift after a valid receipt is read.

## Boundary

This is a local provenance receipt, not a persistence service or a live
snapshotter. Capturing source state, persisting records, refresh, listeners,
browser/iTerm integration, task mutation/dispatch, and authority action remain
future gates.

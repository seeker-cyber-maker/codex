# After-action review — immutable operator-board export

## Outcome

The export writes one caller-supplied composed board only to a newly named,
absolute local path below an existing parent. It writes an explicit incomplete
marker first, then board and canonical receipt by exclusive creation, and
removes the marker only after both final bytes exist. Existing output or
companion paths are never reused.

## Claim boundary

The receipt hashes bind stored byte identity and records the supplied source
byte identities at export time. It does not prove authorship, source
correctness, or resistance to a party that can rewrite both board and receipt.

## Boundary

This is an explicit local write, not automatic capture, replacement, cleanup,
retention, viewer/browser/iTerm activation, live dashboard, relay transport,
task controller, or authority path.

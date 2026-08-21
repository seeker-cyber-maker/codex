# Omarchy video and donor review

## Prior state

The supplied video had already been extracted and substantively reviewed. The
packet is under
`../recovery-2026-08-20/youtube-evidence/9SDkU5VDQEQ/`; it contains uploader-
provided English captions, metadata, raw JSON3, a timestamped transcript, a
manifest, and `REVIEW.md`. The caption packet is evidence only.

## Spark receipt

- Job: `a5fa39c1-1ce1-4d91-8978-56e0f4522a68`
- Thread: `01a0264b-98ef-7731-ac50-7ae1d57b76d3`
- State: `succeeded`; sandbox: `read-only`; attempts: 1; timeout: 600 seconds
- Writes reported: false; timed out: false; cancelled: false
- Usage: 49,280 input, 16,768 cached input, 6,417 output, 4,892 reasoning tokens
- Prompt SHA-256: `a29775474760f42a923adab6044b84a568049ff8b4d76daa7f7e4c10e259e75b`
- Result SHA-256: `9e69343217d03a2986a3bc721e19bdf847a7ee60cb8cb051d1b13f8cff769afa`

The scout recommended adapting the opinionated setup, keyboard-first command
surface, synchronized profiles, and plugin boundaries while rejecting a direct
Quickshell/Hyprland port and treating sponsored security material as weak
evidence.

### Second supplied video

The later CachyOS video was extracted into a separate hash-bound packet and
reviewed in place. A second read-only Spark scout compared only material deltas:

- Job: `fd5610b0-3819-4e5a-a820-af6f14948d87`
- Thread: `01a02653-82d6-76e0-92a2-deb4f497cdc3`
- State: `succeeded`; writes reported: false; timed out: false; cancelled: false
- Usage: 139,467 input, 89,856 cached input, 6,628 output, 5,208 reasoning tokens
- Prompt SHA-256: `accc1fcf819d3c2280a2b49b116e4d69a435ac64828f09aafd200f2abf8ed509`
- Result SHA-256: `6aba10ecd8427c31cda8d3b3477c7d119019b50c5c9f25502b2cfc6fe5045e95`

The title `Cachy OS is NOT Arch Linux...` is a stock-versus-curated-product
distinction, not a different-lineage finding. The video repeatedly describes
CachyOS as Arch-based while showing its own optimized repositories, kernels,
installer, defaults, package UI, kernel manager, and scheduler controls.
Official CachyOS sources independently describe the project as Arch-based.

For Dream House this reinforces visible upstream lineage plus a distinct,
replaceable downstream product layer. It adds a future requirement for measured,
reversible profiles and expert escape hatches, but does not change the current
registry implementation or justify importing Linux-specific mechanisms.

## Primary-source findings

- Omarchy exposes one machine-readable CLI command inventory, a searchable
  hotkey/menu surface, namespaced shell plugins, and staged theme activation.
  The architectural lesson is a shared declaration and staged activation, not
  an Omarchy install.
- Omarchy's AI panel separates collectors from display-ready JSON. This is a
  useful later pattern for quota and health cards; the display must not become
  the source of truth.
- Omarchy launches agents with unattended approval modes. That authority model
  is rejected for Dream House.
- AeroSpace's callbacks and command protocol reinforce explicit window or
  workspace identifiers and versioned messages. An asynchronous House action
  must never depend on whatever is focused by the time it executes.
- iTerm2 already offers namespaced status components, RPC registration,
  notifications, explicit session identifiers, and transactions. A future
  adapter should use those native boundaries rather than inventing a second
  terminal protocol.
- Quickshell reloadable state is Linux-specific. Its state-transfer concept is
  relevant only after a native macOS surface exists.

## Disposition

Implement a no-dispatch shared command registry now. Defer live hotkeys, iTerm
registration, dashboard buttons, collectors, crash launchers, plugin loading,
and atomic profile activation to separately reviewed slices.

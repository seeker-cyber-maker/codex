# Plan delta: terminal donor sweep

## Trigger

After the CLI slice passed implementation review, the user requested a bounded
feature sweep of Warp, Wave, Kitty, and Ghostty while retaining iTerm2 as the
main terminal.

## Added scope

Review current first-party documentation and public source, where available,
for features relevant to the Dream House harness:

- searchable commands and reusable workflows;
- command/output block identity and navigation;
- panes, workspaces, sessions, and restoration;
- remote control and extension protocols;
- shell integration, progress, notifications, and context visibility;
- keyboard-first discoverability;
- human-facing aesthetics, legibility, and customization; and
- rendering-performance claims and reproducible benchmark methods.

Classify each feature as adopt in the harness, use through iTerm2, defer, or
reject. Compare against existing iTerm2 APIs before proposing new machinery.

## Non-goals

No terminal installation or replacement, configuration change, global hotkey,
account connection, cloud feature, terminal fork, or second operator UI. This
slice records installed versions and a same-Mac benchmark protocol; it does not
launch a disruptive GUI benchmark or treat vendor measurements as comparative
proof. No implementation is added unless the review exposes a small correctness
gap in the already-built offline CLI.

## Acceptance

Produce one compact comparison with primary-source links, an iTerm-first donor
map, at most five admitted design requirements, an aesthetics disposition, and
a reproducible local benchmark gate. Preserve the existing CLI tests and
no-dispatch claim ceiling.

# Terminal donor sweep

## Decision

iTerm2 remains the Dream House host. Warp, Wave, Kitty, and Ghostty are terminal
applications with useful harness-like operator surfaces; they are not imported
as agent harnesses or alternate control planes. The current implementation does
not need another code change: the shared registry and CLI are the correct seam
for adopting their best interaction patterns later.

Local read-only inventory on 2026-08-21 found:

| Terminal | Installed version | Strongest donor lesson | Disposition |
| --- | --- | --- | --- |
| iTerm2 | 3.7.0beta9 | shell marks, status/cwd/runtime, session restoration, Python API | retain as host |
| Warp | 0.2026.07.29.09.05.02 | searchable command palette, atomic command/output blocks, YAML launch layouts | translate into shared registry and declarative project recipes |
| Wave | 0.14.5 | stable block/workspace IDs and CLI-addressable visual widgets | borrow identity and projection concepts; do not import its GUI or AI authority |
| Kitty | 0.48.2 | keyboard-first operation, declarative sessions, explicit remote selectors, reproducible benchmark tool | borrow declarations and selectors; reject arbitrary remote send-text |
| Ghostty | 1.3.1 | native macOS presentation, strong font/theme defaults, prompt navigation, restored window state | borrow visual restraint and native-fit principles; use iTerm equivalents |

## Why iTerm2 is sufficient underneath

iTerm2 shell integration already marks prompt, command, and output boundaries;
records return status, working directory, host, and runtime; supports command
navigation and completion alerts; and exposes sessions, arrangements, windows,
tabs, prompts, screens, profiles, and status bars through its Python API. The
Dream House companion should project those events into stable Codex-owned
records rather than parse pixels or introduce another terminal.

Primary sources:

- https://iterm2.com/documentation-shell-integration.html
- https://iterm2.com/python-api/
- https://iterm2.com/documentation-triggers.html

iTerm triggers can run commands, scripts, coprocesses, or send text. Those are
capabilities to constrain, not a reason to grant the companion ambient
authority. Initial integration remains observation-only and typed-targeted.

## Donor map

### Warp

Warp's command palette searches actions, shortcuts, workflows, and launch
configurations. A Block binds one command to its output as a navigable unit.
Launch configurations serialize windows, tabs, panes, working directories, and
optional commands in YAML.

Sources:

- https://docs.warp.dev/terminal/command-palette
- https://docs.warp.dev/terminal/blocks
- https://docs.warp.dev/terminal/sessions/launch-configurations
- https://docs.warp.dev/terminal/entry/yaml-workflows

Adopt the search and block model. Defer launch recipes until they can be
declared without automatically executing embedded commands. Reject cloud-owned
workflow state as a source of truth.

### Wave

Wave gives terminals, file previews, browsers, and other widgets stable block,
tab, workspace, client, and connection identities. Its `wsh` CLI bridges shell
commands to visual blocks and remote sessions, while saved workspaces retain
layouts and histories.

Sources:

- https://docs.waveterm.dev/gettingstarted
- https://docs.waveterm.dev/widgets
- https://docs.waveterm.dev/workspaces
- https://docs.waveterm.dev/connections
- https://docs.waveterm.dev/wsh

Adopt stable identifiers and the principle that CLI and human projections share
one object model. Keep rich previews in the future human dashboard or iTerm
companion; do not import Wave's command-running, file-transfer, browser, or AI
control surface.

### Kitty

Kitty is explicitly keyboard-first, stores reproducible configuration in text,
supports declarative sessions, and exposes a powerful remote-control protocol
with typed match fields. Its shell integration provides prompt navigation and
last-command output selection.

Sources:

- https://sw.kovidgoyal.net/kitty/overview/
- https://sw.kovidgoyal.net/kitty/sessions/
- https://sw.kovidgoyal.net/kitty/shell-integration/
- https://sw.kovidgoyal.net/kitty/remote-control/
- https://sw.kovidgoyal.net/kitty/rc_protocol/

Adopt declarative session recipes and explicit selectors. Treat general remote
control and send-text as a negative security example: no fuzzy focus target and
no command injection through the presentation layer.

### Ghostty

Ghostty combines a native macOS interface with Metal rendering, system-aware
light/dark themes, ligatures, grapheme handling, tabs/splits, Quick Look,
AppleScript automation, and restored window state. Shell integration provides
prompt marking and command-output navigation.

Sources:

- https://ghostty.org/docs/about
- https://ghostty.org/docs/features
- https://ghostty.org/docs/features/shell-integration
- https://ghostty.org/docs/config
- https://ghostty.org/docs/config/reference

Adopt the native-fit rule: typography, spacing, focus, and state colors should
feel like a Mac tool rather than a themed game dashboard. Use iTerm2's existing
native controls and API rather than embedding Ghostty or rebuilding a renderer.

## Five admitted requirements

1. One typed registry must feed CLI search, key maps, help, and future visual
   palettes; no surface-specific action catalog.
2. Every command run exposed by the companion must have stable command/output
   identity plus cwd, host, timestamps, status, and source session.
3. Project layouts may later be declarative and versioned, but opening a layout
   and executing commands are separate capabilities and approvals.
4. Terminal automation must use explicit typed target selectors. Ambient focus,
   arbitrary send-text, and regex-triggered execution are outside the default
   authority boundary.
5. Human presentation must preserve keyboard reachability, readable typography,
   restrained state color, native macOS behavior, and a generated discoverable
   key map.

## Aesthetics disposition

Aesthetics are a user requirement, not decoration. Dream House should preserve
the user's iTerm profile as the baseline and add only a thin semantic layer:

- one consistent type scale and monospace family with verified glyph coverage;
- clear focus and command-state cues that do not rely on color alone;
- compact cards/marks for running, passed, failed, blocked, and approval-needed;
- optional light/dark palettes derived from the host profile;
- no wallpaper, animated chrome, terminal-specific theme generator, or forced
  font replacement in the harness core.

Warp and Wave demonstrate richer visual grouping. Ghostty demonstrates native
fit and careful text rendering. Kitty demonstrates deep text-configurable font
and color control. Their themes are inspiration for the human projection, not
runtime dependencies or a reason to overwrite the user's current iTerm setup.

## Rendering benchmark gate

No published table reviewed here is a valid five-way macOS verdict. Kitty's
official benchmark separates latency, throughput, and energy/CPU, but its
published comparison is Linux/X11 and explicitly omits iTerm2. Ghostty states
that performance has multiple meanings and does not publish a definitive
cross-terminal table. GPU acceleration alone does not establish lower input
latency, smoother rendering, or lower energy use.

Source:

- https://sw.kovidgoyal.net/kitty/performance/
- https://ghostty.org/docs/about

A later local benchmark should use the already-installed versions above, a
fresh identical shell/profile, the same font/size/window dimensions, and at
least five repetitions per case. Record raw results, OS/build, display refresh,
power state, terminal configuration hashes, and outliers. Measure separately:

1. cold and warm launch-to-prompt time;
2. keyboard-to-pixel latency with a hardware or high-frame-rate-camera method;
3. parser throughput for ASCII, Unicode, CSI, and image protocols;
4. rendered scrolling/frame pacing rather than parser-only throughput;
5. CPU, GPU, memory, and energy during idle, sustained output, and a real TUI;
6. correctness under Unicode, ligatures, wide glyphs, color, links, images, and
   synchronized updates; and
7. subjective legibility, focus recovery, key discoverability, and visual
   fatigue using the same tasks.

The result should inform the companion's presentation budget and configuration,
not silently change the main terminal. A terminal switch remains a separate
human decision even if another renderer wins a metric.

## Feature-creep boundary

Do not add a second terminal renderer, terminal compatibility framework, cloud
notebook, embedded browser, AI chat surface, plugin store, global hotkey daemon,
or unrestricted remote-control bridge. Reopen only for a concrete workflow that
iTerm2 plus the shared registry cannot support, or after a controlled local
benchmark identifies a material user-visible problem.

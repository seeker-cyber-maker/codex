# Interface qualification

| Terminal | Installed version | Safe command lane | Result |
| --- | --- | --- | --- |
| iTerm2 | 3.7.0beta9 | installed Python API: create exact window with custom command, retain returned window ID, close exact ID | qualified |
| Kitty | 0.48.2 | LaunchServices new instance, `--config NONE`, fixed command, self-close | qualified with activation caveat |
| Ghostty | 1.3.1 | LaunchServices new instance, disable default config and saved-window restoration, fixed initial command, terminate exact new PID after result | qualified for bounded receipt only; lifecycle divergence observed |
| Warp | 0.2026.07.29.09.05.02 | no non-writing arbitrary-command interface found | unqualified |
| Wave | 0.14.5 | `wsh run` is available only inside a Wave-managed session; external credential was not extracted | unqualified |

## Important exclusions

- Computer Use refused all four alternate terminal bundle identifiers. No
  alternate UI automation, accessibility bypass, AppleScript, or ambient
  send-text path was used.
- Most permission popups on this Mac require a human click. Kitty also showed
  that a background surface can stall until focused. Launch-to-prompt,
  time-to-first-token, and any other human-gated startup timing are therefore
  excluded rather than normalized.
- Warp could be driven by creating a launch-configuration file, and Wave could
  be driven from an already-authenticated in-session `wsh`. Both would cross
  the frozen no-configuration/no-credential boundary.
- No screenshot-based aesthetics score was produced because the authorized
  computer-control layer blocks these terminal applications. This remains a
  manual identical-fixture test, not a missing number to estimate.

## Lifecycle observations

- The exact iTerm2 API lane preserved the original window ID and all three
  pre-existing ShellLauncher sessions after both runs.
- Two initial Kitty qualification windows did not advance until the user
  focused them. They were closed by the user and are excluded. Later fixed
  command runs completed and self-closed.
- Ghostty launched through LaunchServices returned benchmark output, but the
  bundle remained alive and accumulated login children after the initial
  command. Exact newly created Ghostty PIDs were terminated after each receipt.
  Direct execution of the bundle binary produced no result and was interrupted.
  This is a launch/lifecycle finding, not a renderer-correctness verdict.

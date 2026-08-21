# Official repository review

The installed applications were not rebuilt or updated. Public repositories
were consulted only to qualify launch and measurement interfaces. Repository
heads are therefore source evidence for current interface semantics, not proof
that an installed bundle was built from that exact commit.

| Application | Public source reviewed | Relevant conclusion |
| --- | --- | --- |
| iTerm2 | `gnachman/iTerm2` | The Python API exposes typed window creation and exact forced close. The installed API was used to create and remove one exact benchmark window while preserving the pre-existing window. |
| Warp | `warpdotdev/warp`, especially `app/src/uri/mod.rs` | `warp://action/new_tab` and `new_window` accept a path. Command execution is supplied through saved launch configurations, which would write user configuration and was therefore excluded. |
| Wave | `wavetermdev/waveterm`, especially `emain/emain.ts` | A second application launch creates another Wave window but does not accept a command. The installed `wsh run` exists, but external use fails closed without the in-session `WAVETERM_JWT`; no credential was extracted. |
| Kitty | `kovidgoyal/kitty`, especially `tools/cmd/benchmark/main.go` | `kitten __benchmark__` opens the controlling TTY, sends fixed payloads, waits for three device-status responses, and reports parse-loop throughput. Without `--render` it wraps payloads in synchronized-output mode 2026; with `--render` it does not. |
| Ghostty | `ghostty-org/ghostty` plus installed `+show-config --default --docs` | `-e` is intended to set an initial command and force exit after the command. `config-default-files=false` and `window-save-state=never` are the documented CLI isolation controls. The installed macOS bundle did not fully match the expected post-command lifecycle in this run. |

Primary locations:

- https://github.com/gnachman/iTerm2
- https://github.com/warpdotdev/warp/blob/master/app/src/uri/mod.rs
- https://github.com/wavetermdev/waveterm/blob/main/emain/emain.ts
- https://github.com/kovidgoyal/kitty/blob/master/tools/cmd/benchmark/main.go
- https://github.com/ghostty-org/ghostty

The GitHub code-search API reached its authenticated rate limit during the
mode-2026 cross-repository sweep. No claim of repository-wide absence is based
on that incomplete search.

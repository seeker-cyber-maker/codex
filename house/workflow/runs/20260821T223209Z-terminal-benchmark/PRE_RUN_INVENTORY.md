# Pre-run inventory

Captured before any benchmark application was launched.

| Application | Version | Initial process state |
| --- | --- | --- |
| iTerm2 | 3.7.0beta9 | PID 5572 present; three pre-existing user shells (5580, 19299, 31362) |
| Warp | 0.2026.07.29.09.05.02 | not running |
| Wave | 0.14.5 | not running |
| Kitty | 0.48.2 | not running |
| Ghostty | 1.3.1 | not running |

Protected pre-existing iTerm2 processes are out of scope and must remain alive.
Kitty's existing user configuration was observed but will not be loaded by the
benchmark: `~/.config/kitty/kitty.conf`, 125,740 bytes, SHA-256
`4826157b81a1c6a1d1e7e286376a5f279427d9aefdd7a6e20865386c9b34f19f`.

The Computer Use safety layer refused both Kitty (`net.kovidgoyal.kitty`) and
Ghostty (`com.mitchellh.ghostty`). Consequently no accessibility-driven input,
screenshots, or visual scoring will be attempted through an alternate UI
automation mechanism. CLI-launched, self-terminating measurement windows remain
eligible because they do not require UI control.

# iTerm2 and TestFlight status

Observed locally on 2026-08-21 without installing or updating either app.

## Installed

- iTerm2: `3.7.0beta9`.
- iTerm2 Buddy: version `1.0`, build `7`.
- TestFlight: version `4.3.0`, build `659.1`.

## TestFlight lane

The signed-in TestFlight detail page currently presents iTerm2 Buddy version
`1.0`, build `7`, released 2026-07-27 and expiring 2026-10-25. Its test notes
say to use iTerm2 `3.7.0beta8`. Automatic updates are enabled. TestFlight did
not present a newer build; it showed `Install`, not `Update`, despite the same
build already existing on disk, so TestFlight's local install-recognition state
should not be treated as authoritative.

Conclusion: the installed Buddy bundle matches the newest build currently
offered to this tester, but it is behind repository development build `9`.

## Mac beta lane

The official download page currently offers iTerm2 `3.7.0beta11`, while this
Mac has beta9. No update was performed. The offline WebView renderer does not
depend on Buddy and does not require a paired update.

## Compatibility boundary

Application build numbers are evidence, not the protocol negotiation rule.
Before any live Buddy use, re-check the paired protocol revision/minimum-peer
values and update the Mac and TestFlight apps together if required. Buddy relay
and remote terminal input remain outside the Dream House companion slice.

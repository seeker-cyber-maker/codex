# Handoff

## Completed

- Selected iTerm2's public toolbelt WebView as the future local presentation
  surface; terminal-window launch and session text injection were rejected.
- Added a deterministic renderer from a complete verified display-batch chain
  to self-contained HTML.
- Escaped every card field and prohibited scripts, links, images, forms,
  external resources, framing, and network connections through structure and
  content-security policy.
- Added total batch, text, and encoded-document bounds.
- Added an unbound registration descriptor with observe-only authority, no
  reverse channel, no terminal input, no transport, and no iTerm API action.
- Recorded that loopback/capability URL validation is not implemented and is a
  mandatory gate before binding.
- Verified the current TestFlight lane: Buddy build 7 is both installed and the
  newest build offered to this tester; repository development is build 9.

## Acceptance boundary

This accepts offline rendering only. It does not accept a loopback server,
capability token, iTerm registration, live Codex event source, Buddy relay,
mobile display, push notification, or terminal-control path.

## Next admissible slice

Implement and independently review a pure URL/capability validator with exact
loopback address handling, an unguessable expiring token, replay rules, and
origin checks. Keep it offline. Only after that validator is accepted may a
separate operation consider a loopback viewer or iTerm WebView registration.

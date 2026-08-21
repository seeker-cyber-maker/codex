# Handoff

## Completed

- Recovered the already-accepted projector, display-batch, inert HTML,
  capability, and unbound WebView descriptor chain instead of rebuilding it.
- Verified the installed iTerm API wrapper exposes WebView registration with a
  URL and duplicate reveal, but no refresh or unregister wrapper.
- Added `OneShotLoopbackViewer`, which binds exact IPv4 or IPv6 loopback,
  measures the selected high port, issues one redacted capability, strictly
  parses bounded HTTP, serves one inert document, and stops.
- Added uniform error mapping, no access logging, cache/referrer/content
  security headers, bounded slow-request handling, a 32-rejection budget,
  explicit close, monotonic expiry, and a distinct consumed-response-failure
  state.
- Added no activation CLI and performed no iTerm registration.

## Verification

Six viewer tests, all 36 terminal-companion tests, and all 129 House tests pass.
Ruff, formatting, compilation, diff checks, operation hashes, source hashes,
and independent plan and implementation reviews pass. Seven test listeners
were started and all seven closed.

## Claim ceiling

This accepts a bounded one-shot exact-loopback HTML transport. It does not
accept iTerm/WKWebView compatibility, persistent refresh, live Codex capture,
iTerm registration, terminal input, Buddy relay, or general dashboard serving.

## Next boundary

The user requested the already-documented same-Mac terminal aesthetics and
rendering benchmark next. Keep that separate from iTerm registration. A future
registration experiment must resolve URL refresh/reveal behavior and obtain a
new stateful-app operation review before touching iTerm.

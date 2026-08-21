# One-shot iTerm loopback viewer plan

## Objective

Implement the smallest live transport beneath the accepted offline terminal
companion: serve one already-rendered inert HTML document through one
single-use capability on an exact loopback IP. Exercise it with local tests,
but do not register anything with iTerm2.

## Recovered state

- `projector.py` accepts bounded exported Codex completion notifications.
- `display_batch.py` produces verified one-way display-only batches.
- `webview.py` produces inert self-contained HTML and an unbound iTerm
  registration descriptor.
- `capability.py` issues and atomically consumes bounded single-use loopback
  capabilities using caller-supplied monotonic time.
- Installed iTerm2 3.7.0beta9 exposes
  `async_register_web_view_tool(display_name, identifier,
  reveal_if_already_registered, url)`. Duplicate registration reveals the
  existing tool but the public wrapper exposes no URL-refresh or unregister
  operation. Registration is therefore not admitted in this slice.

## Graph

1. Freeze the exact local listener and lifecycle boundary.
2. Obtain independent read-only plan review.
3. Add a dependency-free one-shot loopback viewer plus security fixtures.
4. Run focused tests, the complete House suite, static checks, and direct
   source inspection.
5. Obtain independent read-only implementation review.
6. Seal source, reconcile the local socket effects, write handoff/AACR, and
   commit locally.

## Invariants

- Bind only exact `127.0.0.1` or `::1`, using a high port selected by the OS or
  an explicit high port.
- Issue the capability only after binding, using the listener's measured
  canonical address and port. Require exactly one canonical `Host` header that
  matches that authority; reject missing, duplicate, absolute-form,
  noncanonical, or mismatched authority.
- Use `time.monotonic_ns`; wall-clock time never decides validity.
- Serve only the exact capability URL with `GET` and no `Origin` header.
- Accept only origin-form HTTP/1.0 or HTTP/1.1 requests with a request line of
  at most 2,048 bytes, at most 32 headers and 8,192 total header bytes, no
  transfer encoding, and no request body (`Content-Length` absent or zero).
- Collapse every rejection to the same small external response without
  disclosing validator codes or the bearer.
- Emit no access log, query log, URL log, or bearer-bearing receipt.
- Send `no-store`, no-referrer, nosniff, and restrictive CSP headers.
- Stop after one successful document response, explicit close, or capability
  expiry; bound request handling and thread shutdown. At most 32 rejected
  request attempts may be processed, and rejected traffic cannot extend the
  original monotonic deadline.
- Persist no token, document, history, cookie, keychain item, or configuration.
- Do not import iTerm, register a tool, send terminal input, connect to Codex,
  open native Codex state, or expose a reverse channel.

## Acceptance

- Positive IPv4 and available IPv6 requests return the exact rendered bytes.
- Wrong method, Origin, Host, request form, version, path, token, replay,
  expiry, body, transfer encoding, oversized line/header set, and excess
  request attempts fail uniformly.
- An invalid request does not consume the valid capability.
- The successful response includes the frozen security and cache headers.
- The safe receipt and object representations contain no bearer.
- The listener closes deterministically and leaves no active background thread.
- Existing terminal-companion and complete House tests remain green.
- Independent review finds no consequential authority, lifecycle, or secret
  handling defect.

## Claim ceiling

This phase may establish a bounded local one-shot HTTP display transport. It
does not establish iTerm/WKWebView compatibility, live Codex capture, automatic
refresh, persistent viewing, iTerm registration, terminal control, or general
dashboard serving.

## Model advisory

Case type: `security_containment`. The bounded implementation remains suitable
for Terra/medium with independent review. Escalate before iTerm registration,
persistent serving, refresh/reload support, or any reverse/control channel.

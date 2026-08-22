# After-action council record — frozen relay dashboard renderer

## Decision

Reuse the established static-document pattern from the terminal companion,
but do not reuse or start a transport. The relay view renders a response that
has already been frozen by its caller.

## Why

The next useful integration seam is presentation, not a second control plane.
Keeping rendering pure makes its output reviewable and preserves the adapter's
unbound `418` boundary for every write-like request.

## Acceptance

Deterministic tests cover exact input shape, escaped hostile text, inert CSP,
visible `418` state, and rejection of malformed responses. Focused and full
House suites passed.

## Open gate

Any listener, browser session, capability consumption, or authority-aware
mutation path is a distinct future review. It is not implied by static HTML.

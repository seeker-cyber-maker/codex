# Offline iTerm WebView adapter

## Objective

Select and implement the smallest local presentation surface for the accepted
iTerm display-batch contract without connecting to iTerm or registering a tool.

## Selected surface

iTerm2's public Python API exposes a toolbelt WebView registration surface. It
is preferable to terminal-window creation or session text injection because a
WebView can present many command cards without turning any card into terminal
input.

## Invariants

- The complete display-batch chain is verified before rendering.
- Untrusted card text is HTML-escaped.
- The document has no JavaScript, links, images, forms, or external resources.
- The content-security policy prohibits network connections.
- The registration descriptor has no URL and performs no iTerm API call.
- A future URL must be loopback-only and capability-bearing.
- Terminal input and Buddy relay remain prohibited/out of scope.
- Rendering is bounded by batch count, text characters, and encoded bytes.

## Acceptance

Focused and full House tests, Ruff, formatting, compilation, JSON parsing, and
diff checks must pass. Static inspection must confirm no iTerm import, socket,
server, subprocess, terminal-input API, registration call, or network request.

## Model advisory

Routine bounded implementation: Terra/medium. Escalate before any live iTerm
registration, HTTP listener, authentication token, or reverse channel.

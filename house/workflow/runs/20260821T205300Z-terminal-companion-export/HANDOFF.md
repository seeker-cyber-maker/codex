# Handoff

`house.terminal_companion` is a pure offline projector for exported completed
`commandExecution` notifications. It displays the client-facing command
representation, cwd, terminal status, exit code, duration, and aggregate
output in a stable JSON card.

It intentionally consumes no live stream. A future adapter must qualify its
app-server capture/subscription boundary and preserve Codex's redaction before
connecting an iTerm presentation.

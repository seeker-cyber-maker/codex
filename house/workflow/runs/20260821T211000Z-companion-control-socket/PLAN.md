# Shared control-socket companion seam

## Objective

Qualify the pinned source app-server's Unix control-socket plus proxy path as
the shared transport for a later desktop client and read-only terminal
companion.

## Non-goals

- Do not attach to, restart, instrument, or mutate the currently running app.
- Do not start a thread, turn, provider request, model, tool, or iTerm window.
- Do not read or write the live Codex home.

## Plan

1. Start the source-built app-server against an isolated temporary Codex home
   and explicit temporary Unix socket.
2. Connect through the source-built `app-server proxy`, complete only the
   initialize/initialized handshake, and request the loaded-thread list.
3. Require a valid response, no live-home access, no provider event, clean
   client/server termination, and removal of temporary state.
4. Implement only the smallest downstream launcher/capture contract justified
   by the receipt.

## Disposition

The isolated server start succeeded, but the proposed proxy probe was based on
the wrong framing assumption. `app-server proxy` forwards a raw WebSocket byte
stream over stdio; it does not translate JSONL into app-server messages. The
currently running desktop app-server processes also use `stdio://`, not a
shared Unix listener. This branch is therefore pruned without implementation.

The follow-on iTerm2 investigation is recorded in
`ITERM_BETA_PROTOCOL_REVIEW.md`. It identifies separate presentation seams but
does not change the negative control-socket verdict.

## Model advisory

`provider_bridge_debug`; Sol/high for the transport boundary. Reassess after
the isolated handshake and before any desktop integration.

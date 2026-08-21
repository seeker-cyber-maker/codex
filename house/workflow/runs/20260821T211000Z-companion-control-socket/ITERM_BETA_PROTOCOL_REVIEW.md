# iTerm2 beta and Buddy protocol review

## Scope and identity

Read-only inspection used the official `gnachman/iTerm2` repository at commit
`14c75a3c64c6af8f1dc74e7e22d6bd4d7084fc0d` (2026-08-20) plus installed bundle
metadata and the official beta download page.

- Installed macOS app: iTerm2 `3.7.0beta9`, signed by team `H7V7XYVQ7D`.
- Installed iOS-on-Mac TestFlight wrapper: iTerm2 Buddy `1.0` build `7`, bundle
  `com.googlecode.iterm2.companion`, signed for TestFlight distribution.
- Current official macOS beta at inspection time: `3.7.0beta11`, built
  2026-08-19. The installed macOS app is two beta releases behind.
- Repository Buddy project version: `1.0` build `9`.
- Repository companion protocol: revision `11`, minimum peer `11`. Revision 11
  is deliberately lockstep because it migrates both peers to a sharded relay
  resolver.

Updating only one side can therefore break pairing until the other side is
updated. No update was installed or initiated by this review.

## Three different protocols

### 1. Codex app-server

Codex app-server uses JSON-RPC messages over WebSocket or stdio. A Unix listener
supports multiple WebSocket clients, but the currently running ChatGPT/Codex
desktop processes are launched with `stdio://`. The source `app-server proxy`
is a raw WebSocket bridge; it is not a JSONL protocol converter.

This remains the canonical semantic source for thread, turn, item, command,
approval, diff, and completion events.

### 2. iTerm2 Python API

`proto/api.proto` defines protobuf `ClientOriginatedMessage` and
`ServerOriginatedMessage` envelopes over iTerm2's authenticated WebSocket API.
The repository's remote `it2.py` path adds a Unix-domain/length-prefixed bridge
for SSH-side use. It is a programmable iTerm session/UI API, not the Buddy
protocol.

This is the appropriate future presentation adapter for local status, session,
toolbelt, or custom-component integration. It must not become the source of
truth for Codex execution state.

### 3. iTerm2 Buddy

Buddy is fully present in the public repository. Both devices make outbound
WebSocket connections to a relay. Admission uses JSON `Hello -> Challenge ->
Proof -> Result`; admitted binary frames are opaque to the relay. A Noise
`XK_25519_ChaChaPoly_BLAKE2s` channel then carries versioned JSON RPC/control
envelopes. Live terminal view is a separate low-latency HEVC media channel.

Buddy is not inherently read-only. The current protocol includes remote session
resize, selection, scroll input, and phone-driven key injection. Dream House
must not expose those reverse-control messages through a display-only adapter.

## Patterns to adopt

1. Explicit `revision` and `minimum_peer` compatibility, independent of app
   version numbers.
2. Explicit turn lifecycle events rather than inferring task state from typing
   indicators or screen motion.
3. Separate semantic control events from video/media and human presentation.
4. Bounded queues, frame sizes, daily quotas, keepalive timeouts, and capped
   reconnect backoff.
5. Permission checks at point of use, with revocable one-time or standing grants.
6. Deterministic hard rules first; an undecidable safety classification requires
   human approval rather than being treated as safe.
7. Contentless wakeups followed by authenticated retrieval, so notifications do
   not need to carry sensitive command/output content.
8. Authenticate the peer before trusting a local socket. iTerm2 beta9 itself
   fixed a local socket peer-authentication defect and bounded an authenticated
   Python API client's inbound WebSocket buffering.

## Patterns not to adopt

- Do not use Buddy's relay or HEVC stream as the Codex event bus.
- Do not derive command completion from terminal pixels, typing indicators, or
  AI interpretation when app-server emits a typed completion event.
- Do not let an iTerm session, AI chat, mention, clipping, or remote key event
  grant Dream House execution authority.
- Do not label a Buddy-derived display or notification as a Codex source.
- Do not place aggregate command output in a remote push notification. Output
  remains `NOT_ATTESTED` for redaction and requires an explicit view permission.

## Dream House bridge decision

The first bridge is one-way and local:

`Codex app-server event -> terminal card projector -> versioned display batch -> iTerm2 local presentation adapter`

The app-server event remains authoritative. The projected content is
`DISPLAY_ONLY`, dispatch remains `NOT_ATTEMPTED`, and no reverse control channel
exists in protocol revision 1. Buddy may later mirror a contentless task-state
wakeup for the human, but it is neither an authority path nor a worker route.

Live integration remains gated on one of two explicit architectures:

1. Dream House owns the source app-server launched on a Unix WebSocket listener,
   and both the client and the companion subscribe as ordinary clients; or
2. a narrowly reviewed upstream event mirror/fan-out is added.

The current ChatGPT desktop's private stdio app-server is not to be tapped or
restarted for this phase.

## Primary source anchors

- `proto/api.proto`
- `Companion/CompanionCore/Sources/CompanionTransport/CompanionTransports.swift`
- `Companion/CompanionCore/Sources/CompanionTransport/RelayTransport.swift`
- `Companion/CompanionCore/Sources/CompanionNoise/NoiseProtocol.swift`
- `Companion/CompanionCore/Sources/CompanionProtocol/CompanionProtocolVersion.swift`
- `Companion/CompanionCore/Sources/CompanionProtocol/Wire/WireCoding.swift`
- `sources/Companion/CompanionHostBridge.swift`
- `sources/Companion/CompanionSessionStreamer.swift`
- `sources/Companion/CompanionVideoEncoder.swift`
- `sources/ClaudeCode/Orchestration/OrchestratorSafetyGate.swift`
- `docs/notes-3.7.0beta9.txt`
- `docs/notes-3.7.0beta10.txt`

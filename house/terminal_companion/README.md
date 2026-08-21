# Terminal companion thin slice

This is an offline projector for exported app-server `item/completed`
`commandExecution` notifications. It produces compact command cards containing
the redacted command presentation supplied by Codex, cwd, terminal status,
exit code, duration, and aggregate output.

The source command is shown with `redaction_state: UPSTREAM_ASSERTED`: the
projector relies on Codex's exported presentation and does not claim to
independently discover every secret. Aggregate output is separately marked
`output_redaction_state: NOT_ATTESTED`; it may be sensitive and needs a later,
separate display/redaction policy. Projected command/output content is always
`DISPLAY_ONLY` data, never an instruction to the companion. Input count and
capture/output sizes are bounded and malformed terminal fields fail closed.

This accepts thread/turn `item/completed` records only. It deliberately ignores
partial `item/commandExecution/outputDelta` events and does not interpret the
separate connection-scoped `command/exec/outputDelta` protocol.

It does not connect to iTerm, sockets, running Codex, rollouts, or native
databases. Capture and live subscription are separate future integrations.

The offline WebView renderer turns a complete verified display-batch chain into
a self-contained HTML document for a future iTerm2 toolbelt WebView. It has no
scripts, links, forms, images, external resources, or network permissions; all
card text is HTML-escaped and the content-security policy denies every source
except the document's fixed inline style. The companion registration descriptor
is deliberately unbound: it permits only a future capability-bearing loopback
URL and records that iTerm registration and transport were not attempted.
The pure in-memory validator enforces exact IPv4 or IPv6 loopback authorities,
an explicit high port, one canonical path, a 256-bit random bearer, five-minute
maximum lifetime, exact GET/no-Origin policy, audience binding, atomic
single-use consumption, and bounded storage. Only the token digest is retained;
the bearer is omitted from object representations and receipts. The validator
is accepted offline but remains unbound: trusted monotonic-clock wiring, an
actual listener, request/error mapping, and iTerm registration require a new
live-binding review.

The one-shot loopback viewer is the first accepted transport beneath that
validator. It binds an exact loopback IP, measures its assigned authority,
issues one capability, strictly bounds and parses raw HTTP, serves one already
rendered inert document, suppresses access logging, emits no-store and
no-referrer headers, and stops after success, expiry, explicit close, or a
finite rejection budget. Its terminal receipts omit the bearer. This component
has no CLI activation path and has not been registered with iTerm2; persistent
viewing, refresh, and WKWebView behavior remain separate acceptance gates.
`Session.async_send_text`, terminal-window command launch, and Buddy relay are
not part of this surface.

The optional display-batch wrapper adds an explicit protocol revision,
compatibility floor, sequence, previous-batch link, deterministic batch id, and
an offline full-chain verifier. It is one-way (`CODEX_TO_ITERM`), observe-only,
and prohibits a reverse channel. Raw source cards are not put into the display
batch: terminal control characters and invisible Unicode format controls are
made visible, the adapter is restricted to plain-text presentation, and each
safe card retains the SHA-256 identity of its untouched source card. The hashes
prove deterministic byte identity only; they are not signatures or authority
receipts. This adopts iTerm2 Buddy's useful compatibility and flow-boundary
patterns without using or impersonating Buddy's relay protocol.

The accompanying in-memory `DisplayBatchReconciler` is the first bounded
receiver-side state machine for that display contract. It applies only the next
contiguous batch, buffers at most 50 future batches, ignores only identical
recent replays, and rejects conflicting, stale, or broken-predecessor batches.
It retains only a bounded duplicate window; the complete conserved history
remains the separately verified display chain. The reconciler has no transport,
storage, rendering, iTerm, or reverse-channel capability.

```sh
PYTHONPATH=/absolute/path/to/codex-dream-house \
  python3 -m house.terminal_companion --input exported-notifications.json

PYTHONPATH=/absolute/path/to/codex-dream-house \
  python3 -m house.terminal_companion --jsonl --input exported-notifications.jsonl

PYTHONPATH=/absolute/path/to/codex-dream-house \
  python3 -m house.terminal_companion --jsonl --display-batch --sequence 0 \
  --input exported-notifications.jsonl
```

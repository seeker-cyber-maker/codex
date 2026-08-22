# Pi-to-Pi communication review

Evidence packet: `youtube-evidence/PIdETjcXNIk.evidence.json` (SHA-256
`f598d60e294d78dc61bed1226abaca81ffe4a058ef4e696c2760ff7cb7491d67`).
The transcript is automatic-caption evidence, so it supports design provenance,
not a proof of the video's engineering claims.

## Adopted in the offline slice

- Addressed two-way messages with stable message IDs and threaded replies.
- Store-and-forward delivery, acknowledgment, and later status retrieval.
- Independent, focused worker contexts instead of indiscriminate context
  sharing.
- Bounded conversation: per-envelope hop TTL and decreasing reply-turn budget.

## Deliberately rejected or deferred

- Peer availability does not imply capability, transport, or authority.
- The relay does not expose a chat room, execute attached artifacts, or allow a
  proposal to cause a task/worker action.
- No live network, SSH, provider, or cross-device transport is adopted.
- Dynamic worker directory/capability discovery remains a later bridge from the
  sealed provider catalog, never a live registry query.

The video itself warns that communication bounce raises cost with agent count.
That is why this relay keeps finite budgets rather than treating peer
communication as an unbounded substitute for orchestration.

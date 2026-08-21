# Authority ceremony design handoff

The design-only operation is complete. It replaces the vague idea that a model
should hold the keys with a narrower boundary: owner hardware signs
administrative authority; a dedicated local service holds the database write
capability and executes only verified typed transitions; Codex receives a
limited task-intent capability; restricted local models receive a smaller
non-delegable subset; contractors remain buffer-only.

Primary and recovery YubiKeys are independent alternatives, not simultaneous
launch keys. One explicitly selected device/slot is polled per step. The last
recovery-capable key cannot be ordinarily revoked, and persistent lockdown
cannot be cleared by a model, restart, timeout, dashboard, or configuration
edit.

The future task boundary authorizes one durable intent and reconciles delivery
across authority and inbox stores. Protected checkpoints narrow hash-chain
claims honestly. Both-owner-key loss retires the old registry and creates an
explicit continuity break rather than fabricating recovery.

Ten requirements are traced through 26 recovery scenarios and 24 frozen future
tests. No provider, network, key, hardware, service, database, or source-code
operation occurred. The next admissible slice is Stage 0 only: implement pure
canonicalization and independent fixed vectors in a new operation. It may not
touch hardware or modify the live authority path without a separate grant.

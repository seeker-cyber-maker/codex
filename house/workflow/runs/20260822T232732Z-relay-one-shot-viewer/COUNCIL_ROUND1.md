# Outside council round 1

Packet reviewed:
`EVIDENCE_PACKET.md`, SHA-256
`622ceba5eb577861757eaf0f776b15f12c686183ebd0ccfcbd277c711bfba2ee`.

All three reviewers independently matched the packet hash. One reviewer
returned `ACCEPT`; two returned `ACCEPT_WITH_REQUIREMENTS`.

## Accepted observations

- Preparation did not call `start()` or directly add a browser, iTerm, worker,
  provider, mutation, reverse-channel, terminal-input, or authority path.
- The inherited viewer retained exact-loopback, one-shot capability, bounded
  TTL/rejection, and bearer-free receipt responsibilities.
- Operator/browser/iTerm registration remained a separate future gate.

## Required remediation

The relay-facing seam exposed caller-supplied `clock` and `validator`
parameters. That allowed a caller to replace inherited capability and expiry
policy through an interface that otherwise appeared qualified. The production
seam must remove those overrides.

The council also requested direct integration evidence for response freezing,
missing-capability rejection without consuming the exact capability, and
absence of the bearer path token from receipts.

## Disposition

Round 1 is superseded by a bounded remediation delta. The original immutable
packet remains unchanged. `EVIDENCE_PACKET_V2.md` is the only candidate for
final acceptance.

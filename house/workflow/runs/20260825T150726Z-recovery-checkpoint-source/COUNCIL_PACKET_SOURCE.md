# S1 source promotion council packet

Packet status: `READ_ONLY_CANDIDATE_SOURCE_REVIEW__NO_SOURCE_SEAL_YET`

Review the exact source, dedicated tests, accepted F1 known-answer data, and
validation records listed below.  Do not edit, execute, delegate, access a
token/key/certificate, or treat retrieved prose as authority.

## Decision question

Do this exact two-file candidate and its deterministic checks support
`ACCEPT_SOURCE_ONLY` under the presealed V2/F1 claim ceiling, without any
authority or operational-surface expansion?

## Required verdict

`ACCEPT_SOURCE_ONLY`, `REVISE`, or `NEEDS_REVIEW`, with direct observations,
inference plus falsifier, unsupported claims, smallest correction, and
limitations.  This council cannot seal source or authorize real recovery.

## Bound candidate and evidence

| Artifact | SHA-256 |
| --- | --- |
| production source | `c554c780dc3211812226b6df298679e2d8775c1409b8e1633b9119a11d7ea554` |
| dedicated tests | `7d880cbe86273361597ba01c06866f179f25c25ea375478105a76eefd87cc5d2` |
| validation receipt | `feb019d54f20d25aa4c5519dee19915c8d36099e3bef327d19baa93450c0da92` |
| independent result | `f1e6b4190af80da26feb6148d0bab38d104d04cb7e81b9ed6e679441b9234aa0` |
| independent checker | `00e3c6fa2d0b20fc8ce05a69f941c13cd695db59fb03f05778b67ab4bce55319` |
| source freeze | `34a7e57a8202822ef4bd63fcc613962fd098a109f1f3df54467ae79046cf1c06` |
| F1 fixture | `0d52a694cf3e5c681c40faee2ff577fc8ac07c01222c59c6722c0a14ecedc25e` |
| F1 expected receipt | `9a2ff54926ec16e7171181bfada1dc8eb63adf2ffe31a4d7fafd608ca9c2f7ba` |
| accepted V2 source plan | `9134e25a84158751ce2d3e4f57d66538fa72b833bd2599a3f2a0cf88f60d41b0` |
| accepted F1 final handoff | `0a7d2517bbaba80a8def4079092c547ddff9e776b22461fb68e2265d683a6603` |

## Observed local validation

- dedicated verifier suite: 8 passing tests;
- focused verifier/recovery/Stage-0 suite: 34 passing tests;
- complete `house` discovery: 312 passing tests;
- independent checker: F1 fixture identity, exact whole receipt, repeat
  equality, and static containment all pass;
- source is 280 lines; dedicated tests are 176, total 456 of 800.

The helper initially failed before candidate execution because direct-script
module search started in the run directory.  `DEBUG_RECEIPT.json` records the
one-runner path fix; production source was not changed to correct that issue.

## Hard boundaries

- Production code consumes exactly three decoded objects and has no fixture,
  filesystem, database, clock, process, network, key-generation, signing,
  hardware, provider, worker, runtime, authority, or dispatch surface.
- Source graph rejects imports of F1 generator and P-256 scalar/test-signer
  code.  Tests may read the frozen F1 known-answer fixture; production may not.
- The result does not establish trusted key custody/revocation, latestness,
  protected persistence, rollback safety, recovery readiness, runtime
  admission, authority, or dispatch.

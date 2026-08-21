# Independent plan review

Reviewer: `routing_integration_audit` (read-only outside council lane)

## First verdict: BLOCK

The first plan omitted two consequential requirements:

1. exact incoming `Host` binding to the listener's measured post-bind
   authority, including duplicate, missing, absolute-form, and noncanonical
   rejection; and
2. explicit request-line, header-count, header-byte, body, and attempt bounds.

No implementation had started. The root accepted both findings and amended the
plan and operation budget without changing the objective.

## Second verdict: PASS

The revised plan requires post-bind capability issuance, one exact canonical
`Host`, origin-form requests, 2,048 request-line bytes, 32 headers, 8,192 header
bytes, no transfer encoding or body, 32 rejected requests, and a fixed
monotonic deadline. The reviewer found no remaining consequential omission for
the bounded no-iTerm-registration slice.

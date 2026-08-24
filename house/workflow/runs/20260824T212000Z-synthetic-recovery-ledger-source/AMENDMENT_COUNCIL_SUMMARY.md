# Plan Amendment Council Summary

Amendment SHA-256:
`66521a326570a0a469c9f0e0382e43a9a4b50d119a71b60986b64b207b524077`

Root disposition: `ACCEPT_TEST_ONLY_COMPATIBILITY_DELTA`

All three local same-provider read-only roles returned `ACCEPT`. They agreed
that exact canonical-path exemptions for only the private adapter and its
dedicated test preserve the reciprocal source-isolation checks. No reviewer
ran tests, edited files, accessed runtime/database state, or used a network.

The adversarial response transcribed the unchanged legacy-test hash as
`37e08de7c2ed774bdabcb9e25fcbf7704502ad844af1db6923c8147ec74f7042`,
which does not match the locally recomputed value frozen by the amendment,
`37e08de7c2ed774bdabcb9e25fcbf7704502ad844511bf0d723bfa68da2ae9aa`.
The evidence and constructive roles reproduced the frozen value exactly. This
reporting discrepancy does not alter the accepted edit and is not treated as
independent hash evidence.

Authorized delta: edit only
`house/task_spine/tests/test_recovery_policy.py` to exclude the two sanctioned
exact paths from its static scan, then rerun deterministic tests. Candidate
promotion remains unapproved pending V1 and C1.

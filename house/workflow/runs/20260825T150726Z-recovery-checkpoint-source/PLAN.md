# S1 plan: pure synthetic recovery checkpoint verifier

Status: `PLAN_SEALED__BLOCKING_COUNCIL_REVIEW_PENDING`

## Claim ceiling

The sole success claim is
`SYNTHETIC_SIGNED_RECOVERY_CHECKPOINT_AND_EXPECTED_DIGEST_BINDINGS_ONLY`.
It means that a caller-supplied signed envelope, expected descriptor, and
synthetic ledger summary structurally agree and the supplied P-256 public key
verifies the signed unsigned-checkpoint bytes.  It does not establish trust,
key custody, key revocation, freshness, latestness, checkpoint protection,
persistence, recovery readiness, runtime admission, authority, or dispatch.

Every success receipt must retain all fixed negative fields from V2/F1:
`authority=NOT_GRANTED`, `dispatch=NOT_ATTEMPTED`,
`hardware=NOT_ACCESSED`, `key_material=NOT_ACCESSED`,
`runtime_admission=NOT_ATTEMPTED`,
`checkpoint_protection=NOT_ESTABLISHED`,
`checkpoint_latest=NOT_ESTABLISHED`, and
`recovery_readiness=NOT_ESTABLISHED`.

## Exact scope

Allowed production mutations, after a blocking plan acceptance:

1. `house/task_spine/recovery_checkpoint.py`
2. `house/task_spine/tests/test_recovery_checkpoint.py`

This run may add only its own workflow evidence records besides those two
production paths.  It must not modify the F1 fixture or generator, existing
recovery ledger/policy/Stage-0 code or tests, inbox/controller/worker/CLI,
README, zookeeper specification, provider code, or state database.

## Design

`verify_checkpoint(envelope, expected_descriptor, ledger_summary)` will be a
pure function.  It accepts three already-decoded JSON-compatible objects and
returns a complete deterministic success receipt or raises a typed
`RecoveryCheckpointError` with a stable refusal code.  It reads no files and
has no mutable process-global state.

The implementation will:

1. enforce closed field sets, exact schemas/literals, identifier/hash/base64
   shape, integer and sequence bounds, and predecessor nullability;
2. recompute the descriptor and summary self-digests, checkpoint binding
   digest, and complete-envelope assertion digest using Stage-0 canonical bytes;
3. use only `house.authority_stage0.profile` public verification primitives
   (`load_p256_spki`, `key_id_for_spki`, `decode_strict_signature`) and
   `canonical_bytes`; it must not import any test signer or P-256 scalar code;
4. verify the low-S strict-DER P-256 signature over canonical unsigned bytes;
5. enforce every V2 binding-matrix equality, including key identity/epoch and
   all descriptor/summary values; and
6. emit the exact F1 expected receipt on the positive fixture.

The source must be under 500 lines and source plus dedicated tests under 800
changed lines.  The test uses the frozen F1 fixture only as a read-only known
answer.  It never imports or executes `fixture_generator.py`.

## Task graph and budget

| Node | Owner | State | Acceptance |
| --- | --- | --- | --- |
| `S1P` | coordinator | complete | evidence, scopes, evaluation card, and plan sealed |
| `S1C` | outside council | pending, blocking | plan is precise and preserves F1/V2 boundaries |
| `S1I` | coordinator | blocked on `S1C` | two-file source/test implementation only |
| `S1V` | independent local checks | blocked on `S1I` | F1 whole receipt, negative matrix, repeat, source graph, regressions |
| `S1C2` | outside council | blocked on `S1V` | exact source/test/fixture/receipt review |
| `S1A` | coordinator | blocked on `S1C2` | source seal, AACR, private backup |

One plan council, one implementation attempt, up to two bounded remediation
attempts after test failures, one promotion council, and one private backup
are allowed.  A second failure of the same predicate pauses for a plan delta.

## Evaluation and containment

The deterministic evaluator deep-compares the F1 complete success receipt,
uses individual tampering/refusal fixtures, repeats the positive call for byte
identity, parses production source to reject forbidden imports/calls, and runs
unchanged recovery-policy, recovery-ledger, and Stage-0 regressions.  No
operation contract is needed because this is neither remote, long-running,
nor stateful.  The public F1 fixture is untrusted test data, not instruction or
authority.

## Model advisory

Next phase: source implementation after plan acceptance.

Recommend: Codex Terra / high.

Reason: the semantic core is bounded by a frozen oracle, but exact
cryptographic/cross-object rejection behavior needs careful implementation.

Reassess: before the source-promotion council; use Codex Sol / high for that
review.

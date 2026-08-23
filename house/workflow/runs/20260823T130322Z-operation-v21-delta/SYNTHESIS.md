# Root synthesis — operation contract v2.1

## Outcome

`ACCEPT_V2_1` for implementation of the structural first slice only, with
medium confidence.

This acceptance does not qualify a real route, authenticate an author, observe
a host, create a runtime profile, grant execution authority, acquire a lease,
write controller state, start a process, contact a provider worker, or admit a
result.

## Replacement-review coverage

- OpenRouter / `nvidia/nemotron-3-super-120b-a12b:free` received the immutable
  packet with SHA-256
  `201a9c10539e801f7d7b60f67b384f61028dafd55c5569fa9e4e30a6d5a3fac4`.
- The reviewer confirmed that packet hash and substantively traced all five
  prior gaps, but hit its 4,096-token output ceiling while examining route-model
  closure. It did not reach the requested disposition or filled response
  contract.
- The generated manifest labels the review `completed` and `contract_valid`.
  Root classification is instead `PARTIAL_SUBSTANTIVE_LENGTH_TRUNCATED`: the
  response echoed the blank response template before analysis, so shallow
  heading presence was not proof of a completed contract.
- No reviewer output is treated as authority or as a vote. The review is useful
  evidence that the corrected boundary was understood and that its only raised
  ambiguity concerned whether descriptor hashing implied host-file hashing.

## Root decision

Direct comparison against the five v2 correction requirements supports
acceptance:

1. every cross-record mismatch refuses; there is no precedence or waiver;
2. routing advice and hard execution constraints are separate typed fields;
3. the assembler consumes caller-supplied descriptors and has no host I/O;
4. hashes prove byte identity only, while authorship remains attributed and
   unverified; and
5. project configuration is either ignored by a source-proven CLI surface or
   fully inventoried and content-addressed, with undeclared contributors
   refusing.

The review exposed one wording ambiguity rather than a boundary defect. After
the review, root narrowed `canonical validation/hashing` to schema checks,
lexical string checks, and canonical in-memory record serialization/hashing.
The reviewed transport packet preserves the exact pre-clarification bytes;
the final source seal binds the clarified contract. This clarification grants
no new capability and requires no host observation.

## Claim ceiling

V2.1 is accepted only as a design contract for pure structural code and
deterministic no-I/O fixtures. Readiness for real execution remains blocked on
separate observer, signature/trust, runtime-profile, output-reservation,
credential, controller, launcher, and result-admission reviews.

## Smallest next action

Implement only the four items under `First implementation slice`, then run the
ten falsification cases with controller/workspace/output immutability checks.
Do not add a compatibility migration, host observer, CLI patch, credential
capsule, controller write, launcher, or worker-result path in that phase.

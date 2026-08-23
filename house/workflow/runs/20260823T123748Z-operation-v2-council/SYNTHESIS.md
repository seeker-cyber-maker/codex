# Council synthesis — operation contract v2

## Outcome

`REVISE_DESIGN` with medium confidence.

The five-object separation is the correct architectural direction, and both
substantive external reviews endorsed it. The proposal is not ready for
implementation unchanged. Its contradiction semantics, route-authentication
claim, and definition of a pure builder need a bounded v2.1 correction.

## Council coverage

- OpenRouter / `google/gemma-4-31b-it:free`: completed, valid design contract,
  packet hash confirmed, `ACCEPT_DESIGN`.
- ClinePass / `cline-pass/deepseek-v4-flash`: substantive partial response,
  packet hash confirmed, truncated at the 4,096-token ceiling before the final
  required section/disposition.
- OpenCode Go / `deepseek-v4-flash`, then `qwen3.8-max`: both timed out at the
  declared 90-second bound; no review content and no packet-hash confirmation.

The two substantive lanes used different provider harnesses and different
model families. The failed adversarial lane weakens coverage; it does not count
as agreement. The ClinePass manifest reports provider accounting cost
`0.01046716`; OpenRouter reports zero. No repository, worker, controller,
credential, or hardware action was available to reviewers.

## Confirmed observations

1. V1 obtains `--model` from task-card recipient metadata and therefore lacks
   the intended separation between routing preference and execution selection.
2. A task card, route selection, operation, runtime profile, and execution
   authority must be separate, hash-bound objects, none able to mint the next
   object's authority.
3. Explicit model/provider/account/pool identities, capability closure,
   expiry/freshness, and no-fallback stop rules are required.
4. Operation and profile verification must remain no-dispatch; execution
   authority is a later single-use controller concern.
5. Project configuration needs an explicit strategy: ignore it through a
   reviewed CLI surface, or content-address and admit it as declared input.

## Corrections required for v2.1

### 1. Agreement, not precedence

No later object overrides an earlier object. The correct rule is:

```text
task intent + recorded routing disposition
  == route-selection task binding
  == operation argv/provider policy
  == observed runtime profile
```

Any disagreement refuses. A runtime profile describes observed reality; it
cannot take precedence over or repair an operation. A route selection cannot
silently override an advisory specific-model request. The route record must
explicitly say whether each routing hint was `HONORED`, `OVERRIDDEN_WITH_REASON`,
or `NOT_APPLICABLE`. A true task constraint is a different typed field and may
not be overridden.

### 2. Make the builder genuinely pure

`prepare_operation_v2` must not resolve paths, stat or hash files, create output
paths, read config, or inspect credentials. Rename it `assemble_operation_v2`
or document equivalent semantics. It accepts already verified, immutable input
descriptors and performs only canonical validation and hashing.

Filesystem observation and output reservation belong to separate producers.
Their evidence may later enter a runtime profile, but they are not hidden I/O
inside the assembler.

### 3. Do not call an unauthenticated hash qualified

A `selection_evidence_sha256` proves byte identity only. V2.1 must either:

- carry a verifiable issuer/key/signature binding under a separately admitted
  trust policy; or
- label the record `ROUTE_SELECTION_NO_DISPATCH` and treat signer admission as
  a later gate.

The first implementation slice should use the second, narrower claim. It can
verify canonical structure and bindings without claiming authenticated
provenance.

### 4. Type freshness and routing semantics

Route selection must bind `observed_at`, `not_after`, and the evidence/freshness
policy that determined them. Task routing must distinguish advisory class,
advisory model preference, and hard execution constraint. Ambiguous legacy
fields fail migration rather than being guessed.

### 5. Keep isolation strategy explicit

The operation must seal `PROJECT_CONFIG_IGNORED` or
`PROJECT_INPUTS_CONTENT_ADDRESSED`. The first requires an implemented and
source-tested Codex CLI path; the second requires exact discovered-layer and
instruction inventories. Managed policy may narrow only. An effective runtime
capture with any undeclared tool or context surface refuses.

## Rejected or unsupported claims

- A runtime profile does not override an operation.
- Hash binding alone is not authenticated provenance, truth, or signature.
- A pure operation assembler cannot perform ambient filesystem observation.
- The council does not prove that upstream will accept an
  `--ignore-project-config` flag, that credential projection is safe, or that a
  real runner is ready.
- One complete and one partial review are not full adversarial coverage.

## Smallest next action

Revise the immutable proposal to v2.1 with the five corrections above, then
send only the revised delta and prior claim ledger to one bounded adversarial
replacement review. Do not implement until that reviewer either accepts the
delta or identifies one concrete unresolved invariant.

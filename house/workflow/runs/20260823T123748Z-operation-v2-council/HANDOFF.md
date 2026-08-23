# Operation v2 council — handoff

## Milestone

Outside council review is complete and preserved under
`council-runs/20260823-1237-operation-v2/`.

- one completed OpenRouter/Gemma review;
- one substantive, packet-confirmed ClinePass/DeepSeek partial review;
- one failed OpenCode Go lane after two bounded timeouts;
- identical transport SHA-256
  `6d0a55cd66389681fb0b0d6c43bec5e442f3780a985cf1b6b111841cbff50071`.

Root disposition: `REVISE_DESIGN`.

## Required v2.1 delta

1. Replace precedence with exact agreement and refusal.
2. Give advisory routing hints an explicit disposition; separate hard
   constraints.
3. Make the operation assembler zero-host-I/O by accepting verified input
   descriptors.
4. Stop calling an evidence hash authenticated qualification; defer signer
   admission or add a real signature/trust contract.
5. Seal one explicit project-config strategy and reject undeclared effective
   capabilities.

## Next acceptance check

Freeze the v2.1 delta and send it, plus this claim ledger, to one bounded
adversarial replacement lane. Only after that gate may the first implementation
slice add a pure route-selection record and pure operation-v2
assembler/verifier.

No Codex worker, operation, runtime profile, credential, controller, lease,
intent, task, or hardware state changed in this run.

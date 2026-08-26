# Interrupted local TERM collection: candidate 02

State: `TERMINATED_BY_OPERATOR_SAFETY_INTERRUPTION / NON_RESULT`

The local-only candidate process was deliberately terminated after the human
reported a VRAM sudden-death interruption. No atomic candidate receipt was
written, no partial output was retained by the runner, and this is not a
negative, positive, or comparative model result.

- Opaque candidate: `local-term-candidate-02`
- Process observed before termination: `61109`
- Scope: sealed local TERM compatibility experiment only
- Forbidden surfaces remain unattempted: provider/network, task/relay/
  authority/worker dispatch, training/weight mutation, promotion/routing,
  credential/secret/Keychain, dashboard/hook/upstream core
- Reopen condition: independently diagnose and clear the VRAM interruption,
  then create a new append-only attempt rather than overwriting this record.

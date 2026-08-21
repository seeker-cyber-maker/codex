# Authority ceremony design after-action review

The strongest correction was separating four things that had been described as
one key-holder: human policy authority, hardware signing authority, the local
service's OS write capability, and the model's limited task capability. Models
can request work without carrying owner private keys in prompt-visible memory.

Treating proof acceptance as authorization of a durable intent resolves the
candidate's cross-database causality gap more cleanly than repeatedly signing
function-call retries. It also makes crash and response-loss tests enumerable.

The design preserves two independent owner keys without turning them into a
dual-launch ritual. It fails closed when device selection is ambiguous, stages
replacement before revocation, and admits that losing both keys breaks
cryptographic continuity.

Monitoring conserves every near-miss count while bounding repeated event
storage. It treats a failed early layer as an incident even when a later layer
prevents the final effect, and orders actionable alerts ahead of informational
noise.

Remaining uncertainty is implementation-shaped: portable canonicalization,
SQLite concurrency, OS identities and IPC, disk and clock faults, protected
checkpoint storage, PIV client behavior, and human usability all require their
frozen stages. The design must not be promoted by prose agreement; Stage 0 is
the smallest next falsifiable step.

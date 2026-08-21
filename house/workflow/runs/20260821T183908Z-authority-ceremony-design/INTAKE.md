# Authority ceremony design intake

The user authorized a design-only operation after both the local and outside
security councils accepted that next stage. This run may specify a future
real-key ceremony but may not implement it, enroll or poll a key, access a
YubiKey, start a service, alter permissions, contact a provider, or promote the
existing authority candidate.

The councils' mandatory inputs are authoritative requirements for this design:
complete key lifecycle and last-key recovery; durable authority/inbox saga
causality; protected journal anchoring or a permanently narrowed claim;
portable independent signing vectors; concurrency/crash/disk tests; and bounded
rejection monitoring.

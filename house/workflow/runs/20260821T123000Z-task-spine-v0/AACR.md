# Task-spine v0 after-action review

The useful design correction was making projection replacement transactional;
an interrupted rebuild now leaves the previous read model intact. Late worker
records are conserved as late evidence without reopening a sealed buffer.
Envelope repair creates a linked identity rather than rewriting prior evidence.

The result remains deliberately local and offline. Real process leases need
wall-clock expiry, fencing tokens, reconciliation, and controller ownership;
the event-count lease here is only a deterministic authority-path fixture.

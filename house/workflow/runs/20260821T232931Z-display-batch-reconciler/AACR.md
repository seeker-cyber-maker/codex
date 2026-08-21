# After-action review

## What worked

- Warp's ordered replay pattern fitted the existing versioned display-batch
  contract without changing its one-way authority boundary.
- The existing hash-bound batch identity made duplicate/conflict distinction
  deterministic.
- A bounded duplicate map corrected an otherwise easy memory-growth mistake:
  display recovery metadata is finite, while the conserved chain retains the
  complete history elsewhere.

## Limits retained

- No snapshot import, persistence, rendering, or live receiver exists.
- The 50-batch cap is a local safety bound, not a claim about the future iTerm
  transport's throughput.

## Decision

Accept as a narrow offline receiver primitive. Add a live binding only after a
separate iTerm/WebView lifecycle and source-capture acceptance gate.

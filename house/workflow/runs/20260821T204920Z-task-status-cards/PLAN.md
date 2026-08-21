# Read-only task-status cards

## Objective

Expose existing Task Packet routing and lifecycle evidence as a compact,
human-readable CLI surface without adding a dashboard process or touching the
canonical journal.

## Acceptance

1. Status reads only the canonical task-spine journal.
2. Each card shows the preserved model advisory, automatic route, optional
   manual choice, WIP and candidate metadata.
3. Status cannot rebuild a projection, switch a client model, or dispatch work.
4. Regression, lint, compilation, and diff checks pass.

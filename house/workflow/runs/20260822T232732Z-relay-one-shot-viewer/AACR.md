# After-action council review — relay one-shot viewer seam

## Outcome

Accepted after two bounded remediation rounds. The initial architecture was
sound, but its public clock/validator injection points were broader than the
relay-facing security claim. Removing them made the seam inherit the qualified
viewer policy without replacement hooks.

## Evidence improvements

Council review added direct natural-clock expiry, unknown-capability
non-consumption, response freezing, bearer omission, and post-consumption
connection-refusal tests. The final packet and exit-code-bearing validation
receipt received two independent `ACCEPT` dispositions.

## Workflow improvement

Routing advice is most useful before a task prompt or phase dispatch. Future
workflow prompts should begin with the recommended model and effort, then state
the bounded request. A later advisory remains useful only when evidence changes
the recommendation.

## Remaining boundary

This run does not qualify a browser, iTerm registration, operator authority,
persistent listener, worker/provider route, relay mutation, terminal input, or
reverse channel. Those remain future gates rather than implied follow-ons.

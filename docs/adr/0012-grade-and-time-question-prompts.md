---
status: accepted
---

# Grade and time question prompts while preserving continuation

Structured questions carry both a text label and color: `GREEN/PREFERENCE`
uses the recommended default after about three unanswered minutes;
`BLUE/PRECISION` may continue after three to five minutes under a declared
reversible assumption; `AMBER/TECHNICAL_GATE` pauses only the affected boundary
while adjacent safe work continues; and `RED/AUTHORITY_GATE` never crosses a
credential, safety, cost, destructive-action, or external-authority boundary by
timeout. Exact continuation signals such as `.`, `continue`, `go on`,
`go ahead`, and `do next step` resume the current bounded action, are signed
and logged like other answers, and never broaden authority merely through
brevity. Every question declares its recommended default, the fallback that
will actually be selected after timeout, and whether that fallback is permitted
at its severity. With an open question, `.` selects that permitted fallback;
without one, it advances the ordinary workflow's current bounded next step.
The literal `.` main-session shortcut follows the independently inspected
[OMP input-controller behavior at revision `72000ac`](https://github.com/can1357/oh-my-pi/blob/72000acfeb902e21816252699482887f34d1a5a4/packages/coding-agent/src/modes/controllers/input-controller.ts#L664-L681),
while recommended choices and timeout auto-selection are a separate Ask-tool
behavior.

A confirmed Blocker is not kept alive as an unanswered question. The affected
task branch enters a Paused Blocker state that names the failed acceptance
check, current evidence, the smallest remediation, and a Resolver Assignment
to the human, lead agent, or an external dependency. Agent-resolvable work is
queued for the capable agent rather than converted into a human prompt;
human-resolvable work creates one actionable reminder containing the exact ask;
external blockers use a bounded monitoring cadence and reassessment horizon.
Adjacent authorized work continues when dependency boundaries permit it.

Blocker reminders correlate under the same task and condition instead of
creating a new prompt at every interval. Their cadence may back off, but the
reminder persists until evidence clears the blocker, the objective becomes
moot, authority explicitly accepts the residual condition, or the task is
cancelled or superseded. A timeout never fabricates resolution or lets a task
cross the blocked acceptance boundary.

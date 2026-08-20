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

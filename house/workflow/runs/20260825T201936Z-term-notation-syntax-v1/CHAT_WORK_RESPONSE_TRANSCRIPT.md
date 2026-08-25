# Chat/Work response transcript

This is the locally rendered response text returned by the supervised Pi
chair. The provider wire envelope was not exposed. Formatting-only transport
details are not claimed to be preserved.

1. **Contradiction or ambiguity**
   - **Hypothesis:** `TERM?` allows optional `MEAN/NOT/SCOPE`, but the statement "any included detail line must be from the closed set" is unambiguous. However, it is unclear whether multiple `MEAN` lines are forbidden or simply fail closed.
   - `PREF= ... | preferred|not_preferred|no_preference|undetermined` implies single-choice semantics, but also mentions `ALT` after `not_preferred`; the grammar for `ALT` is not formally shown.

2. **Smallest safe cross-model dictionary fields**
   ```json
   {
     "operator": "TERM? | TERM= | TERM~ | PREF? | PREF=",
     "candidate": "string or null",
     "mean": "string or null",
     "not": "string or null",
     "scope": "string or null",
     "ctx": "string or null",
     "why": "string or null",
     "target": "string or null",
     "preference": "preferred | not_preferred | no_preference | undetermined | not_stated"
   }
   ```

3. **Negative fixtures**
   - Duplicate fields:
     ```
     TERM= X | MEAN foo | MEAN bar | SCOPE Y | CTX Z
     ```
   - Unknown fields:
     ```
     TERM? house | COLOR blue
     ```
   - Unknown operator:
     ```
     TERMM? X
     ```
   - Oversize value: a candidate longer than the declared maximum.
   - Control-plane leakage:
     ```
     TERM? door | EXEC open
     ```
   - Silent parse risk: missing required fields in `TERM=` or `TERM~`.

4. **Stop-hook coupling risks**
   - **Direct dependency:** None; the design performs no I/O and does not invoke or rely on Codex stop-hooks.
   - **Future integration risk:** If TERM validation is later gated behind stop-hook delivery, TERM correctness could be delayed or suppressed. Parsing should continue to fail closed regardless of hook status.

5. **Explicit non-blocking exclusions**
   - No global lexicon or command surface binding.
   - No task, relay, or authority effects.
   - Parser independence from CLI hooks.

6. **Preference line**
   ```
   PREF= target=TERM_NOTATION/1 | preferred|not_preferred|no_preference|undetermined
   ```

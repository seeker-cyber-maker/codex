# TERM notation standalone syntax slice

Status: `STANDALONE / DATA_ONLY / NOT PROMPT-INTEGRATED`

This module implements the first closed syntax and dictionary for Scoped
Terminology Repair notation (`TERM_NOTATION/1`). It parses one record into a
typed, immutable data object. It does not insert model context, update a task,
dispatch work, call a hook, or grant authority.

## Grammar

```ebnf
repair-query       = "TERM? ", value,
                     [ newline, "MEAN ", value ],
                     [ newline, "NOT ", value ],
                     [ newline, "SCOPE ", value ] ;

working-definition = "TERM= ", value,
                     " | MEAN ", value,
                     " | SCOPE ", value,
                     " | CTX ", context-id ;

unresolved         = "TERM~ ", value,
                     " | SCOPE ", value,
                     " | WHY ", value ;

preference-query   = "PREF? target=TERM_NOTATION/1" ;

preference-response = "PREF= target=TERM_NOTATION/1 | ", preference,
                      [ " | ALT ", value ] ;

preference = "preferred" | "not_preferred" |
             "no_preference" | "undetermined" ;
```

The `ALT` field is valid only with `not_preferred`. The wrapper-only
`not_stated` value cannot be parsed from model text; callers obtain it through
`missing_preference()` when a required response is absent.

Fields are closed, unique, and canonically ordered. Values are nonempty and
cannot contain `|`, a newline, or a control character. The parser rejects
unknown syntax rather than treating it as prose.

## Local check

```bash
python3 -m unittest discover -s house/term_notation/tests -v
```

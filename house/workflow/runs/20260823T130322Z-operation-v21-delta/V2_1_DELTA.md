# Operation contract v2.1 — bounded delta from v2

Status: `PROPOSED / NO IMPLEMENTATION / NO DISPATCH`

The sealed v2 proposal remains historical evidence. V2.1 changes exactly five
decision-bearing surfaces:

1. **Precedence removed.** Every cross-record fact must agree; disagreement
   refuses. No route, operation, profile, or human action repairs an earlier
   record in place.
2. **Routing semantics typed.** Advisory class, advisory model preference, and
   hard execution constraints are distinct. Every advisory input receives an
   explicit disposition in the route record.
3. **Assembler made zero-host-I/O.** `assemble_operation_v2` accepts verified
   descriptors and performs only schema checks, lexical string checks, and
   canonical in-memory record serialization/hashing. Observation, hashing of
   host files, and output reservation are separate producers.
4. **Qualification claim narrowed.** The first route-selection record is
   `STRUCTURE_BOUND_NO_DISPATCH`; a content hash is not a signature or proof of
   authorship. Signer admission remains a separate future gate.
5. **Project configuration strategy sealed.** Every operation chooses
   `PROJECT_CONFIG_IGNORED` or `PROJECT_INPUTS_CONTENT_ADDRESSED`; undeclared
   effective context or tool capability refuses.

No other v2 claim is promoted by this delta.

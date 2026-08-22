# After-action council review

The council found a concrete gap in the prior controller: an expired lease
could otherwise permit a second acquisition after a durable live intent.  This
slice fixes that invariant without widening execution capability.  The new
tests encode the finding directly.  Remaining runtime concerns are deliberately
not generalized away: the next runner proposal must be separately reviewed.

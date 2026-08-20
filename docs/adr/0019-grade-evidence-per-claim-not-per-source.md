---
status: accepted
---

# Grade evidence per claim rather than per source

Evidence Grade belongs to the relationship between an evidence item and an
exact claim or Verification Requirement, never permanently to a person,
organization, channel, or media type. A CoLateral build video can strongly show
what its author demonstrated while providing weak support that the methodology
is correct; a domain expert's technical explanation, a lead engineer describing
a system they built, and a generic “ten best ways” video have different access
and competence for different claims without any source receiving blanket truth
authority. The same separation applies to websites: an article hosted on the
Hugging Face blog can be direct evidence of what its author proposed or reported
without the venue certifying the concept, methodology, or author quality.
Provenance records authorship, transmission, venue, and lineage as neutral facts;
it is not a reputation proxy. Source Role is likewise neutral, while directness,
firsthand access, relevant expertise, declared scope, reproducibility, and
independent evidence explain the grade used by each route. Favorable dimensions
support the named claim only and never substitute for its required determination.

Evidence Grade is stored as an explainable vector, not a single score. Its
claim-relative dimensions are:

- directness: whether the item observes, derives, attributes, or merely repeats
  the exact claim;
- access fit: whether the source had firsthand access to the relevant system,
  event, artifact, or data;
- competence fit: demonstrated competence relevant to this claim, not general
  fame, job title, or author reputation;
- scope fit: whether the evidence addresses the exact claim, only part of it,
  or an adjacent matter;
- reproducibility: how independently inspectable, replayable, or testable the
  evidence is;
- independent corroboration: whether supporting evidence has genuinely separate
  lineage rather than repeating a common origin; and
- temporal fit: whether the evidence applies to the claim's declared time.

Each dimension may remain unknown. Dimensions are not averaged or collapsed
into stored authority. A query interface may derive a purpose-specific badge or
ordering, but it must expose the underlying vector and derivation and must not
write the presentation result back as evidence or Claim Status.

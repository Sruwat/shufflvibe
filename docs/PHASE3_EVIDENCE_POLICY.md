# Phase 3 — evidence and admission policy

## Admission

`Admitted` requires all of the following:

- supported venue category: bar, nightclub, pub, restaurant, or café;
- official website identity evidence, or a strong OSM secondary match;
- current Google rating and review count available at enrichment time;
- review count of at least 200 and rating above the category threshold;
- no closed/non-operational business status;
- at least five of the eleven SHUFFL factors supported by evidence or an
  explicit `not_specialised` flag;
- valid fit-out/opening evidence from the official source;
- review evidence is either absent or explicitly SHUFFL-owned/licensed.

## Decision meanings

- `Admitted`: all required evidence and quality gates pass.
- `Insufficient evidence`: a required fact is missing or unresolved. The
  pipeline does not guess a value.
- `Rejected`: a hard quality/policy failure occurs, such as unsupported type,
  low rating/review count, closed status, invalid score values, or unlicensed
  review evidence.

Every result contains `evidence_audit` with identity source, official status,
score coverage, review provenance, fit-out status, hard failures, and evidence
gaps. Google review text is never part of a durable output; only the
SHUFFL-owned review CSV can contribute permanent review evidence.

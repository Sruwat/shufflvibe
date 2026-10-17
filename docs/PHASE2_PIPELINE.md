# Phase 2 — discovery and official-source hardening

## Runtime order

1. Load the manually maintained `config/areas.csv`.
2. Resolve missing coordinates through Nominatim.
3. For only unresolved areas, use Google Places Text Search.
4. For anything still unresolved, use Overpass area-name lookup.
5. Query Google Nearby Search for `bar`, `night_club`, `pub`, `restaurant`,
   and `cafe`.
6. Deduplicate by normalized Google `place_id` and retain every category and
   area that produced the match.
7. Query Overpass as secondary venue evidence and match by fuzzy name plus
   coordinate distance; an OSM match never replaces Google identity.
8. Fetch the official website root and same-domain linked evidence pages for
   menu, booking, events, hours, contact/about, schedule, and music signals.
9. Run the deterministic scorer and optionally merge Gemini output.
10. Write failures to `pipeline_failures.json` and continue unaffected venues.

## Failure behavior

- A failed area geocoder does not abort immediately; it advances to the next
  resolver and records the attempted sources on the area record.
- A failed Overpass area is recorded as a pipeline failure. Google discovery
  can continue.
- A failed Google category request is recorded with area and category.
- A failed details/official enrichment request is recorded with `place_id`.
- Missing official evidence remains unknown and is never inferred as fact.

## Commands

```powershell
python venue_pipeline_backend/run_pipeline.py areas `
  --areas venue_pipeline_backend/config/areas.csv `
  --output-dir venue_pipeline_backend/data `
  --overpass

python venue_pipeline_backend/run_pipeline.py run `
  --areas venue_pipeline_backend/config/areas.csv `
  --output-dir venue_pipeline_backend/data
```

The pipeline produces `areas_resolved.json`, `osm_candidates.json`, and
`pipeline_failures.json` alongside the market-ready outputs.

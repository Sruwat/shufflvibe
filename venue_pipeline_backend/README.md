# SHUFFL Venue Pipeline Backend

Delhi + NCR venue database pipeline. It accepts a manual area list, resolves missing coordinates with OpenStreetMap Nominatim, optionally cross-checks venues through Overpass, discovers candidates with Google Places API (New), derives SHUFFL-owned scores, creates an official-source verification queue, and exports a licensing-safe market-ready database.

## Pipeline

```text
manual areas.csv/json -> Nominatim -> Overpass/OSM cross-check -> Google Nearby Search
-> temporary Google Details read -> review evidence/scoring -> discard Google content
-> official website/social verification -> admission -> human pass
-> own SQLite + JSON + CSV + Excel; Google details are fetched live at display time
```

## Setup

```powershell
$env:GOOGLE_PLACES_API_KEY = "YOUR_GOOGLE_PLACES_API_KEY"
python venue_pipeline_backend/run_pipeline.py run --areas venue_pipeline_backend/config/areas.csv --dry-run
```

The Google key must have **Places API (New)** enabled. Nearby Search, Place Details and Text Search are endpoints of that one API.

## Area input

Edit `venue_pipeline_backend/config/areas.csv`. Required columns:

```text
area,city,state,latitude,longitude,radius_meters,priority
```

Latitude and longitude may be blank; Nominatim fills them. Review `data/areas_resolved.json` before spending Google API calls.

## Commands

```powershell
# Resolve coordinates and optionally run Overpass
python venue_pipeline_backend/run_pipeline.py areas --areas venue_pipeline_backend/config/areas.csv --overpass

# Full run
python venue_pipeline_backend/run_pipeline.py run --areas venue_pipeline_backend/config/areas.csv

# Full run without Overpass
python venue_pipeline_backend/run_pipeline.py run --areas venue_pipeline_backend/config/areas.csv --skip-overpass

# Build legacy workbook (not licensing-safe for production)
node venue_pipeline_backend/export_excel.mjs venue_pipeline_backend/data

# Build the licensing-safe market-ready package from the transient staging run
python venue_pipeline_backend/make_candidates.py --out venue_pipeline_backend/data/candidates_south_delhi.csv --city Delhi --areas "Hauz Khas" "Saket" "Aerocity" "Vasant Kunj" "Mehrauli" "Chattarpur" "Greater Kailash I" "Greater Kailash II" "Defence Colony" "South Extension" "Khan Market" "Lodhi Road" "Okhla" "Sarita Vihar"
python venue_pipeline_backend/enrich.py --src venue_pipeline_backend/data/candidates_south_delhi.csv --output-dir venue_pipeline_backend/data_market_ready_v2
node venue_pipeline_backend/export_human_pass_excel.mjs venue_pipeline_backend/data_market_ready_v2

# Legacy auto website enrichment flow (not used by the clean MVP path)
python venue_pipeline_backend/auto_enrich.py --output-dir venue_pipeline_backend/data_market_ready
# Client edits only human_status/human_notes in the auto_review_queue sheet of the XLSX
python venue_pipeline_backend/promote_verified.py
python venue_pipeline_backend/build_market_ready.py
node venue_pipeline_backend/export_market_ready_excel.mjs venue_pipeline_backend/data_market_ready
```

Outputs are written to `venue_pipeline_backend/data_market_ready/`: candidates keyed by Google `place_id`, officially verified venues, hours, evidence-backed time slots, scores, score evidence, approved tags, field-level provenance, human pass, admission log, SQLite and Excel. Fill `config/official_verification.csv` before a candidate can become an active venue. The old `data/` folder is legacy staging and must not be shipped to production because it contains transient Google content.

The public Nominatim service has a one-request-per-second limit and requires a descriptive User-Agent. For large recurring runs, use a self-hosted Nominatim instance or a commercial geocoder. Google Maps pages are not scraped. The raw Google response cache is transient; the normalized database keeps only the selected structured fields, identifiers, derived scores, decisions and provenance needed by the MVP.

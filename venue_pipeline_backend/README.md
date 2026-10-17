# SHUFFL Venue Pipeline Backend

Delhi + NCR venue database pipeline. It accepts a manual area list, resolves missing coordinates with OpenStreetMap Nominatim, cross-checks venues through Overpass, discovers candidates with Google Places API (New), derives SHUFFL-owned scores with Gemini plus deterministic fallback, applies automatic admission, and exports a licensing-safe market-ready database. Human verification is not part of the build.

## Pipeline

```text
manual areas.csv/json -> Nominatim -> Overpass/OSM cross-check -> Google Nearby Search
-> temporary Google Details read -> review evidence/Gemini scoring -> automatic admission
-> explicit time slots or gold gaps -> own SQLite + JSON + CSV + Excel
; Google name/address/rating/reviews/hours are fetched live at display time
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

# Full automatic run; no human verification stage
python venue_pipeline_backend/run_pipeline.py run --areas venue_pipeline_backend/config/areas.csv

# Full run without Overpass
python venue_pipeline_backend/run_pipeline.py run --areas venue_pipeline_backend/config/areas.csv --skip-overpass

# Build legacy workbook (not licensing-safe for production)
node venue_pipeline_backend/export_excel.mjs venue_pipeline_backend/data

# Build the licensing-safe market-ready package from the transient staging run
python venue_pipeline_backend/make_candidates.py --out venue_pipeline_backend/data/candidates_south_delhi.csv --city Delhi --areas "Hauz Khas" "Saket" "Aerocity" "Vasant Kunj" "Mehrauli" "Chattarpur" "Greater Kailash I" "Greater Kailash II" "Defence Colony" "South Extension" "Khan Market" "Lodhi Road" "Okhla" "Sarita Vihar"
python venue_pipeline_backend/enrich.py --src venue_pipeline_backend/data/candidates_south_delhi.csv --output-dir venue_pipeline_backend/data_market_ready_v2
node venue_pipeline_backend/export_market_ready_excel.mjs venue_pipeline_backend/data_market_ready_v2

# Legacy auto website enrichment flow (not used by the clean MVP path)
python venue_pipeline_backend/auto_enrich.py --output-dir venue_pipeline_backend/data_market_ready
# The legacy verification scripts remain for old workbooks only; do not use them for the
# automatic production database.
```

Outputs are written to `venue_pipeline_backend/data_market_ready/` (or the selected output directory): candidates keyed by Google `place_id`, automatically admitted venues, live-display references, evidence-backed time slots, explicit gold schedule gaps, scores, not-specialised flags, score evidence, approved tags, field-level provenance, admission log, SQLite and Excel. There is no human-pass or human-verification dependency. The old `data/` folder is legacy staging and must not be shipped to production because it contains transient Google content.

The public Nominatim service has a one-request-per-second limit and requires a descriptive User-Agent. For large recurring runs, use a self-hosted Nominatim instance or a commercial geocoder. Google Maps pages are not scraped. The raw Google response cache is transient; the normalized database keeps only the selected structured fields, identifiers, derived scores, decisions and provenance needed by the MVP.
# SHUFFL Venue Pipeline

The auto-only pipeline now supports official website evidence and SHUFFL-owned review analytics.

## SHUFFL-owned reviews (Option B)

Put user reviews in `config/shuffl_reviews.csv` using:

```text
google_place_id,rating,review_text,reviewed_at
ChIJ...,5,"Great music and food",2026-10-12
```

Only reviews owned by SHUFFL may be used for permanent review distribution. The pipeline produces count, mean, 1–5 distribution, and evidence provenance. Google review data remains transient/live-only.

## Run

```powershell
python venue_pipeline_backend\run_pipeline.py run `
  --areas venue_pipeline_backend\config\areas.csv `
  --shuffl-reviews venue_pipeline_backend\config\shuffl_reviews.csv `
  --output-dir venue_pipeline_backend\data_auto_only_full
node venue_pipeline_backend\export_market_ready_excel.mjs venue_pipeline_backend\data_auto_only_full
```

Official website pages are fetched from each venue's `websiteUri` when available. The extractor records official identity, hours, menu/booking/event URLs, social URLs, explicit schedule evidence, and fit-out evidence. Missing evidence remains `unknown` or `gold`; it is never inferred from venue type.

Admission policy: a missing fit-out year/status is `auto_insufficient_evidence` and is excluded from the active `Venues` table, but retained in `Candidates` and `Admission_Log`. It is not silently admitted and is not treated as a quality rejection. Optional official social/event credentials are read from `.env` when supplied. Overpass retries the configured endpoint and fallback endpoints before recording an area failure.

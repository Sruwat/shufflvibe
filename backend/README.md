# SHUFFL South Delhi venue database pipeline

This folder builds and validates the South Delhi venue database used by SHUFFL.

## What the pipeline does

1. Discovers South Delhi candidates through OpenStreetMap/Overpass.
2. Enriches candidates through Foursquare Places when `FOURSQUARE_API_KEY` is supplied.
3. Verifies public official venue pages without login, CAPTCHA bypass, or private social data.
4. Uses the supplied workbook as the current research seed and keeps source URLs/audit dates.
5. Validates IDs, duplicates, status values, score ranges, URLs, time slots, and source coverage.
6. Produces a validation report and a machine-readable staging directory for the workbook refresh.

## Current seed workbook

The supplied workbook is expected at:

`backend/data/SHUFFL_South_Delhi_Venue_Database_MVP.xlsx`

The source workbook contains the current South Delhi research pass. It is a seed, not a claim that the census is exhaustive or that every field is verified.

## Setup

PowerShell:

```powershell
$env:GOOGLE_MAPS_API_KEY = "YOUR_KEY"
```

Enable billing and Places API (New) in Google Cloud before running live discovery. The client uses explicit field masks to control cost.

## Commands

```powershell
python backend/run_pipeline.py validate --workbook backend/data/SHUFFL_South_Delhi_Venue_Database_MVP.xlsx
python backend/run_pipeline.py discover --output-dir backend/staging
python backend/run_pipeline.py enrich --input backend/staging/place_ids.json --output-dir backend/staging
python backend/run_pipeline.py build-report --workbook backend/data/SHUFFL_South_Delhi_Venue_Database_MVP.xlsx --output-dir backend/staging
```

To refresh the validator's CSV view of the workbook with the bundled Node runtime:

```powershell
# Run once per checkout. This junction points at the bundled workspace packages.
New-Item -ItemType Junction -Path backend/node_modules -Target "C:\Users\shank\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules"
node backend/tools/export_workbook_csv.mjs backend/data/SHUFFL_South_Delhi_Venue_Database_MVP.xlsx backend/data/csv_export
```

The OSM discovery stage does not require a key. Foursquare discovery requires `FOURSQUARE_API_KEY`.
The legacy Google commands remain available only for licensed/live display verification and require
`GOOGLE_MAPS_API_KEY`; Google Maps pages are not scraped.

## Local API start on Windows

Use the guarded launcher so an already-running API is reused instead of
starting a second Uvicorn process on the same port:

```powershell
.\backend\start_local.ps1 -Port 8005 -Reload
```

If the script reports that the API is already running, open
`http://127.0.0.1:8005/admin/`. MySQL is expected on `127.0.0.1:3306`.

For the locked free/low-cost stack:

```powershell
python backend/run_pipeline.py osm-discover --output-dir backend/staging
$env:FOURSQUARE_API_KEY = "YOUR_SERVICE_API_KEY"
python backend/run_pipeline.py foursquare-discover --output-dir backend/staging
python backend/run_pipeline.py site-verify --input backend/staging/osm_candidates.json --output-dir backend/staging
```

## Important data policy

Google response bodies are not used as a scraping source. Durable venue facts must be sourced from
OSM, official venue pages, licensed providers, venue agreements, or SHUFFL's own user captures.
Foursquare responses are treated as licensed-source data and should be displayed/retained according
to the Foursquare agreement; do not commit API responses or keys to Git.

# SHUFFL Venue Admin — simple operating guide

## What the admin owns

The MySQL `admin_venues` table is the operational source of truth. The dashboard can:

1. sync pipeline output from `venue_pipeline_backend/data_auto_only_final_v2`;
2. add one venue manually;
3. import `.xlsx`, `.xlsm` or `.csv` files;
4. filter by city, state, area, admission and verification;
5. open a complete venue profile;
6. edit SHUFFL fields and keep an audit trail; and
7. export the database to Excel.

## What one venue contains

The venue profile keeps the pipeline facts and evidence together: Google `place_id`, area/city/state, official identity, official website, menu/booking/social links, OSM/source provenance, opening-hours status, time slots, SHUFFL factor scores, score evidence, tags, admission reasons, fit-out evidence, operator class, nearest metro, manual vibe and editorial notes.

## Live Google display data

When an admin opens Preview, the API uses the stored `google_place_id` to fetch current Google name, address, coordinates, rating, review count, review excerpts, opening hours and photos. The photo proxy keeps the Google key on the server. These fields are request-scoped and are not written to MySQL.

## Gemini

The Preview endpoint sends the current live response to Gemini for derived description/tags/scores when quota is available. If Gemini is unavailable or rate-limited, the dashboard shows a clearly labelled deterministic fallback. The fallback never hides the reason.

## Adding one venue

Use **Venues → Add venue**. Name is required. Add a Google Place ID when known; it enables live Google Preview. Add official website, menu, booking, social links, nearest metro, vibe, tags and notes. The venue starts as **Insufficient evidence / In process** unless an admin later changes it.

## Importing files

Use **Import Excel**. Every sheet is read. The first row is treated as headers. Recommended headers are `name` or `display_name`, `google_place_id`, `city`, `state`, `area`, `website_url` or `official_url`, `menu_url`, `booking_url`, `metro_name`, `metro_distance_km`, `manual_vibe`, `manual_tags`, and `manual_notes`. Matching `google_place_id` records are updated; new records are inserted.

## Optional human verification

Verification is intentionally optional. `In process` means the record can be improved later. `Verified` means the admin has checked the important official source details. `Rejected` keeps the record out of the app. Manual changes are written to `admin_audit_log`.

## Safe operating rule

Run **Sync pipeline** whenever new pipeline output exists. It refreshes pipeline facts but preserves `admin_override`, so manually entered venue data is not silently lost.

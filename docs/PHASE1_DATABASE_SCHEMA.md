# SHUFFL MVP — Phase 1 database contract

Phase 1 establishes MySQL as the operational source of truth for the admin
dashboard and the mobile app. `admin_venues` remains the lifecycle and
publication root so existing dashboard data continues to work. Structured
venue data is also available in normalized tables:

- `venue_identity`: official/editorial identity, website/social links,
  operator and fit-out evidence, and nearest metro.
- `venue_scores`: one row per SHUFFL factor and venue, with method and
  evidence metadata.
- `venue_tags`: controlled SHUFFL tags and explicit `not_specialised` flags.
- `venue_sources`: provenance for every durable field or evidence item.
- `venue_time_slots`: only official/SHUFFL schedule evidence. This is not a
  cache for Google opening hours.
- `venue_metros`: nearest metro data and source reference.

## Google display-only rule

The canonical schema intentionally does not contain Google rating, review
text/count, address, coordinates, or opening-hours columns. The public API
will use `google_place_id` from `admin_venues` to fetch those values at display
time. They must not be copied into durable venue rows.

## Applying the schema

From the `backend` directory:

```powershell
alembic upgrade head
```

The FastAPI/admin bootstrap also calls the same additive schema contract so a
fresh local SQLite database gets the tables automatically. Existing rows are
preserved; no destructive migration is performed.

## Phase 1 exit criteria

- MySQL and SQLite both create the same canonical venue tables.
- Existing `admin_venues` rows remain intact.
- Dashboard publication status remains the app visibility gate.
- Google display-only fields are absent from durable canonical tables.
- Later API work can query normalized tables without parsing `data_json`.

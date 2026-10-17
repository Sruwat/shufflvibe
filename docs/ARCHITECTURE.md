# SHUFFL repository architecture

This repository has one shared product backend and three user-facing surfaces.

## Repository layout

```text
SHUFFL/
├── mobile/                 Expo application (canonical app source)
├── backend/                FastAPI API, migrations, stores and tests
│   └── venue_db/            Venue database access and domain helpers
├── admin_dashboard/        Admin browser frontend, served by the API
├── website/                Public marketing website
├── venue_pipeline_backend/ Venue discovery, enrichment and export jobs
├── docs/                   Engineering plans, audits and architecture notes
└── shuffl-docs/            Preserved product specifications and brand assets
```

The older top-level `decisions/`, `frontend/`, `simulations/`, `specs/` and `superseded/`
folders are retained as reference material for existing links and historical context. New
runtime code belongs only in the active folders above.

## Active surfaces

- `mobile/` — canonical Expo mobile app source.
- `backend/` — canonical FastAPI API, database stores, migrations, tests and operational tools.
- `backend/venue_db/` — venue database access and venue-domain helpers.
- `venue_pipeline_backend/` — venue discovery, enrichment and export pipeline consumed by the API and admin operations.
- `admin_dashboard/` — browser dashboard mounted by the API at `/admin/`.
- `website/` — public static marketing site.

## Shared wiring

```text
mobile/ ───────────────────┐
admin_dashboard/ ──────────┼──> backend/ (FastAPI, /v1/*)
website/ ──────────────────┘

venue_pipeline_backend/ ───> backend stores and venue data
backend/venue_db/ ─────────> database and venue-domain access
```

The API serves the admin dashboard from `admin_dashboard/` and serves venue media from
`backend/data/media/`. The mobile client uses `EXPO_PUBLIC_API_URL`; the website is static and
should use the deployed app URL rather than importing application code directly.

## Canonical product documentation

`shuffl-docs/shuffl-spec-main/` remains the preserved product-spec location. It is reference
material and is not imported by runtime code.

## Legacy recovery material

`archive/legacy/app_code_snapshot/` is a recovery copy of the older duplicate app tree. It is not
an active runtime source and must not be used for builds. The old duplicate root `app_code/` has
been removed from the active repository layout.

## Validation gates before merging restructuring work

1. `python -m pytest backend/tests -q`
2. `npm run typecheck` from `mobile/`
3. `npm run test` from `mobile/`
4. Start the API and verify `/v1/health/readiness` and `/admin/`.
5. Start the website and verify all public pages and app links.

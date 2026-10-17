# SHUFFL Venue Platform Operations

## Local setup

1. Copy `backend/.env.example` to `backend/.env`.
2. Set `DATABASE_URL` to a disposable local SQLite URL for development, or the approved MySQL/PostgreSQL URL for a deployment.
3. Set a non-default `ADMIN_API_TOKEN` before exposing `/admin/` beyond localhost.
4. Keep `APP_ENV=development` for local work. `production` and `staging` fail closed when admin authentication is missing.
5. Set `SHUFFL_DEMO_MODE=1` only when deliberately testing fixture venues. Production API-backed builds must keep it `0`.
6. Set mobile `EXPO_PUBLIC_API_URL` in the build environment; otherwise the mobile app intentionally stays in fixture/demo mode.

## Venue lifecycle

Admin edits are drafts. Use the admin API or dashboard lifecycle controls:

- `PATCH /v1/admin/venues/{venue_id}` saves a draft and writes override/history records.
- `POST /v1/admin/venues/{venue_id}/publish` publishes only `AUTO_APPROVED` or `PROVISIONAL` venues.
- `POST /v1/admin/venues/{venue_id}/unpublish` removes a venue from public discovery without deleting it.
- `POST /v1/admin/venues/{venue_id}/archive` hides the record while retaining it.
- `POST /v1/admin/venues/{venue_id}/restore` returns an archived record to draft.
- `GET /v1/admin/venues/{venue_id}/history` returns change history.

Public discovery is served by `/v1/discovery` and only returns published, eligible, non-rejected records. It returns `dto_version: venue-dto-v1` data.

## Media development adapter

The local adapter accepts JPEG, PNG, and WebP files up to 8 MB and stores them under `backend/data/media/`. It records rights status and alt text in `venue_media`. Before production, replace local disk storage with approved object storage, add image dimensions/variant processing, and configure private upload authorization.

## Migration and rollback

The additive migration is `backend/alembic/versions/0002_venue_platform.py`. Back up the database and generated pipeline snapshot before applying it. Do not use a destructive downgrade: restore the dated backup and redeploy the previous revision during an approved maintenance window.

## Pipeline safety

Do not start Google or Gemini jobs without explicit credentials, quota/budget review, and an approved run window. The existing pipeline snapshot can be synced through the admin control. Paid external calls were intentionally not executed as part of the implementation pass.

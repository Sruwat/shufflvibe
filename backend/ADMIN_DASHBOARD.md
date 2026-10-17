# SHUFFL admin dashboard

The dashboard is served by the FastAPI app at `/admin/` and uses the same admin database as the public venue API.

## Database

Production uses MySQL through `DATABASE_URL`:

```powershell
$env:DATABASE_URL = "mysql+pymysql://shuffl_user:password@127.0.0.1:3306/shuffl"
$env:ADMIN_API_TOKEN = "use-a-long-random-token"
```

In MySQL Workbench, run this once in a query tab before starting the app:

```sql
CREATE DATABASE IF NOT EXISTS shuffl
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Use a dedicated MySQL user for the app when possible. Do not put the Workbench
password in source control or chat. Copy `.env.example` to `backend/.env`, then
replace the `DATABASE_URL` placeholder locally. The app now loads `backend/.env`
automatically at startup and keeps process-level environment variables higher
priority.

If `DATABASE_URL` is not set, local development uses `backend/data/shuffl_admin.db` so the dashboard can be tested without a database server.

## Start

```powershell
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --port 8000
```

Open `http://127.0.0.1:8000/admin/`. Enter the same `ADMIN_API_TOKEN` in the dashboard when one is configured.

## Sync the venue pipeline

The pipeline output is imported into `admin_venues` while preserving `admin_override` values. Run it from the dashboard's **Sync pipeline** button or:

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/v1/admin/sync
```

The admin record keeps pipeline facts, source evidence, scores, tags, hours and time slots together. Manual edits are stored in `admin_override`, and every edit is written to `admin_audit_log`. Syncing later does not erase manual overrides.

## App reflection

`GET /v1/venues` now reads admitted, non-rejected records from `admin_venues`. The app receives the manual tags/vibe and SHUFFL scores from this store. Google name, address, coordinates, hours, ratings and reviews remain display-time fields fetched with `google_place_id`; they are not copied into the durable database.

## Excel handoff

`GET /v1/admin/export.xlsx` downloads a workbook with:

- `Venues`: pipeline fields plus the JSON override payload
- `Users`: admin-visible user directory
- `Audit_Log`: manual edit history

The detailed source pipeline workbook remains available under `venue_pipeline_backend/data_auto_only_final_v2/`.

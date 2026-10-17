# SHUFFL Phase 6 — production operations

Phase 6 adds the controls needed to run the venue database safely. It does not
store Google reviews, coordinates, or opening hours permanently; live Google
enrichment remains display-time only.

## Configuration

Copy `backend/.env.example` to `backend/.env` locally. For staging/production,
set these values in the deployment secret manager instead of committing them:

- `DATABASE_URL` — MySQL URL for the canonical database.
- `ADMIN_API_TOKEN` or `ADMIN_ROLE_TOKENS` — non-placeholder admin secret.
- `GOOGLE_PLACES_API_KEY` — restricted to the required Places APIs and server IPs.
- `CORS_ALLOWED_ORIGINS` — the exact app/admin origins, comma separated.
- `SHUFFL_RATE_LIMIT_PER_MINUTE` and `SHUFFL_STOP_OPTIONS_RATE_LIMIT_PER_MINUTE`.

The readiness probe is `GET /v1/health/readiness`. A deployment is ready only
when both configuration and database checks are `ok`. Every response includes
an `X-Request-ID`; logs contain that ID, method, path, status, and duration but
never query strings or API tokens.

## Database migration and backup

Run migrations before starting the API:

```powershell
alembic upgrade head
python backend/tools/backup_database.py --output-dir backend/backups
```

The backup creates timestamped JSON and Excel files. JSON contains the database
rows needed for recovery; Excel is the human-readable export. It excludes
`.env` and secrets. Keep backups outside public/static directories and use
encrypted storage plus a retention policy in production.

## Scheduled sync

Use Windows Task Scheduler or a server scheduler to run the existing pipeline
and then the admin sync command. A safe Windows action is:

```powershell
python venue_pipeline_backend/run_pipeline.py run --areas venue_pipeline_backend/config/areas.csv --output-dir venue_pipeline_backend/data_auto_only_final_v2
python -c "from backend.app.admin_store import store; print(store.sync_from_source())"
python backend/tools/backup_database.py --output-dir backend/backups
```

Schedule only after API keys and quota limits are configured. Failed admin runs
remain visible in `GET /v1/admin/pipeline/runs` and can be retried from the
dashboard; the public stop-options endpoint is rate-limited because it may
perform live Google enrichment.

## Launch gates

Before opening the app to users, verify:

1. `GET /v1/health/readiness` returns `ready` in staging.
2. `alembic current` is at `head` and a backup can be restored to a test DB.
3. The staging pipeline has no unexplained failures and all published venues
   have canonical evidence, admission status, and source provenance.
4. Google Places display, photo, attribution, retention, and billing terms have
   been reviewed by the project owner.
5. CORS origins, admin tokens, database credentials, and API key restrictions
   are production values and are not present in Git or logs.

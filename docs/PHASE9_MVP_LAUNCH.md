# SHUFFL Phase 9 — final MVP launch

Phase 9 is the final implementation phase. It packages the system for a
controlled MVP launch and verifies the running API without spending provider
quota.

## Launch sequence

1. Apply migrations: `alembic upgrade head`.
2. Create a backup: `python backend/tools/backup_database.py --output-dir backend/backups`.
3. Run the canonical repair if a new import was made:
   `python backend/tools/repair_canonical.py`.
4. Start the API with production secrets and an explicit CORS allow-list.
5. Run the smoke test:
   `python backend/tools/smoke_test.py --base-url https://api.example.com`.
6. Confirm the Phase 7 launch audit is green.
7. Release the mobile build only after the public catalogue returns published,
   admitted venues.

## What the smoke test covers

`backend/tools/smoke_test.py` checks health, database readiness, locked MVP
release scope, public discovery, public venue list, hosted rooms,
conversations, notifications, admin summary, launch-audit readiness, and Excel
export. It sends the admin token only as a request header and never prints it.
It deliberately does not call `/v1/venues/stop-options`, because that endpoint
can perform live Google enrichment and consume quota.

This smoke test proves backend launch readiness only. It does not replace the
Phase 8 device-level screenshot comparison; visual parity still requires
captures from the target Android/iOS device (or a browser session reachable by
the capture tool).

## Rollback and monitoring

- Keep the last known-good API build and database backup together.
- If readiness fails, stop public traffic, restore the backup to a separate
  database, and compare the Phase 7 audit before switching back.
- Monitor `X-Request-ID`, 5xx responses, 429 responses, failed pipeline runs,
  Google quota, and backup creation.
- Never make Google reviews, Google coordinates, Google hours, Google address,
  or Google photos part of the durable catalogue.

## MVP acceptance gates

- Phase 7 audit: `ready_for_launch: true`.
- Smoke test: every check returns `ok`.
- MySQL backup and restore have been tested once in staging.
- Admin token, database password, API keys, CORS origins, billing limits,
  Google attribution/retention terms, and privacy policy are production-ready.

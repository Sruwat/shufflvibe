"""Create a portable JSON + Excel backup of the canonical venue database.

This deliberately uses SQLAlchemy rather than mysqldump so the same command
works in local SQLite, staging MySQL, and production MySQL. It never reads or
copies backend/.env.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

VENUE_TABLES = (
    "admin_venues", "venue_identity", "venue_scores", "venue_tags",
    "venue_sources", "venue_time_slots", "venue_metros", "admin_users",
    "admin_audit_log", "venue_publication_versions", "venue_manual_overrides",
    "venue_change_history", "venue_pipeline_runs", "venue_media",
)

# A launch backup must be able to restore the product state, not only the
# catalogue.  These tables are intentionally explicit so a new table cannot
# silently disappear from backups.
APP_TABLES = (
    "users", "profiles", "assessment_sessions", "card_exposures", "plans",
    "plan_stops", "rooms", "join_requests", "capsules", "conversations",
    "messages", "notifications", "reports", "privacy_settings", "feature_flags",
    "auth_users", "auth_sessions", "auth_verification_tokens",
    "auth_password_reset_tokens", "app_runtime_state",
)
TABLES = VENUE_TABLES + APP_TABLES


def main() -> int:
    parser = argparse.ArgumentParser(description="Back up the complete SHUFFL application database")
    parser.add_argument("--output-dir", default="backend/backups")
    args = parser.parse_args()
    from app.admin_store import store  # noqa: PLC0415
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    payload: dict[str, object] = {"created_at": datetime.now(timezone.utc).isoformat(), "tables": {}}
    counts: dict[str, int] = {}
    missing_tables: list[str] = []
    with store.engine.connect() as connection:
        for table in TABLES:
            try:
                rows = [dict(row) for row in connection.execute(text(f"SELECT * FROM {table}")).mappings().all()]
            except Exception:
                missing_tables.append(table)
                rows = []
            payload["tables"][table] = rows  # type: ignore[index]
            counts[table] = len(rows)
    if missing_tables:
        raise RuntimeError(f"Backup aborted; required tables are missing: {', '.join(missing_tables)}")
    payload["schema"] = {"tables": list(TABLES), "complete": True}
    json_path = output_dir / f"shuffl_backup_{stamp}.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    workbook = store.export_xlsx()
    xlsx_path = output_dir / f"shuffl_backup_{stamp}.xlsx"
    xlsx_path.write_bytes(workbook.getvalue())
    print(json.dumps({"json": str(json_path), "xlsx": str(xlsx_path), "counts": counts}, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

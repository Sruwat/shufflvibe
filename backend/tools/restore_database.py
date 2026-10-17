"""Restore a SHUFFL JSON backup into the configured database.

This is intentionally an explicit, destructive maintenance command. It never
runs without ``--confirm`` and supports ``--dry-run`` for validation.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys

from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))


def main() -> int:
    parser = argparse.ArgumentParser(description="Restore a SHUFFL JSON database backup")
    parser.add_argument("backup", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--confirm", action="store_true", help="allow replacing rows in the target database")
    parser.add_argument("--allow-live", action="store_true", help="explicitly allow a destructive restore into MySQL/PostgreSQL")
    args = parser.parse_args()
    payload = json.loads(args.backup.read_text(encoding="utf-8"))
    tables = payload.get("tables")
    if not isinstance(tables, dict) or not tables:
        raise SystemExit("Backup has no tables")
    from app.admin_store import store  # noqa: PLC0415
    if store.engine.dialect.name != "sqlite" and not args.allow_live:
        raise SystemExit("Refusing destructive restore into a live database. Use an isolated SQLite target, or explicitly pass --allow-live.")
    # A fresh rehearsal target does not yet have the auth/runtime tables that
    # are owned by their stores rather than AdminStore.
    from app.auth_store import AuthStore  # noqa: PLC0415
    from app.state_store import RuntimeStateStore  # noqa: PLC0415
    from app.models import Base  # noqa: PLC0415
    AuthStore(store.engine)
    RuntimeStateStore(store.engine)
    Base.metadata.create_all(store.engine)
    with store.engine.connect() as connection:
        existing = set(connection.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).scalars().all()) if store.engine.dialect.name == "sqlite" else set()
        missing = [name for name in tables if existing and name not in existing]
    if missing:
        raise SystemExit(f"Target is missing tables: {', '.join(missing)}")
    counts = {name: len(rows) for name, rows in tables.items() if isinstance(rows, list)}
    if args.dry_run:
        print(json.dumps({"dry_run": True, "tables": counts}, indent=2))
        return 0
    if not args.confirm:
        raise SystemExit("Restore is destructive. Re-run with --confirm, or use --dry-run first.")
    # Child-first deletion avoids foreign-key failures.  Tables not present in
    # a particular old backup are simply skipped.
    delete_order = [
        "messages", "notifications", "reports", "card_exposures", "plan_stops",
        "join_requests", "capsules", "conversations", "plan_stops", "plans", "rooms", "profiles", "users",
    ]
    ordered = delete_order + [name for name in tables if name not in delete_order]
    with store.engine.begin() as connection:
        for table in ordered:
            if table not in tables:
                continue
            connection.execute(text(f"DELETE FROM {table}"))
        for table, rows in tables.items():
            if not rows:
                continue
            columns = list(rows[0].keys())
            names = ",".join(columns)
            bind_names = ",".join(f":{column}" for column in columns)
            for row in rows:
                row = dict(row)
                # Older backups predate token expiry columns.  Preserve the
                # session for rehearsal with a bounded compatibility expiry;
                # production restores should rotate sessions after recovery.
                if table == "auth_sessions" and not row.get("expires_at"):
                    row["expires_at"] = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
                connection.execute(text(f"INSERT INTO {table} ({names}) VALUES ({bind_names})"), row)
    print(json.dumps({"restored": True, "tables": counts}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

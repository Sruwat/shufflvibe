"""Migrate legacy ``app_runtime_state`` user-facing records into SQL tables.

Run once with ``--dry-run`` first, then ``--apply``. The command is idempotent
for messages, notifications and reports and prints counts/mismatches instead
of silently overwriting canonical rows.
"""

from __future__ import annotations

import argparse
import json
import sys

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.dry_run == args.apply:
        raise SystemExit("Choose exactly one of --dry-run or --apply")
    from backend.app.main import _auth_accounts, _messages, _notifications, _profiles, _reports, _runtime_state, _domain_store
    from backend.app.models import JoinRequest, Plan, Room

    legacy = {
        "profiles": _runtime_state.load("profiles") or _profiles,
        "messages": _runtime_state.load("messages") or _messages,
        "notifications": _runtime_state.load("notifications") or _notifications,
        "reports": _runtime_state.load("reports") or _reports,
    }
    summary = {key: len(value) if hasattr(value, "__len__") else 0 for key, value in legacy.items()}
    legacy_plans = _runtime_state.load("plans") or {}
    legacy_rooms = _runtime_state.load("rooms") or []
    summary["plans"] = len(legacy_plans)
    summary["rooms"] = len(legacy_rooms)
    summary["auth_accounts"] = len(_auth_accounts)
    if args.dry_run:
        print(json.dumps({"dry_run": True, "legacy_counts": summary}, indent=2, default=str))
        return 0
    migrated = {"profiles": 0, "messages": 0, "notifications": 0, "reports": 0, "plans": 0, "rooms": 0, "join_requests": 0}
    for user_id, profile in (legacy["profiles"] or {}).items():
        _domain_store.ensure_user(str(user_id), name=str((profile or {}).get("name", "")))
        migrated["profiles"] += 1
    for message in legacy["messages"]:
        if not message.get("id") or not message.get("body"):
            continue
        existing = _domain_store.conversation_messages(str(message.get("conversation_id", "conversation-demo")))
        if any(row.get("id") == message["id"] for row in existing):
            continue
        _domain_store.add_message(message_id=str(message["id"]), conversation_id=str(message.get("conversation_id", "conversation-demo")), sender_id=str(message.get("sender_id", "demo-user")), body=str(message["body"]))
        migrated["messages"] += 1
    for notification in legacy["notifications"]:
        if not notification.get("id"):
            continue
        user_id = str(notification.get("user_id", "demo-user"))
        if any(row.get("id") == notification["id"] for row in _domain_store.list_notifications(user_id)):
            continue
        payload = {key: value for key, value in notification.items() if key not in {"id", "user_id", "kind", "read", "created_at"}}
        _domain_store.add_notification(notification_id=str(notification["id"]), user_id=user_id, kind=str(notification.get("kind", "system")), payload=payload)
        migrated["notifications"] += 1
    for report in legacy["reports"]:
        if not report.get("id"):
            continue
        if any(row.get("id") == report["id"] for row in _domain_store.list_reports()):
            continue
        _domain_store.add_report(report_id=str(report["id"]), reporter_id=str(report.get("reporter_id", "demo-user")), target_id=str(report.get("target_id", "")), reason=str(report.get("reason", "")))
        migrated["reports"] += 1
    # Rooms must be inserted before plans because Plan.room_id is a foreign
    # key.  The migration is idempotent and only handles the stable fields;
    # richer stop rows are created by the canonical plan API going forward.
    from sqlalchemy import select
    with _domain_store.Session.begin() as session:
        for raw_room in legacy_rooms:
            room_id = str(raw_room.get("id", ""))
            host_id = str(raw_room.get("owner_id") or raw_room.get("host_id") or (raw_room.get("members") or ["demo-user"])[0])
            if not room_id:
                continue
            _domain_store.ensure_user(host_id)
            if not session.get(Room, room_id):
                session.add(Room(id=room_id, host_id=host_id, title=str(raw_room.get("title", "SHUFFL room")), visibility=str(raw_room.get("visibility", "friends")), status=str(raw_room.get("status", "draft"))))
                migrated["rooms"] += 1
        for plan_id, raw_plan in legacy_plans.items():
            if session.get(Plan, str(plan_id)):
                continue
            room_id = next((str(room.get("id")) for room in legacy_rooms if str(room.get("plan_id", "")) == str(plan_id)), None)
            owner_id = "demo-user"
            session.add(Plan(id=str(plan_id), user_id=owner_id, room_id=room_id, style=str((raw_plan.get("venue_types") or ["Open Night"])[0]), chemistry=raw_plan.get("chemistry") or {}, status=str(raw_plan.get("status", "draft")), locked_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc) if raw_plan.get("locked") else None))
            migrated["plans"] += 1
        for raw_room in legacy_rooms:
            room_id = str(raw_room.get("id", ""))
            for member_id in raw_room.get("members", [])[1:]:
                member_id = str(member_id)
                _domain_store.ensure_user(member_id)
                existing = session.scalar(select(JoinRequest).where(JoinRequest.room_id == room_id, JoinRequest.user_id == member_id))
                if not existing:
                    session.add(JoinRequest(room_id=room_id, user_id=member_id, status="accepted", note="migrated"))
                    migrated["join_requests"] += 1
    print(json.dumps({"applied": True, "legacy_counts": summary, "migrated": migrated}, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

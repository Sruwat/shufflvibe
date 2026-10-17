"""Small SQLAlchemy repository for durable user-facing domain state.

The legacy runtime aggregate remains available for migration compatibility, but
new authenticated chat, notification and report operations use this store.
It deliberately contains no venue Google payloads; those remain display-time
enrichment as required by the venue data policy.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import json
from uuid import uuid4

from sqlalchemy import select, text
from sqlalchemy.orm import Session, sessionmaker

from .models import Base, Conversation, Message, Notification, PrivacySettings, Profile, Report, User


class DomainStore:
    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.Session = sessionmaker(bind=engine, expire_on_commit=False)
        # AdminStore owns the one-time schema creation.  Avoid running a
        # second metadata DDL pass during every API import: on Windows this
        # can hold a SQLite/MySQL metadata lock while the HTTP test subprocess
        # is starting.  Availability is checked by the first repository call.
        self.available = True

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    def ensure_user(self, user_id: str, *, email: str | None = None, name: str = "") -> None:
        if not self.available:
            return
        with self.Session.begin() as session:
            user = session.get(User, user_id)
            if not user:
                session.add(User(id=user_id, email=email))
            if name or email:
                profile = session.scalar(select(Profile).where(Profile.user_id == user_id))
                if not profile:
                    session.add(Profile(user_id=user_id, display_name=name or (email or "")))
                elif name:
                    profile.display_name = name

    def ensure_domain_schema(self) -> None:
        """Create the small compatibility columns/tables needed by the
        normalized domain repositories.

        The venue catalogue remains owned by AdminStore. These tables contain
        only user-owned application state and are deliberately free of Google
        display payloads.
        """
        with self.engine.begin() as conn:
            for statement in (
                "ALTER TABLE plans ADD COLUMN metadata_json TEXT",
                "ALTER TABLE rooms ADD COLUMN metadata_json TEXT",
                "ALTER TABLE privacy_settings ADD COLUMN visibility_json TEXT",
            ):
                try:
                    conn.execute(text(statement))
                except Exception:
                    pass
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS room_members (
                    room_id VARCHAR(36) NOT NULL,
                    user_id VARCHAR(180) NOT NULL,
                    role VARCHAR(24) NOT NULL DEFAULT 'member',
                    joined_at VARCHAR(40) NOT NULL,
                    PRIMARY KEY (room_id, user_id)
                )
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS room_invites (
                    invite_id VARCHAR(64) PRIMARY KEY,
                    room_id VARCHAR(36) NOT NULL,
                    invite_token VARCHAR(180) UNIQUE NOT NULL,
                    created_by VARCHAR(180) NOT NULL,
                    expires_at VARCHAR(40),
                    used_by VARCHAR(180),
                    created_at VARCHAR(40) NOT NULL
                )
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS message_receipts (
                    message_id VARCHAR(64) NOT NULL,
                    user_id VARCHAR(180) NOT NULL,
                    read_at VARCHAR(40) NOT NULL,
                    PRIMARY KEY (message_id, user_id)
                )
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS notification_reads (
                    notification_id VARCHAR(64) NOT NULL,
                    user_id VARCHAR(180) NOT NULL,
                    read_at VARCHAR(40) NOT NULL,
                    PRIMARY KEY (notification_id, user_id)
                )
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS capsules_members (
                    capsule_id VARCHAR(64) NOT NULL,
                    user_id VARCHAR(180) NOT NULL,
                    approved INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (capsule_id, user_id)
                )
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS blocked_users (
                    user_id VARCHAR(180) NOT NULL,
                    target_id VARCHAR(180) NOT NULL,
                    created_at VARCHAR(40) NOT NULL,
                    PRIMARY KEY (user_id, target_id)
                )
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS plan_location_consents (
                    plan_id VARCHAR(36) PRIMARY KEY,
                    user_id VARCHAR(180) NOT NULL,
                    approved INTEGER NOT NULL DEFAULT 0,
                    updated_at VARCHAR(40) NOT NULL
                )
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS admin_feature_flags (
                    name VARCHAR(80) PRIMARY KEY,
                    enabled INTEGER NOT NULL DEFAULT 0,
                    updated_at VARCHAR(40) NOT NULL,
                    updated_by VARCHAR(180) NOT NULL DEFAULT 'system'
                )
            """))
            # Keep the existing contract fixture available from the canonical
            # store; it is a locked sample room, not an application fallback.
            ignore = "INSERT IGNORE" if conn.dialect.name == "mysql" else "INSERT OR IGNORE"
            conn.execute(text(f"{ignore} INTO users(id,email) VALUES ('demo-user','demo@shuffl.local')"))
            conn.execute(text(f"{ignore} INTO plans(id,user_id,style,chemistry,status,metadata_json) VALUES ('plan-demo','demo-user','Open Night','{{}}','locked',:metadata)"), {"metadata": self._json({"id": "plan-demo", "user_id": "demo-user", "venue_types": [], "stops": 1, "locked": True})})
            conn.execute(text(f"{ignore} INTO rooms(id,host_id,title,visibility,status,metadata_json) VALUES ('room-demo','demo-user','Friday night, open to the city','public','hosted',:metadata)"), {"metadata": self._json({"id": "room-demo", "owner_id": "demo-user", "plan_id": "plan-demo", "chemistry": {}})})
            conn.execute(text(f"{ignore} INTO room_members(room_id,user_id,role,joined_at) VALUES ('room-demo','demo-user','host',:now)"), {"now": self._now().isoformat()})

    @staticmethod
    def _json(value: Any) -> str:
        return json.dumps(value, ensure_ascii=False, default=str)

    def profile_get(self, user_id: str) -> dict[str, Any]:
        self.ensure_user(user_id)
        with self.engine.connect() as conn:
            row = conn.execute(text("SELECT display_name,city,pronouns,bio,preferences FROM profiles WHERE user_id=:id"), {"id": user_id}).mappings().first()
        if not row:
            return {"name": "", "city": "New Delhi", "pronouns": "", "bio": "", "preferences": {}}
        preferences = row.get("preferences") or {}
        if isinstance(preferences, str):
            try: preferences = json.loads(preferences)
            except ValueError: preferences = {}
        return {"name": row.get("display_name") or "", "city": row.get("city") or "New Delhi", "pronouns": row.get("pronouns") or "", "bio": row.get("bio") or "", "preferences": preferences}

    def profile_update(self, user_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        self.ensure_user(user_id, name=payload.get("name", ""))
        with self.engine.begin() as conn:
            conn.execute(text("""UPDATE profiles SET display_name=:name, city=:city, pronouns=:pronouns, bio=:bio, preferences=:preferences WHERE user_id=:id"""), {"id": user_id, "name": payload.get("name", ""), "city": payload.get("city", "New Delhi"), "pronouns": payload.get("pronouns", ""), "bio": payload.get("bio", ""), "preferences": self._json(payload.get("preferences", {}))})
        return self.profile_get(user_id)

    def profile_delete(self, user_id: str) -> None:
        with self.engine.begin() as conn:
            for table, column in (("profiles", "user_id"), ("assessment_sessions", "user_id"), ("notifications", "user_id"), ("privacy_settings", "user_id"), ("blocked_users", "user_id"), ("blocked_users", "target_id")):
                try: conn.execute(text(f"DELETE FROM {table} WHERE {column}=:id"), {"id": user_id})
                except Exception: pass

    def privacy_get(self, user_id: str) -> dict[str, Any]:
        self.ensure_user(user_id)
        with self.engine.connect() as conn:
            row = conn.execute(text("SELECT location_sharing,approximate_presence,discoverability,visibility_json FROM privacy_settings WHERE user_id=:id"), {"id": user_id}).mappings().first()
        visibility = {}
        if row and row.get("visibility_json"):
            try: visibility = json.loads(row["visibility_json"]) if isinstance(row["visibility_json"], str) else row["visibility_json"]
            except ValueError: visibility = {}
        return {"location_sharing": bool(row["location_sharing"]) if row else False, "approximate_presence": bool(row["approximate_presence"]) if row else True, "discoverability": bool(row["discoverability"]) if row else True, "visibility": visibility}

    def privacy_update(self, user_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        self.ensure_user(user_id)
        with self.engine.begin() as conn:
            params = {"id": user_id, "location": int(payload["location_sharing"]), "presence": int(payload["approximate_presence"]), "discoverability": int(payload["discoverability"]), "visibility": self._json(payload.get("visibility", {}))}
            exists = conn.execute(text("SELECT 1 FROM privacy_settings WHERE user_id=:id"), {"id": user_id}).first()
            if exists:
                conn.execute(text("UPDATE privacy_settings SET location_sharing=:location,approximate_presence=:presence,discoverability=:discoverability,visibility_json=:visibility WHERE user_id=:id"), params)
            else:
                conn.execute(text("INSERT INTO privacy_settings(user_id,location_sharing,approximate_presence,discoverability,visibility_json) VALUES (:id,:location,:presence,:discoverability,:visibility)"), params)
        return {**payload, "visibility": payload.get("visibility", {})}

    def add_assessment(self, user_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        self.ensure_user(user_id)
        record_id = str(uuid4()); now = self._now(); now_text = now.isoformat()
        with self.engine.begin() as conn:
            conn.execute(text("INSERT INTO assessment_sessions(id,user_id,scores_raw,scores_rescaled,vibe_name,status,created_at) VALUES (:id,:user,:raw,:rescaled,:vibe,'completed',:created)"), {"id": record_id, "user": user_id, "raw": self._json(payload.get("scores", {})), "rescaled": self._json(payload.get("scores", {})), "vibe": payload.get("vibe_name", ""), "created": now_text})
        return {"id": record_id, "user_id": user_id, **payload, "completed_at": now_text}

    def latest_assessment(self, user_id: str) -> dict[str, Any] | None:
        with self.engine.connect() as conn:
            row = conn.execute(text("SELECT * FROM assessment_sessions WHERE user_id=:id ORDER BY created_at DESC LIMIT 1"), {"id": user_id}).mappings().first()
        if not row: return None
        scores = row.get("scores_raw") or {}
        if isinstance(scores, str):
            try: scores = json.loads(scores)
            except ValueError: scores = {}
        return {"id": row["id"], "user_id": user_id, "scores": scores, "vibe_name": row.get("vibe_name") or "", "completed_at": row.get("created_at")}

    def add_skeleton(self, user_id: str, payload: dict[str, Any], durations: list[float]) -> dict[str, Any]:
        self.ensure_user(user_id); skeleton_id = str(uuid4()); now = self._now(); now_text = now.isoformat()
        metadata = {**payload, "stop_durations": durations}
        with self.engine.begin() as conn:
            conn.execute(text("INSERT INTO plans(id,user_id,style,chemistry,status,metadata_json) VALUES (:id,:user,:style,:chemistry,'skeleton',:metadata)"), {"id": skeleton_id, "user": user_id, "style": "Skeleton", "chemistry": self._json(payload.get("scores", {})), "metadata": self._json(metadata)})
        return {"id": skeleton_id, "user_id": user_id, **metadata, "created_at": now_text}

    def latest_skeleton(self, user_id: str) -> dict[str, Any] | None:
        with self.engine.connect() as conn:
            row = conn.execute(text("SELECT * FROM plans WHERE user_id=:id AND status='skeleton' ORDER BY id DESC LIMIT 1"), {"id": user_id}).mappings().first()
        if not row: return None
        metadata = row.get("metadata_json") or "{}"
        try: metadata = json.loads(metadata) if isinstance(metadata, str) else metadata
        except ValueError: metadata = {}
        return {"id": row["id"], "user_id": user_id, **metadata, "created_at": row.get("created_at")}

    def location_consent(self, plan_id: str, user_id: str, approved: bool | None = None) -> bool:
        if approved is not None:
            with self.engine.begin() as conn:
                params = {"plan": plan_id, "user": user_id, "approved": int(approved), "now": self._now().isoformat()}
                if conn.execute(text("SELECT 1 FROM plan_location_consents WHERE plan_id=:plan"), {"plan": plan_id}).first():
                    conn.execute(text("UPDATE plan_location_consents SET user_id=:user,approved=:approved,updated_at=:now WHERE plan_id=:plan"), params)
                else:
                    conn.execute(text("INSERT INTO plan_location_consents(plan_id,user_id,approved,updated_at) VALUES (:plan,:user,:approved,:now)"), params)
        with self.engine.connect() as conn:
            row = conn.execute(text("SELECT approved FROM plan_location_consents WHERE plan_id=:plan AND user_id=:user"), {"plan": plan_id, "user": user_id}).scalar()
        return bool(row)

    def block_user(self, user_id: str, target_id: str) -> None:
        with self.engine.begin() as conn:
            if not conn.execute(text("SELECT 1 FROM blocked_users WHERE user_id=:user AND target_id=:target"), {"user": user_id, "target": target_id}).first():
                conn.execute(text("INSERT INTO blocked_users(user_id,target_id,created_at) VALUES (:user,:target,:now)"), {"user": user_id, "target": target_id, "now": self._now().isoformat()})

    def unblock_user(self, user_id: str, target_id: str) -> None:
        with self.engine.begin() as conn:
            conn.execute(text("DELETE FROM blocked_users WHERE user_id=:user AND target_id=:target"), {"user": user_id, "target": target_id})

    def blocked_users(self, user_id: str) -> list[str]:
        with self.engine.connect() as conn:
            return [str(row[0]) for row in conn.execute(text("SELECT target_id FROM blocked_users WHERE user_id=:user ORDER BY target_id"), {"user": user_id}).all()]

    def feature_flags(self) -> dict[str, bool]:
        with self.engine.connect() as conn:
            rows = conn.execute(text("SELECT name,enabled FROM admin_feature_flags ORDER BY name")).all()
        flags = {str(row[0]): bool(row[1]) for row in rows}
        return flags or {"capsules": True, "heatmap": True, "live_chat": False}

    def set_feature_flag(self, name: str, enabled: bool, actor: str = "system") -> dict[str, bool]:
        with self.engine.begin() as conn:
            params = {"name": name, "enabled": int(enabled), "now": self._now().isoformat(), "actor": actor}
            if conn.execute(text("SELECT 1 FROM admin_feature_flags WHERE name=:name"), {"name": name}).first():
                conn.execute(text("UPDATE admin_feature_flags SET enabled=:enabled,updated_at=:now,updated_by=:actor WHERE name=:name"), params)
            else:
                conn.execute(text("INSERT INTO admin_feature_flags(name,enabled,updated_at,updated_by) VALUES (:name,:enabled,:now,:actor)"), params)
        return self.feature_flags()

    def _json_obj(self, raw: Any) -> dict[str, Any]:
        if isinstance(raw, dict):
            return raw
        try:
            return json.loads(raw or "{}")
        except (TypeError, ValueError):
            return {}

    def create_plan(self, plan: dict[str, Any]) -> dict[str, Any]:
        self.ensure_user(plan["user_id"])
        with self.engine.begin() as conn:
            conn.execute(text("""INSERT INTO plans
                (id,user_id,style,chemistry,status,metadata_json)
                VALUES (:id,:user,:style,:chemistry,:status,:metadata)"""), {
                "id": plan["id"], "user": plan["user_id"], "style": plan.get("style", plan.get("title", "")),
                "chemistry": self._json(plan.get("chemistry", {})), "status": plan.get("status", "draft"),
                "metadata": self._json(plan),
            })
            for stop in plan.get("selected_stops", []):
                conn.execute(text("""INSERT INTO plan_stops
                    (id,plan_id,stop_index,venue_id,venue_type,duration_share,arrival_window)
                    VALUES (:id,:plan,:idx,:venue,:venue_type,:duration,:arrival)"""), {
                    "id": uuid4().hex, "plan": plan["id"], "idx": int(stop.get("stop_index", 0)),
                    "venue": stop.get("venue_id"), "duration": int(float(plan.get("duration_hours", 1)) * 60 / max(1, len(plan.get("selected_stops", [])))),
                    "venue_type": stop.get("name", "venue"), "arrival": self._json({"name": stop.get("name", ""), "area": stop.get("area", "")}),
                })
        return plan

    def get_plan(self, plan_id: str) -> dict[str, Any] | None:
        with self.engine.connect() as conn:
            row = conn.execute(text("SELECT * FROM plans WHERE id=:id"), {"id": plan_id}).mappings().first()
            if not row:
                return None
            stops = conn.execute(text("SELECT * FROM plan_stops WHERE plan_id=:id ORDER BY stop_index"), {"id": plan_id}).mappings().all()
        plan = self._json_obj(row.get("metadata_json"))
        plan.update({"id": row["id"], "user_id": row["user_id"], "style": row.get("style") or plan.get("style", ""), "status": row.get("status") or plan.get("status", "draft"), "locked": (row.get("status") == "locked") or bool(plan.get("locked"))})
        selected = []
        for stop in stops:
            meta = self._json_obj(stop.get("arrival_window"))
            selected.append({"venue_id": stop.get("venue_id"), "name": meta.get("name", ""), "area": meta.get("area", ""), "stop_index": int(stop.get("stop_index", 0))})
        if selected:
            plan["selected_stops"] = selected
            plan["stops"] = [f"{item['name']} · {item['area']}" for item in selected]
        return plan

    def update_plan_stops(self, plan_id: str, stops: list[dict[str, Any]]) -> dict[str, Any] | None:
        with self.engine.begin() as conn:
            row = conn.execute(text("SELECT status,metadata_json FROM plans WHERE id=:id"), {"id": plan_id}).mappings().first()
            if not row:
                return None
            if row.get("status") == "locked":
                raise ValueError("Locked plans cannot change stops")
            conn.execute(text("DELETE FROM plan_stops WHERE plan_id=:id"), {"id": plan_id})
            for stop in stops:
                conn.execute(text("""INSERT INTO plan_stops
                    (id,plan_id,stop_index,venue_id,venue_type,duration_share,arrival_window)
                    VALUES (:id,:plan,:idx,:venue,:venue_type,:duration,:arrival)"""), {
                    "id": uuid4().hex, "plan": plan_id, "idx": int(stop["stop_index"]), "venue": stop.get("venue_id"),
                    "venue_type": stop.get("name", "venue"), "duration": 60, "arrival": self._json({"name": stop.get("name", ""), "area": stop.get("area", "")}),
                })
            metadata = self._json_obj(row.get("metadata_json")); metadata["selected_stops"] = stops; metadata["locked"] = False
            conn.execute(text("UPDATE plans SET metadata_json=:metadata,status='draft' WHERE id=:id"), {"id": plan_id, "metadata": self._json(metadata)})
        return self.get_plan(plan_id)

    def lock_plan(self, plan_id: str) -> dict[str, Any] | None:
        with self.engine.begin() as conn:
            row = conn.execute(text("SELECT metadata_json FROM plans WHERE id=:id"), {"id": plan_id}).mappings().first()
            if not row:
                return None
            metadata = self._json_obj(row.get("metadata_json")); metadata["locked"] = True; metadata["status"] = "locked"
            conn.execute(text("UPDATE plans SET status='locked',metadata_json=:metadata WHERE id=:id"), {"id": plan_id, "metadata": self._json(metadata)})
        return self.get_plan(plan_id)

    def create_room(self, room: dict[str, Any]) -> dict[str, Any]:
        self.ensure_user(room["owner_id"])
        members = list(dict.fromkeys([room["owner_id"], *room.get("member_ids", room.get("members", []))]))
        with self.engine.begin() as conn:
            conn.execute(text("""INSERT INTO rooms(id,host_id,title,visibility,status,metadata_json)
                VALUES (:id,:host,:title,:visibility,:status,:metadata)"""), {
                "id": room["id"], "host": room["owner_id"], "title": room["title"], "visibility": room["visibility"],
                "status": room.get("status", "draft"), "metadata": self._json(room),
            })
            for member in members:
                self.ensure_user(member)
                conn.execute(text("INSERT INTO room_members(room_id,user_id,role,joined_at) VALUES (:room,:user,:role,:now)"), {"room": room["id"], "user": member, "role": "host" if member == room["owner_id"] else "member", "now": self._now().isoformat()})
        return self.get_room(room["id"])

    def get_room(self, room_id: str) -> dict[str, Any] | None:
        with self.engine.connect() as conn:
            row = conn.execute(text("SELECT * FROM rooms WHERE id=:id"), {"id": room_id}).mappings().first()
            if not row: return None
            members = conn.execute(text("SELECT user_id FROM room_members WHERE room_id=:id ORDER BY joined_at"), {"id": room_id}).all()
            invites = conn.execute(text("SELECT * FROM room_invites WHERE room_id=:id ORDER BY created_at DESC"), {"id": room_id}).mappings().all()
        room = self._json_obj(row.get("metadata_json")); room.update({"id": row["id"], "owner_id": row["host_id"], "title": row["title"], "visibility": row["visibility"], "status": row["status"], "members": [str(item[0]) for item in members], "join_requests": room.get("join_requests", [])})
        if invites: room["invite_token"] = invites[0].get("invite_token")
        return room

    def update_room(self, room_id: str, **changes: Any) -> dict[str, Any] | None:
        with self.engine.begin() as conn:
            row = conn.execute(text("SELECT metadata_json FROM rooms WHERE id=:id"), {"id": room_id}).mappings().first()
            if not row: return None
            metadata = self._json_obj(row.get("metadata_json")); metadata.update(changes)
            fields = {"id": room_id, "metadata": self._json(metadata)}
            conn.execute(text("UPDATE rooms SET title=COALESCE(:title,title),visibility=COALESCE(:visibility,visibility),status=COALESCE(:status,status),metadata_json=:metadata WHERE id=:id"), {**fields, "title": changes.get("title"), "visibility": changes.get("visibility"), "status": changes.get("status")})
        return self.get_room(room_id)

    def add_member(self, room_id: str, user_id: str, role: str = "member") -> dict[str, Any] | None:
        self.ensure_user(user_id)
        with self.engine.begin() as conn:
            if not conn.execute(text("SELECT 1 FROM room_members WHERE room_id=:room AND user_id=:user"), {"room": room_id, "user": user_id}).first():
                conn.execute(text("INSERT INTO room_members(room_id,user_id,role,joined_at) VALUES (:room,:user,:role,:now)"), {"room": room_id, "user": user_id, "role": role, "now": self._now().isoformat()})
        return self.get_room(room_id)

    def create_invite(self, room_id: str, created_by: str, token: str, expires_at: str | None) -> dict[str, Any]:
        invite_id = new_id = uuid4().hex
        with self.engine.begin() as conn:
            conn.execute(text("INSERT INTO room_invites(invite_id,room_id,invite_token,created_by,expires_at,created_at) VALUES (:id,:room,:token,:user,:expires,:now)"), {"id": invite_id, "room": room_id, "token": token, "user": created_by, "expires": expires_at, "now": self._now().isoformat()})
        return {"id": invite_id, "room_id": room_id, "invite_token": token, "expires_at": expires_at}

    def room_for_invite(self, token: str) -> dict[str, Any] | None:
        with self.engine.connect() as conn:
            row = conn.execute(text("SELECT room_id,expires_at,used_by FROM room_invites WHERE invite_token=:token"), {"token": token}).mappings().first()
        if not row or row.get("used_by"): return None
        if row.get("expires_at"):
            try:
                if datetime.fromisoformat(str(row["expires_at"])) <= self._now(): return None
            except ValueError: return None
        return self.get_room(str(row["room_id"]))

    def use_invite(self, token: str, user_id: str) -> dict[str, Any] | None:
        room = self.room_for_invite(token)
        if not room: return None
        with self.engine.begin() as conn:
            conn.execute(text("UPDATE room_invites SET used_by=:user WHERE invite_token=:token AND used_by IS NULL"), {"user": user_id, "token": token})
        return self.add_member(room["id"], user_id)

    def create_capsule(self, capsule: dict[str, Any]) -> dict[str, Any]:
        with self.engine.begin() as conn:
            conn.execute(text("INSERT INTO capsules(id,room_id,status,members) VALUES (:id,:room,:status,:members)"), {"id": capsule["id"], "room": capsule["room_id"], "status": capsule.get("status", "awaiting_approval"), "members": self._json(capsule.get("members", []))})
            for member in capsule.get("members", []):
                conn.execute(text("INSERT INTO capsules_members(capsule_id,user_id,approved) VALUES (:capsule,:user,0)"), {"capsule": capsule["id"], "user": member})
        return self.get_capsule(capsule["id"]) or capsule

    def add_join_request(self, request: dict[str, Any]) -> dict[str, Any]:
        self.ensure_user(request["member_id"])
        with self.engine.begin() as conn:
            conn.execute(text("INSERT INTO join_requests(id,room_id,user_id,status,note) VALUES (:id,:room,:user,:status,:note)"), {"id": request["id"], "room": request["room_id"], "user": request["member_id"], "status": request["status"], "note": request.get("note", "")})
        return request

    def join_requests(self, room_id: str, status: str = "pending") -> list[dict[str, Any]]:
        with self.engine.connect() as conn:
            clause = "room_id=:room" if status == "all" else "room_id=:room AND status=:status"
            params = {"room": room_id, "status": status}
            rows = conn.execute(text(f"SELECT id,room_id,user_id,status,note FROM join_requests WHERE {clause} ORDER BY id"), params).mappings().all()
        return [{"id": row["id"], "room_id": row["room_id"], "member_id": row["user_id"], "status": row["status"], "note": row["note"], "created_at": None} for row in rows]

    def decide_join_request(self, request_id: str, status: str) -> dict[str, Any] | None:
        with self.engine.begin() as conn:
            row = conn.execute(text("SELECT id,room_id,user_id,status,note FROM join_requests WHERE id=:id"), {"id": request_id}).mappings().first()
            if not row: return None
            conn.execute(text("UPDATE join_requests SET status=:status WHERE id=:id"), {"id": request_id, "status": status})
        result = {"id": row["id"], "room_id": row["room_id"], "member_id": row["user_id"], "status": status, "note": row["note"]}
        if status == "accepted": self.add_member(str(row["room_id"]), str(row["user_id"]))
        return result

    def get_capsule(self, capsule_id: str) -> dict[str, Any] | None:
        with self.engine.connect() as conn:
            row = conn.execute(text("SELECT * FROM capsules WHERE id=:id"), {"id": capsule_id}).mappings().first()
            if not row: return None
            members = conn.execute(text("SELECT user_id,approved FROM capsules_members WHERE capsule_id=:id"), {"id": capsule_id}).all()
        values = [str(item[0]) for item in members]
        approvals = {str(item[0]): bool(item[1]) for item in members}
        return {"id": row["id"], "room_id": row["room_id"], "status": row["status"], "members": values, "approvals": approvals}

    def approve_capsule(self, capsule_id: str, user_id: str, approved: bool) -> dict[str, Any] | None:
        with self.engine.begin() as conn:
            result = conn.execute(text("UPDATE capsules_members SET approved=:approved WHERE capsule_id=:capsule AND user_id=:user"), {"approved": int(approved), "capsule": capsule_id, "user": user_id})
            if not result.rowcount: return None
            pending = conn.execute(text("SELECT COUNT(*) FROM capsules_members WHERE capsule_id=:capsule AND approved=0"), {"capsule": capsule_id}).scalar()
            status = "approved" if int(pending or 0) == 0 else "awaiting_approval"
            conn.execute(text("UPDATE capsules SET status=:status WHERE id=:capsule"), {"status": status, "capsule": capsule_id})
        return self.get_capsule(capsule_id)

    def conversation_ids(self, user_id: str) -> list[str]:
        with self.engine.connect() as conn:
            rows = conn.execute(text("SELECT DISTINCT c.id FROM conversations c JOIN messages m ON m.conversation_id=c.id JOIN room_members rm ON rm.room_id=c.room_id WHERE rm.user_id=:user ORDER BY c.id"), {"user": user_id}).all()
        return [str(row[0]) for row in rows] or ["conversation-demo"]

    def conversation_summary(self, conversation_id: str, user_id: str) -> dict[str, Any]:
        messages = self.conversation_messages(conversation_id)
        with self.engine.connect() as conn:
            unread = conn.execute(text("""SELECT COUNT(*) FROM messages m
                WHERE m.conversation_id=:conversation AND m.sender_id<>:user
                AND NOT EXISTS (SELECT 1 FROM message_receipts r WHERE r.message_id=m.id AND r.user_id=:user)"""), {"conversation": conversation_id, "user": user_id}).scalar()
        return {"id": conversation_id, "kind": "group", "title": "Friday Room" if conversation_id == "conversation-demo" else conversation_id, "unread": int(unread or 0), "messages": messages}

    def conversation_messages(self, conversation_id: str) -> list[dict[str, Any]]:
        if not self.available:
            return []
        with self.Session() as session:
            rows = session.scalars(select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.asc())).all()
            return [{"id": row.id, "conversation_id": row.conversation_id, "sender_id": row.sender_id, "body": row.body, "created_at": row.created_at.isoformat() if row.created_at else None, "read": False} for row in rows]

    def add_message(self, *, message_id: str, conversation_id: str, sender_id: str, body: str) -> dict[str, Any]:
        self.ensure_user(sender_id)
        with self.Session.begin() as session:
            conversation = session.get(Conversation, conversation_id)
            if not conversation:
                session.add(Conversation(id=conversation_id, kind="group", title="SHUFFL conversation"))
            row = Message(id=message_id, conversation_id=conversation_id, sender_id=sender_id, body=body)
            session.add(row)
        return {"id": message_id, "conversation_id": conversation_id, "sender_id": sender_id, "body": body, "created_at": self._now().isoformat(), "read": False}

    def mark_conversation_read(self, conversation_id: str, user_id: str) -> int:
        now = self._now().isoformat()
        with self.engine.begin() as conn:
            rows = conn.execute(text("SELECT id FROM messages WHERE conversation_id=:conversation_id AND sender_id<>:user"), {"conversation_id": conversation_id, "user": user_id}).all()
            for row in rows:
                params = {"message": row[0], "user": user_id, "now": now}
                if conn.execute(text("SELECT 1 FROM message_receipts WHERE message_id=:message AND user_id=:user"), params).first():
                    conn.execute(text("UPDATE message_receipts SET read_at=:now WHERE message_id=:message AND user_id=:user"), params)
                else:
                    conn.execute(text("INSERT INTO message_receipts(message_id,user_id,read_at) VALUES (:message,:user,:now)"), params)
        return len(rows)

    def list_notifications(self, user_id: str, unread_only: bool = False) -> list[dict[str, Any]]:
        if not self.available:
            return []
        with self.Session() as session:
            query = select(Notification).where(Notification.user_id == user_id).order_by(Notification.id.desc())
            if unread_only:
                query = query.where(Notification.read.is_(False))
            rows = session.scalars(query).all()
            return [{"id": row.id, "user_id": row.user_id, "kind": row.kind, **(row.payload or {}), "read": bool(row.read)} for row in rows]

    def add_notification(self, *, notification_id: str, user_id: str, kind: str, payload: dict[str, Any]) -> dict[str, Any]:
        self.ensure_user(user_id)
        with self.Session.begin() as session:
            session.add(Notification(id=notification_id, user_id=user_id, kind=kind, payload=payload, read=False))
        return {"id": notification_id, "user_id": user_id, "kind": kind, **payload, "read": False}

    def mark_notification_read(self, notification_id: str, user_id: str) -> bool:
        with self.Session.begin() as session:
            row = session.get(Notification, notification_id)
            if not row or row.user_id != user_id:
                return False
            row.read = True
            with self.engine.begin() as conn:
                params = {"notification": notification_id, "user": user_id, "now": self._now().isoformat()}
                if conn.execute(text("SELECT 1 FROM notification_reads WHERE notification_id=:notification AND user_id=:user"), params).first():
                    conn.execute(text("UPDATE notification_reads SET read_at=:now WHERE notification_id=:notification AND user_id=:user"), params)
                else:
                    conn.execute(text("INSERT INTO notification_reads(notification_id,user_id,read_at) VALUES (:notification,:user,:now)"), params)
            return True

    def add_report(self, *, report_id: str, reporter_id: str, target_id: str, reason: str) -> dict[str, Any]:
        self.ensure_user(reporter_id)
        with self.Session.begin() as session:
            session.add(Report(id=report_id, reporter_id=reporter_id, target_id=target_id, reason=reason, status="received"))
        return {"id": report_id, "reporter_id": reporter_id, "target_id": target_id, "reason": reason, "status": "received", "created_at": self._now().isoformat()}

    def list_reports(self, status: str | None = None) -> list[dict[str, Any]]:
        with self.Session() as session:
            query = select(Report).order_by(Report.id.desc())
            if status:
                query = query.where(Report.status == status)
            rows = session.scalars(query).all()
            return [{"id": row.id, "reporter_id": row.reporter_id, "target_id": row.target_id, "reason": row.reason, "status": row.status} for row in rows]

    def update_report(self, report_id: str, status: str) -> bool:
        with self.Session.begin() as session:
            row = session.get(Report, report_id)
            if not row:
                return False
            row.status = status
            return True


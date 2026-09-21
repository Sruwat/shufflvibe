from datetime import datetime, timezone
from typing import Any
from fastapi import FastAPI
from pydantic import BaseModel, Field
from .full_engine import chemistry_v2, select_venue_types

app = FastAPI(title="SHUFFL API", version="0.1.0")

class Answer(BaseModel):
    card_id: str
    action: str
    score: int = Field(ge=0, le=100)

class PlanRequest(BaseModel):
    scores: dict[str, float]
    members: list[str] = []

class RoomRequest(BaseModel):
    title: str
    member_ids: list[str] = []
    visibility: str = "friends"

class JoinRequest(BaseModel):
    room_id: str
    note: str = ""

class CapsuleRequest(BaseModel):
    room_id: str
    member_ids: list[str] = []

class MessageRequest(BaseModel):
    conversation_id: str
    body: str

class ReportRequest(BaseModel):
    target_id: str
    reason: str

class PrivacyUpdate(BaseModel):
    location_sharing: bool = False
    approximate_presence: bool = True
    discoverability: bool = True

class FeatureFlagUpdate(BaseModel):
    name: str
    enabled: bool

_rooms: list[dict[str, Any]] = [{"id": "room-demo", "title": "Friday night, open to the city", "members": ["demo-user"], "visibility": "friends"}]
_notifications: list[dict[str, Any]] = [{"id": "n-1", "kind": "room_request", "title": "A room is forming", "read": False}]
_flags: dict[str, bool] = {"capsules": True, "heatmap": True, "live_chat": False}

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "shuffl-api"}

@app.post("/v1/sessions")
def create_session() -> dict[str, Any]:
    return {"id": "demo-session", "mode": "demo", "created_at": datetime.now(timezone.utc).isoformat()}

@app.get("/v1/profiles/me")
def profile() -> dict[str, Any]:
    return {"name": "Aarav Mehta", "city": "New Delhi", "preferences": {"FOOD": 88, "SCEN": 88, "NOV": 62}}

@app.post("/v1/assessment/answers")
def answer(payload: Answer) -> dict[str, Any]:
    return {"accepted": True, "card_id": payload.card_id, "score": payload.score}

@app.post("/v1/plans/generate")
def generate_plan(payload: PlanRequest) -> dict[str, Any]:
    energy = payload.scores.get("ENRG", 62)
    members = [payload.scores] if not payload.members else [payload.scores for _ in payload.members]
    chemistry = chemistry_v2(members)
    return {"style": "Could Go Late" if energy >= 70 else "Settle Then Roam", "stops": chemistry["stops"], "chemistry": chemistry, "venue_types": select_venue_types(members), "venues": ["Sidecar, GK-2", "Majnu ka Tila Lane", "Sunder Nursery"][:chemistry["stops"]]}

@app.post("/v1/plans/{plan_id}/lock")
def lock_plan(plan_id: str) -> dict[str, Any]:
    return {"id": plan_id, "status": "locked"}

@app.get("/v1/discovery")
def discovery() -> dict[str, Any]:
    return {"items": [{"name": "Sidecar, GK-2", "type": "pub", "area": "Greater Kailash II"}, {"name": "Sunder Nursery", "type": "open ground", "area": "Nizamuddin"}]}

@app.get("/v1/venues")
def venues(query: str = "", city: str = "New Delhi") -> dict[str, Any]:
    items = discovery()["items"]
    if query:
        items = [item for item in items if query.lower() in item["name"].lower()]
    return {"city": city, "items": items}

@app.get("/v1/search")
def search(q: str, kind: str = "all") -> dict[str, Any]:
    return {"query": q, "kind": kind, "items": venues(q)["items"]}

@app.post("/v1/rooms")
def create_room(payload: RoomRequest) -> dict[str, Any]:
    room = {"id": f"room-{len(_rooms)+1}", "title": payload.title, "members": payload.member_ids, "visibility": payload.visibility, "status": "draft"}
    _rooms.append(room)
    return room

@app.get("/v1/rooms")
def rooms() -> dict[str, Any]:
    return {"items": _rooms}

@app.post("/v1/rooms/join-requests")
def join_room(payload: JoinRequest) -> dict[str, Any]:
    return {"id": "join-demo", "room_id": payload.room_id, "status": "pending", "note": payload.note}

@app.post("/v1/capsules")
def create_capsule(payload: CapsuleRequest) -> dict[str, Any]:
    return {"id": "capsule-demo", "room_id": payload.room_id, "members": payload.member_ids, "status": "awaiting_approval"}

@app.get("/v1/conversations")
def conversations() -> dict[str, Any]:
    return {"items": [{"id": "conversation-demo", "kind": "group", "title": "Friday room", "unread": 2}]}

@app.post("/v1/conversations/messages")
def send_message(payload: MessageRequest) -> dict[str, Any]:
    return {"id": "message-demo", "conversation_id": payload.conversation_id, "body": payload.body, "status": "sent"}

@app.get("/v1/notifications")
def notifications() -> dict[str, Any]:
    return {"items": _notifications}

@app.post("/v1/reports")
def report(payload: ReportRequest) -> dict[str, Any]:
    return {"id": "report-demo", "target_id": payload.target_id, "reason": payload.reason, "status": "received"}

@app.post("/v1/privacy")
def update_privacy(payload: PrivacyUpdate) -> dict[str, Any]:
    return {"saved": True, "settings": payload.model_dump()}

@app.get("/v1/feature-flags")
def feature_flags() -> dict[str, bool]:
    return _flags

@app.post("/v1/feature-flags")
def update_feature_flag(payload: FeatureFlagUpdate) -> dict[str, bool]:
    _flags[payload.name] = payload.enabled
    return _flags

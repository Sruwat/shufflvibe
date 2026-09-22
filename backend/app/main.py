from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .full_engine import DEMO_VENUES, chemistry_v2, fill_venues, select_venue_types

app = FastAPI(title="SHUFFL API", version="0.2.0")


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:12]}"


class Answer(BaseModel):
    card_id: str
    action: str
    score: int = Field(ge=0, le=100)


class PlanRequest(BaseModel):
    scores: dict[str, float]
    members: list[str] = Field(default_factory=list)
    member_scores: list[dict[str, float]] = Field(default_factory=list)
    preferences: dict[str, float] = Field(default_factory=dict)
    pol_sense: str = "both"
    duration_hours: float = Field(default=4, gt=0, le=16)
    strangers: bool = False


class RoomRequest(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    member_ids: list[str] = Field(default_factory=list)
    visibility: str = "friends"


class RoomUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=160)
    visibility: str | None = None


class JoinRequest(BaseModel):
    room_id: str
    note: str = ""


class JoinDecision(BaseModel):
    status: str


class CapsuleRequest(BaseModel):
    room_id: str
    member_ids: list[str] = Field(default_factory=list)


class CapsuleApproval(BaseModel):
    member_id: str
    approved: bool


class MessageRequest(BaseModel):
    conversation_id: str
    body: str = Field(min_length=1, max_length=4000)


class ReportRequest(BaseModel):
    target_id: str
    reason: str = Field(min_length=1, max_length=2000)


class PrivacyUpdate(BaseModel):
    location_sharing: bool = False
    approximate_presence: bool = True
    discoverability: bool = True
    visibility: dict[str, str] = Field(default_factory=dict)


class PlanLocationConsent(BaseModel):
    approved: bool


class FeatureFlagUpdate(BaseModel):
    name: str
    enabled: bool


_rooms: list[dict[str, Any]] = [{"id": "room-demo", "title": "Friday night, open to the city", "members": ["demo-user"], "visibility": "friends", "status": "hosted", "plan_id": "plan-demo", "chemistry": {}, "join_requests": []}]
_plans: dict[str, dict[str, Any]] = {}
_capsules: dict[str, dict[str, Any]] = {}
_messages: list[dict[str, Any]] = []
_reports: list[dict[str, Any]] = []
_privacy: dict[str, dict[str, Any]] = {}
_plan_location_consents: dict[str, bool] = {}
_notifications: list[dict[str, Any]] = [{"id": "n-1", "kind": "room_request", "title": "A room is forming", "read": False}]
_flags: dict[str, bool] = {"capsules": True, "heatmap": True, "live_chat": False}
_answers: list[dict[str, Any]] = []


def find_room(room_id: str) -> dict[str, Any]:
    room = next((item for item in _rooms if item["id"] == room_id), None)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "shuffl-api"}


@app.post("/v1/sessions")
def create_session() -> dict[str, Any]:
    return {"id": new_id("session"), "mode": "demo", "created_at": datetime.now(timezone.utc).isoformat()}


@app.get("/v1/profiles/me")
def profile() -> dict[str, Any]:
    return {"name": "Aarav Mehta", "city": "New Delhi", "preferences": {"FOOD": 88, "SCEN": 88, "NOV": 62}}


@app.post("/v1/assessment/answers")
def answer(payload: Answer) -> dict[str, Any]:
    record = {"id": new_id("answer"), **payload.model_dump(), "created_at": datetime.now(timezone.utc).isoformat()}
    _answers.append(record)
    return {"accepted": True, **record}


@app.post("/v1/plans/generate")
def generate_plan(payload: PlanRequest) -> dict[str, Any]:
    members = payload.member_scores or [payload.scores]
    chemistry = chemistry_v2(members, payload.duration_hours, payload.strangers)
    venue_types = select_venue_types(members, payload.duration_hours, payload.strangers)
    venue_preferences = [{"preferences": payload.preferences, "pol_sense": payload.pol_sense}]
    venues = fill_venues(venue_types, venue_preferences, DEMO_VENUES)
    plan = {"id": new_id("plan"), "style": "Could Go Late" if chemistry["vector"].get("ENRG", 50) >= 70 else "Settle Then Roam", "stops": chemistry["stops"], "chemistry": chemistry, "venue_types": venue_types, "venues": venues, "member_ids": payload.members, "status": "draft", "locked": False, "created_at": datetime.now(timezone.utc).isoformat()}
    _plans[plan["id"]] = plan
    return plan


@app.post("/v1/plans/{plan_id}/lock")
def lock_plan(plan_id: str) -> dict[str, Any]:
    plan = _plans.get(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    plan["status"] = "locked"
    plan["locked"] = True
    return plan


@app.get("/v1/discovery")
def discovery() -> dict[str, Any]:
    return {"items": [{"name": venue["name"], "type": venue["type"], "area": venue["area"]} for venue in DEMO_VENUES]}


@app.get("/v1/venues")
def venues(query: str = "", city: str = "New Delhi") -> dict[str, Any]:
    items = discovery()["items"]
    if query:
        items = [item for item in items if query.lower() in item["name"].lower() or query.lower() in item["type"].lower() or query.lower() in item["area"].lower()]
    return {"city": city, "items": items}


@app.get("/v1/search")
def search(q: str, kind: str = "all") -> dict[str, Any]:
    items = venues(q)["items"]
    if kind == "rooms":
        items = [room for room in _rooms if q.lower() in room["title"].lower()]
    return {"query": q, "kind": kind, "items": items}


@app.post("/v1/rooms")
def create_room(payload: RoomRequest) -> dict[str, Any]:
    if payload.visibility not in {"private", "friends", "public"}:
        raise HTTPException(status_code=422, detail="visibility must be private, friends, or public")
    room = {"id": new_id("room"), "title": payload.title.strip(), "members": list(dict.fromkeys(payload.member_ids)), "visibility": payload.visibility, "status": "draft", "plan_id": None, "chemistry": {}, "join_requests": []}
    _rooms.append(room)
    return room


@app.get("/v1/rooms")
def rooms(status: str | None = None, visibility: str | None = None) -> dict[str, Any]:
    items = _rooms
    if status:
        items = [room for room in items if room["status"] == status]
    if visibility:
        items = [room for room in items if room["visibility"] == visibility]
    return {"items": items}


@app.patch("/v1/rooms/{room_id}")
def update_room(room_id: str, payload: RoomUpdate) -> dict[str, Any]:
    room = find_room(room_id)
    if room["status"] == "hosted" and payload.title is not None:
        room["title"] = payload.title
    elif room["status"] != "hosted" and payload.title is not None:
        room["title"] = payload.title
    if payload.visibility is not None:
        if payload.visibility not in {"private", "friends", "public"}:
            raise HTTPException(status_code=422, detail="invalid visibility")
        if room["status"] == "hosted":
            raise HTTPException(status_code=409, detail="Visibility is frozen after hosting")
        room["visibility"] = payload.visibility
    return room


@app.post("/v1/rooms/{room_id}/host")
def host_room(room_id: str, plan_id: str) -> dict[str, Any]:
    room = find_room(room_id)
    plan = _plans.get(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    if room["status"] == "hosted":
        raise HTTPException(status_code=409, detail="Room is already hosted")
    plan["locked"] = True
    plan["status"] = "locked"
    room["plan_id"] = plan_id
    room["visibility"] = "public"
    room["status"] = "hosted"
    room["chemistry"] = plan["chemistry"]
    return room


@app.post("/v1/rooms/join-requests")
def join_room(payload: JoinRequest) -> dict[str, Any]:
    room = find_room(payload.room_id)
    if room["status"] != "hosted":
        raise HTTPException(status_code=409, detail="Room is not accepting requests")
    request = {"id": new_id("join"), "room_id": payload.room_id, "status": "pending", "note": payload.note, "created_at": datetime.now(timezone.utc).isoformat()}
    room["join_requests"].append(request)
    return request


@app.post("/v1/rooms/{room_id}/join-requests/{request_id}/decision")
def decide_join(room_id: str, request_id: str, payload: JoinDecision) -> dict[str, Any]:
    room = find_room(room_id)
    if payload.status not in {"accepted", "declined"}:
        raise HTTPException(status_code=422, detail="status must be accepted or declined")
    request = next((item for item in room["join_requests"] if item["id"] == request_id), None)
    if request is None:
        raise HTTPException(status_code=404, detail="Join request not found")
    if request["status"] != "pending":
        raise HTTPException(status_code=409, detail="Join request already resolved")
    request["status"] = payload.status
    if payload.status == "accepted":
        room["members"].append(request_id)
    return {"request": request, "room": room, "plan_frozen": True}


@app.post("/v1/capsules")
def create_capsule(payload: CapsuleRequest) -> dict[str, Any]:
    find_room(payload.room_id)
    if not _flags.get("capsules", False):
        raise HTTPException(status_code=403, detail="Capsules are disabled")
    capsule = {"id": new_id("capsule"), "room_id": payload.room_id, "members": list(dict.fromkeys(payload.member_ids)), "approvals": {member_id: False for member_id in payload.member_ids}, "status": "awaiting_approval", "created_at": datetime.now(timezone.utc).isoformat()}
    _capsules[capsule["id"]] = capsule
    return capsule


@app.post("/v1/capsules/{capsule_id}/approvals")
def approve_capsule(capsule_id: str, payload: CapsuleApproval) -> dict[str, Any]:
    capsule = _capsules.get(capsule_id)
    if capsule is None:
        raise HTTPException(status_code=404, detail="Capsule not found")
    if payload.member_id not in capsule["approvals"]:
        raise HTTPException(status_code=404, detail="Member is not in this capsule")
    capsule["approvals"][payload.member_id] = payload.approved
    capsule["status"] = "approved" if capsule["approvals"] and all(capsule["approvals"].values()) else "awaiting_approval"
    return capsule


@app.get("/v1/conversations")
def conversations() -> dict[str, Any]:
    return {"items": [{"id": "conversation-demo", "kind": "group", "title": "Friday room", "unread": 2, "messages": [message for message in _messages if message["conversation_id"] == "conversation-demo"]}]}


@app.post("/v1/conversations/messages")
def send_message(payload: MessageRequest) -> dict[str, Any]:
    message = {"id": new_id("message"), "conversation_id": payload.conversation_id, "body": payload.body, "status": "sent", "created_at": datetime.now(timezone.utc).isoformat()}
    _messages.append(message)
    return message


@app.get("/v1/notifications")
def notifications(unread_only: bool = False) -> dict[str, Any]:
    items = [item for item in _notifications if not unread_only or not item["read"]]
    return {"items": items}


@app.post("/v1/notifications/{notification_id}/read")
def mark_notification_read(notification_id: str) -> dict[str, Any]:
    notification = next((item for item in _notifications if item["id"] == notification_id), None)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification["read"] = True
    return notification


@app.post("/v1/reports")
def report(payload: ReportRequest) -> dict[str, Any]:
    record = {"id": new_id("report"), "target_id": payload.target_id, "reason": payload.reason, "status": "received", "created_at": datetime.now(timezone.utc).isoformat()}
    _reports.append(record)
    return record


@app.get("/v1/plans/{plan_id}/location-consent")
def get_plan_location_consent(plan_id: str) -> dict[str, bool]:
    if plan_id not in _plans:
        raise HTTPException(status_code=404, detail="Plan not found")
    permitted = _privacy.get("demo-user", PrivacyUpdate().model_dump())["location_sharing"]
    return {"approved": bool(permitted and _plan_location_consents.get(plan_id, False))}


@app.post("/v1/plans/{plan_id}/location-consent")
def set_plan_location_consent(plan_id: str, payload: PlanLocationConsent) -> dict[str, bool]:
    if plan_id not in _plans:
        raise HTTPException(status_code=404, detail="Plan not found")
    permitted = _privacy.get("demo-user", PrivacyUpdate().model_dump())["location_sharing"]
    if payload.approved and not permitted:
        raise HTTPException(status_code=409, detail="Enable per-plan location sharing in privacy settings first")
    _plan_location_consents[plan_id] = payload.approved
    return {"approved": payload.approved}


@app.post("/v1/privacy")
def update_privacy(payload: PrivacyUpdate) -> dict[str, Any]:
    invalid = {key: value for key, value in payload.visibility.items() if value not in {"everyone", "friends", "nobody"}}
    if invalid:
        raise HTTPException(status_code=422, detail="visibility values must be everyone, friends, or nobody")
    settings = payload.model_dump()
    _privacy["demo-user"] = settings
    if not settings["location_sharing"]:
        _plan_location_consents.clear()
    return {"saved": True, "settings": settings}


@app.get("/v1/privacy")
def get_privacy() -> dict[str, Any]:
    return _privacy.get("demo-user", PrivacyUpdate().model_dump())


@app.get("/v1/feature-flags")
def feature_flags() -> dict[str, bool]:
    return _flags


@app.post("/v1/feature-flags")
def update_feature_flag(payload: FeatureFlagUpdate) -> dict[str, bool]:
    _flags[payload.name] = payload.enabled
    return _flags

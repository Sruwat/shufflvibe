from datetime import datetime, timezone
from contextlib import asynccontextmanager
import asyncio
import logging
import os
import io
import json
import secrets
import hashlib
import hmac
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request
import re
import smtplib
from email.message import EmailMessage
from typing import Any
from uuid import uuid4

from fastapi import BackgroundTasks, Depends, FastAPI, File, Form, Header, HTTPException, Query, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .full_engine import DEMO_VENUES, chemistry_v2, fill_venues, joiner_shape_fit, select_venue_types


def _load_local_env() -> None:
    """Load simple KEY=VALUE settings from backend/.env before store creation.

    This intentionally does not overwrite variables already supplied by the
    process environment, so deployment secrets remain authoritative.
    """
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"").strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_local_env()
from .admin_store import store
from .auth_store import AuthStore
from .domain_store import DomainStore
from .release_scope import release_scope
from .state_store import RuntimeStateStore
from venue_pipeline_backend.venue_pipeline.gemini import GeminiClient, GeminiError
from venue_pipeline_backend.venue_pipeline.google_places import GooglePlacesClient, GooglePlacesError
from venue_pipeline_backend.venue_pipeline.live_google import fetch_for_display
from venue_pipeline_backend.venue_pipeline.scoring import fallback_metadata, score
from .ops import SlidingWindowLimiter, allowed_origins, database_readiness, env_int, validate_startup_config
from .launch_audit import build_launch_audit

@asynccontextmanager
async def app_lifespan(_app: FastAPI):
    """Validate runtime configuration using FastAPI's current lifecycle API."""
    report = validate_startup_config()
    try:
        # Remove legacy display-only Google payloads from older snapshots before
        # the API serves them. Current writes already exclude these fields.
        store.purge_live_google_cache()
    except Exception as exc:  # pragma: no cover - driver-specific startup issue
        _log.warning("google_display_cache_cleanup_failed error=%s", exc)
    for warning in report["warnings"]:
        _log.warning("configuration_warning %s", warning)
    if not report["ok"]:
        message = "; ".join(report["errors"])
        if report["environment"] in {"production", "staging"}:
            raise RuntimeError(f"SHUFFL startup configuration invalid: {message}")
        _log.warning("configuration_error development_mode=%s", message)
    yield


app = FastAPI(title="SHUFFL API", version="0.2.0", lifespan=app_lifespan)
app.mount("/admin", StaticFiles(directory=str(Path(__file__).resolve().parents[2] / "admin_dashboard"), html=True), name="admin-dashboard")
MEDIA_ROOT = Path(__file__).resolve().parents[1] / "data" / "media"
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(MEDIA_ROOT)), name="venue-media")

_log = logging.getLogger("shuffl.api")
_origins = allowed_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=bool(_origins and "*" not in _origins),
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
_public_limiter = SlidingWindowLimiter(env_int("SHUFFL_RATE_LIMIT_PER_MINUTE", 120))
_stop_options_limiter = SlidingWindowLimiter(env_int("SHUFFL_STOP_OPTIONS_RATE_LIMIT_PER_MINUTE", 30))


@app.middleware("http")
async def operational_middleware(request, call_next):
    """Attach request IDs, safe access logs, and abuse protection to every API call."""
    request_id = request.headers.get("X-Request-ID") or uuid4().hex
    path = request.url.path
    if path.startswith("/v1/") and path != "/v1/health/readiness":
        client = request.client.host if request.client else "unknown"
        limiter = _stop_options_limiter if path == "/v1/venues/stop-options" else _public_limiter
        if not limiter.allow(f"{client}:{path.split('/')[2] if len(path.split('/')) > 2 else 'api'}"):
            return JSONResponse(
                {"detail": "Rate limit exceeded. Try again later.", "request_id": request_id},
                status_code=429,
                headers={"Retry-After": "60", "X-Request-ID": request_id},
            )
    session_id = request.headers.get("X-Session-Id", "").strip()
    if session_id:
        # Session records are intentionally lightweight in the MVP, but keeping
        # last_seen_at current makes the handshake observable and gives the
        # future auth layer a safe migration point.
        for session in _session_records:
            if session.get("id") == session_id:
                session["last_seen_at"] = datetime.now(timezone.utc).isoformat()
                break
    started = __import__("time").monotonic()
    try:
        response = await call_next(request)
    except Exception:
        _log.exception("request_failed request_id=%s method=%s path=%s", request_id, request.method, path)
        raise
    response.headers["X-Request-ID"] = request_id
    # Canonical production routes persist through MySQL repositories. The
    # legacy aggregate is intentionally not written on every request anymore;
    # it is retained only for explicit migration/rollback tooling.
    _log.info("request request_id=%s method=%s path=%s status=%s duration_ms=%d", request_id, request.method, path, response.status_code, int((__import__("time").monotonic() - started) * 1000))
    return response


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:12]}"


class Answer(BaseModel):
    card_id: str
    action: str
    score: int = Field(ge=0, le=100)


class SessionRequest(BaseModel):
    """Small client-session handshake used by API-backed mobile builds."""

    client_id: str = Field(default="", max_length=180)


class AuthRegisterRequest(BaseModel):
    email: str = Field(min_length=5, max_length=320)
    password: str = Field(min_length=8, max_length=200)
    name: str = Field(default="", max_length=120)


class AuthLoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=320)
    password: str = Field(min_length=8, max_length=200)


class GoogleAuthRequest(BaseModel):
    id_token: str = Field(min_length=20, max_length=10000)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=20, max_length=500)


class PasswordResetRequest(BaseModel):
    email: str = Field(min_length=5, max_length=320)


class PasswordResetConfirm(BaseModel):
    token: str = Field(min_length=20, max_length=500)
    password: str = Field(min_length=8, max_length=200)


class EmailVerificationRequest(BaseModel):
    token: str = Field(min_length=20, max_length=500)


class AssessmentCompletion(BaseModel):
    scores: dict[str, float] = Field(default_factory=dict)
    vibe_name: str = Field(min_length=1, max_length=120)
    chosen_top: str | None = None
    latency_firmness: dict[str, float] = Field(default_factory=dict)
    actions: dict[str, str] = Field(default_factory=dict)


class SkeletonRequest(BaseModel):
    scores: dict[str, float] = Field(default_factory=dict)
    stops: int = Field(ge=1, le=3)
    energy: float = Field(ge=0, le=100)
    crowd: float = Field(ge=0, le=100)
    tags: list[str] = Field(default_factory=list, max_length=8)
    stop_durations: list[float] = Field(default_factory=list, max_length=3)
    source: str = Field(default="assessment", max_length=40)


class PlanRequest(BaseModel):
    scores: dict[str, float]
    members: list[str] = Field(default_factory=list)
    member_scores: list[dict[str, float]] = Field(default_factory=list)
    preferences: dict[str, float] = Field(default_factory=dict)
    pol_sense: str = "both"
    duration_hours: float = Field(default=4, gt=0, le=16)
    strangers: bool = False


class SelectedPlanStop(BaseModel):
    venue_id: str | None = None
    name: str = Field(min_length=1, max_length=255)
    area: str = Field(default="Delhi NCR", max_length=160)
    stop_index: int = Field(ge=0, le=10)


class SelectedPlanRequest(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    duration_hours: float = Field(gt=0, le=16)
    scores: dict[str, float] = Field(default_factory=dict)
    stops: list[SelectedPlanStop] = Field(min_length=1, max_length=3)
    chemistry: dict[str, Any] = Field(default_factory=dict)


class SelectedPlanStopsUpdate(BaseModel):
    stops: list[SelectedPlanStop] = Field(min_length=1, max_length=3)


class RoomRequest(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    member_ids: list[str] = Field(default_factory=list)
    visibility: str = "friends"


class RoomUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=160)
    visibility: str | None = None


class InviteJoinRequest(BaseModel):
    invite_token: str = Field(min_length=8, max_length=120)


class JoinRequest(BaseModel):
    room_id: str
    member_id: str = Field(default="demo-joiner", min_length=1, max_length=200)
    note: str = Field(default="", max_length=1000)
    scores: dict[str, Any] = Field(default_factory=dict)


class JoinEligibilityRequest(BaseModel):
    room_id: str
    scores: dict[str, Any] = Field(default_factory=dict)


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
    target_id: str = Field(min_length=1, max_length=200)
    reason: str = Field(min_length=1, max_length=2000)


class BlockRequest(BaseModel):
    target_id: str = Field(min_length=1, max_length=200)


class PrivacyUpdate(BaseModel):
    location_sharing: bool = False
    approximate_presence: bool = True
    discoverability: bool = True
    visibility: dict[str, str] = Field(default_factory=dict)


class ProfileUpdate(BaseModel):
    name: str = Field(default="", max_length=120)
    city: str = Field(default="New Delhi", max_length=120)
    pronouns: str = Field(default="", max_length=40)
    bio: str = Field(default="", max_length=500)
    preferences: dict[str, float] = Field(default_factory=dict)


class PlanLocationConsent(BaseModel):
    approved: bool


class FeatureFlagUpdate(BaseModel):
    name: str
    enabled: bool


class AdminVenueUpdate(BaseModel):
    display_name: str | None = None
    city: str | None = None
    state: str | None = None
    area: str | None = None
    official_url: str | None = None
    google_lookup_url: str | None = None
    google_place_id: str | None = None
    discovered_type: str | None = None
    website_url: str | None = None
    menu_url: str | None = None
    booking_url: str | None = None
    social_urls: list[str] | None = None
    metro_name: str | None = None
    metro_distance_km: float | None = None
    photos: list[str] | None = None
    verification_status: str | None = None
    eligibility_status: str | None = None
    operator_class: str | None = None
    fit_out_status: str | None = None
    fit_out_year: int | None = None
    manual_notes: str | None = None
    manual_vibe: str | None = None
    manual_tags: list[str] | None = None
    manual_opening_hours: dict[str, str] | None = None
    manual_time_slots: list[dict[str, Any]] | None = None
    published: bool | None = None
    override_reason: str | None = Field(default=None, max_length=500)


ADMIN_PERMISSIONS: dict[str, set[str]] = {
    "VIEWER": {"admin.read"},
    "EDITOR": {"admin.read", "venue.draft", "media.write"},
    "ADMIN": {"admin.read", "admin.moderate", "venue.draft", "media.write", "venue.publish", "pipeline.run", "database.export"},
    "SUPER_ADMIN": {"admin.read", "admin.moderate", "venue.draft", "media.write", "venue.publish", "pipeline.run", "database.export", "rbac.manage"},
}


def _admin_principal(token: str | None) -> dict[str, str]:
    """Resolve a role from server-side token configuration.

    Tokens are never returned to clients. Production should use a secret manager
    to populate ADMIN_ROLE_TOKENS; the single ADMIN_API_TOKEN remains a
    backwards-compatible SUPER_ADMIN bootstrap token for local development.
    """
    token = (token or "").strip()
    configured_roles: dict[str, str] = {}
    for pair in os.getenv("ADMIN_ROLE_TOKENS", "").split(","):
        if "=" not in pair:
            continue
        role, secret = pair.split("=", 1)
        role, secret = role.strip().upper(), secret.strip()
        if role in ADMIN_PERMISSIONS and secret:
            configured_roles[secret] = role
    bootstrap = os.getenv("ADMIN_API_TOKEN", "").strip()
    if bootstrap:
        configured_roles.setdefault(bootstrap, "SUPER_ADMIN")
    if configured_roles:
        role = next((configured_role for configured_token, configured_role in configured_roles.items() if secrets.compare_digest(configured_token, token)), None)
        if not role:
            raise HTTPException(status_code=401, detail="Admin token required")
        return {"actor": token, "role": role}
    if os.getenv("APP_ENV", "development").lower() in {"production", "staging"}:
        raise HTTPException(status_code=503, detail="Admin authentication is not configured")
    return {"actor": token or "local-admin", "role": "SUPER_ADMIN"}


def require_admin(x_admin_token: str | None = Header(default=None)) -> str:
    return _admin_principal(x_admin_token)["actor"]


def require_admin_photo(
    x_admin_token: str | None = Header(default=None),
    token: str | None = Query(default=None),
) -> str:
    """Authenticate photo tags as well as API calls.

    Browsers cannot attach the admin header to a normal <img> request. The
    dashboard therefore sends its already-configured local admin token as a
    query value for this narrowly scoped image proxy.
    """
    return _admin_principal(x_admin_token or token)["actor"]


def require_admin_permission(permission: str):
    def dependency(x_admin_token: str | None = Header(default=None)) -> str:
        principal = _admin_principal(x_admin_token)
        if permission not in ADMIN_PERMISSIONS[principal["role"]]:
            raise HTTPException(status_code=403, detail=f"Role {principal['role']} cannot perform {permission}")
        return principal["actor"]

    return dependency


_plans: dict[str, dict[str, Any]] = {"plan-demo": {"id": "plan-demo", "status": "locked", "locked": True, "stops": 1, "venue_types": ["table for the night"], "chemistry": {}}}
_rooms: list[dict[str, Any]] = [{"id": "room-demo", "title": "Friday night, open to the city", "members": ["demo-user"], "visibility": "public", "status": "hosted", "plan_id": "plan-demo", "chemistry": {}, "join_requests": []}]
_capsules: dict[str, dict[str, Any]] = {}
_messages: list[dict[str, Any]] = []
_reports: list[dict[str, Any]] = []
_blocked_users: set[str] = set()
_privacy: dict[str, dict[str, Any]] = {}
_plan_location_consents: dict[str, bool] = {}
_notifications: list[dict[str, Any]] = [{"id": "n-1", "kind": "room_request", "title": "A room is forming", "read": False}]
_flags: dict[str, bool] = {"capsules": True, "heatmap": True, "live_chat": False}
_answers: list[dict[str, Any]] = []
_assessment_results: list[dict[str, Any]] = []
_skeletons: list[dict[str, Any]] = []
_runtime_state = RuntimeStateStore(store.engine)
_auth_store = AuthStore(store.engine)
_domain_store = DomainStore(store.engine)
try:
    _domain_store.ensure_domain_schema()
except Exception as exc:
    _domain_store.available = False
    _log.warning("canonical_domain_schema_unavailable error=%s", str(exc)[:240])
_session_records: list[dict[str, Any]] = []
_auth_accounts: dict[str, dict[str, Any]] = {}
_auth_tokens: dict[str, dict[str, Any]] = {}
_profiles: dict[str, dict[str, Any]] = {"demo-user": {"name": "Aarav Mehta", "city": "New Delhi", "pronouns": "", "bio": "", "preferences": {"FOOD": 88, "SCEN": 88, "NOV": 62}}}
_room_sockets: dict[str, set[WebSocket]] = {}


def _restore_runtime_state() -> None:
    """Restore durable app aggregates without restoring fixtures in production."""
    global _plans, _rooms, _capsules, _messages, _reports, _blocked_users
    global _privacy, _plan_location_consents, _notifications, _answers, _session_records, _assessment_results, _skeletons, _profiles, _auth_accounts, _auth_tokens
    keys = (
        "plans", "rooms", "capsules", "messages", "reports", "blocked_users",
        "privacy", "plan_location_consents", "notifications", "answers", "sessions", "assessment_results", "skeletons", "profile", "profiles", "auth_accounts", "auth_tokens",
    )
    try:
        persisted = {key: _runtime_state.load(key) for key in keys}
    except Exception as exc:
        _log.warning("runtime_state_restore_unavailable error=%s", str(exc)[:240])
        persisted = {key: None for key in keys}
    if persisted["plans"] is not None:
        _plans = persisted["plans"]
    if persisted["rooms"] is not None:
        _rooms = persisted["rooms"]
    if persisted["capsules"] is not None:
        _capsules = persisted["capsules"]
    if persisted["messages"] is not None:
        _messages = persisted["messages"]
    if persisted["reports"] is not None:
        _reports = persisted["reports"]
    if persisted["blocked_users"] is not None:
        _blocked_users = set(persisted["blocked_users"])
    if persisted["privacy"] is not None:
        _privacy = persisted["privacy"]
    if persisted["plan_location_consents"] is not None:
        _plan_location_consents = persisted["plan_location_consents"]
    if persisted["notifications"] is not None:
        _notifications = persisted["notifications"]
    if persisted["answers"] is not None:
        _answers = persisted["answers"]
    if persisted["sessions"] is not None:
        _session_records = persisted["sessions"]
    if persisted["auth_accounts"] is not None:
        _auth_accounts = persisted["auth_accounts"]
    if persisted["auth_tokens"] is not None:
        _auth_tokens = persisted["auth_tokens"]
    if persisted["assessment_results"] is not None:
        _assessment_results = persisted["assessment_results"]
    if persisted["skeletons"] is not None:
        _skeletons = persisted["skeletons"]
    if persisted["profiles"] is not None:
        _profiles = persisted["profiles"]
    elif persisted["profile"] is not None:
        _profiles = {"demo-user": persisted["profile"]}
    elif os.getenv("APP_ENV", "development").lower() in {"production", "staging"} and os.getenv("SHUFFL_DEMO_MODE", "0") != "1":
        _plans, _rooms, _capsules = {}, [], {}
        _messages, _reports, _blocked_users = [], [], set()
        _privacy, _plan_location_consents, _notifications, _answers = {}, {}, [], []
        _assessment_results, _skeletons = [], []
        _profiles = {}
        _auth_accounts, _auth_tokens = {}, {}


def _persist_runtime_state() -> None:
    _runtime_state.save("plans", _plans)
    _runtime_state.save("rooms", _rooms)
    _runtime_state.save("capsules", _capsules)
    _runtime_state.save("messages", _messages)
    _runtime_state.save("reports", _reports)
    _runtime_state.save("blocked_users", sorted(_blocked_users))
    _runtime_state.save("privacy", _privacy)
    _runtime_state.save("plan_location_consents", _plan_location_consents)
    _runtime_state.save("notifications", _notifications)
    _runtime_state.save("answers", _answers)
    _runtime_state.save("sessions", _session_records)
    _runtime_state.save("assessment_results", _assessment_results)
    _runtime_state.save("skeletons", _skeletons)
    _runtime_state.save("profiles", _profiles)
    _runtime_state.save("auth_accounts", _auth_accounts)
    _runtime_state.save("auth_tokens", _auth_tokens)


_restore_runtime_state()


def find_room(room_id: str) -> dict[str, Any]:
    room = _domain_store.get_room(room_id) if _domain_store.available else None
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


def _room_snapshot(room_id: str) -> dict[str, Any]:
    room = find_room(room_id)
    return {
        "type": "room_state",
        "room": {key: value for key, value in room.items() if key != "join_requests"},
        "plan": _domain_store.get_plan(room.get("plan_id")) if _domain_store.available else None,
    }


async def _broadcast_room(room_id: str, event: dict[str, Any] | None = None) -> None:
    """Push the latest authoritative snapshot to every connected room client."""
    sockets = list(_room_sockets.get(room_id, set()))
    if not sockets:
        return
    payload = {**_room_snapshot(room_id), "event": event} if event else _room_snapshot(room_id)
    stale: list[WebSocket] = []
    for socket in sockets:
        try:
            await socket.send_json(payload)
        except Exception:
            stale.append(socket)
    for socket in stale:
        _room_sockets.get(room_id, set()).discard(socket)


def _queue_room_event(room_id: str, event_type: str, **data: Any) -> None:
    """Schedule broadcast from synchronous API handlers without blocking them."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return
    loop.create_task(_broadcast_room(room_id, {"type": event_type, **data}))


def _record_notification(user_id: str, kind: str, payload: dict[str, Any]) -> dict[str, Any]:
    notification_id = new_id("notification")
    created_at = datetime.now(timezone.utc).isoformat()
    record = {"id": notification_id, "user_id": user_id, "kind": kind, **payload, "read": False, "created_at": created_at}
    if _domain_store.available:
        try:
            record = {**_domain_store.add_notification(notification_id=notification_id, user_id=user_id, kind=kind, payload=payload), "created_at": created_at}
        except Exception:
            _log.exception("notification_persist_failed notification_id=%s", notification_id)
    return record


def _touch_room(room: dict[str, Any]) -> None:
    room["updated_at"] = datetime.now(timezone.utc).isoformat()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "shuffl-api"}


@app.get("/v1/health/readiness")
def readiness() -> dict[str, Any]:
    """Deployment probe: configuration can be inspected without admin credentials."""
    config = validate_startup_config()
    database = database_readiness(store.engine)
    ready = bool(config["ok"] and database["status"] == "ok")
    return {
        "status": "ready" if ready else "not_ready",
        "service": "shuffl-api",
        "environment": config["environment"],
        "checks": {"configuration": config, "database": database},
    }


@app.get("/v1/admin/health")
def admin_health(_: str = Depends(require_admin)) -> dict[str, Any]:
    return {"status": "ok", "service": "shuffl-admin", "database": store.summary()}


class AdminSettingsUpdate(BaseModel):
    pipeline_locked: bool | None = None
    feature_flags: dict[str, bool] = Field(default_factory=dict)
    backup_retention_days: int | None = Field(default=None, ge=1, le=365)


@app.get("/v1/admin/settings")
def admin_settings(_: str = Depends(require_admin)) -> dict[str, Any]:
    """Expose safe operational status; never return secret values."""
    config = validate_startup_config()
    database = database_readiness(store.engine)
    summary = store.summary()
    persisted = store.setting_snapshot()
    return {
        "environment": config["environment"],
        "ready": bool(config["ok"] and database["status"] == "ok"),
        "database": database,
        "database_configured": config["database_configured"],
        "google_places_configured": bool(os.getenv("GOOGLE_PLACES_API_KEY", "").strip() or os.getenv("GOOGLE_MAPS_API_KEY", "").strip()),
        "google_login_configured": bool(os.getenv("GOOGLE_OAUTH_CLIENT_ID", "").strip()),
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY", "").strip()),
        "admin_auth_configured": bool(os.getenv("ADMIN_API_TOKEN", "").strip() or os.getenv("ADMIN_ROLE_TOKENS", "").strip()),
        "cors_origins_configured": config["cors_origins_configured"],
        "pipeline_locked": summary["pipeline_locked"],
        "feature_flags": {key.removeprefix("feature_flag."): value == "1" for key, value in persisted.items() if key.startswith("feature_flag.")},
        "backup_retention_days": int(persisted.get("backup_retention_days", "30")),
        "google_reviews_persisted": False,
        "opening_hours_mode": "display_time_live",
        "warnings": config["warnings"],
        "errors": config["errors"],
    }


@app.patch("/v1/admin/settings")
def update_admin_settings(payload: AdminSettingsUpdate, actor: str = Depends(require_admin_permission("rbac.manage"))) -> dict[str, Any]:
    """Persist only safe operational settings; secrets remain server-side."""
    if payload.pipeline_locked is not None:
        store.set_setting("pipeline_locked", "1" if payload.pipeline_locked else "0", actor)
    for name, enabled in payload.feature_flags.items():
        if not re.fullmatch(r"[a-z][a-z0-9_-]{1,79}", name):
            raise HTTPException(status_code=422, detail=f"Invalid feature flag name: {name}")
        store.set_setting(f"feature_flag.{name}", "1" if enabled else "0", actor)
    if payload.backup_retention_days is not None:
        store.set_setting("backup_retention_days", str(payload.backup_retention_days), actor)
    with store.engine.begin() as conn:
        conn.execute(text("INSERT INTO admin_audit_log (id,venue_id,action,actor,after_json,created_at) VALUES (:id,'__system__','settings_updated',:actor,:after_json,:created_at)"), {"id": uuid4().hex, "actor": actor, "after_json": json.dumps(payload.model_dump(exclude_none=True)), "created_at": datetime.now(timezone.utc).isoformat()})
    return admin_settings(actor)


@app.get("/v1/admin/summary")
def admin_summary(_: str = Depends(require_admin)) -> dict[str, Any]:
    return store.summary()


@app.get("/v1/admin/ops/launch-audit")
def admin_launch_audit(_: str = Depends(require_admin)) -> dict[str, Any]:
    return build_launch_audit(store.engine)


@app.get("/v1/admin/me")
def admin_me(x_admin_token: str | None = Header(default=None)) -> dict[str, Any]:
    principal = _admin_principal(x_admin_token)
    return {"actor": principal["actor"], "role": principal["role"], "permissions": sorted(ADMIN_PERMISSIONS[principal["role"]])}


@app.get("/v1/admin/roles")
def admin_roles(_: str = Depends(require_admin_permission("rbac.manage"))) -> dict[str, Any]:
    return {"roles": [{"name": role, "permissions": sorted(permissions)} for role, permissions in ADMIN_PERMISSIONS.items()]}


class PipelineStartRequest(BaseModel):
    source_dir: str | None = None
    max_rows: int = Field(default=5000, ge=1, le=10000)
    retry_of: str | None = None


def _run_pipeline(run_id: str, source_dir: str | None, max_rows: int) -> None:
    """Run the deterministic source sync in a durable background record."""
    try:
        store.update_pipeline_run(run_id, "RUNNING")
        result = store.sync_from_source(source_dir)
        result["processed"] = result.get("source_rows", 0)
        result["max_rows"] = max_rows
        store.update_pipeline_run(run_id, "SUCCEEDED", summary=result)
    except Exception as exc:
        store.update_pipeline_run(run_id, "FAILED", summary={"error": str(exc)}, error_count=1)


@app.get("/v1/admin/pipeline/runs")
def admin_pipeline_runs(limit: int = Query(default=50, ge=1, le=200), _: str = Depends(require_admin)) -> dict[str, Any]:
    return {"items": store.pipeline_runs(limit)}


@app.post("/v1/admin/pipeline/runs")
def start_admin_pipeline(payload: PipelineStartRequest, background_tasks: BackgroundTasks, actor: str = Depends(require_admin_permission("pipeline.run"))) -> dict[str, Any]:
    if store.summary().get("pipeline_locked"):
        raise HTTPException(status_code=423, detail="Venue database is locked; pipeline sync is disabled")
    run = store.create_pipeline_run(payload.source_dir)
    background_tasks.add_task(_run_pipeline, run["run_id"], payload.source_dir, payload.max_rows)
    return {"run": run, "queued_by": actor, "cost": {"provider_calls": 0, "currency": "USD"}}


@app.post("/v1/admin/pipeline/runs/{run_id}/retry")
def retry_admin_pipeline(run_id: str, background_tasks: BackgroundTasks, actor: str = Depends(require_admin_permission("pipeline.run"))) -> dict[str, Any]:
    if os.getenv("VENUE_PIPELINE_LOCKED", "0").strip().lower() in {"1", "true", "yes", "on"}:
        raise HTTPException(status_code=423, detail="Venue database is locked; pipeline sync is disabled")
    prior = store.pipeline_run(run_id)
    if not prior:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    if prior["status"] not in {"FAILED", "CANCELLED"}:
        raise HTTPException(status_code=409, detail="Only failed or cancelled runs can be retried")
    run = store.create_pipeline_run(prior.get("source_dir"))
    background_tasks.add_task(_run_pipeline, run["run_id"], prior.get("source_dir"), 5000)
    return {"run": run, "retry_of": run_id, "queued_by": actor}


@app.get("/v1/admin/pipeline/runs/{run_id}")
def admin_pipeline_run(run_id: str, _: str = Depends(require_admin)) -> dict[str, Any]:
    run = store.pipeline_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    return run


@app.get("/v1/admin/venues")
def admin_venues(
    search: str = Query(default="", max_length=160),
    status: str = Query(default="", max_length=40),
    verification: str = Query(default="", max_length=40),
    city: str = Query(default="", max_length=120),
    state: str = Query(default="", max_length=120),
    area: str = Query(default="", max_length=160),
    venue_type: str = Query(default="", max_length=80),
    publication: str = Query(default="", max_length=40),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=200, ge=1, le=200),
    _: str = Depends(require_admin),
) -> dict[str, Any]:
    if publication and publication not in {"DRAFT", "PUBLISHED", "UNPUBLISHED", "ARCHIVED"}:
        raise HTTPException(status_code=422, detail="Invalid publication status")
    return store.list_venues(search, status, verification, page, page_size, city, state, area, venue_type, publication)


class AdminVenueCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=255)
    google_place_id: str | None = None
    city: str = "New Delhi"
    state: str = "Delhi"
    area: str = ""
    discovered_type: str = "venue"
    official_url: str = ""
    menu_url: str = ""
    booking_url: str = ""
    social_urls: list[str] = Field(default_factory=list)
    metro_name: str = ""
    metro_distance_km: float | None = None
    photos: list[str] = Field(default_factory=list)
    manual_vibe: str = ""
    manual_tags: list[str] = Field(default_factory=list)
    manual_notes: str = ""
    admission_status: str = "Insufficient evidence"
    verification_status: str = "in_process"


class PipelineStartRequest(BaseModel):
    source_dir: str | None = None
    max_rows: int = Field(default=5000, ge=1, le=10000)
    retry_of: str | None = None


class MediaLayoutUpdate(BaseModel):
    sort_order: int | None = Field(default=None, ge=0, le=999)
    crop: dict[str, float] | None = None


class AdminStatusUpdate(BaseModel):
    status: str = Field(min_length=1, max_length=40)


class AdminRoleUpdate(BaseModel):
    role: str = Field(min_length=1, max_length=40)


@app.get("/v1/admin/options")
def admin_options(_: str = Depends(require_admin)) -> dict[str, list[str]]:
    return store.distinct_values()


@app.get("/v1/admin/areas")
def admin_area_catalog(_: str = Depends(require_admin)) -> dict[str, Any]:
    return {"items": store.area_catalog(), "source": "venue_pipeline_backend/config/areas.csv + admin_venues"}


@app.post("/v1/admin/venues")
def create_admin_venue(payload: AdminVenueCreate, actor: str = Depends(require_admin_permission("venue.draft"))) -> dict[str, Any]:
    try:
        return store.create_venue(payload.model_dump(), actor)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/v1/admin/import")
async def import_admin_workbook(file: UploadFile = File(...), actor: str = Depends(require_admin_permission("venue.draft"))) -> dict[str, Any]:
    if not file.filename or not file.filename.lower().endswith((".xlsx", ".xlsm", ".csv")):
        raise HTTPException(status_code=415, detail="Upload an .xlsx, .xlsm or .csv workbook")
    content = await file.read()
    rows: list[dict[str, Any]] = []
    if file.filename.lower().endswith(".csv"):
        import csv, io
        rows = list(csv.DictReader(io.StringIO(content.decode("utf-8-sig"))))
    else:
        from openpyxl import load_workbook
        workbook = load_workbook(io.BytesIO(content), read_only=True, data_only=True)
        for sheet in workbook.worksheets:
            values = list(sheet.values)
            if not values:
                continue
            headers = [str(value or "").strip() for value in values[0]]
            rows.extend({headers[index]: row[index] for index in range(min(len(headers), len(row))) if headers[index]} for row in values[1:] if any(row))
    try:
        return {"filename": file.filename, **store.import_rows(rows, actor)}
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/v1/admin/venues/{venue_id}")
def admin_venue(venue_id: str, _: str = Depends(require_admin)) -> dict[str, Any]:
    item = store.get_venue(venue_id)
    if not item:
        raise HTTPException(status_code=404, detail="Venue not found")
    normalized = store.normalized_venue(venue_id)
    item["normalized"] = normalized
    # Keep the dashboard's existing DTO compatible while exposing the new
    # canonical tables in a single detail response.
    item["venue_identity"] = [normalized["identity"]] if normalized.get("identity") else []
    item["venue_scores"] = normalized.get("scores", [])
    item["venue_tags"] = normalized.get("tags", [])
    item["venue_sources"] = normalized.get("sources", [])
    item["venue_time_slots"] = normalized.get("time_slots", [])
    item["venue_metros"] = normalized.get("metros", [])
    item["venue_media"] = store.media(venue_id)
    item["venue_history"] = store.history(venue_id)
    return item


@app.post("/v1/admin/schema/backfill")
def backfill_admin_schema(_: str = Depends(require_admin_permission("pipeline.run"))) -> dict[str, Any]:
    """One-time/repair backfill from lifecycle JSON into canonical tables."""
    return store.backfill_normalized()


@app.get("/v1/admin/venues/{venue_id}/live")
def admin_live_venue(venue_id: str, _: str = Depends(require_admin)) -> dict[str, Any]:
    """Fetch licensed Google display fields and optional AI insight per request.

    This endpoint deliberately does not write Google details, reviews, hours,
    coordinates or photos to MySQL. They are request-scoped display data.
    """
    item = store.get_venue(venue_id)
    if not item:
        raise HTTPException(status_code=404, detail="Venue not found")
    place_id = item.get("google_place_id")
    if not place_id:
        raise HTTPException(status_code=422, detail="Venue has no Google place_id")
    try:
        live = fetch_for_display(place_id)
    except GooglePlacesError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    ai: dict[str, Any]
    try:
        ai = GeminiClient().analyze(live)
        ai["provider"] = "gemini"
    except GeminiError as exc:
        ai = {**fallback_metadata(live), "provider": "deterministic_fallback", "message": str(exc)}
    ai.setdefault("deterministic_scores", score(live))
    return {"venue": item, "google_live": live, "ai_insight": ai, "persisted": False}


@app.get("/v1/admin/live/photo")
def admin_live_photo(name: str = Query(min_length=1), max_width_px: int = Query(default=900, ge=200, le=1600), _: str = Depends(require_admin_photo)) -> StreamingResponse:
    """Proxy a Google Place photo so the browser never receives the API key."""
    if not re.fullmatch(r"places/[A-Za-z0-9_-]+/photos/[A-Za-z0-9_-]+", name):
        raise HTTPException(status_code=400, detail="Invalid Google photo resource name")
    api_key = os.getenv("GOOGLE_PLACES_API_KEY") or os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="Google Places API key is not configured")
    query = urllib.parse.urlencode({"maxWidthPx": max_width_px, "key": api_key})
    url = f"https://places.googleapis.com/v1/{name}/media?{query}"
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            body = response.read()
            media_type = response.headers.get_content_type() or "image/jpeg"
    except urllib.error.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Google photo request failed: {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise HTTPException(status_code=502, detail=f"Google photo network error: {exc.reason}") from exc
    return StreamingResponse(iter([body]), media_type=media_type, headers={"Cache-Control": "private, max-age=300"})


@app.patch("/v1/admin/venues/{venue_id}")
def update_admin_venue(venue_id: str, payload: AdminVenueUpdate, actor: str = Depends(require_admin_permission("venue.draft"))) -> dict[str, Any]:
    try:
        item = store.update_venue(venue_id, payload.model_dump(exclude_none=True), actor)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if not item:
        raise HTTPException(status_code=404, detail="Venue not found")
    return item


@app.post("/v1/admin/venues/{venue_id}/publish")
def publish_admin_venue(venue_id: str, actor: str = Depends(require_admin_permission("venue.publish"))) -> dict[str, Any]:
    try:
        item = store.publish_venue(venue_id, actor)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if not item:
        raise HTTPException(status_code=404, detail="Venue not found")
    return item


@app.post("/v1/admin/venues/{venue_id}/unpublish")
def unpublish_admin_venue(venue_id: str, actor: str = Depends(require_admin_permission("venue.publish"))) -> dict[str, Any]:
    item = store.unpublish_venue(venue_id, actor)
    if not item:
        raise HTTPException(status_code=404, detail="Venue not found")
    return item


@app.post("/v1/admin/venues/{venue_id}/archive")
def archive_admin_venue(venue_id: str, actor: str = Depends(require_admin_permission("venue.publish"))) -> dict[str, Any]:
    item = store.archive_venue(venue_id, actor)
    if not item:
        raise HTTPException(status_code=404, detail="Venue not found")
    return item


@app.post("/v1/admin/venues/{venue_id}/restore")
def restore_admin_venue(venue_id: str, actor: str = Depends(require_admin_permission("venue.publish"))) -> dict[str, Any]:
    item = store.restore_venue(venue_id, actor)
    if not item:
        raise HTTPException(status_code=404, detail="Venue not found")
    return item


@app.get("/v1/admin/venues/{venue_id}/history")
def admin_venue_history(venue_id: str, _: str = Depends(require_admin)) -> dict[str, Any]:
    if not store.get_venue(venue_id):
        raise HTTPException(status_code=404, detail="Venue not found")
    return {"items": store.history(venue_id)}


@app.get("/v1/admin/venues/{venue_id}/media")
def admin_venue_media(venue_id: str, _: str = Depends(require_admin)) -> dict[str, Any]:
    if not store.get_venue(venue_id):
        raise HTTPException(status_code=404, detail="Venue not found")
    return {"items": store.media(venue_id)}


@app.get("/v1/admin/media")
def admin_media_library(
    search: str = "",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=60, ge=1, le=200),
    _: str = Depends(require_admin),
) -> dict[str, Any]:
    return store.media_library(search=search, page=page, page_size=page_size)


@app.post("/v1/admin/venues/{venue_id}/media")
async def upload_admin_venue_media(
    venue_id: str,
    file: UploadFile = File(...),
    alt_text: str = Form(default=""),
    rights_status: str = Form(default="licensed"),
    actor: str = Depends(require_admin_permission("media.write")),
) -> dict[str, Any]:
    allowed = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
    extension = allowed.get(file.content_type or "")
    if not extension:
        raise HTTPException(status_code=415, detail="Only JPEG, PNG and WebP images are supported")
    content = await file.read(8 * 1024 * 1024 + 1)
    if len(content) > 8 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image must be 8 MB or smaller")
    media_id = uuid4().hex
    path = MEDIA_ROOT / f"{media_id}{extension}"
    path.write_bytes(content)
    try:
        item = store.add_media(venue_id, f"/media/{path.name}", "image", "admin_upload", rights_status[:80], alt_text[:255], actor)
    except ValueError as exc:
        path.unlink(missing_ok=True)
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return item


@app.delete("/v1/admin/venues/{venue_id}/media/{media_id}")
def delete_admin_venue_media(venue_id: str, media_id: str, _: str = Depends(require_admin_permission("media.write"))) -> dict[str, bool]:
    media = next((item for item in store.media(venue_id) if item.get("media_id") == media_id), None)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    if not store.remove_media(venue_id, media_id, "admin"):
        raise HTTPException(status_code=404, detail="Media not found")
    url = str(media.get("url", ""))
    if url.startswith("/media/"):
        candidate = (MEDIA_ROOT / Path(url.removeprefix("/media/"))).resolve()
        if MEDIA_ROOT.resolve() in candidate.parents and candidate.exists():
            candidate.unlink()
    return {"deleted": True}


@app.post("/v1/admin/venues/{venue_id}/media/{media_id}/cover")
def cover_admin_venue_media(venue_id: str, media_id: str, actor: str = Depends(require_admin_permission("media.write"))) -> dict[str, bool]:
    if not store.set_cover_media(venue_id, media_id, actor):
        raise HTTPException(status_code=404, detail="Media not found")
    return {"cover": True}


@app.patch("/v1/admin/venues/{venue_id}/media/{media_id}")
def layout_admin_venue_media(venue_id: str, media_id: str, payload: MediaLayoutUpdate, actor: str = Depends(require_admin_permission("media.write"))) -> dict[str, bool]:
    if payload.crop:
        if any(value < 0 or value > 1 for value in payload.crop.values()):
            raise HTTPException(status_code=422, detail="Crop values must be between 0 and 1")
    if not store.update_media_layout(venue_id, media_id, actor, sort_order=payload.sort_order, crop=payload.crop):
        raise HTTPException(status_code=404, detail="Media not found")
    return {"updated": True}


@app.post("/v1/admin/sync")
def sync_admin_database(source_dir: str | None = None, _: str = Depends(require_admin_permission("pipeline.run"))) -> dict[str, Any]:
    if store.summary().get("pipeline_locked"):
        raise HTTPException(status_code=423, detail="Venue database is locked; pipeline sync is disabled")
    return store.sync_from_source(source_dir)


@app.get("/v1/admin/users")
def admin_users(search: str = "", status: str = "", _: str = Depends(require_admin)) -> dict[str, Any]:
    items = store.users(search=search, status=status)
    return {"items": items, "count": len(items)}


@app.get("/v1/admin/rooms")
def admin_rooms(_: str = Depends(require_admin)) -> dict[str, Any]:
    """Operational room view without exposing private join-request payloads."""
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    items = []
    with _domain_store.engine.connect() as conn:
        room_ids = conn.execute(text("SELECT id FROM rooms ORDER BY id DESC")).all()
    for room_row in room_ids:
        room = _domain_store.get_room(str(room_row[0]))
        if not room:
            continue
        plan = _domain_store.get_plan(room.get("plan_id"))
        items.append({
            "id": room.get("id"),
            "title": room.get("title"),
            "status": room.get("status"),
            "visibility": room.get("visibility"),
            "owner_id": room.get("owner_id"),
            "member_count": len(room.get("members", [])),
            "plan_id": room.get("plan_id"),
            "plan_locked": bool(plan and plan.get("locked")),
            "updated_at": room.get("updated_at") or room.get("created_at"),
        })
    return {"items": items}


@app.get("/v1/admin/reports")
def admin_reports(status: str | None = None, _: str = Depends(require_admin)) -> dict[str, Any]:
    items = _domain_store.list_reports(status) if _domain_store.available else (_reports if not status else [item for item in _reports if item.get("status") == status])
    return {"items": items, "count": len(items)}


@app.patch("/v1/admin/reports/{report_id}")
def update_admin_report(report_id: str, payload: AdminStatusUpdate, actor: str = Depends(require_admin_permission("admin.moderate"))) -> dict[str, Any]:
    if payload.status not in {"received", "reviewing", "resolved", "dismissed"}:
        raise HTTPException(status_code=422, detail="Invalid report status")
    updated = _domain_store.update_report(report_id, payload.status) if _domain_store.available else False
    if not updated:
        item = next((row for row in _reports if row.get("id") == report_id), None)
        if not item:
            raise HTTPException(status_code=404, detail="Report not found")
        item["status"] = payload.status
        return item
    item = next((row for row in _domain_store.list_reports() if row.get("id") == report_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Report not found")
    _log.info("admin_report_updated actor=%s report_id=%s status=%s", actor, report_id, payload.status)
    with store.engine.begin() as conn:
        conn.execute(text("INSERT INTO admin_audit_log (id,venue_id,action,actor,after_json,created_at) VALUES (:id,'__moderation__','report_updated',:actor,:after_json,:created_at)"), {"id": uuid4().hex, "actor": actor, "after_json": json.dumps(item), "created_at": datetime.now(timezone.utc).isoformat()})
    return item


@app.patch("/v1/admin/users/{user_id}")
def update_admin_user(user_id: str, payload: AdminStatusUpdate, actor: str = Depends(require_admin_permission("rbac.manage"))) -> dict[str, Any]:
    if payload.status not in {"active", "disabled", "suspended"}:
        raise HTTPException(status_code=422, detail="Invalid user status")
    with store.engine.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE auth_users ADD COLUMN status VARCHAR(40) NOT NULL DEFAULT 'active'"))
        except Exception:
            pass
        result = conn.execute(text("UPDATE auth_users SET status=:status WHERE id=:id"), {"status": payload.status, "id": user_id})
        if not result.rowcount:
            raise HTTPException(status_code=404, detail="User not found")
    if payload.status != "active" and _auth_store.available:
        _auth_store.revoke_user_sessions(user_id)
    with store.engine.begin() as conn:
        conn.execute(text("INSERT INTO admin_audit_log (id,venue_id,action,actor,after_json,created_at) VALUES (:id,'__users__','user_status_updated',:actor,:after_json,:created_at)"), {"id": uuid4().hex, "actor": actor, "after_json": json.dumps({"user_id": user_id, "status": payload.status}), "created_at": datetime.now(timezone.utc).isoformat()})
    _log.info("admin_user_updated actor=%s user_id=%s status=%s", actor, user_id, payload.status)
    return {"user_id": user_id, "status": payload.status}


@app.patch("/v1/admin/users/{user_id}/role")
def update_admin_user_role(user_id: str, payload: AdminRoleUpdate, actor: str = Depends(require_admin_permission("rbac.manage"))) -> dict[str, Any]:
    if payload.role.upper() not in ADMIN_PERMISSIONS:
        raise HTTPException(status_code=422, detail="Invalid admin role")
    with store.engine.begin() as conn:
        result = conn.execute(text("UPDATE admin_users SET role=:role WHERE user_id=:id"), {"role": payload.role.upper(), "id": user_id})
        if not result.rowcount:
            raise HTTPException(status_code=404, detail="Admin user not found")
        conn.execute(text("INSERT INTO admin_audit_log (id,venue_id,action,actor,after_json,created_at) VALUES (:id,'__users__','user_role_updated',:actor,:after_json,:created_at)"), {"id": uuid4().hex, "actor": actor, "after_json": json.dumps({"user_id": user_id, "role": payload.role.upper()}), "created_at": datetime.now(timezone.utc).isoformat()})
    _log.info("admin_role_updated actor=%s user_id=%s role=%s", actor, user_id, payload.role.upper())
    return {"user_id": user_id, "role": payload.role.upper()}


@app.post("/v1/admin/users/{user_id}/reset")
def reset_admin_user(user_id: str, actor: str = Depends(require_admin_permission("rbac.manage"))) -> dict[str, Any]:
    """Reset onboarding/application state while preserving account identity."""
    if _auth_store.available:
        _auth_store.revoke_user_sessions(user_id)
    if _domain_store.available:
        with _domain_store.engine.begin() as conn:
            for table in ("assessment_sessions", "card_exposures", "plans", "plan_location_consents", "privacy_settings"):
                try:
                    conn.execute(text(f"DELETE FROM {table} WHERE user_id=:id"), {"id": user_id})
                except Exception:
                    pass
    with store.engine.begin() as conn:
        conn.execute(text("INSERT INTO admin_audit_log (id,venue_id,action,actor,after_json,created_at) VALUES (:id,'__users__','user_account_reset',:actor,:after_json,:created_at)"), {"id": uuid4().hex, "actor": actor, "after_json": json.dumps({"user_id": user_id}), "created_at": datetime.now(timezone.utc).isoformat()})
    return {"user_id": user_id, "reset": True, "sessions_revoked": True}


@app.delete("/v1/admin/users/{user_id}")
def delete_admin_user(user_id: str, actor: str = Depends(require_admin_permission("rbac.manage"))) -> dict[str, Any]:
    """Soft-delete an account without breaking moderation/audit references."""
    if user_id == actor:
        raise HTTPException(status_code=409, detail="An admin cannot delete their own account")
    if _auth_store.available:
        _auth_store.revoke_user_sessions(user_id)
    anonymized_email = f"deleted+{uuid4().hex[:12]}@invalid.shuffl"
    with store.engine.begin() as conn:
        result = conn.execute(text("UPDATE auth_users SET email=:email,name='Deleted user',status='disabled',password_hash=NULL,provider_subject=NULL WHERE id=:id"), {"email": anonymized_email, "id": user_id})
        if not result.rowcount:
            raise HTTPException(status_code=404, detail="User not found")
        conn.execute(text("INSERT INTO admin_audit_log (id,venue_id,action,actor,before_json,after_json,created_at) VALUES (:id,'__users__','user_soft_deleted',:actor,:before_json,:after_json,:created_at)"), {"id": uuid4().hex, "actor": actor, "before_json": json.dumps({"user_id": user_id}), "after_json": json.dumps({"user_id": user_id, "status": "disabled", "anonymized": True}), "created_at": datetime.now(timezone.utc).isoformat()})
    return {"user_id": user_id, "deleted": True, "mode": "soft_delete"}


@app.get("/v1/admin/users/{user_id}/audit")
def admin_user_audit(user_id: str, _: str = Depends(require_admin)) -> dict[str, Any]:
    with store.engine.connect() as conn:
        rows = conn.execute(text("SELECT id,action,actor,before_json,after_json,created_at FROM admin_audit_log WHERE venue_id='__users__' AND (after_json LIKE :needle OR before_json LIKE :needle) ORDER BY created_at DESC"), {"needle": f"%{user_id}%"}).mappings().all()
    return {"items": [dict(row) for row in rows]}


@app.get("/v1/admin/export.xlsx")
def export_admin_database(_: str = Depends(require_admin_permission("database.export"))) -> StreamingResponse:
    workbook = store.export_xlsx()
    return StreamingResponse(workbook, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=SHUFFL_Admin_Venue_Database.xlsx"})


@app.post("/v1/sessions")
def create_session(payload: SessionRequest | None = None) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    session = {
        "id": new_id("session"),
        "client_id": (payload.client_id if payload else "").strip(),
        "mode": "api",
        "created_at": now.isoformat(),
        "last_seen_at": now.isoformat(),
    }
    _session_records.append(session)
    return session


def _normalise_email(value: str) -> str:
    return value.strip().casefold()


def _password_digest(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 210_000)
    return f"pbkdf2_sha256$210000${salt.hex()}${digest.hex()}"


def _password_matches(password: str, encoded: str) -> bool:
    try:
        algorithm, rounds, salt_hex, digest_hex = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(rounds)).hex()
        return hmac.compare_digest(candidate, digest_hex)
    except (ValueError, TypeError):
        return False


def _issue_auth_token(user_id: str) -> str:
    if _auth_store.available:
        return _auth_store.issue_session(user_id)
    token = secrets.token_urlsafe(32)
    _auth_tokens[token] = {"user_id": user_id, "issued_at": datetime.now(timezone.utc).isoformat()}
    return token


def _auth_tokens_for(user_id: str) -> dict[str, str]:
    """Issue the short-lived access token and durable refresh token together."""
    if _auth_store.available:
        return {
            "access_token": _auth_store.issue_session(user_id, kind="access", ttl_seconds=900),
            "refresh_token": _auth_store.issue_refresh(user_id),
        }
    access = _issue_auth_token(user_id)
    refresh = secrets.token_urlsafe(40)
    _auth_tokens[refresh] = {"user_id": user_id, "kind": "refresh", "issued_at": datetime.now(timezone.utc).isoformat()}
    return {"access_token": access, "refresh_token": refresh}


def _send_auth_email(*, recipient: str, subject: str, body: str) -> bool:
    """Send transactional auth mail; development mode deliberately logs only."""
    host = os.getenv("SMTP_HOST", "").strip()
    if not host:
        if os.getenv("APP_ENV", "development").lower() in {"development", "test"}:
            _log.info("auth_email_dev recipient=%s subject=%s body=%s", recipient, subject, body)
            return False
        raise HTTPException(status_code=503, detail="SMTP is not configured")
    port = int(os.getenv("SMTP_PORT", "587"))
    message = EmailMessage()
    message["From"] = os.getenv("SMTP_FROM_EMAIL", os.getenv("SMTP_USERNAME", ""))
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)
    try:
        with smtplib.SMTP(host, port, timeout=10) as smtp:
            if os.getenv("SMTP_USE_TLS", "1").strip().lower() not in {"0", "false", "no"}:
                smtp.starttls()
            username = os.getenv("SMTP_USERNAME", "")
            if username:
                smtp.login(username, os.getenv("SMTP_PASSWORD", ""))
            smtp.send_message(message)
        return True
    except (OSError, smtplib.SMTPException) as exc:
        _log.exception("auth_email_failed recipient=%s", recipient)
        raise HTTPException(status_code=503, detail="Email delivery is temporarily unavailable") from exc


def _auth_user(authorization: str | None) -> dict[str, Any] | None:
    value = (authorization or "").strip()
    if not value.lower().startswith("bearer "):
        return None
    token = value[7:].strip()
    if _auth_store.available:
        return _auth_store.user_for_token(token)
    record = _auth_tokens.get(token)
    if not record:
        return None
    return _auth_accounts.get(record.get("user_id"))


def _require_user(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = _auth_user(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


def _request_user_id(authorization: str | None) -> str:
    """Return the authenticated owner, retaining the development demo user."""
    user = _auth_user(authorization)
    return str(user["id"]) if user else "demo-user"


@app.post("/v1/auth/register")
def register(payload: AuthRegisterRequest) -> dict[str, Any]:
    email = _normalise_email(payload.email)
    if _auth_store.available:
        if _auth_store.find_email(email):
            raise HTTPException(status_code=409, detail="An account with this email already exists")
        user_id = new_id("user")
        account = _auth_store.create_user(user_id=user_id, email=email, name=payload.name.strip(), password_hash=_password_digest(payload.password), provider="password", provider_subject=None)
        tokens = _auth_tokens_for(user_id)
        if os.getenv("APP_ENV", "development").lower() in {"production", "staging"}:
            verification = _auth_store.create_one_time_token("auth_verification_tokens", user_id, 24 * 60 * 60)
            _send_auth_email(recipient=email, subject="Verify your SHUFFL email", body=f"Verify your SHUFFL account with this token: {verification}")
        else:
            _auth_store.mark_verified(user_id)
        return {**tokens, "token_type": "bearer", "user": {"id": user_id, "email": email, "name": account.get("name", "")}}
    if any(account.get("email") == email for account in _auth_accounts.values()):
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    user_id = new_id("user")
    _auth_accounts[user_id] = {
        "id": user_id,
        "email": email,
        "name": payload.name.strip(),
        "password_hash": _password_digest(payload.password),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    tokens = _auth_tokens_for(user_id)
    return {**tokens, "token_type": "bearer", "user": {"id": user_id, "email": email, "name": payload.name.strip()}}


@app.post("/v1/auth/login")
def login(payload: AuthLoginRequest) -> dict[str, Any]:
    email = _normalise_email(payload.email)
    if _auth_store.available:
        account = _auth_store.find_email(email)
        if not account or not _password_matches(payload.password, str(account.get("password_hash") or "")):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        return {**_auth_tokens_for(str(account["id"])), "token_type": "bearer", "user": {"id": account["id"], "email": account["email"], "name": account.get("name", "")}}
    account = next((item for item in _auth_accounts.values() if item.get("email") == email), None)
    if not account or not _password_matches(payload.password, str(account.get("password_hash", ""))):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {**_auth_tokens_for(str(account["id"])), "token_type": "bearer", "user": {"id": account["id"], "email": account["email"], "name": account.get("name", "")}}


@app.post("/v1/auth/google")
def google_login(payload: GoogleAuthRequest) -> dict[str, Any]:
    """Exchange a Google ID token for a SHUFFL session.

    The token is verified server-side through Google's tokeninfo endpoint and
    the audience must match GOOGLE_OAUTH_CLIENT_ID. Access tokens are never
    accepted as a substitute for an ID token.
    """
    client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID", "").strip()
    if not client_id:
        raise HTTPException(status_code=503, detail="Google login is not configured")
    try:
        query = urllib.parse.urlencode({"id_token": payload.id_token})
        with urllib.request.urlopen(f"https://oauth2.googleapis.com/tokeninfo?{query}", timeout=8) as response:
            claims = __import__("json").loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Google token could not be verified") from exc
    if claims.get("aud") != client_id or claims.get("iss") not in {"accounts.google.com", "https://accounts.google.com"}:
        raise HTTPException(status_code=401, detail="Google token audience or issuer is invalid")
    if str(claims.get("email_verified", "")).lower() != "true":
        raise HTTPException(status_code=401, detail="Google email is not verified")
    email = _normalise_email(str(claims.get("email", "")))
    subject = str(claims.get("sub", ""))
    if not email or not subject:
        raise HTTPException(status_code=401, detail="Google token is missing identity claims")
    name = str(claims.get("name") or claims.get("given_name") or email.split("@", 1)[0])[:120]
    account = _auth_store.find_google_subject(subject) if _auth_store.available else None
    if account is None and _auth_store.available:
        if _auth_store.find_email(email):
            raise HTTPException(status_code=409, detail="This email already has a password account")
        account = _auth_store.create_user(user_id=new_id("user"), email=email, name=name, password_hash=None, provider="google", provider_subject=subject)
    if account is None:
        raise HTTPException(status_code=503, detail="Durable authentication storage is unavailable")
    return {**_auth_tokens_for(str(account["id"])), "token_type": "bearer", "user": {"id": account["id"], "email": account["email"], "name": account.get("name", name)}}


@app.get("/v1/auth/me")
def auth_me(user: dict[str, Any] = Depends(_require_user)) -> dict[str, Any]:
    return {"id": user["id"], "email": user["email"], "name": user.get("name", ""), "created_at": user.get("created_at")}


@app.post("/v1/auth/logout")
def logout(authorization: str | None = Header(default=None)) -> dict[str, bool]:
    value = (authorization or "").strip()
    if value.lower().startswith("bearer "):
        token = value[7:].strip()
        if _auth_store.available:
            _auth_store.revoke(token)
        else:
            _auth_tokens.pop(token, None)
    return {"logged_out": True}


@app.post("/v1/auth/refresh")
def refresh(payload: RefreshRequest) -> dict[str, Any]:
    if _auth_store.available:
        account = _auth_store.user_for_token(payload.refresh_token)
        if not account or account.get("token_kind") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
        _auth_store.revoke(payload.refresh_token)
        return {**_auth_tokens_for(str(account["id"])), "token_type": "bearer", "user": {"id": account["id"], "email": account["email"], "name": account.get("name", "")}}
    record = _auth_tokens.get(payload.refresh_token)
    if not record or record.get("kind") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    _auth_tokens.pop(payload.refresh_token, None)
    user_id = str(record["user_id"])
    return {**_auth_tokens_for(user_id), "token_type": "bearer", "user": _auth_accounts.get(user_id, {"id": user_id})}


@app.post("/v1/auth/verify-email")
def verify_email(payload: EmailVerificationRequest) -> dict[str, bool]:
    if not _auth_store.available:
        raise HTTPException(status_code=503, detail="Durable authentication storage is unavailable")
    user_id = _auth_store.consume_one_time_token("auth_verification_tokens", payload.token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Verification token is invalid or expired")
    _auth_store.mark_verified(user_id)
    return {"verified": True}


@app.post("/v1/auth/password-reset/request")
def request_password_reset(payload: PasswordResetRequest) -> dict[str, bool]:
    email = _normalise_email(payload.email)
    account = _auth_store.find_email(email) if _auth_store.available else next((item for item in _auth_accounts.values() if item.get("email") == email), None)
    # Do not disclose whether an account exists.
    if account:
        if not _auth_store.available:
            raise HTTPException(status_code=503, detail="Durable authentication storage is unavailable")
        token = _auth_store.create_one_time_token("auth_password_reset_tokens", str(account["id"]), 30 * 60)
        _send_auth_email(recipient=email, subject="Reset your SHUFFL password", body=f"Reset your SHUFFL password with this token: {token}")
    return {"accepted": True}


@app.post("/v1/auth/password-reset/confirm")
def confirm_password_reset(payload: PasswordResetConfirm) -> dict[str, bool]:
    if not _auth_store.available:
        raise HTTPException(status_code=503, detail="Durable authentication storage is unavailable")
    user_id = _auth_store.consume_one_time_token("auth_password_reset_tokens", payload.token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Reset token is invalid or expired")
    _auth_store.update_password(user_id, _password_digest(payload.password))
    _auth_store.revoke_user_sessions(user_id)
    return {"reset": True}


@app.get("/v1/profiles/me")
def profile(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user_id = _request_user_id(authorization)
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    return _domain_store.profile_get(user_id)


@app.patch("/v1/profiles/me")
def update_profile(payload: ProfileUpdate, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user_id = _request_user_id(authorization)
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    return _domain_store.profile_update(user_id, payload.model_dump())


@app.get("/v1/people")
def people(
    q: str = Query(default="", max_length=120),
    limit: int = Query(default=24, ge=1, le=50),
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    """List discoverable members for co-host and capsule selection."""
    user_id = _request_user_id(authorization)
    if _domain_store.available:
        return {"items": _domain_store.people_search(user_id, q, limit)}
    fallback = []
    for account in _auth_accounts.values():
        if str(account.get("id")) == user_id or str(account.get("status", "active")) != "active":
            continue
        name = str(account.get("name", "")).strip()
        if q.strip().lower() not in name.lower():
            continue
        fallback.append({"id": str(account["id"]), "name": name, "city": "New Delhi", "bio": ""})
    return {"items": fallback[:limit]}


@app.delete("/v1/account")
def delete_account(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    """Reset user-owned runtime state for the current MVP account."""
    user_id = _request_user_id(authorization)
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    _domain_store.profile_delete(user_id)
    if _auth_store.available:
        _auth_store.revoke_user_sessions(user_id)
    return {"deleted": True, "message": "User account data reset. Published venue data was not changed."}


@app.post("/v1/assessment/answers")
def answer(payload: Answer) -> dict[str, Any]:
    record = {"id": new_id("answer"), **payload.model_dump(), "created_at": datetime.now(timezone.utc).isoformat()}
    _answers.append(record)
    return {"accepted": True, **record}


@app.post("/v1/assessment/complete")
def complete_assessment(payload: AssessmentCompletion, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    """Persist the completed daily six-factor assessment result."""
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    record = _domain_store.add_assessment(_request_user_id(authorization), payload.model_dump())
    return {"accepted": True, "assessment": record}


@app.get("/v1/assessment/today")
def latest_assessment(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user_id = _request_user_id(authorization)
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    return {"assessment": _domain_store.latest_assessment(user_id)}


@app.post("/v1/skeletons")
def save_skeleton(payload: SkeletonRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    durations = payload.stop_durations or [round(1 / payload.stops, 4)] * payload.stops
    if len(durations) != payload.stops:
        raise HTTPException(status_code=422, detail="stop_durations must have one value per stop")
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    return _domain_store.add_skeleton(_request_user_id(authorization), payload.model_dump(), durations)


@app.get("/v1/skeletons/latest")
def latest_skeleton(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user_id = _request_user_id(authorization)
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    return {"skeleton": _domain_store.latest_skeleton(user_id)}


@app.post("/v1/plans/generate")
def generate_plan(payload: PlanRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    members = payload.member_scores or [payload.scores]
    chemistry = chemistry_v2(members, payload.duration_hours, payload.strangers)
    venue_types = select_venue_types(members, payload.duration_hours, payload.strangers)
    venue_preferences = [{"preferences": payload.preferences, "pol_sense": payload.pol_sense}]
    venues = fill_venues(venue_types, venue_preferences, DEMO_VENUES)
    plan = {"id": new_id("plan"), "user_id": _request_user_id(authorization), "style": "Could Go Late" if chemistry["vector"].get("ENRG", 50) >= 70 else "Settle Then Roam", "stops": chemistry["stops"], "chemistry": chemistry, "venue_types": venue_types, "venues": venues, "member_ids": payload.members, "status": "draft", "locked": False, "created_at": datetime.now(timezone.utc).isoformat()}
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    return _domain_store.create_plan(plan)


@app.post("/v1/plans")
def create_selected_plan(payload: SelectedPlanRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    """Persist a validated user-built draft from the stop-by-stop picker."""
    ordered = sorted(payload.stops, key=lambda stop: stop.stop_index)
    expected_indexes = list(range(len(ordered)))
    if [stop.stop_index for stop in ordered] != expected_indexes:
        raise HTTPException(status_code=422, detail="Stops must be numbered contiguously from zero")
    identifiers = [stop.venue_id for stop in ordered if stop.venue_id]
    if len(identifiers) != len(set(identifiers)):
        raise HTTPException(status_code=422, detail="A venue cannot be selected for more than one stop")
    for stop in ordered:
        if not stop.venue_id:
            continue
        venue = store.get_venue(stop.venue_id)
        if not venue or venue.get("publication_status") != "PUBLISHED" or venue.get("eligibility_status") not in {"AUTO_APPROVED", "PROVISIONAL"}:
            raise HTTPException(status_code=422, detail=f"Venue is not currently selectable: {stop.venue_id}")
    plan = {
        "id": new_id("plan"),
        "user_id": _request_user_id(authorization),
        "style": payload.title,
        "title": payload.title,
        "stops": [f"{stop.name} · {stop.area}" for stop in ordered],
        "selected_stops": [stop.model_dump() for stop in ordered],
        "chemistry": payload.chemistry,
        "scores": payload.scores,
        "duration_hours": payload.duration_hours,
        "venue_types": [],
        "member_ids": [],
        "status": "draft",
        "locked": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    return _domain_store.create_plan(plan)


@app.post("/v1/plans/{plan_id}/lock")
def lock_plan(plan_id: str, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    plan = _domain_store.get_plan(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    if plan.get("user_id", "demo-user") != _request_user_id(authorization):
        raise HTTPException(status_code=403, detail="You do not own this plan")
    selected_stops = plan.get("selected_stops") or []
    if not selected_stops or any(not item.get("venue_id") for item in selected_stops):
        raise HTTPException(status_code=422, detail="Select one published venue for every stop before locking the plan")
    indexes = [int(item.get("stop_index", -1)) for item in selected_stops]
    if indexes != list(range(len(selected_stops))):
        raise HTTPException(status_code=422, detail="Locked plans must contain an ordered stop for every position")
    if len({item.get("venue_id") for item in selected_stops}) != len(selected_stops):
        raise HTTPException(status_code=422, detail="Locked plans cannot repeat a venue")
    for item in selected_stops:
        venue = store.get_venue(str(item["venue_id"]))
        if not venue or venue.get("publication_status") != "PUBLISHED" or venue.get("eligibility_status") not in {"AUTO_APPROVED", "PROVISIONAL"}:
            raise HTTPException(status_code=422, detail=f"A selected venue is no longer published: {item['venue_id']}")
    locked = _domain_store.lock_plan(plan_id)
    if not locked:
        raise HTTPException(status_code=404, detail="Plan not found")
    return locked


@app.get("/v1/plans/{plan_id}")
def get_plan(plan_id: str, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    plan = _domain_store.get_plan(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    user_id = _request_user_id(authorization)
    if plan.get("user_id", "demo-user") != user_id:
        raise HTTPException(status_code=403, detail="You do not have access to this plan")
    return plan


@app.patch("/v1/plans/{plan_id}/stops")
def update_plan_stops(plan_id: str, payload: SelectedPlanStopsUpdate, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    plan = _domain_store.get_plan(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    if plan.get("user_id", "demo-user") != _request_user_id(authorization):
        raise HTTPException(status_code=403, detail="Only the plan owner can edit stops")
    if plan.get("locked") or plan.get("status") == "locked":
        raise HTTPException(status_code=409, detail="Locked plans cannot change stops")
    ordered = sorted(payload.stops, key=lambda stop: stop.stop_index)
    if [stop.stop_index for stop in ordered] != list(range(len(ordered))):
        raise HTTPException(status_code=422, detail="Stops must be numbered contiguously from zero")
    identifiers = [stop.venue_id for stop in ordered if stop.venue_id]
    if len(identifiers) != len(set(identifiers)):
        raise HTTPException(status_code=422, detail="A venue cannot be selected for more than one stop")
    for stop in ordered:
        if not stop.venue_id:
            raise HTTPException(status_code=422, detail="Select one published venue for every stop")
        venue = store.get_venue(stop.venue_id)
        if not venue or venue.get("publication_status") != "PUBLISHED" or venue.get("eligibility_status") not in {"AUTO_APPROVED", "PROVISIONAL"}:
            raise HTTPException(status_code=422, detail=f"Venue is not currently selectable: {stop.venue_id}")
    try:
        result = _domain_store.update_plan_stops(plan_id, [stop.model_dump() for stop in ordered])
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if not result:
        raise HTTPException(status_code=404, detail="Plan not found")
    return result


@app.get("/v1/rooms/{room_id}/plan")
def get_room_plan(room_id: str, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    room = _domain_store.get_room(room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    user_id = _request_user_id(authorization)
    if user_id not in room.get("members", []) and room.get("owner_id", "demo-user") != user_id:
        raise HTTPException(status_code=403, detail="You are not a member of this room")
    plan_id = room.get("plan_id")
    if not plan_id:
        raise HTTPException(status_code=404, detail="This room has no plan")
    plan = _domain_store.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="This room has no plan")
    return plan


@app.websocket("/v1/ws/rooms/{room_id}")
async def room_websocket(websocket: WebSocket, room_id: str):
    """Authoritative room snapshot channel with push and sync fallback."""
    room = _domain_store.get_room(room_id) if _domain_store.available else None
    if room is None:
        await websocket.close(code=4404)
        return
    user_id = (websocket.query_params.get("user_id") or "demo-user").strip()
    if user_id not in room.get("members", []) and room.get("owner_id", "demo-user") != user_id:
        await websocket.close(code=4403)
        return
    await websocket.accept()
    _room_sockets.setdefault(room_id, set()).add(websocket)
    try:
        await websocket.send_json(_room_snapshot(room_id))
        while True:
            message = await websocket.receive_json()
            if message.get("type") in {"sync", "ping"}:
                await websocket.send_json(_room_snapshot(room_id))
    except WebSocketDisconnect:
        return
    finally:
        _room_sockets.get(room_id, set()).discard(websocket)


@app.get("/v1/discovery")
def discovery() -> dict[str, Any]:
    items = store.public_venues(include_needs_review=True)
    if not items and os.getenv("SHUFFL_DEMO_MODE", "0") == "1":
        items = [{"name": venue["name"], "type": venue["type"], "area": venue["area"]} for venue in DEMO_VENUES]
    return {"items": items, "source": "demo" if os.getenv("SHUFFL_DEMO_MODE", "0") == "1" and not store.public_venues() else "published_venue_api", "version": "venue-dto-v1"}


@app.get("/v1/release")
def release_metadata() -> dict[str, Any]:
    """Expose the immutable MVP scope to clients and launch diagnostics."""
    scope = release_scope()
    # The catalogue lock is an operational setting persisted in MySQL. The
    # environment variable remains the bootstrap/default for fresh installs,
    # but the API contract must reflect the live database state after an admin
    # changes it from the dashboard.
    try:
        scope["venue_catalogue"]["locked"] = bool(
            store.summary().get("pipeline_locked", scope["venue_catalogue"]["locked"])
        )
    except Exception:
        # Keep the static release contract available while readiness reports the
        # underlying database failure separately.
        pass
    return scope


@app.get("/v1/venues")
def venues(query: str = "", city: str = "") -> dict[str, Any]:
    items = store.public_venues(query, city, include_needs_review=True)
    if not items and os.getenv("SHUFFL_DEMO_MODE", "0") == "1":
        items = discovery()["items"]
        if query:
            items = [item for item in items if query.lower() in item["name"].lower() or query.lower() in item["type"].lower() or query.lower() in item["area"].lower()]
    return {"city": city, "items": items}


@app.get("/v1/venues/stop-options")
def venue_stop_options(
    energy: float | None = Query(default=None, ge=0, le=100),
    crowd: float | None = Query(default=None, ge=0, le=100),
    conversation: float | None = Query(default=None, ge=0, le=100),
    food: float | None = Query(default=None, ge=0, le=100),
    scene: float | None = Query(default=None, ge=0, le=100),
    live_music: float | None = Query(default=None, ge=0, le=100),
    city: str = "",
    area: str = "",
    limit: int = Query(default=10, ge=1, le=20),
    include_live: bool = True,
) -> dict[str, Any]:
    """Return ranked published venues with optional request-scoped Google data."""
    target = {key: value for key, value in {"energy": energy, "crowd": crowd, "conversation": conversation, "food": food, "scene": scene, "live_music": live_music}.items() if value is not None}
    items = store.public_venues(city=city)
    if area:
        items = [item for item in items if area.lower() in str(item.get("area", "")).lower()]
    ranked = sorted(items, key=lambda item: _venue_fit(item, target))[:limit]
    result: list[dict[str, Any]] = []
    for item in ranked:
        row = {**item, "match_distance": _venue_fit(item, target), "hours_mode": "display_time_live"}
        if include_live and item.get("google_place_id"):
            try:
                row["live"] = fetch_for_display(item["google_place_id"])
            except GooglePlacesError:
                row["live"] = None
        result.append(row)
    return {"items": result, "count": len(result), "persisted": False, "live_source": "google_places_display_time" if include_live else "not_requested"}


@app.get("/v1/venues/{venue_id}")
def public_venue(venue_id: str) -> dict[str, Any]:
    """Return one published normalized venue; Google display fields stay live-only."""
    item = store.get_venue(venue_id)
    if not item or item.get("publication_status") not in {"PUBLISHED", "DRAFT"} or item.get("eligibility_status") not in {"AUTO_APPROVED", "PROVISIONAL", "NEEDS_REVIEW"} or item.get("verification_status") == "rejected":
        raise HTTPException(status_code=404, detail="Published venue not found")
    normalized = store.normalized_venue(venue_id)
    card = next((candidate for candidate in store.public_venues(include_needs_review=True) if candidate.get("id") == venue_id), None)
    return {"venue": card or {"id": venue_id, "name": item.get("display_name")}, "normalized": normalized, "google_place_id": item.get("google_place_id"), "google_lookup_url": item.get("google_lookup_url"), "live_fields": {"source": "google_places_display_time", "persisted": False}}


@app.get("/v1/venues/{venue_id}/live")
def public_live_venue(venue_id: str) -> dict[str, Any]:
    """Fetch current Google display fields without storing them."""
    item = store.get_venue(venue_id)
    if (
        not item
        or item.get("publication_status") not in {"PUBLISHED", "DRAFT"}
        or item.get("eligibility_status") not in {"AUTO_APPROVED", "PROVISIONAL", "NEEDS_REVIEW"}
        or item.get("verification_status") == "rejected"
        or not item.get("google_place_id")
    ):
        raise HTTPException(status_code=404, detail="Published venue or Google place_id not found")
    try:
        live = fetch_for_display(item["google_place_id"])
    except GooglePlacesError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"venue_id": venue_id, "google_live": live, "persisted": False}


def _venue_fit(item: dict[str, Any], target: dict[str, float]) -> float:
    scores = item.get("scores") or {}
    aliases = {"ENRG": "energy", "CROWD": "crowd", "TALK": "conversation", "MOVE": "movement", "GAMES": "games", "FOOD": "food", "LIVE": "live_music", "POL": "politics", "SCEN": "scene", "HERIT": "heritage"}
    gaps: list[float] = []
    for requested, value in target.items():
        key = aliases.get(requested.upper(), requested.lower())
        actual = scores.get(key)
        if isinstance(value, (int, float)) and isinstance(actual, (int, float)):
            gaps.append(abs(float(value) - float(actual)))
    return round(sum(gaps) / len(gaps), 2) if gaps else 50.0


@app.get("/v1/search")
def search(q: str, kind: str = "all") -> dict[str, Any]:
    items = venues(q)["items"]
    if kind == "rooms":
        if not _domain_store.available:
            raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
        with _domain_store.engine.connect() as conn:
            ids = conn.execute(text("SELECT id FROM rooms WHERE LOWER(title) LIKE :query ORDER BY id DESC"), {"query": f"%{q.lower()}%"}).all()
        items = [_domain_store.get_room(str(row[0])) for row in ids]
    return {"query": q, "kind": kind, "items": items}


@app.post("/v1/rooms")
def create_room(payload: RoomRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    if payload.visibility not in {"private", "friends", "public"}:
        raise HTTPException(status_code=422, detail="visibility must be private, friends, or public")
    owner_id = _request_user_id(authorization)
    now = datetime.now(timezone.utc).isoformat()
    room = {"id": new_id("room"), "owner_id": owner_id, "title": payload.title.strip(), "members": list(dict.fromkeys([owner_id, *payload.member_ids])), "visibility": payload.visibility, "status": "draft", "plan_id": None, "chemistry": {}, "join_requests": [], "created_at": now, "updated_at": now}
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    return _domain_store.create_room(room)


@app.get("/v1/rooms")
def rooms(status: str | None = None, visibility: str | None = None) -> dict[str, Any]:
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    with _domain_store.engine.connect() as conn:
        clauses = ["1=1"]; params: dict[str, Any] = {}
        if status: clauses.append("status=:status"); params["status"] = status
        if visibility: clauses.append("visibility=:visibility"); params["visibility"] = visibility
        rows = conn.execute(text(f"SELECT id FROM rooms WHERE {' AND '.join(clauses)} ORDER BY id DESC"), params).all()
    items = [_domain_store.get_room(str(row[0])) for row in rows]
    public_items = []
    for room in items:
        item = {key: value for key, value in room.items() if key != "join_requests"}
        plan = _domain_store.get_plan(room.get("plan_id")) if room else None
        if room["status"] == "hosted" and plan:
            item["stop_types"] = plan.get("venue_types", [])
            selected_stops = plan.get("selected_stops", [])
            item["selected_stops"] = selected_stops
            item["stop_count"] = len(selected_stops) or plan.get("stops", 0)
        public_items.append(item)
    return {"items": public_items}


@app.patch("/v1/rooms/{room_id}")
def update_room(room_id: str, payload: RoomUpdate, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    room = _domain_store.get_room(room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    if room.get("owner_id", "demo-user") != _request_user_id(authorization):
        raise HTTPException(status_code=403, detail="Only the room host can edit this room")
    changes: dict[str, Any] = {}
    if payload.title is not None:
        changes["title"] = payload.title
    if payload.visibility is not None:
        if payload.visibility not in {"private", "friends", "public"}:
            raise HTTPException(status_code=422, detail="invalid visibility")
        if room["status"] == "hosted":
            raise HTTPException(status_code=409, detail="Visibility is frozen after hosting")
        changes["visibility"] = payload.visibility
    result = _domain_store.update_room(room_id, **changes)
    _queue_room_event(room_id, "room_updated")
    return result or room


@app.post("/v1/rooms/{room_id}/host")
def host_room(room_id: str, plan_id: str, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    room = _domain_store.get_room(room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    user_id = _request_user_id(authorization)
    if room.get("owner_id", "demo-user") != user_id:
        raise HTTPException(status_code=403, detail="Only the room host can publish this room")
    plan = _domain_store.get_plan(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    if plan.get("user_id", "demo-user") != user_id:
        raise HTTPException(status_code=403, detail="You do not own this plan")
    if room["status"] == "hosted":
        raise HTTPException(status_code=409, detail="Room is already hosted")
    _domain_store.lock_plan(plan_id)
    room = _domain_store.update_room(room_id, plan_id=plan_id, visibility="public", status="hosted", chemistry=plan.get("chemistry", {})) or room
    with _domain_store.engine.begin() as conn:
        metadata = json.dumps({**room, "plan_id": plan_id, "chemistry": plan.get("chemistry", {})})
        conn.execute(text("UPDATE rooms SET metadata_json=:metadata WHERE id=:id"), {"id": room_id, "metadata": metadata})
    room = _domain_store.get_room(room_id) or room
    _queue_room_event(room_id, "room_hosted", plan_id=plan_id)
    return room


@app.post("/v1/rooms/join-eligibility")
def room_join_eligibility(payload: JoinEligibilityRequest) -> dict[str, Any]:
    room = _domain_store.get_room(payload.room_id) if _domain_store.available else None
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    if room["status"] != "hosted":
        raise HTTPException(status_code=409, detail="Room is not accepting requests")
    plan = _domain_store.get_plan(room.get("plan_id"))
    if not plan:
        raise HTTPException(status_code=409, detail="This room has no available frozen plan")
    return joiner_shape_fit(payload.scores, plan.get("venue_types", []), plan.get("stops", 0))


@app.post("/v1/rooms/join-requests")
def join_room(payload: JoinRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    room = _domain_store.get_room(payload.room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    if room["status"] != "hosted":
        raise HTTPException(status_code=409, detail="Room is not accepting requests")
    authenticated_user = _auth_user(authorization)
    member_id = str(authenticated_user["id"]) if authenticated_user else payload.member_id.strip()
    if not member_id:
        raise HTTPException(status_code=422, detail="member_id cannot be blank")
    if member_id in room["members"]:
        raise HTTPException(status_code=409, detail="Member is already in this room")
    plan = _domain_store.get_plan(room.get("plan_id"))
    if not plan:
        raise HTTPException(status_code=409, detail="This room has no available frozen plan")
    fit = joiner_shape_fit(payload.scores, plan.get("venue_types", []), plan.get("stops", 0))
    if not fit["eligible"]:
        raise HTTPException(status_code=409, detail={"code": "plan_shape_mismatch", "message": "This room's frozen plan is outside your current vibe fit", "reasons": fit["reasons"]})
    existing = next((item for item in _domain_store.join_requests(payload.room_id, "pending") if item["member_id"] == member_id), None)
    if existing:
        return existing
    request = {"id": new_id("join"), "room_id": payload.room_id, "member_id": member_id, "status": "pending", "note": payload.note.strip(), "fit": fit["eligible"], "fit_reasons": fit["reasons"], "created_at": datetime.now(timezone.utc).isoformat()}
    return _domain_store.add_join_request(request)


@app.get("/v1/rooms/{room_id}/join-requests")
def get_join_requests(room_id: str, status: str = "pending", authorization: str | None = Header(default=None)) -> dict[str, Any]:
    room = _domain_store.get_room(room_id) if _domain_store.available else None
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    if room.get("owner_id", "demo-user") != _request_user_id(authorization):
        raise HTTPException(status_code=403, detail="Only the room host can view join requests")
    if status not in {"pending", "accepted", "declined", "all"}:
        raise HTTPException(status_code=422, detail="invalid join request status")
    return {"items": _domain_store.join_requests(room_id, status)}


@app.post("/v1/rooms/{room_id}/join-requests/{request_id}/decision")
def decide_join(room_id: str, request_id: str, payload: JoinDecision, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    room = _domain_store.get_room(room_id) if _domain_store.available else None
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    if room.get("owner_id", "demo-user") != _request_user_id(authorization):
        raise HTTPException(status_code=403, detail="Only the room host can decide join requests")
    if payload.status not in {"accepted", "declined"}:
        raise HTTPException(status_code=422, detail="status must be accepted or declined")
    request = next((item for item in _domain_store.join_requests(room_id, "all") if item["id"] == request_id), None)
    if request is None:
        raise HTTPException(status_code=404, detail="Join request not found")
    if request["status"] != "pending":
        raise HTTPException(status_code=409, detail="Join request already resolved")
    updated = _domain_store.decide_join_request(request_id, payload.status)
    request = updated or request
    room = _domain_store.get_room(room_id) or room
    _record_notification(request["member_id"], "room_join_decision", {"title": "Room request updated", "body": f"Your request to join {room['title']} was {payload.status}.", "room_id": room_id, "member_id": request["member_id"]})
    _queue_room_event(room_id, "member_joined" if payload.status == "accepted" else "join_request_decided", member_id=request["member_id"], status=payload.status)
    return {"request": request, "room": room, "plan_frozen": True}


@app.post("/v1/capsules")
def create_capsule(payload: CapsuleRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    room = _domain_store.get_room(payload.room_id) if _domain_store.available else None
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    authenticated_user = _auth_user(authorization)
    user_id = _request_user_id(authorization)
    if authenticated_user and room.get("owner_id", "demo-user") != user_id and user_id not in room.get("members", []):
        raise HTTPException(status_code=403, detail="Only room members can create a capsule")
    if not _flags.get("capsules", False):
        raise HTTPException(status_code=403, detail="Capsules are disabled")
    members = list(dict.fromkeys(([user_id] if authenticated_user else []) + payload.member_ids))
    if authenticated_user and any(member_id not in room.get("members", []) for member_id in members):
        raise HTTPException(status_code=422, detail="Every capsule member must belong to the room")
    capsule = {"id": new_id("capsule"), "room_id": payload.room_id, "created_by": user_id, "members": members, "approvals": {member_id: False for member_id in members}, "status": "awaiting_approval", "created_at": datetime.now(timezone.utc).isoformat()}
    return _domain_store.create_capsule(capsule)


@app.get("/v1/capsules/{capsule_id}")
def get_capsule(capsule_id: str) -> dict[str, Any]:
    capsule = _domain_store.get_capsule(capsule_id) if _domain_store.available else None
    if capsule is None:
        raise HTTPException(status_code=404, detail="Capsule not found")
    return capsule


@app.post("/v1/rooms/{room_id}/invite")
def create_room_invite(room_id: str, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    room = _domain_store.get_room(room_id) if _domain_store.available else None
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    if room.get("owner_id", "demo-user") != _request_user_id(authorization):
        raise HTTPException(status_code=403, detail="Only the room host can create invites")
    if room["status"] != "hosted":
        raise HTTPException(status_code=409, detail="Host the room before creating an invite")
    token = secrets.token_urlsafe(12)
    invite = _domain_store.create_invite(room_id, _request_user_id(authorization), token, (datetime.now(timezone.utc) + __import__('datetime').timedelta(days=7)).isoformat())
    return {**invite, "invite_url": f"shuffl://join/{room_id}?token={token}"}


@app.post("/v1/rooms/join-by-invite")
def join_by_invite(payload: InviteJoinRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user_id = _request_user_id(authorization)
    room = _domain_store.room_for_invite(payload.invite_token) if _domain_store.available else None
    if room is None:
        raise HTTPException(status_code=404, detail="Invite is invalid or expired")
    if room.get("status") != "hosted":
        raise HTTPException(status_code=409, detail="This room is not accepting members")
    room = _domain_store.use_invite(payload.invite_token, user_id) or room
    _queue_room_event(room["id"], "member_joined", member_id=user_id)
    return {key: value for key, value in room.items() if key != "join_requests"}


@app.post("/v1/capsules/{capsule_id}/approvals")
def approve_capsule(capsule_id: str, payload: CapsuleApproval, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    capsule = _domain_store.get_capsule(capsule_id) if _domain_store.available else None
    if capsule is None:
        raise HTTPException(status_code=404, detail="Capsule not found")
    authenticated_user = _auth_user(authorization)
    member_id = str(authenticated_user["id"]) if authenticated_user else payload.member_id
    if member_id not in capsule.get("approvals", {}):
        raise HTTPException(status_code=404, detail="Member is not in this capsule")
    capsule = _domain_store.approve_capsule(capsule_id, member_id, payload.approved) or capsule
    capsule_room = _domain_store.get_room(capsule.get("room_id")) if _domain_store.available else None
    notification_target = (capsule_room or {}).get("owner_id", member_id)
    _record_notification(notification_target, "capsule_approval", {"title": "Capsule approval updated", "body": f"{member_id} {'approved' if payload.approved else 'declined'} the capsule."})
    return capsule


@app.get("/v1/conversations")
def conversations(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    user_id = _request_user_id(authorization)
    return {"items": [_domain_store.conversation_summary(conversation_id, user_id) for conversation_id in _domain_store.conversation_ids(user_id)]}


@app.post("/v1/conversations/messages")
def send_message(payload: MessageRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    sender_id = _request_user_id(authorization)
    if not _domain_store.conversation_member(payload.conversation_id, sender_id):
        raise HTTPException(status_code=403, detail="You are not a member of this conversation")
    message_id = new_id("message")
    try:
        message = _domain_store.add_message(message_id=message_id, conversation_id=payload.conversation_id, sender_id=sender_id, body=payload.body)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    message.update({"status": "sent", "read": True})
    room_id, members = _domain_store.conversation_room_members(payload.conversation_id)
    if room_id:
        for member_id in members:
            if member_id != sender_id:
                _record_notification(member_id, "message_received", {"title": "New room message", "body": payload.body, "room_id": room_id, "conversation_id": payload.conversation_id})
        _queue_room_event(room_id, "message_received", message=message)
    return message


@app.post("/v1/conversations/{conversation_id}/read")
def mark_conversation_read(conversation_id: str, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    user_id = _request_user_id(authorization)
    if not _domain_store.conversation_member(conversation_id, user_id):
        raise HTTPException(status_code=403, detail="You are not a member of this conversation")
    count = _domain_store.mark_conversation_read(conversation_id, user_id)
    return {"conversation_id": conversation_id, "marked_read": count}


@app.get("/v1/notifications")
def notifications(unread_only: bool = False, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    user_id = _request_user_id(authorization)
    return {"items": _domain_store.list_notifications(user_id, unread_only)}


@app.post("/v1/notifications/{notification_id}/read")
def mark_notification_read(notification_id: str, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    user_id = _request_user_id(authorization)
    if not _domain_store.mark_notification_read(notification_id, user_id):
        raise HTTPException(status_code=404, detail="Notification not found")
    return next(item for item in _domain_store.list_notifications(user_id) if item["id"] == notification_id)


@app.post("/v1/reports")
def report(payload: ReportRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    target_id = payload.target_id.strip()
    reason = payload.reason.strip()
    if not target_id or not reason:
        raise HTTPException(status_code=422, detail="target_id and reason cannot be blank")
    if target_id == "demo-user":
        raise HTTPException(status_code=422, detail="You cannot report your own account")
    reporter_id = _request_user_id(authorization)
    record = _domain_store.add_report(report_id=new_id("report"), reporter_id=reporter_id, target_id=target_id, reason=reason) if _domain_store.available else {"id": new_id("report"), "reporter_id": reporter_id, "target_id": target_id, "reason": reason, "status": "received", "created_at": datetime.now(timezone.utc).isoformat()}
    return record


@app.get("/v1/blocks")
def blocked_users(authorization: str | None = Header(default=None)) -> dict[str, list[str]]:
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    return {"items": _domain_store.blocked_users(_request_user_id(authorization))}


@app.post("/v1/blocks")
def block_user(payload: BlockRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    target_id = payload.target_id.strip()
    if not target_id:
        raise HTTPException(status_code=422, detail="target_id cannot be blank")
    user_id = _request_user_id(authorization)
    if target_id == user_id:
        raise HTTPException(status_code=422, detail="You cannot block your own account")
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    _domain_store.block_user(user_id, target_id)
    return {"target_id": target_id, "blocked": True}


@app.delete("/v1/blocks/{target_id}")
def unblock_user(target_id: str, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    target_id = target_id.strip()
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    _domain_store.unblock_user(_request_user_id(authorization), target_id)
    return {"target_id": target_id, "blocked": False}


@app.get("/v1/plans/{plan_id}/location-consent")
def get_plan_location_consent(plan_id: str, authorization: str | None = Header(default=None)) -> dict[str, bool]:
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    plan = _domain_store.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    user_id = _request_user_id(authorization)
    if plan.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="You do not own this plan")
    permitted = _domain_store.privacy_get(user_id)["location_sharing"] if _domain_store.available else False
    consent = _domain_store.location_consent(plan_id, user_id) if _domain_store.available else _plan_location_consents.get(plan_id, False)
    return {"approved": bool(permitted and consent)}


@app.post("/v1/plans/{plan_id}/location-consent")
def set_plan_location_consent(plan_id: str, payload: PlanLocationConsent, authorization: str | None = Header(default=None)) -> dict[str, bool]:
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    plan = _domain_store.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    user_id = _request_user_id(authorization)
    if plan.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="You do not own this plan")
    permitted = _domain_store.privacy_get(user_id)["location_sharing"] if _domain_store.available else False
    if payload.approved and not permitted:
        raise HTTPException(status_code=409, detail="Enable per-plan location sharing in privacy settings first")
    if _domain_store.available:
        _domain_store.location_consent(plan_id, user_id, payload.approved)
    return {"approved": payload.approved}


@app.post("/v1/privacy")
def update_privacy(payload: PrivacyUpdate, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    invalid = {key: value for key, value in payload.visibility.items() if value not in {"everyone", "friends", "nobody"}}
    if invalid:
        raise HTTPException(status_code=422, detail="visibility values must be everyone, friends, or nobody")
    user_id = _request_user_id(authorization)
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    settings = _domain_store.privacy_update(user_id, payload.model_dump())
    return {"saved": True, "settings": settings}


@app.get("/v1/privacy")
def get_privacy(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    return _domain_store.privacy_get(_request_user_id(authorization))


@app.get("/v1/feature-flags")
def feature_flags() -> dict[str, bool]:
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    return _domain_store.feature_flags()


@app.post("/v1/feature-flags")
def update_feature_flag(payload: FeatureFlagUpdate, authorization: str | None = Header(default=None)) -> dict[str, bool]:
    if not re.fullmatch(r"[a-z][a-z0-9_-]{1,79}", payload.name):
        raise HTTPException(status_code=422, detail="Invalid feature flag name")
    if not _domain_store.available:
        raise HTTPException(status_code=503, detail="Canonical MySQL domain storage is unavailable")
    return _domain_store.set_feature_flag(payload.name, payload.enabled, _request_user_id(authorization))

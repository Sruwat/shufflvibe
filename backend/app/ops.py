"""Operational safeguards shared by the API and maintenance commands."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import os
from threading import Lock
import time
from typing import Any

from sqlalchemy import text


PLACEHOLDERS = {
    "change-this-in-production",
    "change-super-admin",
    "change-admin",
    "change-editor",
    "change-viewer",
    "paste_your_service_api_key_here",
    "your_google_places_api_key_here",
    "your_gemini_api_key_here",
    "your_google_oauth_client_id.apps.googleusercontent.com",
}
MIN_PRODUCTION_SECRET_LENGTH = 16


def _truthy(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def allowed_origins() -> list[str]:
    raw = os.getenv("CORS_ALLOWED_ORIGINS", "").strip()
    if raw:
        return [item.strip() for item in raw.split(",") if item.strip()]
    if os.getenv("APP_ENV", "development").lower() in {"development", "test"}:
        return ["*"]
    return []


def validate_startup_config() -> dict[str, Any]:
    """Return actionable configuration errors without exposing secret values."""
    env = os.getenv("APP_ENV", "development").strip().lower() or "development"
    errors: list[str] = []
    warnings: list[str] = []
    db_url = os.getenv("DATABASE_URL", "").strip()
    admin_token = os.getenv("ADMIN_API_TOKEN", "").strip()
    role_tokens = os.getenv("ADMIN_ROLE_TOKENS", "").strip()
    google_key = os.getenv("GOOGLE_PLACES_API_KEY", "").strip() or os.getenv("GOOGLE_MAPS_API_KEY", "").strip()
    google_oauth_client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID", "").strip()

    # The locked MVP catalogue is intended to run from the shared MySQL
    # database. Keep local SQLite available for development unless the project
    # explicitly opts into the MySQL-only launch gate.
    if _truthy("SHUFFL_REQUIRE_MYSQL") and (not db_url or db_url.startswith("sqlite")):
        errors.append("SHUFFL_REQUIRE_MYSQL is enabled but DATABASE_URL does not point to MySQL")

    if env in {"production", "staging"}:
        if not db_url or db_url.startswith("sqlite"):
            errors.append("DATABASE_URL must point to MySQL/PostgreSQL outside development")
        if not admin_token and not role_tokens:
            errors.append("ADMIN_API_TOKEN or ADMIN_ROLE_TOKENS is required")
        if admin_token.lower() in PLACEHOLDERS or "change-this" in admin_token.lower():
            errors.append("ADMIN_API_TOKEN is still a placeholder")
        if admin_token and len(admin_token) < MIN_PRODUCTION_SECRET_LENGTH:
            errors.append("ADMIN_API_TOKEN must be at least 16 characters")
        if role_tokens:
            for pair in role_tokens.split(","):
                if "=" not in pair or len(pair.split("=", 1)[1].strip()) < MIN_PRODUCTION_SECRET_LENGTH:
                    errors.append("ADMIN_ROLE_TOKENS contains a missing or weak secret")
                    break
        if not google_key or google_key.lower() in PLACEHOLDERS:
            errors.append("GOOGLE_PLACES_API_KEY is required for live venue enrichment")
        if not google_oauth_client_id or google_oauth_client_id.lower() in PLACEHOLDERS:
            errors.append("GOOGLE_OAUTH_CLIENT_ID is required for Google login")
        if not allowed_origins():
            errors.append("CORS_ALLOWED_ORIGINS must be configured")
        elif "*" in allowed_origins():
            errors.append("CORS_ALLOWED_ORIGINS cannot contain * outside development")
    else:
        if not db_url:
            warnings.append("DATABASE_URL is unset; local SQLite fallback is active")
        if not google_key:
            warnings.append("Google Places key is unset; live enrichment will be unavailable")

    return {
        "environment": env,
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "database_configured": bool(db_url),
        "mysql_required": _truthy("SHUFFL_REQUIRE_MYSQL"),
        "cors_origins_configured": bool(allowed_origins()),
    }


def database_readiness(engine: Any) -> dict[str, Any]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as exc:  # pragma: no cover - driver-specific failure text
        return {"status": "error", "error": str(exc)[:240]}


@dataclass
class SlidingWindowLimiter:
    limit: int
    window_seconds: int = 60

    def __post_init__(self) -> None:
        self._events: dict[str, deque[float]] = {}
        self._lock = Lock()

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        with self._lock:
            events = self._events.setdefault(key, deque())
            cutoff = now - self.window_seconds
            while events and events[0] <= cutoff:
                events.popleft()
            if len(events) >= max(1, self.limit):
                return False
            events.append(now)
            if len(self._events) > 5000:
                self._events = {k: v for k, v in self._events.items() if v and v[-1] > cutoff}
            return True


def env_int(name: str, default: int) -> int:
    try:
        return max(1, int(os.getenv(name, str(default))))
    except ValueError:
        return default

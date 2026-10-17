"""Durable password/Google identity and session storage."""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import Engine, text


class AuthStore:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.available = True
        try:
            self.ensure_schema()
        except Exception:
            self.available = False

    def ensure_schema(self) -> None:
        with self.engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS auth_users (
                    id VARCHAR(180) PRIMARY KEY,
                    email VARCHAR(320) UNIQUE NOT NULL,
                    name VARCHAR(120) NOT NULL DEFAULT '',
                    password_hash TEXT,
                    provider VARCHAR(40) NOT NULL DEFAULT 'password',
                    provider_subject VARCHAR(255),
                    created_at VARCHAR(40) NOT NULL,
                    status VARCHAR(40) NOT NULL DEFAULT 'active',
                    UNIQUE (provider, provider_subject)
                )
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS auth_sessions (
                    token_hash VARCHAR(64) PRIMARY KEY,
                    user_id VARCHAR(180) NOT NULL,
                    issued_at VARCHAR(40) NOT NULL,
                    revoked_at VARCHAR(40),
                    token_kind VARCHAR(20) NOT NULL DEFAULT 'access',
                    expires_at VARCHAR(40) NOT NULL
                )
            """))
            # Existing installations created before token rotation need a
            # non-destructive schema upgrade.  MySQL and SQLite both accept
            # these ALTER statements when the column is missing.
            for statement in (
                "ALTER TABLE auth_users ADD COLUMN status VARCHAR(40) NOT NULL DEFAULT 'active'",
                "ALTER TABLE auth_sessions ADD COLUMN token_kind VARCHAR(20) NOT NULL DEFAULT 'access'",
                "ALTER TABLE auth_sessions ADD COLUMN expires_at VARCHAR(40)",
            ):
                try:
                    conn.execute(text(statement))
                except Exception:
                    pass
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS auth_verification_tokens (
                    token_hash VARCHAR(64) PRIMARY KEY,
                    user_id VARCHAR(180) NOT NULL,
                    created_at VARCHAR(40) NOT NULL,
                    expires_at VARCHAR(40) NOT NULL,
                    used_at VARCHAR(40)
                )
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS auth_password_reset_tokens (
                    token_hash VARCHAR(64) PRIMARY KEY,
                    user_id VARCHAR(180) NOT NULL,
                    created_at VARCHAR(40) NOT NULL,
                    expires_at VARCHAR(40) NOT NULL,
                    used_at VARCHAR(40)
                )
            """))

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def find_email(self, email: str) -> dict[str, Any] | None:
        if not self.available:
            return None
        with self.engine.connect() as conn:
            row = conn.execute(text("SELECT * FROM auth_users WHERE email=:email"), {"email": email}).mappings().first()
        return dict(row) if row else None

    def find_google_subject(self, subject: str) -> dict[str, Any] | None:
        if not self.available:
            return None
        with self.engine.connect() as conn:
            row = conn.execute(text("SELECT * FROM auth_users WHERE provider='google' AND provider_subject=:subject"), {"subject": subject}).mappings().first()
        return dict(row) if row else None

    def create_user(self, *, user_id: str, email: str, name: str, password_hash: str | None, provider: str, provider_subject: str | None) -> dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        with self.engine.begin() as conn:
            conn.execute(text("INSERT INTO auth_users(id,email,name,password_hash,provider,provider_subject,created_at) VALUES (:id,:email,:name,:password_hash,:provider,:subject,:created_at)"), {"id": user_id, "email": email, "name": name, "password_hash": password_hash, "provider": provider, "subject": provider_subject, "created_at": now})
        return {"id": user_id, "email": email, "name": name, "password_hash": password_hash, "provider": provider, "provider_subject": provider_subject, "created_at": now}

    def update_google_identity(self, user_id: str, *, email: str, name: str, subject: str) -> dict[str, Any]:
        with self.engine.begin() as conn:
            conn.execute(text("UPDATE auth_users SET email=:email,name=:name,provider='google',provider_subject=:subject WHERE id=:id"), {"id": user_id, "email": email, "name": name, "subject": subject})
        return self.find_email(email) or {"id": user_id, "email": email, "name": name, "provider": "google", "provider_subject": subject}

    def issue_session(self, user_id: str, *, kind: str = "access", ttl_seconds: int | None = None) -> str:
        token = secrets.token_urlsafe(32)
        ttl = ttl_seconds if ttl_seconds is not None else (900 if kind == "access" else 60 * 60 * 24 * 30)
        now = datetime.now(timezone.utc)
        with self.engine.begin() as conn:
            conn.execute(text("INSERT INTO auth_sessions(token_hash,user_id,issued_at,token_kind,expires_at) VALUES (:token_hash,:user_id,:issued_at,:token_kind,:expires_at)"), {"token_hash": self._hash_token(token), "user_id": user_id, "issued_at": now.isoformat(), "token_kind": kind, "expires_at": (now + timedelta(seconds=ttl)).isoformat()})
        return token

    def issue_refresh(self, user_id: str) -> str:
        return self.issue_session(user_id, kind="refresh")

    def user_for_token(self, token: str) -> dict[str, Any] | None:
        with self.engine.connect() as conn:
            row = conn.execute(text("SELECT u.*, s.token_kind, s.expires_at FROM auth_sessions s JOIN auth_users u ON u.id=s.user_id WHERE s.token_hash=:token_hash AND s.revoked_at IS NULL AND COALESCE(u.status,'active')='active'"), {"token_hash": self._hash_token(token)}).mappings().first()
        if row:
            expiry = row.get("expires_at")
            try:
                if expiry and datetime.fromisoformat(str(expiry)) <= datetime.now(timezone.utc):
                    self.revoke(token)
                    return None
            except ValueError:
                return None
        return dict(row) if row else None

    def revoke(self, token: str) -> None:
        with self.engine.begin() as conn:
            conn.execute(text("UPDATE auth_sessions SET revoked_at=:revoked_at WHERE token_hash=:token_hash"), {"token_hash": self._hash_token(token), "revoked_at": datetime.now(timezone.utc).isoformat()})

    def revoke_user_sessions(self, user_id: str) -> None:
        with self.engine.begin() as conn:
            conn.execute(text("UPDATE auth_sessions SET revoked_at=:revoked_at WHERE user_id=:user_id AND revoked_at IS NULL"), {"user_id": user_id, "revoked_at": datetime.now(timezone.utc).isoformat()})

    def create_one_time_token(self, table: str, user_id: str, ttl_seconds: int) -> str:
        if table not in {"auth_verification_tokens", "auth_password_reset_tokens"}:
            raise ValueError("unsupported auth token table")
        token = secrets.token_urlsafe(40)
        now = datetime.now(timezone.utc)
        with self.engine.begin() as conn:
            conn.execute(text(f"INSERT INTO {table}(token_hash,user_id,created_at,expires_at) VALUES (:token_hash,:user_id,:created_at,:expires_at)"), {"token_hash": self._hash_token(token), "user_id": user_id, "created_at": now.isoformat(), "expires_at": (now + timedelta(seconds=ttl_seconds)).isoformat()})
        return token

    def consume_one_time_token(self, table: str, token: str) -> str | None:
        if table not in {"auth_verification_tokens", "auth_password_reset_tokens"}:
            raise ValueError("unsupported auth token table")
        token_hash = self._hash_token(token)
        with self.engine.begin() as conn:
            row = conn.execute(text(f"SELECT user_id,expires_at,used_at FROM {table} WHERE token_hash=:token_hash"), {"token_hash": token_hash}).mappings().first()
            if not row or row.get("used_at"):
                return None
            try:
                if datetime.fromisoformat(str(row["expires_at"])) <= datetime.now(timezone.utc):
                    return None
            except (KeyError, ValueError):
                return None
            conn.execute(text(f"UPDATE {table} SET used_at=:used_at WHERE token_hash=:token_hash"), {"token_hash": token_hash, "used_at": datetime.now(timezone.utc).isoformat()})
            return str(row["user_id"])

    def update_password(self, user_id: str, password_hash: str) -> None:
        with self.engine.begin() as conn:
            conn.execute(text("UPDATE auth_users SET password_hash=:password_hash, provider='password', provider_subject=NULL WHERE id=:id"), {"id": user_id, "password_hash": password_hash})

    def mark_verified(self, user_id: str) -> None:
        # The column is added lazily so old local DBs remain usable.
        with self.engine.begin() as conn:
            try:
                conn.execute(text("ALTER TABLE auth_users ADD COLUMN email_verified INTEGER NOT NULL DEFAULT 0"))
            except Exception:
                pass
            conn.execute(text("UPDATE auth_users SET email_verified=1 WHERE id=:id"), {"id": user_id})

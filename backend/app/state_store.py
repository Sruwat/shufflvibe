"""Small durable runtime-state store used while domain migrations are phased in."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Engine, text


class RuntimeStateStore:
    """Persist app aggregates across API restarts in the configured database."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.schema_error: str | None = None
        try:
            self.ensure_schema()
        except Exception as exc:  # readiness endpoint can still explain the outage
            self.schema_error = str(exc)[:240]

    def ensure_schema(self) -> None:
        with self.engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS app_runtime_state (
                    state_key VARCHAR(120) PRIMARY KEY,
                    data_json TEXT NOT NULL,
                    updated_at VARCHAR(40) NOT NULL
                )
            """))

    def load(self, key: str) -> Any | None:
        with self.engine.connect() as conn:
            raw = conn.execute(
                text("SELECT data_json FROM app_runtime_state WHERE state_key=:key"),
                {"key": key},
            ).scalar()
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except (TypeError, ValueError):
            return None

    def save(self, key: str, value: Any) -> None:
        payload = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        now = datetime.now(timezone.utc).isoformat()
        with self.engine.begin() as conn:
            exists = conn.execute(
                text("SELECT 1 FROM app_runtime_state WHERE state_key=:key"),
                {"key": key},
            ).first()
            if exists:
                conn.execute(
                    text("UPDATE app_runtime_state SET data_json=:data, updated_at=:updated WHERE state_key=:key"),
                    {"key": key, "data": payload, "updated": now},
                )
            else:
                conn.execute(
                    text("INSERT INTO app_runtime_state(state_key, data_json, updated_at) VALUES (:key, :data, :updated)"),
                    {"key": key, "data": payload, "updated": now},
                )


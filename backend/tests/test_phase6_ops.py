from backend.app.ops import SlidingWindowLimiter, validate_startup_config
from backend.tools.backup_database import TABLES


def test_rate_limiter_blocks_only_after_limit():
    limiter = SlidingWindowLimiter(limit=2, window_seconds=60)
    assert limiter.allow("client")
    assert limiter.allow("client")
    assert not limiter.allow("client")
    assert limiter.allow("another-client")


def test_development_config_is_actionable(monkeypatch):
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("GOOGLE_PLACES_API_KEY", raising=False)
    result = validate_startup_config()
    assert result["ok"] is True
    assert result["warnings"]


def test_production_config_rejects_placeholders(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///not-production.db")
    monkeypatch.setenv("ADMIN_API_TOKEN", "change-this-in-production")
    monkeypatch.setenv("GOOGLE_PLACES_API_KEY", "your_google_places_api_key_here")
    monkeypatch.delenv("ADMIN_ROLE_TOKENS", raising=False)
    monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)
    result = validate_startup_config()
    assert result["ok"] is False
    assert len(result["errors"]) >= 4


def test_production_config_rejects_weak_secret_and_wildcard_cors(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", "mysql+pymysql://user:password@db/shuffl")
    monkeypatch.setenv("ADMIN_API_TOKEN", "short")
    monkeypatch.setenv("GOOGLE_PLACES_API_KEY", "real-google-key")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "*")
    result = validate_startup_config()
    assert result["ok"] is False
    assert any("16 characters" in error for error in result["errors"])
    assert any("cannot contain" in error for error in result["errors"])


def test_locked_mvp_can_require_mysql_without_changing_local_default(monkeypatch):
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("SHUFFL_REQUIRE_MYSQL", "1")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    result = validate_startup_config()
    assert result["ok"] is False
    assert result["mysql_required"] is True
    assert any("DATABASE_URL" in error for error in result["errors"])


def test_backup_uses_canonical_runtime_table_names():
    assert "venue_pipeline_runs" in TABLES
    assert "venue_change_history" in TABLES
    assert "pipeline_runs" not in TABLES
    assert "venue_history" not in TABLES

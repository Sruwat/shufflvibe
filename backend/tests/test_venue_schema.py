from sqlalchemy import create_engine, inspect, text

from app.admin_store import store
from app.venue_schema import ensure_venue_schema, sync_normalized_venue


def test_canonical_venue_tables_exist_in_bootstrap_database():
    names = set(inspect(store.engine).get_table_names())
    assert {
        "admin_venues",
        "venue_identity",
        "venue_scores",
        "venue_tags",
        "venue_sources",
        "venue_time_slots",
        "venue_metros",
    }.issubset(names)


def test_google_display_only_fields_are_not_in_canonical_identity_table():
    columns = {column["name"] for column in inspect(store.engine).get_columns("venue_identity")}
    assert "google_rating" not in columns
    assert "google_reviews" not in columns
    assert "opening_hours" not in columns
    assert "latitude" not in columns
    assert "longitude" not in columns


def test_normalized_sync_keeps_google_display_data_out_of_durable_tables():
    engine = create_engine("sqlite:///:memory:", future=True)
    with engine.begin() as conn:
        ensure_venue_schema(conn)
        sync_normalized_venue(conn, {
            "venue_id": "venue:test",
            "discovered_type": "bar",
            "google_rating": 4.8,
            "google_reviews": [{"text": "live only"}],
            "venue_identity": [{"official_name": "Test Bar", "official_url": "https://example.com"}],
            "venue_scores": [{"factor": "energy", "score": 80}],
            "venue_tags": [{"tag": "late-night", "tag_family": "scene"}],
        }, "2026-01-01T00:00:00Z")
        row = conn.execute(text("SELECT official_name, venue_type FROM venue_identity WHERE venue_id='venue:test'")).first()
        assert tuple(row) == ("Test Bar", "bar")
        assert conn.execute(text("SELECT COUNT(*) FROM venue_scores WHERE venue_id='venue:test'")).scalar() == 1
        columns = {column["name"] for column in inspect(conn).get_columns("venue_identity")}
        assert "google_rating" not in columns


def test_normalized_sync_repairs_missing_admitted_tags_with_category_only():
    engine = create_engine("sqlite:///:memory:", future=True)
    with engine.begin() as conn:
        ensure_venue_schema(conn)
        sync_normalized_venue(conn, {
            "venue_id": "venue:admitted-no-tags",
            "discovered_type": "pub",
            "admission_decision": "Admitted",
            "google_reviews": [{"text": "must not be stored"}],
        }, "2026-01-01T00:00:00Z")
        row = conn.execute(text("SELECT tag, tag_type, source FROM venue_tags WHERE venue_id='venue:admitted-no-tags'")).first()
        assert tuple(row) == ("pub", "category", "remediation")

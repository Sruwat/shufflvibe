from sqlalchemy import create_engine, text

from backend.app.launch_audit import build_launch_audit
from backend.app.venue_schema import ensure_venue_schema


def _engine():
    engine = create_engine("sqlite:///:memory:", future=True)
    with engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE admin_venues (
              venue_id VARCHAR(180) PRIMARY KEY, google_place_id VARCHAR(180),
              publication_status VARCHAR(40), admission_status VARCHAR(40),
              eligibility_status VARCHAR(40), verification_status VARCHAR(40), data_json TEXT
            )
        """))
        ensure_venue_schema(connection)
    return engine


def test_launch_audit_accepts_complete_admitted_record():
    engine = _engine()
    with engine.begin() as connection:
        connection.execute(text("INSERT INTO admin_venues VALUES ('v1','p1','PUBLISHED','Admitted','AUTO_APPROVED','verified','{}')"))
        connection.execute(text("INSERT INTO venue_identity VALUES ('v1','Example','bar','','','','','','[]','unknown','unknown','verified',2020,'high',NULL,NULL,'now','now')"))
        for index in range(5):
            connection.execute(text("INSERT INTO venue_scores VALUES (:id,'v1',:factor,70,'deterministic','{}','v1','now','now')"), {"id": f"s{index}", "factor": f"factor{index}"})
        connection.execute(text("INSERT INTO venue_sources VALUES ('src1','v1','name','official_website','https://example.com','observed','high','{}','now','now')"))
    report = build_launch_audit(engine)
    assert report["ready_for_launch"] is True


def test_launch_audit_rejects_google_live_payload():
    engine = _engine()
    with engine.begin() as connection:
        connection.execute(text("INSERT INTO admin_venues VALUES ('v1','p1','PUBLISHED','Admitted','AUTO_APPROVED','verified',:payload)"), {"payload": '{"openingHours": {}}'})
    report = build_launch_audit(engine)
    assert report["ready_for_launch"] is False
    assert "live_google_fields_present_in_persistent_payload" in report["hard_failures"]


def test_launch_audit_rejects_published_record_not_publicly_eligible():
    engine = _engine()
    with engine.begin() as connection:
        connection.execute(text("INSERT INTO admin_venues VALUES ('v1','p1','PUBLISHED','Admitted','NEEDS_REVIEW','verified','{}')"))
    report = build_launch_audit(engine)
    assert report["ready_for_launch"] is False
    assert "published_venue_is_not_publicly_eligible" in report["hard_failures"]


def test_launch_audit_rejects_out_of_range_score():
    engine = _engine()
    with engine.begin() as connection:
        connection.execute(text("INSERT INTO admin_venues VALUES ('v1','p1','PUBLISHED','Admitted','AUTO_APPROVED','verified','{}')"))
        connection.execute(text("INSERT INTO venue_scores VALUES ('s1','v1','energy',101,'deterministic','{}','v1','now','now')"))
    report = build_launch_audit(engine)
    assert report["ready_for_launch"] is False
    assert "admitted_venue_has_invalid_scores" in report["hard_failures"]

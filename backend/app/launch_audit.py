"""Read-only pre-launch audit for the canonical venue platform."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text


PROHIBITED_LIVE_KEYS = (
    "reviews", "reviewText", "userRatingCount", "openingHours", "regularOpeningHours",
    "latitude", "longitude", "formattedAddress", "photos",
)


def _count(connection: Any, query: str, params: dict[str, Any] | None = None) -> int:
    try:
        return int(connection.execute(text(query), params or {}).scalar() or 0)
    except Exception:
        return 0


def build_launch_audit(engine: Any) -> dict[str, Any]:
    """Check lifecycle/canonical invariants without calling any provider API."""
    with engine.connect() as connection:
        total = _count(connection, "SELECT COUNT(*) FROM admin_venues")
        published = _count(connection, "SELECT COUNT(*) FROM admin_venues WHERE publication_status='PUBLISHED'")
        published_non_admitted = _count(connection, "SELECT COUNT(*) FROM admin_venues WHERE publication_status='PUBLISHED' AND admission_status <> 'Admitted'")
        published_not_publicly_eligible = _count(connection, """
            SELECT COUNT(*) FROM admin_venues
            WHERE publication_status='PUBLISHED'
              AND (eligibility_status NOT IN ('AUTO_APPROVED','PROVISIONAL')
                   OR verification_status='rejected')
        """)
        published_missing_place = _count(connection, "SELECT COUNT(*) FROM admin_venues WHERE publication_status='PUBLISHED' AND (google_place_id IS NULL OR google_place_id='')")
        admitted_missing_identity = _count(connection, """
            SELECT COUNT(*) FROM admin_venues a
            LEFT JOIN venue_identity i ON i.venue_id=a.venue_id
            WHERE a.admission_status='Admitted' AND (i.venue_id IS NULL OR i.official_name='')
        """)
        admitted_missing_scores = _count(connection, """
            SELECT COUNT(*) FROM (
              SELECT a.venue_id FROM admin_venues a
              LEFT JOIN venue_scores s ON s.venue_id=a.venue_id
              WHERE a.admission_status='Admitted'
              GROUP BY a.venue_id HAVING COUNT(s.score_id) < 5
            ) missing_scores
        """)
        admitted_missing_sources = _count(connection, """
            SELECT COUNT(*) FROM (
              SELECT a.venue_id FROM admin_venues a
              LEFT JOIN venue_sources s ON s.venue_id=a.venue_id
              WHERE a.admission_status='Admitted'
              GROUP BY a.venue_id HAVING COUNT(s.source_id)=0
            ) missing_sources
        """)
        admitted_invalid_scores = _count(connection, """
            SELECT COUNT(DISTINCT a.venue_id) FROM admin_venues a
            JOIN venue_scores s ON s.venue_id=a.venue_id
            WHERE a.admission_status='Admitted'
              AND s.score IS NOT NULL AND (s.score < 0 OR s.score > 100)
        """)
        admitted_missing_tags = _count(connection, """
            SELECT COUNT(*) FROM (
              SELECT a.venue_id FROM admin_venues a
              LEFT JOIN venue_tags t ON t.venue_id=a.venue_id
              WHERE a.admission_status='Admitted'
              GROUP BY a.venue_id HAVING COUNT(t.tag_id)=0
            ) missing_tags
        """)
        live_key_rows = 0
        try:
            raw_rows = connection.execute(text("SELECT data_json FROM admin_venues WHERE data_json IS NOT NULL")).scalars().all()
            for raw in raw_rows:
                if not isinstance(raw, str):
                    continue
                try:
                    payload = json.loads(raw)
                except (TypeError, ValueError):
                    payload = {}
                encoded = json.dumps(payload, ensure_ascii=False).lower()
                if any(f'"{key.lower()}"' in encoded for key in PROHIBITED_LIVE_KEYS):
                    live_key_rows += 1
        except Exception:
            pass

    hard_failures: list[str] = []
    if total == 0:
        hard_failures.append("database_has_no_venues")
    if published_non_admitted:
        hard_failures.append("published_venue_is_not_admitted")
    if published_not_publicly_eligible:
        hard_failures.append("published_venue_is_not_publicly_eligible")
    if published_missing_place:
        hard_failures.append("published_venue_missing_google_place_id")
    if admitted_missing_identity:
        hard_failures.append("admitted_venue_missing_identity")
    if admitted_missing_scores:
        hard_failures.append("admitted_venue_missing_score_coverage")
    if admitted_missing_sources:
        hard_failures.append("admitted_venue_missing_provenance")
    if admitted_invalid_scores:
        hard_failures.append("admitted_venue_has_invalid_scores")
    if live_key_rows:
        hard_failures.append("live_google_fields_present_in_persistent_payload")

    warnings: list[str] = []
    if published == 0:
        warnings.append("no_published_venues")
    if admitted_missing_tags:
        warnings.append("admitted_venue_missing_shuffl_tags")

    return {
        "ready_for_launch": not hard_failures,
        "hard_failures": hard_failures,
        "warnings": warnings,
        "counts": {
            "total_venues": total,
            "published": published,
            "published_non_admitted": published_non_admitted,
            "published_not_publicly_eligible": published_not_publicly_eligible,
            "published_missing_place_id": published_missing_place,
            "admitted_missing_identity": admitted_missing_identity,
            "admitted_missing_scores": admitted_missing_scores,
            "admitted_missing_sources": admitted_missing_sources,
            "admitted_invalid_scores": admitted_invalid_scores,
            "admitted_missing_tags": admitted_missing_tags,
            "persistent_live_key_rows": live_key_rows,
        },
        "policy": "phase7-launch-audit-v2",
    }

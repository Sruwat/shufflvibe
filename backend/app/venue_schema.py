"""Canonical venue-platform schema used by both admin and public APIs.

The admin store keeps ``admin_venues`` as the lifecycle/publication root for
backwards compatibility.  The tables below hold the structured, queryable
parts of a venue record instead of forcing every consumer to parse
``data_json``.  Google display-only fields (hours, rating, reviews, address
and coordinates) are intentionally not persisted here.
"""

from __future__ import annotations

import json
from typing import Any
from uuid import uuid4

from sqlalchemy import Connection, text


DDL = (
    """
    CREATE TABLE IF NOT EXISTS venue_identity (
        venue_id VARCHAR(180) PRIMARY KEY,
        official_name VARCHAR(255) NOT NULL DEFAULT '',
        venue_type VARCHAR(120) NOT NULL DEFAULT '',
        description TEXT,
        website_url TEXT,
        menu_url TEXT,
        booking_url TEXT,
        event_url TEXT,
        social_urls_json TEXT NOT NULL,
        operator_class VARCHAR(120) NOT NULL DEFAULT 'unknown',
        operator_class_status VARCHAR(80) NOT NULL DEFAULT 'unknown',
        fit_out_status VARCHAR(80) NOT NULL DEFAULT 'unknown',
        fit_out_year INTEGER,
        fit_out_confidence VARCHAR(40) NOT NULL DEFAULT 'none',
        metro_name VARCHAR(160),
        metro_distance_km DECIMAL(8,3),
        created_at VARCHAR(40) NOT NULL,
        updated_at VARCHAR(40) NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS venue_scores (
        score_id VARCHAR(64) PRIMARY KEY,
        venue_id VARCHAR(180) NOT NULL,
        factor VARCHAR(40) NOT NULL,
        score INTEGER,
        score_method VARCHAR(80) NOT NULL DEFAULT 'deterministic',
        evidence_json TEXT NOT NULL,
        score_version VARCHAR(40) NOT NULL DEFAULT 'mvp-v1',
        created_at VARCHAR(40) NOT NULL,
        updated_at VARCHAR(40) NOT NULL,
        UNIQUE (venue_id, factor)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS venue_tags (
        tag_id VARCHAR(64) PRIMARY KEY,
        venue_id VARCHAR(180) NOT NULL,
        tag VARCHAR(80) NOT NULL,
        tag_type VARCHAR(40) NOT NULL DEFAULT 'shuffl',
        not_specialised INTEGER NOT NULL DEFAULT 0,
        source VARCHAR(80) NOT NULL DEFAULT 'pipeline',
        created_at VARCHAR(40) NOT NULL,
        UNIQUE (venue_id, tag)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS venue_sources (
        source_id VARCHAR(180) PRIMARY KEY,
        venue_id VARCHAR(180) NOT NULL,
        field_name VARCHAR(120) NOT NULL,
        source_type VARCHAR(80) NOT NULL,
        source_url TEXT,
        status VARCHAR(40) NOT NULL DEFAULT 'observed',
        confidence VARCHAR(40) NOT NULL DEFAULT 'unknown',
        evidence_json TEXT,
        checked_at VARCHAR(40),
        created_at VARCHAR(40) NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS venue_time_slots (
        slot_id VARCHAR(180) PRIMARY KEY,
        venue_id VARCHAR(180) NOT NULL,
        day_of_week VARCHAR(20) NOT NULL DEFAULT 'all',
        start_time VARCHAR(10) NOT NULL,
        end_time VARCHAR(10) NOT NULL,
        label VARCHAR(120) NOT NULL DEFAULT '',
        source_id VARCHAR(180),
        source_type VARCHAR(80) NOT NULL DEFAULT 'official_venue',
        confidence VARCHAR(40) NOT NULL DEFAULT 'unknown',
        is_current INTEGER NOT NULL DEFAULT 1,
        created_at VARCHAR(40) NOT NULL,
        updated_at VARCHAR(40) NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS venue_metros (
        metro_id VARCHAR(64) PRIMARY KEY,
        venue_id VARCHAR(180) NOT NULL,
        metro_name VARCHAR(160) NOT NULL,
        distance_km DECIMAL(8,3),
        line_name VARCHAR(120),
        source_id VARCHAR(180),
        created_at VARCHAR(40) NOT NULL,
        UNIQUE (venue_id, metro_name)
    )
    """,
)


INDEXES = (
    "CREATE INDEX IF NOT EXISTS idx_venue_identity_type ON venue_identity (venue_type)",
    "CREATE INDEX IF NOT EXISTS idx_venue_scores_factor ON venue_scores (factor, score)",
    "CREATE INDEX IF NOT EXISTS idx_venue_tags_tag ON venue_tags (tag)",
    "CREATE INDEX IF NOT EXISTS idx_venue_sources_venue ON venue_sources (venue_id)",
    "CREATE INDEX IF NOT EXISTS idx_venue_slots_lookup ON venue_time_slots (venue_id, day_of_week, is_current)",
    "CREATE INDEX IF NOT EXISTS idx_venue_metros_venue ON venue_metros (venue_id)",
)


def ensure_venue_schema(conn: Connection) -> None:
    """Create the canonical venue tables on SQLite or MySQL."""
    for statement in DDL:
        conn.execute(text(statement))
    for statement in INDEXES:
        try:
            conn.execute(text(statement))
        except Exception:
            # Older MySQL versions do not accept IF NOT EXISTS on indexes;
            # the tables remain valid and the next migration can add them.
            pass


def _json(value: Any) -> str:
    return json.dumps(value if value is not None else {}, ensure_ascii=False, default=str)


def _rows(payload: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = payload.get(key, [])
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def sync_normalized_venue(conn: Connection, payload: dict[str, Any], now: str) -> None:
    """Replace pipeline facts for one venue while retaining admin overrides.

    This function only writes SHUFFL-owned/official evidence.  It deliberately
    ignores Google live identity, rating, reviews, coordinates and hours.
    """
    venue_id = str(payload.get("venue_id") or "").strip()
    if not venue_id:
        return
    identity = next(iter(_rows(payload, "venue_identity")), {})
    # Fresh pipeline syncs keep candidate fields at the payload root; exports
    # may nest them under ``candidates``. Both shapes must backfill identically.
    candidates = next(iter(_rows(payload, "candidates")), {}) or payload
    override = payload.get("admin_override") or {}
    if not isinstance(override, dict):
        override = {}
    effective_override = {**payload, **override}
    display_name = str(effective_override.get("display_name") or identity.get("official_name") or payload.get("display_name") or "")
    venue_type = str(payload.get("discovered_type") or "")
    social = identity.get("official_social_urls", "[]")
    if isinstance(social, list):
        social = _json(social)
    conn.execute(text("DELETE FROM venue_identity WHERE venue_id=:venue_id"), {"venue_id": venue_id})
    conn.execute(text("""
        INSERT INTO venue_identity
        (venue_id,official_name,venue_type,description,website_url,menu_url,booking_url,event_url,social_urls_json,operator_class,operator_class_status,fit_out_status,fit_out_year,fit_out_confidence,metro_name,metro_distance_km,created_at,updated_at)
        VALUES (:venue_id,:official_name,:venue_type,:description,:website_url,:menu_url,:booking_url,:event_url,:social_urls_json,:operator_class,:operator_class_status,:fit_out_status,:fit_out_year,:fit_out_confidence,:metro_name,:metro_distance_km,:created_at,:updated_at)
    """), {
        "venue_id": venue_id,
        "official_name": display_name,
        "venue_type": venue_type,
        "description": identity.get("official_description", "") or effective_override.get("manual_vibe", ""),
        "website_url": identity.get("official_url", "") or effective_override.get("official_url", "") or effective_override.get("website_url", ""),
        "menu_url": identity.get("menu_url", "") or effective_override.get("menu_url", ""),
        "booking_url": identity.get("booking_url", "") or effective_override.get("booking_url", ""),
        "event_url": identity.get("event_url", "") or effective_override.get("event_url", ""),
        "social_urls_json": str(social if social not in ("[]", "") else _json(effective_override.get("social_urls", []))),
        "operator_class": candidates.get("operator_class", effective_override.get("operator_class", "unknown")) or "unknown",
        "operator_class_status": candidates.get("operator_class_status", "unknown") or "unknown",
        "fit_out_status": candidates.get("fit_out_status", "unknown") or "unknown",
        "fit_out_year": candidates.get("fit_out_year"),
        "fit_out_confidence": candidates.get("fit_out_confidence", "none") or "none",
        "metro_name": effective_override.get("metro_name"),
        "metro_distance_km": effective_override.get("metro_distance_km"),
        "created_at": now,
        "updated_at": now,
    })

    for table in ("venue_scores", "venue_tags", "venue_sources", "venue_time_slots", "venue_metros"):
        conn.execute(text(f"DELETE FROM {table} WHERE venue_id=:venue_id"), {"venue_id": venue_id})

    for row in _rows(payload, "venue_scores"):
        conn.execute(text("""
            INSERT INTO venue_scores
            (score_id,venue_id,factor,score,score_method,evidence_json,score_version,created_at,updated_at)
            VALUES (:score_id,:venue_id,:factor,:score,:score_method,:evidence_json,:score_version,:created_at,:updated_at)
        """), {
            "score_id": f"{venue_id}:score:{row.get('factor', uuid4().hex)}",
            "venue_id": venue_id,
            "factor": str(row.get("factor", "")),
            "score": row.get("score"),
            "score_method": str(row.get("score_method") or row.get("evidence_type") or "deterministic"),
            "evidence_json": _json(row),
            "score_version": str(row.get("score_version", "mvp-v1")),
            "created_at": now,
            "updated_at": now,
        })

    seen_tags: set[str] = set()
    for row in _rows(payload, "venue_tags"):
        tag = str(row.get("tag", "")).strip()
        if not tag or tag in seen_tags:
            continue
        seen_tags.add(tag)
        conn.execute(text("""
            INSERT INTO venue_tags
            (tag_id,venue_id,tag,tag_type,not_specialised,source,created_at)
            VALUES (:tag_id,:venue_id,:tag,:tag_type,:not_specialised,:source,:created_at)
        """), {
            "tag_id": f"{venue_id}:tag:{tag}",
            "venue_id": venue_id,
            "tag": tag,
            "tag_type": str(row.get("tag_family") or row.get("tag_type") or "shuffl"),
            "not_specialised": 1 if row.get("not_specialised") else 0,
            "source": str(row.get("source") or row.get("source_type") or "pipeline"),
            "created_at": now,
        })
    for tag in effective_override.get("manual_tags", []) if isinstance(effective_override.get("manual_tags"), list) else []:
        tag = str(tag).strip()
        if tag and tag not in seen_tags:
            conn.execute(text("""
                INSERT INTO venue_tags
                (tag_id,venue_id,tag,tag_type,not_specialised,source,created_at)
                VALUES (:tag_id,:venue_id,:tag,'admin',0,'admin',:created_at)
            """), {"tag_id": f"{venue_id}:admin-tag:{tag}", "venue_id": venue_id, "tag": tag, "created_at": now})

    # Legacy admitted rows sometimes have no tag array at all. Add only a
    # conservative category tag from the already-persisted venue type; never
    # invent scene claims or copy Google live metadata during remediation.
    if not seen_tags and str(payload.get("admission_decision", "")) == "Admitted":
        category_tags = {"bar": "bar", "pub": "pub", "restaurant": "restaurant", "cafe": "cafe", "night_club": "nightclub", "nightclub": "nightclub"}
        fallback_tag = category_tags.get(venue_type.casefold())
        if fallback_tag:
            conn.execute(text("""
                INSERT INTO venue_tags
                (tag_id,venue_id,tag,tag_type,not_specialised,source,created_at)
                VALUES (:tag_id,:venue_id,:tag,'category',0,'remediation',:created_at)
            """), {"tag_id": f"{venue_id}:remediation-tag:{fallback_tag}", "venue_id": venue_id, "tag": fallback_tag, "created_at": now})

    seen_source_ids: set[str] = set()
    for index, row in enumerate(_rows(payload, "venue_sources"), start=1):
        # Google live display evidence is transient by policy and must not be
        # copied into the durable provenance table. Other duplicate source IDs
        # are made deterministic and unique so legacy exports can be repaired.
        source_type = str(row.get("source_type", ""))
        if source_type == "google_live_display_only":
            continue
        raw_source_id = str(row.get("source_id") or "source")
        source_id = f"{venue_id}:source:{raw_source_id}"
        if source_id in seen_source_ids:
            source_id = f"{source_id}:{index}"
        seen_source_ids.add(source_id)
        conn.execute(text("""
            INSERT INTO venue_sources
            (source_id,venue_id,field_name,source_type,source_url,status,confidence,evidence_json,checked_at,created_at)
            VALUES (:source_id,:venue_id,:field_name,:source_type,:source_url,:status,:confidence,:evidence_json,:checked_at,:created_at)
        """), {
            "source_id": source_id,
            "venue_id": venue_id,
            "field_name": str(row.get("field_name", "")),
            "source_type": source_type,
            "source_url": row.get("source_url", ""),
            "status": str(row.get("status", "observed")),
            "confidence": str(row.get("confidence", "unknown")),
            "evidence_json": _json(row),
            "checked_at": row.get("retrieved_at") or row.get("checked_at"),
            "created_at": now,
        })

    for index, row in enumerate(_rows(payload, "venue_time_slots"), start=1):
        start = str(row.get("from_time") or row.get("start_time") or "").strip()
        end = str(row.get("to_time") or row.get("end_time") or "").strip()
        if not start and not end:
            continue
        conn.execute(text("""
            INSERT INTO venue_time_slots
            (slot_id,venue_id,day_of_week,start_time,end_time,label,source_id,source_type,confidence,is_current,created_at,updated_at)
            VALUES (:slot_id,:venue_id,:day_of_week,:start_time,:end_time,:label,:source_id,:source_type,:confidence,1,:created_at,:updated_at)
        """), {
            "slot_id": f"{venue_id}:slot:{index}",
            "venue_id": venue_id,
            "day_of_week": str(row.get("days") or row.get("day_of_week") or "all"),
            "start_time": start,
            "end_time": end,
            "label": str(row.get("type") or row.get("label") or ""),
            "source_id": row.get("source_id"),
            "source_type": str(row.get("source_type", "official_venue")),
            "confidence": str(row.get("confidence", "unknown")),
            "created_at": now,
            "updated_at": now,
        })

    metro_name = str(effective_override.get("metro_name") or "").strip()
    if metro_name:
        conn.execute(text("""
            INSERT INTO venue_metros
            (metro_id,venue_id,metro_name,distance_km,line_name,source_id,created_at)
            VALUES (:metro_id,:venue_id,:metro_name,:distance_km,'',NULL,:created_at)
        """), {"metro_id": f"{venue_id}:metro", "venue_id": venue_id, "metro_name": metro_name, "distance_km": effective_override.get("metro_distance_km"), "created_at": now})

from __future__ import annotations

import csv
import json
import sqlite3
from datetime import date
from pathlib import Path
from typing import Any

from .scoring import FACTORS, score


TAG_RULES = {
    "outdoorSeating": ("layout", "outdoor-seating"),
    "liveMusic": ("programming", "live-music"),
    "reservable": ("social", "reservable"),
    "goodForGroups": ("social", "good-for-groups"),
}

TAG_VOCAB = {
    "table-led", "booth-heavy", "bar-rail", "open", "standing-room", "floor", "courtyard",
    "open-air", "rooftop", "garden", "terrace", "basement", "daylight", "skyline", "waterside", "indoor-only",
    "heritage-building", "heritage-styled", "listed-structure", "colonial-bungalow", "minimal", "maximalist", "industrial", "dive",
    "tasting-menu", "small-plates", "thali-service", "counter-service", "full-service", "late-kitchen", "early-kitchen", "bar-snacks-only",
    "walk-in", "reservation-only", "ticketed", "cover-charge", "members", "queue-after-9", "no-queue", "age-gated",
    "live-music", "dj-after-11", "sufi-night", "sitar-classical", "ghazal-qawwali", "quiz-night", "screening", "match-days", "open-mic",
    "outdoor-seating", "reservable", "good-for-groups", "food-service", "alcohol-service",
    "bar", "pub", "restaurant", "cafe", "nightclub",
}


def _text(details: dict[str, Any]) -> str:
    return ((details.get("displayName") or {}).get("text") or "venue").strip()


def _auto_operator_class(details: dict[str, Any]) -> tuple[str, str]:
    """Infer only when the API evidence is strong; never pretend unknown is verified."""
    name = _text(details).lower()
    types = {str(value).lower() for value in details.get("types", [])}
    if any(token in name for token in ("marriott", "hyatt", "hilton", "novotel", "aloft", "taj ", "oberoi", "itc ")):
        return "hotel", "inferred_from_name"
    if any(token in name for token in ("social", "blue tokai", "third wave", "starbucks", "hard rock", "chili's", "big chill")):
        return "chain_or_group", "inferred_from_name"
    if "lodging" in types or "hotel" in types:
        return "hotel", "inferred_from_google_type"
    return "unknown", "insufficient_machine_evidence"


def _safe_slots(raw: dict[str, Any], venue_id: str) -> list[dict[str, Any]]:
    official = raw.get("official_data") or {}
    slots = (official.get("time_slots") or []) + (raw.get("time_slots") or [])
    result = []
    for index, slot in enumerate(slots):
        if not isinstance(slot, dict):
            continue
        days = str(slot.get("days", "")).strip()
        from_time = str(slot.get("from_time", slot.get("from", ""))).strip()
        to_time = str(slot.get("to_time", slot.get("to", ""))).strip()
        evidence = str(slot.get("evidence", "")).strip()
        if not (days or from_time or to_time or evidence):
            continue
        result.append({"venue_id": venue_id, "slot_id": f"{venue_id}:slot:{index + 1}", "days": days, "from_time": from_time, "to_time": to_time, "type": str(slot.get("type", "")).strip(), "slot_status": "filled", "evidence": evidence, "source_type": str(slot.get("source_type", "official_website")), "source_url": str(slot.get("source_url", "")), "confidence": str(slot.get("confidence", "medium"))})
    return result


def _live_slot(venue_id: str, place_id: str) -> dict[str, Any]:
    """Create a non-fabricated slot row for display-time resolution."""
    return {
        "venue_id": venue_id,
        "slot_id": f"{venue_id}:live-hours",
        "days": "",
        "from_time": "",
        "to_time": "",
        "type": "",
        "slot_status": "live_google_required",
        "evidence": "Google opening hours and current programming must be fetched at display time.",
        "source_type": "google_places_live",
        "source_url": f"https://www.google.com/maps/search/?api=1&query=Google&query_place_id={place_id}",
        "confidence": "live_only",
    }


def _approved_tags(details: dict[str, Any], scores: dict[str, Any]) -> list[dict[str, Any]]:
    tags: list[dict[str, Any]] = []
    for field, (family, tag) in TAG_RULES.items():
        if details.get(field) is True and tag in TAG_VOCAB:
            tags.append({"tag": tag, "tag_family": family, "evidence": f"structured field {field}=true", "confidence": "medium"})
    if details.get("goodForWatchingSports") is True:
        tags.append({"tag": "screening", "tag_family": "programming", "evidence": "structured field goodForWatchingSports=true", "confidence": "medium"})
    primary = str(details.get("primaryType", "")).lower()
    type_tags = {"bar": "bar", "pub": "pub", "restaurant": "restaurant", "cafe": "cafe", "night_club": "nightclub"}
    if primary in type_tags:
        tags.append({"tag": type_tags[primary], "tag_family": "category", "evidence": f"Google primaryType={primary}", "confidence": "medium"})
    if any(details.get(key) is True for key in ("servesDinner", "servesBrunch", "servesDessert", "servesVegetarianFood")):
        tags.append({"tag": "food-service", "tag_family": "service", "evidence": "Google structured food-service field", "confidence": "medium"})
    if any(details.get(key) is True for key in ("servesBeer", "servesWine", "servesCocktails")):
        tags.append({"tag": "alcohol-service", "tag_family": "service", "evidence": "Google structured alcohol-service field", "confidence": "medium"})
    if scores.get("scores", {}).get("heritage", 0) >= 75 and scores.get("score_evidence", {}).get("heritage"):
        tags.append({"tag": "heritage-styled", "tag_family": "period-and-character", "evidence": "; ".join(scores["score_evidence"]["heritage"]), "confidence": "low"})
    return tags


def build_market_ready(raw_rows: list[dict[str, Any]], areas: list[dict[str, Any]], verification_path: Path | None = None) -> dict[str, Any]:
    """Build the licensing-safe database from transient API responses.

    `verification_path` remains accepted for backwards compatibility, but is
    intentionally ignored: the production build is fully automatic.
    """
    candidates: list[dict[str, Any]] = []
    venues: list[dict[str, Any]] = []
    identity: list[dict[str, Any]] = []
    hours: list[dict[str, Any]] = []
    slots: list[dict[str, Any]] = []
    score_rows: list[dict[str, Any]] = []
    evidence_rows: list[dict[str, Any]] = []
    score_audit_rows: list[dict[str, Any]] = []
    tags: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []
    gold_list: list[dict[str, Any]] = []
    admission_log: list[dict[str, Any]] = []
    live_fields: list[dict[str, Any]] = []

    for raw in raw_rows:
        place_id = raw.get("google_place_id", "")
        details = raw.get("google_details", {}) or {}
        venue_id = f"venue:{place_id}"
        computed = score(details)
        score_values = raw.get("scores") or computed.get("scores", {})
        score_evidence = raw.get("score_evidence") or computed.get("score_evidence", {})
        score_confidence = raw.get("score_confidence") or computed.get("score_confidence", "low")
        score_bundle = {"scores": score_values, "score_evidence": score_evidence}
        is_admitted = raw.get("admission_decision") == "Admitted"
        decision_status = "auto_admitted" if is_admitted else ("auto_insufficient_evidence" if raw.get("admission_decision") == "Insufficient evidence" else "auto_rejected")
        operator_class, operator_evidence = _auto_operator_class(details)
        official = raw.get("official_data") or {}
        osm = raw.get("osm_data") or {}
        review = raw.get("shuffl_review_summary") or {"shuffl_review_count": 0, "shuffl_rating_mean": None, "shuffl_rating_distribution": {}, "review_source": "none", "review_license_status": "not_available", "review_confidence": "none"}
        explicit_slots = _safe_slots(raw, venue_id)
        fitout_status = official.get("fit_out_status", "unknown")
        fitout_year = official.get("fit_out_year")
        fitout_age = (date.today().year - int(fitout_year)) if fitout_year else None
        hours_value = official.get("official_hours", "")
        candidate = {
            "venue_id": venue_id,
            "google_place_id": place_id,
            "discovered_area": raw.get("discovered_area", ""),
            "discovered_city": raw.get("discovered_city", ""),
            "discovered_type": raw.get("discovered_type", ""),
            "admission_decision": raw.get("admission_decision", "Rejected"),
            "admission_reason": raw.get("admission_reason", ""),
            "operator_class": operator_class,
            "operator_class_status": operator_evidence,
            "fit_out_years": None,
            "fit_out_year": fitout_year,
            "fit_out_years": fitout_age,
            "fit_out_status": fitout_status,
            "fit_out_confidence": official.get("fit_out_confidence", "none"),
            "review_source": review.get("review_source", "none"),
            "review_license_status": review.get("review_license_status", "not_available"),
            "shuffl_review_count": review.get("shuffl_review_count", 0),
            "shuffl_rating_mean": review.get("shuffl_rating_mean"),
            "shuffl_rating_distribution": json.dumps(review.get("shuffl_rating_distribution", {}), ensure_ascii=False),
            "verification_status": decision_status,
            "evidence_audit": json.dumps(raw.get("evidence_audit", {}), ensure_ascii=False),
            "live_google_required": True,
            "google_lookup_url": f"https://www.google.com/maps/search/?api=1&query=Google&query_place_id={place_id}",
        }
        candidates.append(candidate)
        admission_log.append({"venue_id": venue_id, "decision": raw.get("admission_decision", "Rejected"), "verification_status": decision_status, "reason": raw.get("admission_reason", ""), "operator_class": operator_class, "fit_out_status": fitout_status, "review_source": review.get("review_source", "none"), "evidence_audit": json.dumps(raw.get("evidence_audit", {}), ensure_ascii=False), "created_at": date.today().isoformat()})
        score_audit_rows.append({"venue_id": venue_id, **(raw.get("evidence_audit", {}).get("score_audit", {}) if isinstance(raw.get("evidence_audit"), dict) else {}), "score_confidence": score_confidence})

        identity_source = (raw.get("evidence_audit") or {}).get("identity_source", "none")
        identity.append({"venue_id": venue_id, "google_place_id": place_id, "osm_id": osm.get("osm_id", ""), "osm_name": osm.get("name", ""), "osm_address": osm.get("address", ""), "osm_latitude": osm.get("latitude", ""), "osm_longitude": osm.get("longitude", ""), "osm_website": osm.get("website", ""), "official_name": official.get("official_name", ""), "official_address": official.get("official_address", ""), "official_phone": official.get("official_phone", ""), "official_url": official.get("official_url", ""), "official_social_urls": json.dumps(official.get("official_social_urls", []), ensure_ascii=False), "menu_url": official.get("menu_url", ""), "booking_url": official.get("booking_url", ""), "event_url": official.get("event_url", ""), "official_description": official.get("official_description", ""), "fit_out_evidence": official.get("fit_out_evidence", ""), "identity_source": identity_source, "identity_confidence": "high" if identity_source == "official_website" else ("medium" if identity_source == "osm_secondary" else "none")})

        factor_states: dict[str, str] = {}
        for factor in FACTORS:
            value = score_values.get(factor)
            ev = score_evidence.get(factor, [])
            not_specialised = factor in (raw.get("not_specialised") or [])
            state = "not_specialised" if not_specialised else ("served" if ev else "unknown")
            factor_states[factor] = state
            score_rows.append({"venue_id": venue_id, "factor": factor, "score": value if state != "not_specialised" else None, "state": state, "confidence": score_confidence, "score_version": "shuffl-auto-v2", "scored_at": date.today().isoformat()})
            evidence_rows.append({"venue_id": venue_id, "factor": factor, "score": value, "evidence_text": "; ".join(ev), "evidence_type": "official_or_shuffl_evidence" if (official.get("official_status") == "fetched" or review.get("shuffl_review_count", 0)) else ("structured_or_derived" if ev else "none"), "evidence_source": "official_website_or_shuffl_reviews" if (official.get("official_status") == "fetched" or review.get("shuffl_review_count", 0)) else "temporary_google_live_response", "confidence": score_confidence})
        for tag in _approved_tags(details, score_bundle):
            tags.append({"venue_id": venue_id, **tag, "source_id": f"google-live:{place_id}"})
        sources.append({"source_id": f"google-live:{place_id}", "venue_id": venue_id, "field_name": "derived_scores", "source_type": "google_live_only", "source_url": "", "retrieved_at": date.today().isoformat(), "verified_by": "pipeline", "confidence": score_confidence})
        if official.get("official_url"):
            for evidence in official.get("official_evidence", []) or []:
                sources.append({"source_id": f"official:{place_id}", "venue_id": venue_id, "field_name": evidence.get("field_name", "official_page"), "source_type": "official_website", "source_url": evidence.get("source_url", official.get("official_url")), "retrieved_at": official.get("official_checked_on", date.today().isoformat()), "verified_by": "pipeline", "confidence": evidence.get("confidence", "medium"), "evidence_text": evidence.get("evidence_text", "")})
            if hours_value:
                sources.append({"source_id": f"official-hours:{place_id}", "venue_id": venue_id, "field_name": "opening_hours", "source_type": "official_website", "source_url": official.get("official_url", ""), "retrieved_at": official.get("official_checked_on", date.today().isoformat()), "verified_by": "pipeline", "confidence": official.get("hours_confidence", "medium"), "evidence_text": hours_value})
        if review.get("shuffl_review_count", 0):
            sources.append({"source_id": f"shuffl-reviews:{place_id}", "venue_id": venue_id, "field_name": "review_distribution", "source_type": "shuffl_owned_reviews", "source_url": "", "retrieved_at": date.today().isoformat(), "verified_by": "pipeline", "confidence": review.get("review_confidence", "medium")})

        if is_admitted:
            # Google display fields are deliberately not persisted. The app uses
            # google_place_id + this live URL to fetch them at render time.
            venues.append({"venue_id": venue_id, "google_place_id": place_id, "area": raw.get("discovered_area", ""), "city": raw.get("discovered_city", ""), "discovered_type": raw.get("discovered_type", ""), "operator_class": operator_class, "operator_class_status": operator_evidence, "fit_out_year": fitout_year, "fit_out_years": fitout_age, "fit_out_status": fitout_status, "fit_out_confidence": official.get("fit_out_confidence", "none"), "fit_out_evidence": official.get("fit_out_evidence", ""), "review_source": review.get("review_source", "none"), "review_license_status": review.get("review_license_status", "not_available"), "shuffl_review_count": review.get("shuffl_review_count", 0), "shuffl_rating_mean": review.get("shuffl_rating_mean"), "shuffl_rating_distribution": json.dumps(review.get("shuffl_rating_distribution", {}), ensure_ascii=False), "official_url": official.get("official_url", ""), "official_social_urls": json.dumps(official.get("official_social_urls", []), ensure_ascii=False), "menu_url": official.get("menu_url", ""), "booking_url": official.get("booking_url", ""), "event_url": official.get("event_url", ""), "status": "active", "admission_decision": "Admitted", "admission_reason": raw.get("admission_reason", ""), "verification_status": decision_status, "live_google_required": True, "google_lookup_url": f"https://www.google.com/maps/search/?api=1&query=Google&query_place_id={place_id}", "factor_states": json.dumps(factor_states, ensure_ascii=False)})
        if hours_value:
            hours.append({"venue_id": venue_id, "hours_text": hours_value, "hours_source": "official_website", "hours_status": "official", "hours_confidence": official.get("hours_confidence", "medium"), "hours_last_checked": official.get("official_checked_on", date.today().isoformat()), "source_url": official.get("official_url", "")})
        if is_admitted and not hours_value:
            hours.append({"venue_id": venue_id, "hours_text": "", "hours_source": "google_places_live", "hours_status": "live_google_required", "hours_confidence": "live_only", "hours_last_checked": "", "source_url": f"https://www.google.com/maps/search/?api=1&query=Google&query_place_id={place_id}"})
        slots.extend(explicit_slots)
        if is_admitted and not explicit_slots:
            slots.append(_live_slot(venue_id, place_id))
        if not explicit_slots:
            gold_list.append({"venue_id": venue_id, "google_place_id": place_id, "gap": "no_explicit_time_evidence", "status": "gold", "note": "No time slot inferred; resolve at query time or through later structured schedule capture."})
        sources.append({"source_id": f"google-live:{place_id}", "venue_id": venue_id, "field_name": "display_identity_hours_rating_reviews", "source_type": "google_live_display_only", "source_url": f"https://www.google.com/maps/search/?api=1&query=Google&query_place_id={place_id}", "retrieved_at": date.today().isoformat(), "verified_by": "pipeline", "confidence": "live_only"})
        for field_name in ("displayName", "formattedAddress", "location", "regularOpeningHours", "rating", "userRatingCount", "reviews", "priceLevel"):
            live_fields.append({"venue_id": venue_id, "google_place_id": place_id, "field_name": field_name, "fetch_mode": "display_time", "persisted": False, "endpoint": "Google Places API (New) Place Details", "lookup_url": f"https://www.google.com/maps/search/?api=1&query=Google&query_place_id={place_id}"})

    return {"retrieved_on": date.today().isoformat(), "candidates": candidates, "venues": venues, "venue_identity": identity, "venue_hours": hours, "venue_time_slots": slots, "gold_list": gold_list, "venue_scores": score_rows, "score_evidence": evidence_rows, "score_evidence_audit": score_audit_rows, "venue_tags": tags, "venue_sources": sources, "admission_log": admission_log, "live_google_fields": live_fields, "areas": areas}


def save_market_ready(payload: dict[str, Any], out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for key, rows in payload.items():
        if key == "retrieved_on":
            continue
        (out / f"{key}.json").write_text(json.dumps({"retrieved_on": payload["retrieved_on"], key: rows}, ensure_ascii=False, indent=2), encoding="utf-8")
        if isinstance(rows, list):
            with (out / f"{key}.csv").open("w", encoding="utf-8", newline="") as handle:
                fields = sorted({field for row in rows for field in row}) if rows else []
                if fields:
                    writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
                    writer.writeheader()
                    writer.writerows(rows)
    connection = sqlite3.connect(out / "venue_database_market_ready.sqlite3")
    try:
        connection.executescript("""
        DROP TABLE IF EXISTS candidates; DROP TABLE IF EXISTS venues; DROP TABLE IF EXISTS venue_identity; DROP TABLE IF EXISTS venue_hours; DROP TABLE IF EXISTS venue_time_slots; DROP TABLE IF EXISTS gold_list; DROP TABLE IF EXISTS venue_scores; DROP TABLE IF EXISTS score_evidence; DROP TABLE IF EXISTS score_evidence_audit; DROP TABLE IF EXISTS venue_tags; DROP TABLE IF EXISTS venue_sources; DROP TABLE IF EXISTS human_pass; DROP TABLE IF EXISTS admission_log; DROP TABLE IF EXISTS admission_rejected; DROP TABLE IF EXISTS enrichment_failures; DROP TABLE IF EXISTS pipeline_failures; DROP TABLE IF EXISTS run_summary; DROP TABLE IF EXISTS areas; DROP TABLE IF EXISTS live_google_fields;
        """)
        empty_schemas = {
            "venue_hours": ["venue_id", "day", "open", "close", "source_id"],
            "venue_identity": ["venue_id", "google_place_id", "official_url", "identity_source", "identity_confidence"],
            "venue_time_slots": ["venue_id", "slot_id", "days", "from_time", "to_time", "type", "slot_status", "evidence", "source_type", "confidence"],
            "gold_list": ["venue_id", "google_place_id", "gap", "status", "note"],
            "enrichment_failures": ["google_place_id", "error"],
        }
        for key, rows in payload.items():
            if key in {"retrieved_on"}:
                continue
            table = key
            columns = sorted({field for row in rows for field in row}) or empty_schemas.get(key, [])
            if not columns:
                continue
            safe = {column: "TEXT" for column in columns}
            connection.execute(f"CREATE TABLE {table} ({','.join(f'[{column}] TEXT' for column in columns)})")
            placeholders = ",".join("?" for _ in columns)
            connection.executemany(f"INSERT INTO {table} ({','.join(f'[{column}]' for column in columns)}) VALUES ({placeholders})", [[str(row.get(column, "")) for column in columns] for row in rows])
        connection.commit()
    finally:
        connection.close()

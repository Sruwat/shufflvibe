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


def _text(details: dict[str, Any]) -> str:
    return ((details.get("displayName") or {}).get("text") or "venue").strip()


def _load_verification(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return {(row.get("google_place_id") or row.get("venue_id") or "").strip(): row for row in csv.DictReader(handle) if (row.get("google_place_id") or row.get("venue_id"))}


def _approved_tags(details: dict[str, Any], scores: dict[str, Any]) -> list[dict[str, Any]]:
    tags: list[dict[str, Any]] = []
    for field, (family, tag) in TAG_RULES.items():
        if details.get(field) is True:
            tags.append({"tag": tag, "tag_family": family, "evidence": f"structured field {field}=true", "confidence": "medium"})
    if details.get("priceLevel"):
        tags.append({"tag": "price-listed", "tag_family": "service", "evidence": "structured priceLevel", "confidence": "medium"})
    if scores.get("scores", {}).get("heritage", 0) >= 75 and scores.get("score_evidence", {}).get("heritage"):
        tags.append({"tag": "heritage-styled", "tag_family": "period-and-character", "evidence": "; ".join(scores["score_evidence"]["heritage"]), "confidence": "low"})
    return tags


def build_market_ready(raw_rows: list[dict[str, Any]], areas: list[dict[str, Any]], verification_path: Path) -> dict[str, Any]:
    verification = _load_verification(verification_path)
    candidates: list[dict[str, Any]] = []
    venues: list[dict[str, Any]] = []
    hours: list[dict[str, Any]] = []
    slots: list[dict[str, Any]] = []
    score_rows: list[dict[str, Any]] = []
    evidence_rows: list[dict[str, Any]] = []
    tags: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []
    human_pass: list[dict[str, Any]] = []
    admission_log: list[dict[str, Any]] = []

    for raw in raw_rows:
        place_id = raw.get("google_place_id", "")
        details = raw.get("google_details", {}) or {}
        venue_id = f"venue:{place_id}"
        scores = raw.get("scores") or score(details)
        verified = verification.get(place_id) or verification.get(venue_id) or {}
        is_verified = (verified.get("verification_status") or "").lower() == "verified"
        candidate = {
            "venue_id": venue_id,
            "google_place_id": place_id,
            "discovered_area": raw.get("discovered_area", ""),
            "discovered_city": raw.get("discovered_city", ""),
            "discovered_type": raw.get("discovered_type", ""),
            "verification_status": "verified" if is_verified else "needs_official_verification",
            "live_google_required": True,
        }
        candidates.append(candidate)
        human_pass.append({"venue_id": venue_id, "google_place_id": place_id, "candidate_label": "live Google lookup required", "official_website_checked": verified.get("official_website_checked", "false"), "official_social_checked": verified.get("official_social_checked", "false"), "hours_confirmed": verified.get("hours_confirmed", "false"), "scene_confirmed": verified.get("scene_confirmed", "false"), "final_decision": "Admitted" if is_verified else "Review", "reviewer_name": verified.get("reviewer_name", ""), "reviewed_at": verified.get("reviewed_at", ""), "notes": verified.get("notes", "")})
        admission_log.append({"venue_id": venue_id, "decision": "Admitted" if is_verified else "Review", "reason": "official_verification_completed" if is_verified else "official_verification_required", "created_at": date.today().isoformat()})

        factor_states: dict[str, str] = {}
        for factor in FACTORS:
            value = scores.get("scores", {}).get(factor)
            ev = scores.get("score_evidence", {}).get(factor, [])
            state = "served" if ev else "unknown"
            factor_states[factor] = state
            score_rows.append({"venue_id": venue_id, "factor": factor, "score": value, "state": state, "confidence": scores.get("score_confidence", "low"), "score_version": "shuffl-local-v1", "scored_at": date.today().isoformat()})
            evidence_rows.append({"venue_id": venue_id, "factor": factor, "score": value, "evidence_text": "; ".join(ev), "evidence_type": "structured_or_derived" if ev else "none", "evidence_source": "temporary_google_live_response", "confidence": scores.get("score_confidence", "low")})
        for tag in _approved_tags(details, scores):
            tags.append({"venue_id": venue_id, **tag, "source_id": f"google-live:{place_id}"})
        sources.append({"source_id": f"google-live:{place_id}", "venue_id": venue_id, "field_name": "derived_scores", "source_type": "google_live_only", "source_url": "", "retrieved_at": date.today().isoformat(), "verified_by": "pipeline", "confidence": scores.get("score_confidence", "low")})

        if is_verified:
            # These values are accepted only from the user's official verification file.
            venues.append({"venue_id": venue_id, "google_place_id": place_id, "name": verified.get("name", ""), "address": verified.get("address", ""), "area": verified.get("area", raw.get("discovered_area", "")), "city": verified.get("city", raw.get("discovered_city", "")), "latitude": verified.get("latitude", ""), "longitude": verified.get("longitude", ""), "venue_type": verified.get("venue_type", ""), "official_website": verified.get("official_website", ""), "official_instagram": verified.get("official_instagram", ""), "official_facebook": verified.get("official_facebook", ""), "menu_url": verified.get("menu_url", ""), "booking_url": verified.get("booking_url", ""), "status": "active", "factor_states": json.dumps(factor_states, ensure_ascii=False)})
            source_type = "official_website_or_social"
            sources.append({"source_id": f"official:{venue_id}", "venue_id": venue_id, "field_name": "identity_and_hours", "source_type": source_type, "source_url": verified.get("official_website", "") or verified.get("official_instagram", ""), "retrieved_at": verified.get("reviewed_at", date.today().isoformat()), "verified_by": verified.get("reviewer_name", ""), "confidence": "high"})
            verified_hours = verified.get("hours_json", "")
            if verified_hours:
                try:
                    for row in json.loads(verified_hours):
                        hours.append({"venue_id": venue_id, **row, "source_id": f"official:{venue_id}"})
                except json.JSONDecodeError:
                    pass

    return {"retrieved_on": date.today().isoformat(), "candidates": candidates, "venues": venues, "venue_hours": hours, "venue_time_slots": slots, "venue_scores": score_rows, "score_evidence": evidence_rows, "venue_tags": tags, "venue_sources": sources, "human_pass": human_pass, "admission_log": admission_log, "areas": areas}


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
        DROP TABLE IF EXISTS candidates; DROP TABLE IF EXISTS venues; DROP TABLE IF EXISTS venue_hours; DROP TABLE IF EXISTS venue_time_slots; DROP TABLE IF EXISTS venue_scores; DROP TABLE IF EXISTS score_evidence; DROP TABLE IF EXISTS venue_tags; DROP TABLE IF EXISTS venue_sources; DROP TABLE IF EXISTS human_pass; DROP TABLE IF EXISTS admission_log; DROP TABLE IF EXISTS areas;
        """)
        for key, rows in payload.items():
            if key in {"retrieved_on"} or not rows:
                continue
            table = key
            columns = sorted({field for row in rows for field in row})
            safe = {column: "TEXT" for column in columns}
            connection.execute(f"CREATE TABLE {table} ({','.join(f'[{column}] TEXT' for column in columns)})")
            placeholders = ",".join("?" for _ in columns)
            connection.executemany(f"INSERT INTO {table} ({','.join(f'[{column}]' for column in columns)}) VALUES ({placeholders})", [[str(row.get(column, "")) for column in columns] for row in rows])
        connection.commit()
    finally:
        connection.close()

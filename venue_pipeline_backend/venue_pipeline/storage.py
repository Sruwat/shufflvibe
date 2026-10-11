from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path
from typing import Any


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def normalize(raw: dict[str, Any]) -> dict[str, Any]:
    details = raw.get("google_details", {})
    scores = raw.get("scores", {})
    name = (details.get("displayName") or {}).get("text", "")
    return {
        "venue_id": f"google:{raw.get('google_place_id', '')}",
        "name": name,
        "google_place_id": raw.get("google_place_id", ""),
        "google_maps_url": details.get("googleMapsUri", ""),
        "address": details.get("formattedAddress", ""),
        "latitude": (details.get("location") or {}).get("latitude"),
        "longitude": (details.get("location") or {}).get("longitude"),
        "area": raw.get("discovered_area", ""),
        "city": raw.get("discovered_city", ""),
        "website": details.get("websiteUri", ""),
        "phone": details.get("nationalPhoneNumber", ""),
        "venue_type": details.get("primaryType", ""),
        "price_level": details.get("priceLevel", ""),
        "rating": details.get("rating"),
        "review_count": details.get("userRatingCount"),
        "opening_hours": json.dumps(details.get("regularOpeningHours", {}), ensure_ascii=False),
        "food": any(details.get(key) is True for key in ("servesDinner", "servesBrunch", "servesDessert", "servesVegetarianFood")),
        "alcohol": any(details.get(key) is True for key in ("servesBeer", "servesWine", "servesCocktails")),
        "live_music": details.get("liveMusic"),
        "outdoor_seating": details.get("outdoorSeating"),
        "reservable": details.get("reservable"),
        "description": raw.get("description", ""),
        "tags": json.dumps(raw.get("tags", []), ensure_ascii=False),
        "time_slots": json.dumps(raw.get("time_slots", []), ensure_ascii=False),
        **{f"{key}_score": value for key, value in scores.items()},
        "admission_decision": raw.get("admission_decision", "Review"),
        "admission_reason": raw.get("admission_reason", ""),
        "verification_status": raw.get("verification_status", "Needs human verification"),
        "score_confidence": raw.get("score_confidence", "low"),
        "source": "Google Places API (New)",
    }


def save_sqlite(path: Path, venues: list[dict[str, Any]], queue: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        connection.executescript("""
        DROP TABLE IF EXISTS venues;
        DROP TABLE IF EXISTS verification_queue;
        CREATE TABLE venues (venue_id TEXT PRIMARY KEY, name TEXT, google_place_id TEXT UNIQUE, google_maps_url TEXT, address TEXT, area TEXT, city TEXT, venue_type TEXT, rating REAL, review_count INTEGER, website TEXT, phone TEXT, price_level TEXT, food INTEGER, alcohol INTEGER, live_music INTEGER, outdoor_seating INTEGER, reservable INTEGER, description TEXT, tags TEXT, time_slots TEXT, energy_score INTEGER, crowd_score INTEGER, conversation_score INTEGER, movement_score INTEGER, focus_score INTEGER, food_score INTEGER, live_music_score INTEGER, politics_score INTEGER, scene_score INTEGER, heritage_score INTEGER, games_score INTEGER, admission_decision TEXT, admission_reason TEXT, verification_status TEXT, score_confidence TEXT, source TEXT);
        CREATE TABLE verification_queue (queue_id INTEGER PRIMARY KEY AUTOINCREMENT, venue_id TEXT, issue TEXT, priority TEXT, status TEXT, notes TEXT);
        """)
        if venues:
            columns = [key for key in venues[0] if key not in {"latitude", "longitude", "opening_hours"}]
            placeholders = ",".join("?" for _ in columns)
            connection.executemany(f"INSERT OR REPLACE INTO venues ({','.join(columns)}) VALUES ({placeholders})", [[row.get(column) for column in columns] for row in venues])
        connection.executemany("INSERT INTO verification_queue (venue_id, issue, priority, status, notes) VALUES (?, ?, ?, ?, ?)", [(row.get("venue_id"), row.get("issue", "human_verification"), row.get("priority", "normal"), row.get("status", "open"), row.get("notes", "")) for row in queue])
        connection.commit()
    finally:
        connection.close()


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    keys = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

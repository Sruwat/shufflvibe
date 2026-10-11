from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .config import (
    ALLOWED_BOOLEAN, ALLOWED_DECISIONS, ALLOWED_SLOT_STATUS, ALLOWED_STATUS,
    SLOT_HEADERS, SOURCE_HEADERS, VENUE_HEADERS,
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    # Imported Excel tables can contain a blank spacer row before the review queue.
    return [row for row in rows if any((value or "").strip() for value in row.values())]


def _is_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")


def validate_rows(venues: list[dict[str, str]], slots: list[dict[str, str]], sources: list[dict[str, str]]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    venue_ids = [row.get("venue_id", "") for row in venues]
    if len(venue_ids) != len(set(venue_ids)):
        errors.append("Duplicate venue_id values found")
    slot_ids = [row.get("slot_id", "") for row in slots]
    if len(slot_ids) != len(set(slot_ids)):
        errors.append("Duplicate slot_id values found")
    known_ids = set(venue_ids)
    for row_number, row in enumerate(venues, start=2):
        if set(row) != set(VENUE_HEADERS):
            errors.append(f"Venues row {row_number} has unexpected headers")
        if row.get("status") not in ALLOWED_STATUS:
            warnings.append(f"Venues row {row_number}: unexpected status {row.get('status')!r}")
        if row.get("admission_decision") not in ALLOWED_DECISIONS:
            warnings.append(f"Venues row {row_number}: unexpected admission decision")
        for field in ("serves_food", "serves_alcohol", "outdoor_seating", "reservable", "live_music", "games_available"):
            if row.get(field, "") not in ALLOWED_BOOLEAN:
                warnings.append(f"Venues row {row_number}: {field} has invalid value {row.get(field)!r}")
        for field in ("latitude", "longitude"):
            value = row.get(field, "")
            if value not in ("", "Unknown"):
                try:
                    float(value)
                except ValueError:
                    errors.append(f"Venues row {row_number}: {field} is not numeric")
        for field in ("energy_score", "crowd_score", "conversation_score", "food_score", "scene_score", "live_music_score", "games_score", "heritage_score", "polish_score"):
            value = row.get(field, "")
            if value not in ("", "Unknown"):
                try:
                    score = float(value)
                    if not 0 <= score <= 100:
                        errors.append(f"Venues row {row_number}: {field} outside 0-100")
                except ValueError:
                    errors.append(f"Venues row {row_number}: {field} is not numeric")
        for field in ("official_website", "menu_url", "source_url"):
            value = row.get(field, "")
            if value not in ("", "Unknown") and not _is_url(value):
                warnings.append(f"Venues row {row_number}: {field} is not a URL")
    for row_number, row in enumerate(slots, start=2):
        if row.get("venue_id") not in known_ids:
            errors.append(f"Slot row {row_number}: unknown venue_id {row.get('venue_id')}")
        if row.get("slot_status") not in ALLOWED_SLOT_STATUS:
            warnings.append(f"Slot row {row_number}: unexpected slot_status")
        if row.get("slot_source_url") not in ("", "Unknown") and not _is_url(row.get("slot_source_url", "")):
            warnings.append(f"Slot row {row_number}: invalid slot_source_url")
    source_counts = Counter(row.get("venue_id") for row in sources)
    for venue_id in known_ids:
        if source_counts[venue_id] == 0:
            warnings.append(f"Venue {venue_id} has no source record")
    return {
        "venue_count": len(venues),
        "slot_count": len(slots),
        "source_count": len(sources),
        "duplicate_venue_ids": len(venue_ids) - len(set(venue_ids)),
        "errors": errors,
        "warnings": warnings,
    }


def write_report(report: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = ["SHUFFL South Delhi venue database validation report", "", f"Venues: {report['venue_count']}", f"Slots: {report['slot_count']}", f"Sources: {report['source_count']}", f"Errors: {len(report['errors'])}", f"Warnings: {len(report['warnings'])}", ""]
    if report["errors"]:
        lines += ["Errors:"] + [f"- {item}" for item in report["errors"]] + [""]
    if report["warnings"]:
        lines += ["Warnings:"] + [f"- {item}" for item in report["warnings"]]
    output.write_text("\n".join(lines), encoding="utf-8")

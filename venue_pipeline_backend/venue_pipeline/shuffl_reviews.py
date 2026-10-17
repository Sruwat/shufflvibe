from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Any


def load_reviews(path: Path | None) -> dict[str, dict[str, Any]]:
    """Load SHUFFL-owned reviews. Expected columns: google_place_id, rating, review_text, reviewed_at."""
    if not path or not path.exists():
        return {}
    grouped: dict[str, list[dict[str, Any]]] = {}
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            place_id = (row.get("google_place_id") or "").strip()
            if not place_id:
                continue
            try:
                rating = int(float(row.get("rating") or 0))
            except ValueError:
                rating = 0
            if 1 <= rating <= 5:
                grouped.setdefault(place_id, []).append({"rating": rating, "review_text": (row.get("review_text") or "").strip(), "reviewed_at": (row.get("reviewed_at") or "").strip()})
    result: dict[str, dict[str, Any]] = {}
    for place_id, rows in grouped.items():
        counts = Counter(row["rating"] for row in rows)
        result[place_id] = {"shuffl_review_count": len(rows), "shuffl_rating_mean": round(sum(row["rating"] for row in rows) / len(rows), 2), "shuffl_rating_distribution": {str(i): counts.get(i, 0) for i in range(1, 6)}, "shuffl_reviews": rows, "review_source": "shuffl_owned", "review_license_status": "owned", "review_confidence": "high" if len(rows) >= 20 else "medium"}
    return result


def empty_review_summary() -> dict[str, Any]:
    return {"shuffl_review_count": 0, "shuffl_rating_mean": None, "shuffl_rating_distribution": {str(i): 0 for i in range(1, 6)}, "shuffl_reviews": [], "review_source": "none", "review_license_status": "not_available", "review_confidence": "none"}

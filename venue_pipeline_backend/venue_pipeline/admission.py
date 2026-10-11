from __future__ import annotations

from collections import defaultdict
from statistics import quantiles
from typing import Any


def admit(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_type: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        details = row.get("google_details", {})
        rating = details.get("rating")
        if isinstance(rating, (int, float)):
            by_type[details.get("primaryType", "unknown")].append(float(rating))
    thresholds = {kind: (float(quantiles(values, n=20)[6]) if len(values) >= 8 else 4.0) for kind, values in by_type.items()}
    for row in rows:
        details = row.get("google_details", {})
        rating = details.get("rating")
        review_count = details.get("userRatingCount")
        kind = details.get("primaryType", "unknown")
        reasons: list[str] = []
        if not isinstance(rating, (int, float)):
            reasons.append("missing_rating")
        if not isinstance(review_count, int) or review_count < 200:
            reasons.append("review_count_below_200")
        if isinstance(rating, (int, float)) and rating < thresholds.get(kind, 4.0):
            reasons.append("rating_below_type_threshold")
        if details.get("businessStatus") not in (None, "OPERATIONAL"):
            reasons.append(f"business_status_{details.get('businessStatus')}")
        row["admission_decision"] = "Admitted" if not reasons else "Review"
        row["admission_reason"] = "meets_mvp_rules" if not reasons else ";".join(reasons)
        row["verification_status"] = "Human verification required"
    return rows

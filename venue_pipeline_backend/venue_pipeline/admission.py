from __future__ import annotations

from collections import defaultdict
from statistics import quantiles
from typing import Any

from .scoring import FACTORS

ADMISSION_POLICY_VERSION = "mvp-evidence-v2"
SUPPORTED_TYPES = {"bar", "night_club", "pub", "restaurant", "cafe", "nightclub"}
MIN_SCORE_COVERAGE = 5


def _identity_evidence(row: dict[str, Any]) -> tuple[str, list[str]]:
    official = row.get("official_data") or {}
    osm = row.get("osm_data") or {}
    if official.get("official_status") == "fetched" and official.get("official_name"):
        return "official_website", []
    if osm.get("name") and osm.get("match_confidence") in {"medium", "high"}:
        return "osm_secondary", []
    return "none", ["identity_source_missing"]


def _score_audit(row: dict[str, Any]) -> dict[str, Any]:
    scores = row.get("scores") or {}
    evidence = row.get("score_evidence") or {}
    not_specialised = set(row.get("not_specialised") or [])
    invalid_not_specialised = sorted(not_specialised.difference(FACTORS))
    covered = [factor for factor in FACTORS if evidence.get(factor) or factor in not_specialised]
    missing = [factor for factor in FACTORS if factor not in covered]
    invalid = []
    for factor in FACTORS:
        value = scores.get(factor)
        if value is None and factor in not_specialised:
            continue
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 100):
            invalid.append(factor)
    return {
        "required_factors": list(FACTORS),
        "covered_factors": covered,
        "missing_factors": missing,
        "invalid_factors": invalid,
        "invalid_not_specialised": invalid_not_specialised,
        "coverage_count": len(covered),
        "coverage_threshold": MIN_SCORE_COVERAGE,
    }


def _review_audit(row: dict[str, Any]) -> dict[str, Any]:
    review = row.get("shuffl_review_summary") or {}
    raw_count = review.get("shuffl_review_count")
    count = raw_count if isinstance(raw_count, int) and not isinstance(raw_count, bool) and raw_count >= 0 else 0
    source = review.get("review_source", "none")
    license_status = review.get("review_license_status", "not_available")
    malformed_count = raw_count is not None and count == 0 and raw_count not in (0, "0")
    valid = not malformed_count and (count == 0 or (source == "shuffl_owned" and license_status == "owned"))
    return {"source": source, "license_status": license_status, "count": count, "permanent_storage_allowed": valid, "invalid": not valid, "malformed_count": malformed_count}


def admit(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Apply strict admission without persisting Google review data."""
    by_type: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        details = row.get("google_details", {}) or {}
        rating = details.get("rating")
        if isinstance(rating, (int, float)):
            by_type[details.get("primaryType", "unknown")].append(float(rating))
    thresholds = {kind: (float(quantiles(values, n=20)[6]) if len(values) >= 8 else 4.0) for kind, values in by_type.items()}

    for row in rows:
        details = row.get("google_details", {}) or {}
        official = row.get("official_data") or {}
        rating = details.get("rating")
        review_count = details.get("userRatingCount")
        kind = str(details.get("primaryType", "unknown")).lower()
        hard_failures: list[str] = []
        evidence_gaps: list[str] = []
        if kind not in SUPPORTED_TYPES:
            (evidence_gaps if kind in {"", "unknown"} else hard_failures).append("category_missing" if kind in {"", "unknown"} else "unsupported_category")
        if not isinstance(rating, (int, float)):
            evidence_gaps.append("missing_rating")
        elif rating < thresholds.get(kind, 4.0):
            hard_failures.append("rating_below_type_threshold")
        if not isinstance(review_count, int):
            evidence_gaps.append("missing_review_count")
        elif review_count < 200:
            hard_failures.append("review_count_below_200")
        if details.get("businessStatus") not in (None, "OPERATIONAL"):
            hard_failures.append(f"business_status_{details.get('businessStatus')}")

        identity_source, identity_gaps = _identity_evidence(row)
        evidence_gaps.extend(identity_gaps)
        audit = _score_audit(row)
        if audit["invalid_factors"] or audit["invalid_not_specialised"]:
            hard_failures.append("invalid_score_values")
        if audit["coverage_count"] < MIN_SCORE_COVERAGE:
            evidence_gaps.append("score_evidence_coverage_below_threshold")

        fitout_year = official.get("fit_out_year")
        fitout_status = official.get("fit_out_status", "unknown")
        if official.get("official_status") != "fetched" or isinstance(fitout_year, bool) or not isinstance(fitout_year, int) or fitout_status not in {"exact", "estimated"}:
            evidence_gaps.append("fit_out_evidence_missing")
        elif fitout_year < 1900 or fitout_year > 2100:
            hard_failures.append("fit_out_year_invalid")

        review_audit = _review_audit(row)
        if review_audit["invalid"]:
            hard_failures.append("unlicensed_review_evidence")

        row["evidence_audit"] = {"policy_version": ADMISSION_POLICY_VERSION, "identity_source": identity_source, "official_status": official.get("official_status", "missing"), "osm_match": bool(row.get("osm_data")), "score_audit": audit, "review_audit": review_audit, "fit_out_status": fitout_status, "hard_failures": hard_failures, "evidence_gaps": sorted(set(evidence_gaps))}
        reasons = sorted(set(hard_failures + evidence_gaps))
        if hard_failures:
            row["admission_decision"] = "Rejected"
            row["admission_reason"] = ";".join(reasons)
            row["verification_status"] = "auto_rejected"
        elif evidence_gaps:
            row["admission_decision"] = "Insufficient evidence"
            row["admission_reason"] = ";".join(reasons)
            row["verification_status"] = "auto_insufficient_evidence"
        else:
            row["admission_decision"] = "Admitted"
            row["admission_reason"] = "meets_evidence_policy"
            row["verification_status"] = "auto_admitted"
    return rows

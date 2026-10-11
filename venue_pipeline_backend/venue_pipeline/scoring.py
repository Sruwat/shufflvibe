from __future__ import annotations

import re
from typing import Any

FACTORS = ("energy", "crowd", "conversation", "movement", "focus", "food", "live_music", "politics", "scene", "heritage", "games")
POSITIVE = {
    "energy": ("loud", "high energy", "party", "buzzy", "vibrant", "dj", "dance"),
    "crowd": ("crowded", "popular", "packed", "busy", "buzzing"),
    "conversation": ("quiet", "conversation", "intimate", "calm", "cozy"),
    "movement": ("dance", "dance floor", "dj", "club", "standing"),
    "focus": ("work", "laptop", "comfortable", "wifi", "calm"),
    "food": ("food", "dinner", "menu", "cuisine", "kitchen", "restaurant"),
    "live_music": ("live music", "band", "gig", "acoustic", "concert"),
    "politics": ("sports screening", "match", "news", "discussion"),
    "scene": ("rooftop", "skyline", "design", "stylish", "beautiful", "terrace"),
    "heritage": ("heritage", "historic", "old", "mansion", "haveli"),
    "games": ("games", "pool", "billiards", "bowling", "board game", "darts"),
}
TYPE_PRIORS = {"bar": {"energy": 58, "crowd": 55}, "night_club": {"energy": 78, "movement": 78}, "restaurant": {"food": 62, "conversation": 52}, "cafe": {"focus": 58, "conversation": 60}}


def _corpus(details: dict[str, Any]) -> str:
    parts: list[str] = []
    for review in details.get("reviews", []) or []:
        text = review.get("text", {}) if isinstance(review, dict) else {}
        parts.append(text.get("text", "") if isinstance(text, dict) else str(text))
    for key in ("editorialSummary", "generativeSummary"):
        value = details.get(key, {}) or {}
        parts.append(value.get("text", "") if isinstance(value, dict) else str(value))
    return " ".join(parts).lower()


def score(details: dict[str, Any]) -> dict[str, Any]:
    corpus = _corpus(details)
    primary = details.get("primaryType", "")
    scores: dict[str, int | None] = {}
    evidence: dict[str, list[str]] = {}
    for factor in FACTORS:
        base = TYPE_PRIORS.get(primary, {}).get(factor, 50)
        hits = [term for term in POSITIVE.get(factor, ()) if term in corpus]
        neg_hits = [term for term in POSITIVE.get(factor, ()) if f"no {term}" in corpus or f"not {term}" in corpus]
        if not corpus and factor not in TYPE_PRIORS.get(primary, {}):
            scores[factor] = None
            evidence[factor] = []
            continue
        value = base + min(30, len(hits) * 8) - min(25, len(neg_hits) * 10)
        if factor == "live_music" and details.get("liveMusic") is True:
            value, hits = 85, hits + ["structured:liveMusic=true"]
        if factor == "food" and any(details.get(key) is True for key in ("servesDinner", "servesBrunch", "servesDessert")):
            value, hits = max(value, 65), hits + ["structured:food-service"]
        if factor == "games" and details.get("goodForGroups") is True:
            value, hits = max(value, 58), hits + ["structured:goodForGroups"]
        scores[factor] = max(0, min(100, int(value)))
        evidence[factor] = hits
    return {"scores": scores, "score_evidence": evidence, "score_confidence": "medium" if corpus else "low"}


def fallback_metadata(details: dict[str, Any]) -> dict[str, Any]:
    """Create transparent, non-LLM metadata when Gemini quota is unavailable."""
    name = (details.get("displayName") or {}).get("text", "Venue")
    venue_type = details.get("primaryType", "venue").replace("_", " ")
    tags: list[str] = [venue_type]
    if details.get("servesDinner") or details.get("servesBrunch") or details.get("servesDessert"):
        tags.append("food")
    if details.get("servesBeer") or details.get("servesWine") or details.get("servesCocktails"):
        tags.append("alcohol")
    for key, tag in (("liveMusic", "live-music"), ("outdoorSeating", "outdoor-seating"), ("reservable", "reservable"), ("goodForGroups", "groups")):
        if details.get(key) is True:
            tags.append(tag)
    if details.get("priceLevel"):
        tags.append(str(details["priceLevel"]).lower().replace("price_level_", ""))
    summary = (details.get("editorialSummary") or details.get("generativeSummary") or {}).get("text", "")
    description = summary or f"{name} is listed on Google Places as a {venue_type}. Verify the current scene, menu, hours and suitability before publishing."
    return {
        "description": description,
        "tags": sorted(set(tags)),
        # Deliberately empty: a time-of-day mode must be supported by explicit evidence.
        "time_slots": [],
        "metadata_evidence": "Google structured fields/local fallback; verify manually",
    }

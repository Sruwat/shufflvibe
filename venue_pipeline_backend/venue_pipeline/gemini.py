from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


class GeminiError(RuntimeError):
    pass


class GeminiClient:
    def __init__(self, api_key: str | None = None, model: str | None = None, timeout: int = 60) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
        self.timeout = timeout
        if not self.api_key or self.api_key.startswith("PASTE_") or self.api_key == "replace_me":
            raise GeminiError("Set GEMINI_API_KEY before running Gemini scoring")

    def analyze(self, details: dict[str, Any]) -> dict[str, Any]:
        name = (details.get("displayName") or {}).get("text", "")
        reviews = []
        for review in details.get("reviews", []) or []:
            text = review.get("text", {}) if isinstance(review, dict) else {}
            review_text = text.get("text", "") if isinstance(text, dict) else str(text)
            if review_text:
                reviews.append(review_text[:1500])
        summaries = []
        for key in ("editorialSummary", "generativeSummary"):
            value = details.get(key, {}) or {}
            text = value.get("text", "") if isinstance(value, dict) else str(value)
            if text:
                summaries.append(text[:2000])
        payload = {
            "name": name,
            "primary_type": details.get("primaryType", ""),
            "types": details.get("types", []),
            "rating": details.get("rating"),
            "review_count": details.get("userRatingCount"),
            "structured_fields": {key: details.get(key) for key in (
                "priceLevel", "regularOpeningHours", "servesDinner", "servesBrunch", "servesDessert",
                "servesVegetarianFood", "servesBeer", "servesWine", "servesCocktails", "outdoorSeating",
                "reservable", "liveMusic", "goodForGroups", "businessStatus",
                "goodForWatchingSports",
            )},
            "reviews": reviews,
            "summaries": summaries,
        }
        prompt = f"""You are the SHUFFL venue scoring engine. Analyze this venue only from the supplied evidence.
Do not invent facts. If evidence is missing, use null and put the field in unknown_fields.
Return JSON only with this exact shape:
{{
  \"description\": \"short factual app description\",
  \"tags\": [\"short lowercase tags\"],
  \"scores\": {{\"energy\": 0, \"crowd\": 0, \"conversation\": 0, \"movement\": 0, \"focus\": 0, \"food\": 0, \"live_music\": 0, \"politics\": 0, \"scene\": 0, \"heritage\": 0, \"games\": 0}},
  \"evidence\": {{\"energy\": [\"short evidence\"]}},
  \"time_slots\": [{{\"days\": \"\", \"from_time\": \"\", \"to_time\": \"\", \"type\": \"\", \"evidence\": \"\"}}],
  \"unknown_fields\": [\"field names\"],
  \"confidence\": \"low|medium|high\"
}}
Scores must be integers 0-100. Treat silence as unknown, not zero. Only create a time slot when the evidence explicitly names a day or time.

Evidence:
{json.dumps(payload, ensure_ascii=False)}"""
        body = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"},
        }
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        request = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), method="POST", headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                response_body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise GeminiError(f"Gemini {exc.code}: {error_body[:800]}") from exc
        except urllib.error.URLError as exc:
            raise GeminiError(f"Gemini network error: {exc.reason}") from exc
        try:
            text = response_body["candidates"][0]["content"]["parts"][0]["text"]
            result = json.loads(text.strip().removeprefix("```json").removesuffix("```").strip())
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise GeminiError("Gemini returned an invalid JSON scoring response") from exc
        return self._validate(result)

    @staticmethod
    def _validate(result: dict[str, Any]) -> dict[str, Any]:
        scores = result.get("scores", {}) if isinstance(result, dict) else {}
        clean_scores = {}
        for factor in ("energy", "crowd", "conversation", "movement", "focus", "food", "live_music", "politics", "scene", "heritage", "games"):
            value = scores.get(factor)
            clean_scores[factor] = max(0, min(100, int(value))) if isinstance(value, (int, float)) else None
        return {
            "description": str(result.get("description", ""))[:500],
            "tags": [str(tag).lower().strip() for tag in result.get("tags", []) if str(tag).strip()][:12],
            "scores": clean_scores,
            "score_evidence": result.get("evidence", {}) if isinstance(result.get("evidence", {}), dict) else {},
            "time_slots": result.get("time_slots", []) if isinstance(result.get("time_slots", []), list) else [],
            "unknown_fields": result.get("unknown_fields", []) if isinstance(result.get("unknown_fields", []), list) else [],
            "score_confidence": result.get("confidence", "low") if result.get("confidence") in {"low", "medium", "high"} else "low",
        }

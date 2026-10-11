from __future__ import annotations

import json
import os
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from .models import Area


class GooglePlacesError(RuntimeError):
    pass


BASE_URL = "https://places.googleapis.com/v1"
DISCOVERY_FIELDS = "places.id,places.displayName,places.formattedAddress,places.location,places.googleMapsUri,places.primaryType,places.types"
DETAIL_FIELDS = ",".join([
    "id", "displayName", "formattedAddress", "location", "googleMapsUri", "websiteUri",
    "nationalPhoneNumber", "primaryType", "primaryTypeDisplayName", "types", "rating",
    "userRatingCount", "reviews", "editorialSummary", "generativeSummary", "priceLevel",
    "regularOpeningHours", "businessStatus", "servesDinner", "servesBrunch", "servesCoffee",
    "servesDessert", "servesVegetarianFood", "servesBeer", "servesWine", "servesCocktails",
    "outdoorSeating", "reservable", "liveMusic", "goodForGroups", "allowsDogs",
])
SEARCH_TYPES = ("bar", "night_club", "pub", "restaurant", "cafe")


class GooglePlacesClient:
    def __init__(self, api_key: str | None = None, timeout: int = 45) -> None:
        self.api_key = api_key or os.getenv("GOOGLE_PLACES_API_KEY") or os.getenv("GOOGLE_MAPS_API_KEY")
        self.timeout = timeout
        # Google Places Details is commonly limited to about 600 requests/minute.
        # Serialize the start of detail requests so concurrent workers do not burst
        # past the per-minute quota.
        self._details_rate_lock = threading.Lock()
        self._next_details_at = 0.0
        self._details_interval_seconds = 0.16
        if not self.api_key or self.api_key.startswith("PASTE_") or self.api_key == "replace_me":
            raise GooglePlacesError("Set GOOGLE_PLACES_API_KEY before running the Google stage")

    def _post(self, path: str, payload: dict[str, Any], field_mask: str) -> dict[str, Any]:
        request = urllib.request.Request(
            f"{BASE_URL}/{path}", data=json.dumps(payload).encode("utf-8"), method="POST",
            headers={"Content-Type": "application/json", "X-Goog-Api-Key": self.api_key, "X-Goog-FieldMask": field_mask},
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise GooglePlacesError(f"Google Places {exc.code}: {body[:800]}") from exc
        except urllib.error.URLError as exc:
            raise GooglePlacesError(f"Google Places network error: {exc.reason}") from exc

    def nearby(self, area: Area, included_type: str) -> list[dict[str, Any]]:
        payload = {
            "includedTypes": [included_type],
            "maxResultCount": 20,
            "languageCode": "en",
            "locationRestriction": {"circle": {"center": {"latitude": area.latitude, "longitude": area.longitude}, "radius": float(area.radius_meters)}},
        }
        return self._post("places:searchNearby", payload, DISCOVERY_FIELDS).get("places", [])

    def text_search(self, query: str) -> list[dict[str, Any]]:
        payload = {"textQuery": query, "pageSize": 1, "languageCode": "en"}
        fields = "places.id,places.displayName,places.formattedAddress,places.location,places.types"
        return self._post("places:searchText", payload, fields).get("places", [])

    def details(self, place_id: str) -> dict[str, Any]:
        for attempt in range(3):
            with self._details_rate_lock:
                now = time.monotonic()
                wait_for = self._next_details_at - now
                if wait_for > 0:
                    time.sleep(wait_for)
                self._next_details_at = time.monotonic() + self._details_interval_seconds
            request = urllib.request.Request(
                f"{BASE_URL}/places/{place_id}", method="GET",
                headers={"X-Goog-Api-Key": self.api_key, "X-Goog-FieldMask": DETAIL_FIELDS},
            )
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    return json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")
                if exc.code == 429 and attempt < 2:
                    # Let Google's fixed one-minute quota window roll over.
                    time.sleep(65)
                    continue
                raise GooglePlacesError(f"Google Place Details {exc.code}: {body[:800]}") from exc


def discover(client: GooglePlacesClient, areas: list[Area], max_workers: int = 8) -> list[dict[str, Any]]:
    unique: dict[str, dict[str, Any]] = {}
    tasks = [(area, category) for area in areas for category in SEARCH_TYPES]
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(client.nearby, area, category): (area, category) for area, category in tasks}
        for index, future in enumerate(as_completed(futures), start=1):
            area, category = futures[future]
            try:
                places = future.result()
            except Exception as exc:
                print(f"Warning: Nearby Search failed for {area.area}/{category}: {exc}", flush=True)
                continue
            for place in places:
                place_id = place.get("id") or place.get("name", "").removeprefix("places/")
                if place_id:
                    unique.setdefault(place_id, {"google_place_id": place_id, "discovered_area": area.area, "discovered_city": area.city, "discovered_type": category, "discovery": place})
            if index % 20 == 0 or index == len(tasks):
                print(f"Nearby Search progress: {index}/{len(tasks)}", flush=True)
    return list(unique.values())

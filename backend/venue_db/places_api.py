from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Iterable


BASE_URL = "https://places.googleapis.com/v1"

# Durable policy: the caller may persist only id and maps URL from these responses.
DISCOVERY_FIELDS = "places.id,places.name,places.googleMapsUri,nextPageToken"
DETAIL_FIELDS = ",".join([
    "id", "name", "googleMapsUri", "displayName", "formattedAddress", "location",
    "primaryType", "primaryTypeDisplayName", "types", "websiteUri",
    "nationalPhoneNumber", "regularOpeningHours", "priceLevel", "priceRange",
    "businessStatus", "servesDinner", "servesBrunch", "servesCoffee", "servesDessert",
    "servesVegetarianFood", "servesBeer", "servesWine", "servesCocktails",
    "outdoorSeating", "reservable", "liveMusic", "goodForGroups",
])


class PlacesApiError(RuntimeError):
    pass


class PlacesClient:
    def __init__(self, api_key: str | None = None, timeout: int = 30) -> None:
        self.api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY")
        self.timeout = timeout
        if not self.api_key:
            raise PlacesApiError("GOOGLE_MAPS_API_KEY is not set")

    def _request(self, path: str, payload: dict[str, Any], field_mask: str) -> dict[str, Any]:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{BASE_URL}/{path}", data=data, method="POST",
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.api_key,
                "X-Goog-FieldMask": field_mask,
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise PlacesApiError(f"Places API {exc.code}: {body[:500]}") from exc
        except urllib.error.URLError as exc:
            raise PlacesApiError(f"Places API network error: {exc.reason}") from exc

    def text_search(self, query: str, page_size: int = 20) -> list[dict[str, Any]]:
        response = self._request(
            "places:searchText",
            {"textQuery": query, "pageSize": min(max(page_size, 1), 20), "languageCode": "en"},
            DISCOVERY_FIELDS,
        )
        # Return in memory only. The caller intentionally extracts only id and maps URL.
        return response.get("places", [])

    def details(self, place_id: str) -> dict[str, Any]:
        # Details (New) is a GET endpoint. It still requires an explicit field mask.
        req = urllib.request.Request(
            f"{BASE_URL}/places/{place_id}", method="GET",
            headers={
                "X-Goog-Api-Key": self.api_key,
                "X-Goog-FieldMask": DETAIL_FIELDS,
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise PlacesApiError(f"Places Details API {exc.code}: {body[:500]}") from exc

    @staticmethod
    def durable_identifier(place: dict[str, Any]) -> dict[str, str]:
        place_id = place.get("id") or place.get("name", "").removeprefix("places/")
        return {
            "google_place_id": place_id,
            "google_maps_url": place.get("googleMapsUri", ""),
        }


def iter_queries(areas: Iterable[str], categories: Iterable[str]) -> Iterable[str]:
    for area in areas:
        for category in categories:
            yield f"{category} in {area}, South Delhi, India"

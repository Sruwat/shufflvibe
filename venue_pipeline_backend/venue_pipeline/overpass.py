from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from typing import Any

from .models import Area


class OverpassError(RuntimeError):
    pass


ENDPOINT = os.getenv("OVERPASS_ENDPOINT", "https://overpass-api.de/api/interpreter")
FALLBACK_ENDPOINTS = [
    ENDPOINT,
    "https://overpass.kumi.systems/api/interpreter",
]
TIMEOUT_SECONDS = int(os.getenv("OVERPASS_TIMEOUT_SECONDS", "25"))


def discover_with_report(areas: list[Area], endpoint: str = ENDPOINT) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for area in areas:
        if area.latitude is None or area.longitude is None:
            continue
        query = (
            f"[out:json][timeout:60];"
            f"nwr[amenity~\"^(bar|pub|nightclub|restaurant|cafe)$\"]"
            f"(around:{area.radius_meters},{area.latitude},{area.longitude});"
            "out center tags;"
        )
        data = urllib.parse.urlencode({"data": query}).encode("utf-8")
        request = urllib.request.Request(endpoint, data=data, method="POST", headers={"User-Agent": "SHUFFL-Venue-Pipeline/1.0", "Content-Type": "application/x-www-form-urlencoded"})
        payload = None
        area_error = None
        for candidate_endpoint in dict.fromkeys(FALLBACK_ENDPOINTS):
            request = urllib.request.Request(candidate_endpoint, data=data, method="POST", headers={"User-Agent": "SHUFFL-Venue-Pipeline/1.0", "Content-Type": "application/x-www-form-urlencoded"})
            try:
                with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                break
            except Exception as exc:
                area_error = exc
        if payload is None:
            errors.append(f"{area.area}: {area_error}")
            continue
        for element in payload.get("elements", []):
            tags = element.get("tags", {})
            osm_id = f"{element.get('type')}:{element.get('id')}"
            center = element.get("center", {})
            latitude = element.get("lat", center.get("lat"))
            longitude = element.get("lon", center.get("lon"))
            if not tags.get("name") or latitude is None or longitude is None:
                continue
            rows[osm_id] = {
                "osm_id": osm_id,
                "name": tags.get("name", ""),
                "amenity": tags.get("amenity", ""),
                "latitude": float(latitude),
                "longitude": float(longitude),
                "address": ", ".join(filter(None, [tags.get("addr:housenumber"), tags.get("addr:street"), tags.get("addr:suburb")])),
                "website": tags.get("website", tags.get("contact:website", "")),
                "phone": tags.get("phone", tags.get("contact:phone", "")),
                "area": area.area,
                "city": area.city,
                "source": "OpenStreetMap Overpass",
            }
    if not rows and errors:
        raise OverpassError("All Overpass endpoints failed: " + " | ".join(errors[:3]))
    return list(rows.values()), [{"stage": "overpass", "error": error} for error in errors]


def discover(areas: list[Area], endpoint: str = ENDPOINT) -> list[dict[str, Any]]:
    """Backward-compatible discovery API returning only OSM candidates."""
    rows, _ = discover_with_report(areas, endpoint)
    return rows

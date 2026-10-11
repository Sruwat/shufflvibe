from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from .config import OSM_AMENITIES, SOUTH_DELHI_BBOX

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
USER_AGENT = "SHUFFL-Venue-Database/1.0"


class OsmApiError(RuntimeError):
    pass


def _bbox_chunks(bbox: tuple[float, float, float, float], rows: int = 2, cols: int = 3):
    south, west, north, east = bbox
    lat_step = (north - south) / rows
    lon_step = (east - west) / cols
    for r in range(rows):
        for c in range(cols):
            yield (
                south + r * lat_step,
                west + c * lon_step,
                south + (r + 1) * lat_step,
                west + (c + 1) * lon_step,
            )


def _query(bbox: tuple[float, float, float, float]) -> list[dict[str, Any]]:
    south, west, north, east = bbox
    amenities = "|".join(OSM_AMENITIES)
    query = (
        f'[out:json][timeout:180];('
        f'nwr["amenity"~"^({amenities})$"]({south},{west},{north},{east});'
        f');out center tags;'
    )
    payload = urllib.parse.urlencode({"data": query}).encode("utf-8")
    request = urllib.request.Request(
        OVERPASS_URL,
        data=payload,
        method="POST",
        headers={"User-Agent": USER_AGENT, "Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(request, timeout=240) as response:
            return json.loads(response.read().decode("utf-8")).get("elements", [])
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        raise OsmApiError(str(exc)) from exc


def _point(element: dict[str, Any]) -> tuple[float | None, float | None]:
    if element.get("lat") is not None and element.get("lon") is not None:
        return element["lat"], element["lon"]
    center = element.get("center") or {}
    return center.get("lat"), center.get("lon")


def normalise(element: dict[str, Any]) -> dict[str, Any] | None:
    tags = element.get("tags") or {}
    name = (tags.get("name") or tags.get("name:en") or "").strip()
    lat, lon = _point(element)
    if not name or lat is None or lon is None:
        return None
    element_id = f"{element.get('type', 'nwr')}/{element.get('id')}"
    osm_url = f"https://www.openstreetmap.org/{element.get('type', 'node')}/{element.get('id')}"
    return {
        "osm_id": element_id,
        "osm_url": osm_url,
        "venue_name": name,
        "latitude": lat,
        "longitude": lon,
        "address": ", ".join(x for x in [tags.get("addr:housenumber"), tags.get("addr:street"), tags.get("addr:suburb"), tags.get("addr:city")] if x),
        "area": tags.get("addr:suburb") or tags.get("addr:district") or "",
        "official_website": tags.get("website") or tags.get("contact:website") or "",
        "phone": tags.get("phone") or tags.get("contact:phone") or "",
        "opening_hours": tags.get("opening_hours") or "",
        "cuisine": tags.get("cuisine") or "",
        "amenity": tags.get("amenity") or "",
        "outdoor_seating": tags.get("outdoor_seating") or "",
        "reservable": tags.get("reservable") or "",
        "description": tags.get("description") or "",
        "source_url": osm_url,
    }


def discover(bbox: tuple[float, float, float, float] = SOUTH_DELHI_BBOX, pause_seconds: float = 2.0) -> list[dict[str, Any]]:
    """Discover named OSM venue candidates in small chunks with conservative retries."""
    rows: dict[str, dict[str, Any]] = {}
    for chunk in _bbox_chunks(bbox):
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                for element in _query(chunk):
                    row = normalise(element)
                    if row:
                        rows[row["osm_id"]] = row
                last_error = None
                break
            except OsmApiError as exc:
                last_error = exc
                time.sleep(3 * (attempt + 1))
        if last_error:
            print(f"OSM chunk failed after retries: {chunk}: {last_error}")
        time.sleep(pause_seconds)
    return sorted(rows.values(), key=lambda row: (row.get("area", ""), row["venue_name"].lower()))

from __future__ import annotations

import csv
import json
import os
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

from .models import Area, row_to_area


class AreaError(RuntimeError):
    pass


def load_areas(path: Path) -> list[Area]:
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload.get("areas", payload) if isinstance(payload, dict) else payload
    else:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
    if not rows:
        raise AreaError(f"No areas found in {path}")
    areas = [row_to_area({str(k): "" if v is None else str(v) for k, v in row.items()}) for row in rows]
    for area in areas:
        if not area.area or not area.city:
            raise AreaError("Every area needs at least area and city")
        if area.radius_meters <= 0:
            raise AreaError(f"Radius must be positive for {area.area}")
    return areas


def geocode_missing(areas: list[Area], user_agent: str, sleep_seconds: float = 1.05) -> list[Area]:
    headers = {"User-Agent": user_agent, "Accept": "application/json"}
    missing: list[Area] = []
    for index, area in enumerate(areas):
        if area.latitude is not None and area.longitude is not None:
            continue
        area.geocode_attempts = []
        query = ", ".join(part for part in (area.area, area.city, area.state, "India") if part)
        params = urllib.parse.urlencode({"format": "jsonv2", "q": query, "limit": 1})
        request = urllib.request.Request(f"https://nominatim.openstreetmap.org/search?{params}", headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                results = json.loads(response.read().decode("utf-8"))
            if results:
                area.latitude = float(results[0]["lat"])
                area.longitude = float(results[0]["lon"])
                area.geocode_source = "OpenStreetMap Nominatim"
                area.geocode_attempts.append("nominatim:success")
            else:
                area.geocode_attempts.append("nominatim:no_result")
                missing.append(area)
        except Exception as exc:
            area.geocode_attempts.append(f"nominatim:error:{type(exc).__name__}")
            missing.append(area)
        if index < len(areas) - 1:
            time.sleep(sleep_seconds)
    if missing:
        try:
            geocode_with_google(missing)
        except Exception as exc:
            for area in missing:
                area.geocode_attempts = (area.geocode_attempts or []) + [f"google_text:unavailable:{type(exc).__name__}"]
    still_missing = [area for area in areas if area.latitude is None or area.longitude is None]
    if still_missing:
        geocode_with_overpass(still_missing, user_agent)
    unresolved = [area.area for area in areas if area.latitude is None or area.longitude is None]
    if unresolved:
        raise AreaError("Unable to resolve coordinates after Nominatim, Google Text Search, and Overpass: " + ", ".join(unresolved))
    return areas


def geocode_with_google(areas: list[Area]) -> list[Area]:
    from .google_places import GooglePlacesClient, GooglePlacesError

    client = GooglePlacesClient()
    for index, area in enumerate(areas):
        if area.latitude is not None and area.longitude is not None:
            continue
        query = ", ".join(part for part in (area.area, area.city, area.state, "India") if part)
        try:
            results = client.text_search(query)
        except GooglePlacesError as exc:
            area.geocode_attempts = (area.geocode_attempts or []) + [f"google_text:error:{str(exc)[:120]}"]
            continue
        if not results or not results[0].get("location"):
            area.geocode_attempts = (area.geocode_attempts or []) + ["google_text:no_result"]
            continue
        location = results[0]["location"]
        area.latitude = float(location["latitude"])
        area.longitude = float(location["longitude"])
        area.geocode_source = "Google Places Text Search fallback"
        area.geocode_attempts = (area.geocode_attempts or []) + ["google_text:success"]
        if index < len(areas) - 1:
            time.sleep(0.05)
    return areas


def geocode_with_overpass(areas: list[Area], user_agent: str) -> list[Area]:
    missing = [area for area in areas if area.latitude is None or area.longitude is None]
    if not missing:
        return areas
    endpoint = os.getenv("OVERPASS_ENDPOINT", "https://overpass-api.de/api/interpreter")
    city_boxes = {
        "Delhi": (28.40, 76.85, 28.90, 77.35),
        "Gurugram": (28.25, 76.85, 28.65, 77.25),
        "Noida": (28.45, 77.25, 28.75, 77.50),
        "Greater Noida": (28.25, 77.35, 28.65, 77.75),
        "Ghaziabad": (28.55, 77.30, 28.90, 77.65),
        "Faridabad": (28.25, 77.15, 28.55, 77.55),
        "Meerut": (28.85, 77.50, 29.20, 77.90),
    }
    elements: list[dict] = []
    grouped: dict[tuple[str, tuple[float, float, float, float]], list[str]] = {}
    for area in missing:
        bbox = city_boxes.get(area.city, (27.0, 74.0, 30.5, 79.0))
        grouped.setdefault((area.city, bbox), []).append(area.area)
    for (city, bbox), city_names in grouped.items():
        for start in range(0, len(city_names), 10):
            names = city_names[start:start + 10]
            pattern = "|".join(re.escape(name) for name in names)
            south, west, north, east = bbox
            query = (
                "[out:json][timeout:120];"
                f"nwr[\"name\"~\"^({pattern})$\"]({south},{west},{north},{east});"
                "out center tags;"
            )
            request = urllib.request.Request(
                endpoint,
                data=urllib.parse.urlencode({"data": query}).encode("utf-8"),
                method="POST",
                headers={"User-Agent": "SHUFFL-Venue-Pipeline/1.0", "Content-Type": "application/x-www-form-urlencoded"},
            )
            try:
                with urllib.request.urlopen(request, timeout=180) as response:
                    elements.extend(json.loads(response.read().decode("utf-8")).get("elements", []))
            except Exception as exc:
                raise AreaError(f"Overpass fallback geocoding failed for {city}: {exc}") from exc
            if start + 10 < len(city_names):
                time.sleep(1.0)
    candidates: dict[str, list[tuple[int, float, float]]] = {}
    preferred_places = {"city", "town", "suburb", "neighbourhood", "quarter", "district", "village"}
    for element in elements:
        tags = element.get("tags", {})
        name = tags.get("name", "")
        center = element.get("center", {})
        latitude = element.get("lat", center.get("lat"))
        longitude = element.get("lon", center.get("lon"))
        if not name or latitude is None or longitude is None:
            continue
        score = 2 if tags.get("place") in preferred_places else 1 if tags.get("boundary") else 0
        candidates.setdefault(name, []).append((score, float(latitude), float(longitude)))
    unresolved = []
    for area in missing:
        choices = candidates.get(area.area, [])
        if not choices:
            unresolved.append(area.area)
            continue
        _, area.latitude, area.longitude = sorted(choices, reverse=True)[0]
        area.geocode_source = "OpenStreetMap Overpass fallback"
        area.geocode_attempts = (area.geocode_attempts or []) + ["overpass:success"]
    if unresolved:
        raise AreaError("No OSM coordinate found for: " + ", ".join(unresolved))
    return areas

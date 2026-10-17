from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class Area:
    area: str
    city: str
    state: str
    latitude: float | None = None
    longitude: float | None = None
    radius_meters: int = 3000
    priority: str = "normal"
    geocode_source: str = "manual"
    geocode_attempts: list[str] | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def row_to_area(row: dict[str, str]) -> Area:
    def number(name: str) -> float | None:
        value = (row.get(name) or "").strip()
        return float(value) if value else None

    radius = (row.get("radius_meters") or "3000").strip()
    return Area(
        area=(row.get("area") or "").strip(),
        city=(row.get("city") or "").strip(),
        state=(row.get("state") or "").strip(),
        latitude=number("latitude"),
        longitude=number("longitude"),
        radius_meters=int(float(radius)),
        priority=(row.get("priority") or "normal").strip() or "normal",
        geocode_attempts=None,
    )

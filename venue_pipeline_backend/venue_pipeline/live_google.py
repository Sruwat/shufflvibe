from __future__ import annotations

from typing import Any

from .google_places import GooglePlacesClient


def fetch_for_display(place_id: str, client: GooglePlacesClient | None = None) -> dict[str, Any]:
    """Fetch current Google fields for a venue screen without persisting them."""
    places = client or GooglePlacesClient()
    return places.details(place_id)

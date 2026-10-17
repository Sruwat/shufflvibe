from __future__ import annotations

from typing import Any

from .google_places import GooglePlacesClient


def fetch_for_display(place_id: str, client: GooglePlacesClient | None = None) -> dict[str, Any]:
    """Fetch current Google fields for a venue screen without persisting them.

    The normalized keys make the UI independent of Google's response shape. The
    returned object must remain request-scoped; callers must not write it to the
    durable venue tables.
    """
    places = client or GooglePlacesClient()
    details = places.details(place_id)
    location = details.get("location") or {}
    return {
        "google_place_id": place_id,
        "name": (details.get("displayName") or {}).get("text", ""),
        "address": details.get("formattedAddress", ""),
        "latitude": location.get("latitude"),
        "longitude": location.get("longitude"),
        "map_url": details.get("googleMapsUri", f"https://www.google.com/maps/search/?api=1&query=Google&query_place_id={place_id}"),
        "rating": details.get("rating"),
        "review_count": details.get("userRatingCount"),
        "reviews": details.get("reviews", []),
        "opening_hours": details.get("regularOpeningHours", {}),
        "price_level": details.get("priceLevel"),
        "photos": details.get("photos", []),
        "website": details.get("websiteUri", ""),
        "fetched_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
    }

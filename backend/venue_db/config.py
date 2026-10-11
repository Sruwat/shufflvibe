from __future__ import annotations

SOUTH_DELHI_AREAS = [
    "Hauz Khas", "Green Park", "SDA", "Saket", "Mehrauli", "Qutub",
    "Malviya Nagar", "Greater Kailash", "Defence Colony", "South Extension",
    "Lajpat Nagar", "Vasant Kunj", "Aerocity", "Chattarpur", "Nehru Place",
    "Kalkaji", "CR Park", "Kailash Colony", "Panchsheel Park",
    "Safdarjung Enclave", "Anand Lok", "Vasant Vihar", "Chanakyapuri",
]

SEARCH_CATEGORIES = [
    "restaurant", "cafe", "bar", "pub", "rooftop restaurant", "night club",
    "live music venue", "lounge", "brewery", "sports bar", "game bar",
    "premium casual dining",
]

# Locked MVP discovery stack. OSM is used for broad candidate discovery; Foursquare and
# public official pages are enrichment/verification sources. Google Maps is deliberately not
# scraped. The catchment is intentionally a little wider than a single neighbourhood because
# the SHUFFL spec's South Delhi pass includes Aerocity, Vasant Kunj and the southern districts.
SOUTH_DELHI_BBOX = (28.45, 76.80, 28.65, 77.30)  # south, west, north, east
OSM_AMENITIES = ("bar", "pub", "nightclub", "restaurant", "cafe")
FOURSQUARE_QUERIES = (
    "bar", "pub", "nightclub", "restaurant", "cafe", "lounge",
    "rooftop restaurant", "live music", "brewery", "sports bar", "game bar",
)

CANONICAL_TYPES = [
    "table for the night", "quiet bar", "buzzy restaurant", "pub", "games bar",
    "games pub", "live room", "lounge / rooftop", "club", "open ground",
    "big loud bar", "match bar",
]

VENUE_HEADERS = [
    "venue_id", "venue_name", "city", "area", "address", "latitude", "longitude",
    "osm_id", "google_place_id", "google_maps_url", "official_website", "phone",
    "venue_type", "price_band", "opening_hours", "serves_food", "serves_alcohol",
    "outdoor_seating", "reservable", "live_music", "games_available", "status",
    "operator_class", "fitout_year_or_estimate", "description", "primary_photo_url",
    "menu_url", "energy_score", "crowd_score", "conversation_score", "food_score",
    "scene_score", "live_music_score", "games_score", "heritage_score", "polish_score",
    "tags", "admission_decision", "admission_reason", "confidence", "source",
    "source_url", "source_date", "last_verified_date", "notes",
]

SLOT_HEADERS = [
    "slot_id", "venue_id", "days", "from_time", "to_time", "time_based_type",
    "energy_score", "crowd_score", "conversation_score", "food_score", "scene_score",
    "live_music_score", "games_score", "heritage_score", "polish_score", "slot_status",
    "slot_source", "slot_source_url", "slot_source_date", "confidence", "notes",
]

SOURCE_HEADERS = [
    "source_id", "venue_id", "source_type", "source_url", "source_title",
    "fields_supported", "source_date", "access_date", "reliability",
    "license_or_usage_note", "researcher_notes",
]

ALLOWED_STATUS = {"Active", "Closed", "Unverified", "Unknown"}
ALLOWED_DECISIONS = {"Admitted", "Rejected", "Review", "Unknown"}
ALLOWED_SLOT_STATUS = {"Confirmed", "Estimated", "Gold", "Unknown"}
ALLOWED_BOOLEAN = {"Yes", "No", "Unknown", ""}

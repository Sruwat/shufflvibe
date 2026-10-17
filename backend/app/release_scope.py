"""Runtime contract for the locked MVP catalogue and deferred features."""

import os
from typing import Any


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def release_scope() -> dict[str, Any]:
    return {
        "release": "mvp",
        "contract_version": "venue-dto-v1",
        "venue_catalogue": {
            "locked": _truthy(os.getenv("VENUE_PIPELINE_LOCKED")),
            "source": "published_venue_api",
            "opening_hours": "display_time_live",
            "google_reviews_persisted": False,
        },
        "features": {
            "gold_campaign": False,
            "messages_shuffl": False,
            "group_insights": False,
            "reservations": False,
            "automatic_outing_plan": False,
        },
    }

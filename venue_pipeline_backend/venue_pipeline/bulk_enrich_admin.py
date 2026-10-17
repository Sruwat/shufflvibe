"""Checkpointed Google Places Details enrichment for the admin venue store.

This is intentionally separate from discovery: it enriches the existing
canonical place-id set without creating/deleting venues or changing editorial
admission/publication decisions.
"""

from __future__ import annotations

import argparse
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import text

from backend.app.admin_store import AdminStore
from .google_places import GooglePlacesClient, GooglePlacesError


ROOT = Path(__file__).resolve().parents[2]
CHECKPOINT = ROOT / "backend" / "data" / "google-enrichment-checkpoint.json"


def load_env() -> None:
    for path in (ROOT / "backend" / ".env", ROOT / "venue_pipeline_backend" / ".env"):
        if not path.exists():
            continue
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_checkpoint() -> dict:
    if not CHECKPOINT.exists():
        return {"completed": [], "failed": {}}
    try:
        return json.loads(CHECKPOINT.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"completed": [], "failed": {}}


def write_checkpoint(value: dict) -> None:
    CHECKPOINT.parent.mkdir(parents=True, exist_ok=True)
    temporary = CHECKPOINT.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(CHECKPOINT)


def selected_live(details: dict) -> dict:
    """Persist only the normalized display payload, never the API key/raw HTTP response."""
    fields = (
        "id", "displayName", "formattedAddress", "location", "googleMapsUri", "websiteUri",
        "nationalPhoneNumber", "primaryType", "primaryTypeDisplayName", "types", "rating",
        "userRatingCount", "reviews", "editorialSummary", "generativeSummary", "priceLevel",
        "photos", "regularOpeningHours", "businessStatus", "servesDinner", "servesBrunch",
        "servesCoffee", "servesDessert", "servesVegetarianFood", "servesBeer", "servesWine",
        "servesCocktails", "outdoorSeating", "reservable", "liveMusic", "goodForGroups",
        "allowsDogs", "goodForWatchingSports",
    )
    return {key: details[key] for key in fields if key in details}


def persist(store: AdminStore, venue_id: str, details: dict) -> None:
    live = selected_live(details)
    name = ((live.get("displayName") or {}).get("text") or "").strip()
    website = str(live.get("websiteUri") or "").strip()
    maps_url = str(live.get("googleMapsUri") or "").strip()
    with store.engine.begin() as conn:
        row = conn.execute(text("SELECT data_json, display_name, official_url, google_lookup_url FROM admin_venues WHERE venue_id=:venue_id"), {"venue_id": venue_id}).mappings().first()
        if not row:
            return
        data = json.loads(row["data_json"] or "{}")
        # Google details are display-time enrichment only. Keep provenance and
        # stable links, but never write Google reviews, hours, coordinates,
        # ratings, addresses or photos into the durable venue record.
        for key in ("google_live_cache", "google_live_retrieved_at", "google_rating", "google_reviews", "google_address", "google_hours", "latitude", "longitude"):
            data.pop(key, None)
        data["google_data_status"] = "live_details_available"
        data["google_photo_rights"] = "google_display_only"
        display_name = name or row["display_name"] or ""
        official_url = row["official_url"] or website
        lookup_url = row["google_lookup_url"] or maps_url
        conn.execute(text("UPDATE admin_venues SET display_name=:display_name, official_url=:official_url, google_lookup_url=:google_lookup_url, data_json=:data_json, updated_at=:updated_at WHERE venue_id=:venue_id"), {"venue_id": venue_id, "display_name": display_name, "official_url": official_url, "google_lookup_url": lookup_url, "data_json": json.dumps(data, ensure_ascii=False), "updated_at": now()})


def main() -> int:
    load_env()
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="0 means all existing venue IDs")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--retry-failed", action="store_true")
    args = parser.parse_args()
    store = AdminStore()
    checkpoint = read_checkpoint()
    completed = set(checkpoint.get("completed", []))
    failed = dict(checkpoint.get("failed", {}))
    with store.engine.connect() as conn:
        rows = conn.execute(text("SELECT venue_id, google_place_id FROM admin_venues WHERE google_place_id IS NOT NULL AND google_place_id <> '' ORDER BY venue_id")).mappings().all()
    pending = [dict(row) for row in rows if row["venue_id"] not in completed and (args.retry_failed or row["venue_id"] not in failed)]
    if args.limit:
        pending = pending[:args.limit]
    print(f"Google enrichment pending: {len(pending)} / total {len(rows)}", flush=True)
    if not pending:
        print("Nothing to enrich.", flush=True)
        return 0
    client = GooglePlacesClient()
    lock = threading.Lock()
    succeeded = 0
    run = store.create_pipeline_run("google_places_bulk_enrichment")
    store.update_pipeline_run(run["run_id"], "RUNNING", summary={"total": len(rows), "pending": len(pending), "checkpoint": str(CHECKPOINT)})

    def one(row: dict) -> tuple[str, dict]:
        return row["venue_id"], client.details(row["google_place_id"])

    try:
        with ThreadPoolExecutor(max_workers=max(1, min(args.workers, 12))) as executor:
            futures = {executor.submit(one, row): row for row in pending}
            for index, future in enumerate(as_completed(futures), start=1):
                row = futures[future]
                try:
                    venue_id, details = future.result()
                    persist(store, venue_id, details)
                    with lock:
                        completed.add(venue_id)
                        failed.pop(venue_id, None)
                        succeeded += 1
                except Exception as exc:
                    with lock:
                        failed[row["venue_id"]] = str(exc)[:500]
                if index % 25 == 0 or index == len(pending):
                    write_checkpoint({"updated_at": now(), "completed": sorted(completed), "failed": failed})
                    print(f"Google enrichment progress: {index}/{len(pending)} success={succeeded} failed={len(failed)}", flush=True)
        summary = {"total": len(rows), "processed": len(pending), "succeeded": succeeded, "failed": len(failed), "checkpoint": str(CHECKPOINT)}
        store.update_pipeline_run(run["run_id"], "SUCCEEDED" if not failed else "FAILED", summary=summary, error_count=len(failed))
        print(json.dumps(summary), flush=True)
        return 0 if not failed else 2
    except Exception as exc:
        store.update_pipeline_run(run["run_id"], "FAILED", summary={"error": str(exc), "checkpoint": str(CHECKPOINT)}, error_count=1)
        raise


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from venue_pipeline.admission import admit
from venue_pipeline.scoring import fallback_metadata
from venue_pipeline.storage import normalize, save_sqlite, write_csv, write_json


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"


def main() -> None:
    payload = json.loads((DATA / "google_details_raw.json").read_text(encoding="utf-8"))
    rows = payload.get("places", [])
    for row in rows:
        metadata = fallback_metadata(row.get("google_details", {}))
        for key, value in metadata.items():
            if not row.get(key):
                row[key] = value
    admitted = admit(rows)
    venues = [normalize(row) for row in admitted]
    queue = [{"venue_id": row["venue_id"], "issue": row["admission_reason"], "priority": "high" if row["admission_decision"] == "Admitted" else "normal", "status": "open", "notes": "Verify address, closure status, operator class, fit-out age, current venue scene and all AI/local fallback metadata."} for row in venues]
    write_json(DATA / "google_details_raw.json", {"retrieved_on": date.today().isoformat(), "places": rows})
    write_json(DATA / "venues.json", {"retrieved_on": date.today().isoformat(), "venues": venues})
    write_json(DATA / "verification_queue.json", {"retrieved_on": date.today().isoformat(), "items": queue})
    write_csv(DATA / "venues.csv", venues)
    write_csv(DATA / "verification_queue.csv", queue)
    save_sqlite(DATA / "venue_database.sqlite3", venues, queue)
    print(f"Backfilled {len(venues)} venues; admitted={sum(row['admission_decision'] == 'Admitted' for row in venues)}; review={sum(row['admission_decision'] == 'Review' for row in venues)}")


if __name__ == "__main__":
    main()

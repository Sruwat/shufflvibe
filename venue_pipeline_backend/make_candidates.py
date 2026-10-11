from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a minimal place_id-only candidate CSV from transient discovery output")
    parser.add_argument("--src", type=Path, default=ROOT / "data" / "google_details_raw.json")
    parser.add_argument("--out", type=Path, default=ROOT / "data" / "candidates_south_delhi.csv")
    parser.add_argument("--city", default="Delhi")
    parser.add_argument("--areas", nargs="*", default=[])
    args = parser.parse_args()
    places = json.loads(args.src.read_text(encoding="utf-8")).get("places", [])
    rows = []
    allowed = set(args.areas)
    for row in places:
        if row.get("discovered_city") != args.city: continue
        if allowed and row.get("discovered_area") not in allowed: continue
        rows.append({"venue_id": f"venue:{row.get('google_place_id', '')}", "google_place_id": row.get("google_place_id", ""), "area": row.get("discovered_area", ""), "city": row.get("discovered_city", ""), "discovered_type": row.get("discovered_type", ""), "google_lookup_url": f"https://www.google.com/maps/search/?api=1&query=Google&query_place_id={row.get('google_place_id', '')}"})
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["venue_id", "google_place_id", "area", "city", "discovered_type", "google_lookup_url"]); writer.writeheader(); writer.writerows(rows)
    print(f"Wrote {len(rows)} place_id-only candidates to {args.out}")


if __name__ == "__main__":
    main()

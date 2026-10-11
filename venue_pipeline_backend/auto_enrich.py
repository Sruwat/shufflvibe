from __future__ import annotations

import argparse
import csv
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from venue_pipeline.auto_enrichment import extract_official_data

ROOT = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser(description="Auto-enrich verification queue from official public pages")
    parser.add_argument("--input", type=Path, default=ROOT / "data" / "google_details_raw.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data_market_ready")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()
    raw = json.loads(args.input.read_text(encoding="utf-8"))["places"]
    if args.limit: raw = raw[:args.limit]

    def one(row: dict) -> dict:
        details = row.get("google_details", {})
        website = details.get("websiteUri", "")
        result = extract_official_data(website)
        return {"venue_id": f"venue:{row.get('google_place_id', '')}", "google_place_id": row.get("google_place_id", ""), "discovered_area": row.get("discovered_area", ""), "discovered_city": row.get("discovered_city", ""), "discovered_type": row.get("discovered_type", ""), "google_lookup_url": f"https://www.google.com/maps/search/?api=1&query=Google&query_place_id={row.get('google_place_id', '')}", "human_status": "", "human_notes": "", "auto_status": result.get("status", "in_process"), "auto_confidence": result.get("confidence", "low"), **result}

    rows: list[dict] = []
    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = [executor.submit(one, row) for row in raw]
        for index, future in enumerate(as_completed(futures), start=1):
            rows.append(future.result())
            if index % 100 == 0 or index == len(futures): print(f"Official auto-enrichment: {index}/{len(futures)}", flush=True)
    rows.sort(key=lambda row: row["venue_id"])
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "auto_review_queue.json").write_text(json.dumps({"auto_review_queue": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    fields = sorted({field for row in rows for field in row})
    with (args.output_dir / "auto_review_queue.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore"); writer.writeheader(); writer.writerows(rows)
    print(f"Wrote {len(rows)} auto-enrichment rows to {args.output_dir}")


if __name__ == "__main__":
    main()

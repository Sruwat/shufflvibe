from __future__ import annotations

import argparse
import csv
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path

from venue_pipeline.admission import admit
from venue_pipeline.google_places import GooglePlacesClient
from venue_pipeline.market_ready import build_market_ready, save_market_ready
from venue_pipeline.scoring import score

ROOT = Path(__file__).resolve().parent


def load_local_env() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        if key.strip() and value:
            os.environ.setdefault(key.strip(), value)


def load_candidates(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [row for row in csv.DictReader(handle) if (row.get("google_place_id") or "").strip()]


def main() -> None:
    load_local_env()
    parser = argparse.ArgumentParser(description="Google Details -> SHUFFL scores -> admission -> human_pass")
    parser.add_argument("--src", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data_market_ready_v2")
    args = parser.parse_args()
    candidates = load_candidates(args.src)
    client = GooglePlacesClient()
    lock = threading.Lock()
    enriched: list[dict] = []
    failures: list[dict[str, str]] = []

    def one(candidate: dict[str, str]) -> dict:
        place_id = candidate["google_place_id"].strip()
        details = client.details(place_id)
        local = score(details)
        return {"google_place_id": place_id, "discovered_area": candidate.get("area", ""), "discovered_city": candidate.get("city", ""), "discovered_type": candidate.get("discovered_type", ""), "google_details": details, **local}

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(one, candidate): candidate for candidate in candidates}
        for index, future in enumerate(as_completed(futures), start=1):
            candidate = futures[future]
            try:
                enriched.append(future.result())
            except Exception as exc:
                failures.append({"google_place_id": candidate.get("google_place_id", ""), "error": str(exc)[:500]})
            if index % 25 == 0 or index == len(futures):
                print(f"Google Details enrichment: {index}/{len(futures)}", flush=True)

    admitted_rows = admit(enriched)
    admitted = [row for row in admitted_rows if row.get("admission_decision") == "Admitted"]
    rejected = [{"google_place_id": row.get("google_place_id", ""), "reason": row.get("admission_reason", "")} for row in admitted_rows if row.get("admission_decision") != "Admitted"]
    areas = []
    seen = set()
    for candidate in candidates:
        key = (candidate.get("area", ""), candidate.get("city", ""))
        if key not in seen:
            seen.add(key); areas.append({"area": key[0], "city": key[1]})
    payload = build_market_ready(admitted, areas, ROOT / "config" / "official_verification.csv")
    payload["human_pass"] = [{"venue_id": f"venue:{row.get('google_place_id', '')}", "google_place_id": row.get("google_place_id", ""), "google_lookup_url": f"https://www.google.com/maps/search/?api=1&query=Google&query_place_id={row.get('google_place_id', '')}", "fit_out_age": "", "operator_class": "", "instagram_schedule": "", "human_status": "", "human_notes": ""} for row in admitted]
    payload["admission_rejected"] = rejected
    payload["enrichment_failures"] = failures
    payload["run_summary"] = [{"retrieved_on": date.today().isoformat(), "input_candidates": len(candidates), "details_success": len(enriched), "admitted": len(admitted), "rejected_or_review": len(rejected), "failures": len(failures), "google_raw_persisted": False}]
    save_market_ready(payload, args.output_dir)
    print(f"Details succeeded: {len(enriched)}; admitted: {len(admitted)}; human pass: {len(payload['human_pass'])}; rejected/review: {len(rejected)}")
    print(f"Output: {args.output_dir}")


if __name__ == "__main__":
    main()

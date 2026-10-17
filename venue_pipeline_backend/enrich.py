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
from venue_pipeline.gemini import GeminiClient, GeminiError
from venue_pipeline.market_ready import build_market_ready, save_market_ready
from venue_pipeline.scoring import score
from venue_pipeline.official_sources import enrich_official_website
from venue_pipeline.shuffl_reviews import empty_review_summary, load_reviews

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
    parser = argparse.ArgumentParser(description="Google Details -> SHUFFL scores -> auto admission -> market-ready database")
    parser.add_argument("--src", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data_market_ready_v2")
    args = parser.parse_args()
    candidates = load_candidates(args.src)
    client = GooglePlacesClient()
    gemini = GeminiClient()
    shuffl_reviews = load_reviews(ROOT / "config" / "shuffl_reviews.csv")
    gemini_disabled = threading.Event()
    lock = threading.Lock()
    enriched: list[dict] = []
    failures: list[dict[str, str]] = []

    def one(candidate: dict[str, str]) -> dict:
        place_id = candidate["google_place_id"].strip()
        details = client.details(place_id)
        official = enrich_official_website((details.get("websiteUri") or "").strip())
        review_summary = shuffl_reviews.get(place_id, empty_review_summary())
        scoring_details = dict(details)
        scoring_details["editorialSummary"] = {"text": " ".join(str(official.get(key, "")) for key in ("official_description", "fit_out_evidence")) + " " + " ".join(row.get("review_text", "") for row in review_summary.get("shuffl_reviews", []))}
        local = score(scoring_details)
        merged = {**local}
        if not gemini_disabled.is_set():
            try:
                ai = gemini.analyze(details)
                merged.update(ai)
                merged["scores"] = {key: ai.get("scores", {}).get(key) if ai.get("scores", {}).get(key) is not None else local.get("scores", {}).get(key) for key in local.get("scores", {})}
                merged["score_evidence"] = {key: ai.get("score_evidence", {}).get(key) or local.get("score_evidence", {}).get(key, []) for key in local.get("scores", {})}
                merged["not_specialised"] = local.get("not_specialised", [])
            except GeminiError as exc:
                if " 429:" in str(exc) or " 503:" in str(exc):
                    gemini_disabled.set()
                merged.update({"description": "", "tags": [], "time_slots": [], "gemini_fallback": str(exc)[:200]})
        return {"google_place_id": place_id, "discovered_area": candidate.get("area", ""), "discovered_city": candidate.get("city", ""), "discovered_type": candidate.get("discovered_type", ""), "google_details": details, "official_data": official, "shuffl_review_summary": review_summary, **merged}

    with ThreadPoolExecutor(max_workers=12) as executor:
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
    # Build from every enriched row so the database contains candidates plus a
    # transparent machine admission log. There is no human-pass sheet/queue.
    payload = build_market_ready(admitted_rows, areas)
    payload["admission_rejected"] = rejected
    payload["enrichment_failures"] = failures
    payload["run_summary"] = [{"retrieved_on": date.today().isoformat(), "input_candidates": len(candidates), "details_success": len(enriched), "admitted": len(admitted), "rejected_or_review": len(rejected), "failures": len(failures), "google_raw_persisted": False}]
    save_market_ready(payload, args.output_dir)
    print(f"Details succeeded: {len(enriched)}; admitted automatically: {len(admitted)}; rejected automatically: {len(rejected)}")
    print(f"Output: {args.output_dir}")


if __name__ == "__main__":
    main()

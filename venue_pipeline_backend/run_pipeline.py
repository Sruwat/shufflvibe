from __future__ import annotations

import argparse
import json
import os
import re
import sys
import threading
from difflib import SequenceMatcher
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path
from math import hypot

from venue_pipeline.admission import admit
from venue_pipeline.areas import AreaError, geocode_missing, load_areas
from venue_pipeline.google_places import GooglePlacesClient, GooglePlacesError, discover
from venue_pipeline.gemini import GeminiClient, GeminiError
from venue_pipeline.overpass import OverpassError, discover_with_report as overpass_discover_report
from venue_pipeline.scoring import fallback_metadata, score
from venue_pipeline.market_ready import build_market_ready, save_market_ready
from venue_pipeline.storage import write_json
from venue_pipeline.official_sources import enrich_official_website
from venue_pipeline.shuffl_reviews import empty_review_summary, load_reviews

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"


def load_local_env() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key and value:
            os.environ.setdefault(key, value)


def write_areas(areas: list, out: Path) -> None:
    write_json(out / "areas_resolved.json", {"retrieved_on": date.today().isoformat(), "areas": [area.as_dict() for area in areas]})


def load_or_resolve_areas(path: Path, output_dir: Path):
    cached = output_dir / "areas_resolved.json"
    if cached.exists():
        from venue_pipeline.models import Area
        payload = json.loads(cached.read_text(encoding="utf-8"))
        cached_areas = [Area(**item) for item in payload.get("areas", [])]
        configured = load_areas(path)
        if len(cached_areas) == len(configured) and all(area.latitude is not None and area.longitude is not None for area in cached_areas):
            return cached_areas
    return geocode_missing(load_areas(path), os.getenv("NOMINATIM_USER_AGENT", "SHUFFL-Venue-Pipeline/1.0 contact@example.com"))


def _norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())


def _osm_match(item: dict, osm_rows: list[dict]) -> dict:
    discovery = item.get("discovery") or {}
    name = _norm(((discovery.get("displayName") or {}).get("text") or ""))
    location = discovery.get("location") or {}
    lat, lon = location.get("latitude"), location.get("longitude")
    address = _norm((discovery.get("formattedAddress") or ""))
    best: dict = {}
    best_rank = (-1.0, -1.0)
    for row in osm_rows:
        row_name = _norm(row.get("name", ""))
        if not name or not row_name:
            continue
        name_similarity = SequenceMatcher(None, name, row_name).ratio()
        distance = hypot(float(row.get("latitude", 0)) - float(lat or row.get("latitude", 0)), float(row.get("longitude", 0)) - float(lon or row.get("longitude", 0)))
        # OSM is secondary evidence only: require a close coordinate and a
        # strong name match, allowing punctuation/ampersand/brand suffixes.
        if distance > 0.012 or name_similarity < 0.84:
            continue
        address_bonus = 0.05 if address and _norm(row.get("address", "")) and any(token in _norm(row.get("address", "")) for token in (address[:12],)) else 0.0
        rank = (name_similarity + address_bonus, -distance)
        if rank > best_rank:
            best = {**row, "match_confidence": "high" if name_similarity >= 0.95 and distance < 0.003 else "medium", "match_name_similarity": round(name_similarity, 3), "match_coordinate_delta": round(distance, 6)}
            best_rank = rank
    return best


def area_stage(args: argparse.Namespace) -> int:
    try:
        areas = load_or_resolve_areas(args.areas, args.output_dir)
    except AreaError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_areas(areas, args.output_dir)
    print(f"Resolved {len(areas)} areas -> {args.output_dir / 'areas_resolved.json'}")
    if args.overpass:
        try:
            rows, failures = overpass_discover_report(areas)
        except OverpassError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        write_json(args.output_dir / "osm_candidates.json", {"retrieved_on": date.today().isoformat(), "venues": rows})
        write_json(args.output_dir / "pipeline_failures.json", {"retrieved_on": date.today().isoformat(), "failures": failures})
        print(f"Overpass found {len(rows)} OSM candidates")
    return 0


def run(args: argparse.Namespace) -> int:
    try:
        loaded_areas = load_areas(args.areas)
        areas = loaded_areas if args.dry_run else load_or_resolve_areas(args.areas, args.output_dir)
    except AreaError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_areas(areas, args.output_dir)
    if args.dry_run:
        print(f"Dry run complete: validated {len(areas)} areas")
        return 0
    osm_rows: list[dict] = []
    pipeline_failures: list[dict] = []
    if not args.skip_overpass:
        try:
            osm_rows, overpass_failures = overpass_discover_report(areas)
            pipeline_failures.extend(overpass_failures)
            write_json(args.output_dir / "osm_candidates.json", {"retrieved_on": date.today().isoformat(), "venues": osm_rows})
            print(f"Overpass candidates: {len(osm_rows)}")
        except OverpassError as exc:
            print(f"Warning: {exc}", file=sys.stderr)
            pipeline_failures.append({"stage": "overpass", "error": str(exc)[:500]})
    try:
        client = GooglePlacesClient()
        gemini = GeminiClient()
        shuffl_reviews = load_reviews(args.shuffl_reviews)
        gemini_disabled = threading.Event()
        discovery_failures: list[dict] = []
        identifiers = discover(client, areas, failures=discovery_failures)
        pipeline_failures.extend(discovery_failures)
        print(f"Google discovered unique places: {len(identifiers)}")
        def enrich(item: dict) -> dict:
            details = client.details(item["google_place_id"])
            osm = _osm_match(item, osm_rows)
            official_url = (details.get("websiteUri") or osm.get("website", "") or "").strip()
            official = enrich_official_website(official_url)
            review_summary = shuffl_reviews.get(item["google_place_id"], empty_review_summary())
            scoring_details = dict(details)
            official_text = " ".join(str(official.get(key, "")) for key in ("official_description", "official_evidence", "fit_out_evidence"))
            review_rows = [{"text": {"text": row.get("review_text", "")}} for row in review_summary.get("shuffl_reviews", [])]
            scoring_details["editorialSummary"] = {"text": f"{official_text} {' '.join(row['text']['text'] for row in review_rows)}"}
            local_scores = score(scoring_details)
            local_metadata = fallback_metadata(scoring_details)
            try:
                if gemini_disabled.is_set():
                    return {**item, "google_details": details, "osm_data": osm, "official_data": official, "shuffl_review_summary": review_summary, **local_scores, **local_metadata}
                ai_scores = gemini.analyze(details)
                merged = {**local_scores, **ai_scores}
                for key, value in local_metadata.items():
                    if not merged.get(key):
                        merged[key] = value
                merged["scores"] = {key: ai_scores["scores"].get(key) if ai_scores["scores"].get(key) is not None else local_scores["scores"].get(key) for key in local_scores["scores"]}
                merged["not_specialised"] = local_scores.get("not_specialised", [])
            except GeminiError as exc:
                if " 429:" in str(exc) or " 503:" in str(exc):
                    gemini_disabled.set()
                    print("Warning: Gemini quota/service limit reached; continuing all remaining venues with the local SHUFFL scorer.", file=sys.stderr, flush=True)
                else:
                    print(f"Warning: Gemini fallback for {item['google_place_id']}: {exc}", file=sys.stderr, flush=True)
                merged = {**local_scores, **local_metadata}
            return {**item, "google_details": details, "osm_data": osm, "official_data": official, "shuffl_review_summary": review_summary, **merged}

        enriched: list[dict] = []
        details_failures = 0
        detail_failure_rows: list[dict[str, str]] = []
        with ThreadPoolExecutor(max_workers=12) as executor:
            futures = {executor.submit(enrich, item): item for item in identifiers}
            for index, future in enumerate(as_completed(futures), start=1):
                item = futures[future]
                try:
                    enriched.append(future.result())
                except Exception as exc:
                    details_failures += 1
                    failure = {"stage": "google_details_or_enrichment", "google_place_id": item.get("google_place_id", ""), "error": str(exc)[:500]}
                    detail_failure_rows.append(failure)
                    pipeline_failures.append(failure)
                    if details_failures == 1 or details_failures % 100 == 0:
                        print(f"Warning: {details_failures} Google Details failures so far; latest: {exc}", file=sys.stderr, flush=True)
                if index % 25 == 0 or index == len(identifiers):
                    print(f"Google details/Gemini progress: {index}/{len(identifiers)}", flush=True)
        if details_failures:
            print(f"Google Details failures: {details_failures}; successful enrichments: {len(enriched)}", file=sys.stderr, flush=True)
    except GooglePlacesError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    admitted_rows = admit(enriched)
    areas_rows = [area.as_dict() for area in areas]
    payload = build_market_ready(admitted_rows, areas_rows)
    payload["run_summary"] = [{"retrieved_on": date.today().isoformat(), "input_candidates": len(identifiers), "details_success": len(enriched), "admitted": sum(row.get("admission_decision") == "Admitted" for row in admitted_rows), "rejected": sum(row.get("admission_decision") == "Rejected" for row in admitted_rows), "google_raw_persisted": False, "human_verification": False}]
    payload["enrichment_failures"] = detail_failure_rows
    payload["pipeline_failures"] = pipeline_failures
    save_market_ready(payload, args.output_dir)
    write_json(args.output_dir / "pipeline_failures.json", {"retrieved_on": date.today().isoformat(), "failures": pipeline_failures})
    print(f"Durable auto-admitted venues: {len(payload['venues'])}")
    print(f"SQLite database: {args.output_dir / 'venue_database_market_ready.sqlite3'}")
    return 0


def main() -> int:
    load_local_env()
    parser = argparse.ArgumentParser(description="SHUFFL Delhi-NCR venue pipeline")
    sub = parser.add_subparsers(dest="command", required=True)
    areas = sub.add_parser("areas")
    areas.add_argument("--areas", type=Path, default=ROOT / "config" / "areas.csv")
    areas.add_argument("--output-dir", type=Path, default=DATA)
    areas.add_argument("--overpass", action="store_true")
    areas.set_defaults(func=area_stage)
    full = sub.add_parser("run")
    full.add_argument("--areas", type=Path, default=ROOT / "config" / "areas.csv")
    full.add_argument("--output-dir", type=Path, default=DATA)
    full.add_argument("--skip-overpass", action="store_true")
    full.add_argument("--shuffl-reviews", type=Path, default=ROOT / "config" / "shuffl_reviews.csv", help="Optional SHUFFL-owned review CSV")
    full.add_argument("--dry-run", action="store_true")
    full.set_defaults(func=run)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

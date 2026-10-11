from __future__ import annotations

import argparse
import json
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path

from venue_pipeline.admission import admit
from venue_pipeline.areas import AreaError, geocode_missing, load_areas
from venue_pipeline.google_places import GooglePlacesClient, GooglePlacesError, discover
from venue_pipeline.gemini import GeminiClient, GeminiError
from venue_pipeline.overpass import OverpassError, discover as overpass_discover
from venue_pipeline.scoring import fallback_metadata, score
from venue_pipeline.storage import normalize, save_sqlite, write_csv, write_json

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
        return [Area(**item) for item in payload.get("areas", [])]
    return geocode_missing(load_areas(path), os.getenv("NOMINATIM_USER_AGENT", "SHUFFL-Venue-Pipeline/1.0 contact@example.com"))


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
            rows = overpass_discover(areas)
        except OverpassError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        write_json(args.output_dir / "osm_candidates.json", {"retrieved_on": date.today().isoformat(), "venues": rows})
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
    if not args.skip_overpass:
        try:
            osm_rows = overpass_discover(areas)
            write_json(args.output_dir / "osm_candidates.json", {"retrieved_on": date.today().isoformat(), "venues": osm_rows})
            print(f"Overpass candidates: {len(osm_rows)}")
        except OverpassError as exc:
            print(f"Warning: {exc}", file=sys.stderr)
    try:
        client = GooglePlacesClient()
        gemini = GeminiClient()
        gemini_disabled = threading.Event()
        identifiers = discover(client, areas)
        print(f"Google discovered unique places: {len(identifiers)}")
        def enrich(item: dict) -> dict:
            details = client.details(item["google_place_id"])
            local_scores = score(details)
            local_metadata = fallback_metadata(details)
            try:
                if gemini_disabled.is_set():
                    return {**item, "google_details": details, **local_scores, **local_metadata}
                ai_scores = gemini.analyze(details)
                merged = {**local_scores, **ai_scores}
                for key, value in local_metadata.items():
                    if not merged.get(key):
                        merged[key] = value
                merged["scores"] = {key: ai_scores["scores"].get(key) if ai_scores["scores"].get(key) is not None else local_scores["scores"].get(key) for key in local_scores["scores"]}
            except GeminiError as exc:
                if " 429:" in str(exc) or " 503:" in str(exc):
                    gemini_disabled.set()
                    print("Warning: Gemini quota/service limit reached; continuing all remaining venues with the local SHUFFL scorer.", file=sys.stderr, flush=True)
                else:
                    print(f"Warning: Gemini fallback for {item['google_place_id']}: {exc}", file=sys.stderr, flush=True)
                merged = {**local_scores, **local_metadata}
            return {**item, "google_details": details, **merged}

        enriched: list[dict] = []
        details_failures = 0
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(enrich, item): item for item in identifiers}
            for index, future in enumerate(as_completed(futures), start=1):
                item = futures[future]
                try:
                    enriched.append(future.result())
                except Exception as exc:
                    details_failures += 1
                    if details_failures == 1 or details_failures % 100 == 0:
                        print(f"Warning: {details_failures} Google Details failures so far; latest: {exc}", file=sys.stderr, flush=True)
                if index % 25 == 0 or index == len(identifiers):
                    print(f"Google details/Gemini progress: {index}/{len(identifiers)}", flush=True)
        if details_failures:
            print(f"Google Details failures: {details_failures}; successful enrichments: {len(enriched)}", file=sys.stderr, flush=True)
    except GooglePlacesError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    write_json(args.output_dir / "google_details_raw.json", {"retrieved_on": date.today().isoformat(), "places": enriched})
    admitted = admit(enriched)
    venues = [normalize(row) for row in admitted]
    queue = [{"venue_id": row["venue_id"], "issue": row["admission_reason"], "priority": "high" if row["admission_decision"] == "Admitted" else "normal", "status": "open", "notes": "Verify address, closure status, operator class, fit-out age and current venue scene."} for row in venues]
    write_json(args.output_dir / "venues.json", {"retrieved_on": date.today().isoformat(), "venues": venues})
    write_json(args.output_dir / "verification_queue.json", {"retrieved_on": date.today().isoformat(), "items": queue})
    write_csv(args.output_dir / "venues.csv", venues)
    write_csv(args.output_dir / "verification_queue.csv", queue)
    save_sqlite(args.output_dir / "venue_database.sqlite3", venues, queue)
    print(f"Durable venues: {len(venues)}")
    print(f"SQLite database: {args.output_dir / 'venue_database.sqlite3'}")
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
    full.add_argument("--dry-run", action="store_true")
    full.set_defaults(func=run)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

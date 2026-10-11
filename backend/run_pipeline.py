from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import date
from pathlib import Path

from venue_db.config import SOUTH_DELHI_AREAS, SEARCH_CATEGORIES
from venue_db.places_api import PlacesApiError, PlacesClient, iter_queries
from venue_db.foursquare_api import FoursquareApiError, FoursquareClient, discover as fsq_discover
from venue_db.osm_api import OsmApiError, discover as osm_discover
from venue_db.site_verify import verify as verify_site
from venue_db.validation import read_csv, validate_rows, write_report


ROOT = Path(__file__).resolve().parent


def cmd_discover(args: argparse.Namespace) -> int:
    try:
        client = PlacesClient()
    except PlacesApiError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    identifiers: dict[str, dict[str, str]] = {}
    for query in iter_queries(SOUTH_DELHI_AREAS, SEARCH_CATEGORIES):
        print(f"Searching: {query}")
        for place in client.text_search(query):
            identifier = client.durable_identifier(place)
            if identifier["google_place_id"]:
                identifiers[identifier["google_place_id"]] = identifier
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir / "place_ids.json"
    output.write_text(json.dumps({"retrieved_on": date.today().isoformat(), "places": list(identifiers.values())}, indent=2), encoding="utf-8")
    print(f"Wrote {len(identifiers)} durable place identifiers to {output}")
    return 0


def cmd_enrich(args: argparse.Namespace) -> int:
    source = json.loads(args.input.read_text(encoding="utf-8"))
    try:
        client = PlacesClient()
    except PlacesApiError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    # This output is intentionally transient and gitignored. It is for a human/licensed-source review only.
    rows: list[dict[str, str]] = []
    for item in source.get("places", []):
        details = client.details(item["google_place_id"])
        rows.append({
            "google_place_id": item["google_place_id"],
            "google_maps_url": item.get("google_maps_url", ""),
            "live_verification_retrieved_on": date.today().isoformat(),
            "display_name_live": details.get("displayName", {}).get("text", ""),
            "formatted_address_live": details.get("formattedAddress", ""),
            "business_status_live": details.get("businessStatus", ""),
            "website_live": details.get("websiteUri", ""),
            "opening_hours_live": json.dumps(details.get("regularOpeningHours", {}), ensure_ascii=False),
        })
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with (args.output_dir / "google_live_review.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["google_place_id"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} transient live verification rows. Do not import Google-owned fields into the durable workbook without a permitted/licensed basis.")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    # The workbook is converted to CSV by the companion export step, because the backend itself is standard-library-only.
    csv_dir = args.workbook.parent / "csv_export"
    expected = {"Venues": "Venues.csv", "Venue_Time_Slots": "Venue_Time_Slots.csv", "Venue_Sources": "Venue_Sources.csv"}
    missing = [name for name in expected.values() if not (csv_dir / name).exists()]
    if missing:
        print("CSV exports are missing. Run build-report after exporting the workbook with the spreadsheet tool.", file=sys.stderr)
        for name in missing:
            print(f"- {csv_dir / name}", file=sys.stderr)
        return 2
    report = validate_rows(read_csv(csv_dir / expected["Venues"]), read_csv(csv_dir / expected["Venue_Time_Slots"]), read_csv(csv_dir / expected["Venue_Sources"]))
    write_report(report, args.output_dir / "validation_report.txt")
    print(json.dumps(report, indent=2))
    return 1 if report["errors"] else 0


def cmd_build_report(args: argparse.Namespace) -> int:
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "workbook_source.txt").write_text(str(args.workbook), encoding="utf-8")
    print("Workbook report scaffold created. Export the workbook tabs to backend/data/csv_export before running validate.")
    return 0


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def cmd_osm_discover(args: argparse.Namespace) -> int:
    try:
        rows = osm_discover()
    except OsmApiError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    output = args.output_dir / "osm_candidates.json"
    _write_json(output, {"retrieved_on": date.today().isoformat(), "source": "OpenStreetMap Overpass", "venues": rows})
    print(f"Wrote {len(rows)} OSM venue candidates to {output}")
    return 0


def cmd_foursquare_discover(args: argparse.Namespace) -> int:
    try:
        client = FoursquareClient()
        rows = fsq_discover(client)
    except FoursquareApiError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    output = args.output_dir / "foursquare_candidates.json"
    _write_json(output, {"retrieved_on": date.today().isoformat(), "source": "Foursquare Places API", "venues": rows})
    print(f"Wrote {len(rows)} Foursquare venue candidates to {output}")
    return 0


def cmd_site_verify(args: argparse.Namespace) -> int:
    source = json.loads(args.input.read_text(encoding="utf-8"))
    rows = source.get("venues", source if isinstance(source, list) else [])
    rows = [row for row in rows if row.get("official_website") or row.get("website")]
    output_rows = []
    for index, row in enumerate(rows, start=1):
        url = row.get("official_website") or row.get("website") or ""
        # Avoid wasting requests on the many OSM records that do not publish a website.
        result = verify_site(url) if url else {"website_status": "missing"}
        output_rows.append({**row, **result})
        if index % 100 == 0 or index == len(rows):
            print(f"Verified {index}/{len(rows)} public venue websites")
    output = args.output_dir / "website_verification.json"
    _write_json(output, {"retrieved_on": date.today().isoformat(), "source": "public official venue pages", "website_candidate_count": len(rows), "venues": output_rows})
    print(f"Wrote {len(output_rows)} website verification rows to {output}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="SHUFFL South Delhi venue database pipeline")
    sub = parser.add_subparsers(dest="command", required=True)
    discover = sub.add_parser("discover")
    discover.add_argument("--output-dir", type=Path, default=ROOT / "staging")
    discover.set_defaults(func=cmd_discover)
    enrich = sub.add_parser("enrich")
    enrich.add_argument("--input", type=Path, required=True)
    enrich.add_argument("--output-dir", type=Path, default=ROOT / "staging")
    enrich.set_defaults(func=cmd_enrich)
    validate = sub.add_parser("validate")
    validate.add_argument("--workbook", type=Path, required=True)
    validate.add_argument("--output-dir", type=Path, default=ROOT / "staging")
    validate.set_defaults(func=cmd_validate)
    report = sub.add_parser("build-report")
    report.add_argument("--workbook", type=Path, required=True)
    report.add_argument("--output-dir", type=Path, default=ROOT / "staging")
    report.set_defaults(func=cmd_build_report)
    osm = sub.add_parser("osm-discover")
    osm.add_argument("--output-dir", type=Path, default=ROOT / "staging")
    osm.set_defaults(func=cmd_osm_discover)
    fsq = sub.add_parser("foursquare-discover")
    fsq.add_argument("--output-dir", type=Path, default=ROOT / "staging")
    fsq.set_defaults(func=cmd_foursquare_discover)
    site = sub.add_parser("site-verify")
    site.add_argument("--input", type=Path, required=True)
    site.add_argument("--output-dir", type=Path, default=ROOT / "staging")
    site.set_defaults(func=cmd_site_verify)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

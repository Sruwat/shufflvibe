from __future__ import annotations

import argparse
import csv
from pathlib import Path


ALLOWED = {"verified", "rejected", "in_process", "update_required"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the four human review statuses")
    parser.add_argument("file", type=Path, default=Path("venue_pipeline_backend/data_market_ready/auto_review_queue.csv"), nargs="?")
    args = parser.parse_args()
    with args.file.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    invalid = [row.get("venue_id", "") for row in rows if (row.get("human_status") or row.get("auto_status") or "in_process") not in ALLOWED]
    if invalid:
        raise SystemExit(f"Invalid status in {len(invalid)} rows. Allowed: {sorted(ALLOWED)}")
    counts = {status: sum((row.get("human_status") or row.get("auto_status") or "in_process") == status for row in rows) for status in ALLOWED}
    print(counts)
    print("Only rows with human_status=verified may be promoted to the active venue database.")


if __name__ == "__main__":
    main()

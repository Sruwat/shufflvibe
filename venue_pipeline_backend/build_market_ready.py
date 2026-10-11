from __future__ import annotations

import json
from pathlib import Path

from venue_pipeline.market_ready import build_market_ready, save_market_ready

ROOT = Path(__file__).resolve().parent
LEGACY = ROOT / "data"
OUT = ROOT / "data_market_ready"
VERIFICATION = ROOT / "config" / "official_verification.csv"


def main() -> None:
    raw = json.loads((LEGACY / "google_details_raw.json").read_text(encoding="utf-8"))
    areas = json.loads((LEGACY / "areas_resolved.json").read_text(encoding="utf-8")).get("areas", [])
    payload = build_market_ready(raw.get("places", []), areas, VERIFICATION)
    save_market_ready(payload, OUT)
    print(f"Market-ready candidates: {len(payload['candidates'])}")
    print(f"Officially verified active venues: {len(payload['venues'])}")
    print(f"Human-pass queue: {len(payload['human_pass'])}")
    print(f"Output: {OUT}")


if __name__ == "__main__":
    main()

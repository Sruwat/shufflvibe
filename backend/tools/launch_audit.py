"""Run the read-only SHUFFL pre-launch audit against the configured database."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(ROOT))

from app.admin_store import store  # noqa: E402
from app.launch_audit import build_launch_audit  # noqa: E402


if __name__ == "__main__":
    report = build_launch_audit(store.engine)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["ready_for_launch"] else 2)

"""Final MVP smoke test for a running SHUFFL API.

This checks local API contracts only. It intentionally does not call live
Google stop-options enrichment, so it is safe to run in CI or before launch.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
# ``photos`` may contain SHUFFL-owned/licensed media. Google live photo
# payloads are still excluded from the durable catalogue by the server and
# are checked by the Phase 7 audit.
PUBLIC_PROHIBITED_KEYS = {"reviews", "reviewText", "userRatingCount", "openingHours", "regularOpeningHours", "latitude", "longitude", "formattedAddress"}


def local_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if value:
        return value
    env_file = ROOT / "backend" / ".env"
    if not env_file.exists():
        return ""
    for line in env_file.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith(f"{name}="):
            return line.split("=", 1)[1].strip().strip("\"'")
    return ""


def fetch(base: str, path: str, token: str = "", timeout: int = 15) -> tuple[int, bytes, str]:
    headers = {"Accept": "application/json"}
    if token:
        headers["X-Admin-Token"] = token
    request = Request(base.rstrip("/") + path, headers=headers)
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read()
            return response.status, body, response.headers.get("content-type", "")
    except HTTPError as exc:
        return exc.code, exc.read(), exc.headers.get("content-type", "")
    except (URLError, TimeoutError, OSError) as exc:
        return 0, str(exc).encode(), ""


def json_body(body: bytes) -> dict:
    try:
        value = json.loads(body)
        return value if isinstance(value, dict) else {}
    except (TypeError, ValueError):
        return {}


def public_catalogue_is_safe(body: bytes) -> bool:
    payload = json_body(body)
    items = payload.get("items")
    if not isinstance(items, list):
        return False
    for item in items:
        if not isinstance(item, dict):
            return False
        if PUBLIC_PROHIBITED_KEYS.intersection(item):
            return False
        if item.get("publication_status") not in (None, "PUBLISHED"):
            return False
        if item.get("eligibility_status") not in (None, "AUTO_APPROVED", "PROVISIONAL"):
            return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Run SHUFFL MVP API smoke tests")
    parser.add_argument("--base-url", default=local_env("SHUFFL_API_BASE_URL") or "http://127.0.0.1:8000")
    parser.add_argument("--admin-token", default=local_env("ADMIN_API_TOKEN"))
    args = parser.parse_args()
    checks = [
        ("health", "/health", False),
        ("readiness", "/v1/health/readiness", False),
        ("release scope", "/v1/release", False),
        ("public discovery", "/v1/discovery", False),
        ("public venue list", "/v1/venues?city=", False),
        ("hosted rooms", "/v1/rooms?status=hosted", False),
        ("conversations", "/v1/conversations", False),
        ("notifications", "/v1/notifications", False),
        ("admin summary", "/v1/admin/summary", True),
        ("launch audit", "/v1/admin/ops/launch-audit", True),
        ("Excel export", "/v1/admin/export.xlsx", True),
    ]
    results = []
    failed = False
    for name, path, admin in checks:
        timeout = 120 if name == "Excel export" else 15
        status, body, content_type = fetch(args.base_url, path, args.admin_token if admin else "", timeout)
        ok = status == 200 and (name != "Excel export" or body[:2] == b"PK")
        if name == "readiness" and status == 200:
            try:
                ok = json.loads(body).get("status") == "ready"
            except (TypeError, ValueError):
                ok = False
        if name == "release scope" and status == 200:
            release = json_body(body)
            ok = release.get("release") == "mvp" and release.get("venue_catalogue", {}).get("locked") is True
        if name in {"public discovery", "public venue list"} and status == 200:
            ok = public_catalogue_is_safe(body)
        if name == "launch audit" and status == 200:
            ok = json_body(body).get("ready_for_launch") is True
        results.append({"check": name, "ok": ok, "status": status, "content_type": content_type})
        failed = failed or not ok
    print(json.dumps({"base_url": args.base_url, "ready": not failed, "checks": results}, indent=2))
    return 0 if not failed else 2


if __name__ == "__main__":
    raise SystemExit(main())

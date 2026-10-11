from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from .config import FOURSQUARE_QUERIES, SOUTH_DELHI_BBOX

BASE_URL = "https://places-api.foursquare.com"
API_VERSION = "2025-06-17"


def _load_local_env() -> None:
    """Load the local, gitignored backend/.env without adding a dependency."""
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name.strip() and name.strip() not in os.environ:
            os.environ[name.strip()] = value.strip().strip('"').strip("'")


class FoursquareApiError(RuntimeError):
    pass


class FoursquareClient:
    def __init__(self, api_key: str | None = None, timeout: int = 45) -> None:
        _load_local_env()
        self.api_key = api_key or os.getenv("FOURSQUARE_API_KEY")
        self.timeout = timeout
        if not self.api_key:
            raise FoursquareApiError("FOURSQUARE_API_KEY is not set")

    def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        query = urllib.parse.urlencode({k: v for k, v in params.items() if v not in (None, "")})
        request = urllib.request.Request(
            f"{BASE_URL}{path}?{query}",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "X-Places-Api-Version": API_VERSION,
                "Accept": "application/json",
                "User-Agent": "SHUFFL-Venue-Database/1.0",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise FoursquareApiError(f"Foursquare {exc.code}: {body[:500]}") from exc
        except urllib.error.URLError as exc:
            raise FoursquareApiError(f"Foursquare network error: {exc.reason}") from exc

    def search(self, query: str, near: str = "South Delhi, India", limit: int = 50) -> list[dict[str, Any]]:
        response = self._get("/places/search", {"query": query, "near": near, "limit": min(limit, 50)})
        return response.get("results") or response.get("places") or []

    def details(self, fsq_place_id: str, fields: str | None = None) -> dict[str, Any]:
        params = {"fields": fields} if fields else {}
        return self._get(f"/places/{urllib.parse.quote(fsq_place_id, safe='')}", params)


def discover(client: FoursquareClient, queries: tuple[str, ...] = FOURSQUARE_QUERIES) -> list[dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for query in queries:
        for row in client.search(query):
            place_id = row.get("fsq_place_id") or row.get("fsq_id") or row.get("id")
            if place_id:
                rows[place_id] = row
        time.sleep(0.25)
    return list(rows.values())

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from html.parser import HTMLParser
from typing import Any


class _PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self._in_title = False
        self.links: list[str] = []
        self.text_parts: list[str] = []
        self.jsonld: list[dict[str, Any]] = []
        self._in_jsonld = False
        self._jsonld_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "title": self._in_title = True
        if tag == "a" and values.get("href"): self.links.append(values["href"] or "")
        if tag == "script" and values.get("type", "").lower() == "application/ld+json":
            self._in_jsonld = True; self._jsonld_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "title": self._in_title = False
        if tag == "script" and self._in_jsonld:
            self._in_jsonld = False
            try:
                value = json.loads("".join(self._jsonld_parts))
                self.jsonld.extend(value if isinstance(value, list) else [value])
            except json.JSONDecodeError:
                pass

    def handle_data(self, data: str) -> None:
        if self._in_title: self.title += data
        if self._in_jsonld: self._jsonld_parts.append(data)
        self.text_parts.append(data)


def _fetch(url: str, timeout: int = 8) -> tuple[str, str]:
    request = urllib.request.Request(url, headers={"User-Agent": "SHUFFL-Venue-Verification/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.geturl(), response.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError, ValueError):
        return url, ""


def extract_official_data(url: str) -> dict[str, Any]:
    if not url:
        return {"source_url": "", "status": "in_process", "confidence": "none"}
    final_url, html = _fetch(url)
    if not html:
        return {"source_url": final_url, "status": "update_required", "confidence": "low"}
    parser = _PageParser(); parser.feed(html)
    text = " ".join(" ".join(parser.text_parts).split())
    structured: dict[str, Any] = {}
    for item in parser.jsonld:
        item_type = item.get("@type") if isinstance(item, dict) else ""
        item_types = item_type if isinstance(item_type, list) else [item_type]
        if isinstance(item, dict) and any(value in {"Restaurant", "CafeOrCoffeeShop", "BarOrPub", "FoodEstablishment", "LocalBusiness"} for value in item_types):
            structured = item; break
    same_as = structured.get("sameAs", []) if isinstance(structured, dict) else []
    if isinstance(same_as, str): same_as = [same_as]
    social_links = [link for link in parser.links + list(same_as) if any(host in link.lower() for host in ("instagram.com", "facebook.com"))]
    hours = structured.get("openingHoursSpecification", []) if isinstance(structured, dict) else []
    address = structured.get("address", {}) if isinstance(structured, dict) else {}
    slots: list[dict[str, Any]] = []
    for pattern, slot_name in ((r"(?:every\s+)?fridays?[^.]{0,80}(?:live\s+music|dj)", "Friday programming"), (r"sundays?[^.]{0,80}brunch", "Sunday brunch"), (r"(?:kitchen|food)\s+(?:open|available)[^.]{0,40}(?:until|till)\s+\d", "late kitchen")):
        match = re.search(pattern, text, re.I)
        if match:
            slots.append({"slot_name": slot_name, "evidence_text": match.group(0), "source_url": final_url, "confidence": "medium"})
    return {
        "source_url": final_url,
        "official_name": (structured.get("name", "") if isinstance(structured, dict) else "") or parser.title.strip(),
        "official_address": address.get("streetAddress", "") if isinstance(address, dict) else "",
        "official_website": final_url,
        "social_links": sorted(set(social_links)),
        "hours_json": json.dumps(hours, ensure_ascii=False) if hours else "",
        "time_slots": slots,
        "status": "in_process",
        "confidence": "medium" if structured else "low",
    }

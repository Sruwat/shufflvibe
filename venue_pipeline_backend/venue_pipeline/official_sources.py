from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from datetime import date
from html import unescape
from typing import Any
from urllib.parse import urljoin, urlparse


USER_AGENT = "SHUFFL-Venue-Pipeline/1.0 (+official-source-enrichment)"
SOCIAL_HOSTS = {"instagram.com", "www.instagram.com", "facebook.com", "www.facebook.com"}


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", unescape(str(value or ""))).strip()


def _text_from_html(html: str) -> str:
    html = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.I | re.S)
    html = re.sub(r"<style[^>]*>.*?</style>", " ", html, flags=re.I | re.S)
    return _clean(re.sub(r"<[^>]+>", " ", html))


def _json_ld(html: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for match in re.findall(r"<script[^>]+type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>", html, flags=re.I | re.S):
        try:
            value = json.loads(unescape(match.strip()))
        except (TypeError, ValueError):
            continue
        values = value if isinstance(value, list) else [value]
        for item in values:
            if isinstance(item, dict):
                rows.append(item)
                for nested in item.get("@graph", []) or []:
                    if isinstance(nested, dict):
                        rows.append(nested)
    return rows


def _find_url(html: str, base_url: str, words: tuple[str, ...]) -> str:
    for href, label in re.findall(r"<a[^>]+href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", html, flags=re.I | re.S):
        value = f"{href} {_text_from_html(label)}".lower()
        if any(word in value for word in words):
            return urljoin(base_url, href)
    return ""


def _social_urls(html: str, base_url: str) -> list[str]:
    urls: list[str] = []
    for href in re.findall(r"(?:href|content)=[\"']([^\"']+)[\"']", html, flags=re.I):
        absolute = urljoin(base_url, href)
        host = (urlparse(absolute).hostname or "").lower()
        if host in SOCIAL_HOSTS and absolute not in urls:
            urls.append(absolute)
    return urls


def _fetch_html(url: str, timeout: int) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read(2_000_000).decode("utf-8", errors="replace")


def _linked_pages(html: str, base_url: str, limit: int = 6) -> list[str]:
    """Find same-site pages that are likely to contain durable evidence."""
    root = urlparse(base_url)
    keywords = ("menu", "food", "book", "reserve", "event", "what", "about", "contact", "music", "schedule", "hours")
    candidates: list[tuple[int, str]] = []
    seen = {base_url.rstrip("/")}
    for href, label in re.findall(r"<a[^>]+href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", html, flags=re.I | re.S):
        absolute = urljoin(base_url, href).split("#", 1)[0].rstrip("/")
        parsed = urlparse(absolute)
        if parsed.scheme not in {"http", "https"} or parsed.hostname != root.hostname or absolute in seen:
            continue
        clue = f"{absolute} {_text_from_html(label)}".lower()
        score = sum(1 for word in keywords if word in clue)
        if score:
            candidates.append((score, absolute))
            seen.add(absolute)
    return [url for _, url in sorted(candidates, key=lambda item: (-item[0], item[1]))[:limit]]


def _hours(text: str) -> tuple[str, str]:
    patterns = [
        r"((?:mon|tue|wed|thu|fri|sat|sun)[a-z\-–, ]{0,30}(?:\d{1,2}(?::\d{2})?\s*(?:am|pm)?\s*[-–]\s*\d{1,2}(?::\d{2})?\s*(?:am|pm)?))",
        r"((?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)[^.;]{0,80}\d{1,2}(?::\d{2})?\s*(?:am|pm)?\s*[-–]\s*\d{1,2}(?::\d{2})?\s*(?:am|pm)?)",
    ]
    for pattern in patterns:
        found = re.findall(pattern, text, flags=re.I)
        if found:
            return _clean(found[0]), "high"
    if re.search(r"opening hours|open daily|hours", text, flags=re.I):
        return "", "low"
    return "", "unknown"


def _fitout(text: str) -> dict[str, Any]:
    exact_patterns = [
        r"(?:opened|established|launched|renovated|redesigned|refurbished)\s+(?:in\s+)?(20\d{2})",
        r"(?:since|from)\s+(20\d{2})",
    ]
    for pattern in exact_patterns:
        match = re.search(pattern, text, flags=re.I)
        if match:
            year = int(match.group(1))
            return {"fit_out_year": year, "fit_out_status": "estimated", "fit_out_confidence": "medium", "fit_out_evidence": _clean(match.group(0))}
    if re.search(r"heritage|historic|old building|colonial|mansion|haveli|redesigned|renovated", text, flags=re.I):
        return {"fit_out_year": None, "fit_out_status": "estimated", "fit_out_confidence": "low", "fit_out_evidence": "Official page contains fit-out/heritage language; year not established."}
    return {"fit_out_year": None, "fit_out_status": "unknown", "fit_out_confidence": "none", "fit_out_evidence": ""}


def _slots(text: str, source_url: str) -> list[dict[str, Any]]:
    patterns = [
        ("live-music", r"(?:every\s+)?(?:mon|tue|wed|thu|fri|sat|sun)[^.;]{0,45}(?:live music|live band|acoustic|gig)"),
        ("dj-after-11", r"(?:dj|deejay)[^.;]{0,45}(?:after|from|at)\s*(?:11|10|9)\s*(?:pm)?"),
        ("quiz-night", r"(?:every\s+)?(?:wed|thu|wednesday|thursday)[^.;]{0,45}quiz"),
        ("screening", r"(?:match screening|live screening|screening|watch the match)"),
        ("sufi-night", r"sufi[^.;]{0,30}(?:night|evening)"),
        ("open-mic", r"open[\- ]mic"),
        ("brunch", r"(?:sunday|weekend)[^.;]{0,45}brunch"),
    ]
    rows: list[dict[str, Any]] = []
    for kind, pattern in patterns:
        match = re.search(pattern, text, flags=re.I)
        if match:
            rows.append({"days": "", "from_time": "", "to_time": "", "type": kind, "slot_status": "filled", "evidence": _clean(match.group(0)), "source_type": "official_website", "source_url": source_url, "confidence": "medium"})
    return rows


def enrich_official_website(url: str, timeout: int = 5, max_pages: int = 6) -> dict[str, Any]:
    if not url or not url.startswith(("http://", "https://")):
        return {"official_status": "missing", "official_url": url or "", "official_evidence": []}
    try:
        html = _fetch_html(url, timeout)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as exc:
        return {"official_status": "unavailable", "official_url": url, "official_error": str(exc)[:300], "official_evidence": []}

    pages: list[tuple[str, str]] = [(url, html)]
    for linked_url in _linked_pages(html, url, max(0, max_pages - 1)):
        try:
            pages.append((linked_url, _fetch_html(linked_url, timeout)))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError):
            continue
    combined_text = " ".join(_text_from_html(page_html) for _, page_html in pages)
    entities = [entity for _, page_html in pages for entity in _json_ld(page_html)]
    def is_business(item: dict[str, Any]) -> bool:
        types = item.get("@type", [])
        types = types if isinstance(types, list) else [types]
        return bool(set(str(value) for value in types) & {"Restaurant", "BarOrPub", "CafeOrCoffeeShop", "LocalBusiness", "NightClub"})

    entity = next((item for item in entities if is_business(item)), entities[0] if entities else {})
    name = _clean(entity.get("name"))
    address = entity.get("address")
    if isinstance(address, dict):
        address = _clean(" ".join(str(address.get(key, "")) for key in ("streetAddress", "addressLocality", "addressRegion", "postalCode")))
    address = _clean(address)
    hours, hours_confidence = _hours(combined_text)
    menu_url = next((_find_url(page_html, page_url, ("menu", "food menu")) for page_url, page_html in pages if _find_url(page_html, page_url, ("menu", "food menu"))), "")
    booking_url = next((_find_url(page_html, page_url, ("book", "reserve", "reservation")) for page_url, page_html in pages if _find_url(page_html, page_url, ("book", "reserve", "reservation"))), "")
    event_url = next((_find_url(page_html, page_url, ("event", "what's on", "whats on", "programme", "program")) for page_url, page_html in pages if _find_url(page_html, page_url, ("event", "what's on", "whats on", "programme", "program"))), "")
    fitout = _fitout(combined_text)
    evidence = [{"field_name": "official_page" if index == 0 else "linked_official_page", "source_type": "official_website", "source_url": page_url, "evidence_text": _text_from_html(page_html)[:1000], "confidence": "medium"} for index, (page_url, page_html) in enumerate(pages)]
    socials: list[str] = []
    for page_url, page_html in pages:
        for social in _social_urls(page_html, page_url):
            if social not in socials:
                socials.append(social)
    return {"official_status": "fetched", "official_url": url, "official_name": name, "official_address": address, "official_phone": _clean(entity.get("telephone")), "menu_url": menu_url, "booking_url": booking_url, "event_url": event_url, "official_hours": hours, "hours_confidence": hours_confidence, "official_social_urls": socials, "official_description": _clean(entity.get("description")) or combined_text[:500], "official_food": bool(re.search(r"restaurant|dining|menu|kitchen|food", combined_text, re.I)), "official_alcohol": bool(re.search(r"bar|cocktail|wine|beer|spirits", combined_text, re.I)), "time_slots": _slots(combined_text, url), **fitout, "official_evidence": evidence, "official_checked_on": date.today().isoformat(), "official_pages_checked": [page_url for page_url, _ in pages]}

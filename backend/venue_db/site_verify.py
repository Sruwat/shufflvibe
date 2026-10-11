from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from typing import Any

USER_AGENT = "SHUFFL-Venue-Database/1.0"


class _Parser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title: list[str] = []
        self.text: list[str] = []
        self.json_ld: list[str] = []
        self._in_title = False
        self._in_json_ld = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "title": self._in_title = True
        if tag.lower() == "script" and dict(attrs).get("type") == "application/ld+json": self._in_json_ld = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title": self._in_title = False
        if tag.lower() == "script": self._in_json_ld = False

    def handle_data(self, data: str) -> None:
        if self._in_title: self.title.append(data)
        if self._in_json_ld: self.json_ld.append(data)
        if not self._in_json_ld: self.text.append(data)


def verify(url: str, timeout: int = 20) -> dict[str, Any]:
    if not url or not url.startswith(("http://", "https://")):
        return {"website_status": "missing"}
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read(2_000_000).decode("utf-8", errors="replace")
            final_url = response.geturl()
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        return {"website_status": "unreachable", "website_error": str(exc)[:250]}
    parser = _Parser()
    parser.feed(body)
    structured: list[dict[str, Any]] = []
    for raw in parser.json_ld:
        try:
            value = json.loads(raw)
            structured.extend(value if isinstance(value, list) else [value])
        except json.JSONDecodeError:
            continue
    text = re.sub(r"\s+", " ", " ".join(parser.text)).strip()
    return {
        "website_status": "ok",
        "website_final_url": final_url,
        "website_title": re.sub(r"\s+", " ", " ".join(parser.title)).strip(),
        "website_text_excerpt": text[:1000],
        "website_jsonld": structured[:20],
    }

from venue_pipeline_backend.venue_pipeline.google_places import discover
from venue_pipeline_backend.venue_pipeline.models import Area
from venue_pipeline_backend.venue_pipeline.official_sources import _linked_pages


class FakeGoogle:
    def nearby(self, area, included_type):
        return [{
            "id": "places/abc123",
            "displayName": {"text": "Same Venue"},
            "location": {"latitude": 28.55, "longitude": 77.20},
        }]


def test_google_discovery_deduplicates_place_id_and_retains_category_provenance():
    areas = [Area("Hauz Khas", "New Delhi", "Delhi", 28.55, 77.20)]
    failures = []
    rows = discover(FakeGoogle(), areas, max_workers=2, failures=failures)
    assert failures == []
    assert len(rows) == 1
    assert rows[0]["google_place_id"] == "abc123"
    assert set(rows[0]["discovered_types"]) == {"bar", "night_club", "pub", "restaurant", "cafe"}


def test_official_source_page_linking_is_same_domain_and_prioritizes_evidence_pages():
    html = '''
      <a href="/menu">Menu</a>
      <a href="https://example.com/events">Events</a>
      <a href="https://other.example/menu">Other</a>
      <a href="/privacy">Privacy</a>
    '''
    pages = _linked_pages(html, "https://example.com/", limit=10)
    assert "https://example.com/menu" in pages
    assert "https://example.com/events" in pages
    assert "https://other.example/menu" not in pages
    assert "https://example.com/privacy" not in pages

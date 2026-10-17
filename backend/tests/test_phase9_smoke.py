from backend.tools.smoke_test import public_catalogue_is_safe


def test_smoke_accepts_safe_public_catalogue():
    assert public_catalogue_is_safe(b'{"items":[{"id":"v1","publication_status":"PUBLISHED","eligibility_status":"AUTO_APPROVED"}]}')


def test_smoke_rejects_live_google_fields_in_public_catalogue():
    assert not public_catalogue_is_safe(b'{"items":[{"id":"v1","openingHours":{}}]}')


def test_smoke_allows_shuffl_media_field():
    assert public_catalogue_is_safe(b'{"items":[{"id":"v1","photos":[]}]}')


def test_smoke_rejects_non_published_public_item():
    assert not public_catalogue_is_safe(b'{"items":[{"id":"v1","publication_status":"DRAFT"}]}')

from backend.app.release_scope import release_scope


def test_mvp_release_scope_defers_non_mvp_features(monkeypatch):
    monkeypatch.setenv("VENUE_PIPELINE_LOCKED", "1")
    scope = release_scope()

    assert scope["release"] == "mvp"
    assert scope["venue_catalogue"]["locked"] is True
    assert scope["venue_catalogue"]["opening_hours"] == "display_time_live"
    assert scope["venue_catalogue"]["google_reviews_persisted"] is False
    assert scope["features"]["gold_campaign"] is True
    assert scope["features"]["messages_shuffl"] is True
    assert scope["features"]["automatic_outing_plan"] is False

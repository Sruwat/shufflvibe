from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    assert client.get('/health').json()['status'] == 'ok'

def test_plan_generation():
    result = client.post('/v1/plans/generate', json={'scores': {'ENRG': 88, 'ROAM': 80}})
    assert result.status_code == 200
    assert result.json()['stops'] == 2  # four-hour plans are capped by the 1.75h-per-stop rule


def test_privacy_settings_persist_and_reject_invalid_visibility():
    settings = {"location_sharing": False, "approximate_presence": True, "discoverability": False, "visibility": {"profile": "nobody", "vibe": "friends"}}
    saved = client.post("/v1/privacy", json=settings)
    assert saved.status_code == 200
    assert saved.json()["settings"] == settings
    assert client.get("/v1/privacy").json() == settings

    invalid = {**settings, "visibility": {"profile": "anyone"}}
    assert client.post("/v1/privacy", json=invalid).status_code == 422


def test_plan_location_consent_requires_global_permission_and_is_revoked():
    created = client.post("/v1/plans/generate", json={"scores": {"ENRG": 88}})
    assert created.status_code == 200
    plan_id = created.json()["id"]
    endpoint = f"/v1/plans/{plan_id}/location-consent"

    assert client.get(endpoint).json() == {"approved": False}
    assert client.post(endpoint, json={"approved": True}).status_code == 409

    privacy = {"location_sharing": True, "approximate_presence": True, "discoverability": True, "visibility": {}}
    assert client.post("/v1/privacy", json=privacy).status_code == 200
    assert client.post(endpoint, json={"approved": True}).json() == {"approved": True}

    privacy["location_sharing"] = False
    assert client.post("/v1/privacy", json=privacy).status_code == 200
    assert client.get(endpoint).json() == {"approved": False}

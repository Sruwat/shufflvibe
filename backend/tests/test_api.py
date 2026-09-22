from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    assert client.get('/health').json()['status'] == 'ok'

def test_plan_generation():
    result = client.post('/v1/plans/generate', json={'scores': {'ENRG': 88, 'ROAM': 80}})
    assert result.status_code == 200
    assert result.json()['stops'] == 2  # four-hour plans are capped by the 1.75h-per-stop rule

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    assert client.get('/health').json()['status'] == 'ok'

def test_plan_generation():
    result = client.post('/v1/plans/generate', json={'scores': {'ENRG': 88}})
    assert result.status_code == 200
    assert result.json()['stops'] == 3

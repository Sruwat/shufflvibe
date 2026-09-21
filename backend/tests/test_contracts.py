from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_social_and_safety_contracts():
    assert client.post('/v1/rooms', json={'title': 'Friday'}).status_code == 200
    assert client.post('/v1/rooms/join-requests', json={'room_id': 'room-demo'}).json()['status'] == 'pending'
    assert client.post('/v1/privacy', json={'location_sharing': False}).json()['saved'] is True
    assert client.post('/v1/reports', json={'target_id': 'user-2', 'reason': 'spam'}).json()['status'] == 'received'

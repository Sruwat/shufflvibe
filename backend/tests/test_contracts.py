from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_social_and_safety_contracts():
    assert client.post('/v1/rooms', json={'title': 'Friday'}).status_code == 200
    assert client.post('/v1/rooms/join-requests', json={'room_id': 'room-demo'}).json()['status'] == 'pending'
    assert client.post('/v1/privacy', json={'location_sharing': False}).json()['saved'] is True
    assert client.post('/v1/reports', json={'target_id': 'user-2', 'reason': 'spam'}).json()['status'] == 'received'

def test_room_host_freezes_plan_and_join_request_is_resolved():
    room = client.post('/v1/rooms', json={'title': 'Parity room'}).json()
    plan = client.post('/v1/plans/generate', json={'scores': {'ENRG': 82, 'ROAM': 70}}).json()
    hosted = client.post(f"/v1/rooms/{room['id']}/host", params={'plan_id': plan['id']})
    assert hosted.status_code == 200
    assert hosted.json()['status'] == 'hosted'
    assert hosted.json()['plan_id'] == plan['id']
    request = client.post('/v1/rooms/join-requests', json={'room_id': room['id'], 'note': 'Joining solo'}).json()
    result = client.post(f"/v1/rooms/{room['id']}/join-requests/{request['id']}/decision", json={'status': 'accepted'})
    assert result.status_code == 200
    assert result.json()['request']['status'] == 'accepted'
    assert result.json()['plan_frozen'] is True

def test_capsule_approval_privacy_and_notifications_persist():
    room = client.post('/v1/rooms', json={'title': 'Capsule room'}).json()
    capsule = client.post('/v1/capsules', json={'room_id': room['id'], 'member_ids': ['member-a', 'member-b']}).json()
    first = client.post(f"/v1/capsules/{capsule['id']}/approvals", json={'member_id': 'member-a', 'approved': True}).json()
    assert first['status'] == 'awaiting_approval'
    final = client.post(f"/v1/capsules/{capsule['id']}/approvals", json={'member_id': 'member-b', 'approved': True}).json()
    assert final['status'] == 'approved'
    saved = client.post('/v1/privacy', json={'location_sharing': False, 'visibility': {'vibe': 'friends'}}).json()
    assert client.get('/v1/privacy').json() == saved['settings']
    notification = client.get('/v1/notifications').json()['items'][0]
    marked = client.post(f"/v1/notifications/{notification['id']}/read").json()
    assert marked['read'] is True

def test_missing_resources_return_not_found():
    assert client.post('/v1/plans/not-a-plan/lock').status_code == 404
    assert client.post('/v1/rooms/not-a-room/join-requests', json={'room_id': 'not-a-room'}).status_code == 404

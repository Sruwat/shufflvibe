from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_social_and_safety_contracts():
    assert client.post('/v1/rooms', json={'title': 'Friday'}).status_code == 200
    assert client.post('/v1/rooms/join-requests', json={'room_id': 'room-demo', 'scores': {'ENRG': 12, 'AFFIL': 88, 'CROWD': 12, 'TALK': 70, 'ROAM': 12, 'MOVE': 12, 'GAMES': 12}}).json()['status'] == 'pending'
    assert client.post('/v1/privacy', json={'location_sharing': False}).json()['saved'] is True
    assert client.post('/v1/reports', json={'target_id': 'user-2', 'reason': 'spam'}).json()['status'] == 'received'

def test_room_host_freezes_plan_and_join_request_is_resolved():
    room = client.post('/v1/rooms', json={'title': 'Parity room'}).json()
    plan = client.post('/v1/plans/generate', json={'scores': {'ENRG': 12, 'AFFIL': 88, 'CROWD': 12, 'TALK': 70, 'ROAM': 12, 'MOVE': 12, 'GAMES': 12}}).json()
    hosted = client.post(f"/v1/rooms/{room['id']}/host", params={'plan_id': plan['id']})
    assert hosted.status_code == 200
    assert hosted.json()['status'] == 'hosted'
    assert hosted.json()['plan_id'] == plan['id']
    request = client.post('/v1/rooms/join-requests', json={'room_id': room['id'], 'member_id': 'joiner-17', 'note': 'Joining solo', 'scores': {'ENRG': 12, 'AFFIL': 88, 'CROWD': 12, 'TALK': 70, 'ROAM': 12, 'MOVE': 12, 'GAMES': 12}}).json()
    assert request['member_id'] == 'joiner-17'
    assert client.get(f"/v1/rooms/{room['id']}/join-requests").json()['items'][0]['id'] == request['id']
    listed = client.get('/v1/rooms?status=hosted').json()['items']
    assert all('join_requests' not in item for item in listed)
    assert client.post('/v1/rooms/join-requests', json={'room_id': room['id'], 'member_id': 'joiner-17', 'scores': {'ENRG': 12, 'AFFIL': 88, 'CROWD': 12, 'TALK': 70, 'ROAM': 12, 'MOVE': 12, 'GAMES': 12}}).json()['id'] == request['id']
    result = client.post(f"/v1/rooms/{room['id']}/join-requests/{request['id']}/decision", json={'status': 'accepted'})
    assert result.status_code == 200
    assert result.json()['request']['status'] == 'accepted'
    assert result.json()['plan_frozen'] is True
    assert 'joiner-17' in result.json()['room']['members']
    assert client.get(f"/v1/rooms/{room['id']}/join-requests").json()['items'] == []

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
    assert client.post('/v1/rooms/join-requests', json={'room_id': 'not-a-room', 'member_id': 'missing-room-joiner'}).status_code == 404


def test_report_validation_and_block_lifecycle():
    target = 'safety-test-user'
    created = client.post('/v1/blocks', json={'target_id': target})
    assert created.status_code == 200
    assert created.json() == {'target_id': target, 'blocked': True}
    assert target in client.get('/v1/blocks').json()['items']
    assert client.post('/v1/blocks', json={'target_id': 'demo-user'}).status_code == 422
    removed = client.delete(f'/v1/blocks/{target}')
    assert removed.status_code == 200 and removed.json()['blocked'] is False
    assert target not in client.get('/v1/blocks').json()['items']
    report = client.post('/v1/reports', json={'target_id': target, 'reason': 'Harassment: repeated unwanted contact'})
    assert report.status_code == 200 and report.json()['status'] == 'received'
    assert report.json()['reason'].startswith('Harassment:')
    assert client.post('/v1/reports', json={'target_id': 'demo-user', 'reason': 'Something else'}).status_code == 422
    assert client.post('/v1/reports', json={'target_id': target, 'reason': '   '}).status_code == 422


def test_join_request_contract_rejects_invalid_members_and_requires_hosted_room():
    room = client.post('/v1/rooms', json={'title': 'Not hosted yet'}).json()
    assert client.post('/v1/rooms/join-requests', json={'room_id': room['id'], 'member_id': 'joiner'}).status_code == 409
    assert client.post('/v1/rooms/join-requests', json={'room_id': 'room-demo', 'member_id': '   '}).status_code == 422
    assert client.get('/v1/rooms/missing/join-requests').status_code == 404


def test_room_join_gate_rejects_vibe_shape_mismatch():
    result = client.post('/v1/rooms/join-requests', json={
        'room_id': 'room-demo',
        'member_id': 'mismatch-user',
        'scores': {'ENRG': 95, 'AFFIL': 5, 'CROWD': 5, 'TALK': 5, 'ROAM': 95, 'MOVE': 95, 'GAMES': 95},
    })
    assert result.status_code == 409
    assert result.json()['detail']['code'] == 'plan_shape_mismatch'
    assert result.json()['detail']['reasons']

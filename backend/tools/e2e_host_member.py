"""Run the disposable host/member launch journey against a running API."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
import uuid


def call(base: str, method: str, path: str, payload: dict | None = None, token: str = "") -> tuple[int, dict]:
    body = None if payload is None else json.dumps(payload).encode()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(base.rstrip("/") + path, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode())


def expect(status: int, body: dict, expected: int = 200) -> dict:
    if status != expected:
        raise RuntimeError(f"E2E request failed: status={status} body={body}")
    return body


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8005")
    args = parser.parse_args()
    suffix = uuid.uuid4().hex[:10]
    _, host = call(args.base_url, "POST", "/v1/auth/register", {"email": f"e2e-host-{suffix}@example.test", "password": "E2E-Host-12345", "name": "E2E Host"})
    _, member = call(args.base_url, "POST", "/v1/auth/register", {"email": f"e2e-member-{suffix}@example.test", "password": "E2E-Member-12345", "name": "E2E Member"})
    host_token = host["access_token"]
    member_token = member["access_token"]
    venues = expect(*call(args.base_url, "GET", "/v1/venues?city="))
    chosen = venues.get("items", [])[:2]
    if len(chosen) < 2:
        raise RuntimeError("At least two published venues are required")
    stops = [{"venue_id": venue["id"], "name": venue["name"], "area": venue.get("area") or "Delhi NCR", "stop_index": index} for index, venue in enumerate(chosen)]
    plan = expect(*call(args.base_url, "POST", "/v1/plans", {"title": "E2E Test Night", "duration_hours": 4, "scores": {"ENRG": 70}, "stops": stops, "chemistry": {"source": "launch-e2e"}}, host_token))
    room = expect(*call(args.base_url, "POST", "/v1/rooms", {"title": "E2E Host Member Room", "member_ids": [], "visibility": "friends"}, host_token))
    expect(*call(args.base_url, "POST", f"/v1/rooms/{room['id']}/host?plan_id={plan['id']}", token=host_token))
    invite = expect(*call(args.base_url, "POST", f"/v1/rooms/{room['id']}/invite", token=host_token))
    joined = expect(*call(args.base_url, "POST", "/v1/rooms/join-by-invite", {"invite_token": invite["invite_token"]}, member_token))
    shared = expect(*call(args.base_url, "GET", f"/v1/rooms/{room['id']}/plan", token=member_token))
    if shared.get("id") != plan["id"] or not shared.get("locked"):
        raise RuntimeError("Member did not receive the same locked plan")
    message = expect(*call(args.base_url, "POST", "/v1/conversations/messages", {"conversation_id": "conversation-demo", "body": "launch e2e message"}, member_token))
    print(json.dumps({"passed": True, "room_id": room["id"], "plan_id": plan["id"], "member_id": member.get("user", {}).get("id"), "message_id": message.get("id"), "member_count": len(joined.get("members", []))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

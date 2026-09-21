from datetime import datetime, timezone
from typing import Any
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="SHUFFL API", version="0.1.0")

class Answer(BaseModel):
    card_id: str
    action: str
    score: int = Field(ge=0, le=100)

class PlanRequest(BaseModel):
    scores: dict[str, float]
    members: list[str] = []

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "shuffl-api"}

@app.post("/v1/sessions")
def create_session() -> dict[str, Any]:
    return {"id": "demo-session", "mode": "demo", "created_at": datetime.now(timezone.utc).isoformat()}

@app.get("/v1/profiles/me")
def profile() -> dict[str, Any]:
    return {"name": "Aarav Mehta", "city": "New Delhi", "preferences": {"FOOD": 88, "SCEN": 88, "NOV": 62}}

@app.post("/v1/assessment/answers")
def answer(payload: Answer) -> dict[str, Any]:
    return {"accepted": True, "card_id": payload.card_id, "score": payload.score}

@app.post("/v1/plans/generate")
def generate_plan(payload: PlanRequest) -> dict[str, Any]:
    energy = payload.scores.get("ENRG", 62)
    return {"style": "Could Go Late" if energy >= 70 else "Settle Then Roam", "stops": 3 if energy >= 70 else 2, "venues": ["Sidecar, GK-2", "Majnu ka Tila Lane", "Sunder Nursery"]}

@app.post("/v1/plans/{plan_id}/lock")
def lock_plan(plan_id: str) -> dict[str, Any]:
    return {"id": plan_id, "status": "locked"}

@app.get("/v1/discovery")
def discovery() -> dict[str, Any]:
    return {"items": [{"name": "Sidecar, GK-2", "type": "pub", "area": "Greater Kailash II"}, {"name": "Sunder Nursery", "type": "open ground", "area": "Nizamuddin"}]}

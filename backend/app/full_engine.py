"""Deterministic demo engine port of the current V10/V4 assessment boundary.

This module is intentionally side-effect free so fixtures can compare mobile and API output.
"""
from dataclasses import dataclass, field
from statistics import mean, pstdev
from typing import Literal

FACTORS = ("ENRG", "AFFIL", "CROWD", "TALK", "ROAM", "MOVE", "GAMES")
SWIPE_SCORE = {"LOVE": 88, "UP": 62, "DOWN": 38, "HARD_PASS": 12}
Action = Literal["LOVE", "UP", "DOWN", "HARD_PASS"]

@dataclass(frozen=True)
class Card:
    id: str
    factor: str
    side: Literal["A", "B"]

@dataclass
class Exposure:
    card: Card
    started_at: float
    ended_by: str | None = None
    latency: float | None = None
    next_count: int = 0

@dataclass
class AssessmentSession:
    queue: list[Card] = field(default_factory=lambda: [Card(f"V-{factor}-A", factor, "A") for factor in FACTORS])
    cursor: int = 0
    exposures: list[Exposure] = field(default_factory=list)
    answers: dict[str, Action] = field(default_factory=dict)
    scores: dict[str, int] = field(default_factory=dict)
    paused: bool = False
    away_prompt: bool = False

    @property
    def current(self) -> Card | None:
        return self.queue[self.cursor] if self.cursor < len(self.queue) else None

    def answer(self, action: Action) -> None:
        card = self.current
        if not card or self.paused:
            return
        self.answers[card.id] = action
        self.scores[card.factor] = SWIPE_SCORE[action]
        self.exposures.append(Exposure(card=card, started_at=0, ended_by="swiped"))
        if action in ("UP", "DOWN") and not any(item.factor == card.factor and item.id != card.id for item in self.queue[self.cursor + 1:]):
            self.queue.insert(min(len(self.queue), self.cursor + 3), Card(f"V-{card.factor}-B", card.factor, "B"))
        self.cursor += 1

    def defer(self, reason: Literal["next", "timeout"]) -> None:
        card = self.current
        if not card:
            return
        self.exposures.append(Exposure(card=card, started_at=0, ended_by=reason, next_count=1))
        moved = self.queue.pop(self.cursor)
        self.queue.insert(min(len(self.queue), self.cursor + 4), moved)
        if reason == "timeout" and sum(exposure.ended_by == "timeout" for exposure in self.exposures) >= 2:
            self.paused = True
            self.away_prompt = True

def firmness(scores: dict[str, float]) -> dict[str, float]:
    return {factor: abs(scores.get(factor, 50) - 50) / 50 for factor in FACTORS}

def rescale(scores: dict[str, float], centre: float = 70.5, population_spread: float = 26.5) -> dict[str, float]:
    values = list(scores.values()) or [50]
    user_mean = mean(values)
    user_spread = max(15, pstdev(values))
    stretch = 1 + 0.33 * (population_spread / user_spread - 1)
    return {factor: max(0, min(100, centre + (score - user_mean) * stretch)) for factor, score in scores.items()}

def chemistry(members: list[dict[str, float]], duration_hours: float = 4) -> dict:
    vector = {factor: round(mean(member.get(factor, 50) for member in members)) for factor in FACTORS} if members else {factor: 50 for factor in FACTORS}
    roam = vector["ROAM"]
    stops = 1 if roam < 35 else 2 if roam < 65 else min(3, max(2, int(duration_hours)))
    return {"vector": vector, "tags": ["Running Hot"] if vector["ENRG"] >= 80 else [], "formation": "Best of Both" if len(members) > 1 else "In Sync", "stops": stops}

"""Deterministic demo engine port of the current V10/V4 assessment boundary.

This module is intentionally side-effect free so fixtures can compare mobile and API output.
"""
from dataclasses import dataclass, field
from statistics import mean, pstdev
from typing import Literal

FACTORS = ("ENRG", "AFFIL", "CROWD", "TALK", "ROAM", "MOVE", "GAMES")
SWIPE_SCORE = {"LOVE": 88, "UP": 62, "DOWN": 38, "HARD_PASS": 12}
Action = Literal["LOVE", "UP", "DOWN", "HARD_PASS"]
PREFERENCE_WEIGHTS = {"FOOD": 20, "LIVE": 18, "POL": 18, "SCEN": 16, "NOV": 14, "HERIT": 14}

VENUE_TYPES = {
    "table for the night": {"ENRG": 25, "AFFIL": 85, "CROWD": 35, "TALK": 90, "MOVE": 10, "GAMES": 15},
    "quiet bar": {"ENRG": 35, "AFFIL": 75, "CROWD": 40, "TALK": 85, "MOVE": 15, "GAMES": 20},
    "buzzy restaurant": {"ENRG": 55, "AFFIL": 70, "CROWD": 70, "TALK": 65, "MOVE": 15, "GAMES": 10},
    "pub": {"ENRG": 60, "AFFIL": 60, "CROWD": 70, "TALK": 55, "MOVE": 25, "GAMES": 45},
    "games bar": {"ENRG": 65, "AFFIL": 65, "CROWD": 65, "TALK": 45, "MOVE": 40, "GAMES": 90},
    "games pub": {"ENRG": 55, "AFFIL": 70, "CROWD": 60, "TALK": 60, "MOVE": 20, "GAMES": 65},
    "live room": {"ENRG": 65, "AFFIL": 50, "CROWD": 70, "TALK": 25, "MOVE": 45, "GAMES": 10},
    "lounge / rooftop": {"ENRG": 50, "AFFIL": 45, "CROWD": 60, "TALK": 60, "MOVE": 20, "GAMES": 10},
    "club": {"ENRG": 90, "AFFIL": 30, "CROWD": 90, "TALK": 10, "MOVE": 90, "GAMES": 5},
    "street / market": {"ENRG": 60, "AFFIL": 55, "CROWD": 85, "TALK": 60, "MOVE": 60, "GAMES": 10},
    "open ground": {"ENRG": 50, "AFFIL": 70, "CROWD": 40, "TALK": 75, "MOVE": 70, "GAMES": 40},
}

DEMO_VENUES = [
    {"name": "Sidecar, GK-2", "type": "pub", "area": "Greater Kailash II", "scores": {"FOOD": 72, "LIVE": 58, "POL": 76, "SCEN": 78, "NOV": 62, "HERIT": 48}, "pol_sense": "current"},
    {"name": "Depot 48", "type": "buzzy restaurant", "area": "Khan Market", "scores": {"FOOD": 86, "LIVE": 34, "POL": 72, "SCEN": 82, "NOV": 55, "HERIT": 40}, "pol_sense": "both"},
    {"name": "Piano Man Jazz Club", "type": "live room", "area": "Safdarjung", "scores": {"FOOD": 46, "LIVE": 92, "POL": 84, "SCEN": 79, "NOV": 64, "HERIT": 38}, "pol_sense": "classy"},
    {"name": "Majnu ka Tila Lane", "type": "street / market", "area": "North Delhi", "scores": {"FOOD": 78, "LIVE": 25, "POL": 52, "SCEN": 88, "NOV": 80, "HERIT": 68}, "pol_sense": "current"},
    {"name": "Sunder Nursery", "type": "open ground", "area": "Nizamuddin", "scores": {"FOOD": 40, "LIVE": 20, "POL": 48, "SCEN": 91, "NOV": 68, "HERIT": 88}, "pol_sense": "both"},
]

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

def pole_strength(score: float, fast: bool = False) -> float:
    if score >= 80 or score <= 20:
        return 1.0
    if score >= 70 or score <= 30:
        return 0.75 if fast else 0.5
    return 0.0

def chemistry_v2(members: list[dict[str, float]], duration_hours: float = 4, strangers: bool = False) -> dict:
    """Apply the current asymmetric axis rules from CHEMISTRY_V2."""
    if not members:
        members = [{factor: 50 for factor in FACTORS}]
    vector = {factor: round(mean(member.get(factor, 50) for member in members)) for factor in FACTORS}
    tags: list[str] = []
    highs = [member.get("ENRG", 50) for member in members if pole_strength(member.get("ENRG", 50)) and member.get("ENRG", 50) >= 70]
    lows = [member.get("ENRG", 50) for member in members if pole_strength(member.get("ENRG", 50)) and member.get("ENRG", 50) <= 30]
    hi_strength = sum(pole_strength(value) for value in highs)
    lo_strength = sum(pole_strength(value) for value in lows)
    if highs and hi_strength > lo_strength:
        vector["ENRG"] = round(max(highs))
    elif highs and lows:
        pull = 0.6 if len(lows) <= 2 else 0.5 if len(lows) == 3 else 0.4
        vector["ENRG"] = round(mean(lows) + pull * (max(highs) - mean(lows)))
        tags.append("Slow Burn")
    elif all(55 <= member.get("ENRG", 50) < 80 for member in members):
        vector["ENRG"] = min(100, round(vector["ENRG"] + 10))
        tags.append("Could Go Late")
    talker = any(pole_strength(member.get("TALK", 50)) and member.get("TALK", 50) >= 70 for member in members)
    if talker:
        vector["TALK"] = max(40, vector["TALK"])
        tags.append("Buzz, Not Noise")
    affil_high = any(member.get("AFFIL", 50) >= 70 for member in members)
    affil_low = any(member.get("AFFIL", 50) <= 30 for member in members)
    if affil_high and affil_low:
        tags.append("Table and Floor")
    elif strangers or all(member.get("AFFIL", 50) <= 30 for member in members):
        tags.append("Meet the Room")
    if sum(member.get("GAMES", 50) >= 70 for member in members) > len(members) / 2:
        tags.append("Common Ground")
    roam = vector["ROAM"]
    stops = 1 if roam < 35 else 2 if roam < 65 else 3
    return {"vector": vector, "tags": tags[:2], "formation": "Best of Both" if len(members) > 1 else "In Sync", "stops": stops, "talk_floor": 40 if talker else 0}

def select_venue_types(members: list[dict[str, float]], duration_hours: float = 4, strangers: bool = False) -> list[str]:
    room = chemistry_v2(members, duration_hours, strangers)
    target = room["vector"]
    candidates = []
    for name, template in VENUE_TYPES.items():
        if room["talk_floor"] and template["TALK"] < room["talk_floor"]:
            continue
        distance = sum(abs(template[factor] - target[factor]) for factor in FACTORS if factor != "ROAM")
        if strangers and name in {"games pub", "pub", "street / market", "open ground"}:
            distance -= 12
        if "Common Ground" in room["tags"] and name in {"games pub", "games bar"}:
            distance -= 10
        candidates.append((distance, name))
    candidates.sort()
    return [name for _, name in candidates[:room["stops"]]] or ["pub"]

def preference_fit(venue: dict, members: list[dict], visited: set[str] | None = None) -> float:
    visited = visited or set()
    total = 0.0
    for member in members or [{}]:
        prefs = member.get("preferences", member)
        sense = member.get("pol_sense", "both")
        for factor, weight in PREFERENCE_WEIGHTS.items():
            if factor == "POL" and sense not in ("both", venue.get("pol_sense", "both")) and venue.get("pol_sense") != "both":
                continue
            score = 100 if factor == "NOV" and venue["name"] not in visited else 20 if factor == "NOV" else venue.get("scores", {}).get(factor, 50)
            total += (prefs.get(factor, 50) / 100) * (score / 100) * weight
    return total

def fill_venues(types: list[str], members: list[dict], venues: list[dict] | None = None, visited: set[str] | None = None) -> list[dict]:
    pool = venues or DEMO_VENUES
    used: set[str] = set()
    selected: list[dict] = []
    for venue_type in types:
        choices = [venue for venue in pool if venue.get("type") == venue_type and venue["name"] not in used]
        if not choices:
            choices = [venue for venue in pool if venue["name"] not in used]
        if not choices:
            break
        choice = max(choices, key=lambda venue: preference_fit(venue, members, visited))
        used.add(choice["name"])
        selected.append(choice)
    return selected

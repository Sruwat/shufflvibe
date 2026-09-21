# Vibe names v4 — a shape of a night, from the seven vibe factors; preferences as badges

**Supersedes `VIBE_NAMES_V3.md`** (2026-09-17). The name now reads the seven vibe factors only.
Both poles of every vibe factor are wants, so there is no refusal prefix — a firm low pole *is*
a want, with a word. Preferences never enter the name; they are badges on the profile.

> **Peak Mingler** — `ENRG` high, firmest; `AFFIL` low, second
> **Quiet Table-Talker** — `CROWD` low, firmest; `TALK` high, second
> **Nomad Floor-Filler** — `ROAM` high, firmest; `MOVE` high, second

---

## 1. The shape

```
[first-factor pole word]  [second-factor pole noun]
        always                if a second qualifies
```

- **No second factor** → the single name for that pole (§3): *Night Climber*, *Slow Burner*.
- **Second factor** → pole word + pole noun: *Peak Mingler*.
- Two tokens. No prefix. Nothing about food, acts, dress, age, or newness — those are badges.

---

## 2. The word-lists — one word per pole, as first and as second

| Factor | Low pole, as first | Low pole, as second | High pole, as first | High pole, as second |
|---|---|---|---|---|
| `ENRG` | Low-Key | Slow-Burner | Peak | Climber |
| `AFFIL` | Mingling | Mingler | Inner-Circle | Insider |
| `CROWD` | Quiet | Quiet-One | Big-Room | Crowd-Chaser |
| `TALK` | Loud | Noise-Seeker | Talking | Table-Talker |
| `ROAM` | Settled | Settler | Nomad | Nomad |
| `MOVE` | Seated | Sitter | Moving | Floor-Filler |
| `GAMES` | No-Games | Lounger | Arcade | Score-Keeper |

Fourteen poles; every name is composed from these. Change a word here and every name that uses
it changes with it — never hand-edit a name.

---

## 3. The rules

### 3.1 First factor

The vibe factor with the greatest \|s − 50\| — the pole they are furthest toward. Ties: latency
(gap ≥ 0.15), then the forced choice (`ASSESSMENT_ENGINE.md` §7.3, options worded per pole).
The forced choice is the only question; the answer is the first factor.

### 3.2 Second factor

```python
STICKY, SECOND_MIN = 15, 25          # within 15 of the first by |s-50|; at least 25 from the middle

def second_factor(vibe, firmness_latency, first):
    d = {f: abs(vibe[f] - 50) for f in VIBE if f != first}
    cands = [f for f in d if d[f] >= d[first] - STICKY and d[f] >= SECOND_MIN]
    if not cands: return None
    hi = max(d[f] for f in cands); tied = [f for f in cands if d[f] == hi]
    if len(tied) == 1: return tied[0]
    tied.sort(key=lambda f: -firmness_latency[f])
    if firmness_latency[tied[0]] - firmness_latency[tied[1]] >= 0.15: return tied[0]
    return max(tied, key=lambda f: WEIGHT[f])
```

No factor is excluded from the second slot any more. `AFFIL` was excluded in V2/V3 because it
ran high for nearly everyone; with both poles as wants and the room-facing pole now a real
signal, it competes like the rest. Watch whether *Insider* ends up on half the names; if it
does, raise `SECOND_MIN` for `AFFIL` alone.

### 3.3 Assembly

```python
def name(vibe, firmness_latency):
    first  = first_factor(vibe, firmness_latency)
    second = second_factor(vibe, firmness_latency, first)
    pole   = lambda f: 'high' if vibe[f] >= 50 else 'low'
    if second is None: return SINGLE[first][pole(first)]
    return f'{FIRST_WORD[first][pole(first)]} {SECOND_WORD[second][pole(second)]}'
```

Written once per session, never recomputed within it. A different day, a different name — that
is the design; the badges are what stay.

---

## 4. The single names — when nothing else is within 15

| Factor | Low pole | High pole |
|---|---|---|
| `ENRG` | Slow Burner | Night Climber |
| `AFFIL` | Room Worker | Inner Circle |
| `CROWD` | Quiet One | Crowd Chaser |
| `TALK` | Noise Seeker | Table Talker |
| `ROAM` | Settler | Nomad |
| `MOVE` | Sitter | Floor Filler |
| `GAMES` | Lounger | Score Keeper |

Fourteen. Each is also a shape in `FACTORS_V5.md` §5, so the name and the archetype agree.

---

## 5. Badges — the preferences, on the profile

A badge for every preference swiped *the whole point*; none for the rest. Stable, editable with
the preference, shown on the profile and never on the daily reveal.

| Preference at 88 | Badge |
|---|---|
| `FOOD` | Foodie |
| `LIVE` | Gig-Goer |
| `POL` classy | Dressed For It |
| `POL` current | Hype |
| `SCEN` | Good Eye |
| `NOV` | First Timer |
| `HERIT` | Old Soul |

A person can carry several. *Foodie · Old Soul* under *Quiet Table-Talker* says everything the
old three-part name was trying to say, in the right two places.

---

## 6. Rules for anyone editing the word-lists

1. **A pole word describes a want.** The low poles are not refusals — *Quiet*, *Seated*,
   *Settled*, *Mingling* are things people go out for.
2. **Two tokens, on a card.**
3. **Nothing about a place.** If a word could be a badge, it is not a name.
4. **Change §2, regenerate the names.** Never hand-edit a pair.
5. **Watch the stability**, as before: a two-factor name will move more than a single one. The
   check from `REMINDERS.md` stands, on seven factors.

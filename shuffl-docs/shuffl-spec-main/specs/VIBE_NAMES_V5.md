# Vibe names v5 — a going-out identity, from the six identity factors; preferences as badges

**Supersedes `VIBE_NAMES_V4.md`** (2026-09-30). Four factors left the naming set when the
architecture split: `CROWD`, `ROAM` and `RAMP` moved to the **skeleton** (the user draws them, so
they are a property of tonight's plan, not of the person) and `GAMES` became a **preference**.
`FOCUS` and `SPONT` joined. The name now reads **six identity factors** and nothing else.

**What the name is for changed too.** Under V4 the name described the shape of a night the engine
was about to plan. Under V5 the plan comes from the skeleton, so the name describes **the person**
— who they are when they go out. That is the only job it has, and it is a bigger one: it is what
another user sees, and what the vibe match score is computed from.

> **Peak Front-Rower** — `ENRG` high, firmest; `FOCUS` high, second
> **Locked-In Table-Talker** — `SPONT` low, firmest; `TALK` high, second
> **Headline Mingler** — `FOCUS` low, firmest; `AFFIL` low, second

---

## 1. The shape — unchanged

```
[first-factor pole word]  [second-factor pole noun]
        always                if a second qualifies
```

- **No second factor** → the single name for that pole (§4): *Night Climber*, *Wild Card*.
- **Second factor** → pole word + pole noun: *Peak Front-Rower*.
- Two tokens. No prefix. Nothing about food, acts, dress, age, or newness — those are badges.

---

## 2. The word-lists — one word per pole, as first and as second

| Factor | Low pole, as first | Low pole, as second | High pole, as first | High pole, as second |
|---|---|---|---|---|
| `ENRG` | Low-Key | Slow-Burner | Peak | Climber |
| `AFFIL` | Mingling | Mingler | Inner-Circle | Insider |
| `TALK` | Loud | Noise-Seeker | Talking | Table-Talker |
| `FOCUS` | Headline | Headliner | Front-Row | Front-Rower |
| `MOVE` | Seated | Sitter | Moving | Floor-Filler |
| `SPONT` | Locked-In | Planner | Last-Minute | Wildcard |

Twelve poles. Every name is composed from these — change a word here and every name that uses it
changes with it. Never hand-edit a name.

**Retired word rows**, kept here so nobody re-invents them under a new name: `CROWD`
(Quiet / Big-Room), `ROAM` (Settled / Nomad), `RAMP` (Straight-In / Slow-Build), `GAMES`
(No-Games / Arcade). *Nomad* is the loss that will be felt — it was the most-liked word in the
list — but how many stops tonight has is now a line the user drags, not a thing they are.

### 2a. The one word that could be misread — `FOCUS` low

`Headline` / `Headliner` for the **low** pole inverts the everyday meaning: a headliner is
normally the act everyone is watching, and here it names the person who does not want an act. The
inversion is deliberate, because the low pole's actual claim is *we are the event* — which is what
a headliner is. *Headline Mingler* reads as "I'm the main character and I work the room," and that
is exactly right.

It is still the one word in the table a user could read backwards. **Test it before launch**: show
*Headline Act* and *Front Row* side by side and ask which one means "there's a band". If more than
a third get it wrong, the fallback is `Own-Show` / `Own-Showman`, which is uglier and unambiguous.

---

## 3. The rules

### 3.1 First factor — unchanged

The factor with the greatest **ranking key** — `|s − 50| + 5 × latency-firmness`
(`ASSESSMENT_ENGINE.md` §7.1). Score decides; latency orders within a score step. The forced
choice (§7.3) remains for a session with no latency at all.

### 3.2 Second factor — `SECOND_MIN` drops from 25 to 20

```python
STICKY, SECOND_MIN = 15, 20          # within 15 of the first by |s-50|; at least 20 from the middle

def second_factor(vibe, firmness_latency, first):
    d_first = abs(vibe[first] - 50)
    d = {f: abs(vibe[f] - 50) for f in IDENTITY if f != first}
    cands = [f for f in d if d[f] >= d_first - STICKY and d[f] >= SECOND_MIN]
    if not cands: return None
    hi = max(d[f] for f in cands); tied = [f for f in cands if d[f] == hi]
    if len(tied) == 1: return tied[0]
    return max(cands, key=lambda f: d[f] + 5 * firmness_latency.get(f, 0.0))
```

**Two reasons, and the second is the real one.**

The measured reason: with six factors instead of eight there are fewer candidates for the second
slot, so far more people fall through to a single name. On 20,000 synthetic people
(`simulations/namesim.py`):

| | distinct names used | most common name | entropy | **single-name rate** |
|---|---|---|---|---|
| V4, eight factors, `SECOND_MIN` 25 | 240 of 240 | 3.0% | 7.18 bits | **41.9%** |
| V5, six factors, `SECOND_MIN` 25 | 132 of 132 | 5.3% | 6.01 bits | **56.6%** |
| V5, six factors, **`SECOND_MIN` 20** | 132 of 132 | 3.7% | 6.49 bits | **41.8%** |

At 25, more than half of all users would get a one-factor name — the ten most common V5 names were
*all* singles. At 20 the rate lands on 41.8%, which is V4's 41.9% almost exactly.

The principled reason: **`|s − 50| ≥ 20` means a score of 30 or below, or 70 or above — which is
the firmness-band boundary the rest of the engine already uses.** The strength ladder in
`CHEMISTRY_V4.md` §0.2 calls 70–79 a lean and 31–69 no position at all; `ASSESSMENT_ENGINE.md`
uses the same edges. At 25 the naming threshold lined up with nothing. At 20 the second slot
requires exactly what every other part of the engine calls *having a position*. That is a better
rule than the number it produces, and the number it produces happens to be right.

### 3.3 Assembly — unchanged

```python
def name(vibe, firmness_latency):
    first  = first_factor(vibe, firmness_latency)
    second = second_factor(vibe, firmness_latency, first)
    pole   = lambda f: 'high' if vibe[f] >= 50 else 'low'
    if second is None: return SINGLE[first][pole(first)]
    return f'{FIRST_WORD[first][pole(first)]} {SECOND_WORD[second][pole(second)]}'
```

Written once per session, never recomputed within it.

---

## 4. The single names — when nothing else clears `SECOND_MIN`

| Factor | Low pole | High pole |
|---|---|---|
| `ENRG` | Slow Burner | Night Climber |
| `AFFIL` | Room Worker | Inner Circle |
| `TALK` | Noise Seeker | Table Talker |
| `FOCUS` | Headline Act | Front Row |
| `MOVE` | Sitter | Floor Filler |
| `SPONT` | Locked In | Wild Card |

Twelve.

---

## 5. What the vocabulary costs

**132 names against V4's 240**, and the simulation uses all 132 — no name is stranded. The honest
accounting:

- **The most common name goes from 3.0% to 3.7% of users.** Fine. Nothing is close to generic.
- **Entropy drops from 7.18 to 6.49 bits.** The name carries about a third less information than
  it did. That is the unavoidable price of four fewer factors and it is not recoverable by
  tuning — only by adding factors back, which is the thing we just decided against.
- **The first slot stays flat** — each of the six factors names 16–18% of the population. No
  factor is structurally advantaged, because the key is `|s − 50|` and every factor has the same
  spread. Losing four factors did not concentrate the name on the survivors.

**What to watch on real users**, and it will not look like the simulation: the synthetic people
above are independent on every axis. Real people are not — whoever scores high on `ENRG` will
probably score high on `MOVE`. Correlated factors collapse the vocabulary far faster than losing
factors does, because they stop producing distinct pairs. **`ENRG` × `MOVE` and `FOCUS` × `TALK`
are the two pairs most likely to collapse**, and if either does, one of them should leave the
naming set even if it stays in the match score.

---

## 6. Badges — the preferences, on the profile

Unchanged except that `GAMES` arrived, so there are now seven.

| Preference at 88 | Badge |
|---|---|
| `FOOD` | Foodie |
| `LIVE` | Gig-Goer |
| `POL` classy | Dressed For It |
| `POL` current | Hype |
| `SCEN` | Good Eye |
| `NOV` | First Timer |
| `HERIT` | Old Soul |
| `GAMES` | Always On The Table |

**`GAMES` as a badge is a promotion, not a demotion.** As a vibe factor it was the weakest thing
in the set — nearly one-ended, and a firm low was mostly indifference. As a badge it does the one
job it was always good at: it tells the other person something true about you, and it tells the
fill stage to prefer a venue with a pool table when everything else is equal.

*Gig-Goer · Always On The Table* under *Front Row* is a profile that reads.

---

## 7. Rules for anyone editing the word-lists

1. **A pole word describes a want.** The low poles are not refusals — *Seated*, *Mingling*,
   *Locked-In*, *Headline* are things people go out for.
2. **Two tokens, on a card.**
3. **Nothing about a place.** If a word could be a badge, it is not a name.
4. **Nothing the skeleton owns.** How many stops, how full, in what order — those are lines the
   user drags. A word for any of them is a category error now, not just a style mistake.
5. **Change §2, regenerate the names.** Never hand-edit a pair.
6. **Re-run `namesim.py` after any change** to `SECOND_MIN`, `STICKY` or the factor set, and check
   the single-name rate first — it is the number that moves.

# Vibe factors and preferences — the split, explored

**Status: exploration, 2026-09-17. Not yet written into the engine specs. Written without reference to
the Google Forms results — the app is the test bed from here.** This document works
through the user's proposal — five of the ten factors are *preferences* that choose venues and
do not change day to day; five are *vibe factors* that shape the night and do — and what the
model becomes if the split is taken. It ends with what it solves, what it breaks, and what needs
a decision before the specs are rewritten.

---

# 0. The proposal, restated

| | Factors | What they are | Change | Measured |
|---|---|---|---|---|
| **Preferences** | `FOOD` `LIVE` `HERIT` `NOV` `SCEN` | how important a *thing* is to you in a place | rarely — set once, editable in the profile | onboarding: "Swipe on the following things on the basis of how important they are to you in a place" — an image of the thing |
| **Vibe factors** | `ENRG` `ACTIV` (was `PLAY`) `AFFIL` `POL` `CROWD` | the *shape* of tonight | daily | the daily deck — scenes, as now |

The night is shaped by the vibe factors and they are **untouchable**: three people high on
`AFFIL`, `ENRG` and `ACTIV` get a night that builds, centred on the people in the room, with
something to do at every stop. The preferences are how the venues for that night are chosen,
and they are **suppressible** — a low `LIVE` score does not mean the person minds live music, it
means it should not be the focus; a high one means they are fine with it being the whole point.
Only when no night can include everyone's vibe factors do bend, firmness, latency, the second-best
vibe factor, and concession, debt and payback come in — on vibe factors only.

---

# 1. Why the split is right — the asymmetry it names

The whole §13.4c family was built on a single scale where 12 on `LIVE` and 12 on `ENRG` meant
the same kind of thing. They do not.

- **A low preference is an absence of interest.** `LIVE` 12: the act is not why they are out. They
  will sit through one. Nothing is violated.
- **A low vibe factor is a want.** `ENRG` 12: a calm night is *what they want*. A rave violates it.

So preferences are **one-ended** — 0 is "irrelevant", 100 is "the point", and there is no
aversion anywhere on the scale. Vibe factors are **two-ended** — both poles are wants (calm ↔
building; own table ↔ the room; casual ↔ dressed; empty ↔ packed; sit and talk ↔ do something),
and the middle is "don't mind". Half the machinery of the last three days — `AVERSION_FLOOR`,
"a served want compensates an overrun aversion", Aarav-hates-live-music — was compensating for
treating one-ended things as two-ended.

| | Preference | Vibe factor |
|---|---|---|
| scale | importance, 0–100 | shape, 0–100, both ends wanted |
| aversion | none — ever | the far pole |
| hard pass | none — the fourth swipe is "don't care" | yes — a firm pole |
| firmness | importance / 100 (low importance abstains) | \|s − 50\| / 50, as now |
| in a group | suppressible — weighted by who cares | untouchable — every member's, within bend, at every stop |
| bend | not needed | as now |
| debt / payback | none | yes, when the shape cannot fit everyone |
| in the name | a badge on the profile | the daily name |
| learning | edited, rarely re-checked | the daily state against a baseline (`PREFERENCE_ENGINE_V2`) |

---

# 2. The cards

**Onboarding, once.** Five preference cards, each the *thing itself* — a plate, a band on a
stage, an old stone courtyard, an unmarked door, a beautiful room. Before them:

> *Swipe on the following things on the basis of how important they are to you in a place.*

Four swipes, reworded for importance — the same gestures, the same colours:

| Swipe | Reads as | Score |
|---|---|---|
| **The whole point** (gold, up) | fine as the sole focus of the night | 88 |
| **Nice to have** (green, right) | | 62 |
| **Don't mind** (grey, left) | | 38 |
| **Don't care** (red, down) | irrelevant — *not* an aversion | 12 |

No second card per preference — importance is not ambiguous the way a scene is. Five cards. The
`POL` sense (classy / current, `ASSESSMENT_ENGINE.md` §5.4) moves here too: it is a stable
taste, asked once as an image pair, kept in the profile. Preferences live in the profile section
and can be edited any time; otherwise they do not change.

**Every day.** The vibe deck only: five factors, one card each, a second if the first swipe was
mild (§2.2 adaptive rule) — **five to ten cards**, down from ten to twenty. `ACTIV` replaces
`PLAY` and widens: games, bowling, karaoke, a dance floor — *something to do* rather than sit.
The "same as yesterday?" swipe, Next, Back, latency, the pause — unchanged.

**What the cards can now be.** The thing that made `SCEN` and `HERIT` untestable in words — they
are visual — is no longer a problem: a preference card *is* a picture of the thing. The vibe
cards keep the scene-and-a-feeling treatment they have.

---

# 3. The profile

```
vibe today:      ENRG 82  ACTIV 70  AFFIL 88  POL 45  CROWD 60        -> the name
preferences:     FOOD 88  LIVE 12  HERIT 50  NOV 62  SCEN 72  · POL sense: classy   -> badges, editable
```

**The name** comes from the vibe factors alone (§7 below). **Badges** come from preferences at
"the whole point": *Foodie*, *Gig-Goer*, *Old Soul*, *Explorer*, *Good Eye* — stable, on the
profile, not on the daily reveal. The two-part identity the naming work kept fighting for — a
stable "who I am" and a moving "what I want tonight" — falls out of the split by itself.

---

# 4. The plan engine — shape, then type, then venue

**The user's statement, 2026-09-17, which is the architecture:** the vibe factors give the
shape of the night — the number of stops, the kind of atmosphere at each, the crowds, the things
to do. From the shape, the **type of venue** needed at each stop is chosen. Then the preferences
come in: at each venue, each person's preferences are served as far as availability allows.
**The venue type is never altered by a preference — only the exact venue.**

### 4.1 Shape (vibe factors → the stops and their types)

| Vibe factor | What it fixes in the shape |
|---|---|
| `ROAM` | how many stops (capped by the duration input), how far apart |
| `ENRG` | the arc — where the night starts and how it builds |
| `TALK` | at each stop, whether you can hear each other |
| `CROWD` | how full each stop should be |
| `GAMES` | whether a stop needs games on the premises |
| `MOVE` | whether a stop needs room to be on your feet — a floor |
| `AFFIL` | whether the setting faces the table or the room |

The room's vibe vector (abstention over the seven) and the arc turn into a list of stops, each
with a **venue type** — a template defined on the vibe axes, not on preferences: *quiet bar*,
*buzzy restaurant*, *games bar*, *live room*, *club*, *lounge*, *rooftop*, *table for the night*
… Every venue in the database carries a type, from its own vibe-axis scores. Every stop's type
must sit inside every member's bend on every vibe factor. That is the untouchable part.

When it cannot — members at opposite poles — this is where the built machinery runs, on vibe
factors only: firmness and latency rank each person's vibe wants, the stop's type is a
compromise on the best-ranked one the group can hold, and concession, debt and payback carry
across stops (§13.4c rules 1–8, 10 on vibe); reach and reserved stops; friend mode's relaxed
bends. Rule 9 and `AVERSION_FLOOR` are retired — on vibe factors both poles are wants and the
one-ended special case is gone.

### 4.2 Fill (preferences → the exact venue of that type)

At each stop, among the venues **of the type the shape fixed**, choose the one that serves the
members' preferences best:

```python
def fill(stop_type, members, used):
    pool = [v for v in venues if v.type == stop_type and v not in used and available(v, stop.time)]
    return max(pool, key=lambda v: pref_fit(v, members) - room_cost(members, v))

def pref_fit(venue, members):
    """Each person's each preference, served as far as the venue allows; importance is the weight,
    so the people who care set it and the people who don't abstain. Whole-point preferences not yet
    had tonight count double (the floor below)."""
    return sum((m.pref[f] / 100) * (2 if m.pref[f] >= 75 and f not in had[m.id] else 1) * min(venue[f], m.pref[f])
               for m in members for f in PREFS)
```

A preference never changes the type. If the shape says *club* at stop 3, the food person gets
the club with the best kitchen, not a restaurant.

**The one floor — rule 10, on preferences.** For every member, every preference swiped *the
whole point* must be *had* by at least one stop's venue in the night (the venue scores ≥
`DELIVERS` on it). Not centred on — had. It is implemented as the doubling above: an un-had
whole-point preference pulls the exact-venue choice hardest at each successive stop until it is
had; if two members' whole-point preferences cannot share a venue of the type, the pull rotates
— one stop's venue leans to hers, the next's to his — inside the same type, with no debt,
because nothing on the vibe was conceded. A whole-point preference no venue of any type in the
night can serve is said on the card and logged as a venue gap.

### 4.3 What this does to the existing sections

| Section | Becomes |
|---|---|
| §5.3 bend, `PASSIVE` / participatory | bend on five vibe factors; the passive/participatory split disappears — preferences have no overshoot and vibe factors are all participatory |
| §13.4 `FLOOR` v3, `ranked_wants`, `serve_level` | on vibe wants (both poles), for the shape stage; a parallel `pref_served` for the fill stage |
| §13.4c rules 1–10 | unchanged in logic, vibe-only; `AVERSION_FLOOR` and rule 9 are no longer needed (they existed to soften one-ended factors treated as two-ended) |
| §13.6 chemistry | on five vibe axes — §6 below |
| §13.7 area fallback | `CROWD` `ENRG` `POL` in the shape stage; `SCEN` in the fill stage |
| §13.9 friend mode | relaxed bends on vibe factors; the combination search runs on vibe wants, then preferences fill |
| §13.4a joiner's gate | shape must fit them at every stop (untouchable) — the hard part; preference fit is the soft part that sorts *strong* from *other* |
| `BLEND_STYLE_DATABASE_V2` | re-derived on five axes — §6 |
| `FACTORS_AND_VIBES_V4` | the 42 library vibes split into a vibe-shape and a preference-tag each |
| `PREFERENCE_ENGINE_V2` | the learning layer runs on vibe factors; preferences get a slow re-check (60 days) and update from venues attended |
| `AREA_SCORES_V1` | unchanged |

---

# 5. What it solves — the list is long

1. **"He hates live music."** He doesn't; it is just not his thing. Rule 9, `AVERSION_FLOOR`, the
   Piano Man workaround — all of it was this one confusion.
2. **The deck.** Five to ten cards a day instead of ten to twenty, with nothing lost, because
   the five that never changed were being asked every day.
3. **`SCEN` and `HERIT` untestable in words.** A picture of the thing, once.
4. **The name's stability.** The daily name reads five moving factors; the stable identity
   lives in badges. V3's three-part-name stability worry mostly dissolves.
5. **The learning layer's hardest job** — deciding which factors have settled — is half done by
   construction: five settle at onboarding.
6. **Room chemistry gets psychology it can stand on.** Five axes with a literature each (§6).
7. **Joining a public room** splits cleanly: does the *shape* fit me (gate) and do the venues
   have my things (sort). Both questions were tangled in one score.
8. **Blend style names can be group archetypes** — "the whole team out", "the catch-up", "the
   send-off" — because they are now shapes of an evening, not mixtures of venue attributes.
9. **Debt and payback shrink to where they belong.** Five factors, both poles real, no aversion
   special case.
10. **The room's mood can move without its taste moving.** A room's food weight does not change
    because a low-energy person joined. That was a real problem: identity and appetite were one
    vector.

---

# 6. Room chemistry on five vibe axes — with the psychology attached

Each axis has a body of work on how it behaves in a group. The states of §13.6.2 stay; what
changes is that they can now be *explained*, and named as human group types.

| Axis | Group behaviour, from the literature | What the engine can say |
|---|---|---|
| `ENRG` | arousal is contagious in groups (Barsade 2002; Hatfield et al. 1994) — it converges upward when nobody blocks it and downward when one firm person does | *Could Go Late* is real: a room with no firm-low member drifts up; a firm-low member is a ceiling, not a vote |
| `AFFIL` | affiliation is *similar*, not complementary (Horowitz et al. 2006): people who want their own table and people who want the room do not meet halfway — they split the night | a room mixed on `AFFIL` is the clearest *Something for Everyone*; low-`AFFIL` members are the ones public rooms exist for |
| `ACTIV` | shared activity bridges divergent groups (Sherif 1961 — superordinate goals; also Csikszentmihalyi's flow) | a stop with something to *do* is the cheapest way to hold a mixed room together — the engine's first move when `AFFIL` or `ENRG` split |
| `CROWD` | density tolerance is individual and stable within a night (Freedman 1975; Stokols 1972) — crowding is felt when it blocks a goal | crowd is the axis most safely served by the *area* rather than the venue: the street can be packed while the table is yours |
| `POL` | self-presentation is a norm one dresses *to* (Goffman 1959); under-dressed is felt as exclusion, over-dressed is not | the floor rule from 2026-09-02 returns, on the right factor: the least dressed-up member binds |

**Named group types**, as the user asked — a vibe shape translated into people:

| Shape | Reads as |
|---|---|
| `AFFIL` high · `ENRG` high · `ACTIV` high | *the whole team out* — a night that builds, our people, something to do at every stop |
| `AFFIL` high · `ENRG` low · `ACTIV` low | *the catch-up* — one table, hours, nowhere to be |
| `AFFIL` low · `CROWD` high · `POL` high | *out to be seen* — the room, dressed, packed |
| `ENRG` high · `AFFIL` low · `ACTIV` high | *the send-off* — loud, everyone, anything |
| `ENRG` high in two, `ACTIV` high in one | *the room the user described*: energy wants to build, one person needs to be doing something — an arcade bar, then the club |

These are blend styles. With five axes at three levels there are 243 shapes; the clustering that
produced the 24 styles re-runs on real rooms and lands on the ones people actually form.

---

# 7. The name, on five factors

Both poles are wants, so each vibe factor has a **high word** and a **low word**, and there is
no refusal prefix — a firm low pole *is* a want with a word:

| Factor | high | low |
|---|---|---|
| `ENRG` | Peak | Low-Key |
| `ACTIV` | Arcade | Lounge |
| `AFFIL` | Inner-Circle | Mingling |
| `POL` | Luxury / Hype (sense) | Casual |
| `CROWD` | Big-Room | Quiet |

**Name = the pole word of the firmest vibe factor + the pole noun of the second**, second within
15 of the first by \|s − 50\|: *Peak Mingler*, *Low-Key Inner-Circle*, *Quiet Lounger*, *Big-Room
Arcade*. Twenty pairs plus ten single names (the V2 ten, re-cut to five factors: *Night Climber*,
*Score Keeper*, *Inner Circle*, *Dressed For It*, *Crowd Chaser*, and five for the low poles —
*Slow Burner*, *Table Talker*, *Room Worker*, *Come As You Are*, *Quiet One*). A much smaller
table than V3's ninety-nine, and every name is a shape of a night, which is what a daily name
should be. Preferences become badges (§3).

---

# 8. More vibe factors? Three candidates

The test for a vibe factor: it shapes the night, it changes day to day, both ends are wants,
and a card can carry it.

| Candidate | Poles | Shapes | Day-to-day? | Verdict |
|---|---|---|---|---|
| **`ROAM`** | settle in one place ↔ hop around | how many stops, how far apart, whether the plan is a plan | strongly — "one place tonight" vs "let's move" is a nightly mood | **add.** The engine currently sets stop count from duration alone; this is the missing input, and *The Long Table* vs *Chase the Night* already exist as styles waiting for it |
| **`TALK`** | conversation ↔ noise | at a given energy, a buzzy restaurant or a club; seating, acoustics | yes — "I actually want to talk tonight" | **add.** Distinct from `ENRG` (a lively room can be either) and from `AFFIL` (you can want your own people and still want music you cannot talk over). Fills a hole between *Small and Perfect* and *Big Room, Loud Night* |
| **`OPEN-AIR`** | indoors ↔ outside | terraces, gardens, rooftops — Delhi October to March | with the weather more than with the mood | **not a card.** A seasonal switch the app sets from the weather plus a profile preference; it would be answered the same way every day of a season |

Also considered and folded: *dance* (into `ACTIV`), *spend* (already a manual input; a mood, but
one people prefer to state as a number), *early / late* (the plan's timing), *celebrate /
unwind* (real, but it is `ENRG` × `AFFIL` in practice, and no single card carries it).

With `ROAM` and `TALK`: **seven vibe factors, seven to fourteen cards a day.** Still fewer than
now, with two things measured that never were. Weights to be re-derived; the two new ones start
at the bottom of the table (6 each) and earn their place from data.

---

# 9. What it breaks, honestly

- **Every spec** carries the ten-factor assumption in its bones — bend, `FLOOR`, the blend
  database, the vibe library, the names. This is a rewrite of the plan engine's §5 and §13, the
  assessment engine's §1, §2, §4–7, and both databases. Two days of work, not two hours.
- **Two new factors mean two new card sets** with no data behind them, on top of the images
  already owed.
- **`POL` is on the borderline.** Dressed-up is a daily mood *and* a stable taste. The split here
  is level daily (vibe), sense stable (preference). It may turn out `POL` is a preference outright.
- **The 42 library vibes** were archetypes on ten factors. Split into a shape and a tag each,
  some collapse into one another. The library gets smaller, which is probably right.

---

# 10. Decided, 2026-09-17

| # | Decision | Taken |
|---|---|---|
| 1 | The split. `PLAY` becomes **two** vibe factors: `GAMES` (needs the venue to have games) and `MOVE` (general — dancing, being on your feet). | yes |
| 2 | `ROAM` and `TALK` in. `OPEN-AIR` is a *preference* of the place, not the night — and left out, since it changes with the season rather than the person. | yes |
| 3 | `POL` is a **preference**, not a vibe factor. Its sense (classy / current) stays with it. | yes |
| 4 | Preference swipes are importance — whichever way you swipe is how much you care about that aspect of a venue — no aversion, no hard pass. | yes |
| 5 | The name from vibe factors only; preferences as badges. | yes |
| 6 | Debt, payback, friend mode, chemistry on vibe factors only; rule 9 and `AVERSION_FLOOR` retired. Rule 10's move to preferences — *every whole-point preference gets a stop* — explained in entry 97 and awaiting a yes. | yes / pending |

**The factor set this gives:**

| Vibe factors (daily, the shape) — 7 | Preferences (once, the venues) — 6 |
|---|---|
| `ENRG` `GAMES` `MOVE` `AFFIL` `CROWD` `ROAM` `TALK` | `FOOD` `LIVE` `HERIT` `NOV` `SCEN` `POL` (+ sense) |

Seven to fourteen cards a day; six preference cards at onboarding. Thirteen factors in all, up
from ten. Weights to be re-derived on the new set.

**A note on `GAMES`.** It may behave nearly one-ended — "I want games tonight" is a want, "no
games" is mostly indifference — so its low pole is weak: treat a *firm* low as a light steer away
from arcades, a mild low as don't-care. `MOVE` is properly two-ended (on your feet ↔ sat down).
Watch both on the first users.

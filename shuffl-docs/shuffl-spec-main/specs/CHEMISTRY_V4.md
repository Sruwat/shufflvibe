# Chemistry V4 — what these people do to each other, when the plan is no longer at stake

**Status: design, 2026-09-30. Prototyped (`simulations/chem4.py`). Supersedes `CHEMISTRY_V3.md`.**

V3 answered *what does this room want from a venue*. V4 answers a different question, because the
plan now comes from the skeleton: **who is this room?** Contagion no longer produces a venue
demand. It produces a **room identity** — and three things are built on it:

| output | used for |
|---|---|
| the room's six-factor **identity vector** | the room's name, its blend style, its colour |
| **`match`** — how close a person is to that vector | the *People* setting of the Join filter |
| **`disturbance`** — how much a person would move that vector | the point-6 question: whose room would I barely change |

**What V4 explicitly does not do:** pick a venue type, set a stop count, set an energy level for a
stop, or veto anything. All of that is the skeleton's, and `OUTING_PLAN_ENGINE.md` §15 owns it.
The *skeleton merge* — how several drawn lines in one room combine — reuses §0.3's machinery on
drawn values, but it is a separate rule set and it is not in this document.

---

# 0a. The distinction that retired, and the better one that replaced it

**V3 §0a split the axes into atmosphere axes and venue-defining axes.** A firm low on `MOVE` or
`GAMES` was undiscounted because *"I don't want a games bar"* is a position about a **kind of
place**. That entire distinction rested on chemistry choosing places. It does not any more, so it
is retired, and both of its members are gone from the set anyway — `GAMES` became a preference.

**What replaced it is a property of the axis itself, not of venues:**

> **An axis SPLITS when its two poles can be enacted at the same time, in the same room, by two
> people standing next to each other. Otherwise the axis is JOINT and the room has one value.**

| | splits | why |
|---|---|---|
| **`AFFIL`** | **yes** | some hold the table while others work the room. Both happen at once. |
| **`MOVE`** | **yes** | some are on the floor while others sit and watch. Both happen at once. |
| `ENRG` | no | a room has one volume and one temperature |
| `TALK` | no | whether you can hear each other is a fact about the room, not about a person |
| `FOCUS` | no | if there is a band, everybody is in the band's room |
| `SPONT` | no | the plan either exists or it does not. The most joint of all. |

This is a better rule than V3's because it **explains `AFFIL`'s long-standing exception instead of
leaving it as a one-off**, and it predicts its own second member. The two axes that split are
exactly the two that describe **where your body is and who you are facing** — the only two things
two people in one room can genuinely do differently.

A split axis reports `split`, not a number. It is not a failure state: *"this room needs a floor
**and** somewhere to sit"* is the most useful thing the engine can say about a room of five.

---

# 0. The machinery — unchanged from V3

These three are about people influencing people, so nothing about the architectural split touches
them.

### 0.0a A value is never an absence (2026-10-07)

> **The user: "no factor is uncertain, it just says how much you want that. A drawn `ENRG` of 50
> means they want a venue with energy but not a lot. A vibe 50 means it is not something they
> completely identify with but identify to a certain degree."**

**`strength()` used to return 0.00 across the whole 31–69 band**, and those members were then
counted as **side-less neutrals**. Measured consequence: *four people at 62 behind a leader at 85*
and *four people at 38 behind the same leader* produced an identical share — 1.00 against 0.57 —
because the model could not tell which way eight mid people were leaning.

**The mid band now advocates for its own side at `MID_W` = 0.30.**

| value | advocates |
|---|---|
| 0–20 / 80–100 | 1.00 |
| 21–30 / 70–79 | 0.50, or 0.75 if fast |
| **31–49 / 51–69** | **0.30, for the side it leans toward** |
| **exactly 50** | **0.00 — the only true neutral there is** |

**Why exactly 50 is the exception.** On a swiped factor it can only arise from a pair that
disagreed — *up for it* then *not for me* — and that is ambiguity rather than a want. On the
**skeleton** there is no such thing: `SKELETON_MERGE_V1.md` §4a already gives a drawn mid band 0.25
on exactly this argument, and says *the skeleton has no true neutrals, because nothing on it
happens by accident.* **This section makes the people side agree with it.**

### 0.0b The split test keeps the firm threshold — and that is not a nicety

**`room()` decides a split with the same call it uses for advocacy, so the change had to be made in
two places, not one.** A split is both poles being **enacted** in one room, and a mild lean enacts
nothing — one person at 62 and one at 38 is not a split.

**And a one-function patch does not merely mis-model it.** `halves()` averages the members at each
pole; a split declared from mid-band leans has nobody at 70+ or 30−, so it divides by an empty
list. Measured over 1,500 rooms, **`match()` crashed in 1,119 of them — 75%.** `firm()` exists for
this one caller.

**A third edit came with it:** `neutrals` narrowed from 31–69 to exactly 50. Leaving it would have
counted a mid member as an advocate *and* as a neutral, damping their own contribution.

---

### 0.1 Influence grows sublinearly (Latané 1981)

```python
IMPACT_EXP = 0.6
impact(pole) = (sum of strengths on that pole) ** 0.6
```

Two 88s are 1.5 times one 88, not twice. **Evidence: strong.**

### 0.2 Firmness is consistency (Moscovici 1969, 1980)

| Score | Strength |
|---|---|
| 0–20 / 80–100 | **1.0** — an extreme, consistent by construction |
| 21–30 / 70–79, swiped fast | **0.75** |
| 21–30 / 70–79, normal speed | **0.5** |
| 31–69 | **0** — no position; these are the people a leader moves |

### 0.3 The shape of every rule

```python
room_level(f) = base + pull(f) × share × (peak − base)
    base  = the plain mean on f
    share = impact(leading pole) / (impact(leading) + impact(other) + impact(neutrals))
    peak  = the most extreme score on the leading pole
    pull  = the axis's own constant
    neutrals count at 0.25 — present, but not advocating
```

---

# 1. `ENRG` — pull 0.75, low discounted to 0.55, leads high

**Unchanged.** Barsade 2002 (*The Ripple Effect*) is a direct experiment: a confederate displaying
high-activation affect raised the whole group's affect. Contagion of *high* arousal is the
documented direction; there is no literature on a calm person quieting a lively group — socially
the lively member leaves rather than converging down. **Evidence: strong.**

| Room | Mean | Reads |
|---|---|---|
| two 88s, two neutrals (45, 50) | 68 | **80** |
| one 88, two firm 12s | 37 | **58** |
| one 88, one firm 12 | 50 | **68** |

---

# 2. `TALK` — pull 0.60, low discounted to 0.50, leads high. **The floor is gone.**

**The level is unchanged.** Thorne 1987: introverts talking with extraverts behaved like
extraverts — the *partner's* sociability predicted their talk. Turn-taking (Sacks, Schegloff &
Jefferson 1974): a speaker selects the next speaker, so one person who wants conversation
structurally pulls others in. **Evidence: strong.**

| Room | Mean | Reads |
|---|---|---|
| one firm talker (88), two low-talk (20, 20) | 43 | **58** |
| one noise-wanter (12), two talkers (85, 82) | 60 | **71** |

**The absolute talk floor is retired (2026-09-30, the user).** V3 held that with any firm talker in
the room, no venue type could go under 40 on talk, because masking is physical rather than a matter
of degree. The physics has not changed — **the reason for the rule has.** The floor protected a
person from a plan the engine *inferred for them*. There is no inference left: every stop exists
because somebody dragged a line there, and every joiner sees the plan before joining. A floor now
would override a choice, not guard against a guess.

What `TALK` still does: it is a full member of the identity vector and the match score **against
other people and rooms**. **It does not score venues either (corrected 2026-10-01, the user)** —
an earlier version of this paragraph had a high-`TALK` person seeing a loud club score low while
browsing, and that is now wrong. Nothing a user swiped reaches a venue at any point.

A loud club is still a bad stop for a firm talker. The engine learns that from **the shape they
draw**, not from the card they swiped.

---

# 3. `MOVE` — pull 0.70, low discounted to 0.55, leads high, **and it splits**

**Changed, and the change follows directly from the architectural split.** V3 made `MOVE`
venue-defining on the user's 2026-09-22 correction: *mimicry is real inside a venue and is not how
a venue gets chosen — nobody books a club because one person in four fancies dancing.* That
correction was right and is now **moot**, because V4 does not choose venues. The question it asks
is the one mimicry actually answers: *will this room end up dancing?* So Chartrand & Bargh 1999
applies again, and the axis leads upward like `ENRG`.

But a lone dancer does not convert two people who firmly do not dance — they sit and watch, which
is a stable outcome, not a level in between. So `MOVE` **splits** (§0a).

| Room | Mean | Reads | |
|---|---|---|---|
| one dancer (88) + two neutrals (45, 50) | 61 | **75** | they don't mind, so they are carried |
| everybody dances (88, 85, 76) | 83 | **86** | |
| one dancer (88) + two firm lows (12, 20) | 40 | **split** | V3 read 28 — a single number was always a fiction here |
| one dancer (88) + one firm low (12) | 50 | **split** | V3 read 37 |

**The split is the better answer than either V3's number or a naive contagion number.** V3's 28
said *this room does not dance*, which is false — one person will. A naive 58 would say *this room
sort of dances*, which is false too. `split` says *one of them will be on the floor and two will
be at the table*, which is what will happen, and it asks the fill stage for a venue that has both.

---

# 4. `FOCUS` — pull 0.80, low discounted to 0.45, leads high. **New, and the strongest pull.**

> **Is there one thing we are all pointed at tonight, or are we the thing?**
> **High:** a gig, a set, a match, a comedy night, a quiz, a screening — one object of attention, at
> the same time, together. **Low:** no main event; the people are the event.

**Finding.** Gaze cueing (Frischen, Bayliss & Tipper 2007): attention follows another person's gaze
*reflexively* — it is one of the least voluntary social behaviours there is. Shteynberg (2010,
2015): knowing that others are attending the same object deepens your own encoding of it. Boothby,
Clark & Bargh 2014: a shared experience is intensified relative to the same experience alone.
Collins' interaction ritual chains makes **mutual focus of attention** the first ingredient of a
ritual that works, and rituals are self-reinforcing once started. **Evidence: strong, and this is
the ingredient nothing in the model previously saw.**

**Asymmetry — the strongest in the table, discount 0.45.** There is a mechanism for focus spreading
and **no mechanism at all for actively un-focusing a room.** Nobody dissolves a gig. The low pole
is the absence of a thing, not a force.

**`pull` 0.80** — above `ENRG`'s 0.75, because the pull is *automatic* rather than affective. You
have to catch someone's mood; you cannot help following their gaze.

| Room | Mean | Reads |
|---|---|---|
| one gig-goer (90) + two neutrals (45, 50) | 62 | **78** |
| one gig-goer (90) + two firm lows (15, 20) | 42 | **65** |
| two gig-goers (90, 82) + two firm lows | 52 | **73** |
| nobody focal (12, 18, 25) | 18 | **13** |

**One person who came for the set takes the room to the set.** Row 2 is the aggressive one and it
is intended: 65 against a mean of 42, with two people firmly uninterested. The defence is that
focus is *joint* — you cannot be at a non-gig while your friend is at the gig — so somebody has to
win, and the literature says it is the one who is already looking.

**`FOCUS` also produces a structural flag, not just a level:** at 70 or above the room **wants a
clock** — one stop anchored to an hour, because the set is at ten. Clock-anchored stops are still
unbuilt (`REMINDERS.md`), and `FOCUS` is now the thing that needs them.

**The old test against `FOCUS` is void, and it should be said plainly.** `COLLECTIVE_V1.md` §5
regressed `FOCUS` on the other six axes and got **R² = 0.91**, and recommended holding it. That
test asked: *can the axes we have already pick the same venue?* `FOCUS` no longer picks venues, so
the question it answered is not a question any more. The live question is whether **people vary
independently on it**, and only a card in the deck and a few hundred sheets can answer that. §5's
caveat said exactly this about itself.

---

# 5. `SPONT` — pull 0.55, high discounted to 0.50, **leads LOW**. New, and the only downward axis.

> **Decide at nine, or planned on Tuesday?**

**Finding, and it is structural rather than psychological: a commitment is asymmetric.** One
person's booking binds everyone — the table exists at nine, and the group goes. One person's
openness binds nobody. Cialdini's commitment-and-consistency principle and the escalation
literature support the stickiness of an existing commitment; the asymmetry itself is a fact about
plans, not about people. **Direction: structural, near-certain. Magnitude: mine.**

This makes `SPONT` **the only axis in the model where the low pole leads.** Everything else leads
high.

| Room | Mean | Reads | |
|---|---|---|---|
| one planner (12) + two neutrals (50, 55) | 39 | **28** | the booking exists, so the room is settled |
| one planner (12) + two firm spontaneous (85, 90) | 62 | **47** | one planner beats two — the booking still exists |
| one spontaneous (90) + two neutrals (45, 50) | 62 | **71** | |
| everyone spontaneous (85, 88, 92) | 88 | **90** | |

**What it is for, and this is a product output rather than a planning one: the room's join
window.** A room reading `SPONT` ≤ 30 is *closed to late joins* — it wants to be settled, and Find
Rooms should stop surfacing it as the hour approaches. A room reading ≥ 70 is *open right up to the
hour*, and is exactly what someone opening the app at nine on a Friday should be shown. Nothing in
the app currently knows which rooms are still live to a late joiner; this is the number that knows.

**`SPONT` is the weakest-carded factor in the set** and that belongs in this document, not only in
the names one. Every other factor is a **scene** you can photograph. `SPONT` is a **process**, and
"I decide at nine" has no image. It is also the one factor that can be measured exactly —
*how long before the night does this person lock a plan* — so it should be carded, watched against
the observation, and dropped if the card does not correlate.

---

# 6. `AFFIL` — pull 0.00. It does not spread; it splits. **Unchanged.**

The interpersonal circumplex (Wiggins 1979; Kiesler 1983; Horowitz et al. 2006): affiliation is
*similar*, not complementary — high-communion people pull each other closer, low-communion people
pull outward, and the two never settle into a shared position the way dominance does. There is no
literature on one room-facing person opening a closed group. **Evidence: strong for non-averaging,
absent for contagion — so the rule is that there is no contagion.**

Firm poles on both sides → `split`. Under V3 that split was read as a venue demand (*Table and
Floor*). Under V4 it is an identity statement: **this room is two rooms socially, and a joiner
joins one of them.**

**Simmel survives:** a pair reads `AFFIL` high whatever the scores — a dyad is its own table.

---

# 7. The cross-axis rules

V3 had five. Three died with their axes. `FOCUS` restores the coupling, which is what it was
expected to do.

| Rule | Finding | Evidence | Fate |
|---|---|---|---|
| room `MOVE` ≥ 65 → `ENRG` **+5** | synchrony raises arousal (Wiltermuth & Heath) | strong | **survives** (suppressed when `MOVE` splits) |
| room `FOCUS` ≥ 70 → `ENRG` **+5** | shared attention amplifies affect (Shteynberg; Boothby) | strong | **new** |
| room `ENRG` ≥ 75 → `MOVE` **+5, capped 60** | arousal produces movement | strong | **survives, new reason for the cap** |
| a pair reads `AFFIL` high | a dyad is its own table (Simmel) | moderate | survives, still unimplemented |
| ~~`AFFIL` ≥ 70 → `CROWD` +8~~ | | | **dead** — `CROWD` is the skeleton's |
| ~~firm split → `GAMES` +10~~ | | | **dead** — `GAMES` is a preference |
| ~~firm `TALK` high → type floor 40~~ | | | **retired** (§2) |

**The cap at 60 has a new and better justification: a derived value must never win the name.** V3
capped the `ENRG`→`MOVE` lift at 60 so the plan never contained a dance floor nobody asked for —
a venue argument, and there is no venue here. The reason it stays is that `VIBE_NAMES_V5.md` names
a room from its two most extreme factors, and a factor that got where it is by arithmetic rather
than by anybody swiping should not be allowed to become who the room *is*. **This generalises: any
future cross-axis rule is capped below 70 and above 30.**

**The rule that deliberately does not exist:** high `ENRG` → high `FOCUS`. A loud club is `ENRG` 90
and `FOCUS` 30 — nobody in it is attending to the same thing. Intensity and shared attention are
independent, and the absence of this rule is what keeps them so.

---

# 8. The three outputs

### 8.1 The identity vector

Six numbers, two of which may be `split`. It drives the room's name (`VIBE_NAMES_V5.md`, read on
the room instead of the person), its blend style and its colour.

### 8.2 `match` — the *People* setting of the Join filter

```python
match(user, room) = 1 − weighted_mean(|user[f] − room[f]|) / 100      # weights: the factor weights
```

**On a split axis the user is matched against the nearer half, not against an average.** The room
genuinely contains both poles and the joiner will join one of them; a table person matched against
an AFFIL-split room should score as well as they would against that room's table half. Averaging a
split would penalise exactly the person the split exists to accommodate.

**The weights now have exactly one job.** `ENRG` 18, `AFFIL` 16, `TALK` 14, `FOCUS` 14, `MOVE` 12,
`SPONT` 10. The naming tie-break was retired on 2026-09-23 and nothing selects venue types any
more, so these numbers weight the match score and nothing else. They sum to 84, and the sum does
not matter.

### 8.3 `disturbance` — the point-6 question

```python
disturbance(user, room) = weighted_mean(|after[f] − before[f]|) / 100
    an axis already split contributes 0      # saturated: nothing left to move
    an axis this person newly splits costs SPLIT_COST = 35     # the room loses a position entirely
```

**It must be normalised by room size before it is used as a sort key.** Raw mean disturbance across
4,000 synthetic rooms:

| room size | 2 | 3 | 4 | 5 |
|---|---|---|---|---|
| mean disturbance a joiner causes | **0.113** | 0.073 | 0.060 | **0.050** |

A pair is transformed by a third person; a five absorbs a sixth. That is §0.1 one level up. An
un-normalised *least-disturbed* sort would therefore just surface **the biggest rooms in the
city**, which is a plausible-looking bug that would be very hard to spot in the app.

### 8.4 The structural flags

Not levels — consequences, carried on the room:

- `FOCUS` ≥ 70 → **wants a clock**: one stop anchored to an hour
- `SPONT` ≤ 30 → **closed to late joins**
- `SPONT` ≥ 70 → **open to joins right up to the hour**
- `AFFIL` split → **two social halves; a joiner joins one of them**
- `MOVE` split → **needs a floor and somewhere to sit**

---

# 9. Point 6, tested — and I overstated it

> **Every figure in this section was re-measured on 2026-10-07 after §0.0a.** The directions and the argument are unchanged; the magnitudes moved a little, and **the headline finding survived**: the two sorts are correlated and are not the same sort. The share of best-matched rooms that are also least-disturbed fell from 40% to **34%**, which strengthens rather than weakens the point.

The claim was that *rooms whose chemistry barely changes when I join* and *rooms whose identity is
closest to mine* are nearly the same sort. **They are correlated, but they are not the same sort,
and the gap is big enough to matter.** 4,000 synthetic rooms of 2–5 people:

| | |
|---|---|
| correlation of `match` against `disturbance`, pooled | **r = −0.527** |
| same, after size normalisation | **r = −0.534** |
| within rooms of 3 | r = −0.587 |
| **of the 400 best-matched rooms, how many are in the 400 least-disturbed** | **134 (34%)** |
| same, size-normalised | **150 (38%)** |

The sign is right — a better match does disturb less. But **fewer than half the top rooms are
shared**, so the two sorts hand the user materially different lists.

**Why they come apart:** `disturbance` depends on the room's *structure*, not on the joiner's
similarity. A room of six neutrals is moved by anybody, however well matched. A room already firm
on both poles of an axis is saturated and cannot be moved, however badly matched. So the two
numbers answer genuinely different questions, and **point 6 is worth surfacing on its own** rather
than as a restatement of the *People* sort — for instance as a line on the join card: *"you would
barely change this room"*.

**And the volatility guess in §0a's predecessor was wrong.** I expected `AFFIL`-split rooms to be
the most volatile. They are the **least**:

| | mean disturbance a joiner causes |
|---|---|
| rooms with an `AFFIL` split | **0.047** |
| rooms without | **0.078** |

A split room is already at both extremes, so one more person cannot move it. The flag's wording in
§8.4 reflects the measurement rather than the guess: a joiner does not change a split room, they
join one half of it. Split rooms are still the likeliest to be a *bad night* — but that is a
different property from volatility, and conflating the two was the error.

---

# 10. What is evidenced and what is mine

| Rule | Direction | Magnitude |
|---|---|---|
| sublinear influence | **evidenced** (Latané) | 0.6 is mine (his data suggest 0.5–0.7) |
| firmness = consistency | **evidenced** (Moscovici) | the ladder is mine |
| `ENRG` contagion upward | **evidenced** (Barsade, direct experiment) | mine |
| `TALK` recruitment upward | **evidenced** (Thorne; turn-taking) | mine |
| retiring the talk floor | **the user's, 2026-09-30** — the floor guarded against inference, and inference is gone | — |
| `MOVE` upward again | **follows from the split** — mimicry answers "will they dance", not "book a club" | mine |
| `MOVE` and `AFFIL` split; the others are joint | **mine** — but it is a definition, not a claim, and it is checkable | — |
| `FOCUS` pull highest | **evidenced** (gaze cueing is reflexive; Shteynberg; Collins) | 0.80 is mine |
| `FOCUS` asymmetry strongest | **evidenced by absence** — no mechanism un-focuses a room | 0.45 is mine |
| `SPONT` leads low | **structural** — a commitment binds, an openness does not | 0.55 is mine |
| `AFFIL` non-averaging | **evidenced** (circumplex) | — |
| `FOCUS` → `ENRG` +5 | **evidenced** (Shteynberg; Boothby) | +5 is mine |
| the mid band advocates | **the user, 2026-10-07** — a value says how much you want a thing, and is never an absence | **`MID_W` 0.30 is mine**, and it is now the third unevidenced constant alongside `FOCUS` 0.80 and `SPLIT_COST` 35 |
| `SPONT` → the join window | **mine**, and it is a product rule dressed as a finding | mine |
| size-normalising `disturbance` | **measured** (§8.3) | the divisors need real data |

**None of it has been measured on a night out in Delhi.** Every study cited is on groups, arousal,
attention or conversation in general — mostly in labs. The transfer is the assumption. The first
few hundred real rooms replace every number in the right-hand column, and any direction that turns
out backwards.

**Two numbers to distrust first:** `FOCUS` pull 0.80, which is the most aggressive claim in the
document and rests on gaze-following generalised a very long way; and `SPLIT_COST` 35, which was
picked so that a newly split axis outweighs a large ordinary move and has no other justification.

---

# 11. What moved where

| V3 had | now |
|---|---|
| `CROWD` §5, `ROAM` §7, `RAMP` | the **skeleton** — the user drags them (`OUTING_PLAN_ENGINE.md` §15) |
| `GAMES` §4 and the Sherif bridging rule | a **preference**; the badge is in `VIBE_NAMES_V5.md` §6 |
| `ROAM`'s split-the-difference clamp | **not dead — moved.** It belongs to the skeleton merge, where a divisible quantity still has to be split rather than won |
| the talk floor | **retired** (§2) |
| §0a atmosphere vs venue-defining | **retired**, replaced by splits vs joint (§0a) |
| the room level as a venue demand | the room level as an **identity**, read by `match`, `disturbance` and the name |
| `OUTING_PLAN_ENGINE.md` §14.3 reading these as plan inputs | **severed.** §15 plans from the skeleton; §13.6.3's `fit` and `disturbance` read this document |

V2's tags and chip precedence stand where they do not reference a retired axis.

# Chemistry V3 — the interplay rules: what these people do to the room, axis by axis

**Status: design, 2026-09-22 (corrected twice the same day — `GAMES` and `MOVE` are venue-defining, §0a). Prototyped (`interplay.py`), supersedes `CHEMISTRY_V2.md` §0–§8 on
how a room's level is reached; V2's tags, floors and cross-axis venue effects stand.**

V2 answered *what the room is like* with ad-hoc rules per situation. This document answers the
question the user actually asked: **when these people are in a room together, what does the
psychology say happens to each axis?** One rule per axis, each with its finding, its direction,
its asymmetry, and a magnitude. The *directions* below are evidenced; the *numbers* are set by
judgement and marked as such.

---

# 0a. Two kinds of axis — the distinction the two corrections revealed

**Added 2026-09-22, after `GAMES` and then `MOVE` were corrected.** The seven axes do not all
behave the same way, and the difference is not psychological — it is about **what a venue is**.

| | **Atmosphere axes** — `ENRG` `TALK` `CROWD` | **Venue-defining axes** — `GAMES` `MOVE` |
|---|---|---|
| what the axis is | a quality a place has *more or less of* | a **kind of place**: a games bar, a club |
| what a **neutral** (31–69) is | a bystander — movable, weight 0.25 | **the same** — a bystander, movable, weight 0.25 |
| what a **firm low** (≤ 30) is | discounted (0.55 `ENRG`, 0.50 `TALK`) — a calm person does not quiet a lively room | **full weight, no discount** — "I don't want a games bar" is a real position and it holds |
| a tie between the poles | goes to the leading impact | goes to the **low** pole — you do not commit a night to a kind of place on a tie |
| the contagion literature | applies — it is about people in a room affecting each other | applies *inside* a venue, not to *choosing* one: mimicry makes people dance once there is a floor; it does not put a floor in the plan |

**The distinction is about the low pole, not about neutrals** (corrected 2026-09-22 — the user).
*Doesn't mind* and *doesn't want* are not the same thing. A room of neutrals is movable on any
axis: one person at `MOVE` 88 with two others in the forties and fifties gives a room that reads
**75**, and they go somewhere with a floor. What a lone enthusiast cannot beat is a *firm* low:
the same 88 against two people at 12 and 20 reads **28**, and they do not.

`AFFIL` and `ROAM` are neither: `AFFIL` does not average at all (§6) and `ROAM` is structural —
it sets how many stops there are (§7).

**Why the distinction matters more than either correction.** A lone enthusiast on an atmosphere
axis lifts the room, because the others are simply carried along by a livelier or chattier place.
A lone enthusiast on a venue-defining axis cannot, because there is no "slightly a games bar" —
the room either goes to one or does not, and one person's want is not enough to commit three
others to a kind of night. The mistake in both cases was the same: applying a finding about
*people influencing people* to a decision about *what sort of place to be in*.

---

# 0. The two general mechanisms — they apply to every axis

### 0.1 Influence grows sublinearly — the first person on a pole matters most

**Finding.** Social impact theory (Latané 1981): the impact of a source grows as a power function
of the number of sources with an exponent below one — the second person adds less than the first,
the fifth much less than the second. Replicated across conformity, persuasion and audience
effects. **Evidence: strong.**

```python
IMPACT_EXP = 0.6
impact(pole) = (sum of strengths on that pole) ** 0.6
```

Two 88s are not twice one 88; they are 1.5 times. This is why one firm person can move a room at
all, and why a fourth person on the same side changes little.

### 0.2 Firmness is consistency, and consistency is what converts

**Finding.** Minority influence (Moscovici 1969, 1980): a numerical minority shifts a majority
when it is *consistent*; inconsistency destroys the effect. Conversion (real, private change) is
the minority's route; compliance is the majority's. **Evidence: strong.**

So a member's **strength** on a pole is their consistency, not their headcount:

| Score | Strength | Reading |
|---|---|---|
| 0–20 / 80–100 | **1.0** | an extreme — consistent by construction |
| 21–30 / 70–79, swiped fast | **0.75** | near-extreme and answered without hesitation |
| 21–30 / 70–79, normal speed | **0.5** | a lean |
| 31–69 | **0** | no position — these are the people a leader moves |

### 0.3 The shape of every rule

```python
room_level(f) = base + pull(f) × share × (peak − base)
    base  = the plain mean on f — where the room sits with nobody leading
    share = impact(leading pole) / (impact(leading pole) + impact(other pole) + impact(neutrals))
    peak  = the most extreme score on the leading pole
    pull  = the axis's own constant (§1–§7): how far the leader can actually take the room
    neutrals count at 0.25 — they are present but do not advocate
```

---

# 1. `ENRG` — arousal is contagious, and it spreads upward

**Finding.** Barsade 2002, *The Ripple Effect*: a confederate trained to display high-activation
affect raised the whole group's affect, cooperation and perceived performance — a direct
experiment on exactly this. Hatfield, Cacioppo & Rapson 1994 on primitive emotional contagion;
Totterdell on mood linkage in real teams. Group polarisation (Moscovici & Zavalloni 1969) adds
that a group leaning one way moves *further* that way after interaction. **Evidence: strong.**

**Asymmetry.** Contagion of *high* arousal is the documented effect; there is no equivalent
literature on a calm person quieting a lively group — socially, the lively member leaves rather
than converging down. So the low pole's influence is **discounted to 0.55**.

**`pull` 0.75, low-pole discount 0.55.**

| Room | Mean | Room reads | Why |
|---|---|---|---|
| **two 88s, two neutrals (45, 50)** | 67 | **80** | highs' impact 1.52 against 0.38 → share 0.80 |
| one 88, two firm 12s | 37 | **58** | the lows outnumber but are discounted → share 0.55 |
| three at 70+, one firm 12 | 62 | **77** | share 0.73 |
| one 88, one firm 12 | 50 | **68** | the asymmetry, at its starkest |

The first row is the user's case and the number it produces — 80 — is the number the user
expected. V2's rule gave 72; it was too weak because it averaged the neutrals in at full weight
instead of discounting them as non-advocates.

---

# 2. `TALK` — one talker recruits the others into talking

**Finding.** Thorne 1987: in dyads, introverts talking with extraverts behaved like extraverts —
the *partner's* sociability, not the person's trait, predicted their talk. Conversation analysis
(Sacks, Schegloff & Jefferson 1974): a speaker *selects the next speaker*, so one person who
wants conversation structurally pulls others into it. **Evidence: strong, and it is the
mechanism the user guessed.**

**Asymmetry.** Upward, like energy — a talker recruits; a quiet person does not silence a table.
Low-pole discount 0.50.

**`pull` 0.60** — lower than energy, because talk is recruited one turn at a time rather than
caught.

| Room | Mean | Room reads |
|---|---|---|
| **one firm talker (88), two low-talk (20, 20)** | 43 | **58** |
| one noise-wanter (12), two talkers (85, 82) | 60 | **71** |

The user's rough example was 30 → 60. The rule gives 43 → 58 on those inputs: the same
movement, from a base that counts everyone.

**And the separate, absolute rule survives from V2.** Masking is not a level — past a threshold
conversation is impossible, not harder. So the **talk floor** stays: with any firm talker in the
room, no venue type under 40 on talk, whatever the room's level. The level says *how much talk
the room wants*; the floor says *where it can physically happen*.

---

# 3. `MOVE` — venue-defining: a floor is a kind of place, so firm lows hold

**Corrected twice on 2026-09-22 (the user).** First: a lone dancer does not move a room, because
mimicry (Chartrand & Bargh 1999) is real *inside* a venue and is not how a venue gets chosen —
people dance because there is a floor and others are on it; nobody books a club because one
person in four fancies dancing. Then: that does not mean *indifference* blocks it. **A lone
dancer among people who don't mind does move the room; a lone dancer against people who firmly
do not want it does not.**

So `MOVE` is a **venue-defining axis** (§0a): neutrals are bystanders, as everywhere, but a firm
low is **not discounted** — unlike `ENRG`, where a calm person's pull is cut to 0.55. And a tie
goes to the low pole. The "first follower" threshold I had invented is retired: it was reaching
for this rule and getting it only half right.

**`pull` 0.70, no discount on either pole, ties to the low pole.**

| Room | Mean | Room reads | |
|---|---|---|---|
| one dancer (88) + **two neutrals** (45, 50) | 61 | **75** | up — the user's case |
| one dancer + two neutrals (40, 60) | 63 | **76** | up |
| one dancer + **three** neutrals | 60 | **73** | up |
| one dancer + **two firm lows** (12, 20) | 40 | **28** | **down** — the user's case |
| one dancer + **one firm low** (12) | 50 | **37** | down — a tie goes to the sitter |
| two dancers (88, 85) + two firm lows | 51 | **38** | still down: two firm lows beat two enthusiasts, undiscounted |
| everyone a dancer | 85 | **87** | up |

**What survives of the synchrony finding.** A room that is *already* moving lifts its own energy
(+5 `ENRG` at `MOVE` ≥ 65 — Wiltermuth & Heath) and closes on a floor. What does not: a
high-energy room where **nobody** asked for a floor gains at most +5 on `MOVE` and is **capped at
60** — room to stand, never a dance floor nobody asked for. Three people at `ENRG` 80–88 with
`MOVE` in the forties read `MOVE` **53**; the same three with two of them wanting a floor read
**78**.

# 4. `GAMES` — venue-defining, so indifference is a vote against

**The user's correction, 2026-09-22, and it overturns how I first applied Sherif.** Sherif's
superordinate goals are about *hostile groups given a task neither can do alone*. A night out in
Delhi is not that: **an activity is a feature of a venue, not a reason to pick one.** The venue
*type* carries the night. So a lone gamer among people who do not care does **not** recruit them
— the room is pulled *down*, because choosing a games bar means choosing a whole kind of place on
one person's say-so.

**The rule that follows: `GAMES` is a venue-defining axis** (§0a). A neutral is still a
bystander — someone who doesn't mind can be taken to a games bar. What holds is a **firm low**:
on this axis it is *not* discounted the way a calm person's `ENRG` is, because "I don't want a
games bar" is a position about the kind of night, and two of those beat one enthusiast.

```python
GAMES: pull 0.50, no discount on either pole, ties go to the low pole, split_cap 65
    neutrals are bystanders (0.25), as on every axis
    a firm low (<= 30) counts at full strength - no discount
    a tie between the poles goes to the low pole
```

| Room | Mean | Room reads | |
|---|---|---|---|
| one gamer (90) + **two neutrals** (40, 55) | 62 | **72** | up — they don't mind, so they go |
| one gamer + **three** neutrals (38–45) | 53 | **66** | up |
| one gamer + **two firm no-games** (12, 20) | 41 | **32** | **down** — the user's case |
| one gamer + **one firm no-games** (15) | 52 | **43** | down — a tie goes to the low pole |
| everyone a gamer | 88 | **89** | up |

**The line is not headcount — it is whether anyone firmly objects.** Among people who don't mind,
one enthusiast is enough; against one firm refusal, it is not. Where the room does not become a
games night, the lone gamer is still served as V2 says — *games available, not the point*: a
**games pub** (a board-game café, a brewery with a shelf), a talkable venue that happens to have
games rather than a venue whose point is games.

**The bridging rule survives, capped, and never on a games argument.** A room firmly split on any
axis *other than `GAMES` itself* gains **+10 `GAMES`** — adding games does not bridge a room that
is divided about games — a divided group holds together around something to do — but **never above 65**, the
games-pub level. Sherif buys a venue that has games; it does not buy a games bar. Run: a room
split on energy with nobody caring about games reads `GAMES` 58, which puts a games pub in play
at the compromise stop and nothing more.

**Evidence.** Sherif's finding is strong for *bridging*, which is why the capped split bonus
stays. The *recruitment* reading — that a game pulls people in — was my extrapolation and the
user's local knowledge overrides it: in Delhi, activities rank below the vibe of the night and
the kind of venue. **Direction: set by domain knowledge, not by a study. Magnitude: mine.**

**Is any other axis venue-defining?** `MOVE` is the candidate — a dance floor is also a kind of
place — but dancing is part of the *vibe* of a Delhi night in a way board games are not, so it
keeps its upward mimicry rule (§3). Watch it on the first real rooms; if a lone dancer turns out
not to move a room either, `MOVE` takes this same treatment.

# 5. `CROWD` — crowding is an appraisal, not an affect; it barely spreads

**Finding.** Stokols 1972 and Freedman 1975: density becomes *crowding* when it interferes with
what you came to do — the same room is atmosphere or oppression depending on the goal. Crowding
is a stress appraisal, and stress appraisals are not contagious the way affect is. **Evidence:
strong for the appraisal account, and it is why `pull` is low.**

**`pull` 0.25, both directions equally** — this is the one axis where the low pole is *not*
discounted, because a crowding aversion is a stress response that does not yield to enthusiasm.

| Room | Mean | Room reads |
|---|---|---|
| one crowd-lover (90), two haters (20, 25) | 45 | **41** — the haters lead, and barely move it |

**The cross-axis rule — social support buffers crowding.** Evans & Lepore (1993) and Baum &
Valins: social support moderates the stress effects of density — being with your own people makes
a full room tolerable. So when the room's `AFFIL` is 70 or more, `CROWD` gains **+8**. Run: a
crowd-lover with two table people reads `CROWD` 68 (60 from the pull, +8 from the buffer) — a
packed room with a table held, which is *Packed but Ours*.

---

# 6. `AFFIL` — it does not spread; it splits

**Finding.** The interpersonal circumplex (Wiggins 1979; Kiesler 1983; Horowitz et al. 2006):
affiliation is *similar*, not complementary — high-communion people pull each other closer,
low-communion people pull outward, and the two do not settle into a shared position the way
dominance does. There is **no** literature on one room-facing person opening up a closed group,
or one table person closing an open one. **Evidence: strong for non-averaging, absent for
contagion — so the rule is that there is no contagion.**

**`pull` 0.00.** And when both poles are firmly present, the room has **no `AFFIL` level at
all** — the output is `split`, and the shape reads it as *Table and Floor*: types that hold a
table inside an open room (pub, buzzy restaurant, games pub, street). A single number here would
be a fiction; that is what "does not average" means.

---

# 7. `ROAM` — settled groups resist moving, and resistance grows with size

**Finding.** The weakest peg in this document. Behaviour settings (Barker 1968): each arrival
re-forms the group, so moving *is* a real social act rather than a logistical one. Steiner 1972
on process losses, and coordination losses that grow with group size: getting five people out of
a bar is harder than getting two, and not linearly. **Evidence: weak — extrapolated. Nothing has
been measured about venue-hopping.**

**`pull` 0.50 × (2 / group size)** — size-damped, no asymmetry.

| Room | Mean | Room reads |
|---|---|---|
| one roamer (92) in a **pair** | 68 | **78** — one other person is easy to move |
| one roamer (92) in a **five** | 57 | **62** — four people are not |

**And the one thing that is not contagion at all (added 2026-09-23, the user's correction).**
`ROAM` is a **quantity**, not a quality. Where positions exist on **both** poles the level is
**clamped into 40-60** before anything downstream reads it: a split on a divisible good is split
the difference, so three places never becomes one and one never becomes three. Influence still
decides *where in* the band, and the band is what sets the stop durations. Nothing else in this
document is clamped, because nothing else is a count.

| Room | Before the clamp | Reads |
|---|---|---|
| a firm settler (12) and a firm roamer (92) | 60 | **60** — two stops, roamer-led, 45 / 55 |
| two firm settlers (12, 15) and a roamer (92) | 34 | **40** — still two stops; the majority sets the durations, not the count |
| a firm settler (12) and a 75 | 43 | **43** — inside the band already, untouched |

---

# 8. The cross-axis rules, collected

| Rule | Finding | Evidence |
|---|---|---|
| `AFFIL` ≥ 70 → `CROWD` **+8** | social support buffers crowding (Evans & Lepore; Baum & Valins) | strong |
| room `MOVE` ≥ 65 → `ENRG` **+5** | synchrony raises arousal (Wiltermuth & Heath) | strong |
| room `ENRG` ≥ 75 → `MOVE` **+5, capped at 60** | arousal produces movement — but not a floor nobody asked for | strong, capped |
| a firm split on any axis **except `GAMES`** → `GAMES` **+10, capped at 65** | superordinate goals (Sherif) — buys a games pub, never a games bar | strong for bridging |
| any firm `TALK`-high → **type floor 40**, whatever the level | masking is absolute | strong |
| group of 5+ → venues with room to split | conversation groups cap at four (Dunbar) | moderate |
| a pair reads `AFFIL` high whatever the scores | a dyad is its own table (Simmel) | moderate |

---

# 9. What is evidenced and what is mine — the honest column

| Rule | Direction | Magnitude |
|---|---|---|
| `ENRG` contagion upward | **evidenced** (Barsade, direct experiment) | mine |
| sublinear influence | **evidenced** (Latané) | exponent 0.6 is mine (his data suggest 0.5–0.7) |
| firmness = consistency | **evidenced** (Moscovici) | the 1.0 / 0.75 / 0.5 ladder is mine |
| `TALK` recruitment upward | **evidenced** (Thorne; turn-taking) | mine |
| the talk floor as absolute | **evidenced** (masking) | 40 is mine — and it is the number a wrong guess makes a night bad |
| `MOVE`: mimicry is real inside a venue, not in choosing one | **domain knowledge** — the user's | mine |
| `GAMES` bridging a split | **evidenced** (Sherif) | mine; capped at the games-pub level |
| `GAMES` and `MOVE` as venue-defining (a firm low is undiscounted; ties to the low pole; neutrals still movable) | **domain knowledge, not a study** — the user's, 2026-09-22 | mine |
| `CROWD` appraisal, low spread | **evidenced** (Stokols) | mine |
| `AFFIL` non-averaging, no contagion | **evidenced** (circumplex) / absence of evidence | — |
| `ROAM` size-damped | **extrapolated** (Steiner, indirectly) | mine |
| the `AFFIL`→`CROWD` buffer | **evidenced** (Evans & Lepore) | +8 is mine |
| `MOVE`↔`ENRG` | **evidenced** | +5 each is mine |

**None of it has been measured on a night out in Delhi.** Every cited study is on groups,
arousal, conversation or density in general — mostly in labs, some in workplaces, one in a boys'
camp. The transfer is the assumption. The first few hundred real rooms replace every number in
the right-hand column, and any direction that turns out backwards.

---

# 10. What this replaces

`CHEMISTRY_V2.md` §0's strength table stands (it is §0.2 here). V2's per-situation `ENRG` rules —
the spark formula, `MINORITY_PULL`, the drift — are **replaced** by §1's single formula, which
reproduces them and fixes the spark (80, not 72). V2's tags, the talk floor, the venue-side
effects of each axis and the chip precedence stand unchanged. `OUTING_PLAN_ENGINE.md` §14.3 v5
reads these levels as its readings.

# Chemistry V2 — the room's chemistry from the psychology of each axis, and what it does to the night

**Status: built into the engine, 2026-09-19 (`OUTING_PLAN_ENGINE.md` §14.3.8; `design3.py` runs it).** Chemistry so far
was read off *how the design went* (§14.3.4). This document makes it what the user asked for: the
chemistry of a room comes from what the psychology says happens when these seven axes meet in a
group — and it **feeds the plan**, not just the chip. Each axis gets its findings, the situations
that arise, a rule with numbers, what the rule does to the room's vector and the shape of the
night, and the tag the room wears.

Two ideas run through all of it:

1. **Some axes are asymmetric.** Energy is the clearest: a calm person can live with a big night;
   a big-night person cannot live with a calm one. Where the literature says an axis only pulls
   one way, the engine only pulls it that way.
2. **Some axes don't average.** Affiliation is the clearest: table people and room people don't
   meet halfway. Where the literature says two poles don't merge, the room vector is not a mean —
   the night has to carry both.

The room's **base vector** is still abstention over the seven (§13.6.1). The rules below modify it
into the **chemistry vector** — the one the shape reads for its targets and signals (§14.3.3),
and the one the blend style is named from. Top factors are untouched by any of this: the design
still starts from every member's top, present at every stop (§14.3). Chemistry moves the *room*,
and the room moves which types win the ties.

---

# 0. Numbers — how many people are on each pole, and how firm

**The user's rule, 2026-09-19.** Contagion is a matter of *how many*. Three people at 70+ with one
firm 12 lift the room; one 88 with one or two firm 12s brings it down to a lively middle, 50–60.
Every axis has a version of this. So every rule below reads the **strength** on each pole first:

| A member counts on a pole at | Strength |
|---|---|
| an extreme score — 80+ / 20− | 1.0 |
| the band — 70–79 / 21–30 — swiped fast | 0.75 |
| the band, at normal speed | 0.5 |
| 31–69 | 0 — neutral; they are the people a spark catches |

`S_hi` and `S_lo` are the sums. The **majority** is whichever is larger; a tie is a tie.

| Axis | Majority on the dominant pole | Tie, or the other pole in the majority | The minority is served |
|---|---|---|---|
| **`ENRG`** | the highs set it; the lows get no weight and live with it (to a degree, up to 70) | the room comes down to the lively middle: `mean(lows) + pull × (peak − mean(lows))`, pull **0.6** at a tie or one more low, **0.5** at two more, **0.4** at three or more → 50–60 for a 12 against an 88 | a lone high: to a degree at a games pub / pub; his #2 stands in |
| **`TALK`** | the floor holds whatever the numbers — masking does not average; the room's talk *target* follows the majority within the floor | the same floor; the loudest type above it | noise-wanters in a talkers' room: the liveliest talkable type |
| **`MOVE`** | movers outnumber → the night **ends on a floor** (club, open ground, street) | sitters outnumber → the last stop has room to stand, not a floor | a lone mover: the closing stop is a street or a lawn, not a club |
| **`AFFIL`** | both poles present → *Table and Floor* whatever the count; the **lean** follows the majority — table people in the majority: a buzzy restaurant with a held table; room people in the majority: a street or a pub | | a lone table person in a room of room people: the booth; a lone room person at a table: the pub's bar |
| **`CROWD`** | the majority sets it; a crowd-hater in the minority is weighed by the room's goal (§3) | | a lone crowd-lover: the street carries it (*Packed but Ours*) |
| **`GAMES`** | gamers outnumber → games types | | a gamer or two among non-gamers: a **games pub** — games on the premises, not the point |
| **`ROAM`** | the bend-weighted middle already counts heads: two roamers against one settler → three stops with a long first; two settlers against one roamer → two | | — |

**Run** (`design3.py`): three at 70+ and one firm 12 → room **81**, *Buzz, Not Noise* (the 12 was
a firm talker, so the floor kept it to a games pub and a games bar). One 88 and two firm 12s →
**58**, a games pub and a games bar, the 88's crowd standing in. One 88 and one 12 → **58**. One
88 and three 12s → **52**. Three table people and one room person → a games pub and a games bar,
*Table and Floor* leaning to the table; the reverse → the food street, leaning to the room. One
gamer among three non-gamers → two games pubs, *In Sync* — games available, not the point.

---

# 1. `ENRG` — arousal is contagious, and it only spreads upward

**Findings.** Emotional and arousal contagion in groups (Barsade 2002; Hatfield, Cacioppo &
Rapson 1994): a few high-arousal members raise the group's arousal, and the effect is strongest
when the rest are unopinionated. Groups converge on energy; they rarely converge *down* — a calm
member in a lively group rises to it; a lively member in a calm group leaves. **Asymmetry:** a
low-energy person can live with a high-energy night; a high-energy person cannot live with a
low-energy one.

**Situations and rules.**

| Situation | Rule | Room `ENRG` | Tag |
|---|---|---|---|
| **1–2 members high (≥ 80), everyone else near neutral (35–65)** | the room catches: `room = mean(neutrals) + 0.6 × (peak − mean(neutrals))` | 45 and a peak of 88 → **70** | **Caught the Spark** |
| highs **outnumber** lows (by strength, §0) | **the highs set it** — the lows get no weight in the room's `ENRG`; their tops, if `ENRG`-low, have their strong #2s stand in, otherwise they stand and are served *to a degree*, which on this axis reaches up to 70 | 81 for three at 70+ and one 12 | no `ENRG` tag — the stand-ins say *Got Your Back*, or *Buzz, Not Noise* if a talker capped the arc |
| lows **match or outnumber** a high | the room comes down to the **lively middle**: `mean(lows) + pull × (peak − mean(lows))`, pull 0.6 / 0.5 / 0.4 by how many more lows; the high's #2 stands in | 58 for one 88 and one or two 12s; 52 for three 12s | **Slow Burn** |
| everyone at 55–79, nobody firm-high | the room drifts up 10 | 62 → 72 | **Could Go Late** (as now) |
| everyone ≥ 80 | abstention as is | | **Running Hot** |
| everyone ≤ 30 | abstention as is | | **Slow Burn** |
| a firm-low member among firm-highs | **the low does not pull.** Their `ENRG`-low is not read as opposing anyone's high (asymmetry); if `ENRG`-low is their top, their strong #2 stands in; if they have none, it stands and is served *to a degree* | the highs' | *Got Your Back* if a #2 stood in |
| a firm-high member among firm-lows | as the row above — the same rule from the other side | | — |

**What it does to the shape.** The chemistry vector's `ENRG` is the arc's end point; *Caught the
Spark* rooms end at a pub, a games bar or a club rather than a buzzy restaurant. In
`effective_top` (§14.3.1), "firmly opposed" on `ENRG` is read **one way only**: a firm high opposes
a low top; a firm low never opposes a high one. And **"to a degree" is generous for the tolerant
pole**: an `ENRG`-low top counts as present, to a degree, at any type up to 70 on energy
(`TOLERATE_TO`) — that is what "can live with it" means in the plan. The same three rules (one-way
opposition, one-way abstention, the tolerant degree) apply to `TALK` and `MOVE`, whose dominant
pole is high.

**Name.** *Caught the Spark* rather than "the energy absorber": the room did not absorb the
energy, it caught it — the finding is contagion.

---

# 2. `AFFIL` — affiliation is similar, not complementary; it does not average

**Findings.** On the interpersonal circumplex (Horowitz et al. 2006; Kiesler 1983) the affiliation
axis is *similar*: people who want their own table pull each other closer; people who want the
room pull each other outward. Unlike dominance, it is not complementary — a table person and a
room person do not settle into a stable pair; they want different rooms. **Symmetric, and
non-averaging.**

| Situation | Rule | Room `AFFIL` | Tag |
|---|---|---|---|
| everyone high | abstention | | **Our Table** — and the room is *not suggested to strangers*: the join list skips it unless the host opts in (§5) |
| everyone low | abstention | | **Meet the Room** — the room is suggested to strangers first; the host's request list is sorted for reinforcement |
| **a firm high and a firm low in one room** | **no mean.** The chemistry vector carries *both* — the shape reads it as "a table in a room": types that support a held table *inside* a full, open space (pub, buzzy restaurant, games pub, street/market) get first claim; a club and a table-for-the-night both lose | both poles flagged | **Table and Floor** |
| the room is public and mostly strangers (friend score 0 between most pairs) | treat as low-`AFFIL` for the first stop whatever the scores: strangers need a setting that faces outward before it faces inward | first stop leans open | **Meet the Room**, first stop |

**What it does to the shape.** *Table and Floor* is a type preference at every stop; *Our Table*
is a gate on the join list (§5).

---

# 3. `CROWD` — crowding is density that blocks a goal

**Findings.** Stokols 1972, Freedman 1975: the same density is felt as crowding or as atmosphere
depending on whether it interferes with what you came to do. A packed room blocks conversation;
it does not block dancing. **Context-dependent, not a fixed aversion.**

| Situation | Rule | Effect | Tag |
|---|---|---|---|
| a firm `CROWD`-low member, and the room's chemistry vector is `TALK`-high or `GAMES`-high | their low counts in full — crowd blocks the goal | the room's `CROWD` target is theirs | — |
| a firm `CROWD`-low member, and the room's vector is `ENRG`-high or `MOVE`-high | their low counts at **half** — crowd is the atmosphere, not an obstacle | the room's `CROWD` sits between | — |
| a firm `CROWD`-high member with `AFFIL`-high members | the **street** can carry the crowd (§13.7): a held table on a packed lane serves both — wired into the designed night as a 0.5 for the crowd-wanter at a table type on a high-`CROWD` area | | **Packed but Ours** |

**What it does to the shape.** Two things the v4 design did not do: the area fallback is wired in
for `CROWD` (and `ENRG`), and a crowd aversion is weighed by what the room is for.

---

# 4. `TALK` — noise defeats conversation absolutely; conversation is a goal

**Findings.** Masking (the cocktail-party effect; Sundstrom on ambient noise): past a threshold,
conversation is not harder, it is impossible. A person who came to talk cannot be served *to a
degree* by a loud room. **Asymmetric the other way from energy:** a noise-wanter can live with a
quiet room; a talker cannot live with a loud one.

| Situation | Rule | Effect | Tag |
|---|---|---|---|
| any firm `TALK`-high member | the room's `TALK` **floor** is theirs: no type under 40 on talk, at any stop, whatever the energy | caps the arc's end: a *Caught the Spark* room with a firm talker ends at a pub or a games pub, not a club | **Buzz, Not Noise** |
| a firm `TALK`-low member among talkers | the low does not pull (asymmetry); their #2 stands in if strong, else their want is served to a degree by a lively-but-talkable type | | *Got Your Back* |
| `TALK`-high and `ENRG`-high both firm in the room | the resolution is the lively middle — buzzy restaurant, pub, games pub, street/market — never the quiet table and never the club | | **Buzz, Not Noise** |

**What it does to the shape.** The talk floor is a hard constraint on types, the only one in the
designed night besides "a top is never absent". In `effective_top`, "firmly opposed" on `TALK`
reads one way: a firm high opposes a low top; a firm low never opposes a high one.

---

# 5. `GAMES` — a shared task bridges a split group

**Findings.** Sherif's superordinate goals (1961): groups that would otherwise split cooperate
when given a task neither can do alone; flow (Csikszentmihalyi) — a task absorbs the attention
that friction would otherwise take. **A games stop is glue.**

| Situation | Rule | Effect | Tag |
|---|---|---|---|
| the design has to meet people in the middle — *Best of Both* — or a #2 has stood in — *Got Your Back* | a games-carrying type gets **first claim on the shared stop** (the one where the most members are only "to a degree"), ahead of coverage and closeness | the compromise stop becomes a games pub or a games bar where the shape allows it | **Common Ground** |
| a public room of strangers (§2, last row) | the **first** stop favours a games-carrying type | an ice-breaker before the night proper | **Common Ground** |
| everyone `GAMES`-high | abstention | | *In Sync* |

**What it does to the shape.** A tie-break above coverage and closeness, but below the top
factors — it changes *which* type carries a compromise, never whether someone's top is present.

---

# 6. `MOVE` — moving together bonds; sitting together deepens

**Findings.** Interpersonal synchrony (Wiltermuth & Heath 2009; McNeill's "muscular bonding"):
moving in time with others raises affiliation and cooperation; it also raises arousal. Seated
groups deepen the conversation they already have. **Asymmetric like energy:** a sitter can live
with a floor stop; a mover cannot live with a whole night seated.

| Situation | Rule | Effect | Tag |
|---|---|---|---|
| a firm `MOVE`-high member and the room is `AFFIL`-low or mostly strangers | a floor stop **late in the arc** is favoured — it bonds a room that started as strangers | the last stop leans club / open ground / street | **On Our Feet** |
| a firm `MOVE`-low member among movers | the low does not pull; #2 stands in if strong, else served to a degree (a place with somewhere to sit *and* a floor) | | *Got Your Back* |
| `MOVE` rides `ENRG` | a *Caught the Spark* room with any `MOVE` want ends on a floor | | — |

---

# 7. `ROAM` — settings reset a group; restlessness grows with time in one place

**Findings.** Behaviour settings (Barker): each arrival re-forms the group and re-opens who talks
to whom; staying put deepens the one conversation. Restlessness in the roamers rises with time at
a stop; the cost of moving is felt by the settlers at the moment of leaving.

| Situation | Rule | Effect | Tag |
|---|---|---|---|
| a firm `ROAM`-high and a firm `ROAM`-low in one room | one number, weighted by bend (as now) — **and the stops are timed**: the first stop is long (the settlers' — they get their one place for most of the night), the later ones short (the roamers' — a move, a second door). Durations from the plan's hours: first stop 55 %, the rest split the remainder | | **Settle Then Roam** |
| everyone `ROAM`-high | three stops, evenly timed | | *In Sync* |
| everyone `ROAM`-low | one place; the fill picks a venue that can hold a group for hours (a table type) | | **The Long Table** (a style name already; as a chip, *In Sync*) |

**What it does to the shape.** A new output — **stop durations** — read off the `ROAM` split.
The plan card shows them: *"Depot 48, 8 to 11 · then the games pub."*

---

# 8. Group size — a finding that cuts across the axes

**Findings.** Conversation groups split above four to five people (Dunbar's conversation-size
work; Simmel on dyads and triads). A room of six cannot hold one conversation; it holds two.

| Situation | Rule |
|---|---|
| a room of **5 or more** with a firm `TALK`-high shape | the fill prefers venues with room to split — long tables, booths, a terrace — over a single small table; `Table and Floor` types score higher |
| a room of **5 or more** with strangers | the games bridge (§5) applies at the first stop regardless of chemistry |
| a room of **2** | `AFFIL` reads as high whatever the scores — a pair is its own table |

---

# 9. The chip — one word per room, and where it comes from

The formation words of §14.3.4 (*In Sync · Got Your Back · Best of Both · Along for the Ride ·
Something for Everyone · Open Night · Could Go Late*) said how the *design* went. One of them
outranks every tag: **Something for Everyone** — somebody's reason to go out is absent at a stop,
and that is always said, whatever else the room is. The tags above
say what the *room is*. One chip. Precedence: **a psychology tag, if one fires; else the
formation word.** Two tags firing → the one from the axis with the higher weight (`ENRG` first).

| Tag | Axis | Fires when |
|---|---|---|
| **Caught the Spark** | `ENRG` | one or two high, the rest neutral; the room lifted |
| **Running Hot** | `ENRG` | everyone high |
| **Slow Burn** | `ENRG` | everyone low, or a lone high among lows |
| **Could Go Late** | `ENRG` | everyone 55–79, nobody demanded it |
| **Our Table** | `AFFIL` | everyone high — and the room is not offered to strangers |
| **Meet the Room** | `AFFIL` | everyone low, or a public room of strangers |
| **Table and Floor** | `AFFIL` | a firm high and a firm low together |
| **Packed but Ours** | `CROWD` × `AFFIL` | a crowd-wanter served by the street at the group's table |
| **Buzz, Not Noise** | `TALK` × `ENRG` | a firm talker in a lively room — the loud types are out |
| **Common Ground** | `GAMES` | the games bridge took a compromise stop, or the first stop of a strangers' room |
| **On Our Feet** | `MOVE` | a floor stop closing a room that started as strangers |
| **Settle Then Roam** | `ROAM` | a settler and a roamer — a long first stop, short later ones |
| *In Sync · Got Your Back · Best of Both · Along for the Ride · Something for Everyone · Open Night* | formation | when no tag fires |

Twelve tags. Fewer is better; the first real rooms will show which fire often enough to keep.
All positive, all things a person could say about their own night.

---

# 10. What feeds what — the map

| Finding | Feeds |
|---|---|
| arousal contagion, upward only | the chemistry vector's `ENRG` (the arc's end); "opposed" one-way on `ENRG`; four tags |
| affiliation is similar, non-averaging | *Table and Floor* type preference; the *Our Table* join gate; strangers' first stop |
| crowding = density blocking a goal | a crowd aversion weighed by what the room is for; the street carrying crowd, wired in |
| masking is absolute | the talk floor on types; "opposed" one-way on `TALK` |
| superordinate goals | the games bridge on compromise stops and strangers' first stops |
| synchrony | the closing floor stop for strangers; "opposed" one-way on `MOVE` |
| behaviour settings, restlessness | stop durations from the `ROAM` split |
| conversation-group size | venue choice at 5+; the pair as its own table |

Every row is an extrapolation from general group research to a Delhi night out. The tags are
written so that a room that fires one and gets it wrong is *mildly* wrong — a games pub instead
of a pub — never badly wrong. The first few hundred rooms replace the extrapolation.

---

# 11. Constants introduced

| | value |
|---|---|
| `SPARK_PULL` — the lift when 1–2 highs (80+) meet neutrals | 0.6 of the gap |
| `MINORITY_PULL` — how far a lone high lifts a room where the lows match or outnumber it | 0.6 at a tie or one more low, 0.5 at two, 0.4 at three or more |
| strength on a pole | extreme 1.0; band-fast 0.75; band 0.5; neutral 0 |
| `TOLERATE_TO` — how far past the middle the tolerant pole is still "to a degree" | 70 |
| `DRIFT_UP` — everyone 55–79 | +10 |
| `TALK_FLOOR` — no type under this on talk when a firm talker is in the room | **40 — decided 2026-09-19.** At 50 the energy people in a talker's room never get a full stop; at a games bar you can still talk to your friends, unlike a club or a live room |
| `CROWD_HALF` — a crowd aversion's weight when the room is for energy or movement | 0.5 |
| `SETTLE_SHARE` — the first stop's share of the night in a *Settle Then Roam* room | 55 % |
| `SPLIT_AT` — the group size above which conversation splits | 5 |
| neutral band for contagion | 35–65 |
| `games pub` type's `ENRG` | 55 — board-game cafés sit at the middle, which is what makes them the bridge between two energy camps |
| tie-break order at a stop | top-factor min → top-factor sum → variety → *Table and Floor* → *Common Ground* → the arc → coverage → closeness to the **chemistry** vector |

All set. All to tune.

---

# 12. Not established

- Every rule. This is the literature applied to a setting it was not written about.
- Whether the tags read as intended, and whether twelve is too many.
- Whether *Our Table* should gate the join list or only nudge the host.
- Whether the `ENRG` asymmetry holds for people at the extreme: a firm 12 who *cannot* do a club
  exists; the rule says they live with it, their #2 standing in. Watch the first complaints.

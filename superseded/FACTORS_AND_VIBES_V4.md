> **Superseded by `FACTORS_V5.md` (2026-09-17).** The ten factors are split into seven vibe factors and six
> preferences; the 42 vibes are retired. Kept for the weights and the reasoning.

# Factors and Vibes V4 — 10 factors, 37 vibes

## The ten factors

| Code | Measures | Penalty | Weight |
|---|---|---|---|
| `CROWD` | how many people you want around you | both ways | 15% |
| `ENRG` | how much movement and intensity | both ways | 12% |
| `SCEN` | how much the look of the place matters | shortfall only | 12% |
| `FOOD` | how much the food itself is the point | shortfall only | 14% |
| `POL` | how dressed-up and polished | both ways | 13% |
| `NOV` | how much you want somewhere new | both ways | 8% |
| `PLAY` | how much you want something to actually do | both ways | 7% |
| `LIVE` | how much a performance is the reason | both ways | 6% |
| `HERIT` | how much you want somewhere old | shortfall only | 5% |
| `AFFIL` | facing the room, or facing your own table | both ways | 8% |

**`SOC` is renamed `CROWD`.** With `AFFIL` in the set, "social" read as though it covered orientation too, and it does not. `CROWD` is headcount; `AFFIL` is which of those people you are there for.

**`AFFIL` is new.** It sits 0.82 inverse-correlated with `CROWD`, but a third of it is independent — and that third is a specific population, not noise: seven vibes that want a busy room while staying focused on their own group (Game-On Friend, Match-Day Regular, Group Hype Friend, Court Regular, Play-and-Plate One, Lawn Lounger, Full-House Feaster). Deriving `AFFIL` from `CROWD` mispredicts every one of them by 19 to 24 points.

**`PLAY` and `LIVE` are participatory, corrected 2026-09-10.** Both were listed here as
shortfall-only, which made an unwanted band or an unwanted pool table cost nothing. They are
things a night does *to* you: a game you did not want still takes the table, and music too loud
to talk over still stops the conversation. Only `SCEN`, `FOOD` and `HERIT` are genuinely free to
overshoot — you can leave a good-looking room or an excellent menu alone. This matches
`OUTING_PLAN_ENGINE.md` §5.3, which always had it right.

Card budget: **20 cards**, two per factor. Nineteen works (one `AFFIL` card, no prior) at a cost of 0.8 points, but loses the pair-disagreement check. Drop to 19 once the `AFFIL` pair is validated. A `CROWD`-derived prior on a single card **makes things worse** — it pulls the exceptions back toward the line they are defined by sitting off.

## The 42 vibes

| Vibe | CROWD | ENRG | SCEN | FOOD | POL | NOV | PLAY | LIVE | HERIT | AFFIL |
|---|---|---|---|---|---|---|---|---|---|---|
| Main-Character Magnet | 95 | 85 | 60 | 35 | 85 | 60 | 40 | 15 | 10 | 15 |
| Dress-Code Devotee | 85 | 70 | 65 | 45 | 95 | 45 | 21 | 20 | 10 | 21 |
| Chaos Collector | 85 | 100 | 20 | 21 | 40 | 85 | 55 | 21 | 5 | 35 |
| Bollywood Extrovert | 90 | 90 | 30 | 35 | 60 | 46 | 55 | 70 | 20 | 30 |
| One Who Knows Everyone | 95 | 65 | 40 | 40 | 60 | 30 | 35 | 20 | 15 | 20 |
| Trend-First Explorer | 85 | 71 | 60 | 45 | 70 | 95 | 40 | 35 | 10 | 21 |
| Warehouse Head | 65 | 90 | 15 | 20 | 20 | 70 | 20 | 95 | 10 | 40 |
| Front-Row Regular | 71 | 80 | 30 | 21 | 45 | 60 | 21 | 95 | 15 | 45 |
| Indie Inner-Circle One | 45 | 40 | 46 | 30 | 45 | 60 | 15 | 85 | 45 | 71 |
| Punchline Regular | 55 | 45 | 30 | 40 | 35 | 55 | 15 | 90 | 15 | 55 |
| Match-Day Regular | 85 | 80 | 21 | 60 | 30 | 20 | 21 | 60 | 10 | 60 |
| Menu-Mood Maker | 45 | 30 | 45 | 95 | 65 | 71 | 15 | 15 | 30 | 65 |
| Curated Night Planner | 60 | 35 | 65 | 90 | 85 | 55 | 10 | 21 | 30 | 60 |
| Quiet Luxury Type | 30 | 20 | 60 | 90 | 90 | 35 | 5 | 15 | 40 | 70 |
| Off-Duty Gourmand | 55 | 45 | 21 | 90 | 20 | 65 | 20 | 20 | 65 | 70 |
| Long-Table Settler | 46 | 30 | 46 | 80 | 60 | 21 | 10 | 20 | 40 | 85 |
| Date-Night Dreamer | 21 | 20 | 95 | 70 | 85 | 45 | 5 | 20 | 30 | 95 |
| Pretty-Place Person | 55 | 35 | 95 | 55 | 65 | 70 | 15 | 15 | 30 | 46 |
| Sundowner Seeker | 71 | 45 | 90 | 46 | 70 | 55 | 20 | 21 | 21 | 45 |
| Sunlit Brunch Friend | 46 | 30 | 85 | 71 | 46 | 40 | 15 | 10 | 20 | 71 |
| Court Regular | 70 | 85 | 35 | 30 | 71 | 35 | 90 | 15 | 5 | 70 |
| Game-On Friend | 70 | 71 | 20 | 30 | 35 | 45 | 95 | 15 | 10 | 71 |
| Trail Wanderer | 45 | 70 | 85 | 21 | 20 | 80 | 70 | 10 | 60 | 71 |
| Lawn Lounger | 65 | 45 | 85 | 55 | 21 | 40 | 40 | 15 | 40 | 70 |
| Deep-Chat Drinker | 35 | 21 | 55 | 46 | 46 | 35 | 10 | 30 | 60 | 90 |
| Low-Key Loyalist | 30 | 20 | 35 | 46 | 21 | 5 | 10 | 10 | 45 | 80 |
| Mystery Mood Seeker | 45 | 65 | 35 | 21 | 45 | 95 | 85 | 45 | 55 | 70 |
| Group Hype Friend | 90 | 80 | 30 | 40 | 45 | 40 | 71 | 21 | 5 | 55 |
| Culture Wanderer | 35 | 35 | 60 | 45 | 40 | 85 | 21 | 21 | 100 | 60 |
| Old-Delhi Wanderer | 55 | 46 | 45 | 85 | 15 | 71 | 35 | 15 | 95 | 65 |
| The Play-and-Plate One | 65 | 71 | 35 | 85 | 45 | 55 | 88 | 30 | 15 | 71 |
| The Monument Wanderer | 45 | 30 | 88 | 45 | 71 | 60 | 20 | 21 | 90 | 65 |
| The Full-House Feaster | 88 | 71 | 40 | 85 | 46 | 46 | 30 | 29 | 35 | 55 |
| The Dressed-Up Front Row | 62 | 55 | 79 | 55 | 82 | 46 | 15 | 85 | 30 | 46 |
| The Big-Night Regular | 80 | 88 | 46 | 40 | 62 | 46 | 30 | 30 | 20 | 35 |
| The Crew-Night Regular | 66 | 82 | 35 | 58 | 55 | 46 | 55 | 21 | 15 | 90 |
| The Whole-Package One | 85 | 79 | 71 | 85 | 58 | 79 | 71 | 21 | 15 | 55 |
| The Table-Sport Crew | 82 | 85 | 30 | 45 | 30 | 56 | 88 | 20 | 18 | 82 |
| The Long-Table Loud One | 85 | 85 | 30 | 70 | 35 | 60 | 40 | 30 | 15 | 82 |
| The Booth Regular | 80 | 70 | 62 | 58 | 80 | 62 | 30 | 35 | 20 | 80 |
| The Closing-Time Crew | 90 | 92 | 30 | 40 | 45 | 70 | 45 | 45 | 12 | 80 |
| The Easy Yes | 55 | 55 | 45 | 55 | 45 | 55 | 45 | 45 | 45 | 55 |

All 42 swipe signatures distinct. Closest vibe pair 78 apart, median 248. Factor pairs with at least one empty corner: 32 of 45 (36 empty corners of 180). Every value sits at least 4 points from the bin cuts at 25 / 50 / 75.


## Addition — The Crew-Night Regular (2026-09-04)

**The big night, but with your own people.** There for the energy and the company; not for how the
place looks, not for a band, not for history. The **Big-Night Regular** is the same energy with
*anyone* — this one is about a specific set of people. `AFFIL` 90 against Big-Night Regular's 35 is
the whole difference.

Added because a real tester matched nothing. On his third card set he sat **120 from The Playful Date
and 121 from The Play-and-Plate One** — a dead tie between two vibes that both fit him badly, which is
the signature of a hole between them rather than a person on a boundary. Against the new vibe he sits
at **71, with the runner-up 49 behind**, so he no longer needs tie-breakers at all.

Nearest existing vibes: Play-and-Plate One 118, Group Hype Friend 126, Court Regular 133. Closer than
the 259 median, but inside the tolerance the blend-style work established (closest accepted pair 107).
Every value sits at least 4 points from the bin cuts.

Flags: `HERIT` tier C, `LIVE` tier C — this vibe is not there for a band or for somewhere old, and
being taken to either is a real cost rather than a neutral one.

## Addition — The Whole-Package One (2026-09-04)

**Wants the night to deliver on every front at once.** Busy, excellent food, something to actually do,
good-looking, and somewhere new — with no interest in a band or in history. Where **The Play-and-Plate
One** pairs food with activity at a modest crowd, and **The Full-House Feaster** pairs food with a big
crowd but scores 30 on activity and 40 on looks, this one refuses to trade any of them away. The Delhi
reference point is the large new multi-format opening rather than a place that does one thing well.

Added from a second real tester, found the same way as the first: a poor nearest fit with a close
runner-up. He sat **132 from The Full-House Feaster with The Play-and-Plate One 11 behind** — off by
+45 on `PLAY`, +35 on `SCEN`, +29 on `NOV` against the nearer of the two. Against the new vibe he sits
at **49, with the runner-up 83 behind**. Both tie-breaker triggers now stay silent for him.

Nearest existing vibes: Play-and-Plate One 142, Full-House Feaster 149, Group Hype Friend 154 —
noticeably better separated than The Crew-Night Regular's 118. Of users already matching a vibe within
90, **0.0%** get reassigned to it, so it fills a hole rather than crowding occupied space. Every value
sits at least 4 points from the bin cuts.

Flags: `HERIT` tier C, `LIVE` tier C — same reasoning as The Crew-Night Regular.

**Note on the distance trigger.** This tester is the argument that `DISTANCE_TRIGGER = 140` may be set
too high: at 132 he was genuinely undescribed by the list and the trigger stayed silent, so he would
have received pair cards separating two vibes when neither was him. Held at 140 rather than tuned on a
single person, but recorded — he and the first tester (71) are the only two real data points, and he
lands in the gap between clearly fine and clearly flagged.


## Addition — four vibes for the busy-room / own-table corner (2026-09-08)

| Vibe | The night |
|---|---|
| **The Table-Sport Crew** | A packed, unfussy room with something to play in it. Pool, darts, a screen, a table. They are there with their own people and the game is the evening; the room being full is the soundtrack, not the point. |
| **The Long-Table Loud One** | The big group dinner that never quietens down. Real food, one long table, everybody staying put. Not a destination restaurant and nobody is dressing for it. |
| **The Booth Regular** | The same instinct in a smart place. A properly done-up room, busy all night, and one booth that the group does not leave. Polish matters here; activity does not. |
| **The Closing-Time Crew** | Maximum room, maximum energy, still going when the staff start stacking chairs. Not fussy about food, looks or a band — the night is the crowd and their own circle inside it. |

**Why these four exist.** `CROWD` and `AFFIL` correlate **-0.74** across the original 37 — the library
was authored as though wanting a full room and wanting your own table were a trade-off. The factor
notes say the opposite: a third of `AFFIL` is independent of `CROWD`, and name seven vibes as covering
that population. **They do not.** The best any of the 37 manages on both at once is **70**
(Court Regular, Game-On Friend), and only **2 of 37** clear 70 on both. Three of the five real sheets
collected sit at 75 or above on both. The corner was empty by construction, not by oversight.

**This is not the rejected pattern.** Adding a vibe per uncovered tester was rejected on 2026-09-07.
The distinction is that this fills a **structurally empty region the factor model says should be
populated**, and the four are spread across it rather than placed on a person: the closest any real
tester sits to any of them is **76**, against a portrait threshold of 39.

**Acceptance tests.** Every value at least 4 points from the bin cuts at 25 / 50 / 75. Each new vibe
at least **98** from the nearest existing one and **87** from the nearest other new one, against the
library's own tightest existing pair at 78. All four clear `CROWD` 78 and `AFFIL` 78.

**Effect on the real sheets.** Mean nearest-vibe distance **102 to 91**. Arnav's sixth reading moves
from The Crew-Night Regular at **117** to The Long-Table Loud One at **76**; his fifth from 114 to 103.
The two earlier readings and the author's sheet are unchanged — those three sit elsewhere in the space.

**What is not established.** Only one of the four is supported by real data; the other three fill the
corner's internal structure — the games / food / polish split — on judgement. The reassignment test
used for previous additions could not be run: a bootstrapped population never lands within 90 of any
vibe at all, because per-factor resampling destroys the correlations that make a real person coherent.
That test needs real users, not simulated ones. And Arnav's second-place gap is **12**, so the pair
tie-breaker still fires for him — he now sits between the games vibe and the food vibe, which is a fair
description of someone at `PLAY` 75 and `FOOD` 62 rather than a failure to place him.


## Addition — The Easy Yes (2026-09-08)

| Vibe | CROWD | ENRG | SCEN | FOOD | POL | NOV | PLAY | LIVE | HERIT | AFFIL |
|---|---|---|---|---|---|---|---|---|---|---|
| The Easy Yes | 55 | 55 | 45 | 55 | 45 | 55 | 45 | 45 | 45 | 55 |

**Up for most things, and led by the day rather than by a fixed taste.** Happy in a room with
people in it, happy for the night to go somewhere, happy to try somewhere new — but needing none
of it. Nothing has to look a certain way, nobody has to dress up, there does not have to be a
game or a band or any history in the walls. What they want on a given night is decided by the
day they have had and the people they are with.

**This is not "no personality" and must never be presented as one.** It is the person whose
preferences are **situational rather than stable**, which is a real and common way to be, and it
is the exact population the conditional mood cards exist to serve. A user who lands here should
be told they are led by the day, and then asked how the day has been.

**Why the library needed it.** Every one of the previous 41 vibes is a character with strong
opinions, so **the middle of the space was empty**: the closest vibe to dead centre sat **150**
away and the median vibe **216**. A person with no strong preferences was therefore further from
any vibe than any real tester has ever been — the five real sheets sit at 71 to 121. The library
was a ring with a hole in it, and the hole was exactly where the undecided users are.

**Why 55 / 45 rather than 50.** Every vibe value must sit at least 4 points from the bin cuts at
25 / 50 / 75, and a flat 50 breaks that rule on all ten factors. The 55s are the mildly social
side — being around people, the night going somewhere, somewhere new, the company, decent food.
The 45s are everything that makes a demand: the look of the place, dressing up, an activity, a
performance, history. Five of those 45s sit on shortfall-only factors, so they effectively drop
out of scoring, which is correct — this user's night should be decided by mood, popularity and
who they are with, not by their factor vector.

**Acceptance tests.** Bin-cut rule: pass. Nearest existing vibe **135** (The Full-House Feaster),
against a duplicate floor of 78: pass. Closest real tester **164**, against a portrait threshold
of 39: pass — this is nobody's portrait.

**Absorption.** The risk with a vibe in the middle is that it is close to everything and swallows
users who already had a real match. It does not: it becomes the nearest vibe for **14%** of the
reachable space while taking over from a decent existing match (within 120) only **1%** of the
time, and it moves **none** of the five real sheets. It selects for precisely the intended
population:

| Factors the user has no strong view on | Chance they land on The Easy Yes |
|---|---|
| 0 of 10 | 0% |
| 3 of 10 | 11% |
| 5 of 10 — the mood-card trigger | 36% |
| 7 of 10 | 79% |

**What is not established.** The same limit as the previous four additions: this is a structural
fix, sized against what the library can and cannot express, not against a measured population.
Whether 14% of real Delhi users are actually this way is unknown, and five sheets from two people
cannot answer it.


## How a user's vibe name is produced (2026-09-09)

**The 42 vibes below are no longer the source of the user-facing name.** They remain in use for
**bend flags**, which fire on nearness to a flagged vibe. The name a user sees is generated from
their own scores:

```
high     = their highest-scoring factor            (ties: first in factor order)
refusal  = their lowest-scoring factor, but ONLY if it is at or below 25
           (HATE+HATE scores 12, HATE+NOT FOR ME scores 25)
           if nothing is at or below 25, there is no refusal
name     = "<high>, not <refusal>"     or, with no refusal, just "<high>"
```

**Stickiness.** A name does not change on a retake unless the new reading beats it by **15 points**,
and **the two halves are held separately** — the refusal survives unless that factor has climbed
clearly above 25; the high survives unless another factor beats it by 15. Held as one unit instead,
stability falls from 82% to 69%, because moving between a two-part and a one-part name counts as a
change.

**Why not the plain lowest factor.** Everyone has a lowest; not everyone refuses anything. Two of
eleven real sheets bottom out **above** neutral — one at `PLAY` 54 — and naming that as a refusal
would be false. Those two are also the two whose readings were soft, so **a missing refusal is a
useful signal that the sheet is weak**.

**Why generated rather than matched.** Three of the first four real testers sit **121 to 213** from
any of the 42 vibes, against a median 110 between neighbouring vibes. One of them is `LIVE` 100 and
`HERIT` 90, a corner where **zero of 42 vibes have both above 75**. A generated name cannot have a
hole; a library always will.

| Scheme | Labels | Survives a retake | Share yours in 100 | Two sharing it are |
|---|---|---|---|---|
| Top 1 factor | 10 | 62% | 10.0 | 243 apart |
| Top 2 factors | 45 | 47% | 2.2 | 210 apart |
| Top 3 factors | 120 | 38% | 0.8 | 188 apart |
| **Highest + refusal** | **~100** | **38%** (82% sticky) | **1.1** | **197 apart** |

Roughly 100 names have to be written. The **ten one-word names matter most** — simulation puts 97%
of people in a two-part name but the real sheets say 9 of 11, so if the true rate is nearer 80%,
one person in five lands in a pool of only ten.

Full reasoning and the rejected alternatives are in `DECISIONS.md`, 2026-09-09.

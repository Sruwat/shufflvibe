> **SUPERSEDED 2026-09-30 by `FACTORS_V6.md`** when the factor set split in two. Eight vibe factors became
> **six identity factors** (`ENRG` `AFFIL` `TALK` `FOCUS` `MOVE` `SPONT`); `CROWD`, `ROAM` and
> `RAMP` moved to the **skeleton**; `GAMES` became a **seventh preference**. §4 (venue types) and
> §5 (the shape library) are still live and are not reproduced in V6 — read them here.

# Factors V5 — seven vibe factors, six preferences, venue types, and the shape library

**Supersedes `FACTORS_AND_VIBES_V4.md`** (2026-09-17). The ten factors are split into two kinds
that behave differently everywhere — the cards, the scoring, the name, the room, the plan.
`DECISIONS.md` entries 96–99 have the reasoning; `VIBE_AND_PREFERENCE_V1.md` has the
exploration.

---

# 1. The two kinds

| | Vibe factors | Preferences |
|---|---|---|
| what | the **shape of tonight** | how much a **thing about a place** matters to you |
| how many | 8 | 6 |
| measured | every day — the daily deck | once, at onboarding; edited in the profile |
| scale | two-ended: both poles are wants, the middle is "don't mind" | one-ended: 0 is irrelevant, 100 is the whole point; **no aversion anywhere** |
| hard pass | yes — a firm pole | no — the fourth swipe is "don't care" |
| firmness | \|s − 50\| / 50 | importance / 100 |
| in a group | **untouchable** — every member's, within bend, at every stop | **suppressible** — weighted by who cares; served at each venue as far as availability allows |
| decides | the number of stops, the atmosphere, the crowds, the things to do → the **venue type** at each stop | the **exact venue** of that type |
| name | the daily name (`VIBE_NAMES_V4.md`) | badges on the profile |
| learning layer | the daily state against a baseline | re-checked rarely; updated from venues attended |

---

# 2. The seven vibe factors

| Code | Axis | Low pole (a want) | High pole (a want) | Weight | What it fixes in the shape |
|---|---|---|---|---|---|
| `ENRG` | energy | a calm night | a night that builds and goes late | 18 | the arc — where the night starts, how it climbs |
| `AFFIL` | who you face | the room — meeting people | your own table, your own people | 16 | table or floor; whether public rooms are for you tonight |
| `CROWD` | how full | somewhere near-empty | the fullest room in the city | 14 | how full each stop should be |
| `TALK` | can you hear each other | music you can't talk over | a night you can actually talk | 14 | at a given energy: a buzzy restaurant or a club; seating, acoustics |
| `ROAM` | how many places | one place, all night | keep moving | 14 | the number of stops (capped by duration), how far apart |
| `RAMP` | where the peak sits | start where we're ending | build to it | 10 | the **order** of the stops and where the night peaks |
| `MOVE` | on your feet | sat down all night | somewhere with a floor | 12 | whether a stop needs room to move — a dance floor, a lawn |
| `GAMES` | something to play | nothing to fiddle with | games on the premises | 12 | whether a stop needs games — pool, darts, bowling, an arcade |

**`ROAM` and `RAMP` are structural and select no venue type.** Every other axis is a demand on
*what kind of place*; these two are demands on *the night*: `ROAM` says how many stops, `RAMP`
says in what order and where the peak is. Their weights are used for naming ties and nothing
else, so adding `RAMP` took no weight from any axis that picks a venue.

**`RAMP`, added 2026-09-23.** `ENRG` was doing two jobs: the **level** (chill ↔ hyped, which is
ideal affect — Tsai's LAP and HAP) and the **trajectory** (whether the night builds). The engine
hard-coded the trajectory: `lo = min(val, 45 + (val−45)×(k+1)/n)` ramped **every** night up from
45, and nobody was ever asked. Four nights people actually want, of which the old model could
express two:

| | |
|---|---|
| **hyped, straight there** | pre-drinks at home, arrive at the club at twelve, stay — *could not be expressed* |
| **hyped, building** | dinner → bar → club — the default it imposed on everyone |
| **chill, steady** | one table, one level, all night |
| **chill, lifting** | a quiet dinner then somewhere warm but not loud — *could not be expressed* |

And the peak-end rule (`COLLECTIVE_V1.md` §6.3) makes where the peak sits **the** thing people
remember about a night, so it should not be a constant. `OUTING_PLAN_ENGINE.md` §14.3.2b has the
arithmetic.

Weights sum to 100 across the six type-selecting axes and are **set, to be re-derived from the first real rooms** — `ENRG` and
`AFFIL` lead because they were the two most decisive factors before the split; the four new or
changed ones (`TALK`, `ROAM`, `MOVE`, `GAMES`) start level and earn their place.

**On `GAMES`.** It may behave nearly one-ended — "I want games tonight" is a want; "no games" is
mostly indifference. Treat a *firm* low as a light steer away from games venues and a mild low
as don't-care. `MOVE` is properly two-ended. Watch both on the first users.

**`AFFIL` low is a want.** It was the odd one out on the old scale, where the low end was read as
a refusal. Facing the room — wanting to meet people — is one of the two things public rooms
exist for, and it now has a word (`VIBE_NAMES_V4.md`).

All seven are **participatory**: overshoot and undershoot both cost. The old passive /
participatory split is gone — it was the preferences that were passive.

---

# 3. The six preferences

| Code | The thing | 12 — don't care | 88 — the whole point | Weight | Venue attribute |
|---|---|---|---|---|---|
| `FOOD` | the food | eat anywhere | the kitchen is why we're here | 20 | food score |
| `LIVE` | a performance | fine without one; fine with one | an act is the reason | 18 | live score |
| `POL` | how dressed-up the place is | come as you are | somewhere worth getting ready for — with a **sense**: classy / current / both | 18 | polish score + sense tag |
| `SCEN` | how it looks | don't notice | the room is half of why | 16 | scene score |
| `NOV` | somewhere new | the usual is fine | must be somewhere none of us has been | 14 | has-been-before, per member |
| `HERIT` | somewhere old | don't notice | the place having a past matters | 14 | heritage score |

Weights sum to 100; same status as above. **A low preference is never an aversion.** `LIVE` 12
does not mean they mind live music; it means it is not what the night should be about. This is
the single fact the split exists to encode.

**`POL` sense** stays with `POL`: asked once at onboarding as an image pair (a suits-and-dresses
room, a streetwear room), stored as `classy` / `current` / `both`, a filter on which venues count
as delivering `POL` for that person (`OUTING_PLAN_ENGINE.md` §14).

---

# 4. Venue types — the shape stage's vocabulary

A **venue type** is a template on the vibe axes. Every venue in the database carries exactly one,
assigned from its own scores on the seven axes (nearest template by L1, checked by hand). The
shape stage picks a type per stop; the fill stage picks the venue.

| Type | `ENRG` | `AFFIL` | `CROWD` | `TALK` | `MOVE` | `GAMES` | In Delhi |
|---|---|---|---|---|---|---|---|
| **table for the night** | 25 | 85 | 35 | 90 | 10 | 15 | a restaurant you don't leave; a friend's terrace |
| **quiet bar** | 35 | 75 | 40 | 85 | 15 | 20 | a cocktail bar, a jazz bar, a hotel bar |
| **buzzy restaurant** | 55 | 70 | 70 | 65 | 15 | 10 | Depot 48, a busy diner, a Khan Market room |
| **pub** | 60 | 60 | 70 | 55 | 25 | 45 | a brewery, a sports bar, a Sector 29 room |
| **games bar** | 65 | 65 | 65 | 45 | 40 | 90 | pool, darts, bowling, an arcade bar |
| **games pub** | 55 | 70 | 60 | 60 | 20 | 65 | board games and a table you can talk at — a Bohca, a brewery with a games shelf |
| **live room** | 65 | 50 | 70 | 25 | 45 | 10 | a gig venue, a live-band bar, Piano Man |
| **lounge / rooftop** | 50 | 45 | 60 | 60 | 20 | 10 | a rooftop, a lounge, a terrace bar |
| **club** | 90 | 30 | 90 | 10 | 90 | 5 | a club, a warehouse |
| ~~**street / market**~~ | — | — | — | — | — | — | **RETIRED 2026-10-01 (the user): “we’re sticking to venues.”** Old Delhi food streets, night markets and melas were never in scope — a street is not a room we can promise anything about. The heritage it carried is served instead by heritage-character *venues*: `VENUE_DATABASE_V1.md` §1.4 |
| **open ground** | 50 | 70 | 40 | 75 | 70 | 40 | a lawn, a park, a drive-and-sit; an event field |
| **big loud bar** | 80 | 35 | 85 | 48 | 35 | 20 | **new 2026-09-23** — a taproom, a standing bar, a brewery at eleven: loud, packed, facing the room, and you can still shout a sentence |
| **match bar** | 65 | 55 | 75 | 50 | 20 | 30 | **new 2026-09-23** — a screen everyone is facing: a match, a screening; talk between overs |

`ROAM` is not a venue property — it is the plan's — and `AFFIL` on a type says what the setting
*supports* (a table you can hold, a floor you can work), not who is there.

**How a stop gets a type.** For each stop the shape stage has a target on the seven axes (the
room's vibe vector, moved along the arc). The type is the nearest template that sits inside
every member's bend on every axis; if none does, the compromise machinery runs
(`OUTING_PLAN_ENGINE.md` §14.3). Thirteen types; the venue database will show which are real and
which split.

**Why the two added on 2026-09-23.** Both were found by running rooms through the engine and
looking at what it was forced to answer with, not by listing Delhi venues:

- **`big loud bar`** closes **two** holes at once. There was no loud venue you could still talk in
  — above `ENRG` 65 the only types were club (`TALK` 10), live room (25) and games bar (45) — so a
  room that was loud *and* talkative got sent to a **bowling alley**. And a firm `AFFIL`-low want
  (out to meet the room) could be served by **the club alone** among eleven types, which made a
  meet-the-room person plus any firm talker an **unservable pair**: the talk floor of 40 excludes
  the only type that faces the room. A taproom is both, and it is the ordinary Delhi answer.
- **`match bar`** is simply missing: a sports bar is one of the commonest ways the city goes out
  and the engine could not produce one. It is also the venue that would make a `FOCUS` axis worth
  measuring (`COLLECTIVE_V1.md` §5) — without it, focus is 91% predictable from the axes we have.

**Run after adding them** (`readings.py`): a room at `ENRG` 88 / `TALK` 85 goes from *bowling
alley → arcade bar* to **standing bar → taproom**; the quiet-but-outward room goes from *Piano Man
→ warehouse* to **rooftop lounge → Old Delhi food walk**.

---

# 5. The shape library — sixteen archetypes on the seven axes

What the 42 library vibes were for — an archetype to read bend from, to name a person by, to
substitute from in friend mode — now on the vibe axes alone. Preferences are not in these
vectors; they are badges. Sixteen, authored, to be re-derived from real users.

| Shape | `ENRG` | `AFFIL` | `CROWD` | `TALK` | `ROAM` | `MOVE` | `GAMES` | In a line |
|---|---|---|---|---|---|---|---|---|
| **Night Climber** | 90 | 55 | 75 | 25 | 70 | 70 | 20 | it builds, it goes late, we move |
| **Slow Burner** | 20 | 75 | 30 | 85 | 15 | 10 | 15 | one calm place, all night |
| **Inner Circle** | 50 | 92 | 35 | 80 | 25 | 15 | 30 | our people, one table |
| **Room Worker** | 65 | 12 | 80 | 40 | 55 | 50 | 20 | out to meet people |
| **Crowd Chaser** | 75 | 45 | 92 | 20 | 50 | 55 | 15 | the fullest room in the city |
| **Quiet One** | 30 | 65 | 10 | 85 | 20 | 10 | 20 | somewhere near-empty |
| **Table Talker** | 45 | 70 | 50 | 92 | 20 | 10 | 25 | a night you can actually talk |
| **Noise Seeker** | 80 | 40 | 80 | 8 | 60 | 75 | 10 | music you can't talk over |
| **Nomad** | 65 | 50 | 60 | 45 | 92 | 50 | 30 | keep moving, three places minimum |
| **Settler** | 40 | 75 | 45 | 70 | 8 | 15 | 40 | one place, no next stop |
| **Floor Filler** | 85 | 40 | 80 | 15 | 55 | 92 | 10 | on your feet, somewhere with a floor |
| **Sitter** | 35 | 70 | 40 | 75 | 30 | 8 | 30 | sat down all night, happily |
| **Score Keeper** | 60 | 70 | 55 | 50 | 40 | 35 | 92 | something to play |
| **The Whole Team Out** | 80 | 85 | 70 | 40 | 60 | 60 | 75 | our people, building, something to do at every stop |
| **The Catch-Up** | 30 | 90 | 30 | 90 | 10 | 10 | 20 | one table, hours, nowhere to be |
| **The Send-Off** | 88 | 35 | 85 | 15 | 75 | 80 | 40 | loud, everyone, anything |

Each shape has a **bend profile** — how far a venue can miss it on each axis before it costs —
by the rule in `OUTING_PLAN_ENGINE.md` §5.3, scaled by the person's own firmness. The nearest
shape to a person's daily vibe (L1) is their archetype for the day; their badges say what they
care about in a place.

---

# 6. What is not in this file, and where it went

- **Bend, `FLOOR`, debt, payback, friend mode, chemistry** — `OUTING_PLAN_ENGINE.md` §14, on the
  seven vibe factors.
- **The cards** — `CARD_SET_V10.md`: six preference cards (the thing itself), seven vibe factors
  with an A and a B card each.
- **The names** — `VIBE_NAMES_V4.md`.
- **Blend styles** — `BLEND_STYLE_DATABASE_V3.md`, as group shapes.
- **The 42 V4 vibes** — retired. Their vectors were on the mixed ten-factor scale and do not
  translate; the sixteen shapes above replace them.

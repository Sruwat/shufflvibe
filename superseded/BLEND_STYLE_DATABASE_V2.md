> **Superseded by `BLEND_STYLE_DATABASE_V3.md` (2026-09-17).** Styles are shapes on the seven vibe axes.

# Blend Style Database V2

**Supersedes `BLEND_STYLE_DATABASE.md`**, which is written on a factor set two generations stale
(`SOC / SOFT / CULT / CAS / FUN / PREM / VALUE / CONV`). That file should be deleted.

A **blend style** is the named identity of a room: what it is called, what colour it is painted, and
the factor vector other rooms are matched against. It is what the join screen filters on and what the
room background colour is drawn from (`VIEW_FLOW.md`).

> **Blend style and room chemistry are two labels on one card.** Blend style is the room's
> *identity* — a name and a palette, from the vector. Chemistry is *how the room got there* — who
> is set on what, who is easy, who is owed something — and puts one positive word next to the
> style name: *Big Room, Loud Night · Got Your Back*. Chemistry can also move the vector, by
> paying back a member whose top factor lost out (`OUTING_PLAN_ENGINE.md` §13.6), so the style is
> read from the vector **after** payback. The seven words: In Sync · Got Your Back · Best of Both ·
> Along for the Ride · Something for Everyone · Open Night · Could Go Late. An Open Night room has
> no style yet — it is painted grey until someone firm joins.

For a solo user the blend style is not used — the room takes the user's own vibe colour until a
second person joins, per `VIEW_FLOW.md`.

## 1. Factor codes

| Code | Factor |
|---|---|
| `CROWD` | How busy the place is |
| `ENRG` | Energy and intensity |
| `SCEN` | How much the look of the place matters |
| `FOOD` | How much the food is the point |
| `POL` | How polished and dressed-up |
| `NOV` | Wanting somewhere new |
| `PLAY` | Something to actually do |
| `LIVE` | Live performance |
| `HERIT` | Somewhere old, with a past |
| `AFFIL` | How close-knit the group feels |

## 2. How this list was derived

These styles were **not hand-authored**. Hand-authoring is the failure mode already identified in the
40 bend flags: it produces a list that describes where the author imagines rooms land rather than
where they actually land.

Instead:

1. 30,000 rooms of 2–5 members were generated from the 38 vibes, spanning the full similarity range —
   tight friend groups, friend groups with one outlier, and matched strangers — because **how similar
   real SHUFFL rooms are is not yet known** and the list must be robust either way.
2. Each room's vector was computed with the approved **abstention rule**: weight each member on each
   factor by their firmness, no floor, undefined when all weights fall below 0.05. (Payback — §13.6,
   added 2026-09-17 — was not part of this derivation; re-run the clustering with it once real
   rooms exist, since paid-back vectors sit slightly further from the corners.)
3. Those vectors were clustered with k-medians under L1, matching the metric the engine actually uses.
4. `k = 24` was selected against what the join screen needs (see §5).
5. Each resulting centre was named and given a palette from its own factor signature.

**Consequence:** every style below is a place rooms genuinely concentrate. None sits in empty space.

## 3. The 24 blend styles

Ordered by how often rooms land in them.

| Blend style | CROWD | ENRG | SCEN | FOOD | POL | NOV | PLAY | LIVE | HERIT | AFFIL | Share |
|---|---|---|---|---|---|---|---|---|---|---|---|
| The Whole Team Out | 78 | 82 | 25 | 30 | 41 | 39 | 85 | 19 | 10 | 71 | 7.6% |
| Dressed and Seen | 88 | 77 | 66 | 39 | 84 | 64 | 29 | 20 | 12 | 19 | 6.7% |
| Big Room, Loud Night | 89 | 84 | 35 | 35 | 65 | 39 | 33 | 28 | 16 | 27 | 6.4% |
| Down the Front | 73 | 85 | 22 | 22 | 31 | 68 | 18 | 91 | 12 | 41 | 5.2% |
| The Proper Dinner | 58 | 30 | 65 | 91 | 77 | 65 | 13 | 17 | 27 | 66 | 5.1% |
| Golden Hour | 69 | 41 | 90 | 50 | 72 | 66 | 17 | 17 | 22 | 44 | 5.0% |
| Supper and a Set | 69 | 61 | 76 | 72 | 80 | 45 | 15 | 81 | 27 | 53 | 4.8% |
| The Easy Good One | 71 | 71 | 51 | 38 | 51 | 64 | 38 | 49 | 20 | 63 | 4.8% |
| The Old City Wander | 37 | 29 | 76 | 43 | 60 | 74 | 18 | 19 | 91 | 69 | 4.6% |
| A Nice One Out | 75 | 59 | 57 | 68 | 69 | 42 | 21 | 24 | 18 | 61 | 4.6% |
| Small and Perfect | 24 | 19 | 83 | 80 | 87 | 37 | 9 | 16 | 31 | 86 | 4.5% |
| Purani Dilli Run | 59 | 43 | 33 | 87 | 18 | 70 | 23 | 17 | 74 | 71 | 4.3% |
| The Back Room Gig | 49 | 39 | 37 | 32 | 37 | 62 | 14 | 84 | 30 | 71 | 3.9% |
| The Long Feast | 85 | 75 | 36 | 83 | 42 | 49 | 26 | 23 | 30 | 59 | 3.9% |
| Nothing Fancy | 29 | 19 | 43 | 44 | 27 | 19 | 12 | 18 | 51 | 85 | 3.5% |
| Loud and Unbothered | 84 | 79 | 21 | 62 | 28 | 21 | 19 | 59 | 13 | 66 | 3.0% |
| The Long Table | 45 | 29 | 37 | 80 | 62 | 22 | 12 | 19 | 35 | 84 | 3.0% |
| Out in the Open | 68 | 43 | 83 | 58 | 24 | 37 | 33 | 15 | 34 | 74 | 3.0% |
| Plates and Play | 70 | 75 | 31 | 83 | 42 | 59 | 82 | 25 | 15 | 74 | 3.0% |
| Something to Do Together | 42 | 57 | 80 | 67 | 73 | 63 | 66 | 23 | 23 | 87 | 2.8% |
| Slow and Pretty | 43 | 27 | 85 | 73 | 47 | 38 | 15 | 13 | 21 | 75 | 2.9% |
| Chase the Night | 86 | 93 | 21 | 23 | 38 | 86 | 57 | 20 | 10 | 35 | 2.7% |
| Out of the City | 45 | 73 | 84 | 21 | 20 | 82 | 70 | 12 | 60 | 74 | 2.5% |
| The Wildcard Hunt | 43 | 69 | 32 | 21 | 43 | 93 | 83 | 39 | 56 | 74 | 2.1% |

## 4. Palettes and what each style is

Each palette is a **base** (room background) and a **deep** (text and name treatment on that base).
Hue is derived from the style's own signature — heat from `ENRG`, light from `SCEN`, earth from
`HERIT`, richness from `FOOD`, depth from `POL`, electric from `LIVE`.

| Blend style | Base | Deep | What the night is |
|---|---|---|---|
| The Whole Team Out | `#E4572E` | `#2A1A12` | A busy, physical night — courts, lanes, karaoke rooms |
| Dressed and Seen | `#7A2E8C` | `#170D1A` | Somewhere new, somewhere polished, somewhere people look |
| Big Room, Loud Night | `#B02E5A` | `#1E1016` | The packed floor, strangers included |
| Down the Front | `#5B3FD9` | `#0F0C1F` | The gig is the reason — warehouse, basement, festival floor |
| The Proper Dinner | `#8C5A2B` | `#1C1209` | A table booked in advance and taken seriously |
| Golden Hour | `#E08A3C` | `#231409` | Rooftops, terraces, the light doing the work |
| Supper and a Set | `#9E3A6B` | `#1C0F16` | Dinner where a band is part of the booking |
| The Easy Good One | `#3F7A8C` | `#0D1A1E` | No agenda, no theme, just out and good |
| The Old City Wander | `#A6772E` | `#1F1708` | Stone, courtyards, something older than all of you |
| A Nice One Out | `#C06A4A` | `#22110C` | Comfortable, well-chosen, nothing to prove |
| Small and Perfect | `#6B4A7A` | `#150E19` | Two or three people, low light, nothing rushed |
| Purani Dilli Run | `#B5602A` | `#20120A` | Plastic stools, paper plates, the good stuff |
| The Back Room Gig | `#4C4FA6` | `#0E0F1F` | A small room, a stage, people you came with |
| The Long Feast | `#C94F30` | `#231009` | A big table, too much food, everyone talking at once |
| Nothing Fancy | `#5E6B4A` | `#111408` | The usual place, the usual people, no effort required |
| Loud and Unbothered | `#D1703A` | `#22130A` | Volume over polish — screens, pitchers, shouting |
| The Long Table | `#8A6A3C` | `#1B140A` | One table, several hours, no next stop |
| Out in the Open | `#5E8C4A` | `#101A0C` | Grass, daylight, something to sit on |
| Plates and Play | `#D98A2B` | `#241708` | Games on the table and food worth staying for |
| Something to Do Together | `#B0518C` | `#1E0F1A` | A date that is not just sitting across a table |
| Slow and Pretty | `#D9A05B` | `#241A0C` | Daylight, good plates, nowhere to be |
| Chase the Night | `#E02F4A` | `#210A0F` | Wherever is open, whatever is next, no plan survives |
| Out of the City | `#3F8C6B` | `#0C1A14` | Ridge, trail, water, and a drive back |
| The Wildcard Hunt | `#7A5AC4` | `#150F22` | Nobody has been here before and that is the point |

## 5. Matching rule

Similarity between two vectors is defined as:

```
similarity = max(0, 1 - L1_distance / 500)
```

The 500 denominator treats an average gap of 50 points per factor as total dissimilarity. This scale
was chosen so the front end's existing thresholds mean something concrete rather than compressing
every room into the high nineties.

Against this scale, the join screen's published bands behave as follows across 30,000 rooms:

| Band | Front-end treatment | Share of rooms |
|---|---|---|
| Above 75% | "Strong blend" | **85.8%** |
| 60–75% | "Other rooms" | 14.2% |
| Below 60% | Hidden | **0.0%** |

Nothing is hidden from itself: every room finds a style it genuinely resembles. The hidden band only
comes into play when matching one room *against another*, which is its actual purpose.

## 6. Validation

| Check | Result |
|---|---|
| Average room-to-style similarity | 81.7% |
| Largest style's share | 7.6% — no style dominates |
| Smallest style's share | 2.1% — no dead entries |
| Median separation between styles | 241 |
| Median separation between *vibes*, for reference | 233 |
| Closest pair | Small and Perfect vs Slow and Pretty, 107 apart (79% alike) |

Styles are as distinguishable from one another as vibes are, which is the bar: if a user can tell two
vibes apart, they can tell two blend styles apart.

Every factor is represented at both extremes:

| Factor | Highest | Lowest |
|---|---|---|
| `CROWD` | Big Room, Loud Night (89) | Small and Perfect (24) |
| `ENRG` | Chase the Night (93) | Small and Perfect (19) |
| `SCEN` | Golden Hour (90) | Loud and Unbothered (21) |
| `FOOD` | The Proper Dinner (91) | Out of the City (21) |
| `POL` | Small and Perfect (87) | Purani Dilli Run (18) |
| `NOV` | The Wildcard Hunt (93) | Nothing Fancy (19) |
| `PLAY` | The Whole Team Out (85) | Small and Perfect (9) |
| `LIVE` | Down the Front (91) | Out of the City (12) |
| `HERIT` | The Old City Wander (91) | The Whole Team Out (10) |
| `AFFIL` | Something to Do Together (87) | Dressed and Seen (19) |

### The heritage gap

The vibe list has five uncovered factor pairs, all involving `HERIT`. Blend styles close three of
them, because **a room can be something no single person is**:

| Pair | Covered by |
|---|---|
| `ENRG` + `HERIT` | Out of the City, The Wildcard Hunt |
| `PLAY` + `HERIT` | Out of the City, The Wildcard Hunt |
| `HERIT` + `AFFIL` | The Old City Wander, Purani Dilli Run, Out of the City |
| `CROWD` + `HERIT` | **still uncovered** |
| `LIVE` + `HERIT` | **still uncovered** |

The two remaining — a busy historic place, and a gig in a historic venue — cannot be reached by
blending, because no vibe carries `HERIT` high enough alongside `CROWD` or `LIVE` for any combination
to land there. **These require new vibes, not new blend styles.**

## 7. Open items

1. **Room-similarity distribution is unknown.** The list was built to be robust across the full range
   deliberately, but if the group test shows real rooms are far tighter or looser than assumed, `k`
   and the centres should be re-derived from real data. The method re-runs in minutes.
2. **The 75 / 60 thresholds are inherited from the front-end document**, where they are already marked
   "due to change". They are now at least measurable against a defined scale, but they are not
   calibrated against user satisfaction.
3. **Palettes are authored, not derived.** Hue follows the signature by rule, but the specific values
   are a design choice and should be checked against the app's actual theme.
4. **Names are authored.** They read as nights rather than people, deliberately distinguishing them
   from vibe names, but they have not been tested on users.
5. **Solo rooms are out of scope** — a room with one member uses that member's vibe colour. Blend
   styles begin at two members.

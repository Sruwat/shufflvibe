# Venue database v1 — what gets in, how a venue is stored, and how a drawn stop finds it

**Status: design, 2026-10-01. Prototyped (`simulations/venuedb.py`, `supplygrid.py`, `venuetag.py`,
`admission.py`).** This is the document the engine has been waiting on. Everything above it —
the skeleton, the merge, the four rungs — is built and simulated; none of it does anything without
this.

---

# 0. The one rule that governs everything else

> **The vibe never touches a venue.** The identity factors score **people and rooms**. A venue is
> reached by the **skeleton** (its shape at an hour) and chosen by the **preferences** (what you
> care about in a place). Nothing in this document reads `ENRG`, `AFFIL`, `TALK`, `FOCUS`, `MOVE`
> or `SPONT`.

**Corrected 2026-10-01, the user.** Earlier drafts had the identity factors acting as rung-1
character discriminators — `TALK` as register, `AFFIL` and `MOVE` as layout. That is retired. It
was the last place the vibe was still doing planning work, and it was doing it invisibly.

**What this costs:** register and layout do not disappear, they just stop being driven by the
vibe. Register is **derived from the venue's own curve** (§2) and used to describe the venue, not
to filter it. Layout becomes a character tag like any other.

---

# 1. Admission — who gets into the database at all

**The rule, 2026-10-01, the user: start premium, where premium means *established and reputed*,
not expensive.** The worked example is his:

> Kent's in Defence Colony and Nik Baker's sit at the same price point. Both are established, both
> are reputed. Kent's is **too locally run for us to promise anyone a vibe there**, and the room
> itself is old. Nik Baker's is not.

**So reviews and interaction get a venue *considered*, never *admitted*.** The API finds
candidates; a second filter decides.

### 1.1 The filter

| test | bar | what it protects |
|---|---|---|
| **rating spread** | **SD ≤ 0.85** | **the promise.** This is the one that does the work |
| **operator class** | chain, group, hotel, or professionally-run independent | consistency across staff and across nights |
| **fit-out age** | room last done ≤ 15 years ago | whether a drawn energy can physically be delivered |
| **review volume** | ≥ 200 | honesty about what we actually know |
| **recency drift** | last 6 months no more than 0.35 below lifetime | places that have already slipped |
| **mean rating** | **the 35th percentile WITHIN ITS TYPE** | **corrected 2026-10-04.** An absolute 4.0 floor is a *type* bar, not a quality bar — see below |

### 1.1a The mean floor must be type-relative — found by running real data

**A real pass over twelve Delhi NCR venues (`simulations/realrun.py`) threw out Privee on a 3.6
mean** — one of the best-known clubs in the city, in the Shangri-La, with 1,380 reviews.

**And we already know why, from §7 of the Bohca test: clubs collect door complaints that
restaurants do not.** *"Terrible rules for entry"*, *"attitude at the door"*, *"bouncers"* — we
decided those are evidence about **the door** rather than about quality, and that they should be
routed rather than counted. **But the mean rating has already counted them before we see it.**

| clubs | | bars and live rooms | |
|---|---|---|---|
| Kitty Su | 4.1 | Piano Man | 4.5 |
| Bohca | 4.1 | Hauz Khas Social | 4.3 |
| **Privee** | **3.6** | Summer House | 4.2 |

**A club rates roughly half a point below a bar of the same quality, structurally.** So an absolute
floor excludes the type the app most needs.

> **The fix: the mean floor is the 35th percentile within the venue's own type.** Same rule, same
> strictness, measured against the right comparison — which is exactly what `quality` already does
> (§2, percentile within type and area). **The admission filter should have been using it from the
> start.**

---

### 1.2 Why the spread, and not the stars

Nik Baker's and a Kent's-like place have **the same mean rating and the same price band**. Any
ranking built on stars cannot tell them apart — which is precisely the failure the user named.
What separates them is the **spread**:

| | mean | SD | reads as |
|---|---|---|---|
| Nik Baker's | 4.3 | **0.62** | most nights are the night you were told about |
| Kent's-like | 4.3 | **1.34** | a lot of 5s and a lot of 2s — it depends who is on |

**A high standard deviation is the measurement of "too locally run to ensure anyone any vibe
there".** It is not a judgement about quality; it is reliability, and it comes free from the same
API call that returns the mean.

**For an app that makes a promise about a night rather than a recommendation about a place, this
is the single most load-bearing number available, and nobody ranks venues on it.** One bad stop
sinks a whole night — the peak-end rule means people remember the worst moment and the last one —
so a venue that is a coin flip makes every plan containing it a coin flip.

### 1.3 There is no casualty — the category error, corrected

**An earlier version of this section claimed the admission filter killed `HERIT` and a slice of
`FOOD`. That was wrong (corrected 2026-10-01, the user), and the error is worth naming because it
is easy to repeat: I had *old-feeling* and *unreliable* as one axis. They are two, and they are
independent.**

| | **reliable** | **unreliable** |
|---|---|---|
| **old-feeling** | **Ikk Punjab, a haveli bar, a colonial bungalow** — premium, consistent, old-world by fabric or by design | a gali in Old Delhi — wonderful, and not something we can promise |
| **new-feeling** | Depot 48, a rooftop | a new place run badly |

**The admission filter cuts the horizontal axis. `HERIT` lives on the vertical one.** The top-left
box is large, premium, and exactly where a great deal of the best Indian hospitality sits — so
nothing about serving heritage requires admitting an unreliable room. **`FOOD` likewise: there is a
lot of very good food in premium venues.**

**And `street / market` is retired as a venue type entirely (2026-10-01, the user): "we're sticking
to venues."** It was never in scope, and it was the only thing the admission filter actually
excluded. Removing it is a deletion, not a loss.

### 1.4 How `HERIT` is served — three routes, all premium-compatible

**`HERIT` is character, not a venue type.** It reaches a user three ways, and only the third moves:

| | what it is | where it lives | moves? |
|---|---|---|---|
| **fabric** | the building genuinely is old — a haveli, a colonial bungalow, a listed structure | standing tag `heritage-building`, **85** | no |
| **styled** | a new or renovated room built to feel old. **Ikk Punjab is this** — old-Punjab architecture, modern premium operation | standing tag `heritage-styled`, **65** | no |
| **programme** | a sufi evening, a sitar and tabla set, a qawwali, a ghazal night | an **event** on the venue, at an hour, **+25** | **yes** |

**Programming lives in a separate events table, not on the venue (2026-10-01).** Since `prefs{}`
are fixed, an hour-scoped lift cannot sit on the venue row. Events are their own records —
`(venue, date, from_hour, to_hour, kind)` — read at stage 2 alongside the fixed preferences. **The
venue is static; the calendar moves.** That is cleaner than carrying a function on the row, and it
is the same table the `FOCUS` clock-anchor will read.

So a venue's *effective* `HERIT` is **hour-scoped**, even though its stored `HERIT` is not. Qila reads 85 all week and
**100 on a Thursday at 21:30** because the sufi evening is on; Piano Man reads 15 most of the week
and **40** when the sitar set is. Same rooms, different nights — which is the point of letting
programming carry it. `simulations/herit.py` runs the week.

**Where the tags come from, and they get cheaper down the list:**

- **fabric — lookup-able.** INTACH and ASI listings, state heritage lists, heritage-precinct
  addresses, and the venue's own copy, which almost always states a period when there is one. A
  one-time pass that rarely changes.
- **styled — a human glance.** Nobody can automate *does this room feel old*; anybody can decide it
  from four photos in about five seconds. At 40–60 seed venues that is under an hour, once.
- **programme — a feed.** Venue socials, Insider, BookMyShow, District. The only one needing
  refresh, and the only one genuinely automatable, because event listings are structured by nature.

**`HERIT` is therefore far cheaper to populate than the energy curve** (§5), which needs a
judgement per venue *per hour* and has no source at all. Heritage needs one lookup, one glance and
one feed.

**One dependency it creates:** programme-led `HERIT` needs **clock-anchored stops** — the ghazal
set is at 21:00, not "in the evening". That is the same unbuilt feature `FOCUS` has been blocked on
since 2026-09-30. **One feature, two factors**, which makes it the most load-bearing item on the
open list.

### 1.5 Eviction

Admission is a filter on the way in. **It cannot keep the promise true after the reviews that
admitted a venue have gone stale**, so the database has to shrink as well as grow:

- a venue whose stops are **rated low** at End Plan, repeatedly
- a venue **skipped at lock time** far more often than its type's base rate
- a venue whose **recency drift** crosses the admission floor on a later pass

Eviction is silent and reversible — the venue leaves the supply grid and can re-enter.

---

# 2. The row — a base, and slots that override it

**Rewritten 2026-10-03 (the user): "each venue's factor scores should be hour and day dependent, so
for a particular venue the factor scores will actively get replaced with the factor scores of that
hour range and day in real time."** Prototyped in `simulations/slots.py`.

**This supersedes both the flat `prefs{}` of 2026-10-01 and the `bands[]` of 2026-10-02**, and it
absorbs them: bands were this idea applied to two factors, and the events table was it applied to a
third. **They are one mechanism.**

```python
{
 'name': 'Summer House Cafe', 'area': 'Aurobindo Place', 'km': 5.8, 'quality': 79,

 # what does not move
 'base': {'SCEN': 89, 'HERIT': 22, 'FOOD': 77, 'POL': 63, 'GAMES': 8,
          'ENRG': 55, 'CROWD': 60, 'TALK': 58, 'MOVE': 30, 'FOCUS': 28, 'LIVE': 35},

 # what does. A slot names ONLY the factors it changes and inherits the rest.
 'slots': [
   {'days':'all',     'from':12, 'to':18, 'type':'cafe',
    'ENRG':32, 'CROWD':48, 'TALK':78, 'MOVE':10, 'FOCUS':15, 'LIVE':10},
   {'days':'all',     'from':18, 'to':22, 'type':'lounge / rooftop',
    'ENRG':58, 'CROWD':74, 'TALK':60, 'MOVE':28, 'FOCUS':30, 'LIVE':35},
   {'days':'wed',     'from':20, 'to':24, 'type':'live room',
    'ENRG':66, 'CROWD':82, 'TALK':42, 'MOVE':50, 'FOCUS':88, 'LIVE':95},   # Boxout Wednesday
   {'days':'thu-sat', 'from':22, 'to':26, 'type':'big loud bar',
    'ENRG':82, 'CROWD':88, 'TALK':22, 'MOVE':78, 'FOCUS':22, 'LIVE':12},
 ],
}
```

**Resolution: start from `base`, apply the most specific matching slot.** A single named day beats a
day range beats `all`. Every factor a slot does not name is inherited.

### Why this was forced, and by what

**The user had been to Summer House on a Thursday and a Friday after 23:00 and seen no live act
either time, until it closed at 01:30. The lexicon had scored it `LIVE` 92.**

**The score was not wrong. It was the right answer to the wrong question.** Summer House genuinely
is a live-music venue — that is its reputation and it is accurate. What the text could not say is
**when**, because **Boxout is a Wednesday** and reviewers write about venues while the venue's own
Instagram writes about the schedule.

| resolved | type | `LIVE` | `FOCUS` | `ENRG` |
|---|---|---|---|---|
| **Wednesday 21:00** | live room | **95** | **88** | 66 |
| **Thursday 23:00** | big loud bar | **12** | 22 | 82 |
| **Friday 23:00** | big loud bar | **12** | 22 | 82 |
| Saturday 14:00 | cafe | 10 | 15 | 32 |

**Which is exactly what the user saw, and what a flat number could never have said.**

### What it costs — about ten authored numbers a venue

Summer House carries 11 base numbers and 30 slot numbers. **Roughly double the flat row — and
almost none of it is authored:**

| | |
|---|---|
| **the base** | from the lexicon (§5.8), one pass | **free** |
| **the ordinary slots** | **generated** from the type curve × the venue amplitude (§5.4) | **free** |
| **the exceptions** | authored by hand | **one or two a venue** |

Summer House's only exception is **Boxout Wednesday**. Bohca's are **Sunday brunch** and the
**weekend club mode**. Two or three slots a venue at three numbers each — **call it ten authored
numbers on top of the base, and a 50-venue seed is still an afternoon.**

### What it changes

**`prefs{}` are no longer fixed** — which reverses the 2026-10-01 decision, **but only for the
factors that genuinely move.** `SCEN`, `HERIT` fabric, `FOOD` and `POL` stay in the base; `LIVE`,
`FOCUS`, `GAMES` and `MOVE` move into slots. **That decision was right about most preferences and
wrong about the programmed ones** — Bohca's Sunday board games was the first sign, and Summer
House's Wednesday is the confirmation.

**The events table and the slot table are the same thing.** Heritage programming, the `FOCUS` clock
anchor, Boxout Wednesday and Sunday brunch are one mechanism: a `(days, hours)` window overriding
some factors. **Two tables collapse into one.**

**"Actively replaced in real time" has two readings and both are kept.** The **source of truth** is
`base` + `slots`, resolved at query time — that is what selection reads. A **materialised
"what is this venue right now" view** sits alongside it for the live surfaces: *what's popping
tonight* and the venue screen. Same data, two access patterns.

**The supply grid is built by expanding slots**, which it already was for bands. More factors come
along for the ride and nothing else changes.

### And it sharpens where each source belongs

| source | gives | fills |
|---|---|---|
| **reviews** | what the place is **like** | **the base** |
| **the venue's own posts** | what the place **does, and when** | **the slots** |
| **images** | confirmation where text is thin | the base |
| **the type curve** | the shape of ordinary hours | the generated slots |

**Boxout Wednesday was stated plainly on Summer House's Instagram and appeared in not one review.**
That is the division of labour in a single example.

---

# 2a0. The pre-promotion build — what gets filled now, and what is left empty

**The sequence (the user, 2026-10-03): build the database from reviews, photos and the venue's own
information first; the gold promotion fills the rest later.** So every slot needs a decision —
**fill it, or leave it for a capture.** Prototyped in `simulations/prebuild.py`.

### What counts as evidence for a SLOT

| source | weight | |
|---|---|---|
| **structured** | **3** | a Google field — type, hours, `liveMusic`, `outdoorSeating`, `reservable` |
| **own copy** | **3** | the venue's site, Facebook or Instagram — **and it states the time** |
| **timed review** | **2** | a fragment naming an hour or a day **and** a character |
| untimed review | 1 | the lexicon base. Describes the venue, says nothing about when |
| the type curve | **0** | not evidence — it is what an empty slot falls back **to** |

> **A slot fills at 3.** One structured field or one line of the venue's own copy is enough; two
> agreeing timed reviews are enough. **The lexicon base alone never is**, because it describes a
> venue and a slot is about an hour.

### What that produces on the two venues we have done

| | | | |
|---|---|---|---|
| **Bohca** | all 12–17 | **buzzy restaurant** | structured: type, hours, *"terrace restaurant, sharing plates"* |
| | **sun** 12–17 | **games pub** | their Facebook: *"Hoppi Sunday Brunch… lovely board games"* |
| | all 17–22 | buzzy restaurant | structured |
| | **fri–sun** 22–02 | **club** | two timed reviews + the closing time |
| | **mon–thu 22–02** | — | **GOLD** — nothing in any source says what this is |
| **Summer House** | all 12–18 | **cafe** | structured + *"date spot during the day"* |
| | **wed** 20–24 | **live room** | their Instagram: *"live independent sound, every Wednesday"* |
| | all 18–22 | — | **GOLD** — one timed review, and one is not enough |
| | **thu–sat 22–02** | — | **GOLD** — *"party harder"* names no hour |
| | **sun–tue 22–02** | — | **GOLD** |

**This is exactly the user's example working.** Bohca's *club after ten at the weekend* is
derivable and gets filled; its **weekday** late night is not, and is left empty.

### The finding: the gold list is not a separate decision

**Nobody chooses which venues go gold. The build produces the list by failing to fill a slot.**
Every slot the evidence cannot reach is a slot the promotion targets, and they are the same object
seen from either end.

**And look at which slots they are.** Every daytime slot fills from structured data alone. **Every
late slot but one is gold.**

> **The evidence is thinnest exactly where the venue transforms** — because that is the part nobody
> writes down. A listing states what a place *is*; reviews describe the night people had, which is
> almost always the busy one. **The quiet Tuesday at eleven is unrecorded everywhere.**

**Across 214 venues, expect half to two-thirds of slots fillable before a single capture**, with
the gaps concentrated in the late bands.

**And the three findings line up, which is the reassuring part:** the slots hardest to derive, the
slots the type curve predicts worst, and the slots users query most **are the same slots.** Nothing
has to be traded off.

### Five rules for whoever builds the first 214 rows

1. **The base always gets filled.** Lexicon over the review corpus, the structured fields, images
   where text is thin. Every venue has a base on day one (§5.8).
2. **A slot is filled only when a source names its time.** *"Sunday brunch"*, *"every Wednesday"*,
   *"the weekend go-to"*, *"during the day"*, *"closes at 1am"*. **A glowing review with no hour in
   it improves the base and must not touch a slot.**
3. **Never infer a slot from the type curve and store it.** This is the one mistake that would
   poison everything — **a stored guess is indistinguishable from a measurement a month later.**
   Leave it empty and let the fallback happen at query time, where it is visible and reversible.
4. **Mark every filled slot with its source.** When a capture later contradicts a slot, the source
   decides which wins: **a capture beats a timed review, and nothing beats the venue's own
   statement of its own programme.**
5. **The empty slots are the gold list.** Export them, sort by venue popularity, and that is the
   promotion's queue with no second decision made.

---

# 2a1. Where the slots come from — checked, 2026-10-03

**The slot table needs a schedule, and the schedule is the one field no API serves well.** Checked
rather than assumed.

### The reframe that shrinks the problem

**Most slots are not events.** The weekday/weekend split, the day/night split, the kitchen hours —
those come from `regularOpeningHours` and the type curve and need no feed at all. **Only the
exceptions need a schedule source, and the exceptions are mostly *recurring weekly rituals*, not
one-off events.**

> **Boxout Wednesday is not an event. It is a standing fact about Wednesdays.** You learn it once
> and it holds for months.

That changes what is needed from *a live events feed* to *a one-time look, refreshed quarterly* —
which is a completely different engineering problem, and a much smaller one.

### What exists, ranked

| source | gives | verdict |
|---|---|---|
| **the venue's own Instagram** | **everything** — recurring nights, one-offs, changes | **the primary source, and effectively the only one.** Boxout Wednesday was announced there and appeared in **zero** reviews |
| **the venue partner agreement** | the schedule, direct and licensed | **the clean route**, and the draft already exists |
| District / Paytm Insider APIs | ticketed events | **exist but are partnership-gated**, and they only cover what sells tickets |
| scraper services (Apify et al.) | Insider and BookMyShow listings | paid, grey, and still only ticketed events |
| **schema.org `Event` on the venue's own site** | would be ideal — published *for* machine reading | **checked on Summer House: it does not exist** |
| Google Places | — | **no events field at all** |

### The check that settled it

`summerhousecafe.in` publishes `schema.org/LocalBusiness` and `WebSite` markup and **zero `Event`
nodes**. The entire site is **four links, all of them menus**. Meanwhile the venue's Instagram has
24.1k followers and is where the Wednesday programme is announced.

**That is the Delhi independent venue in one example: the web presence is a menu, and the schedule
is an Instagram feed.** Any design that assumes a parseable events page will fail on most of the
seed radius.

### So the method

1. **One manual pass at seed time.** Fifty Instagram accounts, note the recurring nights. An hour
   or two, and it is the same pass that collects the images (§5).
2. **The partner agreement carries it after that** — the venue tells us when the programme changes,
   because they want the traffic.
3. **Refresh quarterly**, not nightly. A recurring ritual is stable; treating it as live data is
   solving a problem that does not exist.
4. **One-off events** (a touring act, New Year) are genuinely feed-shaped and genuinely unserved.
   They matter less, because the engine selects on the ordinary night — and a venue with a
   relationship will tell us.

---

# 2a2. Types and bands are DAY-scoped as well as hour-scoped

**The user, 2026-10-02: "Bohca is a club after 10PM on weekends and a pub after 10PM on weekdays."**
The same clock, a different venue. Hour-scoping alone cannot say this.

```python
'types': [('buzzy restaurant', 'all', 12, 17),
          ('games pub',        'sun', 12, 17),     # a specific day overrides
          ('buzzy restaurant', 'all', 17, 22),
          ('pub',              'mon-thu', 22, 26),
          ('club',             'fri-sun', 22, 26)]
```

**Bands take the same dimension**, because a Tuesday at 23:00 in that room is not an 86:

| | ENRG | CROWD |
|---|---|---|
| weekday 22:00–01:00 | **62** | **55** |
| weekend 22:00–01:00 | **86** | **92** |

**The cost barely moves.** Almost every venue has exactly two day-modes, so a venue needs **eight
numbers instead of four** — four weekday, four weekend — with a specific day overriding only where
something genuinely differs, as Sunday brunch does at Bohca. For a 50-venue seed that is still an
afternoon.

**The supply grid gains one dimension and doubles**: `(day_mode, hour, energy bucket, crowd bucket)`
where `day_mode` is `weekday | weekend`. A few thousand cells becomes a few thousand more, which is
nothing.

**Default to two modes, allow seven.** Most venues need `weekday` and `weekend`; the override exists
for the Sunday-brunch case and should be used sparingly, because every override is a number
somebody has to keep true.

---

# 2a3. THE METHOD, stated once: the type is the prior, the venue is the deviation

**This has now arrived three separate times from three different directions, so it is the method
rather than three patches:**

| | the type supplies | the venue supplies |
|---|---|---|
| **energy bands** (§5.4) | the canonical hourly shape | one amplitude |
| **`AFFIL`** (below) | the whole value | **nothing** |
| **lexicon scoring** (§5.8) | the prior for every factor | evidence that moves it |

> **Where venues of a type do not meaningfully differ, a per-venue field is a per-venue opportunity
> to be wrong.**

### `AFFIL` is a type constant and not a venue field at all

**Corrected 2026-10-02, the user, twice over.** An earlier draft had `AFFIL` for a club rising with
its crowd band, on the reasoning that a fuller room makes people hold their table harder.

**That reasoning was wrong about Delhi.** The user: *"people that are on tables are not high AFFIL
by themselves, people mostly use tables to order bottles of alcohol then dance among the crowd."*
**A table in a Delhi club is a logistics base, not a social enclosure** — it is where the bottle
lives, and the people are on the floor.

**So `AFFIL` does not vary with crowd, and it does not vary between clubs.** All clubs carry the
same value. More than that:

> **`AFFIL` cannot decide a venue at all.** *"Someone who wants to be among their group will be
> among their group in a club, or will not if they don't want to."* It is a fact about what a
> person does in a room, not about the room.

This is the sharpest statement yet of why §0 is right that identity factors do not touch venues —
and `AFFIL` is the clearest case, because even the *crowd* estimate barely varies by venue.

---

# 2a4. The door — walked back from a gate to a near-irrelevance

**An earlier draft made the door a hard stage-1 gate**, on the strength of how dominant stag-entry
and guestlist questions are in a decade of Quora threads. **The user corrected the inference, and
the correction is about what the app is for:**

> *"There are only about 8-10 nightclubs that people actually go to on a weekend and getting entry
> there is their job and most people know what it's like. As an app the main utility is finding
> people to go to that club with, or joining a group that is going, rather than getting recommended
> the right club where they can enter."*

**Three things follow, and the third is strategic.**

**The club set is tiny and known.** Eight to ten venues citywide on a weekend. Nobody needs an
engine to find them, and everybody already knows what each door is like. Modelling the door as a
filter solves a problem users do not have.

**So it stays as a tag**, not a gate — `guestlist`, `couples-preferred` — printed on the card for
information, filtering nothing.

**And the app's value is hour-dependent, which nothing else in these documents says.**

| | the set to choose from | what the app is actually for |
|---|---|---|
| **early, 19:00–22:00** | hundreds of venues | **finding the place.** Selection does real work |
| **late, after 22:00** | **eight to ten clubs everybody knows** | **finding the people.** Selection does almost nothing |

**This reframes the thin club supply flagged earlier.** It is not a gap to fill — it is the nature
of that end of the night, and trying to solve it with more venues would be solving the wrong
problem. **At the late end the Place/People filter is barely a choice: it is People, and the
engine's job is the room rather than the room's plan.**

---

# 2a5. The popularity floor, and what releases it

**Corrected 2026-10-02, the user:** there are more than 8-10 clubs - there is a long tail of less
popular ones - **"but the app should only suggest the popular ones if the user hasn't set a
budget."**

**So popularity is a default floor, and a budget is what releases it.**

```python
if room.budget is None:          # no budget stated
    candidates = [v for v in candidates if v.popularity >= POPULARITY_FLOOR]
# a stated budget filters on price instead, and the tail comes back
```

**Why this is right rather than merely convenient.** A user who states no budget has told you
nothing about price, so the safe default is *the places people actually go* - being sent somewhere
obscure is a worse failure than being sent somewhere predictable. **A user who states a budget has
told you what matters to them**, and at that point the long tail is not a risk, it is the answer:
the cheaper, less famous rooms are precisely what a low budget should surface.

`popularity` comes from `userRatingCount` normalised within `(type, area)` - the same field §5.0.1
uses for the crowd amplitude, so nothing new is fetched.

**This also resolves the thin-club worry properly.** The late-night set is small *by default* and
deliberately so. It is not thin supply; it is a floor doing its job - and it lifts the moment a
user says what they want to spend.

---

# 2b. The tag vocabulary — six families, and what asks for each

**Corrected 2026-10-01: this document previously asserted "~600 tags against ~100 types" and
neither number had anything behind it.** Twelve types are actually defined (`FACTORS_V5.md` §4,
now that `street / market` is retired) and **zero tags were.** Here is the vocabulary.

**Tags come in families, and that is what keeps them linear.** A venue carries 4–8 of them, drawn
from any family. 49 are listed here; a full Delhi pass lands around **120–150**, not 600.

| family | tags |
|---|---|
| **layout** (7) | `table-led` `booth-heavy` `bar-rail` `open` `standing-room` `floor` `courtyard` |
| **setting** (9) | `open-air` `rooftop` `garden` `terrace` `basement` `daylight` `skyline` `waterside` `indoor-only` |
| **period & character** (8) | `heritage-building` `heritage-styled` `listed-structure` `colonial-bungalow` `minimal` `maximalist` `industrial` `dive` |
| **service** (8) | `tasting-menu` `small-plates` `thali-service` `counter-service` `full-service` `late-kitchen` `early-kitchen` `bar-snacks-only` |
| **access** (8) | `walk-in` `reservation-only` `ticketed` `cover-charge` `members` `queue-after-9` `no-queue` `age-gated` |
| **programming** (9) | `live-music` `dj-after-11` `sufi-night` `sitar-classical` `ghazal-qawwali` `quiz-night` `screening` `match-days` `open-mic` |

**Rules for adding one.** A tag must (a) sit in exactly one family, (b) be decidable from photos,
the venue's own copy, or a listing — never from a visit, (c) **discriminate within a type**, so if
it is true of every pub it is not a tag, and (d) be something a user could notice. A tag nobody
would ever remark on cannot change whether they liked the night.

## 2b.1 What asks for each family — and this is rung 1's input

**The dangling input, fixed.** §4 rung 1 says *"the tags the room asked for"*, and when the
identity factors stopped touching venues on 2026-10-01 that phrase lost its source: `TALK` had been
register and `AFFIL` + `MOVE` had been layout. **Nothing replaced them, and rung 1 was left reading
from nowhere for a day.** It reads from here instead, and nothing in this table is a vibe factor:

| family | asked for by | example |
|---|---|---|
| **setting** | `SCEN` | SCEN 88 → prefer `skyline`, `garden`, `open-air` |
| **period** | `HERIT` | HERIT 88 → `heritage-building`, `heritage-styled` (§1.4) |
| **programming** | `LIVE`, `HERIT`, and the room's clock-anchor flag | LIVE 96 → `live-music`; a heritage programme → `sufi-night` |
| **service** | `FOOD`, **and the hour** | FOOD 90 → `tasting-menu` / `small-plates`; a 01:00 stop → `late-kitchen` |
| **access** | `POL`'s sense, **and the hour** | POL *classy* → `reservation-only`; POL *current* → `dj-after-11` |
| **layout** | **group size only** | a group of 6+ → `booth-heavy` or `standing-room` (Dunbar: conversation groups cap at four) |

**Three things worth noticing about that table.**

**The preferences do nearly all the work**, which is correct — they are the one thing a user states
*about places*, and rung 3 already scores venues on them. Rung 1 uses them as a **filter**, rung 3
as a **ranking**. Same input, two jobs, and no vibe anywhere.

**The hour is a legitimate asker.** A 01:00 stop wants `late-kitchen` whoever is in the room. That
is structural, not a taste.

**Layout lost its driver and is now mostly descriptive.** It used to come from `AFFIL` and `MOVE`.
Under the correction only **group size** asks for a layout tag; otherwise layout tags are
**printed on the card and not used to filter** — *"a courtyard, table-led"* tells the user what
they are walking into without pretending anybody asked for it. **That is a real demotion and it
should be visible**: if real rooms turn out to care about table-versus-floor, the honest fix is to
ask them on the skeleton, not to quietly re-admit the vibe.

---

# 3. The supply grid

```
(hour, energy bucket, crowd bucket) -> types that actually HAVE venues there
```

Precomputed nightly from §2, shipped to the phone. **This is the table that makes the live preview
in the skeleton game possible** — the box above each circle is an O(1) lookup while the line is
being dragged, not a query.

Five venues give 36 non-empty cells; a real city gives a few thousand, which is small enough to
ship. The grid is **the highest-stakes artefact in the app**: if it is stale or thin, the preview
lies, the user draws against the lie, and the plan disappoints for a reason they cannot see.

---

# 3b. Preference tagging — three states, and only one of them is a number (2026-10-05)

**The user: "the venues need only be tagged with the factors representing the skeleton. The
preference factors are optional … if a place has good food the reviews will definitely mention it
somewhere."**

**A venue is tagged on `ENRG` and `CROWD` always — those are what the skeleton asks for and nothing
reaches a stop list without them.** Preferences are tagged where the evidence speaks and left alone
where it does not. Three states, and a venue may hold a different one per preference:

| state | means | written when |
|---|---|---|
| **served, with a score** | the reviews say so | keyword evidence clears the lexicon's threshold |
| **not specialised** | **a flag, not a zero** | the reviews are silent **and the venue's type is about that preference** |
| **unknown** | no claim either way | the reviews are silent and the type is about something else |

**The difference between the last two is the whole rule.** Silence about food at a *restaurant* is
evidence — reviewers of restaurants write about food, so if nobody did, it is not the point of the
place. **Silence about food at a bar is not evidence**, because reviewers of bars write about drinks
and the room, and a bar with a good kitchen can go a hundred reviews without anyone saying so. That
is the Summer House case exactly.

**`not specialised` must never be stored as a low score.** A score says *we measured this and it is
bad*; the flag says *this is not what this place is for*. They rank identically today and they are
not the same claim, and a stored zero is indistinguishable from a measurement a month later — the
same error §2a1 forbids for slots.

### 3b.1 What the Kwality test found

**Tested on Kwality, Connaught Place (`simulations/prefserve.py`), a 1940 institution.** The
hypothesis held and **the scorer failed it**, which are two different results:

- **Held:** all five reviews say the place is old without being asked — *"since the 1970s"*,
  *"running since 1940"*, *"a piece of Delhi history"*, *"my grandparents ate here"*. **Age is
  narrated.** It is one of the few venue attributes a reviewer treats as a story rather than a fact.
- **Failed:** `HERIT` scored **47**. The lexicon's list was museum vocabulary — *heritage, colonial,
  haveli, old-world* — and **people do not write like that.** Widened to the ordinary words and it
  reads **88 on 34 hits**.
- **And a second defect nobody was looking for: `SCEN` scored 75** on reviews saying the decor is
  *dated*, the room *plain*, *no frills* — because `decor` was a hi keyword and the lo list held
  only *shabby, run-down, dingy*. **The look of a room is what reviewers criticise most readily and
  the list could not hear any of it.** Widened: **34**.

**`SCEN` 34 against `HERIT` 88 is the user's own 2026-10-01 finding, measured.** Old-feeling and
badly-kept are orthogonal, and a single "old" axis could never have said that.

**`NOV` is not derivable from any corpus and never will be.** *Somewhere new* is new **to the
user** — it is served from their own history, not from a venue tag.

---

# 3c. `HERIT`'s selection weight drops to 10 (2026-10-05)

**The user: "HERIT doesn't really hold much of a place in venue selection, it's a preference most
people can go without even if they like it."**

**14 → 10 for selection only.** The badge, the profile and the swipe card are unchanged — this is
about how hard it argues for a venue, not about how much it says about a person. It is a judgement
number, like every other weight in the set, and it compounds with the suppression in §4b, where
`HERIT` is already one of the two preferences a loud stop collapses.

---

# 4. Selection — the skeleton chooses the set, preferences order it

> **Revised 2026-10-05 (the user): "the venues that match each stop are shown for that stop and the
> user gets to choose … they would be ranked on the basis of how well the preference factors are
> served."**
>
> **Stage 2 is no longer conditional.** It used to run *only* where stage 1 tied and the room
> clashed, because the app had to emit **one** venue and preferences were the tie-break. **The app
> now offers a list** (`MVP_INSTRUCTIONS.md` §2.2), so preferences have a bigger and simpler job:
> **stage 1 decides who is in the list, stage 2 decides the order within it.** The clash machinery
> below survives as the rule for *which* preferences count in a room, not for whether to look.

**Rewritten 2026-10-01 (the user): "venue selection should happen exclusively on the basis of the
skeleton — energy and crowd at that moment — and then move onto the preference factors depending
on whether there is a clash in the room."**

Four rungs become three, and the rung that went was the character filter. Prototyped in
`simulations/select3.py`.

### Stage 1 — the skeleton, and nothing else

For each stop the merged skeleton gives `(hour, energy, crowd)`. Rank every venue inside the
radius whose band covers that hour:

```python
distance = |band_energy − drawn_energy| + 0.6 × |band_crowd − drawn_crowd|
```

**No preference, no tag, no vibe.** If one venue is clearly closest, it is the pick and stages 2
and 3 never run.

### Stage 2 — preferences, and only where stage 1 tied *and* the room clashes

```python
SHAPE_GATE = 12
```

**Only venues within `SHAPE_GATE` of the best distance may compete.** Beyond it a user could tell
the difference, so preferences do not get to overrule the line they drew. **This is what makes
stage 1 *exclusive* rather than merely *first*** — without it a venue 25 points off the drawn shape
can win on a preference, which is the engine ignoring the only thing the user actually stated.

Then, inside the gate:

1. **Which preferences are live in the room** — anybody at 70+ on it.
2. **Subtract what has already been served earlier tonight** (see below).
3. **If one candidate serves everything outstanding, take it. No clash.**
4. **If none does, it is a clash**, and it resolves by **who cares, summed**: a venue serving two
   people at 80 beats one serving a single person at 95. Shape still pulls inside the gate, and
   quality breaks what is left.

### Stage 3 — quality, tie-break only, never a chooser

### 4.1 The rule that stops most clashes being clashes

**A clash at one stop is usually not a clash across the night.** Stops are filled in order,
carrying what has already been served:

| | | serves |
|---|---|---|
| 20:00 | Piano Man | `LIVE`, `SCEN` |
| 23:00 | Social, HKV | `FOOD`, `GAMES` |

Four live preferences across a room of three, **no single venue serving more than two**, and all
four served by the night. Neither stop could have done it alone, and at neither stop did the
engine have to pick a loser.

**Only what survives to the end gets the unserved line**, and it goes at the **bottom of the card**
rather than under a stop, because it is a fact about the night: *"No live music tonight — nothing
on this shape has it."*

### 4.2 What tags do now

**Tags no longer filter.** The character rung is gone. They have two jobs:

- **how a preference finds a venue** — `HERIT` looks for `heritage-building`; `LIVE` for
  `live-music`; `GAMES` for `pool-table`. The tag is the *mechanism* of stage 2, not a stage of
  its own.
- **what the card prints** — *"a courtyard, table-led"* tells the user what they are walking into.

Nothing is selected by a tag alone, and the layout family (§2b) is now purely descriptive except
where group size forces it.

---

# 4a2. Coordinate tags instead of factor scores — tested, not adopted (2026-10-07)

> **The user: "explore whether the venues can be tagged with their best co-ordinate in a skeleton as
> a replacement to tagging them with factor scores, and then checking whether that venue matches the
> plan according to the timing and placement."**

**The proposal:** stop storing a venue's energy and crowd, and store **where in a night it belongs**
— an opener, a middle, a closer, at a level — then match a stop's own coordinate to it.

**The implicit argument is robustness, and it is a good one.** Our venue scores carry about **7
points of error**, and a coarse tag may be a more honest statement of what we actually know than a
distance computed to two decimals. **Quantising is the right move when the noise is large relative
to the resolution you are pretending to have.** So the question is not elegance, it is where the
crossover sits. Tested in `simulations/coordtag.py`: 400 venues, 3,000 drawn nights, every stop put
through both methods and **both judged against the venue's true scores, which neither can see.**

### The result

| score error | scores | coordinate | scores better by |
|---|---|---|---|
| 0 points | 8.62 | 15.05 | 6.43 |
| **7.1 points — ours** | **11.21** | **16.36** | **5.15** |
| 14 points | 15.12 | 18.35 | 3.23 |
| 25 points | 20.88 | 22.15 | 1.28 |
| **40 points** | 26.33 | **25.66** | **−0.67 — the coordinate finally wins** |

**The mechanism is real and the crossover exists — it sits at about five times our current error.**
At 7.1 points the scores are better by 5.15, and the quantised list is also **less selective**: 77
venues against 51, because matching a cell admits everything in a band regardless of how close it
actually is.

**So: not adopted, and for a measured reason rather than a preference.** If the lexicon ever
degrades past roughly 25–40 points — which would mean the scoring had largely failed — quantising
becomes the better answer, and this test says so.

### What the test cannot settle

**Whether a venue has a *role in a night* that is genuinely independent of its energy, crowd and
hours.** A heritage restaurant and a quiet cafe can score the same and still be a dinner-first place
and an afternoon place. If that is real, **it is an extra tag rather than a replacement**, and it
would sit beside the scores rather than instead of them.

**The simulation cannot answer it**, because its venues have no role beyond their hours and energy
— the answer would have to be seeded in to come out. **It is a question for the first real database**,
and the way to find it is to look for venues the shape ranking places wrongly in a way their scores
do not explain.

**And note how much placement the hours already do.** A venue that closes at 23:00 cannot be a
closer, and the stop list already filters on opening hours, so *"timing and placement"* is partly
enforced before any tag is consulted.

---

# 4b. Preferences are preferences — feasibility, not a multiplier (2026-10-05)

> **The user: "preference factors are what the name suggests — preferences. They never come above
> the shape of the night, so if a preference can't be served at a venue along with the shape of the
> night at that stop then that preference is not considered while picking the venue."**

### 4b.1 The rule

**For each stop, a preference is LIVE when both hold:**

1. **somebody wants it** — a member at **60 or above**; members below 60 simply do not contribute,
2. **and some venue inside the shape gate can actually serve it.**

**Everything else is ranking.** Live preferences order the stop list by *who cares, summed*; a
preference that fails either test is **not considered at that stop** and **carries forward to the
next one** (§4.1) rather than being marked served.

**It is never a gate and never a veto.** A preference cannot remove a venue from the list, cannot
overrule the drawn shape, and cannot be killed by one member objecting. **A low member is not an
objector — they are simply not an advocate**, which is the correction of 2026-10-05 and the reason
the earlier draft of this section was wrong.

**And the hour does the rest.** Kitchens close and games venues close, and only venues open at that
hour are in the list at all — so *"GAMES, depending on the time"* needs no new machinery.

### 4b.2 Within-factor chemistry — proposed, measured, and **not adopted**

**The user's observation was right: you cannot have high `ENRG` and high `FOOD` in the same room.**
The first prototype (`simulations/prefserve.py`) encoded it as a multiplier on each preference's
weight, scaled by the drawn energy — `FOOD` to 0.25 at a loud stop, `HERIT` to 0.30, `LIVE` boosted
to 1.30.

**`simulations/prefgate.py` then measured whether it was doing any work, and it is not.**

**The shape gate already performs the suppression**, because the venues that serve food *are* the
quiet ones. Share of in-gate venues that can serve each preference, with **no multiplier applied**:

| the stop drawn | in gate | `FOOD` | `LIVE` | `POL` | `SCEN` | `HERIT` | `GAMES` |
|---|---|---|---|---|---|---|---|
| quiet, E25 C35 | 54 | **80%** | 11% | 28% | 72% | 43% | 4% |
| calm, E45 C50 | 83 | 78% | 12% | 49% | 67% | 57% | 1% |
| buzzy, E65 C70 | 113 | 47% | 32% | 51% | 40% | 15% | 27% |
| loud, E80 C85 | 91 | **15%** | 29% | 58% | 40% | 9% | 25% |
| going off, E92 C92 | 61 | **10%** | 11% | 70% | 38% | 2% | 10% |

**`FOOD` falls from 80% to 10% and `HERIT` from 43% to 2% on their own.** The correlation the table
encoded is already in the data, venue by venue.

**Over 4,000 simulated stops the two methods pick the same venue 90.2% of the time** — and in the
9.8% where they differ, **the multiplier is wrong**:

> drawn **E94**, user `FOOD` 88 `POL` 75 `GAMES` 75
> feasibility → **a big loud bar serving `FOOD`, `POL`, `GAMES`** — three live preferences including
> their highest
> the multiplier → **a club serving `POL`, `SCEN`, `GAMES`** — `FOOD` 88 discarded

**The disagreements are all the same shape: a venue inside the gate that serves a suppressed
preference anyway** — the loud bar that genuinely does good food, the busy room that genuinely is
old. **The multiplier penalises exactly the venue that solves the problem**, applying a correlation
learned across types to a venue whose own data contradicts it.

**That is the error §2a1 already forbids for slots, in a new place: the prior is for when evidence
is missing, never for overruling evidence that is present.** We have the venue's own tags. They win.

**So: not adopted.** The suppression table stays in `prefserve.py` as the prototype that was tested
and the measurement that retired it. **The user's observation survives intact — it was true about
the world and already encoded in the gate.** The `LIVE` boost to 1.30 goes with it: unlike the
suppressions it was never a feasibility claim, it was mine, and nothing evidences it.

---

# 4a. THE LICENCE FINDING — Places is a display API, not a data source

**Checked 2026-10-02 against the Google Maps Platform Terms of Service and the Service Specific
Terms. This supersedes every "assume Places" line below it, and it is the most consequential thing
in this document.**

### What the terms actually say

> **3.2.3(a) No Scraping.** *"Customer will not export, extract, or otherwise scrape Google Maps
> Content for use outside the Services. For example, Customer will not: (i) pre-fetch, index,
> store, reshare, or rehost Google Maps Content outside the services; … (iii) **copy and save
> business names, addresses, or user reviews**"*
>
> **3.2.3(c) No Creating Content From Google Maps Content.** *"…(v) construct an index of tree
> locations within a city from Street View imagery; … (vii) **use Google Maps Content to improve
> machine learning and artificial intelligence models, including to train, test, validate or
> fine-tune the models**"*
>
> **3.2.3(d)** *"…(iii) use the Google Maps Core Services **in a listings or directory service**"*
>
> **Service Specific Terms, A.3 — Google ID Caching.** *"Customer may cache the **Google ID
> values**… For example, Customer may cache `place_id` from Places API"*

### What that means, plainly

**The only field you may store is `place_id`.** Not the name, not the address, not the rating, not
the reviews, not the attributes, and not the photos. Everything else must be **fetched live and
displayed**, with attribution, and then discarded.

**So the venue database as designed cannot be populated from Google.** Example (v) of 3.2.3(c) —
*constructing an index of tree locations from Street View* — is structurally identical to
constructing an index of venue energy bands from Places photos. And a stored, tagged, searchable
set of venues is squarely what 3.2.3(d)(iii) calls a listings service.

**This is not a grey area and it should not be treated as one.** It is also not a surprise in
hindsight: Places is priced and shaped for live display inside an app, which is exactly what the
licence permits.

### What Google is still good for

- **`place_id` as the join key**, cached indefinitely and legitimately. Every other source can hang
  off it.
- **Live display on the venue screen** — photos, hours, rating, fetched at view time with
  attribution. `VIEW_FLOW.md`'s media rule already allows exactly this and nothing more.
- **Deciding whether a venue is worth a human's time** during the seed pass. Looking at Google to
  decide where to go is not storing Google's content.

### So what populates the database

| source | what it gives | rights |
|---|---|---|
| **manual curation of the seed radius** | types, four energy bands, four crowd bands, character tags, the heritage call | **ours** — a person deciding things is not Google's content |
| **the venue partner agreement** | the venue's own photos and video, hours, menu, event calendar, capacity | **licensed, by agreement** — a draft already exists in the project folder |
| **our own users** | in-app photos and videos, End Plan ratings, the band corrections | **ours**, and it compounds |
| **OpenStreetMap** | name, location, coarse category | **ODbL** — storage and derivation explicitly permitted, with share-alike |
| **a licensed places provider** | bulk attributes, and possibly the rating distribution §1.2 needs | **paid**, and this is the decision to make if the seed needs to scale |

**The seed radius was already the plan and this makes it the only plan.** Fifty venues, curated by
hand, is not a compromise forced by cost any more — it is the only version of this that is
licensed. The good news is that it was already costed at an afternoon.

### What this kills

**Image-similarity tagging cannot run on Places photos.** §5 keeps its method — reference sets,
the confound rule, mean-versus-share — but it must run on **venue-supplied, user-supplied or
licensed** images. At seed scale that means the venue's own media, which the partner agreement
already asks for.

**The supply grid cannot be built from Google.** It is precomputed and shipped to the phone, which
is storage and redistribution of derived content.

---

# 5.0 What the APIs actually return — checked against the docs, 2026-10-02

**Three assumptions in this document were wrong, and they were load-bearing.** Checked directly
against `developers.google.com/maps/documentation/places`:

| assumed | actually |
|---|---|
| Popular Times comes free with the Places call | **There is no popular-times field in the Places API at all.** There never has been. It is visible in the Maps UI and is not exposed |
| we can compute a rating **spread** for admission (§1.1, SD ≤ 0.85) | **Places returns `rating` and `userRatingCount` only — no histogram, no distribution.** And a **maximum of 5 reviews**, so a spread cannot be computed from them either |
| a venue has enough photos for a top-decile share (§5.2) | **A maximum of 10 photos** are returned per place |

**And one pleasant surprise that offsets a lot of it.** The *Enterprise + Atmosphere* field set
contains structured attributes that replace work I had assigned to image inference:

> `liveMusic` · `goodForWatchingSports` · `outdoorSeating` · `reservable` · `goodForGroups` ·
> `servesCocktails` `servesWine` `servesBeer` `servesDinner` `servesBrunch` `servesCoffee`
> `servesDessert` `servesVegetarianFood` · `editorialSummary` · `generativeSummary` ·
> `neighborhoodSummary` · `reviewSummary` · `priceLevel` · `priceRange` · `regularOpeningHours` ·
> `openingDate` · `parkingOptions` · `allowsDogs` · `restroom` · `accessibilityOptions`

**`liveMusic` is a boolean.** `LIVE` does not need inferring at all. `goodForWatchingSports`
decides the `match bar` type. `outdoorSeating` is a setting tag for free. `regularOpeningHours`
is the clock-pin from §5.4. `openingDate` plus `userRatingCount` gives **reviews per month**,
which is the popularity signal the `CROWD` band needs now that Popular Times is gone.

### 5.0.1 What each broken assumption costs, and what replaces it

**Popular Times — gone, and mostly it does not matter.** §5.4 already measured that the **type's
canonical shape beats crowd-as-shape** for the `ENRG` band, so energy never needed it. What did
need it is the **`CROWD` band**, and the fix is symmetric: **author a crowd curve per type as
well**, scaled by a per-venue busyness amplitude from `userRatingCount / months_open`. Both bands
become *type shape × venue amplitude*, and neither needs a field Google does not publish.

*If real crowd data turns out to be necessary later, it is a paid third party (BestTime and
similar aggregate foot traffic legitimately) — not something to design around now.*

**The rating spread — not obtainable, so §1.1 loses its best test.** What survives of admission:
`rating`, `userRatingCount`, **operator class**, **fit-out age**, and **drift** measured by
comparing the 5 returned reviews (requested newest-first) against the lifetime mean. That drift
check is a much weaker instrument than SD and it is now the only consistency signal in the filter.
**§1.2's argument still stands — spread is the right thing to measure — but it has to come from
somewhere else, and nothing free provides it.** Flag for the first paid-data decision.

**Ten photos — so use the mean, not the share.** §5.2 recommended scoring a venue by the *share*
of its photos clearing the high-pole threshold rather than the mean. **Measured at the cap, that
conclusion flips** (`simulations/photocap.py`): over 400 trials on five venues with known truth,

| estimator | orders venues right, 40 photos | **orders right, 10 photos** |
|---|---|---|
| plain **mean** | 99% | **88%** |
| **top-decile share** | **92%** | 83% |
| mean of top 3 | 90% | 77% |
| max | 80% | 67% |

A decile of ten photos is one photo, so the share quantises to 0/10/20 and loses its resolution.
**Use the share where a venue has 30+ photos — its own feed, an opted-in Instagram — and the mean
at the Places cap.** The selection bias does not go away; it just has to be corrected with a
constant per venue **type** rather than measured per venue.

---

# 5. Where every field comes from — image similarity, and its three limits

**The user's method, 2026-10-02: hold a small reference set of images per factor, embed a venue's
own photos, and score by similarity.** It is the right idea and it is how most of this table gets
filled. Three things in it break on contact, and the corrections are what the rest of this section
is. Prototyped in `simulations/imagetag.py`.

### 5.1 Three of the named factors no longer reach a venue

`MOVE`, `TALK` and `AFFIL` are identity factors, and since §0 they do not touch a venue at any
stage. **Tagging a venue for them is work with no consumer.** Conversely `SCEN` was not on the
list and **it is the single most image-assessable field there is** — `SCEN` *is* the look of the
place. The work shrinks by three and grows by one, and the one it grows by is the easiest.

### 5.2 Selection bias — use the share, not the mean

**People post a venue at its best.** Every venue's photo set skews toward its peak, so every mean
similarity drifts up and the venues compress toward each other. Simulated over five venues with
known truth:

| | spread it can see |
|---|---|
| **mean** similarity to the high-pole reference | **56 points** |
| **share** of photos clearing the high-pole threshold | **94 points** |

**So score a venue by the fraction of its photos that match the high pole, not by average
similarity.** The bias is roughly constant across venues, so a share stays comparable where a mean
does not.

### 5.3 The real risk — a reference set that varies on the wrong thing

**If every `ENRG`-high reference is a dark club photo and every `ENRG`-low reference is a daylight
café, the embedding does not learn energy. It learns brightness.** Run it:

| venue | true `ENRG` | confounded score | controlled score |
|---|---|---|---|
| club, dark | 88 | 90 | 88 |
| **club, brightly lit** | **85** | **42** | **80** |
| **candlelit restaurant** | **26** | **72** | **31** |
| bright daytime café | 20 | 14 | 19 |

**The confounded set calls a brightly-lit club calmer than a candlelit restaurant.** Rank error 8
against 0.

> **The rule: a reference set must vary on everything except the factor.** For `ENRG`-high you need
> a dark club **and** a bright afternoon party **and** a lit-up wedding floor. 10–20 images per
> pole, deliberately mixed on time of day, colour, indoor/outdoor and crowd.

**Nothing downstream will catch this if it is got wrong**, because the number will look perfectly
reasonable. The reference set is the one artefact here that has to be built carefully by a person.

### 5.4 The band problem, and the measured fix

**Bands are hour-scoped and an image score is a property of a venue.** Photo timestamps are when
somebody *posted*, not when they were there — people post the next morning. **Images give the
amplitude and cannot give the shape.** So the shape has to come from somewhere else.

Five candidates, measured against known truth over 20 venues and 3,000 drawn stops
(`simulations/bandfix.py`). The metric that matters is **not** error in the number — it is whether
the pick still lands **inside `SHAPE_GATE`**, because inside the gate the user got a venue that
fits what they drew:

| method | mean error | **inside the gate** |
|---|---|---|
| flat — no shape at all | 14.5 | 70% |
| crowd as the shape (Popular Times) | 9.6 | 78% |
| **the TYPE's canonical shape × image amplitude** | **8.2** | **83%** |
| the type shape, shifted to the venue's crowd peak | 10.1 | **75%** |
| two bands only | 12.4 | 70% |

### The shape comes from the TYPE, not from the crowd

**Three reasons it beats crowd-as-proxy, and the first is the real one:**

**Crowd and energy peak at different hours, and the gap is type-dependent.** A restaurant is
fullest and loudest at the same time; a big loud bar is fullest at midnight and loudest an hour
later; a club is both, late. Using crowd as the shape bakes that lag in as error — and it is a
*different* error per type, so no single constant corrects it.

**The type is already known** — it is stage 1 of selection. Nothing new is fetched.

**Twelve curves authored once** replace a judgement per venue per hour **forever**, including for
every venue added later. That is the part that decides whether this scales past one neighbourhood.

> ```
> TYPE_CURVE['big loud bar'] = {18:.10, 19:.22, 20:.38, 21:.58, 22:.80,
>                               23:.95, 24:1.0, 25:.92, 26:.70}
> energy(venue, hour) = base + (peak_from_images − base) × TYPE_CURVE[type][hour]
> ```
>
> **One number per venue** — the image-derived peak. Everything else is the type's.

### Two things the test killed

**Shifting the curve to the venue's crowd peak makes it worse** (75% against 83%). The crowd peak
is a noisy estimator of the energy peak, and shifting on it adds error rather than removing it.
*This was my own proposal and it is wrong.*

**Two bands is no better than no shape at all** (70% against 70%). If a venue gets only two blocks,
the shape has already been thrown away.

### So: four bands

| bands | mean error | inside the gate |
|---|---|---|
| 2 | 12.3 | 73% |
| 3 | 9.5 | 77% |
| **4** | **8.8** | **84%** |
| 5 | 8.8 | 79% |
| 9 (the full curve) | 8.2 | 83% |

**Four bands is indistinguishable from the full hourly curve and there is no gain beyond it.**
`§2` said "two to four"; it is **four**.

### The correction ladder, in order

| | | when |
|---|---|---|
| **a** | **the venue's own opening hours** pin the curve to the clock — a place that shuts at 23:00 cannot peak at 01:00. Free with the Places call | at ingest |
| **b** | **hand-correct the four numbers** for the seed radius | once, an afternoon |
| **c** | **learn from users.** End Plan already rates each stop; one extra tap — *"louder or quieter than you expected?"* — corrects a band per locked plan | the only route that ends up **right**, and the only one that needs users, so it is last |

~~shift the curve to the crowd peak~~ — measured, harmful, removed.

### 5.5 The access question — and the answer is not Instagram

The user named the hinge correctly: all of this rests on the images being reachable. Honestly:

**Instagram hashtag search is not a viable base.** The Graph API returns a business's own media only
once *they* connect their account; hashtag search is capped at a handful of tags per week, recent
posts only, no engagement data; and scraping is against terms and actively blocked.

**Google Places photos is viable today.** User-submitted photos per venue, under licence, no
hashtag needed — and it arrives in **the same call** as the rating, the review count, the review
text and Popular Times. That is **admission (§1), the `CROWD` band, the `ENRG` seed and the `FOOD`
signal from a single integration.**

~~**So the design assumes Places**~~ — **retracted the same day, see §4a.** Places may be read
live and displayed; it may not be stored or derived from. The foundation is the curated seed plus
the venue partner agreement, and Instagram remains enrichment for venues that connect their own
account.

### 5.6 The source table

| field | primary source | confidence |
|---|---|---|
| **`CROWD` band** | **Popular Times, directly** | high — it *is* the number |
| **`ENRG` band** | image amplitude × Popular Times shape | **seed only, human-corrected** |
| **`SCEN`** | images, top-decile share | high — it *is* the look |
| **`POL`** | images, top-decile share | good |
| **`HERIT`** | heritage lists (fabric) + images (styled) + the events table (programme) | good |
| **`FOOD`** | review text + rating | fair — **quality is not visible in a photo** |
| **`LIVE`** | the venue's own copy + the events feed | high |
| **`GAMES`** | the venue's own copy + images | high — a pool table is a pool table |
| `MOVE` `TALK` `AFFIL` | **not needed** — no consumer since §0 | — |

**`CROWD` should not come from images even though it could.** Popular Times gives the number
directly, hourly, already; inferring it from photos would be estimating something we can simply
read, from a biased sample, with unreliable timestamps.

### 5.7 Field by field — the method, the cost, and how each one fails

**`CROWD` band** — read Popular Times per hour, normalise to 0–100 against the venue's own busiest
hour, collapse to four bands. *Cost: free, in the Places call.* **Fails when** a venue has too few
visits for Google to publish a curve — then fall back to the type curve alone, and mark the venue
low-confidence so a human sees it first.

**`ENRG` band** — `base + (peak − base) × TYPE_CURVE[type][hour]`, where `peak` is the image
amplitude (§5.2's top-decile share, rescaled). Collapse to four bands, pin to opening hours.
*Cost: 12 curves once, then one number per venue.* **Fails when** a venue is atypical for its type
— a quiet club, a loud café. That is exactly what the hand-correction pass and the End Plan tap
are for.

**`SCEN`** — the strongest image case, because `SCEN` *is* the look. Top-decile share against a
reference set of beautiful rooms that **varies on type, light and era** (§5.3). *Cost: one
reference set.* **Fails when** the venue's photos are mostly of food rather than the room — detect
by the share of photos containing a plate, and fall back to the venue's own media.

**`POL`** — same method, two reference sets, because `POL` has a sense: *classy* (tailoring, low
light, set tables) and *current* (streetwear, neon, a crowd shot). A venue can score on both.
*Cost: two reference sets.* **Fails on** venues whose crowd changes by night — a Tuesday and a
Saturday are different rooms. Accept it; it is a preference, not a constraint.

**`HERIT`** — three routes, §1.4. Fabric from heritage listings and the venue's own copy; styled
from images against a reference set of old-world rooms; programme from the events table. *Cost:
one lookup, one glance, one feed.* **Fails when** a modern room has one heritage photograph on the
wall — which is why fabric is a *lookup* and only styling is an image judgement.

**`FOOD`** — **not from images.** A photo shows you plating, not whether it is good. Use the review
text: the share of reviews mentioning food positively, against the venue's overall rating. *Cost:
free with the Places call, plus a text pass.* **Fails on** bars that serve good food nobody reviews
— under-scores them, which is the safe direction.

**`LIVE`** — the venue's own copy and the events feed. A place with live music says so. *Cost:
free.* **Fails when** a venue has occasional acts it does not advertise — the events feed catches
most of it.

**`GAMES`** — the venue's own copy, confirmed by images. A pool table is unmistakable. *Cost:
free.* **Fails** almost never; this is the easiest field in the table.

**Three fields need a human and the rest do not:** the **reference sets** (once, carefully — §5.3),
the **styled/fabric call on heritage** (five seconds a venue), and the **four energy numbers** for
the seed radius. Everything else comes out of one Places call and a text pass.

### 5.8 The lexicon method — scoring a venue from review text

**The user, 2026-10-02: "there's a method underlying here, maybe using certain keywords or patterns
to get the factor scores of a place using the reviews alone, with images as supporting data."**
There is. Built and run on Bohca's real corpus — `simulations/lexicon.py`.

**The principle that makes it work is §7 of the Bohca test: polarity is irrelevant.** *"Too loud"*
and *"amazing energy"* are the same evidence. The method counts what people **describe**, never
whether they liked it — so a one-star review complaining about noise is worth exactly as much as a
five-star one praising the atmosphere.

```python
score(factor) = blend(TYPE_PRIOR[type][factor],          # what to believe before reading anything
                      50 + (hi/(hi+lo) − 0.5) × 100,     # what the text says
                      weight = evidence / (evidence + 6))
```

**Three things had to be fixed before it was usable**, and the first run is why they are here:

| | the failure | the fix |
|---|---|---|
| **wrong word sense** | *"traditional tapas"* fired `HERIT`, scoring a 2017 hotel bar **77** | **exclusion contexts** — a pattern that matches inside a cuisine phrase does not count |
| **saturation** | one-sided evidence pinned `ENRG`, `POL` and `SCEN` all to **98** | **blend toward the type prior**, weighted by evidence volume |
| **silence** | `TALK`, `FOCUS`, `LIVE` scored *nothing* — no reviewer writes *"I could not hear"* | **the prior answers when the text does not.** A club is `TALK` 18 whether or not anyone says so |

**Measured against the hand-built Bohca row:**

| | mean gap | factors scored |
|---|---|---|
| first pass, lexicon alone | **23.1 points** | 8 of 11 |
| **with exclusions and type priors** | **7.1 points** | **11 of 11** |

No factor now misses by more than 14. **`HERIT` went from 77 to 10 — exactly right — on one
exclusion rule.**

**What it still cannot do**, and this is unchanged by any of it: **the bands.** The method gives a
venue-level amplitude, which is precisely what §5.4 needs from images — so reviews and images are
*interchangeable sources for the same input*, and the hourly shape still comes from the type.

**Where images come in, as the user framed it — supporting data.** The lexicon is the primary
reading; images confirm or move it where the text is thin. `SCEN` is the clearest case: a venue
nobody describes visually can still be looked at. And `GAMES` scored 37 against a hand-built 45 on
a single mention — **one photograph of a board-game shelf settles that in a way more text cannot.**

**The honest limit on this validation.** The hand-built row was built from the same corpus by
careful reading, so 7.1 points measures *the method reproducing careful reading*, not the method
being right about Bohca. **Real validation is a venue the user knows well, scored blind.**

---

# 6. Why admission being strict argues *for* seeding one area

Two goals pull in opposite directions and both are right:

> the preview is only honest if the database is **dense**
> the promise is only kept if the database is **choosy**

The resolution is not to compromise on either. It is to **shrink the area**. A dense, choosy,
fully-curved **single radius** beats a thin choosy city: a user inside it gets honest previews and
kept promises, and a user outside it gets nothing — which is better than a bad night.

**Forty to sixty venues in one radius, fully curved and tagged**, is also the first state in which
rungs 1 through 4 face real competition. Everything simulated so far has run on fourteen venues
with one per `(type, area)` cell, which is to say the selection ladder has never actually been
tested.

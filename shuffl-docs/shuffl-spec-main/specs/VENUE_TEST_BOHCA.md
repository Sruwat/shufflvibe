# Can reviews build a venue row? — Bohca, Qutub, tested 2026-10-02

**The first real venue ever entered.** Built only from publicly readable reviews, listings and the
venue's own posts — no visit, no photos analysed, no API stored. The question was how far reviews
alone get us.

**Answer: further than expected on character, not at all on the thing we most need.**

---

# 1. What the sources say

| source | rating | n |
|---|---|---|
| Google | **4.1** | 953 |
| JustDial | 4.0 | 1,384 |
| Zomato | 4.1 | 396 |
| **TripAdvisor** | **2.9** | 9 |

**Hard facts, stated rather than inferred:** Qutub Hotel, Shaheed Jeet Singh Marg, Qutab
Institutional Area. Google type **tapas bar**, described as *"sophisticated restaurant with a
terrace, specialising in traditional tapas & sharing plates."* Service options: **reservations
required**, **all you can eat**, **outdoor seating**. Hours **12:00–01:00**. Price **₹2,000+ per
person** (reported by 32 people); JustDial says ₹3,100 for two. Music: **Bollywood, Punjabi and
English hits**. Opened around **2017** — it appears in LBB's 2017 bars-that-opened-this-year list.
Nominated in the Times Food & Nightlife Awards, *Best Bar (Casual Night Out)*.

**What the review text adds:** *"one of the finest place for the late night party in Delhi"* ·
*"best places to party till late, with amazing food, drinks and vibe"* · *"reserve your table 2–3
days in advance for weekends"* · *"judging by the massive crowd inside, instantly became the
weekend go-to for all of Delhi"* · *"joining the energetic crowd on the dance floor"* ·
*"expensive — 4k plus per person with no food"* · *"so-so music, puking teenagers, smoky indoors,
over smart bouncers"* · *"the club has terrible rules for entry"* · *"customers report variability
in service quality"*. A Reddit thread asks how to get on the **guestlist**.

---

# 2. The row

### types[] — and this is the finding

```
12:00–17:00   buzzy restaurant        (Sunday: games pub)
17:00–22:00   buzzy restaurant
22:00–01:00   big loud bar
```

**`FACTORS_V5.md` cites Bohca as the example of a `games pub`, and everything about its nightlife
reputation says club. Both are right.** From Bohca's own Facebook:

> *"Weekend = Brunch at Bohca! With a wonderful open ambiance, **lovely board games to keep you
> engrossed** and food and drinks to satiate your every hunger, the Hoppi Sunday Brunch…"*

**A board-games brunch place at 2pm on Sunday and a packed loud bar at midnight — the same room.**
This is the single best validation the hour-scoped `types[]` decision has had, and it came from a
venue the user picked for unrelated reasons.

### bands

| | ENRG | CROWD | why |
|---|---|---|---|
| 12:00–16:00 | **28** | **45** | brunch, terrace, board games, conversational |
| 16:00–20:00 | **42** | **40** | the dead part of the day |
| 20:00–22:00 | **65** | **72** | filling, music up, dinner crowd turning over |
| 22:00–01:00 | **86** | **92** | *"massive crowd"*, dance floor, queues, bouncers |

**Every one of these eight numbers is inferred from prose.** No source states an energy level at an
hour. See §4.

### prefs — fixed

| | | evidence |
|---|---|---|
| `FOOD` | **68** | tapas and sharing plates, specific dishes praised; but *"4k with no food"* and the food is not why people go at night |
| `LIVE` | **18** | no live act anywhere in any source. DJ-driven — and a DJ is not `LIVE` |
| `POL` | **78**, sense **current** | ₹2,000+, *"sophisticated"*, reservations, bouncers, guestlist — but Bollywood/Punjabi and teenagers, so current rather than classy |
| `SCEN` | **74** | terrace, *"wonderful open ambiance"*, *"impressed with the ambiance"* |
| `HERIT` | **10** | a 2017 tapas bar in a hotel. Qutab Institutional Area is a place name, not heritage fabric |
| `GAMES` | **45** | board games exist — **but only at Sunday brunch**. See §5 |

### tags

`outdoor-seating` `terrace` · `reservation-only` `guestlist` `queue-after-10` · `floor`
`table-led-early` · `small-plates` `all-you-can-eat` `late-kitchen` · `dj-nightly`

### admission

| test | result |
|---|---|
| volume ≥ 200 | **pass** — 953 |
| mean ≥ 4.0 | **pass** — 4.1 |
| operator class | **pass** — hotel-attached |
| fit-out ≤ 15 yrs | **pass** — opened ~2017 |
| **spread SD ≤ 0.85** | **cannot be computed** (§4) |

---

# 3. The description, in the app's own voice

> **Bohca** — a tapas bar at Qutub Hotel that is two places. Until the evening it is a terrace
> restaurant with sharing plates and board games on the table. After ten it is one of the loudest
> rooms in South Delhi: a dance floor, a Bollywood-and-Punjabi set, a queue, and a door that turns
> people away. It has been doing both since 2017. Book three days ahead for a weekend, and expect
> to spend two thousand a head before you have had much to eat.

---

# 4. What reviews could not give

**The bands.** Not one of the eight energy and crowd numbers is stated anywhere. They are inferred
from *"massive crowd"*, *"party till late"* and a closing time. **Reviews establish the amplitude
and the direction and never the hour** — which is exactly the gap `VENUE_DATABASE_V1.md` §5.4
identified for images, arriving by a different route. The type curve plus one amplitude is doing
the real work here; the reviews only confirm the amplitude is high.

**The spread, numerically.** 4.1 on Google against **2.9 on TripAdvisor** is a very large platform
gap, and 5 returned reviews cannot measure it.

**But the text reveals the variance even though the number cannot.** *"One of the finest places for
a late night party"* sits in the same corpus as *"puking teenagers, smoky indoors, over smart
bouncers"* and *"variability in service quality"*. **That is a bimodal distribution described in
words.**

> **This is worth acting on.** §1.2 says rating spread is the right admission signal and §5.0 says
> it cannot be computed from free data. **Sentiment variance across the five returned review texts
> may be a usable substitute** — it is the same latent quantity, read from prose instead of stars,
> and five texts is enough to see a split this wide. It would not have been obvious without
> running a real venue through it.

---

# 5. The problem this venue exposes

**`prefs{}` are fixed per venue, and Bohca's `GAMES` is not.** Board games are a Sunday-brunch
thing. A fixed `GAMES` of 45 is wrong at both ends: too high at midnight, far too low at Sunday
lunch.

Three ways out, and the first is already in the document:

1. **Let the hour-scoped type carry it.** `games pub` on Sunday afternoons already implies games;
   the `GAMES` preference then only has to discriminate *within* that type. **Cheapest, and it
   needs no new mechanism.**
2. **Put it in the events table** — the one built for heritage programming and the `FOCUS` clock
   anchor. A recurring Sunday entry is exactly what that table holds.
3. Make `prefs` hour-scoped, which contradicts the user's 2026-10-01 decision and should not be
   done for one case.

**1 and 2 together.** Nothing new is required.

---

# 6. Verdict on the method

| | |
|---|---|
| **character** — what kind of place, for whom, at what price, with what door policy | **reviews are excellent.** Richer than expected |
| **types, including the hour split** | **reviews plus the venue's own posts got it exactly right** |
| **preferences** | **good**, except where a preference is itself time-bound |
| **tags** | **good** — most came from stated service options rather than prose |
| **the bands** | **reviews cannot do this**, and no amount of reading fixes it |
| **the spread** | **the number is unavailable; the text carries it anyway** |

**So reviews are a strong source for everything except the two numbers the skeleton actually
selects on.** Those still need the type curve, an amplitude, and a human with a judgement — which
is what §5.4 concluded, now confirmed on a real venue rather than a simulated one.

---

# 7. Negative reviews are not noise — they are answers to a different question

**The user's correction, 2026-10-02: a complaint about the door is not a criticism of the venue.**
*"The drinks tasted bad"* and *"service was slow"* are real criticism. *"They outcast you based on
your drive"* and *"the club has terrible rules for entry"* are grievances about a policy.

**But the right move is not to filter them out. It is to route them.** A complaint about a strict
door is **evidence that the door is strict**, which is a true and useful attribute. Most "negative"
reviews of a nightlife venue are **accurate descriptions written by somebody who disliked what they
accurately described** — and for an app that matches people to rooms, that is the most valuable
text in the corpus.

| the complaint | what it is actually evidence of | where it goes |
|---|---|---|
| *"too loud, couldn't hear anyone"* | the room is loud | **`ENRG` band up**, not a quality mark |
| *"packed, couldn't move"* | the room fills | **`CROWD` band up** |
| *"over smart bouncers", "terrible rules for entry", "attitude at the door"* | selective door | **`guestlist`, `queue-after-10` tags; `POL` up** |
| *"too expensive for what it is"* | price point | **`priceLevel`** — already a field |
| *"full of teenagers"* | a young crowd | **crowd-age character** |
| *"music was too Bollywood"* | the music policy | **a programming tag**, not a fault |
| *"smoky indoors"* | ventilation and smoking | **a real venue criticism** |
| *"the drinks were badly made"* | execution | **real — feeds quality and admission** |
| *"service was slow / inattentive"* | execution | **real — feeds quality and admission** |

**Only the last three rows belong in the quality signal.** The first six are tags and bands wearing
a one-star rating.

### What this does to Bohca's numbers

Re-reading the corpus with the routing applied: **a substantial share of Bohca's negative volume is
door policy and crowd composition, not execution.** Its quality signal is better than its raw
rating implies, and its *character* signal is far richer than a rating could ever be.

**And it sharpens §4's idea rather than killing it.** Sentiment variance can still substitute for
the missing rating spread — but only **after routing**. Variance in *execution* complaints is the
consistency signal admission wants. Variance in *door* complaints is just evidence of a door, and
counting it as inconsistency would penalise exactly the selective, well-run venues the admission
filter is trying to find.

> **So: route first, then measure variance on what is left.** Without the routing step the spread
> substitute would have had its sign backwards on precisely the venues that matter most.

---

# 8. The crowd's vibe — not the venue's

**A venue has no vibe factors.** `FACTORS_V6.md` §0 is explicit and this does not change it. But
**the people in it do**, and that is a real thing the app shows: screen 17's *"who goes here"*
donut. Normally it is computed from users who actually went. Before there are users, it can be
estimated from the same reviews — a **cold start**, to be replaced by real data as soon as there is
any.

### Bohca, after 22:00, as the reviews describe its crowd

| | | the evidence |
|---|---|---|
| `ENRG` | **85** | *"party till late"*, *"energetic crowd"*, a 1am close, queues |
| `MOVE` | **80** | *"joining the energetic crowd on the dance floor"* — the floor is the point |
| `AFFIL` | **68** | reservations three days ahead, tables, sharing plates, birthdays — **you come with your people and you hold a table** |
| `SPONT` | **22** | reservations required, guestlist, booking ahead. **Nobody arrives at Bohca on a whim** |
| `TALK` | **25** | loud music, a floor, complaints about noise and smoke |
| `FOCUS` | **25** | a DJ, not a performance. Nobody is pointed at anything |

**The name that falls out:** `|s−50|` gives `ENRG` 35, `MOVE` 30, `SPONT` 28, `TALK` 25, `FOCUS` 25,
`AFFIL` 18. First factor `ENRG` high; second within 15 and clearing `SECOND_MIN` is `MOVE` high.

> ### Peak Floor-Filler

**Which is a sentence about the people, and it reads true.** A room of Peak Floor-Fillers is what
the reviews describe from both directions — the ones who loved it and the ones who did not.

### Two caveats, and the second one matters

**This is one hour of one kind of night.** The Sunday brunch crowd at 2pm — board games, terrace,
sharing plates — is close to the opposite: low `ENRG`, low `MOVE`, high `TALK`, high `AFFIL`.
**The crowd's vibe is hour-scoped exactly as the types and bands are**, and *"who goes here"* should
be read at the hour the stop falls, not as one figure for the venue.

**And this is a cold start, not a measurement.** The honest version of this chart comes from users
who locked a plan containing Bohca and had their vibe that day. **Estimating it from reviews is
how the chart is non-empty on day one**, and it should be visibly replaced — not blended — once
there are twenty real readings.

---

# 9. Quora, tested — and what it is actually for

**Searched 2026-10-02 for Bohca and for Delhi nightlife generally. Verdict: low value for tagging,
one high-value finding.**

**Why it is poor for this.** The corpus is **7 to 13 years old** — the most recent substantial
thread is three years back, and the venues named across the top answers (Lap, Jynxx, Shroom,
Raasta) include several that have since closed. **And the format is wrong**: Quora answers *"where
should I go?"* with a **list of names**, where tagging needs *"what was it like?"* with a
description. A recommendation corpus, not an experience corpus.

> **Reviews describe. Quora recommends.** For building a venue row, only the first is useful — and
> this is a clean statement of which sources are worth the integration effort.

**The one thing it gave, which nothing else did.** Across a decade and dozens of threads, the
dominant recurring question is not music, price or food. It is **the door** — *"stag entry"*,
*"free for girls"*, *"especially for stag entry"*, *"couple entry"*. A topic that persistent across
that long a span is structural, not incidental.

**That produced `VENUE_DATABASE_V1.md` §2a4: the door is a hard gate and the engine does not model
it.** A group of four men can be refused where a mixed four walks in, and a plan routed to a venue
the room cannot enter is the worst failure the app has — the night simply stops.

**It is worth noting how that arrived.** Quora was useless for the question asked of it, and the
uselessness itself was the signal: when a decade of people keep asking the same question, that
question is a field you are missing.

One other structural fact worth keeping: *"Delhi generally closes down by around 2 am."* That is
the ceiling on every skeleton drawn in this city.

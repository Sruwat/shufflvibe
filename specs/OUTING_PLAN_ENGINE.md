# Outing Plan Engine — Backend Specification

> **2026-09-17 — the factor set is split. Read §14 first.** Seven vibe factors (`ENRG` `AFFIL`
> `CROWD` `TALK` `ROAM` `MOVE` `GAMES`) give the shape of the night and the venue type at each
> stop; six preferences (`FOOD` `LIVE` `POL` `SCEN` `NOV` `HERIT`) pick the exact venue of that
> type and never alter it. §5–§13 are the history and the machinery; §14 says how each part now
> reads. `FACTORS_V5.md` defines the set. Wherever §5–§13 say "factor" without qualification,
> read "vibe factor".

**Audience:** a backend engineer joining SHUFFL with no prior context on this system.
**Companion docs:** `VIEW_FLOW.md` (product flows), `FACTORS_AND_VIBES_V4.md` (factor definitions, weights, and the 42 vibes), `BLEND_STYLE_DATABASE_V2.md` (the 24 blend styles), `ASSESSMENT_ENGINE.md` (how one session of cards becomes a profile), `PREFERENCE_ENGINE.md` (how that profile is refined over weeks).

---

# 0. What this system does

A user taps **"Create Plan"**. Within a few seconds the app returns an ordered night out — typically two or three venues with times, travel between them, and copy explaining why each stop suits the group.

Three subsystems:

| | Runs | Job |
|---|---|---|
| **Venue Intelligence** | offline, scheduled | Builds and maintains the venue database — every venue scored against ten behavioural factors, with a confidence level |
| **Availability Confidence** | offline precompute + live top-up | Estimates the risk a group gets turned away at a given venue, time and party size |
| **Plan Generation** | online, per request | Turns a group's mood into a validated, ordered, *reachable and enterable* plan |

The two offline systems write to tables the online path reads. **Plan Generation must complete in under ~3.5 seconds.**

There is no reservation integration and none is planned. SHUFFL does not book tables; it avoids recommending venues you probably can't get into. §1.5 and §4 explain how.

---

# 1. Domain concepts

You need five ideas before the rest makes sense.

### 1.1 Factors

Everything in SHUFFL — users, venues, plans — is described by the same **ten-dimensional vector**, scored 0–100. These are defined in `FACTORS_AND_VIBES_V4.md`:

| Code | Meaning | Penalty | Weight |
|---|---|---|---|
| `CROWD` | How many people you want around you | both ways | 15% |
| `ENRG` | How much movement and intensity | both ways | 12% |
| `SCEN` | How much the look of the place matters | shortfall only | 12% |
| `FOOD` | How much the food itself is the point | shortfall only | 14% |
| `POL` | How dressed-up and polished | both ways | 13% |
| `NOV` | How much you want somewhere new | both ways | 8% |
| `PLAY` | How much you want something to actually do | both ways | 7% |
| `LIVE` | How much a performance is the reason | both ways | 6% |
| `HERIT` | How much you want somewhere old | shortfall only | 5% |
| `AFFIL` | Facing the room, or facing your own table | both ways | 8% |

`FACTORS_AND_VIBES_V4.md` is the source of truth for the codes, meanings and weights.

**The penalty column is not decoration.** *Shortfall only* factors are `PASSIVE` — too much of
one costs nothing, because nobody is harmed by excellent food they did not ask for. *Both ways*
factors are `PARTICIPATORY`: the night does them to you, and you cannot ignore being at a bowling
alley when you came to talk. §5.3 implements this and the asymmetry is deliberate.

> **`PLAY` and `LIVE` were disputed; settled 2026-09-10 in favour of this file.**
> `FACTORS_AND_VIBES_V4.md` had both as shortfall-only, which would have made an unwanted band
> or an unwanted pool table free. They are participatory: a game you did not ask for still takes
> the table, and a band too loud to talk over still ends the conversation. `PASSIVE` stays at
> exactly `('SCEN', 'FOOD', 'HERIT')` — the three you can leave alone. V4 has been corrected.

### 1.1.1 The factor set changed — reading older documents

Earlier drafts, and any code or doc still carrying them, use a set two generations stale. The
mapping, for anyone reading back:

| Old | Now | |
|---|---|---|
| `SOC` | `CROWD` | straight rename |
| `SOFT` | `SCEN` | same idea, renamed |
| `PREM` | `POL` | same idea, renamed |
| `CULT` | `LIVE` + `HERIT` | split — music and history turned out to be different appetites |
| `PLAY` | `ENRG` + `PLAY` | split — how intense the night is, versus having something to do |
| `CAS`, `FUN` | *gone* | no successor — see the caveat below |
| `VALUE` | *gone* | spend is a manual budget input and a filter, not a preference axis |
| `CONV` | *gone* | distance is a filter, not a preference axis |

Only the `SOC` → `CROWD` row is recorded in `DECISIONS.md`. The rest were reconstructed by
matching definitions across the two factor tables, and the `CAS` / `FUN` row is the weakest of
them — those two were dropped rather than renamed, and no entry says what replaced them. Treat
that row as an explanation, not a history.

`AFFIL` is new and has no predecessor. It is why `SOC` could not keep its name: with `AFFIL` in
the set, "social" read as though it covered orientation too. `CROWD` is headcount; `AFFIL` is
which of those people you are there for.

**`VALUE` and `CONV` are retired as factors, not as concerns.** Budget and travel still constrain
every plan — they are handled by the manual duration/budget inputs and the distance filter (§4),
which is a hard constraint rather than something a match score trades away.

### 1.2 Vibe

A **vibe** is a named point in that 10-D space — a personality archetype like *The Menu-Mood Maker* or *The Low-Key Loyalist*. There are 42, listed with their vectors in `FACTORS_AND_VIBES_V4.md`. Each user is assigned one vibe per day by the swipe game (see `PREFERENCE_ENGINE.md`). You consume the vibe's **vector**, not its name.

### 1.3 Blend style

When several users are in a room together, their vibes combine into a **blend style** — a named group mood with its own vector. Blend styles are what plans are generated for when a group is involved. For a solo user, the blend style is just their own vibe.

### 1.4 Why this isn't a normal recommender

A typical recommender ranks items independently and returns a top-N list. **A plan is a validated sequence.** It must satisfy conditions no ranking function can express:

- every venue must be **open at the projected arrival time**
- each stop must be **reachable** from the one before within the plan's timing
- total spend must fit the group's budget
- the night needs a coherent **arc** — a plan that ends with a quiet cafe after a club is wrong even if both venues score well
- in a group, **every stop** needs something for **every member** — served on a factor they ranked, not just once across the night (§6, §13.4)

Rank three venues independently and you will eventually ship a plan whose second stop closed an hour before arrival. Treat this as constraint satisfaction with a ranking step inside it, not as search.

### 1.5 Arrival risk

The sixth constraint, and the one that needs its own machinery: **a venue that is open, affordable and perfectly matched is still useless if the group can't get in.**

No API answers *"is this restaurant full right now."* Even a full reservation integration wouldn't — a venue with 20 tables might list 5 on one booking platform, 5 on another, and hold 10 for walk-ins. Nobody sees true state.

So the system does not model availability. It models **arrival risk**:

> For a group of size **N** arriving at venue **V** at time **T**, what is the probability they are seated within an acceptable wait — and how much do we trust that number?

Two outputs, always kept separate:

| | |
|---|---|
| `p_seat` | 0–1, probability of being seated acceptably |
| `confidence` | 0–1, how much evidence stands behind `p_seat` |

`p_seat = 0.7` with high confidence and `p_seat = 0.7` with low confidence are completely different decisions. Collapsing them into one number is the central mistake to avoid — exactly as with venue factor scores (§3.5).

**The error asymmetry matters here.** Sending a group into a 45-minute queue costs trust that takes months to rebuild. Skipping an available venue costs nothing — there are thousands of alternatives and the user never learns what they missed. This system therefore optimises **precision over recall**. When uncertain, exclude.

---

# 2. Data model

Postgres-shaped. Adapt as needed; the fields matter more than the DDL.

### 2.1 Venue facts

```sql
venues (
  venue_id          uuid primary key,
  name              text not null,
  city              text not null,
  lat               double precision not null,
  lng               double precision not null,
  google_place_id   text unique,
  category          text not null,        -- cafe | bar | restaurant | rooftop | club | activity
  price_band        smallint not null,    -- 1 = ₹, 2 = ₹₹, 3 = ₹₹₹
  opening_hours     jsonb not null,       -- { "mon": [["18:00","01:00"]], ... }
  capacity_band     smallint,             -- max comfortable group size
  requires_booking  boolean default false,
  serves_alcohol    boolean,
  serves_food       boolean,
  outdoor_seating   boolean,
  status            text default 'active',-- active | closed | unverified
  last_verified_at  timestamptz,
  updated_at        timestamptz
);
create index on venues using gist (ll_to_earth(lat, lng));
create index on venues (city, category, price_band) where status = 'active';
```

**These are gates, not scores.** Never fold opening hours or price into a similarity calculation.

### 2.2 Venue factor scores

**Venues never carry a vibe.** Vibes describe people; venues carry a factor vector. Matching is vector-to-vector — there is no venue-to-vibe mapping anywhere in this system, and adding one would be a design error.

One row per venue **per day part** per factor.

```sql
venue_scores (
  venue_id      uuid references venues,
  day_part      text,          -- morning | afternoon | evening | late
  week_part     text,          -- weekday | weekend | all
  factor        text,          -- CROWD | ENRG | ... | AFFIL
  raw_score     real,          -- 0..100, weighted evidence sum
  percentile    real,          -- 0..100, rank within city for this factor + day_part
  confidence    real,          -- 0..1
  final_score   real,          -- confidence-shrunk percentile — USE THIS for matching
  computed_at   timestamptz,
  primary key (venue_id, day_part, week_part, factor)
);
```

**Why `day_part` is in the key.** A venue's character genuinely changes through the day. A rooftop cafe might score `SCEN 88 · FOOD 70 · ENRG 25` at 11am and `SCEN 92 · FOOD 55 · ENRG 70` at 9pm. Score it once and you average two different venues into one that serves neither — then recommend a brunch spot for a date night.

`week_part` exists for the same reason and matters in Delhi nightlife. **Phase 1 may write `week_part = 'all'`** and defer the split; having the column present makes adding it later a backfill rather than a migration.

Ranking always reads `final_score` **at the day part the stop is scheduled for**. The other columns exist for debugging and the learning loop.

### 2.3 Evidence

```sql
venue_evidence (
  venue_id          uuid,
  evidence_type     text,     -- review_text | photos | attributes | menu | behavioural | own_visits
  factor            text,
  signal            real,     -- 0..100, this evidence type's opinion
  n_samples         int,      -- reviews read, photos analysed, visits recorded
  median_sample_age_days int,
  computed_at       timestamptz,
  primary key (venue_id, evidence_type, factor)
);
```

### 2.4 Templates

```sql
plan_templates (
  template_id       uuid primary key,
  name              text,                -- "Golden Hour Slow Burn"
  blend_styles      text[],              -- which blend styles trigger it
  time_of_day       text,                -- morning | afternoon | evening | late
  min_duration_min  int, max_duration_min int,
  min_group         int, max_group        int,
  budget_bands      smallint[],
  arc               text[],              -- ['warm','intimate','wind_down']
  active            boolean default true
);

template_slots (
  template_id       uuid references plan_templates,
  slot_index        smallint,
  categories        text[],              -- acceptable venue categories
  duration_min      int,
  price_band        smallint,
  emphasis          jsonb,               -- {"SCEN":0.5,"POL":0.3} — factor boosts for this slot
  optional          boolean default false,
  primary key (template_id, slot_index)
);
```

### 2.5 Plans and feedback

```sql
plans (
  plan_id        uuid primary key,
  room_id        uuid,          -- null for solo
  creator_id     uuid not null,
  template_id    uuid,
  member_ids     uuid[],
  group_vector   real[10],
  status         text,          -- draft | locked | active | completed | abandoned
  created_at     timestamptz,
  locked_at      timestamptz,
  regenerated_count int default 0
);

plan_stops (
  plan_id        uuid references plans,
  stop_index     smallint,
  venue_id       uuid references venues,
  planned_arrival timestamptz,
  planned_duration_min int,
  availability_tier text,       -- safe | hedge — tier at time of generation
  arrived_at     timestamptz,   -- set by geofence
  dwell_minutes  int,           -- set by geofence exit
  rating         smallint,      -- 1..5, post-outing
  primary key (plan_id, stop_index)
);
```

`regenerated_count` matters — see §7.

### 2.6 Availability

```sql
venue_availability (
  venue_id      uuid references venues,
  day_part      text,
  hour_bucket   smallint,      -- 0..23
  week_part     text,          -- weekday | weekend
  group_band    smallint,      -- 1: 1-2, 2: 3-4, 3: 5-8, 4: 9+
  p_seat        real,          -- 0..1
  confidence    real,          -- 0..1
  tier          text,          -- safe | hedge | exclude | unknown
  contributing  jsonb,         -- per-source {p, sigma, n} — keep this, see §7
  computed_at   timestamptz,
  primary key (venue_id, day_part, hour_bucket, week_part, group_band)
);

venue_arrival_events (
  venue_id      uuid,
  user_id       uuid,
  plan_id       uuid,
  arrived_at    timestamptz,
  dwell_minutes int,
  group_size    smallint,
  outcome       text,          -- seated | bounced | ambiguous
  primary key (venue_id, user_id, arrived_at)
);
```

**`venue_arrival_events` feeds two systems.** It is `own_visits` evidence for factor scoring (§3.2) *and* the `seated`/`bounced` signal for availability (§4.1). One piece of instrumentation, two payoffs — build it once, early.

Keep `contributing` populated. When a plan goes wrong you need to see *which source was confident and wrong*, and that is the input to recalibration.

---

# 3. Venue Intelligence — the offline pipeline

Runs on a schedule. Nothing here is in the request path.

### 3.1 Ingest facts

Pull venues per city from Google Places, backfilling POI coverage from Foursquare/OSM. Write to `venues`. Refresh weekly; refresh opening hours and `status` more aggressively, because stale hours cause the worst user-visible failures.

### 3.2 Extract evidence

Six evidence types, each producing a 0–100 signal per factor:

| Type | Source | Best at |
|---|---|---|
| `review_text` | Google/Zomato review corpus → LLM extraction | CROWD, FOOD, LIVE, HERIT, POL |
| `photos` | venue + user photos → vision model | **SCEN**, POL, CROWD |
| `attributes` | price level, category, hours → rules | POL, FOOD, PLAY, HERIT |
| `menu` | menu extraction | FOOD, POL |
| `behavioural` | photo-to-review ratio, review velocity, popular-times curve | CROWD, ENRG, SCEN, NOV |
| `own_visits` | our own post-outing ratings | **all — this is ground truth** |

`behavioural` deserves a note: **photo-to-review ratio is a strong, free proxy for "photogenic."** A venue with 0.44 photos per review against a city median of 0.15 is visually striking. Classifying photo *subject* (room vs food vs people) separates a Pretty-Place venue from a Menu-Mood venue using the same photo set.

Do **not** scrape Instagram or any social platform. Beyond ToS and legal exposure, SHUFFL licenses data commercially and enterprise buyers audit provenance.

### 3.3 Combine into a raw score — per day part

Everything from here runs **once per day part**, not once per venue.

```python
for day_part in ('morning', 'afternoon', 'evening', 'late'):
    ev = evidence_for(venue, day_part)     # see partitioning note below
    raw[day_part][f] = sum(W[e][f] * ev[e][f] for e in EVIDENCE_TYPES if present) \
                     / sum(W[e][f]            for e in EVIDENCE_TYPES if present)
```

`W` is a 6×10 weight matrix, hand-initialised and later learned (§7). Renormalise over *present* evidence types so venues missing a source aren't penalised twice.

**Partitioning evidence by day part.** Most sources carry a usable timestamp or hint:

| Evidence | How to partition |
|---|---|
| `review_text` | review timestamp; also extract explicit mentions ("great for brunch", "gets loud after 10") |
| `photos` | EXIF time where present; otherwise infer from image brightness and lighting colour |
| `behavioural` | popular-times curves are already per-hour — the cleanest signal here |
| `own_visits` | exact arrival timestamp from geofence. Best partitioning available. |
| `attributes`, `menu` | not time-varying — apply to all day parts |

Where a venue has too little evidence to partition, **write the same vector to every day part and let confidence carry the uncertainty.** Do not invent variation you can't observe.

### 3.4 Normalise to percentile

```python
percentile[f] = percentile_rank(raw[f], all_active_venues_in_city[day_part][f])
```

Percentile within the **same city and same day part** — a venue is compared against its actual competition at that hour, not against the whole week. Raw scores aren't comparable across cities or factors; percentiles are, and ranking is inherently comparative.

### 3.5 Confidence

```python
volume    = min(1.0, log(1 + n_total) / log(1 + 50))
agreement = clamp(1.0 - stdev(signals_across_types) / 40.0, 0.0, 1.0)
recency   = exp(-median_sample_age_days / 730.0)

confidence = volume * agreement * recency
```

- **volume** saturates — 400 reviews isn't twice as trustworthy as 200.
- **agreement** is the important one. If photos say "romantic" and reviews say "sports bar," you don't know what this venue is, and confidence should collapse.
- **recency** decays over ~2 years; venues change hands.

**Override:** once `own_visits.n_samples >= 20`, set `confidence = max(confidence, 0.95)` and weight `own_visits` at 0.6 in §3.3. First-hand data beats everything.

### 3.6 Shrink toward the category mean

```python
final_score[f] = confidence * percentile[f]
               + (1 - confidence) * category_median_percentile[category][f]
```

This is why an unproven venue can't win a slot on an unverified extreme. A place claiming 94 on SCEN with twelve reviews lands near 70 after shrinkage; a place claiming 88 with 400 reviews stays at 85.

### 3.7 Cold start

A new venue inherits its category median at `confidence ≈ 0.05`, so it will never rank. To break the deadlock, **~1 plan in 15 must include one low-confidence venue** that otherwise passes all hard filters (§5.2). That plan's feedback is worth far more than another rating for a well-understood venue, and it doubles as the novelty users want.

---

# 4. Availability Confidence — offline precompute + live top-up

Produces `venue_availability` (§2.6). Five signals, fused into `p_seat` and `confidence`, then bucketed into a tier the planner can act on.

### 4.1 The five signals

**1 · Own arrivals — strongest, and free.** You already run geofence detection for referral attribution and the arrival prompt. That same data answers this question, and **no competitor has it**.

The key trick is dwell time. A user who arrives and leaves within ~8 minutes almost certainly didn't get a table — that's a direct observation of unavailability:

```python
seated  = arrivals where dwell_minutes >= 20
bounced = arrivals where dwell_minutes <= 8
p_seat_own = seated / (seated + bounced)      # requires n >= 3 to contribute
```

**2 · Venue-reported status.** A capacity toggle in the SHUFFL Business dashboard — *comfortable / filling up / full tonight*. Ground truth when fresh, worthless when stale.

```python
p_seat_venue = {'comfortable': 0.95, 'filling': 0.55, 'full': 0.05}[status]
```
Full weight under 2h old, halved by 6h, discarded past 12h.

**3 · Live busyness.** A licensed busyness API. **Do not scrape Google** — beyond ToS, scraped data in the pipeline becomes a problem in a data-licensing diligence review, not just a code review.

```python
p_seat_live = clamp(1.0 - (busy_pct / 100) ** 1.6 * capacity_pressure(N, cap), 0.02, 0.98)
```
The exponent above 1 is deliberate: 60% busy is usually fine, 95% is effectively closed to walk-ins. The relationship is not linear.

**4 · Typical busyness.** Same API's historical curve for that weekday and hour. Weaker, but always present and **cacheable daily** — this is the workhorse covering venues with no other data.

**5 · Structural prior.** Capacity band, category, price band, weekday, hour, hotspot flag. Always available, always weak. Its job is to stop the system returning nothing.

### 4.2 Fusion

Each source returns `(p_i, σ_i)`. Combine by **inverse-variance weighting** — the standard method for merging estimates of differing reliability.

```python
SIGMA = {
    'own_visits_high':  0.10,   # n >= 10 at this venue + day_part + group band
    'own_visits_low':   0.20,   # 3 <= n < 10
    'venue_fresh':      0.08,   # reported < 2h ago
    'venue_stale':      0.25,   # 2-12h
    'live_busy':        0.18,
    'typical_busy':     0.28,
    'structural':       0.40,
}

def fuse(estimates):                        # [(p, sigma), ...]
    if not estimates:
        return 0.5, 0.0
    precision = sum(1 / s**2 for _, s in estimates)
    p_hat     = sum(p / s**2 for p, s in estimates) / precision

    spread    = weighted_stdev([p for p, _ in estimates],
                               [1 / s**2 for _, s in estimates])
    agreement = clamp(1 - spread / 0.30, 0.0, 1.0)

    confidence = (precision / (precision + 25)) * agreement
    return p_hat, clamp(confidence, 0.0, 1.0)
```

Three properties:

- **Missing sources cost nothing structurally** — they add no precision, which correctly lowers confidence rather than skewing the estimate.
- **Disagreement collapses confidence.** If own-arrivals say "always fine" and live busyness says "packed," you genuinely don't know. The system must say so rather than average them into a confident-looking 0.6.
- **`+25`** sets how much total precision counts as well-evidenced. Tune against observed outcomes (§7).

### 4.3 Group size

Availability for two is not availability for eight. Condition everywhere:

```python
def capacity_pressure(group_size, capacity_band):
    ratio = group_size / max(capacity_band or 6, 1)
    return 1.0 + 1.8 * max(0, ratio - 0.25)
```

A party of 8 at a small cafe is near-impossible even when it's half empty — a frequent real-world failure that pure busyness data misses entirely.

### 4.4 Tiers

**Three tiers, not a binary gate.** Binary include/exclude discards good venues on weak data.

| Tier | Condition | Planner behaviour |
|---|---|---|
| **SAFE** | `p_seat ≥ 0.75` and `confidence ≥ 0.55` | Recommend normally |
| **HEDGE** | `p_seat ≥ 0.55`, or high `p_seat` with low confidence | Recommend; plan card carries *"gets busy — worth calling ahead"* |
| **EXCLUDE** | `p_seat < 0.55` at `confidence ≥ 0.4` | Not offered at this slot |
| **UNKNOWN** | `confidence < 0.25` | Treat as HEDGE; prefer a SAFE alternative if one exists |

Two hard rules on top, enforced in §5.3:

- **At most one HEDGE stop per plan.** A three-stop night where every venue "might be busy" is a warning list, not a plan.
- **Never HEDGE the first stop.** A queue at 7pm poisons the whole evening. First stop is SAFE or the plan is rebuilt.

### 4.5 Precompute schedule

| Data | TTL | When |
|---|---|---|
| Typical busyness curve | 24h | nightly, all venues |
| Structural prior | 7d | weekly |
| Own-arrival aggregates | 1h | rolling |
| Venue-reported status | until changed | on write |
| **Live busyness** | **10 min** | **on demand, shortlist only** |

Everything except live busyness is precomputed into `venue_availability`. Only live busyness makes a request-time call, and only for venues that reach the shortlist (§5.3).

---

# 5. Plan Generation — the request path

**Endpoint:** `POST /plans/generate`

```json
{
  "creator_id": "uuid",
  "room_id": "uuid | null",
  "member_ids": ["uuid"],
  "start_time": "2026-08-24T18:30:00+05:30",
  "duration_min": 240,
  "budget_band": 2,
  "origin": { "lat": 28.55, "lng": 77.19 }
}
```

Four stages. **Latency budget: ~3.5s total.**

### 5.1 Stage 1 — select template *(target <5ms)*

Resolve the blend style for `member_ids`, then:

```sql
select * from plan_templates
where active
  and blend_style = any(blend_styles)
  and time_of_day = :derived_from_start_time
  and :duration_min between min_duration_min and max_duration_min
  and :group_size between min_group and max_group
  and :budget_band = any(budget_bands)
order by random()
limit 1;
```

A DB lookup, not a model call. If several match, prefer ones the group hasn't seen recently.

**Templates are a curated asset, not generated.** They encode the arc of a night — which is authored taste, and the thing that most distinguishes a good plan from three well-ranked venues. Target 40–60 covering blend style × occasion × time of day.

### 5.2 Stage 2 — hard filter *(target <50ms)*

For each slot, compute a projected arrival time by accumulating previous slot durations plus estimated travel, then filter:

```sql
select v.venue_id
from venues v
where v.status = 'active'
  and v.city = :city
  and v.category = any(:slot_categories)
  and v.price_band <= :slot_price_band
  and is_open_at(v.opening_hours, :projected_arrival)      -- CRITICAL
  and earth_distance(...) <= :max_radius_m
  and (v.capacity_band is null or v.capacity_band >= :group_size)
  and v.venue_id <> all(:recently_seen_by_group)
  and v.venue_id <> all(:user_avoided);
```

These are **binary**. A closed venue is not a lower-ranked option; it is not an option.

**Relaxation ladder** if fewer than 5 candidates survive — in this order, never skipping:
1. widen radius by 50%
2. allow one price band higher
3. shorten the novelty cooldown
4. drop an optional slot
5. fall back to a shorter template

Never relax opening hours.

### 5.3 Stage 3 — score and sequence *(target <150ms)*

**Per-candidate match.** Matching compares the user or group's factor vector against the venue's factor vector at the relevant day part. **Distance is deliberately asymmetric** — a mismatch does not cost the same in both directions, and treating it symmetrically produces unexplained mediocre plans that are very hard to debug.

```python
# PASSIVE factors are qualities of a room you can leave alone. Only a shortfall
# hurts — someone who did not prioritise food is not harmed by excellent food.
PASSIVE = ('SCEN', 'FOOD', 'HERIT')

# Everything else is PARTICIPATORY: the night does it TO you, so both directions
# hurt. You can ignore good food; you cannot ignore being at a bowling alley when
# you came to talk, or a band loud enough that you cannot hear each other.
PARTICIPATORY = ('CROWD', 'ENRG', 'POL', 'NOV', 'PLAY', 'LIVE', 'AFFIL')

BEND_TIER = {'A': 0.03,   # physically incompatible
             'B': 0.12,   # something this vibe actively avoids
             'C': 0.25}   # a strong preference
BEND_FLOOR   = 0.40       # unflagged, approach-only
BEND_USER_K  = 1.2        # how far a user's own firmness widens their vibe's bend

def firmness(user_vector, f):
    return abs(user_vector[f] - 50) / 50

def bend_up(vibe, f):
    """How much MORE of f this vibe can absorb."""
    if f in PASSIVE:
        return 1.00                                   # excess of a passive factor is free
    flag = BEND_FLAGS.get(vibe, {}).get(f)
    return BEND_TIER[flag] if flag else max(BEND_FLOOR, vibe.scores[f] / 100)

def bend_down(vibe, f):
    """How much LESS of f this vibe can absorb.

    Derived from the score alone. Do NOT add a second scaler here for how
    central f is to the vibe — that was tried and reverted. Centrality is
    |score - 50|, which is the same quantity as the user firmness applied in
    user_bend() one line later; the two correlate +0.82, and multiplying them
    drove 42% of factors to a fully open limit, i.e. the model saying nothing
    at all about them. The firmness term already separates a defining factor
    from an incidentally high one, because a user's own score on a peripheral
    factor is naturally closer to 50."""
    x = vibe.scores[f]
    if x < 50:
        return max(BEND_FLOOR, (100 - x) / 100)
    return (100 - x) / 100

def user_bend(vibe, user_vector, f, direction):
    """The vibe knows what the night requires; the user's own firmness says
    whether THEY hold it. Both terms are needed — firmness alone reports that a
    Warehouse Head will happily accept a dead bar."""
    base = bend_up(vibe, f) if direction == 'up' else bend_down(vibe, f)
    return min(1.0, base * (1 + BEND_USER_K * (1 - firmness(user_vector, f))))

def factor_penalty(f, user_vector, venue_val, vibe):
    """Bend is a COST MULTIPLIER, never a gate. Enforced as a gate it produced
    absurd exclusions — a romantic vibe blocked from a quiet wine bar."""
    d = venue_val - user_vector[f]
    if d == 0:
        return 0.0
    if f in PASSIVE and d > 0:
        return 0.0                                    # overshoot on a passive factor is free
    b = user_bend(vibe, user_vector, f, 'up' if d > 0 else 'down')
    return abs(d) * (0.5 / max(b, 0.05))
```

**On `bend_down`, and a fix that was tried and reverted.** The upward direction carries roughly 40 hand-authored flags; the downward direction has none and is derived from the score alone. That looks like an asymmetry worth correcting, and a centrality scaler was added to correct it — allowance widened in proportion to how far a factor sits from being the vibe's most extreme one. **It was reverted, and the reason is worth recording so it is not re-proposed.**

Centrality is `|score - 50|`. So is user firmness. They are the same quantity computed on two vectors that are close *by construction*, because a user is matched to their nearest vibe. Measured across 25,000 user-factor pairs the two loosening terms correlate **+0.82**, and applying both multiplicatively drove **42% of factors to a fully open limit** — the model declining to say anything about nearly half of what it measures.

The diagnosis was also methodologically wrong. The problem was identified by examining the vibe bend *in isolation*, ignoring that `user_bend()` applies the firmness term immediately afterwards. Scored on eleven cases — six where a shortfall must hurt, five where it must not:

| Rule | Score |
|---|---|
| vibe bend alone (how it was wrongly tested) | 8 / 11 |
| **vibe bend + user firmness — the system as it already stood** | **9 / 11** |
| plus the centrality scaler | 10 / 11, at 42% of factors fully open |

The single case the scaler won is `Group Hype Friend` at `PLAY` 71 against a nightclub — **a vibe-scoring problem, not a bend problem.** 71 overstates what "hyping the group" wants; dancing is not play in the escape-room sense. Fix the score, not the rule.

**A caution about measuring this at all.** "Shortfalls account for 64% of breaches" was the symptom that prompted the work, but volume is the wrong metric: venues are specialised, so most factors at most venues sit below most users, and a shortfall-dominant profile is expected rather than faulty. Judge changes here on the must-hurt / must-not-hurt cases, never on breach counts.

**Open, and related.** `priority_weights` also scales with firmness, and the cost function multiplies that weight by `1/bend`, which scales with firmness again. That is a second place the same signal is applied twice. It is arguably legitimate — "counts for more" and "has less slack" are genuinely different effects — but it has not been tested, and it is the same shape as the error above.

def match(user_vector, venue_scores_at_daypart, slot_emphasis):
    base = priority_weights(user_vector)          # §5.3.1 — per-user, not global
    num = den = 0.0
    for f in FACTORS:
        w = base[f] * (1 + slot_emphasis.get(f, 0))
        num += w * (1 - factor_penalty(f, user_vector[f], venue_scores_at_daypart[f]) / 100)
        den += w
    return num / den

score = match(group_vector, venue, slot.emphasis) \
      + 0.05 * popularity_norm \
      + 0.05 * novelty_bonus \
      - 0.10 * travel_penalty
```

**Why each rule is shaped that way:**

| Factors | Rule | Reasoning |
|---|---|---|
| `SCEN` `FOOD` `HERIT` | shortfall only | Qualities of a room you can leave alone. Wanted good food, got mediocre → disappointed. Didn't care about food, got excellent → fine. |
| `CROWD` `ENRG` `POL` `NOV` `PLAY` `LIVE` `AFFIL` | both directions | The night does these **to** you. Wanting quiet and getting a packed room is bad; wanting energy and getting an empty room is equally bad. `PLAY` and `LIVE` moved here on 2026-09-03 — you can ignore excellent food, but not an escape room you did not ask for. |

Symmetric distance would reject a lovely venue for a user who simply was not prioritising prettiness. But shortfall-only is wrong for anything the night imposes on you: under the old classification every quiet, conversation-led vibe was structurally unprotected against exactly the venues that ruin its night.

### 5.3.1 Priority weights — per-user, not global

`FACTOR_WEIGHTS` describes the *average* Delhi user: `CROWD` 15%, `FOOD` 14%, `POL` 13%, `ENRG` 12%, `SCEN` 12%, `NOV` 8%, `AFFIL` 8%, `PLAY` 7%, `LIVE` 6%, `HERIT` 5%. Applied unchanged to everyone, a person whose night rests on a low-weighted factor is scored mostly on factors they do not care about. A Front-Row Regular scoring `LIVE` 88 has live music counted at **6%** — the same weight as someone who never goes to gigs.

**Weights are derived per user, from that user's own vector — not from their assigned vibe.** This was previously ambiguous: the section was titled "per-vibe" while the function took `user_vector`. Per-user is correct. The vibe is the nearest archetype, not the person; a user can sit 70 points from their own vibe and still be planned for as themselves. Deriving from the vibe would discard exactly the individual detail the swipe game was built to capture.

Priorities are **derived, never hand-authored**. Hand-tuning weight sets per vibe would be hundreds more numbers to maintain and would drift out of step with the vibe definitions within months. **A user's extremes already are their priorities.**

```python
PRIORITY_ALPHA = 0.35        # 0 = global weights, 1 = pure salience. Tune on feedback.

def salience(user_vector, f):
    """How much THIS USER cares about factor f.
    Direction mirrors factor_penalty: the passive factors earn priority on the
    high side only, because low FOOD means 'doesn't care', not 'rejects food'.
    Participatory factors earn it both ways — CROWD 25 genuinely means 'no crowds',
    and PLAY 12 genuinely means 'do not make me do an activity'."""
    d = user_vector[f] - 50
    if f in PASSIVE:                      # SCEN, FOOD, HERIT
        return max(0, d) / 50
    return abs(d) / 50

def priority_weights(user_vector, alpha=PRIORITY_ALPHA):
    sal   = {f: salience(user_vector, f) for f in FACTORS}
    total = sum(sal.values()) or 1.0
    w     = {f: (1 - alpha) * FACTOR_WEIGHTS[f] + alpha * (sal[f] / total)
             for f in FACTORS}
    s = sum(w.values())
    return {f: w[f] / s for f in FACTORS}       # normalised once, here
```

**The blend must be additive, not multiplicative.** Multiplying the global weight by salience inherits the global floor — `LIVE` would reach only 9% even for a user scoring 88 on it, because it starts at 6%. The additive form breaks that dependency.

Worked effect at α = 0.35 for a user scoring `LIVE` 88, `ENRG` 88, `CROWD` 75, `NOV` 75, `FOOD` 38, `SCEN` 38, `POL` 38, `PLAY` 25, `HERIT` 12, `AFFIL` 50:

```
          CROWD  ENRG  SCEN  FOOD   POL   NOV  PLAY  LIVE  HERIT  AFFIL
global      15%   12%   12%   14%   13%    8%    7%    6%     5%     8%
priority    15%   16%    8%    9%   11%   11%   10%   12%     3%     5%
```

`LIVE` 6%→12% and `ENRG` 12%→16% — the two factors that define this night — rise; `FOOD` 14%→9% and `SCEN` 12%→8%, which they are neutral on, fall. `AFFIL` falls to 5% because they answered exactly 50: no position, so no priority.

Note `PLAY` rising 7%→10% despite a *low* score of 25. That is the participatory rule working as intended: 25 is a strong position, and being taken to an escape room is a real cost, not a neutral one.

**Choosing α.** At α = 0.5 the largest single-factor weight reaches roughly 40% for a user extreme on one factor, which is defensible. At α = 0.7 it reaches 50% and the smallest falls to 1%, effectively deleting factors from consideration. **Ship 0.35; revisit against plan feedback.** This value is a judgement call, not a derived one.

**Three implementation traps:**

1. **Do not stack priority and slot emphasis multiplicatively without a single final normalisation.** Priority weights are computed first, slot emphasis second, and normalisation happens once at the end of `match()`. Applying both as independent multipliers double-counts and collapses the plan to one note.
2. **For groups, derive priorities from the room's blended vector, never by averaging member weight vectors.** The blend vector is produced by the abstention rule and already reflects who holds what. Averaging member weight vectors lets one extreme member hijack the group's priority profile, which fights the every-stop rule in §13.4 rather than supporting it.
3. **An undefined factor in the blended vector carries zero salience and must not be treated as 50.** Under abstention a factor can come back undefined when no member holds a position on it. Feeding 50 in gives it the salience of a genuine neutral, which it is not.

**What this does not fix.** Reweighting re-ranks venues that exist against users that exist; it cannot manufacture a shape no venue has. It also cannot rescue a user whose profile no vibe describes — that is a coverage problem, addressed by adding vibes.

**Secondary benefit.** The pros & cons shown on the plan card are generated from the same weights. Under global weights they cite `CROWD` and `FOOD` for essentially everyone; under priority weights they cite the reasons that particular user actually cares about.

**Then check availability — on the shortlist only.**

This ordering is not optional. Checking availability during Stage 2 would mean ~71 candidates × 3 slots ≈ 213 venues per plan. At 10,000 plans/day that is unaffordable and destroys the latency budget. So:

```
5.2  hard filter          →  ~71 candidates per slot
5.3a vibe ranking         →  top 8 per slot
5.3b AVAILABILITY CHECK   →  24 venues, mostly cached      ← here
5.3c sequence optimise    →  final plan
```

24 venue lookups per plan, and everything except live busyness resolves from `venue_availability` without a network call.

```python
for slot in template.slots:
    for v in shortlist[slot]:
        v.tier, v.p_seat, v.confidence = availability_for(
            v.venue_id, projected_arrival(slot), group_size, week_part)
    shortlist[slot] = [v for v in shortlist[slot] if v.tier != 'exclude']
```

If a slot empties entirely, run the relaxation ladder (§5.2) before falling back to HEDGE-only candidates.

**Then optimise the combination:**

```python
best, best_score = None, -inf
for combo in itertools.product(*slot_candidates):        # ~8^3 = 512, prune early
    if not timing_feasible(combo, start_time):    continue   # arrival within opening windows
    if total_cost(combo) > budget_ceiling:        continue
    if not arc_respected(combo, template.arc):    continue
    if any(serve_level(v, m)[0] == 0 for v in combo for m in members): continue   # §13.4 - nobody gets nothing
    if combo[0].tier != 'safe':                   continue   # first stop must be SAFE (§4.4)
    if sum(1 for v in combo if v.tier == 'hedge') > 1: continue
    served = sum(serve_level(v, m)[0] for v in combo for m in members)              # §13.4
    s = served * SERVE_WEIGHT + sum(scores) - travel_time_penalty(combo) - 0.08 * hedge_count(combo)
    if s > best_score: best, best_score = combo, s
```

The `fairness_satisfied` call that used to sit here is superseded (§6). The check is now
§13.4's: a combination where any member is served on nothing at any stop is out; among the
rest, the total served level leads and venue score follows. `SERVE_WEIGHT` sets how far served
dominates score — start high enough that no venue score can buy a stop where somebody is on #3.
The greedy `pick_stops` in §13.4 is the reference for what "served" means; this loop is the same
criterion applied to whole combinations so timing, budget and availability are checked together.

Brute force with early pruning is fine at this size and is fully explainable when a plan looks wrong — which matters more than elegance here.

Write each chosen stop's tier into `plan_stops.availability_tier`. It drives the "call ahead" line on the card and is what you compare against outcomes in §7.

### 5.4 Stage 4 — narrative *(one LLM call, 1–3s)*

Send the **fully decided** plan and ask for: the editable title, one line per stop on why it suits the group, per-member reasons, and transition phrasing ("Start off with", "Swing by") as specified in `VIEW_FLOW.md`.

The model cannot invent a venue, reorder stops, or break a constraint — everything is already fixed.

**Return Stages 1–3 immediately and stream the narrative in.** The user sees the plan structure instantly; copy fills in. If the LLM call fails or times out, serve template default copy and log it — never fail the request.

**One call per plan, not three.** At 100K DAU and a 10% lock rate that's ~10K plans/day; the difference between one and three calls is lakhs per month.

---

# 6. Group fairness

Averaging member vectors produces plans that satisfy nobody — the mean of "loud party" and "quiet romance" is a lukewarm plan both members reject.

> **Superseded 2026-09-16.** The constraint below — one stop per member across the night — is
> replaced by §13.4: *every* stop has something for *every* member, served on a factor they
> ranked. The old rule produced "stop 1 the restaurant, stop 2 the arcade, stop 3 the mixer" —
> a night where each person has one good hour and two dead ones. Kept here for the record.

~~**Constraint: every member must have at least one stop that genuinely suits them.**~~

```python
# superseded - see §13.4
FAIRNESS_THRESHOLD = 0.72

def fairness_satisfied(combo, member_vectors):
    return all(
        max(match(m, venue, {}) for venue in combo) >= FAIRNESS_THRESHOLD
        for m in member_vectors
    )
```

Minimise the worst experience first; maximise the group average second.

This constraint also *produces* the per-person copy in the plan card ("for Riya there are cocktails, for Kabir the desserts") — those lines are true because the constraint made them true.

If no combination satisfies it, relax `FAIRNESS_THRESHOLD` in steps of 0.05 down to 0.60, then surface the best available and flag the plan `fairness_relaxed` for monitoring.

---

# 7. The feedback loop

Everything above is a starting guess. This is what corrects it.

| Signal | Source | Updates |
|---|---|---|
| Star rating per stop | End Plan flow | `own_visits` evidence → venue scores + confidence |
| **Arrived, dwell ≥ 20 min** | geofence | `seated` event → raises `p_seat` for that slot |
| **Arrived, dwell ≤ 8 min** | geofence | `bounced` event → strong negative on `p_seat` |
| Stop skipped entirely | geofence gap | weak negative on both — may be a queue they saw and left |
| **Plan regenerated** | refresh button | negative on the vibe read **and** the template |
| Locked without edits | lock action | positive on template + venue set |

**One instrumentation, two systems.** The same geofence arrival event is `own_visits` evidence for factor scoring *and* the `seated`/`bounced` signal for availability. Build it once and both halves improve together — this is the highest-leverage thing to ship early.

Four things to learn:

**Venue scores.** Feed ratings into `own_visits` evidence. Highest weight, overrides external sources.

**Evidence weights.** Once you have a few thousand rated stops, regress satisfaction against per-evidence-type predicted match. If `photos` predicts SCEN satisfaction better than `review_text`, raise `W[photos][SCEN]`. This replaces permanent hand-tuning with measurement.

**Availability calibration.** Quarterly, compare each source's predicted `p_seat` against observed outcomes. If `live_busy` predicted 0.8 on occasions that resolved to 0.6, its σ is understated and should rise. Standard reliability calibration — it improves fusion without changing any logic. This is what `contributing` (§2.6) exists for.

**Template quality.** Track lock rate, completion rate and mean rating per template. Retire the bottom decile; clone and vary the top.

**Treat refresh as first-class negative feedback.** It's the clearest signal you'll get and it arrives instantly. A refresh must also return a *meaningfully different* plan — different template or different area — not a permutation of the same venues. Reshuffling the same three reads as broken.

**Where this ends up.** As arrival data accumulates, `own_visits` dominates the precision sum in §4.2 and the paid busyness API demotes to cold-start coverage for venues you haven't sent anyone to yet. Same trajectory as the factor scores — **external data is scaffolding; your own behavioural data is the building.**

---

# 8. External dependencies

| Layer | Service | Used for | Failure mode |
|---|---|---|---|
| Facts, hours | Google Places | ingestion, verification | serve cached; mark `unverified` |
| POI coverage | Foursquare / OSM | backfill | degrade silently |
| Travel time | Google Routes / Distance Matrix | Stage 2 + 3 | fall back to haversine × 1.4 |
| **Busyness** | **licensed busyness API** | **live top-up in Stage 3b only** | **drop from fusion; confidence falls; more venues become HEDGE** |
| **Venue status** | **SHUFFL Business dashboard** | **first-party availability** | **treat as absent past 12h** |
| Narrative | LLM provider | Stage 4 only | template default copy |
| Events | ticketing partners | later — events occupy a slot | feature-flag off |

Only **travel time** and **live busyness** are on the request path, and busyness only for the ~24 shortlisted venues. Cache travel aggressively by origin-destination pair; cache busyness for 10 minutes.

**Never scrape Google for busyness data.** Beyond ToS exposure, SHUFFL licenses data commercially and enterprise buyers audit provenance — scraped inputs surface as a problem in a contract review, not a code review.

---

# 9. Failure modes to handle explicitly

| Situation | Behaviour |
|---|---|
| No candidates after filtering | run the relaxation ladder (§5.2); if still empty, return a single-stop plan |
| Group larger than any venue's capacity | drop to venues without capacity data, flag for review, suggest splitting |
| Travel API down | haversine × 1.4; widen timing buffers |
| LLM timeout | ship structure with default copy |
| All candidates low-confidence | allow it, but cap at one such venue per plan |
| Venue closed permanently mid-plan | mark `status='closed'`, exclude, notify active plans holding it |
| Busyness API down | drop it from fusion; confidence falls naturally; more venues land in HEDGE |
| Every shortlist venue EXCLUDE | widen shortlist → shift slot time ±30 min → relax to HEDGE with an explicit warning |
| Venue reports "full", own arrivals disagree | trust the venue if fresh (<2h); if stale, trust arrivals and flag for review |
| Brand-new venue, zero availability data | structural prior only → UNKNOWN → HEDGE. Acceptable — this is also how you gather data on it |
| Festival, cricket final, long weekend | apply a city-wide multiplier to `capacity_pressure`; these dates are known, hardcode a calendar |

---

# 10. Build order

**Phase 1 — no ML, no paid APIs.**
Ingest facts and hard attributes. Score factors from `review_text` and `photos` with hand-set weights. Implement confidence and shrinkage exactly as specified. Author 15–20 templates. Hard filter plus greedy sequencing. One LLM call for narrative.
*Availability:* typical busyness + structural prior only, two sources through the same fusion, three-tier rule live. Nothing real-time. This alone prevents the worst failure — sending people to a known hotspot at peak Saturday.

**Phase 2 — instrument arrivals. Highest leverage in the whole plan.**
Geofence arrival + dwell classification, writing `venue_arrival_events`. This single build feeds `own_visits` evidence for factor scores **and** `seated`/`bounced` for availability. Within a couple of months it becomes the best signal in both systems. Add template performance tracking, novelty cooldown, the discovery slot, and the every-stop rule (§13.4).

**Phase 3 — paid and first-party signals.**
Licensed live busyness API in Stage 3b. Venue capacity toggle in the SHUFFL Business dashboard.

**Phase 4 — learn.**
Regress evidence weights from satisfaction data. Quarterly σ recalibration for availability sources. Full combinatorial sequencing. Event-listing integration.

---

# 11. What to monitor

| Metric | Why | Target |
|---|---|---|
| **Bounce rate** — arrivals with dwell ≤ 8 min | The number the availability system exists to reduce. Track per tier. | SAFE should be dramatically lower than HEDGE. If not, thresholds are wrong. |
| Tier distribution across shortlists | Over-tight thresholds shrink plan quality for no gain | EXCLUDE under ~25% of shortlisted venues |
| Plan regeneration rate | Inverse proxy for vibe-read accuracy | should not rise as other things change |
| Source calibration drift | Predicted vs actual `p_seat` per source | reviewed monthly, σ retuned quarterly |
| p95 plan latency | Stages 1–3 return before narrative streams | under 500ms excluding the LLM call |

---

# 12. Things that will bite you

- **Opening hours are the highest-severity bug in this system.** A user who arrives at a closed venue does not blame the venue.
- **Never assign a vibe to a venue.** Vibes describe people. Venues carry factor vectors, and matching is vector-to-vector. If a `venue_vibe` column ever appears, something has gone wrong upstream.
- **Always read scores at the stop's scheduled day part.** Querying `venue_scores` without a `day_part` predicate silently returns whichever row the planner picked, which is the kind of bug that produces "why did it send us to a brunch place at midnight."
- **Distance is asymmetric — don't 'simplify' it back to `abs()`.** The one-sided rules in §5.3 are deliberate. Collapsing them looks like a tidy-up and quietly degrades every plan.
- **`AFFIL` is not the inverse of `CROWD`.** They run 0.82 inverse-correlated, which is close enough to tempt someone into deriving one from the other. A third of `AFFIL` is independent, and that third is a real population — seven vibes want a busy room while staying focused on their own table. Deriving it mispredicts every one of them by 19 to 24 points.
- **Overshoot on a `PASSIVE` factor is free, and that is not a rounding-off.** `SCEN`, `FOOD` and `HERIT` only cost you on a shortfall. If a symmetric `abs()` ever creeps back into the penalty for these three, every plan quietly gets worse and nothing looks broken.
- **Never rank on `percentile`** — always `final_score`. Skipping the shrinkage step silently promotes every under-evidenced venue in the city.
- **Never restrict recommendations to venues with commercial contracts.** It degrades the core product to serve a sales objective. Recommend the best venue; bill separately where a contract exists.
- **Availability runs on the shortlist, never during hard filtering.** Checking all ~213 candidates per plan is unaffordable at scale and blows the latency budget.
- **`p_seat` and `confidence` are two numbers, not one.** Multiplying them together to get a single "score" destroys the distinction the tier rules depend on.
- **The first stop must be SAFE.** A queue at 7pm poisons the entire evening, and no later stop recovers it.
- **Dwell time under ~8 minutes is a turned-away signal, not a short visit.** Classify it as `bounced`, not as a low rating.
- **Renormalise weights over present evidence types.** Otherwise a venue with no menu data is penalised on FOOD twice — once for missing evidence, once by the denominator.


---

# 13. Addenda, 2026-09-14 onward

Two gaps found by running a worked journey through the rules above, and one direction logged.

### 13.1 When `FLOOR` fails — relax the softest-held constraint and re-plan

**Decided 2026-09-15.** A member with extreme, firmly held scores can pass the room-join filter
and then have no stop in any plan that serves them. When that happens the engine does not return
a plan that strands them and does not give up. It relaxes **one** constraint — the one that
member is *least sure about* — and plans again.

```python
MAX_RELAX = 3

def plan_with_relaxation(members, venues):
    relaxed = {m.id: [] for m in members}
    for _ in range(MAX_RELAX + 1):
        plan = best_plan(members, venues, relaxed)
        stranded = [m for m in members if is_stranded(m, plan, relaxed[m.id])]
        if not stranded:
            return plan, relaxed
        m = max(stranded, key=lambda m: worst_overrun_at_best_stop(m, plan, relaxed[m.id]))
        f = softest_overrunning_factor(m, plan, relaxed[m.id])
        if f is None:
            break
        relaxed[m.id].append(f)
    return None, relaxed          # room is not a fit - say so before they join

def softest_overrunning_factor(m, plan, already):
    """Of the factors still overrunning at this member's best stop, the one they
    were least sure about - lowest latency-firmness. Relaxing it costs them least."""
    stop = best_stop(m, plan, already)
    over = [f for f in FACTORS if f not in already and overrun(m, stop, f) > 0]
    return min(over, key=lambda f: m.firmness_latency[f]) if over else None
```

**What "relax" means:** for this plan only, that factor's bend for that member is opened fully —
treated as passive in both directions. Their stored profile is untouched. Next session, it is
back.

**Why the softest, not the smallest overrun.** The factor with the smallest overrun might be
one they are certain about. Giving way on it costs them something real. Giving way on the one
they hesitated over costs them least, and latency is what says which that is. By construction
the fastest-answered factors — the top and the refusals — are relaxed last, if ever.

**The cap is the honesty check.** If a member is still stranded after three relaxations, what
is left is what they are surest about, and a plan that gives way on those is not their night.
Stop, and say the room is not a fit — before they join, if this runs at the gate.

**Say what was done — short on the card, detail behind ⓘ.** The engine returns, per stop, a
list of `(member, factor, direction)` for every relaxation that stop needed. The app renders one
note per entry under the venue:

| direction | when | note |
|---|---|---|
| `want` | member's score on the factor ≥ 50 and the venue is below their bend | *"Priya might miss out on the food a little here"* |
| `aversion` | member's score < 50 and the venue is above their bend | *"Priya might not like the crowd a little here"* |

The factor is rendered in the reader's words (`FACTOR_WORD`, the same table the per-person line
uses), never the code. Beside the note, an ⓘ. Tapping it shows three lines: the factor eased;
why it was that one — *"Priya seemed least sure about this one when she swiped"* (that is what
softest-held means, said plainly); and what this stop still gives her — her `serve_level` factor
from §13.4. The note is never hidden — a relaxation the member does not know about is a plan that
quietly ignores them — but the mechanics are one tap away, not on the card.

```python
def relaxation_notes(stop, relaxed):        # relaxed: {member_id: [factor, ...]} from plan_with_relaxation
    notes = []
    for m in members:
        for f in relaxed[m.id]:
            if overrun(m, stop, f) <= 0: continue          # eased, but this stop did not need it
            direction = 'want' if m.scores[f] >= 50 else 'aversion'
            notes.append((m.id, f, direction, m.firmness_latency[f], serve_level(stop, m)[1]))
    return notes
```

**Log every relaxation** — member, factor, how many it took. A factor relaxed often, across many
members, is a factor the venue set is weak on. That is the plan engine telling you what to go
and find.

**Order when more than one member is stranded:** the worst-stranded first, one factor at a time,
re-plan, re-check. Never two at once — the second may not be needed after the first.

### 13.2 The join filter and the plan can disagree — resolved by §13.4a

> **Resolved 2026-09-15.** The joiner's list now runs `FLOOR` for that one person against the
> room's actual venues (§13.4a), which is the "check feasibility before a room is offered" option
> below. The 70% similarity stays as a coarse first pass; `FLOOR` is the check that decides.
> Kept for the record.

The 70% similarity filter on room entry is computed on scores. Whether a plan can actually serve
someone depends on their firmness. A moderate person at 77% similarity is fine; a certain person
at 77% is not, and the filter cannot tell them apart. Either the filter should use
firmness-weighted distance, or feasibility should be checked before a room is offered.

Both gaps are exactly where response latency (`ASSESSMENT_ENGINE.md` §3, §6) decides the
outcome: a slow 100 opens the bend and the plan works; a fast 100 is a genuine wall and the room
should say so before, not after.

### 13.3 Bend has no floor at the extremes — fix before anything else

`bend_down(100)` is `(100 − 100) / 100 = 0`. A firm 100 tolerates nothing below 100, and latency
cannot help because it multiplies a zero. The `BEND_FLOOR` of 0.40 applies only below 50. So a
full heart — which means "this matters a lot" — is read as "only a perfect match will do," and
that is what stranded the worked case in §13.1.

The fix is one floor at each extreme:

```python
def bend_down(vibe, f):
    x = vibe.scores[f]
    if x < 50: return max(BEND_FLOOR, (100 - x) / 100)
    return max(BEND_EXTREME, (100 - x) / 100)             # BEND_EXTREME = 0.20

def bend_up(vibe, f):
    if f in PASSIVE: return 1.00
    flag = BEND_FLAGS.get(vibe, {}).get(f)
    if flag: return BEND_TIER[flag]
    return max(BEND_FLOOR if vibe.scores[f] >= 50 else BEND_EXTREME, vibe.scores[f] / 100)
```

`BEND_EXTREME = 0.20` — a firm 100 accepts an 80. Set 2026-09-15 after a worked run at 0.10
hid a firm Crowd Chaser from four rooms out of five: at 0.10 he tolerated a 10-point miss, so the
loudest venue in the set (CROWD 92, ENRG 95) already overran him, and the person who says "packed
and loud" with full confidence was the hardest person to place anywhere. At 0.20 a fast 100 sits
near 0.20 and a slow or deferred 100 near 0.35–0.40. That is the spread `FLOOR` needs.

### 13.4 `FLOOR` v3 — every stop serves every member on something they ranked

**Decided 2026-09-16. Replaces the definition of 2026-09-03 and the one-stop-per-member
constraint in §6.** The reason is in the shape of the plans the old rule produced: three people
wanting POL, PLAY and FOOD got a restaurant, then an arcade, then a mixer — each person's night
in one hour and two hours of somebody else's. The plan card had always promised *"for X there are
cocktails, for Y there are desserts"* under every stop; the engine only guaranteed one.

**The rule.** At each stop, every member is served on the highest-ranked factor of theirs that
the venue delivers. If no venue delivers everyone's #1, the person missed is served on their #2;
if that fails, their #3. A stop where somebody is served on nothing loses to any stop where
everybody is served on something.

```python
WANT_FLOOR = 60      # a factor counts as a want down to here
DELIVERS   = 55      # a venue has to actually HAVE the thing to serve a want on it
DEBT_K     = 0.6     # how much a shortchanged member's needs count at the next stop

def ranked_wants(m):
    """Their factors in order, top first, down to WANT_FLOOR. AFFIL only at #1 - it
    runs high for nearly everyone, and would otherwise let any table of friends
    count as serving them."""
    hi = max(m.scores.values())
    out = [f for f in sorted(FACTORS, key=lambda f: -m.scores[f]) if m.scores[f] >= WANT_FLOOR]
    return [f for f in out if f != 'AFFIL' or m.scores[f] == hi]

def delivers(venue, m, f):
    """Within their bend on f AND the venue actually has f. Bend alone is not enough:
    a mildly held 70 has a wide bend, so a venue at 30 does not overrun it - but it
    does not deliver it either."""
    return venue[f] >= m.scores[f] - 100 * user_bend(m.vibe, m.scores, f, 'down') \
       and venue[f] >= DELIVERS

AVERSION_FLOOR = 55   # a venue below this on f is not "the thing" and cannot overrun an aversion to it (2026-09-17)

def violated(venue, m, f):
    return venue[f] >= AVERSION_FLOOR and venue[f] > m.scores[f] + 100 * user_bend(m.vibe, m.scores, f, 'up') + 15

def serve_level(venue, m):
    """1/rank of the best-ranked want the venue delivers. #1 -> 1.0, #2 -> 0.5,
    #3 -> 0.33. Nothing -> 0. A violated hard refusal -> 0 regardless of wants."""
    if any(violated(venue, m, f) for f in m.refused): return 0.0, None
    for rank, f in enumerate(ranked_wants(m), 1):
        if delivers(venue, m, f): return 1.0 / rank, f
    return 0.0, None

def pick_stops(members, candidates, n_stops):
    debt = {m.id: 0.0 for m in members}
    chosen, prev_energy = [], -1
    for k in range(n_stops):
        best = None
        for venue in candidates:
            if venue in chosen or venue['ENRG'] < prev_energy - 10: continue   # arc
            levels = [(m, serve_level(venue, m)) for m in members]
            nobody  = sum(1 for _, (lvl, _) in levels if lvl == 0.0)
            served  = sum(lvl * (1 + DEBT_K * debt[m.id]) for m, (lvl, _) in levels)
            key = (-nobody, served, -room_cost(members, venue))     # strict priority order
            if best is None or key > best[0]: best = (key, venue, levels)
        _, venue, levels = best
        chosen.append(venue); prev_energy = venue['ENRG']
        for m, (lvl, _) in levels: debt[m.id] += 1.0 - lvl
    return chosen
```

**The order of priorities is the whole rule:**

1. **Nobody gets nothing.** A stop with nothing for one member loses to any stop with something
   for everyone, however good it is for the others. This is what changes the night.
2. **Highest total served, weighted by debt.** Whoever was served further down their list at
   earlier stops counts more now. This is "the next stop becomes more POL-centric."
3. **Cost**, from §5.3, as the tie-break. It was the objective; now it only separates venues
   that serve people equally well.

**`FLOOR` is now per stop, not per plan.** A plan fails `FLOOR` at a stop where somebody is
served on nothing. §13.1 applies per stop: relax the softest-held want of whoever would get
nothing, and re-pick that stop.

**When this runs.** At plan generation — for the host and co-hosts, before the room is hosted —
and on any refresh while the room is still private. **Hosting freezes the plan.** People who join
a public room join *because* of its plan, and are filtered against it (§13.4a); the plan does not
regenerate when they arrive, and the refresh control is gone from the moment the room is public.
Blend style and colour keep changing as people join — that is the room's identity — but the plan
is what they joined for. Two freezes: hosting freezes the plan, locking freezes the room.

**`delivers` is stricter than `overrun`, and has to be.** Bend says how far a venue can miss
before it costs. Serving a want is a different question: does the venue have the thing. A
restaurant at ENRG 30 does not overrun somebody whose ENRG is a mildly held 70 — their bend is
wide — but it is not a loud room, and it does not serve them on ENRG. Without the `DELIVERS`
floor the #2 fallback was nearly free, which defeated it.

**Worked, three people — POL 100, PLAY 100, FOOD 100 — seven venues, no venue has all three:**

```
old rule    1 fine dining      Pia #1 POL    Rahul —          Neha #1 FOOD
            2 speakeasy        Pia #1 POL    Rahul #2 ENRG    Neha #2 NOV
            3 arcade           Pia #3 CROWD  Rahul #1 PLAY    Neha —

this rule   1 speakeasy        Pia #1 POL    Rahul #2 ENRG    Neha #2 NOV
            2 posh arcade      Pia #2 SCEN   Rahul #1 PLAY    Neha #2 NOV
            3 trendy mixer     Pia #1 POL    Rahul #2 ENRG    Neha #2 NOV
```

Fine dining loses stop 1 under this rule even though it fully serves two of the three, because
it has PLAY 5 and Rahul is served on nothing. Neha never reaches her #1 — no venue with FOOD 80+
also has something for Rahul — and that is the venue set's limit, not the rule's; relaxation is
what handles it.

**What the plan card gets from this.** `serve_level` returns the factor each person was served
on at each stop. That is the per-person line — *"for Rahul, a loud room"* at the speakeasy,
*"for Rahul, the games"* at the arcade — read off the result rather than written by hand, and
guaranteed to have content at every stop.

**Constants, all starting points:** `WANT_FLOOR` 60, `DELIVERS` 55, `DEBT_K` 0.6, the 1/rank
weights. The `-10` on the energy arc is the existing rule.

> **Refined 2026-09-17 by §13.4c:** the 1/rank levels become 1.0 / 0.85-or-0.5 / 1/rank
depending on how strong the #2 is; a debt of 0.5 forces the next stop to serve that person's #1
by the venue; the area can carry a want at half strength (§13.7); and a stop for one person
alone exists only when nothing of theirs can be served any other way. The priorities above are
unchanged.

### 13.4a `FLOOR` for one person — the public-room list

When a user browses public rooms, each room **already has a plan**. The question is not what the
user would do to the room; it is whether the room's plan suits the user. So the list filters on
two things, both about the user alone:

```python
def room_suits(user, room_plan):
    plan_sim = similarity(user.would_be_plan_vector, plan_vector(room_plan))   # the 70% rule
    nothing  = any(serve_level(stop, user)[0] == 0 or serve_level(stop, user)[2] == 'area'
                   for stop in room_plan) if ranked_wants(user) else False   # by the venue - full or partial; the street alone does not count for a joiner
    in_bend  = all(over_points(stop, user) == 0 and not any(violated(stop, user, f) for f in user.refused) for stop in room_plan)
    return plan_sim >= 0.70 and not nothing and in_bend         # bend is a GATE here - §13.4d
```

The 70% on its own passes nearly every room — on a worked set of five it passed all five. The
per-stop check is the one that discriminates, and it needs the actual venues, not the plan's
average vector. (Aligned 2026-09-17 with §13.4c: hidden if any stop serves the joiner on nothing
— unless they want nothing — or overruns an aversion of theirs. The earlier overrun-only test with
its unset threshold is gone.)

**Nothing in this check reads the other members.** Their chemistry — blend drift, CONSENSUS
after the join, the room states if built — is the host's decision when the request arrives, and
sorts the host's request list into Strong Matches and Others. It is not a filter on what the
joiner sees. The two lists use different variables because they answer different questions:
*is this night mine* versus *would this person change our night*.

### 13.4b `POL` sense and `NOV` as a filter — how the plan engine uses them

**`POL` sense.** The profile carries `POL` as one score plus a sense — `classy`, `current`, `both`
(`ASSESSMENT_ENGINE.md` §5.4). Venues carry the same tag from their evidence. At plan time a
member whose sense is `classy` is not served on `POL` by a venue tagged `current`, however high
its `POL` score, and vice versa; `both` is served by either. This is a filter on the `delivers`
check in §13.4, not a new factor and not a new weight.

**`NOV` as a filter.** `NOV` stays in the vector and in the name — it can top somebody's list. But
for most people its job at plan time is choosing between a familiar venue and a brand-new one
among venues that already serve them: high `NOV`, prefer the one they have not been to; low
`NOV`, prefer the one they have. It should carry little weight in the match itself. This is the
existing novelty adjustment and "have you been here before?" made explicit as `NOV`'s role.

### 13.4c Debt and payback across stops — the weak-second rule, the area as a fallback, and the dedicated stop as last resort

**Decided 2026-09-17; refined the same day by running nine rooms through it (`DECISIONS.md`
entries 85–86, 89). Refines §13.4's `serve_level` and `pick_stops`; the priorities in §13.4 stand.**

**What bend is for, by context — the user's framing, 2026-09-17.** Bend does two different jobs
and the engine must know which one it is doing:

| Context | Bend is | What it guarantees |
|---|---|---|
| **A plan for a group** — a host with co-hosts, or friends planning together | **stretch** — how far this person can be pulled across the stops | a firm *aversion* (low score, low bend): at every stop, at least one of their wants is served to some degree (rule 9). A firm *want* (high score, low bend): at least one stop includes it (rule 10). Bend is relaxed as far as it will go to keep the night cohesive while every want is still served. |
| **A plan for one person** — the solo Create flow — or **a room somebody wants to join** | **a gate** — the plan has to be catered to them | every stop inside their bend; served at their level, not partially (§13.4d, §13.4a) |

Concession, debt and payback are the machinery of the first row only. Joiners join a frozen plan
and are gated against it; a solo plan is theirs and nobody is stretched. Where the people planning
together are *friends in the engine's sense* (§13.9), debt is replaced by relaxed bends and the
combination search — the same stretch, without the bookkeeping. So in practice: debt and payback
are for co-hosts and plan-mates who are not yet close.
The question this answers: when somebody's top factor is not served at a stop, what does the next
stop owe them — and when, if ever, does anyone get a stop that is only theirs.

**The shape of it, in one paragraph.** At stop 1 the venue serves Neha on her #2 because it
cannot serve her #1. Whether that is *enough* depends on how good her #2 is. If her #2 is strong
— 70 or more, and within 10 of her #1 — it is nearly as good as the real thing and the room owes
her little. If it is weak — under 70, or more than 10 below her #1 — the room owes her: **the
next stop serves her #1, by the venue itself**, and at that stop the others get their #2 by the
venue (a diner with a good crowd), or, if they have no #2 — everything else of theirs sits in
40–60 — their #1 carried by the *area* the venue is in (a restaurant on a street full of pubs, so
the night can still build). Bend is checked for everyone at every stop; the aim is that every
person has a reason to be at every stop, even the ones that lean to somebody else. **Nobody gets
a stop of their own unless nothing of theirs can be served any other way.**

#### The constants

```python
SECOND_STRONG = 70          # a #2 at or above this ...
SECOND_GAP    = 10          # ... and within this of #1 is nearly as good as #1
STRONG2       = 0.85        # serve level on a strong #2
SOFT          = 0.50        # serve level on a weak #2, or on any want the area carries instead of the venue
DEBT_TRIGGER  = 0.50        # debt at or above this, with #1 not yet served tonight -> the next stop serves it, by the venue
AREA_FACTORS  = {'CROWD', 'ENRG', 'POL', 'SCEN'}   # the only wants an area can carry (§13.7)
SERVED_FLOOR  = 0.85        # best single stop tonight at or above this = one real serving (rule 5). Confirmed 2026-09-17; not a knob
OVERRUN_W     = 0.01        # a served person's overrun costs this per point - at every stop (rule 9), and at a dedicated stop (rule 6)
MAX_STOPS     = 3           # the night can be extended to this many to fit reserved stops (rule 8)
AVERSION_FLOOR = 55         # §13.4 - a venue below this on f cannot overrun an aversion to f
```

A weak #2 served once (0.5 debt) triggers payback at the next stop. A strong #2 (0.15 debt)
does not — and by design never does within a three-stop night: three "nearly"s reach 0.45, under
the trigger. A strong #2 *is* the compromise working (decided 2026-09-17). Served on #3
(0.33) or by the area (0.5) triggers it too.

#### `serve_level`, revised — the venue first, the area only as a fallback

```python
def delivers_at(score, m, f):
    return score >= m.scores[f] - 100 * user_bend(m.vibe, m.scores, f, 'down') and score >= DELIVERS

def second_is_strong(m):
    w = ranked_wants(m)
    return len(w) >= 2 and m.scores[w[1]] >= SECOND_STRONG \
                       and m.scores[w[0]] - m.scores[w[1]] <= SECOND_GAP

def serve_level(venue, m):
    """The best reason this venue gives m to be here: (level, factor, 'venue'|'partial'|'area').
    #1 by the venue 1.0; strong #2 0.85; weak #2 0.5; #3+ 1/rank. The venue HAS the thing
    (>= DELIVERS) but below the person's own floor: 0.5, 'partial' - "to whatever degree". A
    want the venue cannot give but the area can: 0.5, 'area', AREA_FACTORS only. Full by the
    venue beats partial beats area at equal level. Nothing -> 0."""
    if any(violated(venue, m, f) for f in m.refused): return 0.0, None, None
    options = []
    for rank, f in enumerate(ranked_wants(m), 1):
        if delivers_at(venue[f], m, f):                                    # the venue itself, at their level
            level = 1.0 if rank == 1 else (STRONG2 if second_is_strong(m) else SOFT) if rank == 2 else 1.0 / rank
            options.append((level, 2, f, 'venue'))
        elif venue[f] >= DELIVERS:                                         # the venue has it, not at their level
            options.append((SOFT, 1, f, 'partial'))
        elif f in AREA_FACTORS and venue.area and delivers_at(venue.area[f][band], m, f):
            options.append((SOFT, 0, f, 'area'))                           # the street carries it
    if not options: return 0.0, None, None
    level, _, f, how = max(options)
    return level, f, how
```

*Partial* is what "serves everyone's top factors to whatever degree" means in code: Depot 48 has
live music some nights at 60 — under a gig-lover's floor of 64, but it *has* it, and that is half
a reason. Partial by the venue outranks the street carrying it, because the thing is in the room.

`violated` and `overrun` read the venue alone. The area never counts against anyone and never
raises a venue's score; it only gives a person a reason when the venue cannot (§13.7).

#### `pick_stops`, revised

Six rules the first draft did not have, every one found by running a room through it:

1. **Owed = debt ≥ 0.5 *and* their #1 not yet served by a venue tonight.** Once your #1 has been
   served once, a later weak-#2 stop does not create a new hard payback — the debt only leans
   the choice (§13.4's `served × (1 + DEBT_K × debt)`). Otherwise every night bounces.
2. **The debt outranks the energy arc.** If no venue inside the arc pays the owed member, search
   every remaining venue. The late-night restaurant after the club is a payback stop.
3. **The energy arc is a preference, not a constraint.** Try inside it first; it yields, in
   order, to *nobody gets nothing* (if every venue in the arc leaves someone with wants at zero,
   search all remaining venues), to a payback (rule 2), and to an empty pool (the night winds
   down). A person served on nothing is worse than a night that dips.
4. **"Nobody gets nothing" applies to people who want something.** A member with no ranked want
   — everything of theirs in 40–60 — is served on nothing at every stop by definition, takes on no
   debt, and is never stranded. That is *Along for the Ride*; their line on the card comes from
   bend, not from a served factor.
5. **Stranded** = a member *with* wants — one want or four — of whom **none, at any rank**, can be
   served at any remaining venue the others tolerate, either because the others are low and firm
   on all of them or because no such venue exists. If even *one* of their wants is served
   somewhere, they are not stranded: they get a want heightened at the next stop instead
   (rule 7). **One** stranded member who has had nothing yet tonight → their dedicated stop, at
   the next slot (this slot goes ahead with their zero accepted; if this is the last slot, now).
   **Two or more** stranded → not one person left out but a room that does not work: relaxation
   (§13.1) — *unless* rule 8 has reserved them stops, which it will have if the problem is
   structural. A member stranded *after* having had **one real serving** — their *best single
   stop* so far ≥ `SERVED_FLOOR` (0.85: a #1, or a strong #2; two half-reasons do not add up to
   one) — has their zeros accepted from there; no dedicated stop. A member whose only serving was
   a weak #2 or the street (0.5) and who then has nothing reachable is treated as never served,
   and gets the stop: half a reason once is not "one of their wants served".
6. **One dedicated stop per person per night; their own bend holds there; the others are
   softened, not trampled.** The stranded member's *own* aversions are enforced at their own stop
   — a person who wants a gig and hates energy gets the jazz bar, not the warehouse — and if no
   venue serves their #1 inside their own bend, their #2. Among the venues that qualify, take the
   one where the *others* are served best (a lower want, or the street) **and stepped on least**:
   `served − OVERRUN_W × overrun_points` (0.01). Their bend is not a constraint at this stop —
   that is the whole compromise — but between two venues that serve the stranded person equally,
   the one that overruns the others by 20 points beats the one that overruns them by 60. A hard
   refusal is still a wall. After it, the member's zeros are accepted.
8. **Look ahead: `reach`.** Before the first stop, compute for every member the best level any
   venue can give them *with everyone in bend* — `reach[m]`. A member whose reach is under
   `SERVED_FLOOR` can never be served properly alongside the others; the walls are structural
   (their #1 is somebody's firm aversion, or no such venue exists), and no amount of half-reasons
   will change that. **Reserve them a dedicated stop now** — build it at the pre-pass and hold
   its venue out of the ordinary pool — and do not spend ordinary stops on them. Reserved stops
   take the last slots, arc-ordered; the ordinary slots run rules 1–7 and 9 with the reserved
   members' zeros accepted. If a reserved stop cannot be built at all (a hard refusal blocks every
   venue that serves them), the room is not a fit, and that is known before anyone joins. `reach`
   is computed under rule 9's gate, so after rule 9 this fires rarely — the mutual-wall room in the
   traces no longer needs it. If the reserved members plus one ordinary stop for everyone
   else need more stops than the night has, **extend the night** up to `MAX_STOPS` (3); past that,
   "not a fit" — said before anyone joins. Without this rule the planner spent two stops giving
   two mutually-walled people half a reason each and then declared the room broken at the third.
7. **Payback is the most group-compatible unserved want, not always #1.** When somebody is owed,
   try their #1: is there a venue that delivers it with everyone in bend? If not, their #2, then
   #3. The first rank that has a venue is the one heightened at the next stop — "one of their
   other wants, whichever the group's bends allow." After a payback stop they are marked paid for
   the night whatever rank it landed on; the room did the most compatible thing, and debt only
   leans from there.
9. **A served want compensates an overrun aversion.** The user's rule, stated as psychology: *as
   long as one of a person's preferences is being satisfied, they will be happy* — a man who hates
   live music is fine at Piano Man because the crowd is his. So bend is a **gate only for a person
   served on nothing** at that stop. For a person served on anything — fully, partially, or by the
   street — every point a venue sits past their aversion ceiling is a **cost**, not a bar:
   `OVERRUN_W` (0.01) per point, and only where the venue is at or above `AVERSION_FLOOR` on that
   factor. A hard pass is still a wall for everyone. The choice at a stop is then, in strict
   order: **nobody who wants something gets nothing → highest total served, weighted by debt → at
   stop 1, the calmer venue (the night builds; §4.4's SAFE first) → least stepping-on.** Served
   dominates; cost breaks ties. This is what dissolves most "walls": two people whose top factors
   are each other's aversions can share Piano Man — one served on the act, the other on the crowd
   — where a hard gate on bend would have sent them to separate stops.
10. **Every firm want gets a stop.** A want held firmly — score high, bend narrow (firmness ≥
   `FIRM`) — must appear at some stop in the night, served by the venue at least partially. The #1
   is already guaranteed by rules 1–8; this extends it to a firm #2 (a person at `PLAY` 90 and
   `FOOD` 80 gets a night with games *and* a proper meal, not games twice). Uncovered firm wants
   pull the remaining stops toward venues that have them (`COVER_K` 0.4 per want, in the served
   total), and any still uncovered at the end are reported on the card and logged as a venue gap.

```python
def pick_stops(members, candidates, n_stops):
    wanting = [m for m in members if ranked_wants(m)]                         # rule 4
    # rule 8 - look ahead
    def gate(v): return passes(v, members, {x.id: serve_level(v, x) for x in members})
    reach    = {m.id: max([serve_level(v, m)[0] for v in candidates if gate(v)] or [0.0]) for m in wanting}
    reserved = sorted([m for m in wanting if reach[m.id] < SERVED_FLOOR], key=lambda m: -debt_scale(m))
    held = {}
    for m in reserved:                                     # build the reserved stops now; hold their venues
        ded = dedicated_stop(m, [v for v in candidates if v not in held.values()], members)
        if ded is None: return NOT_A_FIT                   # a hard refusal blocks every such venue - say so before anyone joins
        held[m.id] = ded.venue
    required = len(reserved) + (1 if any(m not in reserved for m in wanting) else 0)
    if required > n_stops:
        if required > MAX_STOPS: return NOT_A_FIT
        n_stops = required
    ordinary = n_stops - len(reserved)
    debt, paid_tonight, had_own, pending = {m.id: 0.0 for m in members}, set(), set(reserved), None
    chosen, prev_energy = [], -1
    for k in range(n_stops):
        last      = k == n_stops - 1
        remaining = [v for v in candidates if v not in chosen and (k >= ordinary or v not in held.values())]
        pool      = [v for v in remaining if v['ENRG'] >= prev_energy - 10] or remaining   # rule 3
        if k >= ordinary:                                                      # rule 8 - a reserved slot
            stop = dedicated_stop(reserved[k - ordinary], remaining, members)
            if stop is None: return relax_and_retry(members, candidates, n_stops)
            chosen.append(stop.venue); prev_energy = stop.venue['ENRG']; continue
        owed      = [m for m in wanting if debt[m.id] >= DEBT_TRIGGER
                     and m.id not in paid_tonight and m not in had_own]        # rule 1
        stop = None
        if pending:                                                            # rule 5/6: the promised stop
            stop = dedicated_stop(pending, remaining, members); had_own.add(pending); pending = None
        else:
            stranded = [m for m in wanting if m not in had_own and
                        not any(serve_level(v, m)[0] > 0 and in_bend(v, members) for v in remaining)]
            if len(stranded) >= 2:            return relax_and_retry(members, candidates, n_stops)   # §13.1
            if stranded:
                m = stranded[0]
                if got_something(m):          had_own.add(m)                   # zeros accepted from here
                else:
                    ded = dedicated_stop(m, remaining, members)
                    if ded is None:           return relax_and_retry(members, candidates, n_stops)   # a hard refusal blocks it
                    if last: stop = ded; had_own.add(m)
                    else:    pending = m
            if stop is None:
                if owed:                                                       # rules 2, 7
                    target = {o.id: payback_target(o, remaining, members) for o in owed}   # highest rank the group's bends allow
                    pays = lambda v: all(serve_level(v, o)[1:] == (target[o.id], 'venue') for o in owed if target[o.id]) and in_bend(v, members)
                    pool = [v for v in pool if pays(v)] or [v for v in remaining if pays(v)] or pool
                stop = pick_best(pool, members, debt, ignore_zero=had_own | ({pending} if pending else set()), first=(k == 0))
                if stop is None:              return relax_and_retry(members, candidates, n_stops)
        chosen.append(stop.venue); prev_energy = stop.venue['ENRG']
        for m in wanting:
            lvl, f, how = stop.levels[m.id]
            paid = (m in owed and f == target.get(m.id) and how == 'venue') or stop.dedicated_to == m.id
            debt[m.id] = 0.0 if paid else debt[m.id] + (1.0 - lvl) * debt_scale(m)   # §13.8
            if paid or (lvl == 1.0 and how == 'venue'): paid_tonight.add(m.id)
    return chosen

def payback_target(m, remaining, members):
    """Rule 7: the highest-ranked want of m's that some remaining venue delivers by the venue
    with everyone in bend. None if no want of theirs is reachable - then the debt just leans."""
    for f in ranked_wants(m):
        if any(delivers_at(v[f], m, f) and in_bend(v, members) for v in remaining): return f
    return None

def over_points(venue, m):
    """Points past m's aversion ceiling, summed - only where the venue is at or above AVERSION_FLOOR."""
    return sum(max(0.0, overrun(venue, m, f)) for f in FACTORS if m.scores[f] < 50 and venue[f] >= AVERSION_FLOOR)

def passes(venue, members, levels):
    """Rule 9: a hard refusal is a wall for everyone; a person served on nothing must be inside
    their bend; a person served on anything may be overrun - it costs, it does not bar."""
    if any(violated(venue, m, f) for m in members for f in m.refused): return False
    return all(levels[m.id][0] > 0 or over_points(venue, m) == 0 for m in members)

def pick_best(pool, members, debt, ignore_zero=(), first=False):
    best = None
    for v in pool:
        levels = {m.id: serve_level(v, m) for m in members}
        if not passes(v, members, levels): continue
        nobody = sum(1 for m in members if m not in ignore_zero and ranked_wants(m) and levels[m.id][0] == 0)
        served = sum(l[0] * (1 + DEBT_K * debt[i]) for i, l in levels.items())
        cost   = OVERRUN_W * sum(over_points(v, m) for m in members)
        key    = (-nobody, round(served, 2), -v['ENRG'] if first else 0, -cost)   # rule 9's order
        if best is None or key > best[0]: best = (key, Stop(v, levels))
    return best[1] if best else None

def in_bend(venue, members):
    """Kept for §13.4a (the joiner's gate) and friend mode's relaxed ceilings; inside pick_stops
    the gate is passes(), above."""
    return not any(over_points(venue, m) > 0 for m in members)

def dedicated_stop(m, pool, members):
    """Rule 6: m's own bend holds at m's own stop. Try m's #1, then #2. Among venues that deliver
    it, the one where the others are served best and stepped on least. A hard refusal is a wall."""
    others = [o for o in members if o is not m]
    for f in ranked_wants(m)[:2]:
        ok = [v for v in pool if delivers_at(v[f], m, f) and in_bend(v, [m])
              and not any(violated(v, o, g) for o in others for g in o.refused)]
        if not ok: continue
        def key(v):
            served = sum(serve_level(v, o)[0] for o in others)
            over   = sum(max(0, overrun(v, o, g)) for o in others for g in FACTORS if o.scores[g] < 50)
            return (served - OVERRUN_W * over, v[f])
        v = max(ok, key=key)
        levels = {m.id: (1.0 if f == ranked_wants(m)[0] else STRONG2, f, 'venue'), **{o.id: serve_level(v, o) for o in others}}
        return Stop(v, levels, dedicated_to=m.id)
    return None
```

#### Nine rooms, run through it

Eight venues, four areas, three-stop nights unless stated. Levels are what each person was served
at; *(area)* means the street carried it; **PAID** is a payback landing.

```
B. weak #2 -> payback; the others on their strong #2
   Aarav ENRG 88 CROWD 80 · Divit the same · Neha FOOD 90 SCEN 62 (weak #2)
   1 busy diner (CP)       Aarav CROWD #2 .85   Divit CROWD #2 .85   Neha FOOD #1 1.0
   2 lively bar (CP)       Aarav ENRG #1 1.0    Divit ENRG #1 1.0    Neha SCEN #2 .5 (area)   -> Neha owed
   3 club (Aerocity)       Aarav ENRG #1 1.0    Divit ENRG #1 1.0    Neha SCEN #2 .5          -> not owed: her #1 came at stop 1 (rule 1)

C. weak #2 -> payback; the others have no #2 -> the area carries their #1; stop 3 pays them
   Aarav ENRG 88 only · Divit the same · Neha FOOD 90 SCEN 62
   1 lively bar (CP)       Aarav ENRG #1 1.0    Divit ENRG #1 1.0    Neha SCEN #2 .5 (area)   -> Neha owed
   2 busy diner (CP)       Aarav ENRG #1 .5 (area)  Divit .5 (area)  Neha FOOD #1 1.0 PAID    -> "restaurant on a pub street"
   3 club (Aerocity)       Aarav ENRG #1 1.0    Divit ENRG #1 1.0    Neha SCEN #2 .5          -> the night builds

E. the quaint pub - two stops
   Priya AFFIL 92, ENRG 20, CROWD 25 · Sana SCEN 90 POL 80 · Ria SCEN 85 POL 75
   1 quiet restaurant (HKV) Priya AFFIL #1 1.0  Sana POL #2 .85      Ria POL #2 .85
   2 quaint pub (HKV)      Priya AFFIL #1 1.0   Sana SCEN #1 .5 (area)  Ria SCEN #1 .5 (area)
   The rooftop lounge would serve Sana and Ria on SCEN by the venue - and is outside Priya's bend on
   ENRG. So the pub on the pretty street: Priya's night by the venue, theirs by the neighbourhood.

F. the dedicated stop
   Aarav ENRG 85 CROWD 80 LIVE 15 · Divit the same · Ruchi LIVE 92 HERIT 62
   1 lively bar (CP)       Aarav ENRG #1 1.0    Divit ENRG #1 1.0    Ruchi -  0            -> stranded; her stop is next
   2 gig venue             Aarav -  0           Divit -  0           Ruchi LIVE #1 1.0 PAID -> DEDICATED; their bend not checked
   3 club (Aerocity)       Aarav ENRG #1 1.0    Divit ENRG #1 1.0    Ruchi -  0            -> her zeros accepted from here

G. same, but Divit hard-passed LIVE      -> no dedicated stop can be built: relax (§13.1) / not a fit
H. two firm camps, nothing in common     -> both stranded: not one person left out, a room that does not work
I. one firm person, two with no wants    -> Aarav's night; Divit and Neha take on no debt (rule 4)
A. strong #2 everywhere                  -> nobody is ever owed; stop 3 drops the arc for the late diner (rule 3)
D. two owed on different factors         -> paid one stop at a time, most owed first; Kabir's arcade at stop 1 counts (rule 1)
```

#### What the plan card gets

Per person per stop: the factor, and whether the venue or the area is carrying it — *"for Aarav,
the street outside is buzzing"* against *"for Aarav, a loud room."* A payback stop gets one line:
*"This one's Neha's — the room owed her the food."* A dedicated stop gets one more, honest, for the
others: *"This one's for Ruchi. Next stop's yours."* A member with no wants gets their line from
bend: *"nothing here Divit minds."*

**Constants, all set:** `SECOND_STRONG` 70, `SECOND_GAP` 10, `STRONG2` 0.85, `SOFT` 0.5,
`DEBT_TRIGGER` 0.5, `SERVED_FLOOR` 0.85, `AVERSION_FLOOR` 55. Tune when the first real plans are rated.

#### Seven more rooms, run after the 2026-09-17 refinements (rules 5–7, §13.8, §13.9)

```
F'. dedicated stop, others softened - a heritage restaurant now exists in the pool
   1 haveli restaurant       Aarav CROWD #2 .85   Divit CROWD #2 .85   Ruchi HERIT #2 .5   -> half a reason, not a serving
   2 lively bar              Aarav ENRG #1 1.0    Divit ENRG #1 1.0    Ruchi -  0          -> nothing reachable ahead: her stop is next
   3 gig venue               Aarav ENRG #1 1.0    Divit ENRG #1 1.0    Ruchi LIVE #1 1.0   -> DEDICATED; the gig is loud, so they are served too

J. payback lands on #2 because #1 is blocked by the others' bends
   Ruchi LIVE 92 FOOD 75 SCEN 64 among two who are firm-low on LIVE
   1 lively bar   Ruchi SCEN #3 .5 (area)   2 club   Ruchi SCEN #3 .33   3 busy diner   Ruchi FOOD #2 1.0 PAID  <- LIVE unreachable, FOOD is

K. opinionated vs easy - the same concession costs different debt
   Aarav (five extreme swipes) x1.0 per point; Neha (one) x0.6.   Both stops serve both; nobody owed.

L. FRIENDS: A LIVE 0 / ENRG 90; B LIVE 88 / POL 85
   1 bar with live band      A ENRG #1 1.0 (stretched on LIVE to ~70)   B LIVE #1 1.0
   2 club                    A ENRG #1 1.0                               B POL #2 .85
O. the same two, NOT friends
   1 club                    A ENRG #1 1.0        B POL #2 .85
   2 quiet restaurant (HKV)  A ENRG by area .5    B POL #2 .85        -> arc dropped so nobody gets nothing; B never gets LIVE

M. FRIENDS: A LIVE / CROWD; B POL / SCEN / FOOD; no POL+LIVE venue
   1 club                    A CROWD #2 .85       B POL #1 1.0        <- A's LIVE with B's #1, #2, #3 all failed; A's #2 with B's #1 found
   2 rooftop lounge          A CROWD #2 .85       B POL #1 1.0        -> arc dropped for the pairing

N. FRIENDS: A PLAY only; B HERIT only; nothing joins them
   1 arcade bar              A PLAY #1 1.0        B -  0              -> DEDICATED to A
   2 haveli restaurant       A -  0               B HERIT #1 1.0      -> DEDICATED to B

S. the mutual wall (rule 8) - Aarav ENRG 88 CROWD 70, hates LIVE and HERIT · Bela LIVE 88 SCEN 70, hates ENRG · Chirag FOOD 88, hates HERIT
   reach: Aarav .5, Bela .5 (each one's #1 is the other's firm aversion) -> two stops reserved
   1 quiet restaurant (HKV)  Aarav ENRG by area .5   Bela SCEN #2 .5     Chirag FOOD #1 1.0   <- everyone's stop
   2 arcade bar              Aarav ENRG #1 1.0       Bela SCEN by area .5  Chirag -  0        <- Aarav's; loud but no act (his own bend held); steps on Bela least
   3 jazz bar (Lodhi)        Aarav -  0              Bela LIVE #1 1.0     Chirag -  0         <- Bela's; an act with no energy (her own bend held)
   Before rule 8 this room spent two stops in Hauz Khas on half-reasons and was declared not a fit at the third.
   The same three as FRIENDS: rooftop -> diner -> live-band bar; Aarav stretches on live, Bela on energy; nobody needs a stop of their own.

H. two firm camps, two stops (re-run under rule 8)
   1 arcade bar              Aarav ENRG #1 1.0    Neha -  0            <- Aarav's; the club would have stepped on Neha harder
   2 quiet restaurant (HKV)  Aarav ENRG by area .5  Neha FOOD #1 1.0   <- Neha's

U. the user's Piano Man room (rule 9) - Aarav ENRG 88 CROWD 70, hates LIVE · Bela LIVE 88, hates ENRG, milder on CROWD · Chirag FOOD 88
   1 Piano Man (Safdarjung)  Aarav CROWD #2 .5    Bela LIVE #1 1.0     Chirag FOOD #1 1.0   <- everyone served; Aarav's #1 took the hit
   2 Depot 48 (GK-2)         Aarav ENRG #1 1.0    Bela LIVE partial .5  Chirag FOOD #1 1.0  <- Aarav compensated; energy 65, not 92, because Bela is stepped on least there
   Under the old gate Piano Man was out (its act overran Aarav's LIVE) and this room needed one stop each.

S. the mutual wall, re-run under rule 9 - no reserved stops needed any more
   1 Piano Man               Aarav CROWD #2 .5    Bela LIVE #1 1.0     Chirag FOOD #1 1.0
   2 Depot 48                Aarav ENRG #1 1.0    Bela SCEN #2 .5      Chirag FOOD #1 1.0
   3 rooftop lounge          Aarav CROWD #2 .5    Bela SCEN #2 .5      Chirag FOOD #1 1.0

G. Ruchi LIVE 92 HERIT 62; Divit hard-passed LIVE (re-run)
   reach: Ruchi .5 -> reserved; her #1 is walled by a hard pass, so her stop is her #2
   1 busy diner   2 lively bar   3 haveli restaurant  Ruchi HERIT #2 .85 (hers)   Aarav/Divit CROWD #2 .85
```

### 13.4d The other side of bend — a solo plan, and the room you want to join

**Decided 2026-09-17.** Everything in §13.4c stretches people toward each other. Two places do
the opposite, and bend is a **gate** there:

**A plan for one person** (the solo Create flow — *"the plan being created is catered just to
you"*). No stretching, because there is nobody to stretch toward:

```python
def solo_plan(user, candidates, n_stops):
    pool = [v for v in candidates if over_points(v, user) == 0 and not any(violated(v, user, f) for f in user.refused)]
    chosen, covered = [], set()
    for k in range(n_stops):
        best = max((v for v in pool if v not in chosen),
                   key=lambda v: (serve_level(v, user)[0], sum(1 for f in firm_wants(user) if f not in covered and v[f] >= DELIVERS),
                                  -v['ENRG'] if k == 0 else 0, -room_cost([user], v)), default=None)
        if best is None: return relax_and_retry([user], candidates, n_stops)
        chosen.append(best); covered |= {f for f in ranked_wants(user) if best[f] >= DELIVERS}
    return chosen
```

Every stop inside their bend; each stop the best serving available — their #1 by the venue where
it exists, partials only when nothing better does; firm wants covered across the night; the arc
as before. Relaxation (§13.1) only if their own wants contradict each other in the venue set.

**A room somebody wants to join** (§13.4a). The plan is frozen and was stretched for *other*
people; the question is whether it is theirs. Every stop must be inside the joiner's bend
(`over_points == 0`, and no hard refusal violated) and must serve them on something — a
stop that gives them nothing, or steps on an aversion, hides the room. Rule 9's "served
compensates" does not apply to a joiner: they did not get a say in the stretch.

### 13.5 Bend — three levels of latency, logged as direction

`DECISIONS.md` 2026-09-12. Post-validation. **Level 1:** replace the score-firmness term in
`user_bend()` with combined firmness — one line. **Level 2:** latency decides how much to trust the
archetype versus the person's own score — `lerp(archetype_bend, own_bend, firmness_latency)` —
which changes what bend means, from "archetype scaled by the person" to "the person, with the
archetype as fallback." **Level 3:** `BEND_FLAGS` measured from latency across users of each vibe
rather than hand-written. Level 1 ships with validation; level 2 is the one to design properly;
level 3 waits for volume.

### 13.6 Room chemistry — debt, payback, seven states, and the match

**Decided 2026-09-17.** Blend style (`BLEND_STYLE_DATABASE_V2.md`) is the room's *identity* — a
name, a colour, a vector. Chemistry is *how the room got there*: who is set on what, who is easy,
who is owed something. It is read off the same firmness structure that gives bend — no new
inputs — and it does three things: it can move the room vector by **paying back** a member whose
top factor lost out; it puts one positive word on the room card; and it grades joiners.

This amends the 2026-09-04 rule that chemistry never moves the target vector. It still never
*invents* a value. It only makes one member's stated vote on one factor count more, as a debt,
and never past what the others can live with.

#### 13.6.1 Concession, debt, payback — the rule

*Everyone's top factor should get served. If yours is not, the room owes it to you.*

```python
FIRM, ABSTAIN = 0.5, 0.15        # firmness cut-points: set on a position / sitting it out
DEFINING      = 25               # |room[f] - 50| >= 25 -> f is a defining factor of the room
RECIP         = 2.0              # payback: the owed member's vote on their top factor counts (1 + RECIP x debt_scale(m)) times (§13.8)
DEBT_ALLOW    = 10               # points past a firm member's bend the room may go, for a friend
PAYBACK_MIN   = 10               # a move smaller than this is not a payback
UNDEF         = 0.05             # abstention: total weight below this -> factor undefined

def room_vector(members, boost={}):
    v = {}
    for f in FACTORS:
        w = {m.id: m.firmness[f] * boost.get((m.id, f), 1.0) for m in members}
        v[f] = None if sum(w.values()) < UNDEF else \
               sum(w[m.id] * m.scores[f] for m in members) / sum(w.values())
    return v

def served(m, f, value):
    """Does the room's value on f sit inside m's own bend on f (§5.3 / §13.3)?"""
    return value is not None and overrun_points(m, f, value) <= 0

def owed(members, v):
    """Members whose top factor the room does not deliver. Their concession is the top factor
    itself - it lost out to somebody else's - and the debt is one, paid on that factor."""
    return [m for m in members if not served(m, m.top, v[m.top])]

def payback(members):
    v0    = room_vector(members)
    debt  = owed(members, v0)
    boost = {(m.id, m.top): 1 + RECIP for m in debt}
    v1    = room_vector(members, boost)
    paid, unpaid = [], []
    for m in debt:
        f = m.top
        # cap: no firm member is pushed past their bend plus the allowance
        lo, hi = 0, 100
        for o in members:
            if o is m or o.firmness[f] < FIRM: continue
            allow = 0 if f in o.refused else DEBT_ALLOW          # a hard pass caps with no allowance
            lo = max(lo, o.scores[f] - bend_points(o, f, 'down') - allow)
            hi = min(hi, o.scores[f] + bend_points(o, f, 'up')   + allow)
        v1[f] = min(max(v1[f], lo), hi)
        v1[f] = max(v1[f], v0[f]) if m.scores[f] > 50 else min(v1[f], v0[f])   # the cap never moves the room AWAY from the owed member
        (paid if abs(v1[f] - (v0[f] or 50)) >= PAYBACK_MIN else unpaid).append((m.id, f))
    return v1, paid, unpaid
```

`bend_points(o, f, dir)` is the member's bend on `f` in that direction, in score points, from
§5.3 with the latency multiplier when validated (§13.5). `hi` is `o.scores[f] + bend + DEBT_ALLOW`;
`lo` the mirror.

- **One concession, one payback.** The owed member's vote counts more on their *top* factor only.
  Not on everything they care about — one sentence has to explain it: *"the room went with
  Aarav's energy, so Kabir gets the say on dress code."*
- **The cap is the compromise.** The others accept up to `DEBT_ALLOW` points past their own
  bend, for a friend. Not further. If the cap stops the move short of `PAYBACK_MIN`, the debt is
  **unpaid** at the room level and carried into the plan: §13.4c's stop-level debt serves their
  top factor at the next stop, by the venue, alongside the others' seconds. Never a stop of their
  own — unless nothing of theirs can be served any other way (§13.4c, the dedicated stop).
- **Nobody's served top factor can be unseated by a payback**, because the cap keeps every firm
  member inside bend + allowance on the factor being moved.

**Worked example** — base bend 20 points for illustration.

| | `ENRG` | `POL` |
|---|---|---|
| Aarav | 90 (firm 0.8) | 25 (firm 0.5) |
| Divit | 90 (firm 0.8) | 25 (firm 0.5) |
| Kabir | 55 (0.1 → abstains) | 80 (firm 0.6) — his top |
| room, abstention | **88** | 46 |
| Kabir's top `POL` not served (46 is outside his bend) → owed → `POL` vote × 3 | | |
| room, after payback | **88** | **60** |
| cap: Aarav/Divit tolerate `POL` to ~57, + 10 = 67 → 60 is inside → **paid** | | |

Nearest style moves toward *Big Room, Loud Night* (`POL` 65). The plan, scoring venues against
the paid vector, lands on the dressed-up club. The two who wanted the big night still get it.

#### 13.6.2 The seven states

Read after payback. One state per room; the display word is what the card shows.

| code | display | detected when | room vector |
|---|---|---|---|
| `DRIFT` | **Open Night** | nobody is firm (≥ `FIRM`) on any factor | mostly undefined — no plan until someone firm joins (§13.6.4) |
| `TUG` | **Something for Everyone** | somebody is owed and unpaid on a factor where firm members sit on *opposite* sides | the majority firm side's; the plan pays the owed side at the next stop (§13.4c) |
| `TRADE` | **Best of Both** | two or more paybacks on two or more different factors | raised on both — *Supper and a Set* is this room |
| `COMPROMISE` | **Got Your Back** | at least one payback landed | adjusted by payback |
| `ANCHORED` | **Along for the Ride** | exactly one member firm on anything; everyone else abstains nearly everywhere and is not owed | one person's vibe; the host is told so |
| `SPARK` | **Could Go Late** | no member firm-low on `ENRG`, every member ≥ 55 on it, and `ENRG` is *not* already defining-high | unchanged; the plan keeps a goes-late hedge stop (§4.4) |
| `LOCKSTEP` | **In Sync** | everything else — firm, same direction, nobody owed | plain abstention |

```python
def chemistry(members, v, paid, unpaid):
    firm_any = [m for m in members if any(m.firmness[f] >= FIRM for f in FACTORS)]
    if not firm_any:                                                     return 'DRIFT'
    defining = [f for f in FACTORS if v[f] is not None and abs(v[f] - 50) >= DEFINING]
    if any(opposed(members, f) for _, f in unpaid):                      return 'TUG'   # opposed on a factor somebody is owed and not paid
    if len({f for _, f in paid}) >= 2:                                   return 'TRADE'
    if paid:                                                             return 'COMPROMISE'
    if len(firm_any) == 1 and len(members) >= 2:                         return 'ANCHORED'
    if all(m.scores['ENRG'] >= 55 for m in members) \
       and not any(m.firmness['ENRG'] >= FIRM and m.scores['ENRG'] < 50 for m in members) \
       and 'ENRG' not in defining:                                       return 'SPARK'
    return 'LOCKSTEP'

def opposed(members, f):
    firm = [m for m in members if m.firmness[f] >= FIRM]
    return any(a.scores[f] > 50 for a in firm) and any(b.scores[f] < 50 for b in firm)
```

**Retired:** `FRICTION` ("too many leaders") — it was built on agency, and agency is gone
(2026-09-04). The old `SPLIT` is now two states, because they are two different nights: `TUG`
(opposed on the *same* factor) and `TRADE` (firm on *different* factors, each paid).

The display words are positive by design and are the room-card label — a chip next to the
blend-style name: *Big Room, Loud Night · Got Your Back*. The codes are for the developer and
the log. The words are the first draft; `REMINDERS.md` has the note to revisit them after
testing.

#### 13.6.3 The match — how much a joiner changes the room, and whether they fit its chemistry

For each candidate room, add the joiner, re-run abstention, payback and the state, and read:

```python
def match(joiner, room):
    if room.state == 'DRIFT':
        # an open night thrives on opinions: the more firm positions the joiner has, the better
        n_firm = sum(1 for f in FACTORS if joiner.firmness[f] >= FIRM)
        return 'great' if n_firm >= 5 else 'alright'
    before   = room.vector
    v, paid, unpaid = payback(room.members + [joiner])
    after    = chemistry(room.members + [joiner], v, paid, unpaid)
    defined  = [f for f in FACTORS if before[f] is not None]   # only where the room HAD a position
    shift    = sum(abs(before[f] - (v[f] if v[f] is not None else before[f])) for f in defined) / (50 * max(1, len(defined)))
                                                             # average points moved per defined factor, over 50.
                                                             # a joiner bringing a position on a factor the room
                                                             # was indifferent to is not a shift - the room did not care
    defining = [f for f in FACTORS if before[f] is not None and abs(before[f] - 50) >= DEFINING]
    reinf    = mean(joiner.firmness[f] * (1 if (joiner.scores[f] - 50) * (before[f] - 50) > 0 else -1)
                    for f in defining) if defining else 0.0   # what they add to what the room already is
    worse    = after == 'TUG' and room.state != 'TUG'
    if worse or shift > SHIFT_POOR:                         return 'poor'
    if room.state == 'TUG':
        contested = [f for f in defining if opposed(room.members, f)]
        if all(joiner.firmness[f] < ABSTAIN for f in contested) and reinf >= 0.3:
            return 'great'                                  # glue, not weight
    if shift <= SHIFT_GREAT and reinf >= REINF_GREAT:       return 'great'
    return 'alright'

SHIFT_GREAT, SHIFT_POOR, REINF_GREAT = 0.10, 0.20, 0.5     # 5 and 10 points average per defined factor; set; adjust from data
```

In words, per state — what a joiner needs to be:

| room is | great | alright | poor |
|---|---|---|---|
| In Sync | firm, same direction, on the defining factors | easy on them | firm-opposite on any — nobody here has debt to pay |
| Got Your Back | firm-high on the defining factor *or* the paid-back one | easy on both | firm-low on either — the room is committed to two things now |
| Best of Both | firm-high on either camp's factors | easy on both | firm-low on either |
| Along for the Ride | matches the anchor's firm factors | another easy-going person | a second anchor who disagrees → Tug |
| Something for Everyone | easy on the contested factor, firm on something both sides share | firm on the majority side | firm on the minority side |
| Open Night | **firm on five or more factors — the perfect match** | anyone | nobody |
| Could Go Late | firm-high `ENRG` | mild | firm-low `ENRG` — the first blocker |

**The gate is still the plan.** A hosted room's plan is frozen (§13.4, entry 81); a room whose
plan gives the joiner nothing at some stop is **hidden** whatever the chemistry (§13.4a). Among
the rooms that pass, the match above does the sorting and the two bands: *great* → "Strong
match", *alright* → "Other rooms", *poor* → hidden. This replaces the 2026-09-16 band rule
("strong = served on #1 at some stop"), which is now part of the gate, not the band. Open Night
rooms have no plan yet and therefore no gate — they are listed for everyone.

**The host's request list** uses the same `match` — it *is* the "how much does this person
change our blend style" check the flow doc always had, made precise, with the chemistry on top.

#### 13.6.3a After hosting, the chip freezes with the plan

Blend style (name, colour) keeps recomputing as joiners arrive — by abstention only. The
**chemistry word does not**: it is frozen at hosting along with the plan, and room-level payback
is not re-run for joiners. A joiner is gated on the frozen plan and matched on the frozen
identity; if the chip re-ran with them in it, a room could read *Got Your Back* for a payback
the plan never made. Joiners never see debt (§13.4c head), so they never see a chip that
promises one.

#### 13.6.4 Open Night rooms are hosted without a plan, and the first firm joiner makes one

A `DRIFT` room has nothing to plan from — every factor is undefined or flat — and a generic
popular night would be a plan nobody asked for. So an Open Night is hosted **without a plan
card**. The room list shows it as *Open Night* with the line *"No direction yet — whoever joins
with one, sets it."* A joiner with five or more firm factors is its perfect match and is told
before requesting: *"This room's an open night. You'd be setting the direction."*

The moment the room stops being `DRIFT` — any member firm on anything — the plan generates
(§13.4, for everyone then in the room) and **freezes as if the room had just been hosted**. From
there it is an ordinary room: refresh gone, joiners gated by the plan. This is not an exception
to *hosting freezes the plan*; there was no plan to freeze, and the freeze happens at the first
moment there is one.

#### 13.6.5 Constants

| | value | adjust when |
|---|---|---|
| `FIRM` / `ABSTAIN` | 0.5 / 0.15 | the firmness distribution across real users is known |
| `DEFINING` | 25 | — |
| `RECIP` | 2.0 | paybacks are measured: how often they land, how far they move |
| `DEBT_ALLOW` | 10 | members report a paid-back stop as too much |
| `PAYBACK_MIN` | 10 | — |
| `SHIFT_GREAT` / `SHIFT_POOR` / `REINF_GREAT` | 0.10 / 0.20 / 0.5 | join-accept rates per band are measured |
| Open Night perfect-match threshold | 5 firm factors | — |

All set. The 2026-09-03 finding stands — the *distribution* of states across real rooms cannot be
simulated (random strangers gave 60% split, friend groups 0%) — but with the states now defined
from firmness and debt rather than from thresholds on `CONSENSUS`, the cut-points are the
constants above and the first real rooms tune them.

`CONSENSUS` (2026-09-03) is kept as a logged number per room. It no longer decides a state.

### 13.7 Location as a fallback — the area can carry `CROWD`, `ENRG`, `POL` or `SCEN` when the venue cannot

**Decided 2026-09-17, corrected the same day.** The venue is what matters. But four factors are
also a property of *where* a venue is — how busy the street is, how the night around it is
building, how dressed the area expects you to be, what it looks like when you step out — and
when a venue cannot serve somebody on one of those, the area around it sometimes can. A quaint
pub in an aesthetic neighbourhood: the pub serves the friend who wants her own people and a
low-energy night; the neighbourhood serves the two who wanted somewhere beautiful. That is the
only job location has: **a reason to be there, at half strength, when the venue itself is not
one.**

**What it is not.** It does not raise a venue's score. It does not count against anyone — a
crowd-hater's bend is checked against the venue alone. It is not a factor in matching. A venue
that serves a want on its own never needs its area; the area is consulted only for a want the
venue fails to deliver, and only for these four factors.

**Data.** Every venue gets an `area` (a named neighbourhood: Hauz Khas Village, Aerocity, CP,
Cyber Hub, Mehrauli, Khan Market …). Every area gets scores on the four factors, **per time
band** — early evening, late evening, after midnight — because the crowd and the energy of a
street change through the night in a way its dress code and its look do not. First source: the
footfall-weighted median of the venues already scored in that area, per band; `POL` and `SCEN`
checked by hand. An area with no data is `None` and the fallback never fires. **The first-pass
table is `AREA_SCORES_V1.md`** — 35 neighbourhoods, three bands, with the tagging rules and the
replacement method.

**Where it is used.** One place: `serve_level` (§13.4c) — a want the venue cannot deliver but
the area can is served at `SOFT`, tagged `'area'`, and the plan card says which it was. Serving
by the area leaves 0.5 of debt, so the room still owes that person the real thing at a later
stop if their #1 has not been served yet.

**Not used for** `FOOD`, `PLAY`, `LIVE`, `HERIT`, `NOV`, `AFFIL` — those are the venue's alone.

### 13.8 Overall firmness — how opinionated a person is, and what it does to their debt

**Decided 2026-09-17.** Firmness so far is per factor. There is also a per-person quantity: how
opinionated somebody is *in general*. A person who swipes fast on nearly every card, or lands in
the extremes more often than most people, holds their positions harder across the board than a
person who is firm on two or three factors and easy on the rest. Concession costs the first more
than the second, and the room should owe them sooner.

```python
def overall_firmness(session, population):
    """0-1, a population percentile. Two halves; the latency half joins once §6.3 validates."""
    extreme = sum(1 for a in session.answers if a.swipe in ('love', 'pass')) / len(session.answers)
    score_half = percentile(extreme, population.extreme_share)
    if not population.latency_validated: return score_half
    lat = mean(session.firmness_latency.values())
    return 0.5 * score_half + 0.5 * percentile(lat, population.latency_firm_mean)

def debt_scale(m):           # multiplies every debt increment in §13.4c
    return 0.5 + m.overall_firmness            # 0.5 for the easiest person, 1.5 for the most opinionated
```

So a weak-#2 stop costs an opinionated person 0.75 of debt — over the 0.5 trigger in one stop —
and an easy person 0.25, who needs two before the room owes them. The same scale multiplies
`RECIP` in the room-level payback (§13.6.1): the opinionated person's vote is amplified more
when their top factor lost out. Stored on the assessment record (`ASSESSMENT_ENGINE.md` §10);
recomputed each session; the learning layer (`PREFERENCE_ENGINE_V2.md`) keeps a running value.

**Constants:** the 0.5–1.5 range. Set; adjust when paid-back stops are rated by the people they
were paid to.

### 13.9 Friend mode — relaxed bends instead of debt, for people who go out together

**Decided 2026-09-17.** Two people who keep planning nights together are not strangers
negotiating; they are friends who give way to each other without keeping score. For them the
debt machinery is the wrong model. The right one: **each friend's bend is relaxed toward the
other's firm wants, and every stop is built from one want of each — whichever combination a
real venue can actually serve.** No concession, no debt, no payback.

#### 13.9.1 Who counts as a friend, in the engine's sense

The app's friend list is the candidate set — you can only plan with people you have added. Being
a friend *to the engine* is behavioural, pairwise, and recomputed nightly:

```python
FRIEND_THRESHOLD = 3.0
def friend_score(a, b, days=90):
    return 1.0 * plans_generated_together(a, b, days) \
         + 0.5 * rooms_shared(a, b, days) \
         + 0.1 * interactions(a, b, days)            # messages, profile views, invites either way
friends = friend_score(a, b) >= FRIEND_THRESHOLD     # roughly: three plans together
```

Roughly three plans together in three months. Two people who add each other and plan once are
not friends yet — they get debt and payback, which is the fairer model for people still finding
out what each other wants. Rooms of three or more: friend mode runs only if **every pair** is
friends; a mixed room runs §13.4c with the friend-pair relaxations of §13.9.2 applied to the
bends.

#### 13.9.2 Relaxed bends

On any factor where one friend is firm-low and the other firm-high, the low one's tolerance
stretches to the point where the high one's want can actually be delivered:

```python
FRIEND_MAX_GIVE = 70                    # points; nobody is stretched further than this for a friend
FRIEND_MARGIN   = 10                    # the ceiling sits this far above b's floor, so venues just over it are not lost to rounding

def relaxed_ceiling(a, b, f):
    """a is firm-low on f (score < 40, firmness >= FIRM); b is firm-high (>= 60, firmness >= FIRM).
    a's overrun ceiling on f rises to b's delivery floor plus a margin, capped."""
    own   = a.scores[f] + 100 * user_bend(a.vibe, a.scores, f, 'up')
    need  = b.scores[f] - 100 * user_bend(b.vibe, b.scores, f, 'down')      # what delivers b (§13.4)
    return min(max(own, need + FRIEND_MARGIN), a.scores[f] + FRIEND_MAX_GIVE)
```

Friend A at `LIVE` 0, friend B at `LIVE` 88: B's delivery floor is about 64, so A's ceiling on
`LIVE` rises from ~20 to ~70 (64 + 10, capped at 0 + 70) — a bar with a live act at 65 is inside
A's relaxed bend *and* serves B; a gig venue at 92 still is not. The inverse runs the same way on
A's top factor. It is symmetric, per factor, per pair, and it changes **bends only** — nobody's
score, and not the room vector. `AVERSION_FLOOR` applies here too: a venue under 55 on `LIVE`
never counts against A at all.

**Log the stretch.** Per stop, per friend: how many points past their *own* bend the venue sits on
each factor they were stretched on. It is the card's honesty line — *"Aarav stretched on live
music for Neha tonight"* — and it is the number that tunes `FRIEND_MAX_GIVE`.

#### 13.9.3 The stop — one want of each, against real venues

```python
MAX_RANK = 4

def friend_stop(members, remaining, lead):
    """lead: the member whose #1 gets first claim at this stop (rotates, §13.9.4)."""
    wants = {m.id: ranked_wants(m)[:MAX_RANK] for m in members}
    combos = sorted(product(*[[(m, f) for f in wants[m.id]] for m in members]),
                    key=lambda c: (0 if c[members.index(lead)][1] == wants[lead.id][0] else 1,
                                   sum(wants[m.id].index(f) for m, f in c)))       # lead's #1 first, then lowest total rank
    for combo in combos:
        ok = [v for v in remaining if all(delivers_at(v[f], m, f) for m, f in combo)
                                     and in_bend_relaxed(v, members)]
        if ok: return min(ok, key=lambda v: room_cost(members, v)), combo, None
    return None, None, 'no venue serves any combination'
```

Order: the lead's #1 with the others' #1s; then the lead's #1 with the others' #2s and #3s; then
lower. The first combination a real venue satisfies is the stop. The energy arc yields to the
pairing exactly as it yields to payback in §13.4c: try inside it, then everywhere. This is the user's rule — A wants
`LIVE`, B wants `POL`, there is no `POL` + `LIVE` venue in Delhi, so try B's #2 with A's `LIVE`,
then B's #3, and if B has nothing that pairs, A's #2 against B's wants — *permutations of the two
people's wants, checked against actual venues*.

#### 13.9.4 When no combination works

In order:

1. **Drop the member whose wants pair with nothing** from the combination for this stop and
   re-run (they are served on nothing here, and the next stop leads with them).
2. **Single wants → dedicated stops, one each, in lead order.** If every member has exactly one
   want and no venue joins them, there is nothing to substitute *from*; one stop each is the
   honest night (§13.4c rule 6, with the others softened). Running substitutes first here sent a
   heritage person to a club because "SCEN" stood in for "HERIT" — the dedicated pair is better.
3. **Substitute from their vibe profile** — only for a member with two or more wants. Their
   nearest library vibe (`FACTORS_AND_VIBES_V4.md`, by L1 from the learning layer's μ or today's
   scores) carries factors at 70+ that they did not rank tonight. Try those as stand-ins for the
   failed want — a *Set List* person who cannot get `LIVE` tonight is offered `ENRG` + `CROWD`,
   because that is what a Set List night is made of when there is no act. Re-run the combination
   search with the substitutes appended to their list.
4. **Dedicated stops** for whoever still pairs with nothing.

**Log the venue gap.** Every time a combination fails because *no venue exists* — not because of
anyone's bend — record the factor pair (`LIVE` + `POL`, `HERIT` + `PLAY`). That list is what to go
and find; it is the plan engine saying where the venue set is thin, and it is the same signal
§13.1 logs for relaxations.

#### 13.9.5 Balance without debt

The **lead rotates**: stop 1 leads with the member whose top factor is firmest (score, then
latency); each later stop leads with whoever has been served at the lowest total level so far.
That is all the bookkeeping friend mode does. The card reads the same as §13.4c — the factor each
person is served on, by the venue or the street.

**Constants:** `FRIEND_THRESHOLD` 3.0, the 1.0/0.5/0.1 weights, `FRIEND_MAX_GIVE` 70, `MAX_RANK` 4.
All set; tune when friend plans are rated against co-host plans for the same people.

**Not established.** Whether "three plans together" is the right line, or whether an explicit
"close friends" toggle should exist alongside it. Whether relaxed bends should also widen for
the *area* fallback. Whether friend mode should run debt after all when a friend room has four or
more members. None of this blocks the build; §13.4c is the default and friend mode switches on as
the data accrues.

### 13.10 The variables added 2026-09-17, in one place

Everything the day's work introduced, with what each one is for. All set; all to tune.

| Variable | Where | What it does |
|---|---|---|
| `serve_level` → `(level, factor, how)` | §13.4c | the reason a venue gives a person: 1.0 / 0.85 / 0.5 / 1/rank; by the venue or the street |
| `SECOND_STRONG` 70, `SECOND_GAP` 10 | §13.4c | whether a #2 is nearly as good as #1 |
| `DEBT_TRIGGER` 0.5 | §13.4c | debt at which the next stop must pay |
| `paid_tonight` | §13.4c | whose #1 (or best reachable want) has already been served — no re-opened paybacks |
| `payback_target(m)` | §13.4c rule 7 | the highest-ranked want of m's the group's bends allow — what the next stop heightens |
| `SERVED_FLOOR` 0.85 | §13.4c rule 5 | total served that counts as "one real serving" — below it, a stranded person still gets a dedicated stop |
| `dedicated_stop` with softened others | §13.4c rule 6 | own bend holds; #1 then #2; among qualifying venues, the one giving the others the most and stepping on them least |
| `OVERRUN_W` 0.01 | §13.4c rules 6, 9 | how much a served person's overrun costs, per point — at every stop |
| `COVER_K` 0.4, `firm_wants(m)` | §13.4c rule 10 | every firmly held want appears at some stop; uncovered ones pull later stops |
| `'partial'` serving | §13.4c `serve_level` | the venue has the thing but not at the person's level — half a reason, "to whatever degree" |
| `passes()` — the rule-9 gate | §13.4c | served → aversions cost; unserved → must be in bend; hard pass → wall |
| `reach[m]` | §13.4c rule 8 | best serving any venue can give m with everyone in bend — under `SERVED_FLOOR` means a stop is reserved |
| `MAX_STOPS` 3 | §13.4c rule 8 | the night extends to fit reserved stops, up to this |
| `AVERSION_FLOOR` 55 | §13.4 | a venue under 55 on a factor cannot overrun an aversion to it — bar food is not a food place |
| the arc as a preference | §13.4c rule 3 | yields to nobody-gets-nothing, to payback, to pairing, to an empty pool |
| `overall_firmness`, `debt_scale` 0.5–1.5 | §13.8, assessment §6.5 | how opinionated a person is; scales every debt increment and the room-level `RECIP` |
| `friend_score`, `FRIEND_THRESHOLD` 3.0 | §13.9.1 | pairwise, behavioural: ~three plans together in 90 days |
| `relaxed_ceiling`, `FRIEND_MAX_GIVE` 70, `FRIEND_MARGIN` 10 | §13.9.2 | a friend's aversion ceiling rises to the other's delivery floor + 10, capped at +70 |
| `stretch` (logged) | §13.9.2 | points past their own bend a friend accepted at a stop — the card's honesty line, tunes `FRIEND_MAX_GIVE` |
| `friend_stop`, `MAX_RANK` 4 | §13.9.3 | one want of each, combinations in rank order, against real venues |
| `lead`, `got` | §13.9.5 | whose #1 has first claim at this stop; total served so far — friend mode's only bookkeeping |
| substitutes from the nearest vibe | §13.9.4 | stand-in factors for a want the venue set cannot serve — multi-want members only |
| `venue_gaps` (logged) | §13.9.4 | factor pairs no venue serves — what to go and find |
| behavioural evidence reliabilities | `PREFERENCE_ENGINE_V2` §8b | plan ratings, refreshes, rooms, searches, visits as observations of μ |

# 14. The two-stage engine on the split factor set — shape, type, venue (2026-09-17)

**Read this section first. It supersedes §5.3's passive / participatory split, §13.4c rule 9
and `AVERSION_FLOOR`, and every place §5–§13 assumes ten factors on one scale.** Everything else
in §5–§13 survives as amended here: the same debt, payback, reach, friend mode and chemistry —
run on the seven vibe factors and nothing else. `FACTORS_V5.md` defines the factors, the venue
types and the shape library; `DECISIONS.md` entries 96–99 have the reasoning.

## 14.1 The architecture in one paragraph

The **vibe factors give the shape of the night** — and in a room the night is **designed around
every member's top vibe factor, present at every stop**; a top factor moves only when somebody
firmly opposes it and its owner has a strong #2 to stand in (§14.3). Out of it come how many stops (`ROAM`), the arc (`ENRG`),
whether you can hear each other (`TALK`), how full (`CROWD`), whether there is something to play
(`GAMES`), whether you are on your feet (`MOVE`), whether the setting faces the table or the
room (`AFFIL`). From the shape, a **venue type** is fixed at each stop. Then the **preferences
pick the exact venue of that type** — each person's `FOOD` `LIVE` `POL` `SCEN` `NOV` `HERIT`
served at each stop as far as availability allows. **A preference never alters the venue type.
Only the exact venue.**

## 14.2 Inputs

Per member: `vibe[f]` for the seven vibe factors (today's), `firmness` per vibe factor (score, ×
latency once validated), `bend` per vibe factor (§5.3, on the seven), `refused` (vibe factors
only — a hard pass on a vibe card is a firm pole), `overall_firmness` (§13.8), `pref[f]` for the
six preferences (importance 0–100, from the profile), `pol_sense`, and the pairwise friend
relation (§13.9.1). Per venue: `type` (one of the ten in `FACTORS_V5.md` §4), scores on the
seven vibe axes, scores on the six preference attributes, `area`, availability by time band.

## 14.3 Stage one — shape: the night is designed around every member's top factor, at every stop

**Corrected 2026-09-18 (v4).** A person's top vibe factor is their reason to go out tonight, and
**it is absent from no stop.** All members' top factors are used, by default, to design the
night. Nothing is conceded, nothing is paid back, and **there are no dedicated stops** — a stop
that is one person's defeats the purpose. The night is designed so that every member is happy
*to at least a certain degree* with every stop.

### 14.3.1 Each member's top factor — and the one case it moves

```python
SUB_MIN = 18          # a #2 may stand in for the top only if it is at least this far from the middle: score >= 68 or <= 32

def effective_top(m, members):
    """The top vibe factor stands. It moves in exactly one case: somebody else is firm on the
    OPPOSITE pole of it (a low score with a low bend against m's high, or the reverse) AND m has a
    strong #2 to stand in. With no strong #2, the top stands anyway."""
    top = ranked_vibe_wants(m)[0]                                  # by |s - 50|, >= WANT_FLOOR from the middle
    opposed = [o for o in members if o is not m and o.firmness[top] >= FIRM and pole(o, top) != pole(m, top)]
    seconds = [f for f in by_distance_from_middle(m) if f != top and abs(m.vibe[f] - 50) >= SUB_MIN]
    if opposed and seconds: return seconds[0], substituted=True
    return top, substituted=False
```

That is the whole of "compromise": a strong #2 stands in for a top factor somebody firmly
opposes. If both sides of an opposition have strong #2s, both stand in. If neither does, both
tops stand and the stops meet them in the middle (§14.3.3).

### 14.3.1a Bend counts only at the extremes, or when the swipe was fast — everything else is flexible

**The user's rule, 2026-09-18, corrected the same day.** A vibe swipe says *"I would love this"*
or *"this is not my kind of night"*. It never says *"I must have this"* or *"I absolutely cannot"*
— except in two cases, and they are independent: the score is at an extreme (a slow 12 still
counts — a 12 is a 12), **or** the score is near an extreme and the swipe was fast. A score in
the middle is maximum bend whatever the latency.

**The numbers, solid:**

| Zone | Score | Firm? | Bend, in points |
|---|---|---|---|
| **extreme** | 0–20, 80–100 (inclusive) | **always** — whatever the latency | **25** |
| **band** | 21–29, 71–79 | **only if fast** — latency-firmness ≥ 0.60 (rank-based, §6.2) | **28** |
| **middle** | 30–70 | **never** | flexible |

`FAST = 0.60`, `BEND_EXTREME_PTS = 25`, `BEND_BAND_PTS = 28`. Nobody is "fast" for this purpose
until §6.3 validates latency; until then, firm = extreme, exactly.

```python
def zone(m, f):
    s = m.vibe[f]
    if s <= 20 or s >= 80: return 'extreme'
    if s < 30 or s > 70:   return 'band'
    return 'middle'

def is_firm(m, f):
    z = zone(m, f)
    return z == 'extreme' or (z == 'band' and m.firmness_latency[f] >= FAST)

def bend_pts(m, f):
    if not is_firm(m, f): return abs(m.vibe[f] - 50) + 5      # flexible: anything on your side of the middle
    return 25 if zone(m, f) == 'extreme' else 28
```

**Flexible** means "inside bend" is *anywhere on your side of the middle* (or within 5 of it).
**Firm** means a narrow bend from the score. That is the whole of bend now.

**Where firmness is read in the design (§14.3.1–14.3.4):**

| | Reads |
|---|---|
| "firmly opposed" — the one thing that moves a top factor | only a **firm** person on the opposite pole. A 25 at normal speed opposes nobody; a 25 swiped fast does; a 12 does whatever the speed |
| satisfaction "to a degree" (0.5) | only a firm person met halfway; a flexible person is 1.0 anywhere on their side |
| `ROAM` as one number | the middle only between **firm** `ROAM` demands, **weighted by 1 / bend** — the narrower the bend, the more say. A flexible 30 against a firm 92 lets the 92 set three stops |
| signals — the other factors | firm factors at full weight, flexible at a quarter |
| the joiner's gate (§13.4a) | the same words; bend is wide for everything but the joiner's firm factors, so more rooms pass and the match sorts |
| friend mode's stretch (§13.9.2) | only ever needed between two firm people |
| overall firmness (§13.8) | the count of firm factors — how many walls a person has tonight |

**Run** (`design2.py`): Aarav-88 against Bela-12 → both firm whatever the speed, both have strong
#2s, CROWD and TALK stand in — *Got Your Back*. Bela at **25 at normal speed** → the band, not
fast, flexible, opposes nobody; Aarav's energy stands and the stops sit at the middle — *Best of
Both*. Bela at **25 swiped fast** → firm; Aarav's crowd stands in — *Got Your Back*. `ROAM` 92
against a fast 25 → one number, 60, two stops; against a 30 → three stops, *In Sync*.

### 14.3.2 Stop count

`ROAM` is one number for everyone. Firm `ROAM` demands on one pole set it by abstention; firm
demands on both poles are settled by a middle weighted by 1 / bend — the only place a number is
split, because a night cannot be one place and three. The clock caps it (`n_stops`, §14.3.4 of
the earlier text).

### 14.3.3 The type at each stop — nobody below the degree

```python
DEGREE = 0.5

def satisfaction(t, m, f):
    """How present m's top factor is at a type: 1.0 inside m's bend; DEGREE if the type is at
    least on m's side of the middle (or within 5 of it); 0 if it is on the other side."""
    if delivers(t, m, f): return 1.0
    if abs(t[f] - 50) <= 5 or same_side(t[f], m, f): return DEGREE
    return 0.0

def stop_type(k, members, tops, used, prev_energy, had):
    """At every stop: the type that keeps the LEAST-happy member happiest (maximin on the top
    factors); then the most total; then not a type already used (variety); then the arc — calmer
    first at stop 1, no drop of more than 10 after; then coverage of an un-had whole-point
    preference (§14.3.3 step 6 of the earlier text); then everything else as SIGNALS."""
    best = None
    for t in TYPES:
        sat = {m.id: satisfaction(t, m, tops[m.id]) for m in members if tops[m.id]}
        key = (min(sat.values()), sum(sat.values()), t not in used,
               -t['ENRG'] if k == 0 else (t['ENRG'] >= prev_energy - 10),
               coverage(t, members, had), -signals(t, members))
        if best is None or key > best[0]: best = (key, t)
    return best[1]

def signals(t, members):
    """The other factors - high or low, weighted by their bend - shape the night too, as long as
    they disrupt nobody's top factor. They are a tie-break under the top factors, never above."""
    return sum(abs(t[f] - m.vibe[f]) * m.firmness[f] for m in members for f in STOP_AXES)
```

**Maximin is the rule that carries the user's sentence.** Among the types on offer, the one whose
worst-served member is best served — so a night is never designed by adding up the people who
are happy and ignoring the one who is not. Two tops at opposite poles with no strong #2s land at
a type near the middle, where both are present to a degree; the card says so. Where no type gives
somebody even the degree — three single wants in one place — the least-bad type is taken and the
card says whose reason is missing at that stop; **it never becomes that person's stop**.

### 14.3.4 Chemistry — read off how the design went

| How the design went | Code | On the card |
|---|---|---|
| every top factor fully present at every stop | `LOCKSTEP` | **In Sync** |
| every top factor present at every stop, some only to a degree — people met in the middle | `TRADE` | **Best of Both** |
| a strong #2 stood in for somebody's top, or `ROAM` was split to one number | `COMPROMISE` | **Got Your Back** |
| somebody's top factor is absent at some stop — no type could carry it with the others | `TUG` | **Something for Everyone** |
| only one person brought a top factor | `ANCHORED` | **Along for the Ride** |
| nobody did | `DRIFT` | **Open Night** |
| In Sync, everyone 55+ on `ENRG`, and nobody's top *is* `ENRG` | `SPARK` | **Could Go Late** |

Computed whenever the members change — the design needs no venues — and frozen with the plan at
hosting. The room-level payback of §13.6.1 serves the style vector only.

### 14.3.5 What this retires from the group plan

Concession, debt and payback across stops (§13.4c), reach and reserved one-each stops (§13.4c
rule 8), the compose-then-compromise phases of v3, and friend mode's combination search
(§13.9.3) — all retired for the *group* plan. What survives of them: bend (it decides "inside"
versus "to a degree"), firmness (it decides who is firm on the opposite pole), latency (it breaks
ties in what a person's top *is*), `SERVED_FLOOR` and the joiner's gate (§13.4a — a joiner still
has to fit the frozen plan's types inside their bend), and friend mode's relaxed bends (§13.9.2 —
a friend's "opposite pole" is read through the stretched ceiling, so between friends the top
factor moves less often). Those sections stay in the document as the record of how the rule was
arrived at.

### 14.3.5a Four calls, taken 2026-09-18

1. **A top factor absent everywhere** — no extra stop. The least-bad type is taken and the card
   says whose reason is missing at that stop. An added stop would be that person's stop in a
   different coat.
2. **Friend mode** is the relaxed bend and nothing else: between friends, a firm opposition whose
   gap (less the opposer's bend) is inside `FRIEND_MAX_GIVE` (70) is absorbed — the top factor
   stands, and the friend takes the stretch. Only ever relevant between two firm people.
3. **Overall firmness** stays measured — it is now the count of firm factors, how many walls a
   person has tonight — and feeds nothing yet. The learning layer and the match are its likely
   consumers.
4. **The joiner's match** (§13.6.3) reads "state after" by re-running the design with the joiner's
   top factor added, not from the old payback machine; and the gate (§13.4a) reads bend as
   §14.3.1a defines it, so it passes more rooms and the match sorts them.

### 14.3.5b Chemistry V2 — the psychology of each axis feeds the design (2026-09-19)

`CHEMISTRY_V2.md` is the current chemistry. It replaces the room's base vector with a
**chemistry vector** the shape reads for its closeness and its arc; adds one-way rules on `ENRG`,
`TALK` and `MOVE` (only the dominant pole opposes, only it pulls the vector, the other pole is
"to a degree" up to 70); a talk floor on types; *Table and Floor* and *Common Ground* as
tie-breaks above the arc; the crowd aversion weighed by what the room is for; stop durations from
a `ROAM` split; and twelve tags. **The chip is a psychology tag if one fires, else the formation
word of §14.3.4.** `design3.py` runs it; the traces are in that file's §10 and in entry 109.

### 14.3.6 Solo

The person's own vibe factors are the shape; every stop's type inside their bend; `ROAM` their own.

### 14.3.7 Earlier machinery, kept as the record (v2 and v3 of this section)

#### Two kinds of vibe factor, for the purpose of a collision

| Kind | Factors | Why |
|---|---|---|
| **night-level** — one value for the whole night | `ROAM` (the stop count); `ENRG`'s overall arc | both people live with the same number; it cannot be served one stop each |
| **stop-level** — can differ stop to stop | `CROWD` `TALK` `MOVE` `GAMES` `AFFIL`; `ENRG` at a given stop | one stop can lean to A, the next to B |

#### The negotiation on a night-level collision

```python
def shape(members):
    wants  = {m.id: ranked_vibe_wants(m) for m in members}      # by |s-50| then latency; a firm low pole is a want
    shape, owed = {}, {m.id: [] for m in members}

    # 1. night-level factors: one value, placed by firmness
    for f in NIGHT_LEVEL:
        firm = [m for m in members if m.firmness[f] >= FIRM]
        if not collide(firm, f):                                  # nobody firm at the other pole
            shape[f] = abstention(members, f)                     # the firm ones set it, the rest abstain
        else:
            shape[f] = firmness_weighted_middle(firm, f)          # closer to whoever is firmer
            for m in firm:                                        # whoever is further from their pole is owed
                if abs(shape[f] - m.vibe[f]) > bend_pts(m, f): owed[m.id].append(f)

    # 2. payback on the night-level concession: the next want gets a say in the stops
    for m in members:
        for f in owed[m.id]:
            nxt = next_want(wants[m.id], after=f)                 # their next-firmest vibe factor
            if nxt: promote(m, nxt)                               # counts as their #1 in the stop-level shape

    # 3. stop-level factors: a type that serves both poles' wants if one exists, else across stops
    n = n_stops(shape['ROAM'], duration)
    stops = []
    for k in range(n):
        target = arc_target(shape, k, n)
        stops.append(stop_type(target, members, wants))           # §14.3.3
    return stops
```

**Collide** means firm members at *opposite poles* of the same factor. Two people at the same
pole do not collide however different their scores; a firm member and an easy one do not collide
— the easy one abstains. **CROWD-high and AFFIL-high do not collide**: they are different
factors, and a full room with your own booth serves both.

**The worked case, from the user.** A: `ROAM` high, firm; `CROWD` high. B: `AFFIL` high, firm;
`ROAM` low, firm.

- `ROAM` collides — a night-level factor, so one value: the firmness-weighted middle. Both
  equally firm → two stops (from A's four and B's one). If A is the firmer, three; if B, two
  toward one.
- Whoever ended further from their pole is **owed**, and is paid in the stops: if it settled at
  two, A is owed and A's next want — `CROWD` — is promoted, so the two stops are the full rooms.
  If it settled at three, B is owed and B's next — `GAMES` — is promoted: booths in games bars.
- `CROWD` and `AFFIL` do not collide: the stop type is *a full room with a table you can hold* —
  a pub or a buzzy restaurant with a booth.

So: **the compromise sets the number; the payback shapes the stops.** Neither alone is right.
Four stops with games at each is not a compromise on the thing B was firm about — it is a
consolation on a different axis; and a middle with nobody paid back is the average the engine
exists to avoid.

#### The type at a stop, under compromise

```python
def stop_type(target, members, wants):
    """The venue type (FACTORS_V5 §4) that serves the most members on their best-ranked
    stop-level vibe want - promoted wants counting as #1 - inside as many bends as possible.
    Priorities: nobody firm on a stop-level factor gets nothing -> most served x (1 + DEBT_K x debt)
    -> least stepping-on. Debt carries between stops; the next stop pays back (§13.4c)."""
    ...
```

This is §13.4c's `pick_best`, with venue *types* as the candidates instead of venues, and vibe
wants only. Everything in §13.4c applies: owed-until-served, the arc as a preference, reserved
one-each stops for a member no type can serve alongside the others, `SERVED_FLOOR`, friend
mode's relaxed bends and combination search (§13.9 — on types), overall firmness scaling debt
(§13.8). Rule 9 and `AVERSION_FLOOR` are retired: on vibe factors both poles are wants, and a
member outside bend at a stop is a concession scored by §13.4c, never a gate.

**No walls on vibe factors** (found by the re-cut simulation, 2026-09-17). A hard pass on a vibe
card is a firm low pole — a want, at 12 — and is served or conceded like any other. If it were
also a wall, a *love* at 88 would have to be one too, and two people at opposite firm poles
would leave no type passable at all. The reserved one-each stop is what handles that pair.

**The order at a stop, in full** — every step a tie-break for the one above it:

1. nobody who wants something (and is not excused) gets nothing;
2. most served, weighted by debt (promoted wants counting as #1);
3. least stepping-on — the summed overrun of members' firm poles;
4. **variety** — not the same type as the previous stop;
5. at stop 1, the calmer type (the night builds);
6. **whole-point coverage** — between types the shape cannot separate, the one whose venue pool
   can also carry an un-had whole-point preference of somebody's (a pub with a live-band bar in
   it, for the gig person). *Confirmed 2026-09-17.* This does not touch the shape: a preference
   is an element of the venue, never of the night. A gig person entering a room of people who do
   not care for live music never alters the course of the night or its types — the engine only
   looks, within the shape, for venues that possibly have live music too. A tie between types is
   the shape saying it has no opinion; the fill's question is then the only question left;
7. closeness to the room's vibe target, weighted by firmness per axis.

`open ground` is an early-evening type: a candidate at stop 1 only.

**Friend mode's relaxation reaches implied factors.** An `ENRG`-high want can only be served by
types that are also loud; a friend at `TALK`-high firm would block every one of them. So the
stretch (§13.9.2) applies on the colliding factor *and* on any factor of the friend's that every
type serving the want overruns — to the same cap. Below the cap a 15-against-90 energy split is
still a one-each night, friends or not; that is the cap doing its job.

A stop-level collision that a single type can carry — one booth in one full room — is not a
concession for anyone. One that cannot — `TALK` high, firm, against `TALK` low, firm — is
served across stops: the quiet bar first, the loud room after, debt and payback as built.

#### How many stops, and the arc

```python
def n_stops(roam, duration_hours):
    by_roam = 1 if roam < 35 else 2 if roam < 65 else 3
    by_time = max(1, min(3, int(duration_hours // 1.75)))
    return min(by_roam, by_time)                     # ROAM says how many; the clock caps it
```

`roam` is the negotiated value from §14.3.2, not any one member's. Reserved one-each stops
(§13.4c rule 8) can still extend the night to `MAX_STOPS`. The `ENRG` arc runs from the
negotiated start to the negotiated end across those stops.

#### Solo, and the joiner

For a solo plan the shape is the person's own vibe vector — no negotiation, every stop's type
inside their bend, `ROAM` their own. For a joiner (§13.4a) the gate is **shape-fit**: every
stop's type inside their bend on every vibe axis, and the plan's stop count inside their `ROAM`
bend; no hard pass violated. Preference fit sorts, never gates (§14.6).

## 14.4 Stage two — fill

At each stop, among the venues **of the type the shape fixed**, available at the stop's time:

```python
PREF_WHOLE = 75            # "the whole point" and above
had = {m.id: set() for m in members}                  # whole-point preferences already had tonight

def pref_fit(venue, members):
    """Each person's each preference, served as far as the venue has it; importance is the weight,
    so the people who care set it and the people who don't abstain. A whole-point preference not
    yet had tonight counts double - that is rule 10 on preferences."""
    total = 0.0
    for m in members:
        for f in PREFS:
            w = m.pref[f] / 100
            if f == 'POL' and not sense_ok(venue, m): continue                  # the sense filter (§13.4b)
            if f == 'NOV': v = 100 if not been_before(m, venue) else 20         # newness is per member
            else:          v = venue[f]
            urgent = 2 if m.pref[f] >= PREF_WHOLE and f not in had[m.id] else 1
            total += w * urgent * min(v, m.pref[f])
    return total

def fill(stop, members, used):
    pool = [v for v in venues if v.type == stop.type and v not in used and available(v, stop.band)]
    v = max(pool, key=lambda v: pref_fit(v, members) - room_cost(members, v))
    for m in members:
        for f in PREFS:
            if m.pref[f] >= PREF_WHOLE and venue_has(v, f, m): had[m.id].add(f)
    return v
```

`venue_has(v, f, m)`: the venue scores ≥ `DELIVERS` (55) on f — and passes the sense filter for
`POL`, and is new to m for `NOV`. **Had, not centred on.** A food person at a club gets the club
with the best kitchen; they *eat* there.

**Rule 10 on preferences, stated plainly.** For every member, every preference at *the whole
point* must be had by some stop's venue in the night. The doubling above does it: an un-had
whole-point preference pulls the exact-venue choice hardest at each successive stop until it is
had. Two members whose whole-point preferences cannot share a venue of the type (a `LIVE` 88 and
a `FOOD` 88 where no live room of that type feeds you) get the pull in turn — one stop's venue
leans to hers, the next's to his — **inside the same type, with no debt**, because nothing on
the vibe was conceded. A whole-point preference no venue in the night can serve is said on the
card and logged as a venue gap.

**What preferences never do:** change the type, change the stop count, change the arc, enter the
room vector, enter chemistry, enter the name, or count against anyone. A low preference is not
an aversion — that sentence is the reason this section exists.

## 14.5 The card

Per stop: the **type** in plain words (*"a games bar"*), the venue, then per person **two
lines** where there used to be one:

- the vibe line, from the shape: *"for Aarav — it builds from here"*, *"for Bela — you can hear
  each other"*, *"for Chirag — something to play"*;
- the preference line, from the fill: *"the food's good"*, *"there's a set at ten"*, *"nobody's
  been"*.

Then up to three notes per stop, read off §14.3 v4 — no easing, no ⓘ, no payback, no dedicated
stop: a **stand-in** note when a strong #2 is shaping the night in place of a firmly opposed top
(*"Aarav's here for the crowd tonight; Bela's set on a calm one"*); a **to-a-degree** note when a
top factor is present but not inside bend (*"Some energy here for Arjun; more at the next stop"*);
an **absent** note when no type could carry a top factor with everyone else's (*"No games here for
Chetan — nowhere does games, a floor and a quiet table at once"*). Whole-point preferences the
night could not serve get one line at the bottom of the card.

## 14.6 The room list and the match, on the split set

- **Gate** (§13.4a, §14.3.4): shape-fit at every stop. Hidden otherwise.
- **Sort** (§13.6.3): the match on the seven vibe axes — shift, reinforcement, the state — gives
  *great* / *alright*; **then, within a band**, preference fit orders the list: a room whose
  venues have the joiner's whole-point things sits above one whose venues do not. Preferences
  never hide a room and never move it between bands.
- **Open Night**: as before; "firm on five or more" reads on the seven vibe factors.

## 14.7 What §5–§13 lose, keep, and gain

| | |
|---|---|
| **Lose** | §5.3's `PASSIVE` set and the asymmetric penalty (there are no passive vibe factors); §13.4c rule 9; `AVERSION_FLOOR`; `PLAY`; `POL` as a plan-time factor (it is a fill attribute with a sense filter); the 42-vibe library |
| **Keep** | bend from firmness (§5.3, §13.3, §13.5); `FLOOR` v3's priorities; §13.4c rules 1–8 and 10; reach and reserved stops; `SERVED_FLOOR`; overall firmness (§13.8); friend mode (§13.9); chemistry and the match (§13.6); hosting freezes the plan; Open Night; the area fallback (§13.7 — `CROWD`, `ENRG` in the shape; `POL`, `SCEN` in the fill) |
| **Gain** | `ROAM` → stop count; `TALK`, `MOVE`, `GAMES` as axes; venue types as the shape's vocabulary; a fill stage where preferences are weights and nothing else; two lines per person on the card; badges |

## 14.8 Constants introduced here

| | value | adjust when |
|---|---|---|
| `ROAM` thresholds for 1 / 2 / 3 stops, on the negotiated value | 35 / 65 | stop counts are rated |
| night-level vs stop-level factors | `ROAM`, the `ENRG` arc / the rest | — |
| the firmness-weighted middle on a night-level collision | by firmness | who ends up owed is rated |
| `WANT_FLOOR` on vibe (distance from 50) | 25 | — |
| `PREF_WHOLE` | 75 | — |
| the whole-point doubling | ×2 | whole-point preferences go un-had in rated plans |
| similarity denominator for styles | 350 | — |
| the ten venue types | `FACTORS_V5.md` §4 | the venue database is tagged |

All set. `splitsim.py` is the simulation on this model — seven vibe axes, ten types, a fill
stage, seventeen venues. The runs of 2026-09-17:

```
ROAM (user's case)  A ROAM 92 CROWD 80 · B AFFIL 90 ROAM 12      ROAM collides -> 54 -> 2 stops; both owed; CROWD and AFFIL promoted
                    1 [buzzy restaurant] Depot 48    2 [buzzy restaurant] busy diner   - a full room with your own table, twice
   A firmer (95 v 25) -> 70 -> 3 stops, the same types
U  Piano Man room   Aarav ENRG 88 · Bela ENRG 12 TALK 80 + LIVE whole-point · Chirag FOOD whole-point
                    Aarav reserved (no type serves him with Bela in it)  1 [lounge] rooftop   2 [games bar] bowling, his
                    Bela's LIVE never had - no lounge-type venue with an act in this pool (a venue gap, not a rule)
F  the gig person   Aarav, Divit ENRG 85 CROWD 80, LIVE 12 · Ruchi LIVE 92 (a preference now)
                    1 [pub] bar with live band   2 [club] warehouse    - Ruchi's act at stop 1 by the coverage tie-break; no dedicated stop
E  the quaint pub   Priya AFFIL 92 ENRG 20 CROWD 25 · Sana, Ria SCEN + POL whole-point
                    1 [table for the night] haveli   2 [quiet bar] jazz bar   - Priya's night by the type, theirs by the venue
H  two ENRG camps   Aarav ENRG 90 CROWD 85 · Neha ENRG 15 TALK 85
                    1 [lounge] rooftop   2 [buzzy restaurant] Depot 48   - both on their strong #2 at both stops; nobody's #1, nobody owed
L/O friends v not   A ENRG 90 · B ENRG 15 TALK 80 - identical: 1 [lounge] rooftop  2 [club] warehouse, A's. The stretch caps at 70; 75 apart is one-each either way
N  GAMES v HERIT    1 [games bar] bowling   2 [games bar] arcade   - B's HERIT never had: no heritage games bar exists (gap)
I  one firm, two easy   1 [live room] Piano Man   2 [club] warehouse   - Aarav's night; the easy two carry no debt
T  the whole team out   1 [games bar] bowling   2 [buzzy restaurant] Depot 48   3 [games bar] arcade   - AFFIL, ENRG, GAMES at every stop
P2 Priya hosts 3    1 [table for the night] haveli   2 [buzzy restaurant] Depot 48   - every whole-point preference had, Rohan's act at Depot
```

**Designed-night, 2026-09-18 v4 (`design.py`; an eleventh type, *games pub* — board games and a table you can talk at — added to the pool):**

```
Arjun ENRG 90 · Bea ROAM 88, TALK 80 · Chetan GAMES 92     nobody opposes anybody; ROAM -> 3 stops
   1 [games pub] board-game brewery   2 [pub] brewery   3 [games bar] bowling   - Arjun 0.5 / 0.5 / 0.5, Bea 1 / 1 / 0.5, Chetan 0.5 / 0.5 / 1   -> Best of Both
U  Piano Man room   Aarav ENRG 88 v Bela ENRG 12: both firmly opposed, both have strong #2s -> CROWD and TALK stand in
   1 [quiet bar] jazz bar (Bela's act)   2 [buzzy restaurant] Depot 48   - both 1.0 at both stops                                  -> Got Your Back
H  two ENRG camps, no strong seconds   both tops stand -> 1 [lounge] rooftop  2 [buzzy restaurant] Depot 48  - both 0.5 at both      -> Best of Both
ROAM case   ROAM 92 v 12 -> one number, 54 -> 2 stops; CROWD and AFFIL both 1.0 at both                                              -> Got Your Back
T  whole team out   AFFIL, GAMES, AFFIL all 1.0 at every stop; everyone 55+ on ENRG, nobody's top                                    -> Could Go Late
E  quaint pub   only Priya brings a top -> 1 [table] haveli  2 [quiet bar] jazz bar                                                   -> Along for the Ride
F  the gig person   1 [pub] live-band bar (Ruchi's act)  2 [club] warehouse                                                           -> In Sync
X  GAMES · MOVE · TALK, all ROAM low   one stop; no type carries all three: 1 [open ground] lawn, A's games absent, said on the card  -> Something for Everyone
Y  AFFIL 90 v AFFIL 12, both with strong #2s   CROWD and ENRG stand in -> 1 Depot 48  2 warehouse, both 1.0                            -> Got Your Back
```

**Compose-first, 2026-09-18 v3 (`compose.py`, superseded the same day):**

```
ROAM case           ROAM high v ROAM low -> a collision -> Phase B: settled at 54, 2 stops, CROWD and AFFIL promoted    -> Got Your Back
T  whole team out   {AFFIL, ENRG, GAMES} all carried by one type -> games bar x3                                          -> In Sync
H  two ENRG camps   {ENRG low, TALK high} | {ENRG high, CROWD high} -> 1 [table] haveli  2 [street/market] food walk     -> Best of Both
H1 same, ROAM low   needs 2 stops, ROAM asked for 1 -> one added                                                        -> Got Your Back
U  Piano Man room   1 [table] haveli (Bela calm)  2 [live room] Piano Man (Aarav's energy; Bela's act by coverage)       -> Best of Both; every whole-point had
E  quaint pub       only Priya brings a top factor -> 1 [table] haveli  2 [quiet bar] jazz bar                           -> Along for the Ride
F  the gig person   the boys' {ENRG, CROWD} in one group -> 1 [live room] Piano Man (coverage: Ruchi's act)  2 [club]     -> In Sync
I  one firm, two easy  1 [pub] live-band bar  2 [club] warehouse                                                        -> Along for the Ride
P2 Priya hosts 3    Kabir ROAM low v Rohan ROAM high -> Phase B -> 1 [open ground] lawn  2 [buzzy restaurant] Depot 48    -> Got Your Back
X  GAMES - MOVE - TALK, all ROAM low   needs 2 stops, asked for 1 -> one added: 1 [open ground] lawn  2 [games bar]      -> Got Your Back
```

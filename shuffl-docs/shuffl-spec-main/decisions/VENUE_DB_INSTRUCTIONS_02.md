# Venue database — what to change, and exactly how

**Written 2026-10-06, after reviewing `SHUFFL_South_Delhi_Venue_Database_Discovery.xlsx`.**
Supersedes the "what to run" half of `VENUE_DB_REVIEW_01.md`. Read with
`VENUE_DATABASE_HOW_TO.md`, which is the plain-English version of the same build.

> **The architecture of your pipeline is right. The first source is wrong, and it caps everything
> downstream.** Swap OpenStreetMap for Google Nearby Search at step 1 and the remaining three steps
> work as you designed them.

---

# Part 1 — What the current file shows

## 1.1 Five of the six sheets have not changed

Compared byte for byte against the file sent on 2026-10-05:

| sheet | rows | status |
|---|---|---|
| `Venues` | 110 | **identical** |
| `Venue_Time_Slots` | 155 | **identical** |
| `Venue_Sources` | 1,818 | **identical** |
| `Needs_Verification` | 2,571 | **identical** |
| `Coverage_Report` | 241 | **identical** |
| `Venue_Candidates` | 436 | **new** |

So the database itself is where it was: **0 of 110 venues have a full set of factor scores, 3 have a
`google_place_id`, 61% have opening hours, and admission has never run on our criteria.** Those are
the blockers from the first review and none of them has moved.

**The new sheet is step 1 of your 4-step pipeline and you labelled it correctly** — every row reads
`Review` and *"requires Foursquare enrichment and human admission"*. Nothing below is a criticism of
how that step was executed. The problem is which source it executed against.

## 1.2 Discovery is the gate, and OSM does not have the venues

**Foursquare can only enrich what OpenStreetMap already found.** A venue absent from OSM never
enters the pipeline, is never enriched, is never scored and never reaches the app. **The ceiling on
the entire database is set at step 1.**

What OSM returned for South Delhi:

| | |
|---|---|
| candidates | **436** |
| `bar` + `pub` + `nightclub` | **17 — 4%** |
| `nightclub` | **1** |
| `restaurant` + `cafe` | 419 — 96% |
| overlap with your existing 110 venues | **0** |
| have a website in OSM | 17 — 4% |
| have opening hours in OSM | 58 — 13% |
| have an address | 52 — 12% |

**Nine of ten reference venues are absent:** Summer House, Bohca, Dear Donna, Depot 48, Imperfecto,
Raasta, Qla, Olive — and **Hauz Khas Social, which is already row 1 of your own `Venues` sheet.**
A discovery pass that cannot find a venue you have already catalogued will not find the ones you
have not.

**And the pool it did return is the wrong category.** A sample:

```
Aggarwal Sweet Corner · Aggarwal Sweets · Aggarwal Sweets · Aggarwal Sweets
A1 Chaap Junction · Ajit Khalsa Dhaba · Aali's Kathi Kababs · Aahar
```

Three literal duplicates of one sweet shop. These are the *Kent's in Defence Colony* category the
product explicitly excludes. The `bar` list includes **Blue Frog**, which closed in Delhi years ago
— so OSM here is **thin, stale and duplicated**.

**Why, structurally:** OSM in Delhi is volunteer-maintained. Volunteers map daytime food. Nobody
volunteers to map nightclubs, so nightlife is the category OSM is weakest at — which is the one
category this app is strongest on.

## 1.3 This is the third discovery method that selected the wrong venues

| pass | method | what it selected for |
|---|---|---|
| 1 | official websites | **chains and hotels** — 83% Group/Chain/Hotel, 3 clubs. A corporate website is a proxy for being a chain |
| 2 | OpenStreetMap | **whatever hobbyists mapped** — 4% nightlife, 1 club, sweet shops in triplicate |

**Both are biased because neither ranks by whether anyone actually goes there.** The fix is a
discovery source whose index is built from real-world prominence, because that is the same signal
our admission filter measures. Google Nearby Search ranks by exactly that, which is why it and the
filter agree rather than fight.

## 1.4 The licence reading from the first review is still unfixed

The rule, restated because it is the root of the empty scores:

> **We may CALL the Places API and DERIVE our own data from the response.**
> **We may not STORE Google's names, addresses, ratings, review text, photos or hours.**
> **We may store `place_id` indefinitely, and anything we computed ourselves.**

Avoiding Google entirely is a stricter reading than the terms require, and it is what removed every
rating, every review text and therefore every factor score. **Calling is fine. Keeping is not.**

---

# Part 2 — Exactly which API, and exactly how to call it

## 2.1 Google Places API (New) — the only one needed

Enable **Places API (New)** in a Google Cloud project with billing attached. Check the monthly free
credit; it may cover most of this run.

### Endpoint A — Nearby Search (discovery)

```http
POST https://places.googleapis.com/v1/places:searchNearby
X-Goog-Api-Key: <KEY>
Content-Type: application/json
X-Goog-FieldMask: places.id,places.displayName,places.formattedAddress,places.types

{
  "includedTypes": ["bar"],
  "maxResultCount": 20,
  "locationRestriction": {
    "circle": {
      "center": { "latitude": 28.5535, "longitude": 77.1940 },
      "radius": 800.0
    }
  }
}
```

- `maxResultCount` caps at **20**. That is why discovery runs per district **per type** rather than
  one big call.
- Run it for five types: **`bar`, `night_club`, `pub`, `restaurant`, `cafe`.**
- **~$0.035 a call.** 20 South Delhi districts × 5 types = **100 calls, about $3.50.**
- Deduplicate on `places.id`. Districts are allowed to overlap; a duplicate costs one call and never
  produces a duplicate row.

### Endpoint B — Place Details (enrichment)

```http
GET https://places.googleapis.com/v1/places/<place_id>
X-Goog-Api-Key: <KEY>
X-Goog-FieldMask: id,displayName,formattedAddress,location,types,primaryType,
  primaryTypeDisplayName,rating,userRatingCount,priceLevel,priceRange,
  regularOpeningHours,businessStatus,editorialSummary,generativeSummary,reviews,
  liveMusic,goodForWatchingSports,outdoorSeating,reservable,goodForGroups,
  servesCocktails,servesWine,servesBeer,servesDinner,servesBrunch,servesCoffee,
  servesDessert,servesVegetarianFood
```

**The field mask decides the price.** Asking for `reviews` and the atmosphere fields puts the call on
**Enterprise + Atmosphere, $25 per 1,000**. Without them it would be a few dollars per thousand — but
without reviews there is nothing to score, so this is the call we want.

**There is no separate reviews endpoint.** Reviews arrive inside this response. You get **at most
five** and cannot choose which five. Take the text and discard the rest:

```python
texts = [rv['text']['text'] for rv in detail.get('reviews', [])]
```

### Endpoint C — Text Search (only for resolving a known name)

```http
POST https://places.googleapis.com/v1/places:searchText
X-Goog-FieldMask: places.id,places.displayName,places.formattedAddress
{ "textQuery": "Summer House Cafe Aurobindo Place New Delhi" }
```

**$35 per 1,000.** Use it only to attach a `place_id` to a venue you already have by name — for
example the existing 110. **Always include the area in the query and check the returned address**:
searching *"Cirrus 9"* once returned a venue at The Oberoi when Cirrus 9 is at the Shangri-La, and
**a wrong match is worse than no data.**

## 2.2 Why not the others

| source | why not |
|---|---|
| **OpenStreetMap / Overpass** | Measured above: 4% nightlife, 1 club, no ratings, no reviews, stale entries. It has no rating or review data at all, so it can never feed admission or the lexicon. Fine as a cross-check, useless as the gate. (If you do call it, send a `User-Agent` header or Overpass returns 406.) |
| **Foursquare** | Can only enrich what discovery already found, so it cannot fix a discovery problem. Its Delhi tip volume is also thin and tips are short — our filter needs 200+ ratings and the lexicon needs text at volume. |
| **Yelp** | Effectively no India coverage. Even where it is strong it returns 3 truncated snippets against Google's 5 full reviews. |
| **TripAdvisor** | Delhi coverage skews to tourist venues and hotel restaurants — the exact bias of pass 1, re-imported. |
| **Zomato** | Would be the best source for Delhi. Public API discontinued; partner access only. Worth revisiting alongside venue partnerships. |

**Do not combine two sources for v1.** Every extra source doubles the licensing surface and forces
venue matching across two ID systems, which turns the Cirrus 9 failure from an occasional research
error into a systematic pipeline step.

---

# Part 3 — The build, step by step

`simulations/pipeline.py` implements all of this. Run it, or port it.

## Step 0 — Setup

```bash
export PLACES_KEY=...
cd simulations
```

## Step 1 — Discover

```bash
python pipeline.py discover --dry-run                   # prices it, spends nothing
python pipeline.py discover --key $PLACES_KEY           # south-delhi is the default
python pipeline.py discover --key $PLACES_KEY --catchment ncr
```

| catchment | districts | calls | cost |
|---|---|---|---|
| `south-delhi` (default) | 20 | 100 | ~$3.50 |
| `ncr` | 32 | 160 | ~$5.60 |

The district lists are `SOUTH_DELHI` and `REST_OF_NCR` at the top of `pipeline.py`. The South Delhi
list already matches your stated catchment: Hauz Khas, Deer Park, Safdarjung Enclave, Green Park and
SDA, Panchsheel Park, Malviya Nagar, Saket, Mehrauli and Qutub, Vasant Kunj, Vasant Vihar, Aerocity,
Defence Colony, Lajpat Nagar, South Extension, GK I and II, Kailash Colony, Nehru Place, Kalkaji,
CR Park. → `candidates.json`.

## Step 2 — Enrich

```bash
python pipeline.py enrich --key $PLACES_KEY --limit 20   # sanity-check twenty first
python pipeline.py enrich --key $PLACES_KEY
```

One Details call per candidate, **$25–50 total**. Every response is cached to `cache/places/`, so a
re-run costs nothing and you can interrupt it freely. Retries with backoff on 429 and 5xx.
→ `enriched.json`.

**`cache/places/` is working scratch, not the database.** It is in `.gitignore` and must not ship.

## Step 3 — Build

```bash
python pipeline.py build
```

No API calls, no cost. Four passes:

### 3a. Admission

| criterion | threshold |
|---|---|
| review volume | **≥ 200** |
| mean rating | **≥ the 35th percentile within its own type** (falls back to 4.0 only when a type has fewer than 8 peers) |
| consistency | sentiment spread **≤ 0.85** |
| operator class | chain, group, hotel, or established independent |
| fit-out | **≤ 15 years** (human pass) |
| drift | newest reviews not far below the lifetime mean |

**The mean must be compared within type.** A real pass rejected **Privee** — a well-known club with
1,380 reviews — on a 3.6 average, because clubs collect door complaints restaurants never get. **A
flat 4.0 cut-off is a filter against clubs, not against bad venues.**

**A venue the pipeline cannot classify is admitted and flagged, never rejected.** Otherwise anything
needing a human could never reach one.

### 3b. Factor scores from the text

Corpus = **the five review texts + `editorialSummary` + `generativeSummary`.**

1. Count high-pole and low-pole keyword matches. **Polarity is irrelevant** — *"too loud"* and
   *"amazing energy"* are the same evidence about the room.
2. Drop matches negated within 24 characters (*"no dance floor"*).
3. Drop the wrong sense via exclusion contexts (*"traditional tapas"* is a cuisine, not heritage).
4. `reading = 50 + (hi / (hi + lo) − 0.5) × 100`
5. Blend toward the venue type's prior by evidence volume: `w = n / (n + 6)`, then
   `score = prior × (1 − w) + reading × w`.

**Every venue type must have a prior.** `club`, `big loud bar`, `buzzy restaurant`, `live room`,
`cafe`. A type mapped to a prior that does not exist falls through an undamped path and produces
extremes — a jazz club scored `ENRG` 0 that way. **Assert that every value in the type map has a
prior behind it.**

Accuracy: **about 7 points mean error** against hand-scored venues. Enough to order a list of ten.
Not enough to print as a fact.

### 3c. The venue's own fields override the text

| field | effect |
|---|---|
| `liveMusic: true` | `LIVE` = 85 |
| `liveMusic: false` | `LIVE` → **not specialised** |
| `goodForWatchingSports: true` | `FOCUS` = 78 |
| `outdoorSeating: true` | `SCEN` floored at 60 |
| all `serves*` food fields false | `FOOD` → **not specialised** |

**The `serves*` family is used only in its all-false form.** Every bar "serves dinner" — the field
proves a kitchen exists, not that food is the point. It is good evidence of absence and poor
evidence of presence, and only the half it is good at is used.

### 3d. Three states, and never a zero

| state | meaning |
|---|---|
| a score | the evidence said so |
| **not specialised** | a flag — this is not what the place is for |
| **unknown** | no claim either way |

Silence about food at a **restaurant** is evidence. Silence about food at a **bar** is not, because
reviewers of bars write about drinks. **Never write "not specialised" as a zero** — a zero says we
measured it and it was poor, and it cannot be undone later.

### 3e. Time bands

A band fills only when a source **names its time**: *"Sunday brunch"*, *"every Wednesday"*,
*"closes at 1am"*. A glowing review with no hour improves the base score and must not touch a band.

**Never store a band inferred from the venue type.** Leave it empty; the fallback happens at query
time where it is visible and reversible. **A stored guess is indistinguishable from a measurement a
month later.** Expect half to two-thirds of bands to fill, with the gaps concentrated late at night.

## Step 4 — The human pass (1–2 hours)

`human_pass.csv` lists **admitted venues only**, with two blank columns:

- **`operator_class`** — chain / group / hotel / indie-pro / owner-local. Only the ones the pipeline
  could not guess appear.
- **`fitout_years`** — how long since the room was last done. A glance at the photos, about three
  seconds each. Over 15 years fails.

Paste back and re-run `build`.

## Outputs

| file | contents |
|---|---|
| `venues.json` | the database — scores, bands, `not_specialised` flags, admitted/rejected |
| `gold_list.json` | every band the evidence could not reach — the gold promotion's queue |
| `human_pass.csv` | the two columns above |

---

# Part 4 — What to keep from what you have built

**Do not throw the existing file away.** Three things in it are good and the pipeline does not
produce them:

1. **`Venue_Sources` — 1,818 field-level provenance rows.** No API gives this. It is the audit trail
   if the licensing is ever questioned. Keep it and keep filling it.
2. **The `Unknown` discipline.** *"Estimated slots: 0. No invented time schedules."* This is the
   single most important behaviour in the job and it was done right without being asked twice.
3. **The `Needs_Verification` queue and the duplicate handling.** The WYTE/BLAQ and Woodpecker
   catches were correct.

**Migration:** run Text Search once per existing venue to attach a `place_id`, then feed those IDs
straight into `enrich`. That recovers the 110 you already have **and** keeps their source rows,
without re-researching anything.

---

# Part 5 — How you will know it worked

Run these before spending the enrichment budget.

**After `discover`:**

- [ ] **Summer House, Bohca, Dear Donna, Depot 48 and Imperfecto HKV appear in `candidates.json`
      without anyone naming them.** This is the single test that separates a working discovery pass
      from the last two. If they are missing, stop — the problem is the call, not the catchment.
- [ ] `night_club` and `bar` together are a **meaningful share** of candidates, not 4%.
- [ ] Hauz Khas has more candidates than Aerocity.

**After `build`:**

- [ ] **Every admitted venue has all 11 factor scores or an explicit `not_specialised` flag.** No
      silent blanks.
- [ ] `python realrun.py` still reports **IN 14 / OUT 2** on the sixteen hand-researched venues.
- [ ] `python lexicon.py` still reports **7.1 points** mean gap.
- [ ] The admitted list is **shorter** than 110 and contains **new independents**. Both are the
      filter working.

---

# Part 6 — The traps, in order of cost

1. **Comparing ratings against a flat number instead of within type.** Deletes the clubs. Most
   expensive mistake available.
2. **Storing anything of Google's beyond `place_id`.** Licensing exposure on every row.
3. **Storing a band you inferred from the venue type.** Poisons the data invisibly.
4. **A venue type with no prior behind it.** Produces `ENRG` 0 on a jazz club. Has now happened
   twice — assert it.
5. **Writing "not specialised" as a zero.** Loses the distinction between *not measured* and
   *measured and poor*.
6. **Matching a venue by name without checking the address.** The Cirrus 9 failure. A wrong venue is
   worse than no venue.

---

# Part 7 — What no API provides, so plan for it

| | what to do |
|---|---|
| a rating histogram | Does not exist. We substitute sentiment variance across the 5 reviews with door complaints routed out first — **and that substitution is untested.** Check it once there are a few hundred rows |
| more than 5 reviews | Nothing. Work within it |
| popular times | Not available |
| what is on tonight | **No events API covers Delhi nightlife.** One manual pass over venue Instagrams at seed time, refreshed quarterly |
| fit-out age | The human pass |
| the time bands | What the gold promotion is for (`GOLD_PROMOTION_V1.md`) |

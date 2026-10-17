# How to build the venue database

Everything in one file, written plainly. Last updated 2026-10-05.

This replaces having to read four documents. If you want the reasoning behind a rule rather than
the rule itself, it is in `VENUE_DATABASE_V1.md`.

---

## What you are building

A list of Delhi NCR venues, each with:

- eleven factor scores (how loud it is, how full, whether you can talk, food, live music, and so on)
- its opening hours
- which of those scores are measured and which are still guesses

The app uses it like this: the user draws the shape of their night, and for each stop the app shows
5–10 venues whose scores match that shape and which are open at that hour. The user picks one.

That is all the database has to do. It does not plan anything.

---

## The one rule you must not break

Google lets us **use** their data but not **keep** it.

| | |
|---|---|
| You may store forever | `place_id`, and any number we worked out ourselves |
| You may never store | Google's venue names, addresses, ratings, review text, photos, opening hours |

So: call the API, read the reviews, work out a factor score, save the score, throw the review away.
When the app needs to show a name or a photo, it fetches it live at that moment.

This is the mistake the first database pass made in reverse — it avoided calling Google at all, and
ended up with no ratings and no review text, so nothing could be scored. **Calling is fine. Keeping
is not.**

---

## Which APIs, and what each one gives you

### Google Places API (New) — the only one you need

Two endpoints.

**Nearby Search** — "give me every bar within 800m of this point".
Used once, to find candidates. About **$0.035 a call**.

**Place Details** — everything about one venue.
Used once per venue. **$25 per 1,000 calls** on the Enterprise + Atmosphere tier.

What Place Details returns that we use:

| | |
|---|---|
| rating and number of ratings | runs the admission filter |
| **up to 5 reviews** | the main source of factor scores |
| editorial summary, AI summary | two more sentences, often the densest ones |
| `liveMusic`, `goodForWatchingSports`, `outdoorSeating`, `reservable`, `serves…` | the venue's own statements |
| opening hours | the stop list cannot work without these |
| price level, coordinates, types | the budget filter, distance, the type priors |

**Five reviews is a hard cap.** You cannot get more, however much you pay. Everything about how the
scoring works follows from that.

### What we deliberately do not call

**No Maps SDK, no map tiles, no Directions API.** SHUFFL does not render a map anywhere. The active
plan draws the night as a diagram, and navigation is a **deep link** into Google Maps:

```
https://www.google.com/maps/dir/?api=1&destination=<name>&destination_place_id=<place_id>
```

**A link costs nothing.** Tile loads and Directions requests are both metered; this is neither. It
also stores nothing, and it runs off `place_id`, which is the one Google field we are allowed to
keep.

**Distances between a person and a stop are computed on the device** from coordinates already in
memory for the live display fetch. The distance is ours; the coordinate is Google's and is not
persisted.

### What no API will give you

| | what to do instead |
|---|---|
| A breakdown of the ratings (how many 1-stars, how many 5-stars) | we estimate it from sentiment across the 5 reviews — **this estimate is untested** |
| More than 5 reviews | nothing. Work within it |
| When the venue is busy ("popular times") | not available through the API |
| What is on tonight — gigs, DJ nights, quiz nights | **no events API covers Delhi nightlife.** One manual pass over venue Instagrams, refreshed quarterly |
| How old the fit-out is | look at the photos. About three seconds a venue |

### What we are not using, and why

**OpenStreetMap / Overpass.** Fine for a raw list of places, but it has no ratings and no reviews,
so nothing can be scored or filtered from it. (If you ever do call it, Overpass returns a 406
unless you send a User-Agent header.)

**Scraping websites.** This is what the first pass did, and it quietly selected the wrong venues:
having an official website is a sign of being a chain or a hotel, not of being a good night out. It
produced 83% chains and hotels, 3 clubs, and missed Summer House, Bohca and Depot 48 entirely.

---

## Before you start

1. Make a Google Cloud project, turn on the Places API, attach billing. About 30 minutes.
   Check the monthly free credit — it may cover most of this.
2. Then:

```bash
export PLACES_KEY=...
cd simulations
```

Total spend for a full run: roughly **₹2,500–4,500** ($30–55).

---

## Step 1 — Find the venues

```bash
python pipeline.py discover --dry-run                   # shows the cost, spends nothing
python pipeline.py discover --key $PLACES_KEY           # South Delhi, the default
python pipeline.py discover --key $PLACES_KEY --catchment ncr
```

It searches each district for five kinds of place — bar, night club, pub, restaurant, cafe.

| catchment | districts | calls | cost |
|---|---|---|---|
| `south-delhi` (default) | 20 | 100 | about $3.50 |
| `ncr` | 32 | 160 | about $5.60 |

Output: `candidates.json`.

The district lists are at the top of `pipeline.py`, as `SOUTH_DELHI` and `REST_OF_NCR`. Edit them to
add an area or change a radius. Districts are allowed to overlap — duplicates are dropped by
`place_id`, so covering the same ground twice costs one extra call and never a duplicate row.

**How to tell it worked:** Summer House, Bohca, Dear Donna, Depot 48 and Imperfecto HKV should all
appear without anyone naming them. The website-based pass missed all five.

---

## Step 2 — Get the details

```bash
python pipeline.py enrich --key $PLACES_KEY --limit 20   # try twenty first
python pipeline.py enrich --key $PLACES_KEY              # then the rest
```

### If you already have a list of your own

**`enrich` does not insist on `candidates.json`.** Point `--src` at any CSV with a
`google_place_id` column and it will read that instead:

```bash
python pipeline.py enrich --dry-run --src candidates_south_delhi.csv   # count and cost, spends nothing
python pipeline.py enrich --key $PLACES_KEY --src candidates_south_delhi.csv
```

It also accepts a `place_id` column, takes `name` and `discovered_area` when they are there, and
**drops repeated place_ids before spending anything**. Excel's byte-order mark is handled, so a sheet
saved as CSV works without being cleaned up first.

**Always run `--dry-run` first.** It prints the row count, the unique place_id count and the cost:

```
561 rows read, 561 unique place_ids, ~$14.03
```

If those two counts differ, the difference is duplicates that have already been removed - not an
error.

One Place Details call per venue. Roughly **$25–50** depending on how many candidates you have.

Every response is saved to `cache/places/`, so **running it again costs nothing**. You can stop it
and restart it whenever you like. It retries automatically if Google rate-limits you.

### How the reviews actually arrive

There is no separate "get reviews" call. **The reviews come back inside the same Place Details
response as the rating and the opening hours** — you just have to ask for them.

Google only sends the fields you name, in a header called the field mask. Ours asks for everything
we use, `reviews` among them:

```
POST https://places.googleapis.com/v1/places/<place_id>
X-Goog-Api-Key:    <your key>
X-Goog-FieldMask:  id,displayName,formattedAddress,location,types,rating,userRatingCount,
                   priceLevel,regularOpeningHours,businessStatus,editorialSummary,
                   generativeSummary,reviews,liveMusic,goodForWatchingSports,outdoorSeating,
                   reservable,servesDinner,servesBrunch,servesDessert,servesVegetarianFood
```

Two things follow from that:

**Asking for `reviews` is what puts the call on the expensive tier.** The field mask decides the
price. Without reviews and the atmosphere fields it would be a few dollars per thousand instead of
$25 — but without reviews there is nothing to score, so this is the call we want.

**You get at most five**, and you cannot choose which five. They come back as objects; we take the
text out of each one and nothing else:

```python
texts = [rv['text']['text'] for rv in detail.get('reviews', [])]
```

Those five strings, plus the two summary sentences, are the entire corpus every factor score is
worked out from.

**And then we throw them away.** The review text is held in memory long enough to produce the
scores and is never written to the database — that is the storage rule at the top of this page. The
raw responses sit in `cache/places/` so a re-run costs nothing, and **that cache is working scratch,
not the database.** It is in `.gitignore` and should not be shipped or kept.

Output: `enriched.json`.

---

## Step 3 — Build the database

```bash
python pipeline.py build
```

No API calls. No cost. This is where the actual work happens, in four passes.

### 3a. Admission — who gets in

A venue has to clear all of these:

| | the test | why |
|---|---|---|
| Volume | at least **200 ratings** | below that the average means nothing |
| Average rating | at or above the **35th percentile of its own type** | see the warning below |
| Consistency | sentiment spread of **0.85 or less** | a venue that is great on Friday and awful on Tuesday is not reliable |
| Operator | chain, group, hotel, or established independent | keeps out one-man operations |
| Fit-out | **done up within the last 15 years** | filled in by hand, see step 4 |
| Drift | newest reviews not far below the lifetime average | catches places on the way down |

**The average rating must be compared within type, not against a fixed number.** A real test run
rejected Privee — a well-known club with 1,380 reviews — because its average is 3.6. Clubs collect
complaints about the door that restaurants never get, so a flat 4.0 cut-off is a filter against
clubs rather than against bad venues. The pipeline uses the 35th percentile within each type, and
only falls back to 4.0 when there are fewer than eight venues of that type to compare against.

**A venue the pipeline cannot classify is let in and flagged**, never rejected. Otherwise anything
needing a human to look at it could never reach the human.

### 3b. Factor scores from the reviews

Scores come out of the review text, using a word list. The idea it rests on:

> **It does not matter whether the reviewer liked it.** "Too loud" and "amazing energy" tell you the
> same thing about the room. We count what people describe, not what they thought.

That is why five reviews is enough — we are collecting vocabulary, not opinions.

How one score is worked out, in order:

1. **Count the words.** Each factor has a list for the high end and one for the low end. `ENRG` high
   is *packed, pumping, dance floor, till 2am*; low is *quiet, calm, intimate, mellow*.
2. **Ignore the ones that are negated.** "No dance floor" does not count as a dance floor.
3. **Ignore the wrong sense of a word.** "Traditional tapas" is a cuisine, not heritage. Without
   this rule, a 2017 hotel bar scored 77 for heritage.
4. **Turn the balance into a number.** All high-end words gives 100, all low gives 0, an even split
   gives 50.
5. **Mix it with what the venue type suggests.** A club is assumed loud before you read a word. The
   more evidence the text gives, the more it overrules that assumption. Two keyword hits barely move
   a club; thirty hits overrule it completely.

Kwality in Connaught Place is the clean example. Thirty-four heritage words against a restaurant's
assumed heritage of 20, and it lands on **86**. The reviews said it, so the assumption loses.

**Accuracy: about 7 points out on average** against venues scored by hand. Good enough to order a
list of ten venues. Not good enough to print as a fact on a venue page.

### 3c. The venue's own statements beat the reviews

If the venue's listing says something directly, that wins over anything inferred from words.

| the listing says | we set |
|---|---|
| `liveMusic` is true | live music = 85 |
| `liveMusic` is false | live music = **not its thing** |
| `goodForWatchingSports` is true | there is a main event = 78 |
| `outdoorSeating` is true | looks = at least 60 |
| every `serves…` food field is false | food = **not its thing** |

The food fields are only used when they are **all false**. Every bar in Delhi "serves dinner" — that
tells you a kitchen exists, not that the food is any good. The field is good at proving absence and
bad at proving presence, so only the half it is good at gets used.

### 3d. Three states, not a number for everything

Each preference ends up in one of three states:

| | means |
|---|---|
| **a score** | the reviews said so |
| **not its thing** | a flag, never a zero |
| **unknown** | no claim either way |

The difference between the last two matters. If nobody mentions food at a *restaurant*, that is real
— reviewers of restaurants write about food. If nobody mentions food at a *bar*, that is not
evidence, because reviewers of bars write about the drinks and the room. A bar with a good kitchen
can go a hundred reviews without anyone saying so.

**Never write "not its thing" as a score of zero.** A zero says we measured it and it was bad. The
flag says this is not what the place is for. They are different claims and a zero cannot be undone
later.

### 3e. Hour-by-hour scores, and the ones left empty

A venue is not the same place at 2pm and 2am. Each time band gets its own scores where we can work
them out, and is left empty where we cannot.

A band only gets filled when a source **names a time**: "Sunday brunch", "every Wednesday", "the
weekend go-to", "closes at 1am". A glowing review with no hour in it improves the venue's general
score and must not touch a band.

**Never fill a band with a guess based on the venue type.** Leave it empty. The app falls back to
the type at the moment of asking, where it is visible and can be changed. A stored guess looks
exactly like a measurement a month later, and that is the one mistake that would poison everything.

Expect **about half to two-thirds of bands to fill**, with the gaps concentrated late at night —
because that is the part nobody writes down. A listing tells you what a place is; reviews describe
the busy night. The quiet Tuesday at eleven is unrecorded everywhere.

---

## Step 4 — The part a human has to do (1–2 hours)

`human_pass.csv` comes out with two blank columns, listing **only the venues that got in**.

**`operator_class`** — chain, group, hotel, independent-professional, or owner-local. The pipeline
guesses from the brand and address and only asks you about the ones it could not work out.

**`fitout_years`** — how long since the room was last done up. Look at the photos; about three
seconds each. Over 15 years fails.

Paste the filled columns back and run `python pipeline.py build` again.

---

## What comes out

| file | what it is |
|---|---|
| `venues.json` | the database — one row per venue, with its scores, its bands, and whether it got in |
| `gold_list.json` | every band we could not fill. This is the gold promotion's queue, ready to use |
| `human_pass.csv` | the two columns above |

The gold list is not a separate decision anyone makes. It is simply the gaps, sorted by how popular
the venue is.

---

## How the app uses it

Worth knowing, because it tells you which fields actually matter.

**First, the shape.** For each stop the user drew, rank every venue open at that hour by how close
its energy and crowd are to what they drew:

```
distance = |venue energy − drawn energy| + 0.6 × |venue crowd − drawn crowd|
```

Everything within 12 points of the best match goes in the list. Nothing outside that gets in, no
matter how well it suits the person — they drew a line and the line wins.

**Then, the preferences, to order that list.** A preference counts at a stop if someone in the group
is at 60 or above on it **and** some venue in the list can actually serve it. If nothing in the list
can serve it, it does not count there and carries over to the next stop instead.

Preferences never override the shape and never remove a venue from the list. Someone who does not
care about games is not objecting to games — they are just not asking for them.

**So the two fields the app cannot run without are energy/crowd and opening hours.** Everything else
improves the order; those two decide whether a venue can appear at all.

---

## Things that will catch you out

**Compare ratings within type.** Covered above, and it is the single most expensive mistake
available — it quietly deletes the clubs.

**Never store a band you guessed from the venue type.** Leave it empty.

**Store only IDs and your own numbers.** Everything of Google's is fetched fresh for display.

**Check the mapping between venue types and type assumptions.** This has broken twice. Once the
pipeline's type names did not match the word-list's at all, and every score came out at an extreme.
Then a jazz club scored 0 for energy because "live room" was in one list and not the other. **A type
with no assumption behind it is not neutral — it is unrestrained**, and it produces exactly the wild
numbers the assumptions exist to prevent.

**The consistency estimate is unverified.** No API gives a breakdown of the ratings, so we estimate
it from the tone of five reviews, with complaints about the door removed first (a venue with a
selective door collects those, and counting them would penalise exactly the venues the filter is
meant to keep). **Check this once you have a few hundred rows.**

---

## Checking it before you trust it

`simulations/realrun.py` holds **sixteen Delhi NCR venues researched by hand**, with their real
ratings and review counts. Fourteen get in, two do not.

Run the pipeline over the same sixteen and the numbers should match. It is the only check that
exists, and the places where it disagrees will tell you more than the places where it agrees.

One failure from that research worth remembering: searching for "Cirrus 9" returned a venue at The
Oberoi, when Cirrus 9 is at the Shangri-La. **A wrong venue is worse than no venue**, and it is the
failure mode hand-collection has that an API call does not — the API matches on an ID, a person
searching matches on a name and a guess.

---

## Where everything lives

| | |
|---|---|
| `simulations/pipeline.py` | the tool itself |
| `simulations/lexicon.py` | the word lists |
| `simulations/realrun.py` | the sixteen hand-checked venues |
| `VENUE_DATABASE_V1.md` | the reasoning behind every rule here |
| `VENUE_DB_REVIEW_01.md` | the review of the first attempt, and what went wrong |
| `GOLD_PROMOTION_V1.md` | how the empty bands get filled later, by users |

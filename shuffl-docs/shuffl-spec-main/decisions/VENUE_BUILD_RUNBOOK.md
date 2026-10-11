# Building the venue database — the runbook

**Everything needed to go from nothing to a filtered venue database with a gold list.** Written
2026-10-04. The reasoning behind each step is in `VENUE_DATABASE_V1.md`; this is the instructions.

> **If you want all of it in one plainly-written file, read `VENUE_DATABASE_HOW_TO.md` instead.** This page is the commands only.
>
> **About one working day, and roughly ₹1,300–5,300 of API spend.**

---

# Before you start

**A Google Cloud project with the Places API enabled and billing attached.** ~30 minutes, one-off.
Check the monthly free credit — it may cover most of this.

**Real prices, checked 2026-10-04:** Place Details *Enterprise + Atmosphere* **$25 / 1,000**, Text
Search *Enterprise* **$35 / 1,000**, Place Photos **$7 / 1,000**.

```bash
export PLACES_KEY=...
cd simulations
```

---

# Step 1 — Discover · ~20 min · ~$4

```bash
python pipeline.py discover --dry-run                   # shows the cost, spends nothing
python pipeline.py discover --key $PLACES_KEY           # South Delhi (the default)
python pipeline.py discover --key $PLACES_KEY --catchment ncr
```

**Two catchments, and `--catchment` picks one.**

| | districts | calls | cost |
|---|---|---|---|
| **`south-delhi`** (default) | 20 | 100 | **~$3.50** |
| `ncr` | 32 | 160 | ~$5.60 |

**South Delhi is the default because it is what the first database pass covers; NCR is the
destination** (`MVP_INSTRUCTIONS.md` §2.3, ~360 venues). → `candidates.json`.

**The lists are at the top of `pipeline.py`** — `SOUTH_DELHI` and `REST_OF_NCR`, and `ncr` is the
two concatenated. Edit either to add an area or tighten a radius; **those lists *are* the definition
of the catchment.** Districts may overlap freely: **duplicates are dropped on `place_id`, so
over-covering costs one extra call and never a duplicate row.**

---

# Step 2 — Enrich · ~30 min · ~$25–50

```bash
python pipeline.py enrich --key $PLACES_KEY --limit 20    # try twenty first
python pipeline.py enrich --key $PLACES_KEY
```

**One Details call per venue.** Returns rating, review count, price, opening hours, **five review
texts**, and the structured attributes — `liveMusic`, `outdoorSeating`, `goodForWatchingSports`,
`reservable`, the `serves*` family, `editorialSummary`.

**Every response is cached to `cache/places/`, so a re-run costs nothing.** Interrupt it freely.
Retries with backoff on 429 and 5xx.

---

# Step 3 — Build · minutes · free

```bash
python pipeline.py build
```

No API calls. It runs **admission** (type-relative), the **lexicon**, the **venue's own structured
fields**, and the **confidence gate**, and writes:

**The corpus is the five review texts plus the editorial and generative summaries** (2026-10-05).
Those two sentences are the densest the call returns and were being fetched and discarded.

**Then the venue's own fields win.** A structured field is the venue saying so on its own listing,
so where it is present it beats any amount of keyword inference, and where it is absent it says
nothing: `liveMusic` true sets `LIVE` 85 and false marks it **not specialised**;
`goodForWatchingSports` sets `FOCUS`; `outdoorSeating` floors `SCEN` at 60; and **the `serves*`
family is used only in its all-false form**, because every bar "serves dinner" and that proves a
kitchen exists rather than that food is the point.

| | |
|---|---|
| **`venues.json`** | the database — one row a venue, with `base` scores, `slots_filled`, `slots_gold`, `admitted` |
| **`gold_list.json`** | **every slot the evidence could not reach** — this is the promotion's queue, and it is not a separate decision |
| **`human_pass.csv`** | the two columns no API provides, **for admitted venues only** |

---

# Step 4 — The human pass · 1–2 hours

`human_pass.csv` has two blank columns:

**`operator_class`** — `chain` / `group` / `hotel` / `indie-pro` / `owner-local`. The pipeline
guesses from brand and address and only lists the ones it could not. **A venue it cannot classify
is admitted and flagged rather than rejected** — otherwise anything needing a human could never
reach the human.

**`fitout_years`** — how long since the room was last done. **A glance at the photos, about three
seconds.** Over 15 years fails admission.

Paste the filled columns back and re-run `build`.

---

# What comes out, and what to do with it

**`venues.json`** is the MVP's venue list. Every admitted venue has a `base` — eleven factor
scores from its review text — which is what the *5–10 venues per stop* picker ranks on.

**`gold_list.json`** goes straight into the promotion. Sort by venue popularity and that is the
queue (`GOLD_PROMOTION_V1.md`).

**Expect roughly half to two-thirds of slots filled** and the gaps concentrated in the late bands,
because the evidence is thinnest exactly where a venue transforms.

---

# What the pipeline cannot do, by design

| | |
|---|---|
| **`rating_sd`** | **No source provides a rating histogram, and Places returns 5 reviews.** It substitutes **sentiment variance over those five, with door complaints routed out first** — because variance in *door* complaints is evidence of a door, not inconsistency, and counting it would penalise exactly the selective venues the filter is for. **This substitution is untested.** Check it once there are a few hundred rows. |
| **`fitout_years`** | not in any API. The human pass. |
| **the schedule** | **the slots.** Boxout Wednesday was on Summer House's Instagram and in **zero** reviews. No events API covers Delhi nightlife — one manual pass over the venue Instagrams at seed time, refreshed quarterly (`VENUE_DATABASE_V1.md` §2a1). |
| **the bands** | that is what the gold promotion is for. |

---

# Three things that will bite, and have already

**The mean floor must be type-relative.** A real pass rejected **Privee** — a well-known club, 1,380
reviews — on a 3.6 mean. Clubs collect door complaints restaurants do not, so **an absolute 4.0
floor is a type bar, not a quality bar.** The pipeline uses the **35th percentile within type**, and
falls back to 4.0 only when a type has fewer than eight venues to compare.

**Never store a slot inferred from the type curve.** A stored guess is indistinguishable from a
measurement a month later. Leave it empty; the fallback happens at query time, where it is visible
and reversible.

**Store only IDs and our own derived data.** `place_id` may be cached indefinitely; Google's name,
address and rating may not. The app re-fetches those live for display, which is what Places is
licensed for (`VENUE_DATABASE_V1.md` §4a).

---

# If you want to check it before trusting it

`simulations/realrun.py` holds **sixteen Delhi NCR venues researched by hand** on 2026-10-03/04 —
real ratings and review counts. Run the pipeline over the same sixteen and the numbers should
match. **It is the only validation set that exists**, and the discrepancies will be more
interesting than the agreements.

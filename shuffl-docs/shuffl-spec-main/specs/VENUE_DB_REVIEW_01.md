# Venue database, pass 1 — review and what to change

> **Superseded in part by `VENUE_DB_INSTRUCTIONS_02.md` (2026-10-06).** The licence rule and what to keep still stand; the "what to run" section is replaced there, after a second pass discovered venues from OpenStreetMap instead.

**Reviewing `SHUFFL_South_Delhi_Venue_Database_MVP.xlsx`, 110 venues, delivered 2026-10-05.**
Read with `VENUE_DATABASE_V1.md`, `VENUE_BUILD_RUNBOOK.md` and `MVP_INSTRUCTIONS.md`.

> **The structure is right and the discipline is better than asked for. What's missing is the
> evidence layer, and one decision caused nearly all of it — a reading of the Google licence that
> is stricter than the licence actually is.** Fix that one thing and most of the rest follows from
> a tool that already exists.

---

# 1. What to keep

**Do not rebuild these. They are the parts a pipeline cannot produce.**

**The field-level sourcing.** 1,818 rows in `Venue_Sources`, each naming the field it supports with
a URL, a source date and an access date. **Keep this sheet and keep filling it.** It is the audit
trail if our licensing is ever questioned, and no API gives it to us.

**The refusal to invent.** *"Estimated slots: 0. No invented time schedules."* Every gap is an
honest `Unknown`. **This is the single most important behaviour in this job and it was done
correctly.** A fabricated slot is indistinguishable from a measured one a month later, and it would
have corrupted the database silently — see `VENUE_DATABASE_V1.md` §2a1 rule 3.

**The verification queue, the review queue and the duplicate handling.** 2,571 tracked gaps, 23
candidates parked rather than waved through, and the WYTE/BLAQ and Woodpecker duplicates caught and
documented. **`Needs_Verification` already names almost every gap this review finds**, which means
the problem was never diagnosis — it was being blocked.

---

# 2. Change this first — the licence is less strict than you read it

**The rule is about storage, not about access.**

> We may **call** the Places API and **derive our own data** from what it returns.
> We may not **store** Google's names, addresses, ratings, review text, photos or hours.
> We may store **`place_id` indefinitely**, and we may store **anything we computed ourselves**.

**So ratings and review text are usable.** A rating and a review count run the admission filter in
memory and are then discarded; review text runs the lexicon and what we keep is **our factor
scores**, which are our own derived work and our own copyright. Nothing of Google's persists except
the `place_id`. That is the design in `VENUE_DATABASE_V1.md` §4a, and the whole pipeline is built
around it.

| field | may we store it | where it comes from |
|---|---|---|
| `place_id` | **yes, indefinitely** | Places. **Get this for every venue — it is how the app re-fetches display data legally** |
| our factor scores | **yes — they are ours** | the lexicon, computed from review text that is not stored |
| admission decision | **yes — it is ours** | computed from rating, count, SD, operator, fit-out |
| name, address, rating, reviews, photos, hours | **no** | re-fetched live for display at render time |

**`google_place_id` is filled on 3 of 110 rows.** Without it the venue screen cannot show a photo, a
rating or a review legally, because the live re-fetch has nothing to key on. **Treat it as a
required field.**

---

# 3. What is missing, measured

| | filled | why it matters |
|---|---|---|
| **all nine factor scores** | **0 / 110** | **the database exists to carry these.** Without them the stop list cannot rank, `SHAPE_GATE` cannot run, and the MVP's core loop has no input |
| any factor score | 9 / 110 | |
| **opening hours** | 67 (61%) | **the one field the stop list cannot run without.** 43 venues can never appear in a stop list |
| latitude / longitude | 37 (34%) | the distance filter, and the walk between stops |
| **`google_place_id`** | **3 (3%)** | §2 above |
| price band | 2 (2%) | the budget filter, and a line on every venue row |
| fit-out year | 0 | admission |

**And the slots carry the same gap.** 155 rows across 110 venues, 99 marked `Confirmed` — but the
coverage report is careful that this means *the timing* is confirmed, not the scores. **2 of 155
slots carry any score.** A slot with no scores is not wrong, it just does nothing: at query time it
falls back to the type curve, which is what an empty slot is supposed to do.

### Admission did not run

All 110 are `Admitted`, on *"named public venue with official location evidence"*. **That tests
whether a place exists and is documented. Our filter tests whether it is established and reputed**,
which is a different question. Four of the six criteria have no column at all:

```
volume >= 200 reviews                      no column
mean at the 35th percentile WITHIN TYPE    no column          <- note: WITHIN TYPE, not absolute
spread SD <= 0.85                          no column
operator class                             present, 100% filled   OK
fit-out <= 15 years                        present, 0% filled
drift (recent vs lifetime mean)            no column
```

**The mean floor must be type-relative and this is not a detail.** A real pass rejected Privee — a
well-known club with 1,380 reviews — on a 3.6 mean, because clubs collect door complaints that
restaurants do not. **An absolute 4.0 floor is a type bar, not a quality bar.** Use the 35th
percentile within type, falling back to 4.0 only when a type has fewer than eight venues.

---

# 4. The discovery method selected for the wrong venues

**This is the finding that is hardest to see from inside the work, and it matters more than any
single empty column.**

Building from official websites means **website presence became the filter** — and an official
website is a proxy for *chain or hotel*, not for *established nightlife*. Independent venues in
Delhi often have an Instagram and nothing else.

| | |
|---|---|
| Group, Chain or Hotel-attached | **91 of 110 — 83%.** Independent: 18 |
| branches of just nine brands | **33 rows** — 6 Blue Tokai, 6 First Coffee, 4 SOCIAL, 3 Third Wave, 3 Nukkad, 3 Big Chill, 3 Burma Burma, 2 Chili's, 2 Piano Man |
| hotel F&B | 26 — a Marriott lobby lounge, three Aloft outlets, four at The Grand, a Novotel buffet |
| a nightlife type at all | **36 of 110** |
| **clubs** | **3** |
| Aerocity vs Hauz Khas | **21 vs 8** — the airport hotel district outweighs the actual nightlife centre by nearly three to one |

**Three clubs is the gap that matters most.** The club end is where the app's utility is highest,
because that is where *finding people* beats *finding the place*.

**And five well-known venues inside the stated catchment are absent:** **Summer House** (Hauz Khas),
**Bohca** and **Dear Donna** (Qutub/Mehrauli), **Depot 48** (Defence Colony), **Imperfecto** (HKV).
The catchment list names all four of those areas.

**Rating volume is exactly what separates a chain coffee branch from an established independent
bar**, which is why the admission filter is built on it. Without ratings, website presence was the
only signal available — and it pointed the wrong way.

---

# 5. What to run

**`simulations/pipeline.py` produces every missing column and is ready.** Full instructions in
`VENUE_BUILD_RUNBOOK.md`; the short version:

```bash
export PLACES_KEY=...
cd simulations

python pipeline.py discover --dry-run            # prices it, spends nothing
python pipeline.py discover --key $PLACES_KEY    # South Delhi: 20 districts, 100 calls, ~$3.50
python pipeline.py enrich   --key $PLACES_KEY    # one Details call each, ~$25-50
python pipeline.py build                         # no API, free
```

**`discover` defaults to the South Delhi catchment**, which is the 20 districts your pass covers —
Hauz Khas and Deer Park, Safdarjung Enclave, Green Park and SDA, Panchsheel Park, Malviya Nagar,
Saket, Mehrauli and Qutub, Vasant Kunj, Vasant Vihar, Aerocity, Defence Colony, Lajpat Nagar, South
Extension, GK I and II, Kailash Colony, Nehru Place, Kalkaji and CR Park. `--catchment ncr` adds the
other twelve when we widen. **Districts overlap on purpose; duplicates drop on `place_id`.**

**`enrich` caches every response to `cache/places/`, so a re-run costs nothing.** Interrupt it
freely. It retries with backoff on 429 and 5xx.

**`build` needs no API.** It runs type-relative admission, the lexicon over the five returned review
texts, and the slot confidence gate, and writes `venues.json`, `gold_list.json` and
`human_pass.csv`.

### Three things to expect

**The list will get shorter.** Many coffee branches will not clear the volume floor and several
hotel outlets will not clear the type-relative mean. **That is the filter working** — the MVP wants
roughly 360 NCR venues that are established, not 110 that are documented.

**Discovery should come from Nearby Search, not from websites.** The South Delhi catchment is
already in `pipeline.py` as `SOUTH_DELHI` and is the default, so **the five missing venues should
appear without being named** — that is the check that the method changed, not just the tool.

**The lexicon runs about 7 points of mean error** against hand-scored venues. That is good enough to
rank a stop list and not good enough to state as fact on a venue page.

---

# 6. What the pipeline will not give you — keep doing these by hand

| | |
|---|---|
| **`fit-out age`** | not in any API. `human_pass.csv` lists it, and it is **a glance at the photos, about three seconds a venue** |
| **operator class where it is unclear** | the pipeline guesses from brand and address and flags the rest. **A venue it cannot classify is admitted and flagged, never rejected** — otherwise anything needing a human could never reach one |
| **the schedule** | **no events API covers Delhi nightlife.** Boxout Wednesday was on Summer House's Instagram and in zero reviews. One manual pass over venue Instagrams at seed time, refreshed quarterly |
| **`rating_sd`** | **no source provides a rating histogram and Places returns five reviews.** We substitute sentiment variance over those five with door complaints routed out first — **and that substitution is untested.** Check it once there are a few hundred rows |
| **the bands** | that is what the gold promotion is for (`GOLD_PROMOTION_V1.md`) |
| **field-level sources** | your sheet. Keep it |

---

# 7. The checklist

1. **Get `place_id` for all 110** — it is the one Google field we may keep, and display depends on it.
2. **Run `discover` from Nearby Search over the South Delhi districts**, not from websites.
3. **Run `enrich`, then `build`.** Admission runs properly for the first time, with the mean floor
   **relative to type**.
4. **Expect the list to shrink, and expect new independents to appear.** Both are the filter working.
5. **Fill `fitout_years` and the flagged operators** from `human_pass.csv`, then re-run `build`.
6. **Keep `Venue_Sources` and the `Unknown` discipline exactly as they are.**
7. **Leave empty slots empty.** Never store a slot inferred from the type curve — the fallback
   happens at query time, where it is visible and reversible.

---

**One sentence for the next pass:** the work was blocked by a rule that does not say what it
appeared to say, and `pipeline.py` has been waiting for a key the whole time.

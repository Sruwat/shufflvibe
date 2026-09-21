# Area scores V1 — Delhi NCR neighbourhoods, four factors, three time bands

**For:** `OUTING_PLAN_ENGINE.md` §13.7. An area can carry `CROWD`, `ENRG`, `POL` or `SCEN` for a
person when the venue itself cannot, at half strength. These are the numbers it reads.

**What this is.** A first pass, authored 2026-09-17 from knowledge of the city, not measured.
Every number here is a starting point to be replaced by the footfall-weighted median of the
venues scored in that area (§4 below) as soon as enough venues are in — and `POL` and `SCEN`
checked by people who go out in Delhi. Treat it the way the brief treats every constant: build
with it, tune from data.

**Scale.** 0–100, same as a venue's factor score.

| Factor | What the area number means |
|---|---|
| `CROWD` | how busy the *street* is — people on the pavement, queues, cars, not any one venue |
| `ENRG` | how much of a night is going on around you — spill-out, music through doors, where people are heading |
| `POL` | how dressed the area expects you to be; how polished it feels |
| `SCEN` | what it looks like when you step out — lit-up, pretty, atmospheric — or not |

**Time bands.**

| Band | Clock | Why it is its own band |
|---|---|---|
| `early` | 7:00 – 9:30 pm | dinner crowd; markets and cafés still open |
| `late` | 9:30 pm – 12:30 am | the bar crowd; the night's peak nearly everywhere |
| `after` | 12:30 – 3:00 am | most of Delhi shuts at 1; Gurgaon and the hotel districts run on |

`POL` and `SCEN` change little across bands; `CROWD` and `ENRG` change a lot, and the `after`
column mostly encodes *what is still open*.

---

## 1. The table

`C / E / P / S` = `CROWD` / `ENRG` / `POL` / `SCEN`.

### Delhi — south and central

| Area id | Neighbourhood | early C/E/P/S | late C/E/P/S | after C/E/P/S | The street, in a line |
|---|---|---|---|---|---|
| `hkv` | Hauz Khas Village | 60/50/50/85 | 88/80/55/90 | 45/40/50/70 | lanes, lake, rooftops; packed by ten, emptying by one |
| `cp` | Connaught Place (inner + middle circle, Janpath) | 80/60/55/70 | 85/75/55/70 | 40/35/50/55 | the colonial arcade, every kind of bar; big and loud late |
| `khan` | Khan Market | 75/45/80/70 | 65/45/80/65 | 15/10/75/50 | dressed-up dinner; shuts early |
| `aero` | Aerocity | 55/45/90/75 | 65/65/90/80 | 60/65/90/80 | hotel bars and clubs; polished, and open when nothing else is |
| `mehrauli` | Mehrauli / Qutub (Qutub Minar, Ambawatta, the 1 AQ side) | 55/40/65/90 | 60/50/70/85 | 20/15/65/70 | the minar lit up behind the terrace; the prettiest night in the city |
| `champa` | Champa Gali (Saidulajab) | 55/35/55/85 | 50/35/55/80 | 5/5/50/50 | fairy-lit courtyard lane; cafés more than bars; early |
| `chhatarpur` | Chhatarpur / Dhan Mill | 50/35/75/85 | 55/45/75/80 | 15/10/70/60 | warehouse-chic compound and farm restaurants; quiet street outside |
| `gk` | Greater Kailash (GK-1 M/N block, GK-2 M block) | 65/45/65/60 | 70/60/65/55 | 25/20/60/45 | market-block bars; busy, unremarkable street |
| `defcol` | Defence Colony (market + flyover strip) | 55/40/70/65 | 55/45/70/60 | 15/10/65/45 | leafy, polished, dinner-then-home |
| `saket` | Saket (Select Citywalk, DLF Avenue, the plaza) | 75/50/70/65 | 65/55/70/60 | 20/20/65/45 | mall plaza crowd; lively early, mall hours |
| `vk` | Vasant Kunj (Promenade, Emporio, Ambience) | 65/45/85/65 | 60/55/85/60 | 20/20/80/45 | luxury-mall polished; the street is a car park |
| `nehru` | Nehru Place / Epicuria | 60/45/50/45 | 60/55/50/40 | 15/15/45/30 | metro-station bars; functional |
| `lodhi` | Lodhi Colony / Lodhi Road (Bikaner House, the art district) | 40/25/75/85 | 35/25/75/80 | 5/5/70/60 | murals, wide avenues, gardens; beautiful and quiet |
| `shahpur` | Shahpur Jat | 45/35/60/75 | 40/35/60/70 | 5/5/55/50 | boutique-and-café village; early |
| `greenpark` | Green Park / Safdarjung Enclave (Deer Park, Aurobindo Market, Yusuf Sarai) | 55/40/45/55 | 55/45/45/50 | 15/10/40/35 | neighbourhood bars; easy, unshowy |
| `sunder` | Sunder Nursery / Humayun's Tomb | 35/15/60/95 | 10/5/60/80 | 0/0/60/50 | the most beautiful early evening in Delhi; nothing after |

### Delhi — old, north and west

| Area id | Neighbourhood | early C/E/P/S | late C/E/P/S | after C/E/P/S | The street, in a line |
|---|---|---|---|---|---|
| `purani` | Old Delhi (Chandni Chowk, Jama Masjid, Chawri Bazar) | 95/55/15/80 | 85/50/15/80 | 40/25/15/60 | the food streets; packed, unpolished, unlike anywhere else |
| `mkt` | Majnu ka Tilla | 60/40/25/70 | 55/40/25/65 | 10/5/25/40 | Tibetan lanes, momos and beer; low-key, distinct |
| `karol` | Karol Bagh | 85/50/25/40 | 70/50/25/40 | 20/15/25/25 | market crowd; not a night-out street |
| `rajouri` | Rajouri Garden / Punjabi Bagh | 70/55/50/40 | 80/75/55/40 | 40/40/50/30 | west Delhi's club strip; loud, late, dressed its own way |
| `lajpat` | Lajpat Nagar | 90/45/20/45 | 60/35/20/40 | 10/5/20/25 | market; shuts with the shops |
| `paharganj` | Paharganj | 80/50/10/50 | 75/50/10/50 | 40/35/10/40 | backpacker strip; rooftops, cheap, late |

### Gurgaon

| Area id | Neighbourhood | early C/E/P/S | late C/E/P/S | after C/E/P/S | The street, in a line |
|---|---|---|---|---|---|
| `cyberhub` | Cyber Hub | 85/60/70/75 | 90/80/70/80 | 55/55/70/70 | the big open-air strip; lit up, packed, everyone's first Gurgaon night |
| `s29` | Sector 29 (Leisure Valley) | 65/55/45/45 | 88/85/50/50 | 65/65/50/45 | the bar-and-brewery block; loud, late, casual |
| `gcr` | Golf Course Road (One / Two Horizon, DLF Phase 5) | 50/40/85/70 | 60/60/85/70 | 40/40/85/65 | tower-base bars; polished, late licence |
| `mgroad` | MG Road (Sikanderpur, the mall row) | 70/50/50/45 | 70/65/50/45 | 45/45/45/35 | old-Gurgaon clubs and mall bars; busy, worn |
| `sohna` | Sohna Road / Sector 49–50 | 60/45/45/40 | 65/55/45/40 | 30/30/45/30 | neighbourhood breweries; local crowd |
| `s15` | 32nd Avenue / Sector 15 | 55/40/65/60 | 65/60/65/60 | 35/35/65/50 | one polished block; a good street on a good night |
| `wm65` | Worldmark 65 / Sector 65–66 | 50/35/75/65 | 50/40/75/60 | 20/20/70/50 | new, polished, quiet outside |

### Noida, Ghaziabad, Faridabad

| Area id | Neighbourhood | early C/E/P/S | late C/E/P/S | after C/E/P/S | The street, in a line |
|---|---|---|---|---|---|
| `s18` | Noida Sector 18 (Atta, Mall of India, GIP) | 85/55/45/50 | 75/65/45/50 | 30/30/45/35 | Noida's centre; mall crowd, a few late bars |
| `galleria` | Gardens Galleria (Sector 38A) | 65/45/55/55 | 65/60/55/55 | 25/25/55/40 | the open-air bar row; Noida's best late street |
| `gn` | Greater Noida (Pari Chowk, Knowledge Park) | 45/35/35/40 | 40/35/35/35 | 10/10/35/25 | student crowd; early |
| `indira` | Indirapuram / Vaishali | 65/45/35/35 | 55/45/35/35 | 15/15/35/25 | mall-anchored; local |
| `fbd` | Faridabad (Sector 15–16, the Crown strip) | 55/40/35/35 | 45/40/35/30 | 10/10/35/20 | local; early |

Thirty-five areas. A venue outside all of them gets `area = None` and the fallback never fires
for it — that is correct, not a gap.

---

## 2. How to tag a venue

One `area_id` per venue, by *where you step out onto the street*, not by postal address. The
edge cases that will come up:

- A venue on the **border** of two (Champa Gali vs Mehrauli; the 1 AQ side of Mehrauli vs
  Chhatarpur): whichever street its door opens onto.
- A **hotel** venue inside a hotel district (Aerocity, Golf Course Road): the district.
- A **mall** venue: the mall's area (`saket`, `vk`, `s18`); the plaza outside is the street.
- A **farmhouse** or private venue in Chhatarpur with nothing around it: `None`. The area
  fallback is about a street, and there is none.
- A **rooftop**: the area below it. The view is the venue's own `SCEN`, not the area's.

---

## 3. What the numbers do, and do not do

They are read in exactly one place — `serve_level` (§13.4c) — and only when a venue fails to
deliver one of these four factors to a member who ranks it. Then, if the area's score in the
band the stop falls in passes that member's `delivers_at`, they are served at `SOFT` (0.5) and
the card says the street is carrying it. Nothing else reads this table: not overrun, not venue
scoring, not matching.

The band is the stop's **arrival time** from the plan's timing (§4), not the current clock.

---

## 4. How to replace these numbers

When an area has **six or more scored venues**:

```python
def area_scores(area, band):
    vs = [v for v in venues if v.area == area and v.footfall[band] is not None]
    if len(vs) < 6: return AUTHORED[area][band]                     # this table
    w  = {v: v.footfall[band] for v in vs}
    out = {}
    for f in ('CROWD', 'ENRG'):
        out[f] = weighted_median([v.scores[f] for v in vs], [w[v] for v in vs])   # the street is the sum of its doors
    for f in ('POL', 'SCEN'):
        out[f] = 0.5 * weighted_median([v.scores[f] for v in vs], [w[v] for v in vs]) + 0.5 * AUTHORED[area][band][f]
    return out
```

`CROWD` and `ENRG` are what the venues add up to, so the venue data replaces the authored number
outright. `POL` and `SCEN` are partly the street itself — the minar, the arcade, the murals — so
the authored number keeps half its weight until somebody rates the streets directly.

**Hand check before any of this ships:** give this table to five people who go out in Delhi
regularly and ask them to mark every number they disagree with by more than 15. Where three
agree against the table, change it. That is a two-hour job and it is the first thing to do.

---

## 5. Not established

- Every number. See the top.
- Whether three bands are enough. Friday and Saturday `late` are not Tuesday `late`; a
  day-of-week multiplier on `CROWD` and `ENRG` is the obvious first refinement, and the venue
  footfall data will say what it should be.
- Whether Old Delhi's `SCEN` 80 reads as "beautiful" to the target user or only to me. It is the
  number most likely to be argued with.
- The Gurgaon `after` numbers assume the current late licences. They move when the rules do.

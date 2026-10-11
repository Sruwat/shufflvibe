> **Superseded by `VIBE_NAMES_V4.md` (2026-09-17).** The name reads the seven vibe factors; no refusal prefix;
> preferences are badges.

# Vibe names v3 — one name, up to three parts, never a sentence

**Supersedes `VIBE_NAMES_V2.md`** (2026-09-16). V2 gave the name from the top factor alone and
put everything else on a second line — *also strong on the food, dressing up*. That second line
is gone. The name now carries the second factor and, when there is one, a fast refusal — as a
single name, not a sentence.

> **Luxury Diner** — top `POL` (classy), second `FOOD`
> **Quiet Luxury Diner** — the same person, with a fast refusal of `CROWD`
> **Solo Luxury Diner** — the same person, with a fast refusal of `AFFIL` instead

Nothing downstream reads the name. Matching and plans run on the ten scores. The name's only
job is to be recognised — so it is built from three short word-lists, and the developer never
has to invent a word.

---

## 1. The shape

```
[refusal prefix]  [top-factor word]  [second-factor word]
   optional           always           if a second factor qualifies
```

- **No second factor** → the V2 single name (§4), with the prefix if there is one:
  *Night Climber*, *Solo Night Climber*.
- **Second factor** → top word + second word: *Luxury Diner*.
- **Fast refusal** → prefix on either: *Quiet Luxury Diner*, *Quiet Night Climber*.

Three tokens at most. Hyphenated words count as one. That is the card-width rule from V2,
loosened by one.

---

## 2. The three word-lists

| Factor | as **top** | as **second** | as **refusal** (prefix) |
|---|---|---|---|
| `CROWD` | Big-Room | Crowd-Chaser | Quiet |
| `ENRG` | Peak | Climber | Low-Key |
| `SCEN` | Golden-Hour | Sightseer | No-Frills |
| `FOOD` | Hungry | Diner | Liquid |
| `POL` | Luxury *(classy / both)* · Hype *(current)* | Dresser | Casual |
| `NOV` | Uncharted | Explorer | Loyal |
| `PLAY` | Arcade | Player | No-Games |
| `LIVE` | Front-Row | Gig-Goer | Unplugged |
| `HERIT` | Old-School | Old-Soul | Modern |
| `AFFIL` | Mingling | Mixer *(off by default — §3.2)* | Solo |

`POL` as top reads its sense (`ASSESSMENT_ENGINE.md` §5.4): *Luxury* for classy or both, *Hype*
for current. As second or as refusal the sense is ignored.

Why *Liquid* for a food refusal: a person who hard-passes food is there for the drinks. *Loyal*
for a novelty refusal: they go back to places. *Modern* for heritage: they want the new build.
Every prefix is written as something they *are*, not something they lack — V2 rule 4 still holds.

---

## 3. The rules

### 3.1 Top factor — unchanged from V2

Highest score; latency breaks a tie (gap ≥ 0.15); dead heat → the forced choice
(`ASSESSMENT_ENGINE.md` §7.1, §7.3). The answer to the forced choice is the top.

### 3.2 Second factor

```python
STICKY = 15
SECOND_MIN = 60

def second_factor(scores, firmness_latency, top):
    cands = [f for f in FACTORS
             if f != top and f not in SECOND_EXCLUDED           # SECOND_EXCLUDED = {'AFFIL'}
             and scores[f] >= scores[top] - STICKY
             and scores[f] >= SECOND_MIN]
    if not cands: return None
    hi = max(scores[f] for f in cands)
    tied = [f for f in cands if scores[f] == hi]
    if len(tied) == 1: return tied[0]
    tied.sort(key=lambda f: -firmness_latency[f])
    if firmness_latency[tied[0]] - firmness_latency[tied[1]] >= 0.15: return tied[0]
    return max(tied, key=lambda f: WEIGHT[f])                   # no forced choice for the second
```

- Within 15 of the top and at least 60 — the same "also strong on" band V2 used.
- `AFFIL` is excluded by default, for V2's reason: it runs high for nearly everyone, so
  *Mixer* would be half the population's second word and mean nothing. It still competes for
  the top. The *Mixer* word exists so the exclusion can be lifted from app data without a
  rewrite.
- A tie for second is broken by latency, then by factor weight. **No forced choice** — one
  question per session is the limit, and the top gets it.

### 3.3 Refusal prefix

```python
def refusal_prefix(scores, firmness_latency, refused, validated):
    """refused: the set from ASSESSMENT_ENGINE §5.5.
    validated: has the §6.3 latency check passed for this population?"""
    if validated:
        fast = [f for f in refused if firmness_latency[f] >= FAST_REFUSAL]   # FAST_REFUSAL = 0.6
    else:
        fast = [f for f in refused if scores[f] <= 12]                       # hard pass only
    if not fast: return None
    fast.sort(key=lambda f: (scores[f], -firmness_latency[f]))              # lowest score, then fastest
    return REFUSAL_WORD[fast[0]]
```

- **Before the latency validation passes:** a hard pass (score 12) earns the prefix; a
  not-for-me on both cards (38) does not. The hard pass is the extreme swipe — it is its own
  evidence of firmness.
- **After validation:** any refusal (§5.5) whose latency-firmness is 0.6 or higher.
- **One prefix.** The firmest refusal — lowest score, then fastest. Somebody with no fast
  refusal gets no prefix, as in V2.
- The refused factor can never also be the second factor (a refused score is ≤ 38; the second
  needs ≥ 60), so the two never collide.

### 3.4 Assembly

```python
def name(scores, firmness_latency, refused, pol_sense, validated):
    top    = top_factor(...)                                     # §3.1
    second = second_factor(scores, firmness_latency, top)        # §3.2
    prefix = refusal_prefix(scores, firmness_latency, refused, validated)
    topword = TOP_WORD[top] if top != 'POL' else ('Hype' if pol_sense == 'current' else 'Luxury')
    core   = f'{topword} {SECOND_WORD[second]}' if second else SINGLE_NAME[top]
    return f'{prefix} {core}' if prefix else core
```

**Written once per session and never recomputed** — not when the population centre moves (§9),
not when latency-firmness is later re-read. The name is "your vibe today"; a different day may
give a different name, and that is the design. What must not happen is the name changing under
someone *within* a day.

---

## 4. The single names — when nothing else is within 15

V2's ten, unchanged:

| Factor | Name |
|---|---|
| `CROWD` | Crowd Chaser |
| `ENRG` | Night Climber |
| `SCEN` | Good Eye |
| `FOOD` | Plate Chaser |
| `POL` | Dressed For It |
| `NOV` | First Timer |
| `PLAY` | Score Keeper |
| `LIVE` | Set List |
| `HERIT` | Old Soul |
| `AFFIL` | Inner Circle |

With a prefix: *Quiet Night Climber*, *Solo Set List*, *Liquid Crowd Chaser*.

---

## 5. The full pair table — top down the side, second across the top

| top ↓ / second → | `CROWD` | `ENRG` | `SCEN` | `FOOD` | `POL` | `NOV` | `PLAY` | `LIVE` | `HERIT` |
|---|---|---|---|---|---|---|---|---|---|
| `CROWD` | — | Big-Room Climber | Big-Room Sightseer | Big-Room Diner | Big-Room Dresser | Big-Room Explorer | Big-Room Player | Big-Room Gig-Goer | Big-Room Old-Soul |
| `ENRG` | Peak Crowd-Chaser | — | Peak Sightseer | Peak Diner | Peak Dresser | Peak Explorer | Peak Player | Peak Gig-Goer | Peak Old-Soul |
| `SCEN` | Golden-Hour Crowd-Chaser | Golden-Hour Climber | — | Golden-Hour Diner | Golden-Hour Dresser | Golden-Hour Explorer | Golden-Hour Player | Golden-Hour Gig-Goer | Golden-Hour Old-Soul |
| `FOOD` | Hungry Crowd-Chaser | Hungry Climber | Hungry Sightseer | — | Hungry Dresser | Hungry Explorer | Hungry Player | Hungry Gig-Goer | Hungry Old-Soul |
| `POL` classy/both | Luxury Crowd-Chaser | Luxury Climber | Luxury Sightseer | **Luxury Diner** | — | Luxury Explorer | Luxury Player | Luxury Gig-Goer | Luxury Old-Soul |
| `POL` current | Hype Crowd-Chaser | Hype Climber | Hype Sightseer | Hype Diner | — | Hype Explorer | Hype Player | Hype Gig-Goer | Hype Old-Soul |
| `NOV` | Uncharted Crowd-Chaser | Uncharted Climber | Uncharted Sightseer | Uncharted Diner | Uncharted Dresser | — | Uncharted Player | Uncharted Gig-Goer | Uncharted Old-Soul |
| `PLAY` | Arcade Crowd-Chaser | Arcade Climber | Arcade Sightseer | Arcade Diner | Arcade Dresser | Arcade Explorer | — | Arcade Gig-Goer | Arcade Old-Soul |
| `LIVE` | Front-Row Crowd-Chaser | Front-Row Climber | Front-Row Sightseer | Front-Row Diner | Front-Row Dresser | Front-Row Explorer | Front-Row Player | — | Front-Row Old-Soul |
| `HERIT` | Old-School Crowd-Chaser | Old-School Climber | Old-School Sightseer | Old-School Diner | Old-School Dresser | Old-School Explorer | Old-School Player | Old-School Gig-Goer | — |
| `AFFIL` | Mingling Crowd-Chaser | Mingling Climber | Mingling Sightseer | Mingling Diner | Mingling Dresser | Mingling Explorer | Mingling Player | Mingling Gig-Goer | Mingling Old-Soul |

Ninety-nine pair names (`AFFIL` as second adds nine more if §3.2's exclusion is lifted: *Luxury
Mixer*, *Peak Mixer*…). Any of them takes any of the ten prefixes: *Solo Peak Diner*,
*Unplugged Arcade Climber*, *Loyal Old-School Diner*. The table is generated from §2, not
hand-maintained — change a word in §2 and every name that uses it changes with it.

---

## 6. The eighteen real sheets, renamed

Form-era data has no latency, so the prefix rule runs on hard passes only (§3.3) — and the forms
had no hard pass, so no prefixes appear. Second factors from the sheets' "also strong on" band:

```
Night Climber          →  Peak Diner            (ENRG top, FOOD within 15)
Night Climber          →  Peak Dresser
Set List               →  Front-Row Climber
Score Keeper           →  Arcade Diner
Inner Circle           →  Mingling Climber
Dressed For It (classy)→  Luxury Diner
```

Run the same over the app's first thirty and see whether people recognise themselves. V2's
warning stands and is the thing to measure: **the one-word name stayed the same on retake 15
times out of 15; the two-part V1 name, 6 of 15.** A three-part name will move more than a
one-part name. The prefix gate (hard pass / fast refusal) and the 15-point band for the second
are the two things keeping it still. `REMINDERS.md` has the check.

---

## 7. Rules for anyone editing the word-lists

1. **The name is what they want.** A refusal prefix is written as something they *are* —
   *Quiet*, *Solo*, *Liquid* — never as a lack.
2. **No word may describe everybody.** `AFFIL` stays off the second slot until data says
   otherwise.
3. **Three tokens, on a card.** If a combination overflows the reveal screen, shorten the word
   in §2, not the rule.
4. **Nothing in a name may be a friction.** *Crowd-Chaser*, never *Crowd-Tolerator*.
5. **Change §2, regenerate §5.** Never hand-edit a cell of the table.

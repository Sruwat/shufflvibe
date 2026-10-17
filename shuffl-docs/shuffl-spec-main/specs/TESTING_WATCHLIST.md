# The testing watchlist

**Everything that is a guess, a substitute, or an open question — in one place.** Written 2026-10-07.

Nothing in SHUFFL has been measured on a real person. Every number below was either reasoned from
published psychology, tuned against synthetic people, or picked because it felt right. **This
document exists so that none of them quietly becomes a fact.**

> **How to read it.** §1 is numbers to re-tune. §2 is substitutes that may not work at all. §3 is
> things that cannot be calibrated until there are users. §4 is what the MVP is actually testing.
> §5 is behaviour to watch in the first weeks. §6 is what would prove a design decision *wrong* —
> the most useful section and the one most likely to be skipped.

---

# 1. Numbers that are guesses

## 1.1 The three to distrust first

| | value | what it does | why it is suspect |
|---|---|---|---|
| **`FOCUS` pull** | **0.80** | how hard a gig pulls a room | **The most aggressive claim in the chemistry model.** The direction is well evidenced — gaze cueing is reflexive — but 0.80 is mine, and it is above `ENRG` on the argument that the pull is automatic rather than affective |
| **`SPLIT_COST`** | **35.0** | how much a newly split axis costs a joiner's score | A split is treated as worth a 35-point move. Nothing supports 35 over 25 or 45 |
| **`MID_W`** | **0.30** | what a 31–69 value advocates for its own side | New on 2026-10-07. The principle came from the user and is sound; the number is a guess |

**Watch:** if `FOCUS` is too high, rooms with one gig-goer will be read as gig rooms when they are
not, and the clock flag will fire on rooms that do not want one. If `MID_W` is too high, rooms will
read as more characterful than they are and the room line will overstate.

## 1.2 The rest of the chemistry model

| | value | note |
|---|---|---|
| `IMPACT_EXP` | 0.6 | **Latané's data suggest 0.5–0.7.** 0.6 is the middle of his range, not a measurement of ours |
| `ENRG` / `TALK` / `MOVE` / `SPONT` pulls | 0.75 / 0.60 / 0.70 / 0.55 | directions evidenced, magnitudes mine |
| discounts on the losing pole | 0.45–0.55 | `FOCUS` 0.45 is *evidenced by absence* — no mechanism un-focuses a room — but the number is mine |
| `NEUTRAL_W` | 0.25 | now applies only to an exact 50, so it matters far less than it did |
| `FOCUS` → `ENRG` **+5**, `MOVE` → `ENRG` **+5** | +5 each | **uncapped and they stack.** Two people at 88 and 72 produced a room at 96. Watch for rooms reading hotter than any member |
| the `AFFIL` pair rule | floor of 70 | Simmel on the dyad. **It is a step, not a slope** — the same two people plus one neutral drops `AFFIL` about 26 points |

## 1.3 Naming, lines and selection

| | value | note |
|---|---|---|
| `SECOND_MIN` / `STICKY` | 20 / 15 | measured on 20,000 synthetic people for *name variety*, not for whether the name is right |
| `FLAT` (room line) | 12 | below this a room has no character. Untested |
| `GAP` (you-vs-room) | 18 | below this you and the room are "pitched the same" |
| match bands | 0.80 / 0.70 | never checked against what a person would call a good match |
| **disturbance bands** | **0.047 / 0.090** | **re-cut twice on 2026-10-07.** Terciles of a synthetic distribution — and they must be **size-normalised** before use, because a joiner moves a pair twice as much as a five |
| `SHAPE_GATE` | 12 | what counts as "close enough to the drawn shape". If too wide, preferences overrule the line the user drew |
| `COUNT_PULL` | 0.50 | how much the stop count bends toward the group |
| `OPPOSED` / `AMPLITUDE` | −0.50 / 20 | when two drawings are opposed enough to offer two rooms |
| `SIZE_CEILING` | **uncapped/5/4/4/3** | Steiner — getting five people out of a bar is not linear. **A solo drawer was falling to the default of 3 until 2026-10-14 (entry 202); it is now capped by the window alone.** The group numbers remain reasoned, never measured |

## 1.4 The venue database

| | value | note |
|---|---|---|
| volume floor | 200 ratings | below this a mean says nothing. Reasonable, untested |
| mean floor | **35th percentile within type** | the rule is right (a flat 4.0 deletes clubs); the percentile is a guess |
| `SD_CEILING` | 0.85 | **on a substitute measure — see §2.1** |
| fit-out | 15 years | a judgement about when a room stops reading as current |
| `PRIOR_WEIGHT` | 6.0 | how much evidence it takes to overrule a venue type's prior |
| the five type priors | 55 numbers | written by hand. They are the fallback for every venue with thin reviews |
| the lexicon keyword weights | 1–3 per pattern | **and the lists are not symmetric.** `FOCUS` and `GAMES` have no low list at all |
| slot `FILL_AT` | 3 | one strong source, or two agreeing timed reviews |

---

# 2. Substitutes that may not work at all

## 2.1 `rating_sd` — the one that worries me most

**No API returns a rating histogram, and Places caps at five reviews.** So consistency is estimated
from **sentiment variance across those five**, with door complaints routed out first.

**This has never been validated against anything.** It is doing real work — it is one of six
admission criteria — and it could be measuring nothing at all.

**Check:** once there are a few hundred admitted venues, hand-rate thirty of them for consistency
and correlate. **If the correlation is weak, drop the criterion rather than keep a number that looks
like a measurement.**

## 2.2 Silence as absence

**If reviews do not mention food, we tag the venue "not specialised" rather than scoring it.** The
reasoning holds for a restaurant and not for a bar, which is why the rule is type-dependent.

**The failure mode is a false negative that never corrects itself:** a bar with genuinely good food
whose five reviews all discussed the drinks. **Check by hand-visiting ten venues flagged "not
specialised" on `FOOD`** and seeing how many actually have a kitchen worth it.

## 2.3 The type curve as a band fallback

An unmeasured time band falls back to the venue type's curve, which was measured at **83–84%**
agreement with a full hourly curve on synthetic data. **Real venues transform at the hours the curve
is least sure about**, so the real figure will be worse. The gold promotion exists to replace it.

---

# 3. Cannot be calibrated until there are users

**None of these are bugs. They are all waiting on the same thing.**

| | needs |
|---|---|
| `card_baseline`, `position_baseline` | running means across all users. **Until they exist, latency firmness returns nothing and the name's tie-break falls back to score alone** |
| the population mean and spread for rescaling | the same. At seven users the error is ~5 points a factor; at 300 it is ~1 |
| the personal latency scale | a user's second session onward |
| the disturbance size-normalisation divisors | real rooms of 2, 3, 4 and 5 |
| the heatmap threshold | 20 distinct users in an area |

**The capture is one of six things that must be recorded from day one, and they are now listed together in `MVP_INSTRUCTIONS.md` §3b** — the document a developer builds from, which previously mentioned none of them.

**The capture has to ship before any of it can start.** Three fields per card — total latency across
exposures, first deck position, exposure count. **It is the cheapest thing in the spec to build and
the most expensive to add later, because you cannot backfill timings for sessions that already
happened.**

---

# 4. What the MVP is actually testing

From `MVP_INSTRUCTIONS.md` §5, in the order they will answer themselves.

1. **Will people play the deck daily?** The whole product assumes a daily vibe. If they play once a
   week, the vibe is stale on most nights and the match is against yesterday's person.
2. **Does the match read as true?** A number is easy to show and hard to believe. The chemistry
   lines exist because a percentage does not persuade.
3. **Does drawing a skeleton beat a list of filters?** The skeleton survived the MVP cut because
   *the shape of the night* is a better question than *what kind of bar*. **If users do not get it,
   that is worth knowing before bands are built.**
4. **Will somebody at a bar give ninety seconds for ₹865?** **— not until December.** The Gold
   Campaign is a post-funding item, so this question cannot be asked in the first release and the
   bands stay on the type curve until it is. **This is the one with the clearest pass
   mark** — 578 slots, and we will know inside a month whether they are filling. **If they are not,
   the band problem has no cheap solution** and the answer is partnerships, sooner and slower.

---

# 5. Behaviour to watch in the first weeks

**The room reads hotter than anyone in it.** Two uncapped +5s stack on `ENRG`. Watch for room lines
saying *going hard tonight* about rooms nobody would describe that way.

**Everyone gets the same name.** V5 measured a 41.8% single-name rate on synthetic people. If real
people cluster, most of a city is *Night Climber* and the name stops meaning anything.

**Presets cannibalise drawing.** If almost nobody draws, the skeleton signal gets coarse, the merge
becomes trivial and the two-rooms offer never fires. **Not necessarily bad — but it changes what the
app is**, and it should be a decision rather than a drift.

**The room list is empty.** The join gates are off for the first release, but if ranking alone still
leaves people with nothing to look at, the problem is room supply rather than filtering - and no
amount of ranking fixes it. **Watch the median rooms-shown per user before anything else.**

**The stop list is too long or too short.** 5–10 is a guess about how many options a person wants
before it becomes work.

**Gold is noticed before it is wanted.** The design says gold is something you see while planning a
night, never a reason to plan one. **Watch for people building plans around gold venues** — that is
the failure the whole mechanism is guarded against.

**Verification accuses honest people.** It is wrong about **1.4%** of the time by design, and with
one capture per slot it is the only check on the data. **Watch the retry rate and read the support
messages.**

**The group chat has nothing to say.** A new group has no history, so the venue line is absent and
only chemistry shows. If chemistry alone is not enough to make the panel worth opening, the feature
is thinner than it looks.

---

# 6. What would prove each decision wrong

**The most useful section. Each of these is a design choice that could be mistaken, with the
observation that would show it.**

| the decision | what would falsify it |
|---|---|
| **The vibe matches people and never picks venues** | users consistently say the venues do not suit them *while* saying the people do. That would mean identity does carry venue information we are refusing to use |
| **The skeleton is exclusive; preferences only order** | people routinely pick the 6th-ranked venue in a stop list. That means the shape ranking is not capturing what they want |
| **The app offers rather than generates** | people pick the top option every time. If so they wanted a plan, and the list is ceremony |
| **A preference is live only if someone is 60+ and a venue can serve it** | groups report a preference was ignored that mattered to one person a lot |
| **Silence means absence (§2.2)** | the "not specialised" flag is wrong more than about one time in ten |
| **Within-type rating floors** | admitted clubs are visibly worse than admitted restaurants, or vice versa |
| **`match` and `disturbance` are different sorts** | the two lists rank the same rooms in practice. Measured at **34% overlap** on synthetic rooms — if real users see 80%, one of them is redundant |
| **A split is a feature, not a problem** | split rooms report worse nights than the model's other flags predict |
| **One capture per slot** | the data from single captures is visibly noisier than the type curve it replaces |
| **The daily name is worth having** | people cannot tell you what their name means an hour after seeing it |

---

# 7. Known gaps that block building

| | |
|---|---|
| **`CARD_SET_V11`** | **`FOCUS` and `SPONT` have no card images specified.** Two of six factors. The deck cannot run |
| the swipe game screens | held for the card images |
| the capture's factor cards | screen 22's swipe copy is placeholder for the same reason |
| settings and onboarding | undrawn |
| the preset library | which presets exist, their shapes, their time windows |
| the Go-here card's one-stop state | one line different from screen 18 |
| `IMAGE_PROMPTS.md` | cited by `ASSESSMENT_ENGINE.md` and does not exist |
| *The Desert Run* | drawn as a drive. If it meant **dessert**, the glyphs and its place in the library change |

---

**Last thing.** Every figure in the simulations came from **synthetic people drawn from a normal
distribution**. Real users are not normal, they cluster, and they will break at least one thing in
§1 in a way no amount of re-running fixes. **The first fifty real sessions are worth more than all
twenty thousand synthetic ones.**

# Collective V1 — group psychology and "collective consciousness", against the vibe factors

**Status: research + one proposal, 2026-09-23. Nothing here is adopted.** The proposal at §4 (an
eighth vibe factor, `FOCUS`) needs the user's decision, and §5 is the test that argues against
adopting it on its own. `CHEMISTRY_V3.md` holds the rules that are in force.

> **2026-10-14. Two things here are settled and the page does not say so.** **§4's proposal was adopted** — `FOCUS` is a factor, weight 14 (`FACTORS_V6.md`). And the rules in force are **`CHEMISTRY_V4.md`**, not V3. **§6.2's clock-anchored stops are out of the MVP** (entry 205): `FOCUS` selects venues that reliably have something on, and never claims a start time.

---

# 0. What "collective consciousness" turns out to be

Durkheim's *conscience collective* is about shared moral belief across a society, not a group
mind at a bar — it is the wrong tool for a night out. The thing he named that **is** the right
tool is **collective effervescence**: what happens when assembled people focus on the same thing
and feel the same way at once, and the situation stops feeling ordinary.

That concept now has forty years of measurement behind it, and it has been operationalised. Four
findings matter for this engine, and they are stronger than anything in `CHEMISTRY_V3.md`:

| # | Finding | Source | Evidence |
|---|---|---|---|
| 1 | **Interaction rituals need four ingredients**: bodily co-presence, a barrier to outsiders, **mutual focus of attention**, and a shared mood. Where all four are present the group gets solidarity and *emotional energy*; where they are not, the ritual fails and drains it. | Collins, *Interaction Ritual Chains* (2004) | the central theory of the field |
| 2 | **Shared attention amplifies whatever is attended to** — stronger memory, deeper emotion, firmer motivation, purely from attending *at the same time as* others. It works without a word exchanged: co-tasting the same chocolate made good chocolate better and bitter chocolate worse. | Shteynberg (2015); Boothby, Clark & Bargh (2014) | experimental, replicated |
| 3 | **Synchrony and exertion bond people independently of each other.** Dancing in time raised pain threshold (an endorphin proxy) and in-group closeness; so did effort; the two effects did not depend on one another. | Tarr, Launay, Cohen & Dunbar (2015); Tarr et al. (2016), *Silent disco* | experimental, 2×2 |
| 4 | **Collective effervescence is two things at once** — feeling connected to those present, *and* the situation feeling raised out of the ordinary — and it is common, not rare: it is measurable at concerts, matches and ordinary gatherings, and it predicts wellbeing, self-esteem and "vital energy". | Gabriel et al. (2017, 2020); Páez et al. (2015); meta-analysis, *Frontiers in Psychology* (2022) | large samples, a validated scale |

And one that corrects a thing people assume about crowds:

| 5 | **Anonymity does not make people wild; it makes them conform to the local norm.** Sixty studies found no support for a "deindividuated state": anonymity shifts the self from personal to social, so people follow the *situation's* norms harder. | Postmes & Spears (1998) meta-analysis; SIDE (Reicher, Spears & Postmes) | meta-analytic |

---

# 1. What this says about the seven factors we already have

**Confirmed, and now better grounded than before:**

- **`ENRG`** — shared mood is one of Collins' four ingredients, and contagion (Barsade) is how it
  forms. Nothing changes.
- **`AFFIL`** — this is Collins' **barrier to outsiders**, which is a *requirement* of a working
  ritual, not a preference. A room that cannot say who is inside it does not produce
  effervescence at all. `AFFIL`-high ("our own table") and `AFFIL`-low ("out to meet the room")
  are two different boundaries, not two amounts of one thing — which is why §6 of
  `CHEMISTRY_V3.md` is right that it splits rather than averages.
- **`TALK`** — mutual focus *on each other*. The narrow, conversational form of ingredient three.

**Upgraded — the finding is stronger than the rule we built on it:**

- **`MOVE`** is currently justified by *arousal* (synchrony raises energy, +5 `ENRG`). Finding 3
  says it does something larger: moving in time with people **bonds** them, by a mechanism
  (endorphin release) that has nothing to do with how lively the room is, and **exertion alone
  does it too**. That makes a floor late in the night a *social* instrument, and it matters most
  for exactly the rooms that need bonding — strangers, and first-time public rooms.

**Unchanged:**

- **`CROWD`** — finding 5 says a full room is not a disinhibitor, it is a norm amplifier. That is
  an argument for the low `pull` (0.25) that §5 already gives it, and against ever treating
  "packed" as a proxy for "wild".
- **`ROAM`** — nothing in this literature speaks to venue-hopping. It remains the weakest peg.
- **`GAMES`** — see §4: the research suggests games are a *weak* ritual for a group of four or
  more, which supports the user's Delhi correction from a second direction.

---

# 2. The gap: we model three of the four ingredients

| Collins' ingredient | In the model |
|---|---|
| bodily co-presence | given — they are out together |
| a barrier to outsiders | **`AFFIL`**, plus public / private rooms |
| **mutual focus of attention** | **nothing** |
| a shared mood | **`ENRG`**, and `TALK` |

**The one ingredient Collins says does the work is the one the engine cannot express.** The
closest things it has are `GAMES`, which is participatory and *splits* a group (two people at the
pool table, three at the bar — Collins would call that a weak ritual, and Dunbar's conversation
cap of four says the same), and `LIVE`, which is a **preference**: it picks a venue that happens
to have a band, and by construction it "never alters the venue type". Neither can say *the
group wants to be pointed at one thing tonight*.

---

# 3. Why that gap shows up in real nights

Three rooms the current factor set reads identically and a Delhi person would not:

1. Four people who want **a gig** — one stage, everyone facing it, nobody talking through it.
2. Four people who want **the match on** — one screen, a full room, shouting at the same moment,
   talking between overs.
3. Four people who want **a loud club** — no shared object at all; each person is in their own
   night, next to the others.

All three read as `ENRG` high, `TALK` low, `CROWD` high. The model sends all three to the same
places. But (1) is anchored to a clock, (2) needs a room oriented at a screen and would be ruined
by a dance floor, and (3) needs neither.

---

# 4. The proposal — `FOCUS`, an eighth vibe factor

> **`FOCUS` — is there one thing we are all pointed at tonight, or are we the thing?**
>
> | pole | the want | what it asks of a stop |
> |---|---|---|
> | **high** | a gig, a set, a match, a comedy night, a quiz, a screening — one object of attention, at the same time, together | a venue **oriented** at something (a stage, a screen, a table everyone can see) and usually a **clock**: the set is at ten |
> | **low** | no main event; the people are the event | a room with no focal point competing for attention |
> | middle | don't mind either way | — |

**What makes it different from what we have:**

| | |
|---|---|
| vs **`LIVE`** (preference) | `LIVE` says *I like live music*; `FOCUS` says *I want us all watching the same thing*, which may be a match, a quiz or a screening. `LIVE` picks a venue of a type already fixed; `FOCUS` would fix the type — and the hour. |
| vs **`GAMES`** | games are **participatory and splitting** — a pool table makes players and spectators. A focal event is **unifying** — one object, everyone at once. Opposite effects on a group of five. |
| vs **`TALK`** | `TALK` is mutual attention **to each other**; `FOCUS` is mutual attention **to a third thing**. A quiz night is high on both. A club is low on both. They are not one axis. |
| vs **`ENRG`** | a chamber gig is `FOCUS` 90, `ENRG` 30. A loud club is `ENRG` 90, `FOCUS` 30 (nobody is attending to the same thing — see §3). |

**What it would fix in the shape**, in the language of the other factors: *whether a stop is built
around a scheduled event, and therefore whether the night has a fixed hour in it.*

**Weight if adopted:** 12, taken from `ENRG` 18 → 16 and `AFFIL` 16 → 15, with everything else
unchanged. It is a real axis but not a leading one on most nights.

---

# 5. The test that argues against adopting it on its own

`FOCUS` scored on the venue types and regressed on the six existing stop axes
(`focus_test.py`), which asks: *can the axes we have already say this?*

| | R² |
|---|---|
| **`FOCUS` on the existing 11 venue types** | **0.91** — nearly redundant |
| **`FOCUS` once a twelfth type exists (a screening room / match bar)** | **0.66** |
| for comparison: `ENRG` predicted by the other five | 0.96 |
| `TALK` | 0.90 |
| `CROWD` | 0.86 |
| `AFFIL` | 0.83 |
| `GAMES` | 0.60 |
| `MOVE` | 0.59 |

Read honestly: **on today's venue vocabulary `FOCUS` is as redundant as `TALK` is** — it would
mostly re-express "high energy, low talk". It becomes independent information only when the venue
set contains a focal venue that is **not** loud, **not** a floor and **not** games. That venue
type — a sports bar, a screening room, a comedy room — is a real gap in the eleven anyway; there
is no way to ask this engine for the match.

**Caveat on the test itself.** It regresses twelve hand-authored rows, so it measures whether *my*
numbers are collinear, not whether real people vary independently on this axis. The real test is a
card in the deck and a few hundred sheets.

**So the order matters**, and it is the opposite of the obvious one:

1. **Add the venue type first** (§6) — it is justified on its own, with or without a new factor.
2. **Add clock-anchored stops** — also justified on its own: the engine cannot currently say
   "this stop starts at 10", which it needs for any act, match or show.
3. **Then** put a `FOCUS` card in the deck, and see whether people separate from `ENRG` and
   `TALK` on it. If they do not, drop it and lose nothing.

---

# 6. What is needed either way — no new factor required

### 6.1 A twelfth venue type

| Type | `ENRG` | `AFFIL` | `CROWD` | `TALK` | `MOVE` | `GAMES` | |
|---|---|---|---|---|---|---|---|
| **screening room / match bar** | 65 | 55 | 75 | 50 | 20 | 30 | a match on the big screen, a comedy room, a screening — everyone facing one thing, and you can still talk between |

A sports bar is one of the most common ways Delhi goes out and the engine cannot currently
produce one.

### 6.2 Clock-anchored stops

Every stop today has a duration and no start time. An act, a match or a show has an hour. The
plan needs `starts_at` on a stop, and the availability check needs to respect it. This is also
the fix for the gap found on 2026-09-22 — `start_time` is in the plan request but no screen sets
it.

### 6.3 The arc should target the **peak and the end**, not a smooth climb

Kahneman's peak-end rule with duration neglect (Redelmeier & Kahneman 1996; Kahneman et al. 1993;
meta-analysed 2022): what people remember of an episode is **the most intense moment and the last
moment**, and **how long it lasted barely enters**. The engine currently spreads energy evenly up
a climb and treats duration as though it were value.

**The rule that follows:** score a plan on `(peak + end) / 2` rather than on the mean of its
stops, and require the **highest-energy stop to be last or second-to-last**. A night that peaks
at stop two of three and trails off is worse remembered than the same night reordered, even
though every stop is identical. This is the single best-evidenced change available to the
planner and it needs no new factor.

### 6.4 `MOVE` as a bonding instrument, not only an arousal one

From finding 3: give a `MOVE`-high closing stop extra weight **in rooms of strangers and
first-time rooms**, where bonding is the thing the room actually needs. Proposed: in a strangers'
room the `floor-at-the-end` reading's weight rises from 12 to 18. Synchrony and exertion each do
it, so a lawn, a walk or a street counts, not only a dance floor.

### 6.5 Shared attention amplifies **both** directions — so a focal stop is a risk

Boothby: bitter chocolate tasted together was worse than bitter chocolate tasted alone. A stop the
whole room is pointed at is therefore **high variance** — if the venue disappoints, it
disappoints everyone at once and the night has no other thing to be about. **Rule:** a focal stop
(or any `LIVE`-driven stop) should require a higher venue confidence (§3.5) than an ordinary one.
Proposed: confidence tier one only.

### 6.6 Dunbar's cap, with something to do

`CHEMISTRY_V3.md` §8 lists *group of 5+ → venues with room to split* and it has never been
implemented. With the above it gains a reason: a group of five or more with **no** focal point
**will** split into two conversations, which is fine when `AFFIL` is high (our table, two
conversations) and a failure when the room came to be one unit. Implement it as: **5+ and no
focal reading → prefer types that seat a group in more than one grouping**; 5+ **with** a focal
reading → the focal point holds them, and the cap does not apply.

---

# 7. Candidates considered and rejected

| Candidate | Why not |
|---|---|
| **A "collective effervescence" factor** | It is an *outcome*, not a want. You cannot ask someone to swipe on whether tonight will be transcendent. It belongs where `Caught the Spark` already is — in the chips — and Gabriel's two components (connection + transcendence) map onto `AFFIL`-high plus a late `ENRG` peak, which the model can already read. |
| **Planned vs spontaneous ("see where it goes")** | A real dimension of a Delhi night, but it is a property of *the plan*, not of the person's vibe — and the app already has a form of it in Open Night. Better as a room setting than a card. |
| **Risk / going big** | Partly `ENRG`, partly intoxication. Asking it directly invites bravado on a card and creates a duty-of-care problem for no modelling gain. |
| **Talking to strangers vs to your own** | That is `TALK` × `AFFIL`, and the interaction already produces it. |
| **Status / being seen** | `POL` and `SCEN` as preferences, plus `CROWD`. No separate axis. |

---

# 8. What is evidenced and what is mine

| Claim | Status |
|---|---|
| mutual focus is a necessary ingredient of a working group ritual | **evidenced** — Collins, the field's central theory |
| shared attention amplifies experience in both directions | **evidenced** — Shteynberg; Boothby, Clark & Bargh |
| synchrony and exertion bond independently | **evidenced** — Tarr, Launay, Cohen & Dunbar |
| peak and end dominate remembered experience; duration barely counts | **evidenced** — Kahneman et al.; meta-analysed 2022 |
| anonymity amplifies local norms rather than removing restraint | **evidenced** — Postmes & Spears meta-analysis |
| that `FOCUS` should be a factor | **mine, and the test in §5 argues against it until the venue set changes** |
| the `FOCUS` numbers per venue type, the weight 12, the strangers' weight 18, the tier-one rule | **mine** — every magnitude is judgement |

---

# 9. The decision

**Recommended:** adopt §6.1, §6.2 and §6.3 now — the venue type, clock-anchored stops, and the
peak-end arc. They are the best-evidenced changes in this document and none of them needs a new
factor or a new card. Hold `FOCUS` until the venue set contains focal venues, then test it as a
card rather than assuming it.

**Not recommended:** adding `FOCUS` today. On today's eleven types it is 91% predictable from the
six axes we have, and an eighth card costs every user a swipe every day.

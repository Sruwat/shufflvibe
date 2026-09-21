# SHUFFL — engine specs, front-end flows, and the reasoning

**Assembled:** 2026-09-15 · **Refreshed:** 2026-09-17
**For:** the developer building the vibe assessment, the outing-plan engine, the front end and the backend
**Start with:** `specs/BACKEND_BRIEF_ASSESSMENT.md`. This file is the map; that one is the brief.

> **2026-09-17 — the factor set is split.** Read `specs/FACTORS_V5.md` first, then
> `specs/ASSESSMENT_ENGINE.md` Part 0a, then `specs/OUTING_PLAN_ENGINE.md` §14. Seven vibe factors
> are the daily deck and the shape of the night; six preferences are asked once and pick the exact
> venue. The older sections of every spec are the machinery and the history; the three places
> above say how each part now reads.

## Layout

| Folder | What is in it |
|---|---|
| `specs/` | the backend specs: assessment engine, outing plan engine, learning layer, the brief, factors, names, cards, blend styles, area scores |
| `frontend/` | every screen (`VIEW_FLOW.md` and the same as `.docx`), and the swipe-game change record |
| `decisions/` | `DECISIONS.md` — 111 dated entries, why every rule is what it is; `REMINDERS.md` — open work |
| `simulations/` | the Python models the rules were tested on; `splitsim.py` is the current one |
| `superseded/` | earlier versions, kept for the reasoning; never build from these |

Nothing here is code to ship. The simulations are the rules run on imaginary rooms; the specs
carry pseudocode where prose could be read two ways. Where a number is a guess it says so.

## Reading order

| # | File | Read it for | Time |
|---|---|---|---|
| 1 | `specs/BACKEND_BRIEF_ASSESSMENT.md` | what to build, what's settled, what's provisional, what to instrument | 15 min |
| 2 | `specs/ASSESSMENT_ENGINE.md` | the full method — cards to profile — with pseudocode | 45 min |
| 3 | `frontend/Front End Final V3.docx` | every screen in the app | 30 min |
| 4 | `specs/FACTORS_V5.md` | seven vibe factors, six preferences, venue types, the shape library | 15 min |
| 5 | `specs/VIBE_NAMES_V4.md` | the name from the vibe factors; badges from preferences | 5 min |
| 6 | `specs/OUTING_PLAN_ENGINE.md` | what the profile feeds — matching, bend, plans | 60 min |
| 7 | `specs/BLEND_STYLE_DATABASE_V3.md` | twenty group shapes on the seven vibe axes | 10 min |
| 8 | `specs/CARD_SET_V10.md` | both decks — what each card has to convey | 10 min |
| 9 | `specs/CARD_READABILITY.md` | how the target reader reads a card — five rules | 5 min |
| 10 | `specs/PREFERENCE_ENGINE_V2.md` | the learning layer, later sessions — **not v1** | 20 min |
| 11 | `decisions/DECISIONS.md` | why every rule is what it is, dated — dip in, don't read through | as needed |

The other four — `superseded/FRONTEND_SWIPE_GAME_V3.md`, `frontend/VIEW_FLOW.md`, `specs/CARD_SET_MOOD_V1.md`,
`superseded/PREFERENCE_ENGINE.md` (V1, superseded), `superseded/VIBE_NAMES_V2.md` (superseded), `decisions/REMINDERS.md` — are
supporting files, described below.

---

## The files, one by one

### The brief

**`specs/BACKEND_BRIEF_ASSESSMENT.md`** — Two pages on top of the spec. The flow walked screen by
screen with what the user sees and what gets recorded at each step; the settled rules; the
provisional constants in a table with what data replaces each; what to instrument from the first
user; the traps; what's out of scope. If you read one file, this is it. **Current.**

### The specs

**`specs/ASSESSMENT_ENGINE.md`** — One session of cards → a profile. §2 the adaptive four-way deck
and the swipe values; §3 latency capture, Next, Back, the timeout, the pause; §4–5 scoring and
reading the answers, including the `POL` split; §6 firmness from score and from latency, and the
validation gate; §7 the top factor and the name; §8 follow-ups; §9 rescaling; §10 what to store;
§11 traps; §12 what's not established. **Current. Every constant marked as a guess is one.**

**`specs/OUTING_PLAN_ENGINE.md`** — What consumes the profile. Venue intelligence, arrival risk, plan
generation. §5.3 is the part that reads the assessment output: firmness, bend, the asymmetric
penalty. §13 is the 2026-09-14/15 addendum: the bend floor at the extremes, `FLOOR` as code, what
to do when it fails, and the three latency levels for bend. **Current throughout on the factor set; §6's one-stop-per-member rule is marked superseded by §13.4,
and §5.3's sequencing loop now calls §13.4's check.**

**`specs/PREFERENCE_ENGINE_V2.md`** — How a profile is refined over weeks on the current factor set:
a per-factor baseline updated by how *sure* each swipe was (Kalman gain from firmness), three
factor states (not yet known / settled / unanswerable), settled factors leaving the deck, a
hidden re-check card, a session-quality gate. This is how a 20-card deck becomes a 4-card one.
**Not v1** — held behind the latency validation. `superseded/PREFERENCE_ENGINE.md` is the superseded V1,
kept for the argument.

**`superseded/BLEND_STYLE_DATABASE_V2.md`** — The 24 named room styles with their vectors, and the
abstention rule that builds a room's vector from its members. Chemistry sits next to the style as
a chip — `specs/OUTING_PLAN_ENGINE.md` §13.6. **Current.**

### The reference tables

**`specs/AREA_SCORES_V1.md`** — 35 Delhi NCR neighbourhoods scored on `CROWD` `ENRG` `POL` `SCEN` in three
time bands, for the area fallback in `specs/OUTING_PLAN_ENGINE.md` §13.7; how to tag a venue; how the
numbers get replaced from venue data. **First pass, authored — hand-check before shipping.**

**`superseded/FACTORS_AND_VIBES_V4.md`** — The ten factors, their weights, which are passive and which
participatory, and the 42 library vibes with vectors. **Current. `PLAY` and `LIVE` were corrected
to participatory on 2026-09-11.**

**`superseded/VIBE_NAMES_V3.md`** — The name: `[refusal prefix] [top word] [second word]` — *Luxury Diner*,
*Quiet Luxury Diner*. Three word-lists of ten, the generated pair table, the rules for the second
word and the prefix, and the ten single names for when nothing else is close. Never invent a
word. **Current.** `superseded/VIBE_NAMES_V2.md` is the superseded one-word scheme, kept because its
stability numbers are the thing to beat.

### The cards

**`superseded/CARD_SET_V9_IMAGE.md`** — The wording each card has to convey, `A` and `B` per factor, with
the merged `S` set marked as retired in the app. Images are built from these; the wording is not
caption text. **Current.**

**`specs/CARD_READABILITY.md`** — Five rules about how the target reader actually processes a card,
each recovered from a card that failed. Read before touching any card or image. **Current.**

**`specs/CARD_SET_MOOD_V1.md`** — Eight mood cards, sent only when five or more factors come out
neutral. Referenced by `specs/ASSESSMENT_ENGINE.md` §8.4. Has never fired on anyone. **Reference only.**

### The front end

**`frontend/Front End Final V3.docx`** — Every screen in the app. Updated 2026-09-15 so the Swipe Game
Flow matches the spec; everything else is as it was in V2. A note at the top says what changed.
**Current.**

**`superseded/FRONTEND_SWIPE_GAME_V3.md`** — The rewritten Swipe Game Flow section on its own, plus the
six one-line edits made elsewhere in the document, shown with strike-throughs. Use it to see
exactly what changed between V2 and V3, or to apply the same edits to another copy. **Current.**

**`frontend/VIEW_FLOW.md`** — Markdown mirror of the .docx, for anyone who'd rather grep than open Word.
Same content. **Current.**

### The reasoning

**`decisions/DECISIONS.md`** — 111 dated entries.

**`specs/VIBE_AND_PREFERENCE_V1.md`** — An exploration, not a spec: the proposal to split the ten factors into five
preferences (venue choice, set once) and five vibe factors (the shape of the night, daily), with two new
vibe factors. Read it to know where the model is likely going; build from the specs as they stand.

**`decisions/REMINDERS.md`** — Open work, not open decisions: what waits, on what, and what unblocks it. Every rule in every spec has one, saying what was decided,
why, what was tried and rejected, and what isn't established. When a rule looks odd, search this
file by the date the spec gives. **Not a read-through document.** Later entries supersede earlier
ones where they conflict, and say so.

---

## Where to find things

| You want | File | Section |
|---|---|---|
| The four swipes and their scores | `ASSESSMENT_ENGINE` | §2.1 |
| Why the deck is adaptive, and the second-card rule | `ASSESSMENT_ENGINE` | §2.2 |
| `POL` always gets two cards | `ASSESSMENT_ENGINE` | §2.3 |
| Where the second card is inserted | `ASSESSMENT_ENGINE` | §2.4 |
| Progress bar, no number | `ASSESSMENT_ENGINE` | §2.6 |
| Latency: when the clock starts and stops | `ASSESSMENT_ENGINE` | §3.2 |
| Next and where a deferred card goes | `ASSESSMENT_ENGINE` | §3.3 |
| Timeout and the "Are you there?" pause | `ASSESSMENT_ENGINE` | §3.4 |
| Firmness from score × latency × Next × Back | `ASSESSMENT_ENGINE` | §3.5 |
| The two kinds of person who press Next a lot | `ASSESSMENT_ENGINE` | §3.6 |
| What the user is told before the cards | `ASSESSMENT_ENGINE` | §3.7 |
| Broken pairs, neutral vs soft, refusal | `ASSESSMENT_ENGINE` | §5 |
| The `POL` sense tag (classy / current / both) | `ASSESSMENT_ENGINE` | §5.4 · `OUTING_PLAN_ENGINE` §13.4b |
| `NOV` as a familiar-vs-new filter | `OUTING_PLAN_ENGINE` | §13.4b |
| Strong match / other rooms / hidden | `VIEW_FLOW` | Join flows |
| Refused = hard pass, or not-for-me twice | `ASSESSMENT_ENGINE` | §5.5 |
| Latency-firmness, and when it's allowed to feed things | `ASSESSMENT_ENGINE` | §6.2–6.3 |
| Top factor: score first, latency for ties, forced choice for dead heats | `ASSESSMENT_ENGINE` | §7.1 |
| The name — prefix, top word, second word | `VIBE_NAMES_V3` · `ASSESSMENT_ENGINE` §7.2 | |
| What the plan card says when a constraint was eased | `OUTING_PLAN_ENGINE` | §13.1 |
| Follow-ups, and the identity rule | `ASSESSMENT_ENGINE` | §8 |
| Rescaling and the running population centre | `ASSESSMENT_ENGINE` | §9 |
| The stored record | `ASSESSMENT_ENGINE` | §10 |
| How a room's vector is built (abstention) | `BLEND_STYLE_DATABASE_V2` | §2 |
| Bend — how far a venue can miss someone | `OUTING_PLAN_ENGINE` | §5.3 |
| Bend floor at the extremes | `OUTING_PLAN_ENGINE` | §13.3 |
| `FLOOR` — is anyone stranded — as code | `OUTING_PLAN_ENGINE` | §13.4 |
| What to do when `FLOOR` fails | `OUTING_PLAN_ENGINE` | §13.1 |
| What bend is for, by context — stretch vs gate | `OUTING_PLAN_ENGINE` | §13.4c head, §13.4d |
| Debt across stops — weak #2, area-carried wants, the dedicated stop | `OUTING_PLAN_ENGINE` | §13.4c |
| Location as a fallback — the area carrying `CROWD` `ENRG` `POL` `SCEN` when the venue can't | `OUTING_PLAN_ENGINE` | §13.7 |
| The area scores themselves, and how to tag a venue | `AREA_SCORES_V1` | |
| Room chemistry — debt, payback, the seven states, the match, Open Night | `OUTING_PLAN_ENGINE` | §13.6 |
| Overall firmness, and how it scales debt | `ASSESSMENT_ENGINE` §6.5 · `OUTING_PLAN_ENGINE` §13.8 | |
| Friend mode — relaxed bends, the combination search, no debt | `OUTING_PLAN_ENGINE` | §13.9 |
| Every variable added on 2026-09-17, one table | `OUTING_PLAN_ENGINE` | §13.10 |
| Behaviour as evidence for the learning layer | `PREFERENCE_ENGINE_V2` | §8b |
| Every screen | `frontend/Front End Final V3.docx` | |
| What changed in the front end and why | `FRONTEND_SWIPE_GAME_V3` | |
| What the front end must never do | `FRONTEND_SWIPE_GAME_V3` | last section |
| Why any of the above | `DECISIONS` | by date |

---

## Status of what's in here

**Settled, tested on real people, build as written:** the ten factors; the four-way swipe values;
the reading rules in §5 (broken pairs, neutral vs soft, refusal); score-firmness; the top factor
by score with a forced choice for ties; the name from the top factor; the follow-up chain and the
identity rule; rescaling at one-third; the room vector by abstention; `PLAY` and `LIVE` as
participatory.

**Settled, reasoned, not yet tested — build as written and instrument:** the adaptive deck;
Next and Back; the 12 s timeout and the pause; latency capture; latency as the tie-break;
the three-part name; the `POL` sense; room chemistry and the join match (§13.6); the bend floor; `FLOOR` and its relaxation rule.

**Constants — all set, build as written, adjust from data:** listed in the brief's table. The first
30 app users are where they get tuned, not where they get decided.

**Held behind validation — don't build yet:** latency feeding group weight, bend or abstention;
the learning-layer rules in `PREFERENCE_ENGINE_V2`; the strong/soft names; the refusal prefix on latency rather than hard pass; bend levels 2 and 3.

## What's not in the package, and why

- **Image prompts and image generation guides.** They exist but are written for a 28-card deck
  on an older factor set. Images are placeholders for now — the brief says so — and the prompts
  will be redone against `superseded/CARD_SET_V9_IMAGE.md` when it's time.
- **Older card sets, vibe databases and blend databases.** Superseded. `decisions/DECISIONS.md` records what
  changed and when if it ever matters.
- **The Google Forms test script.** Retired 2026-09-16 — testing is in the app from here. Its
  scale (0–5) and three-branch structure never matched the app; nothing in it is a reference.

## One request

The specs are specific because the testing was. Where they say a number is a guess, it is one.
If something doesn't fit how the app is being built, say so — most rules have a reason in
`decisions/DECISIONS.md`, some of those reasons are forms-specific, and a few were wrong the first time and
fixed. This is the fourth generation of the swipe game in a week. It will not be the last.

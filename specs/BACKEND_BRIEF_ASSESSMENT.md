# Brief — Vibe Assessment, front end and backend

> **2026-09-17 — the factor set is split.** Read `FACTORS_V5.md`, then `ASSESSMENT_ENGINE.md` Part
> 0a, then `OUTING_PLAN_ENGINE.md` §14, before the rest of this brief. In one line: seven *vibe
> factors* are the daily deck and the shape of the night; six *preferences* are asked once, live in
> the profile, and pick the exact venue of the type the shape fixed. A low preference is never an
> aversion. Wherever this brief says "factor", read "vibe factor"; the preference deck is a second
> deck at onboarding with the same screen and its own four labels.
>
> **2026-09-18 — the designed night (§14.3 v4).** Every member's top vibe factor is at every stop;
> a top moves only when somebody is firm on its opposite pole *and* its owner has a strong #2 to
> stand in. Maximin over venue types. No debt, no payback, **no dedicated stops**. Chemistry is how
> the design went. The plan-engine notes in this brief about debt, payback, reserved stops and
> the eased-constraint ⓘ are the record, not the build.

**For:** the developer building both
**From:** Ishaan
**Date:** 2026-09-15
**Read next:** `ASSESSMENT_ENGINE.md` (the spec this brief sits on top of)

---

## What you're building

The part of SHUFFL that turns one session of image cards — ten to twenty, decided by the answers
as they go — into a user's profile for the day: ten factor scores, how firmly each is held, a vibe name, and a set of flags. Everything
downstream — matching people into rooms, blending a room's vibe, generating an outing plan — reads
that profile. Nothing downstream reads the name; it's display only.

You're building both halves: the screens the user moves through, and the engine that scores what
they did on them. This brief walks the flow once, screen by screen, saying what the user sees and
what the backend records at each step, so the two can be built in lockstep. The scoring method
itself is in `ASSESSMENT_ENGINE.md`.

## Read, in this order

| Doc | What it gives you |
|---|---|
| `ASSESSMENT_ENGINE.md` | the method, with pseudocode for every step — **this is the spec** |
| `FACTORS_AND_VIBES_V4.md` | the ten factors, their weights, and the 42 reference vibes |
| `VIBE_NAMES_V2.md` | the ten names and the rules for the label |
| `CARD_SET_V9_IMAGE.md` | what each card has to convey |
| `CARD_READABILITY.md` | how the target reader actually reads a card — five rules, each from a card that failed |
| `OUTING_PLAN_ENGINE.md` | what consumes the profile — §5.3 for how firmness and bend are used |
| `VIEW_FLOW.md` | the surrounding product flow. **Its card counts (18, 28) are stale — the deck is 14** |
| `PREFERENCE_ENGINE.md` | how the profile is refined over later sessions — **not v1** |
| `DECISIONS.md` | why every rule is what it is, dated. Search by date if a rule looks odd |

## Images are placeholders

**The card images are not decided.** Build against placeholders — any image, a coloured rectangle
with the factor code on it is fine. Two things matter regardless of what the image is:

- Every card has a stable id, a factor, and a side (`A`, `B` or `S`).
- The wording the card is meant to convey is stored *with* each answer, not looked up by id later.
  Cards get rewritten; an answer that only points at an id will be reported under whatever that
  card says now. This corrupted a week of analysis on the test forms.

When final images arrive they slot in against the same ids. Nothing in the scoring changes.

**When the images are made**, one constraint: every factor's `A` card has to carry the factor
cleanly on its own, because for a decisive person it is the only card of that factor they see.

---

## The flow, screen by screen

Each step: what the user sees → what gets recorded → constraints.

### 1. Entry

**Returning user:** *"Your most recent vibe is: [name]. Do you feel the same right now?"* — swipe
right to reuse yesterday's vibe as today's (no game), swipe left to play.
**First-time user:** straight to the game.

*Records:* whether they reused or played.

### 2. Instruction screen

One sentence. Copy is still to be settled; this respects the constraint:

> Swipe how you feel about tonight. Gut call — first reaction wins.
> Not sure? Hit Next and it comes back later.

*Constraint:* **no mention of time, no mention of speed.** The drafted line *"the cards disappear
after a few moments so try and answer as fast as you can"* would undo the latency measurement —
once read, every card is answered under instruction to hurry. An engaged user never sees a card
disappear, so they never need warning.

### 3. The card

An image, with a **progress bar above it** and two buttons — **Next** and **Back** — below. The
person swipes the card one of four ways:

| swipe | label | colour |
|---|---|---|
| up | **LOVE** | gold |
| right | **UP FOR IT** | green |
| left | **NOT FOR ME** | grey |
| down | **HARD PASS** | red |

Words in colour. **No emoji.** The earlier "hate" with a vomit emoji went almost entirely unused
and is gone.

*The deck is adaptive.* A **love** or **hard pass** finishes that factor. An **up for it** or
**not for me** adds a second card for the same factor, from a different angle, at least three
cards later — or at the end of the deck if fewer than three remain, which can make it the very
next card when the first was the last (§2.4). So the deck is 10 cards for someone decisive, 20 for someone mild on everything,
around 14 for most. `POL` always gets both cards. §2.

*The progress bar shows no number* — the length isn't known until the last swipe. It reflects
factors resolved out of ten and never moves backwards.

*Records per exposure:* `latency_ms`, `position_in_deck`, `ended_by`. Per card: every exposure,
the final swipe, the swipe history, `next_count`, `back_count`, `changed`. Schema: §3.2.

*Constraints:*
- **The clock starts when the image has fully rendered** and stops at the action — the swipe
  gesture starting, or the button tap.
- **No timer is shown.** No countdown, no ring that reads as time, nothing.
- **No count on the progress bar.**
- A factor's two cards are never adjacent — whether the second arrived by the adaptive rule or
  by a deferral.

### 4. Next — "not yet"

The card goes to the **back of the deck** and reappears after everything else, with a fresh
clock. Its latency accumulates across looks.

*Records:* the exposure ends `next`; `next_count` +1.

*Constraint — pair separation:* a deferred card must never land next to its partner. If it would,
**pull the partner forward to be the very next card shown.** The deferred card stays at the back.
§3.3 has the four-line rule.

### 5. Back — "show me that again"

The previous card returns. They can swipe it again or leave it. Either way it's recorded.

*Records:* the exposure ends `back`; `back_count` +1; `changed = true` if the swipe changed.

*Backend:* a changed swipe halves firmness on that card; coming back and leaving it costs a
little (×0.85). The **score itself is untouched** — a revised *love* is still 88. §3.5.

### 6. Timeout — silent auto-Next

After **12 seconds** with no action, the card is deferred as if Next had been pressed. Nothing is
said. With a Next button available, an engaged user never hits this; it exists to catch absence.

### 7. Pause — "Are you there?"

Two consecutive timeouts — one card timed out, the next is within 5 seconds of doing the same —
pause the deck:

> **Are you there?**  [ Yes ]  [ No, I was away ]

| They... | Then |
|---|---|
| tap **Yes** within 5 s | deck continues; timed-out cards stay at the back |
| tap **No, I was away** | deck goes back to the first timed-out card, fresh clock |
| tap nothing for 5 s | deck goes back to it and freezes — **"Quiz paused"** — until tapped |

*Records:* a pause event — cards, button, duration. **The timed-out exposures are discarded**;
they were absence, not doubt. They don't count toward latency or `next_count`.

*Constraint:* the copy must not mention time. "Are you there?" is about presence.

### 7b. A card that won't resolve

Deferred, returned to, deferred again, timed out on the second look. On the third exposure the
card stays — no timeout, no Next, only Swipe and Back — until answered. Lowest firmness. §3.8.

### 7c. Reading someone who defers a lot

Two people can Next most of the deck and mean opposite things. **Fast Nexts (1–3 s each) on most
cards** is someone who wants to see everything before rating anything — drop those first looks,
score on the second. **Slow Nexts (near the 12 s timeout) on most cards** is someone genuinely
unsure — every signal is real. The line is the median first-look latency on Nexted cards, around
4 s to start. §3.6. Log the pattern either way.

### 8. The deck ends — scoring

Backend runs `ASSESSMENT_ENGINE.md` §4 to §7. In brief: score each factor; check pairs; read
neutral vs soft; handle the `POL` split; compute both firmness vectors; pick the top factor —
outright if one is highest, by latency if tied, by forced choice if latency can't separate them.

### 9. The forced choice — only if needed

Shown only when two or more factors are level at the top **and** latency doesn't separate them.
Most users never see it.

> **Last one. All of these matter to you — but if you could only keep ONE for tonight, which is
> the night?**

One option per tied factor, worded as a thing in a picture (list in `ASSESSMENT_ENGINE.md` §7.3).
Text options for now. Eventually one composite image with the tied things in it and the user taps
the region — **that image doesn't exist yet; text is the fallback.**

*Constraint:* **not a scale.** A scale is what produced the tie. Pick one.

*Records:* `top_source = 'picked'`, the choice, and what latency would have said.

### 10. The reveal

> **Your vibe today is**
> **[Name]**

then a line or two on what that means for them tonight — pulled from the vibe description and
personalised.

*Backend:* one name, up to three words — `[refusal prefix] [top word] [second word]` —
*Luxury Diner*, *Quiet Luxury Diner*, *Solo Night Climber*. Top by §7.1; second = highest other
factor within 15 of the top and ≥ 60, `AFFIL` excluded, tie by latency then weight; prefix = the
firmest refusal (§5.5), hard pass only until the latency check passes. Word-lists and the pair
table are in `VIBE_NAMES_V3.md` — never invent a word. No second line. **The name is written once
per session and never recomputed within it.**

### 11. Follow-ups (off-screen)

If anything is owed — a two-card factor at a true 50, a broken `POL` pair needing its winning
sense confirmed — **one** follow-up goes out, carrying everything. Never two for one session.
Identity is the user id it was built for; whatever they type on it is a check, never the address.
A new session voids anything owed on the old one. §8.

---

## What ships in v1

Everything above, with one qualification: **latency is captured and stored from day one, but feeds
only two things** — the tie-break (step 8) and a second firmness vector logged beside the first
(§6.2). It does **not** feed group weighting, bend or abstention until the validation in §6.3 has
been run. Until then `firmness_score` drives all three.

The reason: latency can't be added to old data. If it isn't captured from the first user, the
validation can never be run. But it hasn't been tested on a single person yet, so it doesn't get
to change anyone's outcome until it has.

## Settled — build as written

- Adaptive deck, 10–20 cards, no branch question: an extreme swipe ends a factor, a mild one adds
  a second card three or more positions later; `POL` always gets both (§2)
- Four swipes — love 88, up for it 62, not for me 38, hard pass 12 — words in colour, no emoji (§2.1)
- Refused = hard pass on any card, or not-for-me on both (§5.5)
- Progress bar above the card, no number (§2.6)
- Latency clock: render-complete to gesture-start, milliseconds, never shown (§3.1)
- Pair broken at a gap of 50+; neutral only at a true 50; single cards at face value (§5)
- `POL` is a split factor — classy / current — and a broken `POL` pair is an answer, not a fault (§5.4)
- Firmness from score: distance from 50 (§6.1)
- Score first, always; latency only breaks a tie; forced choice for a dead heat (§7.1)
- Name = prefix + top word + second word from `VIBE_NAMES_V3`; no second line (§7.2)
- One follow-up per session; identity is the user id (§8)
- Rescale at one-third toward the running population centre; name reads raw, matching reads
  rescaled (§9)

## Set, and to be adjusted from data

Every one of these has a value — build it as written; testing cannot start without one. They
are marked because the first 30 app users are where they get *adjusted*. Build them as constants
in one place, changeable without a deploy.

| Constant | Value | Where | Replaced when |
|---|---|---|---|
| timeout | 12 s | §3.2 | timeout rate is known — target is under a few % of cards |
| warm-up cards excluded from latency baseline | 3 | §6.2 | latency-by-position is plotted |
| Next multiplier | 1/(1+0.5·n) | §3.5 | Next rate and Next-vs-clean agreement are known |
| Back: changed / unchanged | 0.5 / 0.85 | §3.5 | Back rate is known |
| deck-browser line | ~4 s median first look | §3.6 | the two Next patterns are seen in data |
| `BEND_EXTREME` — bend at a firm 100 or 0 | 0.20 | plan engine §13.3 | how often firm people are stranded is known |
| public-room list `FLOOR` cutoff | 0.5 (a 20-pt overrun) | plan engine §13.4a | how many rooms firm people see is known |
| `WANT_FLOOR` / `DELIVERS` / `DEBT_K` | 60 / 55 / 0.6 | plan engine §13.4 | how often members are served on #2 or lower is known |
| pause trigger window | 5 s | §3.4 | pause rate on engaged users is known — should be ~0 |
| pause prompt window | 5 s | §3.4 | same |
| latency tie-break gap | 0.15 | §7.1 | tie-break agreement with forced choice is known |
| mood trigger | 5 true neutrals | §8.4 | has never fired on anyone; may need lowering or removing |
| validation thresholds | 0.5 corr / spread 18–20 | §6.3 | first 30 users |

## What has to be instrumented

None of the provisional values can be set without these. Log them from the first user.

**Per card:** every exposure (latency, position, how it ended), final rating, rating history,
next count, back count, changed.
**Per session:** every pause event (cards, button, duration); total duration; what follow-up was
sent and whether it was answered.
**Per user:** both firmness vectors side by side; how the top factor was decided (`outright` /
`latency` / `picked` / `provisional`); the forced-choice answer if given.

Then, at 30 users:

1. **Does latency separate a firm 4 from a soft 4?** For people whose scores are compressed
   (spread under 18), does latency-firmness spread out where score-firmness can't? Pass/fail.
   Pass and latency starts feeding the blend. Fail and it stays a tie-break.
2. **Does the latency tie-break agree with the forced choice?** Four people have forced-choice
   answers on record from the test forms. Anyone who gives both in the app is a calibration point.
3. **How often does the timeout fire?** With Next available it should be rare everywhere — it's
   an absence detector now. If it's common, the Next button isn't discoverable.
4. **How often do Next and Back fire, and on which cards?** Same logic. And which of the two
   Next patterns (§3.6) is more common.
5. **Does the pause ever fire for an engaged user?** It shouldn't.
5b. **How does deck length distribute?** How many people land at 10, 14, 20. And **does hard pass
   get used?** If it sits near 3% like the old "hate" did, the refusal floor rests entirely on the
   not-for-me-twice rule.
6. **Per card: median latency, Next rate, Back rate, timeout rate.** A card slow for everyone is ambiguous.
   This is how the six single-card factors get checked, since they have no partner card.
7. **Is latency-firmness on a person's top factor stable across sessions?** Needed before the
   name can carry firmness (`VIBE_NAMES_V2.md` V3). Anyone with two or more sessions.

## Traps

The full list is `ASSESSMENT_ENGINE.md` §11. The ones most likely to bite:

- **An inner swipe is a preference, not the absence of one.** Only a true 50 is worth a follow-up.
- **A single *not for me* is never a refusal.** Two are. Hard pass is.
- **An undefined factor is not 50.** It carries no weight. Never substitute.
- **The timer is invisible and nobody is told to be quick.** Either one changes what's measured.
- **A timeout is absence, a Next is doubt.** The first is discarded; the second counts.
- **A fast Next is browsing, a slow Next is doubt.** Don't treat every deferral as uncertainty.
- **A deferred card never lands next to its partner.** Pull the partner forward.
- **Never break a tie with a fixed factor order.** One was tried; it was wrong 3 times in 4.
- **A follow-up knows who it was sent to.** Don't let the answer tell you.
- **Store the wording with the answer.**
- **Keep every raw answer forever.** Every rule in the spec was found by re-reading old answers
  under a new rule.

## Out of scope for v1 — but coming, so build with room for it

- **Card reduction over sessions.** A factor answered fast and consistently settles into the
  baseline and leaves the deck; one answered slowly and inconsistently leaves it the other way.
  `PREFERENCE_ENGINE.md` scope note points at the logged design. Needs latency history per
  factor per user, which is why it's captured from day one.
- **Latency feeding the group blend, bend or abstention.** After validation. Bend has three
  levels logged in `OUTING_PLAN_ENGINE.md` §13.3.
- **Naming V3** — a refusal tag gated on a fast refusal, and strong/soft names by latency.
  Proposed, held behind a validation check. `VIBE_NAMES_V2.md` V3 section.
- The composite image for the forced choice — text options until it exists
- `POL` as two separate factors — decided against; it carries a *sense* instead (§5.4)
- Final card images

## Three things in the plan engine you'll hit

- **Every stop serves every member on something they ranked.** Not one stop per person across the
  night. Each member's factors are ranked top-first; at each stop each member is served on the
  highest-ranked one the venue actually has; a stop where anyone is served on nothing loses to any
  stop where everyone is served on something. The per-person line on the plan card is read off
  this. `OUTING_PLAN_ENGINE.md` §13.4 has the code.
- **Debt across stops (§13.4c).** Served on a weak #2 (under 70, or more than 10 below #1) or by
  the area counts half; that person's #1 must come at the next stop, by the venue, with the
  others on their #2 or their #1 carried by the area. A stop for one person alone only when
  nothing of theirs can be served any other way. Payback only while their #1 hasn't been served
  tonight; the debt outranks the energy arc; people with no wants take on no debt. **Location
  (§13.7):** a fallback only — when the venue can't serve someone on `CROWD`, `ENRG`, `POL` or
  `SCEN`, the area around it can, at half strength. Never raises a score, never counts against.
- **Dedicated stop, precisely (§13.4c rules 5–7).** Only when *none* of a person's wants, at any
  rank, can be served anywhere the others tolerate; and the others are softened there, not at
  zero. If even one want is served, no dedicated stop — the next stop heightens whichever of
  their wants the group's bends allow (#1 first, then #2 …).
- **Overall firmness (§13.8, assessment §6.5).** Per person: share of extreme swipes (plus mean
  latency-firmness once validated), as a population percentile. Scales debt 0.5–1.5×.
- **Friend mode (§13.9).** Behavioural, pairwise: ~three plans together in 90 days. Friends get
  relaxed bends toward each other's firm wants and a combination search (one want of each, against
  real venues; substitutes from their vibe profile; dedicated stops only when nothing pairs) —
  no debt. Co-hosts who are not yet friends get §13.4c.
- **The learning layer reads behaviour** (`PREFERENCE_ENGINE_V2.md` §8b): plan ratings, refreshes,
  rooms joined, venues searched / saved / attended — each an observation with its own reliability.
  Not v1, but log all of it from day one.
- **Bend by context (§13.4c head, §13.4d).** In a group plan bend is *stretch* — how far a person
  can be pulled across the stops; a firm aversion still gets one want served at every stop, a
  firm want gets at least one stop (rule 10). In a solo plan, and for a joiner judging a frozen
  plan, bend is a *gate* — every stop inside it, served at their level.
- **A served want compensates an overrun aversion (§13.4c rule 9).** Bend is a gate only for a
  person served on nothing at that stop; for anyone served — fully, partially (the venue has the
  thing, not at their level), or by the street — being past their aversion ceiling is a cost
  (`OVERRUN_W` per point), not a bar. Hard pass is still a wall. Order at a stop: nobody gets
  nothing → most served (× debt) → calmer first at stop 1 → least stepping-on.
- **Two floors (§13.4, §13.4c).** `AVERSION_FLOOR` 55 — a venue under 55 on a factor can't overrun an
  aversion to it. `SERVED_FLOOR` 0.85 — half a reason once doesn't count as having been served.
  The energy arc is a preference that yields to nobody-gets-nothing, payback and pairing. §13.10
  lists every variable added on 2026-09-17 in one table.
- **Room chemistry (§13.6).** Read off firmness. If a member's top factor is not served by the
  room vector, the room owes it to them: their vote on that one factor counts three times, capped
  at the others' bend + 10. Seven states from that — In Sync, Got Your Back, Best of Both, Along
  for the Ride, Something for Everyone, Open Night, Could Go Late — one word on the room card next
  to the blend style. Joiners are graded by how much they'd shift the room, how much they add to
  it, and whether they fit its state; the plan stays the gate. Open Night rooms host without a
  plan; the first firm joiner makes one.
- **Hosting freezes the plan.** FLOOR v3 runs for host and co-hosts before the room goes public;
  the refresh button is removed on hosting; joiners are filtered against the fixed plan and never
  trigger a regeneration. Locking freezes the room — a separate, later step.

Found on 2026-09-14 by running a worked journey through the rules. `OUTING_PLAN_ENGINE.md` §13.

- **When `FLOOR` fails** — a member with no viable stop — relax that member's softest-held
  constraint (lowest latency-firmness among the overrunning factors), re-plan, repeat up to three
  times, then say the room isn't a fit. Plan-time only; the profile is untouched. The plan card
  carries a short note under the venue — "Ruchi might miss out on the food a little here" (eased a
  want) or "Ruchi might not like the crowd a little here" (eased an aversion) — with an ⓘ that
  opens the factor, the reason, and what the stop still gives her. `OUTING_PLAN_ENGINE.md` §13.1.
- **The public-room list is gated on plan suitability for the joiner alone and sorted by §13.6's match** — 70% plan
  similarity *and* a FLOOR check for that one person against the room's actual venues. The 70% by
  itself passes nearly everything; FLOOR is the check that separates rooms. Blend drift and
  CONSENSUS are the *host's* checks, on the request list, not the joiner's. Plan engine §13.4a.

## Questions welcome on

The spec was written from a week of testing on Google Forms with about twenty people; from
here testing is in the app itself. It's
specific because the testing was; where it says a number is a guess, it is one. If something
doesn't fit how the app is being built, say so — most rules have a reason recorded in
`DECISIONS.md` and some of those reasons are forms-specific.

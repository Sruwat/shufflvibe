# Assessment Engine — Backend Specification

**Audience:** a backend engineer joining SHUFFL with no prior context.
**What this covers:** one session of cards, from the first tap to a stored profile. What happens
*between* sessions — the trait/state model and card reduction over weeks — is `PREFERENCE_ENGINE.md`.
What happens *with* the profile — matching, blending, plans — is `OUTING_PLAN_ENGINE.md`.
**Companion docs:** `FACTORS_V5.md` (the seven vibe factors and six preferences), `VIBE_NAMES_V4.md` (the
name), `CARD_SET_V10.md` (both decks), `DECISIONS.md` (why). **Part 0a below is the 2026-09-17 split;
read it before §1.**

Every rule here was arrived at on real testers during 2026-09-08 to 2026-09-15 and the reason for
each is in `DECISIONS.md` under that date. Where a rule is a guess it says so.

**From 2026-09-16 testing happens in the app itself** — a downloadable build with real images and
real latency. The Google Forms used until then are retired; any reference below to "the test
forms" is history, kept because it explains a rule.

**Card images are placeholders** until the final set is decided. Every card still has a stable id,
a factor and a side, and the wording it is meant to convey is stored with each answer.


---

# 0a. The split factor set — read before §1 (2026-09-17)

**The ten factors became thirteen, in two kinds.** `FACTORS_V5.md` defines them; this part says
what it does to the cards, the scoring, the reading and the record. Wherever §1–§12 below say
"factor", read "vibe factor" unless this part says otherwise. `POL`'s §2.3 and §5.4 rules move to
the preference deck. `PLAY` is gone; `GAMES`, `MOVE`, `ROAM`, `TALK` are new.

| | Vibe factors — 7 | Preferences — 6 |
|---|---|---|
| | `ENRG` `AFFIL` `CROWD` `TALK` `ROAM` `MOVE` `GAMES` | `FOOD` `LIVE` `POL` (+ sense) `SCEN` `NOV` `HERIT` |
| when | every session — the daily deck | once, at onboarding, before the first vibe deck; editable in the profile |
| what a card is | a scene, both poles present, two cards per factor (A, B) | the thing itself, one card |
| the four swipes | **LOVE / UP FOR IT / NOT FOR ME / HARD PASS** — 88 / 62 / 38 / 12, as §2.1 | **The whole point / Nice to have / Don't mind / Don't care** — 88 / 62 / 38 / 12 |
| what a low score is | a want — the low pole | an absence of interest — **never an aversion** |
| hard pass | a firm low pole; `refused` (§5.5) applies | does not exist — the bottom swipe is "don't care" and is not a refusal |
| second card | by the adaptive rule (§2.2), ≥ 3 positions later (§2.4) | none — importance is not ambiguous the way a scene is |
| firmness | \|s − 50\| / 50 (§6.1); latency (§6.2) | importance / 100; latency logged, not used |
| neutral / broken pair / follow-ups (§5, §8) | as written | not applicable — one card, no pair |
| the name (§7) | from these seven — `VIBE_NAMES_V4.md` | badges on the profile, never the name |
| rescaling (§9) | as written, on the seven | none — importance is absolute |
| deck length | **7 to 14 cards** | 6 cards + one image pair, once |

### 0a.1 The onboarding order

1. The preference deck, behind one screen: *"Swipe on the following things on the basis of how
   important they are to you in a place."* Six cards and the `POL` sense pair (`CARD_SET_V10.md`
   §1). Latency is captured (the clock, Next, Back, the pause — §3 apply unchanged) and logged;
   nothing reads it yet.
2. The vibe deck, behind §3.7's screen, as every day after.
3. The reveal: the name from the vibe deck. Then the profile, with the preferences shown as an
   editable row and the badges.

A person who skips or abandons the preference deck gets all six at 50 — *don't mind* — and a
prompt in the profile. Nothing downstream breaks on 50s; the fill stage just has nothing to pull
on for them.

### 0a.2 Scoring a preference

```python
def score_preference(answer: CardAnswer) -> PreferenceReading:
    return PreferenceReading(importance = SWIPE_SCORE[answer.swipe],        # 88 / 62 / 38 / 12
                             firmness   = SWIPE_SCORE[answer.swipe] / 100,  # low importance abstains in a group
                             latency    = answer.total_latency_ms)           # logged
```

`POL` carries its sense from the image pair: `classy` / `current` / `both`. §5.4's table is
retired — there is one `POL` card and one sense tap. The follow-up in the winning sense (§8) is
retired with it.

### 0a.3 Scoring a vibe factor

§4 and §5 as written, on the seven. Both poles are wants, so `refused` (§5.5) now means *a firm
low pole* — a person who hard-passes the crowd card wants an empty room, and that is served, not
avoided. The name's refusal prefix is gone for the same reason (`VIBE_NAMES_V4.md`).

### 0a.4 The record

`Assessment` (§10) gains `preferences: dict[str, PreferenceReading]` and `pol_sense`, both copied
from the profile at session time so a plan generated tonight reads the preferences as they were
tonight; `scores_raw`, `scores_rescaled`, `firmness_*` and `top_factor` are on the seven vibe
factors. `label_line2` is gone; `badges: list[str]` is added.

### 0a.5 What §12 still owes

The two new vibe factors and the two halves of `PLAY` have no card history; `TALK` and `ROAM`
are the ones a picture may fail to carry (`CARD_SET_V10.md` §4). `GAMES` may be nearly one-ended
(`FACTORS_V5.md` §2). Weights on both kinds are set and unmeasured.

---

# 0. What this system does

A user swipes through image cards — between ten and twenty, decided by their own answers as they
go. The engine turns that into:

| Output | Type | Consumed by |
|---|---|---|
| `scores` | ten integers, 0–100 | matching, blending, plan generation |
| `firmness` | ten floats, 0–1 | group weighting, bend, abstention |
| `label` | one name, up to three words (`VIBE_NAMES_V3.md`) | display only — **nothing downstream reads it** |
| `flags` | what needs a follow-up, what looks wrong | the follow-up chain, and card QA |
| `latency` | ten floats, normalised | the tie-break, and (later) firmness |

Two things carry the reading: **which way they swiped each card**, and **how long they took**. The
swipe is the answer; the time is how firmly it is held. Section 3 is the part most likely to be built
wrong, and the part that cannot be fixed on old data afterwards.

---

# 1. The ten factors — *as they were; see Part 0a for the thirteen*

| Code | Measures | Cards agree? | Penalty class |
|---|---|---|---|
| `CROWD` | how many people around you | usually | participatory |
| `ENRG` | movement and intensity | usually | participatory |
| `SCEN` | how much the look matters | usually | passive |
| `FOOD` | how much the food is the point | sometimes | passive |
| `POL` | how dressed-up — **two senses, see §5.4** | often not | participatory |
| `NOV` | wanting somewhere new | often not | participatory |
| `PLAY` | something to actually do | always | participatory |
| `LIVE` | a performance is the reason | always | participatory |
| `HERIT` | somewhere old | usually | passive |
| `AFFIL` | facing the room, or your own table | usually | participatory |

Weights, penalty semantics and the 42 library vibes are in `FACTORS_AND_VIBES_V4.md`. The
"cards agree?" column is measured pair agreement across 22 sheets and decides the card counts in §2.

---

# 2. The cards, and the adaptive deck

### 2.1 The swipe

Each card is an image. The person swipes it one of four ways:

| swipe | label | colour | score |
|---|---|---|---|
| up | **LOVE** | gold | 88 |
| right | **UP FOR IT** | green | 62 |
| left | **NOT FOR ME** | grey | 38 |
| down | **HARD PASS** | red | 12 |

Labels are words in the colour given. **No emoji.** The bottom direction was "hate" with a vomit
emoji in an earlier design and almost nobody used it — 3% of scores reached the floor against 13%
on a number scale. Swiping a vomit at a picture is a social act, not a preference. "Hard pass" is
a preference.

The four scores are the ones the test forms have used since 2026-09-08. No middle value: the two
inner swipes lean, and the person has to lean one way.

### 2.2 The deck adapts to the answers

Every factor starts with one card. What happens next depends on the swipe:

```
LOVE or HARD PASS        the factor is done - one card was enough
UP FOR IT or NOT FOR ME  a second card for the same factor, from a different angle, joins the deck
```

An extreme answer is believed. A mild one is checked. So the deck is **ten cards for somebody
decisive, twenty for somebody who leans mildly on everything, and around fourteen for most** —
without asking anyone how sure they are. The branch question on the test forms did this by
self-report; this does it from behaviour.

The second card resolves the lean:

| first | second | score | reads as |
|---|---|---|---|
| up for it | love | 75 | lean confirmed and strengthened |
| up for it | up for it | 62 | mild yes, confirmed |
| up for it | not for me | 50 | true neutral — §5.2, the follow-up chain |
| up for it | hard pass | 37 | **broken pair** — the two cards disagree, §5.1 |

Symmetric for *not for me*.

### 2.3 `POL` always gets both cards

`POL` is the split factor — its two cards measure two different senses, classy and current
(§5.4). A *love* on the classy card would end `POL` and hide whether they hard-pass the trendy one,
which is exactly what the split exists to catch. So `POL` shows both cards regardless of the first
swipe. It is the only exception.

### 2.4 Where the second card goes

Not next. A factor's two cards are never seen back to back. The second card is inserted **at
least three positions after the first was answered**, or at the end of the deck if fewer than
three remain. The same rule as pair separation on a deferred card (§3.3), for the same reason: a
pair seen together reads as one question asked twice.

**The edge case, explicitly:** if the first card was the *last* card in the deck — or fewer than
three cards remain, counting any deferred cards waiting at the back — the second card goes at the
end, which may make it the very next card. The separation rule gives way; the pair is never
dropped and the deck never ends with a factor half-asked. Deferred cards count as remaining
cards, so a person with three cards still parked at the back gets the normal three-card gap.

```python
def add_second_card(deck, position_now, factor):
    card = second_card_for(factor)
    at = min(position_now + 3, len(deck))
    deck.insert(at, card)
```

### 2.5 The cards

Each factor has two texts, `A` and `B`, two angles on the same thing. `A` is the first card shown;
`B` is the second, when one is needed. Wordings in `CARD_SET_V9_IMAGE.md`; the app renders each
as an image (`IMAGE_PROMPTS.md`), and the wording is what the image has to convey.

The merged `S` cards from the fixed-deck design are retired. They existed to carry both angles
when only one card would be shown; adaptive shows the second angle whenever it is needed.

**Image brief:** each `A` card has to carry its factor cleanly on its own, since for a decisive
person it is the only card of that factor they see.

### 2.6 Order and the progress bar

Start with the ten `A` cards in a fixed order (randomised within the ten is fine). Second cards
join as answers come in, per §2.4; deferred cards rejoin at the back, per §3.3.

**A progress bar sits above the card. It shows no number.** The deck's length is not known in
advance, so "3 of 14" would be wrong the moment a second card was added. The bar reflects
**factors resolved out of ten** — a factor is resolved on an extreme swipe, or on the second
card's swipe — and it never moves backwards. A mild first swipe counts as half.

`score = swipe value`, averaged when a factor has two cards. That is the same 0–100 axis
everything else uses.

---

# 3. Latency, Next and Back

**This is the part to get right from day one, because it cannot be added to old data later.**

Two things carry how firmly an answer is held: how long the person looked before acting, and
whether they deferred or revised. Both are recorded; neither is ever shown to them as a clock.

### 3.1 The three actions on a card

| Action | What it means | What happens |
|---|---|---|
| **Swipe** | the answer | score stored, next card |
| **Next** | "not yet" | card goes to the **back of the deck**, reappears after everything else |
| **Back** | "I want to see that again" | previous card returns; they may swipe it again or leave it |

Next is uncertainty *stated*. The old design inferred it from a card timing out, which is
ambiguous — torn, or phone in pocket. A person who is torn now has a button, so a timeout means
absence and almost nothing else (§3.4).

A card that comes back after Next is answered with the whole deck as context. That is a
comparative reading — "against everything else, this" — and probably a better one.

### 3.2 What is recorded

A card can now be seen more than once. Every exposure is stored.

```python
@dataclass
class Exposure:
    latency_ms:        int          # render-complete -> the action, this exposure
    position_in_deck:  int          # where it was when shown this time
    ended_by:          str          # 'swiped' | 'next' | 'timeout' | 'back'

@dataclass
class CardAnswer:
    user_id, session_id:  str
    factor:               str       # 'CROWD' ... 'AFFIL'
    side:                 str       # 'A' | 'B' | 'S'
    first_position:       int       # 1-based, where it sat in the original deck
    exposures:            list[Exposure]
    swipe:                str | None    # the FINAL swipe: 'love' | 'up' | 'not' | 'pass'
    swipe_history:        list[str]     # every swipe given, in order - Back can change it
    next_count:           int       # deferrals, manual or by timeout
    back_count:           int       # times returned to
    changed:              bool      # final swipe differs from the first one given
    total_latency_ms:     int       # sum over exposures
```

Rules for the clock, per exposure:

1. **Start at render-complete**, not at request. Image load time is network, not thought.
2. **Stop at the action** — the swipe gesture starting, or the Next/Back tap. Not gesture end.
3. **The timer is never shown**, and the person is never told to be quick. See §3.7.
4. **Do not round.** Store milliseconds.

`ended_by` matters. A first exposure ended by `next` after 2 seconds is "show me the rest first."
Ended by `next` after 10 seconds is torn. The same button, two meanings, and the latency tells
them apart (§3.6).

The psychology: attitude accessibility (Fazio et al., 1986 onward). A strongly held attitude
activates fast; a weak one has to be constructed on the spot. Bassili (1996): latency predicts
attitude stability better than asking people how sure they are. Latency measures **strength, not
direction** — a fast "hate it" is as fast as a fast "love it." `DECISIONS.md` 2026-09-11.

### 3.3 Next — deferral, and where the card goes

The card leaves and rejoins at the back. When the person reaches it again it has a fresh
exposure with its own latency; the total accumulates.

**Pair separation on re-insert.** A deferred card can land next to its partner. Say `ENRG·A` is
deferred with `ENRG·B` sitting at position 13 of 14 — the deferred card would go to 15, adjacent.
The rule: **when a deferred card would land adjacent to its partner, the partner is pulled
forward to be the very next card shown.** The deferred card stays at the back; the partner moves
away from it, not the other way round. A factor's two cards are never seen back to back, in
either direction.

```python
def defer(deck, card):
    deck.remove(card); deck.append(card)
    partner = partner_of(card)
    if partner in deck and deck.index(partner) == len(deck) - 2:
        deck.remove(partner); deck.insert(0, partner)      # shown next
```

### 3.4 Timeout — absence, and the pause

A card with no action for **12 seconds** is deferred automatically — an auto-Next, silent.
With a Next button available an engaged person never reaches this, so it is an absence detector
and nothing else. If it fires on more than a few percent of cards something is wrong with the
cards, not the number.

**Two consecutive auto-Nexts** — one card timed out, and the next is within 5 seconds of timing
out — pauses the deck:

> **Are you there?**  [ Yes ]  [ No, I was away ]

| They... | Then |
|---|---|
| tap **Yes** within 5 s | deck continues; the timed-out cards stay at the back |
| tap **No, I was away** | deck goes back to the first timed-out card, fresh exposure |
| tap nothing for 5 s | deck goes back to it and freezes — "Quiz paused" — until tapped |

**A timeout that led to a pause is absence.** Those exposures are **discarded** — dropped from
`exposures`, not counted in `total_latency_ms`, and the auto-Next does not count toward
`next_count`. The second look is the only one that counts.

The prompt copy must not mention time or speed. "Are you there?" is about presence.

Log every pause: which cards, which button, how long. One pause in a session is a soft quality
flag; two is a distracted session.

### 3.5 Firmness from the three signals

Score gives direction and strength. Latency gives thought. Next and Back give explicit doubt.
They combine so that each can only *lower* firmness, never raise it:

```python
def firmness_card(card, latency_rank):
    """latency_rank: this card's rank-based latency firmness (§6.2), computed on
    TOTAL latency across its counted exposures - fastest 1.0, slowest 0.0."""
    f = abs(SCORE[card.swipe] - 50) / 50.0         # from the score: love/pass 0.76, up/not 0.24
    f *= latency_rank                               # from thought
    f *= 1.0 / (1.0 + 0.5 * card.next_count)        # one Next x0.67, two x0.5
    if card.changed:      f *= 0.5                  # they swiped it differently the second time
    elif card.back_count: f *= 0.85                 # came back, left it - a smaller doubt
    return f
```

Accumulated latency does most of the work — a card deferred and then stared at is slow *in
total*, and the rank catches it. The Next and Back terms are for the explicit act, on top.

**The score itself is never touched.** A deferred *love* is still 88.

The constants — 0.5, 0.5, 0.85 — are illustrations of shape, not measured values. §6.3.

### 3.6 Reading a person who defers a lot

Two people can both press Next on most of the deck and mean opposite things. The first-exposure
latency on those Nexts tells them apart:

| Pattern | What it means | What to do |
|---|---|---|
| Nexts on most cards, each after **1–3 s** | wants to see the whole deck before rating any of it | first exposures are browsing, not doubt: **drop them** from the total and do not count those Nexts. Score on the second exposures alone |
| Nexts on most cards, each **near the 12 s timeout** | genuinely unsure about most things | every signal is real: firmness is low across the board, and that is the reading |

The line between them is a threshold on the median first-exposure latency of the Nexted cards —
somewhere around 4 seconds — and it is one more constant to set from data. Log the pattern
either way; the deck-browser is a distinct type of person and worth knowing about.

### 3.7 What the person is told beforehand

Nothing about time, and nothing about speed. The line that was drafted — *"the cards disappear
after a few moments so try and answer as fast as you can"* — would undo the measurement: once
read, every card is answered under instruction to hurry, and latency then measures compliance
rather than accessibility. Every study behind this measures people who are not trying to be
fast.

The copy, settled 2026-09-16:

> Swipe how you feel about tonight. Gut call — first reaction wins.
> Not sure? Hit Next and it comes back later.

It names *tonight* (otherwise people answer about their personality), gives Next a job without
making it an escape, and "first reaction wins" invites speed without asking for it. Back is not
mentioned — it is a visible button and explains itself.

### 3.8 A card that will not resolve

Deferred, come back to, deferred again, timed out on the second look. Someone genuinely stuck.
They have to answer every card, so on the third exposure the card stays with no timeout and no
Next — only Swipe and Back — and that factor gets the lowest firmness there is. The answer counts;
its strength is near zero. Do not skip it and do not substitute 50.

---

# 4. Scoring a factor

```python
def score_factor(answers: list[CardAnswer]) -> FactorReading:
    """answers = every card for one factor in this session: 1 or 2 of them."""
    vals  = [a.rating * 20 for a in answers if not a.timed_out]
    sides = [a.side for a in answers if not a.timed_out]
    if not vals:
        return FactorReading(score=None, ...)              # undefined, never 50
    return FactorReading(
        score      = round(mean(vals)),
        vals       = vals,
        sides      = sides,
        n_cards    = len(vals),
        gap        = max(vals) - min(vals) if len(vals) > 1 else 0,
    )
```

An undefined factor stays undefined. **Never substitute 50** — that is a real neutral, and this is
an absence of data.

---

# 5. Reading the answers

Four questions are asked of every factor, in this order. The constants are the ones running on
the live test as of 2026-09-12.

### 5.1 Is the pair broken?

```python
BROKEN_GAP = 50
if reading.n_cards > 1 and reading.gap >= BROKEN_GAP:
    if factor in SPLIT:      -> §5.4
    else:                    flag 'broken', score stays but is untrusted
```

Two cards 50+ apart are not measuring the same thing. That is a fault in the cards, not a fact
about the person — except for a `SPLIT` factor, where it is the expected answer.

### 5.2 Is it neutral, or merely soft?

Two different questions, and they were the same test until 2026-09-10.

```python
middling = 40 <= score <= 60          # a soft answer
neutral  = abs(score - 50) <= 5       # no information at all
```

**An inner swipe is not an absence of preference. It is one:** *not for me* is would-rather-not,
not would-walk-out. It scores 38, and 38 is a real reading.
Score-firmness reads it as 0.24, bend as nearly open, a group blend as little pull. Only a true 50
means nothing was said.

`middling` is kept as a flag. On the forms it caught somebody who claimed to be sure and then
hedged on eight of ten; in the app there is no claim to check, and latency reads the hedging
directly. Store it, do not act on it.

### 5.3 Single cards are read at face value

Under the adaptive deck a factor rests on one card only when that card was swiped *love* or *hard
pass* — so a single-card factor is always extreme, always believed, never chased. The rule is kept
for completeness and for `POL`, whose two cards can produce any combination:

```python
if reading.n_cards == 1:
    neutral = False                 # a single card is never chased
```

Two cards *can* average to a true 50 — *up for it* then *not for me* — and that is a real fence-sit.

### 5.4 Split factors — `POL`

`POL` has two senses in Delhi: **classy** (suits and dresses) and **current** (whatever is in
fashion). A person can want one and actively not want the other. Meher scored 80 on classy and
20 on current; Anchal scored 40 and 100. Averaging destroys exactly what they said.

```python
SPLIT = {'POL': {'A': 'classy', 'B': 'current'}}

if factor in SPLIT and reading.gap >= BROKEN_GAP:
    winner_side = sides[argmax(vals)]
    score       = max(vals)                     # provisional: the sense they hold
    flag 'split', ask_in_sense = winner_side    -> §7.2
```

When the follow-up returns, **the losing card is dropped, not averaged back** — a 20 on the
trendy card is not a low `POL` score, it is a different thing they did not want.

**`POL` does not become two factors. It carries a sense.** Decided 2026-09-16. The profile stores
one `POL` score and one `POL` sense:

| classy card | current card | `POL` | sense |
|---|---|---|---|
| love | not for me | 88 | `classy` |
| not for me | love | 88 | `current` |
| love | love | 88 | `both` |
| up for it | up for it | 62 | `both` |
| not for me | not for me | 38 | — (refused) |

The score is the higher card when they split, the average when they agree. The sense is a venue
attribute at plan time — a `classy` person is not sent to a streetwear club at POL 85 — and a
label detail: *Dressed For It (classy)*. No new column in the vibe library, no new weight, no
new card. The follow-up in the winning sense (above) stays.

### 5.5 Refused

A rule, not a threshold:

```python
refused = any(sw == 'pass' for sw in card_swipes)  or  all(sw == 'not' for sw in card_swipes)
```

**Hard pass on any card, or not-for-me on both.** The second clause is what gets the floor back:
people will not swipe the bottom direction — 3% did on the four-way forms against 13% on a
number scale — but somebody who says *not for me* to both angles of a factor has refused it in
plain language. A single *not for me* never ends a factor, so it is never a refusal on its own.

Reads the raw swipes, never a rescaled score.

No longer part of the name. Still a flag: it is what lets the plan engine know a factor is a hard
no rather than a soft one.

---

# 6. Firmness

Two measures, kept separate until the second is validated.

### 6.1 From the score

```python
firmness_score = abs(score - 50) / 50          # 0 at the centre, 1 at either end
```

This is what runs today and what drives group weighting, bend and abstention. Its weakness: it is
derived from the score, so a person who compresses to 3-4-5 has low firmness on everything **by
construction**, whether or not they are decisive.

### 6.2 From latency

Rank-based, within person, so it needs no distributional assumptions and is per-person by
construction.

```python
WARMUP = 3          # first cards are interface learning; scored, but not used for the baseline

def latency_firmness(session: list[CardAnswer], card_baseline: dict) -> dict[str, float]:
    usable = [a for a in session if a.first_position > WARMUP and a.exposures]
    if len(usable) < 5:
        return {}                                   # too few to rank

    # remove the card's own slowness - a busy image takes longer for everyone
    # TOTAL latency across counted exposures - a deferred-then-stared-at card is slow in total
    adj = {a: log(a.total_latency_ms) - card_baseline.get((a.factor, a.side), 0.0) for a in usable}

    ranked = sorted(usable, key=lambda a: adj[a])   # fastest first
    n = len(ranked)
    per_card = {a: 1.0 - i / (n - 1) for i, a in enumerate(ranked)}   # fastest 1.0, slowest 0.0

    out = {}
    for factor in FACTORS:
        cards = [a for a in usable if a.factor == factor]
        if cards:
            out[factor] = mean(per_card[a] for a in cards)
    return out
```

`card_baseline[(factor, side)]` is the running mean of `log(latency_ms)` for that card across all
users, maintained like the population centre in §9. Start it at 0 and it self-corrects.

With images this baseline is doing less than it would on text. A sentence takes longer to read
the longer it is, regardless of identification — that confound is gone. What remains is that a
busy image takes longer to parse than a simple one, which the baseline still corrects.

This rank is one of three terms; §3.5 multiplies in the Next and Back terms. Exposures discarded
by a pause (§3.4) or by the deck-browser rule (§3.6) are not in the total.

### 6.3 What latency firmness is used for — and not yet

| Use | Status |
|---|---|
| Tie-break for the top factor (§7.1) | **ship** |
| Logged beside `firmness_score` on every profile | **ship** |
| Group weighting, bend, abstention | **not until validated** — keep `firmness_score` |
| Soft-answer detection, card QA, disengagement, mood routing | after validation |

**Validation criterion** — run on the first 30 app users:
- for people whose score spread is above 20, `firmness_latency` and `firmness_score` should
  correlate at 0.5 or better across their ten factors;
- for people whose score spread is under 18 — the ones who answer 3, 4 or 5 to nearly everything
  — `firmness_latency` should have *more* spread than `firmness_score`.

If the second condition fails, latency is not separating a firm 4 from a soft 4, which is the one
job it was brought in for, and it stays a tie-break only. (On the test forms one in three people
compressed this way; none of them can be used for this check, since the forms have no timing.)

**A third check, for the refusal prefix in `VIBE_NAMES_V3.md` §3.3:** for people with two or
more sessions, is a *fast* refusal stable — same factor refused with latency-firmness ≥ 0.6 each
time? Until this passes the prefix runs on hard passes alone. **A fourth, for the held strong/soft
names:** is latency-firmness on the top factor on the same side of a strong/soft line each
session? If not, the name cannot carry firmness.

### 6.4 Card QA from latency

Once 30 users are in, per card: median normalised latency, Next rate, Back rate, timeout rate. A card
that is slow for everyone, or deferred often, is ambiguous — and this works on the six single-card
factors, where there is no partner card to disagree with. It is the broken-pair check, per card,
automatic.

---

### 6.5 Overall firmness — one number per person

How opinionated somebody is in general, as distinct from how firm they are on any one factor:

```python
extreme_share    = share of cards swiped love or hard pass
overall_firmness = percentile(extreme_share, population)                       # until §6.3 validates
                 = 0.5 * that + 0.5 * percentile(mean latency-firmness, population)   # after
```

A population percentile, 0–1, recomputed each session, stored on the record (§10). The plan
engine reads it to scale how fast the room comes to owe a person (`OUTING_PLAN_ENGINE.md` §13.8):
somebody opinionated about everything is shortchanged more by a compromise than somebody firm on
two factors and easy on the rest. Nothing in this document reads it; it is measured here because
this is where the cards are.

---

# 7. The top factor and the name

See `VIBE_NAMES_V2.md` for the names themselves.

### 7.1 Choosing the top factor

**Score first, always.** Latency never overrides a rating: a 100 answered slowly beats a 90
answered fast. Latency comes into it only when two or more factors are level at the top.

```python
STICKY = 15

def top_factor(scores, lat_firm):
    hi   = max(scores.values())
    tied = [f for f in scores if scores[f] == hi]
    if len(tied) == 1:
        return tied[0], settled=True

    # latency breaks the tie: which of the joint-highest did they answer without hesitation
    if lat_firm and all(f in lat_firm for f in tied):
        by_speed = sorted(tied, key=lambda f: -lat_firm[f])
        if lat_firm[by_speed[0]] - lat_firm[by_speed[1]] >= 0.15:
            return by_speed[0], settled=True

    # dead heat: ask them (§7.3). Until they answer, provisional.
    return tied[0], settled=False
```

The 0.15 gap is a guess. Tune it once latency data exists; the intent is "clearly faster", not
"faster by a millisecond".

**Do not break the tie with a fixed factor order.** One was tried (`ENRG, CROWD, LIVE, PLAY,
FOOD, SCEN, POL, HERIT, AFFIL, NOV`) and was contradicted by three of the four people who were
then asked directly. It is used for exactly one thing: ordering the options in the forced-choice
question, so the display is stable.

### 7.2 The label

**One name, up to three parts, never a sentence** — `VIBE_NAMES_V3.md` (2026-09-16). The
second line ("also strong on …") is gone; what it carried is now in the name.

```
[refusal prefix]  [top-factor word]  [second-factor word]
```

```python
top    = top_factor(scores, firmness_latency)          # §7.1 - score, latency tie-break, forced choice
second = second_factor(scores, firmness_latency, top)  # within 15 of top, >= 60, AFFIL excluded;
                                                       # tie -> latency, then weight; no forced choice
prefix = refusal_prefix(scores, firmness_latency, refused, validated)
                                                       # one, the firmest refusal (§5.5);
                                                       # hard pass only until §6.3 validates,
                                                       # then any refusal with firmness_latency >= 0.6
topword = TOP_WORD[top] if top != 'POL' else ('Hype' if pol_sense == 'current' else 'Luxury')
core   = f'{topword} {SECOND_WORD[second]}' if second else SINGLE_NAME[top]
name   = f'{prefix} {core}' if prefix else core        # 'Luxury Diner', 'Quiet Luxury Diner'
```

Word-lists, the full pair table and the rules are in `VIBE_NAMES_V3.md`. `AFFIL` is excluded from
the second slot because it runs within reach of the top for most people and would say the same
thing about everyone. It still competes for the top, and *Solo* is its refusal prefix.

**The name is written once and not recomputed** when the population centre moves (§9) or when
latency firmness later changes. A label that changes under someone is worse than a slightly
wrong one.

### 7.3 The forced choice

When latency does not separate the joint-highest factors, ask:

> **Last one. All of these matter to you — but if you could only keep ONE for tonight, which is
> the night?**

with one option per tied factor, worded as a thing in a picture:

```
CROWD  The room being packed          NOV    It being somewhere new
ENRG   How late and loud it gets       PLAY   Having something to play
SCEN   The way the place looks         LIVE   The act on stage
FOOD   What comes out of the kitchen   HERIT  The place being old
POL    Everyone being dressed up       AFFIL  Who you came with
```

Eventually one image with the tied things in it, tap the part that is your night. **Not a scale** —
a scale is what produced the tie. The answer becomes the name outright.

---

# 8. Follow-ups

After the session is scored, at most **one** follow-up is sent, containing everything owed:

| Condition | What is asked |
|---|---|
| a two-card factor at a true 50 | that factor's tie-break card, swiped four ways like any other |
| a `SPLIT` factor broken | the tie-break card **in the winning sense only** |
| joint-highest not separated by latency | the forced choice (§7.3) |

If nothing is owed, nothing is sent. If several things are owed, one form carries them all —
somebody is never chased twice for one session.

### 8.1 Merging a follow-up

```python
for factor, extra in followup.items():
    base = reading[factor].vals
    if factor in split_asked:               # keep the winner, drop the loser
        base = [max(base)]
    reading[factor].vals = base + extra
    reading[factor].score = round(mean(reading[factor].vals))
```

### 8.2 Identity — the rule that was broken three times in three days

**A follow-up is built for one known user. Whatever they type on it is a check, never the address
of record.** Match on the user id the form was created for. Three separate bugs this week came from
letting the data say who it was from instead of the system knowing:

- a bulk send that read a retired form's responses and emailed ten people about cards that no
  longer existed
- a person who had already answered being asked again because eligibility was read from the
  original sheet, which still looked unresolved
- a mistyped email on a follow-up stranding the answer under a name that matched nothing

### 8.3 Once per session

A user gets at most one follow-up per assessment session. A **new** session voids anything owed
on the old one — different factors may be unclear this time, or none.

### 8.4 Mood

If, after follow-ups, **five or more** factors are still a true 50, they are sent the mood cards (`CARD_SET_MOOD_V1.md`). On the test data this has never
fired — nobody has ever had five true neutrals — so treat the threshold as a placeholder.

---

# 9. Rescaling, and the running centre

`DECISIONS.md` 2026-09-09. **Direction, not yet implemented on the forms.** Implement it here.

People use the scale differently. One person's 4 is another's 5. Each person's ten scores are
shifted toward the population centre and stretched toward the population spread — **at one third
of the full correction**:

```python
def rescale(scores, pop_mean, pop_sd):
    p_mean = mean(scores.values()); p_sd = stdev(scores.values())
    if p_sd < 5: p_sd = 5                                # a flat person divides by nothing
    out = {}
    for f, s in scores.items():
        full = pop_mean[f] + (s - p_mean) * (pop_sd[f] / p_sd)
        out[f] = s + (full - s) / 3
    return out
```

Full strength was tested and made retakes 37% *less* repeatable; one third leaves them unchanged
while still pulling a compressed person apart.

`pop_mean` and `pop_sd` are **running averages over every user so far, per factor** — not a
constant, not a frozen table. At seven users the error is about 5 points per factor; at 300 it is
about 1. No decay, no window.

**What reads which:**

| | raw | rescaled |
|---|---|---|
| `refused` flag | ✓ | |
| the label (§7) | ✓ | |
| matching, blending, bend | | ✓ |
| the stored profile | both | both |

The label reads raw because a rescale is linear with a positive multiplier and cannot reorder — so
the top factor is the same either way — and because a label must not change under someone when
the centre moves.

---

# 10. What to store

```python
@dataclass
class Assessment:
    user_id, session_id, taken_at
    answers:           list[CardAnswer]      # every card, every exposure - never discard
    pauses:            list[PauseEvent]      # card, button pressed, duration
    session_pattern:   str | None            # 'deck-browser' | 'unsure-throughout' | None  (§3.6)
    scores_raw:        dict[str, int]        # 0-100, None if undefined
    scores_rescaled:   dict[str, float]
    firmness_score:    dict[str, float]
    firmness_latency:  dict[str, float]      # may be empty
    overall_firmness:  float                 # §6.5, population percentile
    top_factor:        str
    top_settled:       bool                  # False while a forced choice is outstanding
    top_source:        str                   # 'outright' | 'latency' | 'picked' | 'provisional'
    label:             str
    label_line2:       str
    flags:             list[str]             # 'broken:FOOD', 'split:POL:B', 'refused:LIVE', ...
    followup_owed:     list[str]
    followup_answers:  list[CardAnswer]      # stored, never merged into `answers`
```

Keep `answers` forever. Every rule in this document was found by re-reading raw answers under a
new rule, and the one thing that has hurt most this week was raw answers that could not be
recovered.

---

# 11. Things that will bite you

- **A single *not for me* is never a refusal.** Two are. Hard pass is.
- **An inner swipe is a preference.** Chasing it with a follow-up gets the same swipe back — the follow-up is answered
  on the same scale. Only a true 50 is worth asking about.
- **An undefined factor is not 50.** It carries no salience. Feeding 50 in gives it the weight of a
  real neutral.
- **The timer is invisible, and nobody is told to be quick.** Either one changes what is measured.
- **A timeout is absence, a Next is doubt.** The first is discarded; the second counts. §3.4.
- **A fast Next is browsing, a slow Next is doubt.** §3.6 tells them apart. Do not treat every
  deferral as uncertainty.
- **A deferred card never lands next to its partner.** Pull the partner forward. §3.3.
- **Latency starts at render-complete and stops at gesture-start.** Anything else measures the
  network or the thumb.
- **Never break a tie with a fixed order.** It was wrong three times in four.
- **A follow-up form knows who it was sent to.** Do not let the answer tell you.
- **Store the card wording with the answer.** Cards get rewritten; a stored answer that points at a
  card by id will be reported under whatever that card says *now*. This corrupted a week of
  per-card analysis on the test forms.
- **The label is written once.** Not on every recompute.
- **Pairs never adjacent.** A and B of the same factor back to back reads as one question asked
  twice — whether the second arrived by adaptive insertion or by a deferral.
- **No number on the progress bar.** The deck length is not known until the last swipe.

---

# 12. Not established

- Every latency rule is an extrapolation from the attitude literature. These cards, this
  population, will have their own confounds. §6.3 is the check.
- The 0.15 latency gap in §7.1, the 12 s timeout in §3.4, the 5 s windows in §3.4, the Next and
  Back multipliers in §3.5 and the ~4 s browser line in §3.6 are **set** — build them as written —
  and marked as starting points because the first 30 app users are where they get *adjusted*.
  Nothing waits on that; testing cannot start without values.
- How often Next, Back and the pause actually fire is unknown. If Next is common and slow, the
  deck is confusing people and that is a card problem before it is a constant problem.
- The Next / Back design (2026-09-15) supersedes an earlier timeout / redo design, and the
  adaptive four-way deck (2026-09-15) supersedes both the 0–5 heart and the fixed deck of
  fourteen. Nothing was built on any of the earlier ones.
- How the deck length actually distributes — how many people land at 10, 14, 20 — is unknown.
- Whether *hard pass* in red gets used where *hate* with a vomit did not is the thing that decides
  whether the refusal floor is back. Check on the first 30.
- The mood threshold has never fired.
- `SCEN` and `HERIT` are visual factors — the look of a place, the age of a place — and cannot be
  tested with words. The form-era readings on them are weak by construction. Judge them on
  images, in the app, not before.
- `NOV` is a night-tuning filter more than a factor. It stays in the vector and can top somebody's
  list — First Timer is a real vibe — but its main job at plan time is choosing between familiar
  and brand-new venues for a person who is otherwise well matched. Decided 2026-09-16.
- Two further uses of latency are logged as directions, not built: the learning layer
  (`DECISIONS.md` 2026-09-12, settled factors leaving the deck) and bend (2026-09-12, three
  levels). Both post-validation. Neither is in this document's scope.
- The refusal prefix in `VIBE_NAMES_V3.md` runs on hard passes alone until the third validation
  check passes; the strong/soft names wait on the fourth. A three-part name will move more on
  retake than the one-word name did — `REMINDERS.md` has the check.

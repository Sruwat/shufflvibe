# Factors V6 — six identity factors, seven preferences, and what the skeleton owns instead

**Supersedes `FACTORS_V5.md`** (2026-09-30). V5 had eight vibe factors and six preferences, and
every vibe factor was a **demand on a venue**. V6 splits that job in two, and the split is the
whole document:

> **The vibe factors are who you are when you go out. The skeleton is what tonight looks like.
> They are different questions, answered by different interactions, and used for different things.**

**And the line between them is harder than earlier drafts had it (corrected 2026-10-01, the user):
the vibe never touches a venue at all.** It is for **matching you to other people**, **blending a
room's chemistry**, and **gating** the app — and nothing else. **Venues come into play only after
the skeleton**, and they are chosen by the drawn shape and the preferences.

Earlier drafts let the identity factors act as rung-1 character discriminators — `TALK` as
register, `AFFIL` and `MOVE` as layout, `FOCUS` as orientation. **That is retired.** It was the
last place the vibe was still doing planning work, and it was doing it invisibly: a user would
have seen a venue chosen partly by cards they swiped on appeal, with no way to know.

`DECISIONS.md` entry 130 has the reasoning. The user's argument for it is the one that settles it:
in a group, the identity factors are **dictated by group dynamics that cannot be predicted from
individual cards** — a group that wants to talk will talk in a nightclub or a restaurant — so using
them to plan was always the weakest link in the engine. Using them to *match* is an honest use of a
noisy signal.

---

# 1. The three kinds of signal

V5 had two. There are three.

| | **identity factors** | **the skeleton** | **observed traits** |
|---|---|---|---|
| how many | 6 | 4 quantities | 3 so far |
| how it is captured | the daily swipe deck | a line the user drags | measured from behaviour |
| measured when | every day | every plan, every join | continuously, silently |
| what it decides | **nothing about the plan** | **everything about the plan** | nothing yet — no home |
| what it is used for | the match score **against other people**; room blend chemistry; which rooms are suggested; **gating** the app; the daily name | the stops, their hour, their energy, their crowd, their order, **and the venue** | — |
| can a user swipe it honestly? | yes | n/a | **no — that is why it is observed** |
| spec | `CHEMISTRY_V4.md`, `VIBE_NAMES_V5.md` | `SKELETON_MERGE_V1.md`, `OUTING_PLAN_ENGINE.md` §15 | none yet |

**Preferences are a fourth thing and always were** — they are one-ended, set once, and they choose
*which venue of the type the skeleton asked for*. They are unchanged by the split except that
`GAMES` joined them.

---

# 2. The six identity factors

| Code | Axis | Low pole (a want) | High pole (a want) | Weight |
|---|---|---|---|---|
| `ENRG` | energy | a calm night | a night that goes hard | 18 |
| `AFFIL` | who you face | the room — meeting people | your own table, your own people | 16 |
| `TALK` | can you hear each other | music you can't talk over | a night you can actually talk | 14 |

> **`TALK` does not split, decided 2026-10-14 (entry 203).** The open question was whether it is a
> fact about the room (can you hear each other) or a fact about the person. **It is the person.**
>
> **The user: "a person with high focus and high talk means they want to have discussions about the
> event they're for, but a person with high focus low talk means they'd rather just have company
> undisturbed while they observe the performance."**
>
> **That reading makes the factor more useful, not less** — and it generalises. **Two factors read
> together say something neither says alone**, which is the chemistry lines' own move pointed at one
> person instead of a room. **Those pairs belong on a profile**, as what somebody reads when they
> scroll past you. Held in `REMINDERS.md` as cross-factor inference lines.
| `FOCUS` | is there a main event | no main event; we are the thing | a gig, a set, a match, a screening | 14 |
| `MOVE` | on your feet | sat down all night | somewhere with a floor | 12 |
| `SPONT` | how the plan happens | booked on Tuesday | decided at nine | 10 |

**The weights now have exactly one job: weighting the match score between two *people* (or a
person and a room's blend).** The naming tie-break was
retired on 2026-09-23 and nothing selects venue types any more. They sum to 84 and the sum does not
matter — only the ratios do.

**`ENRG` means two different things and only one of them is here.** *Personal* `ENRG` — "I am a
high-energy person" — is identity. *Venue* energy — "stop 2 should be loud" — is the skeleton's
vertical axis. Same word, two objects, and conflating them is the easiest mistake to make in the
new architecture.

### 2a. What each one does to a venue: **nothing** (corrected 2026-10-01)

**No identity factor reaches a venue, at any rung.** Not the type, not the character, not the
tie-break. `VENUE_DATABASE_V1.md` §0 states it from the other side and reads none of them.

What the earlier draft had them doing, and where that work actually lives now:

| was going to be | is actually |
|---|---|
| `TALK` as **register** at rung 1 | register is **derived from the venue's own curve** and used to *describe* the venue, not to filter it |
| `AFFIL` + `MOVE` as **layout** at rung 1 | layout is a **character tag** like any other, asked for by the room, not by anyone's cards |
| `FOCUS` as **orientation** | a character tag, plus the clock-anchor flag on the room |
| `ENRG`, `SPONT` | already did nothing at a venue. `ENRG` is the skeleton's; `SPONT` sets the room's **join window** |

**The one exception that is not an exception:** `FOCUS` ≥ 70 still raises the *room's* clock-anchor
flag, which changes **when** a stop happens. That is a property of the room, not a filter on a
venue, and no venue is scored by it.

**And the talk floor is gone** (`CHEMISTRY_V4.md` §2). The physics of masking has not changed; the
justification has. A floor protected someone from a plan the engine **inferred for them**, and
there is no inference left — every stop exists because somebody dragged a line there, and every
joiner sees the plan before joining. `TALK` still makes a loud club score low for a talker while
they are *browsing*. It no longer stops the night being chosen.

### 2b. `FOCUS` and `SPONT` — why these two and not the others

Adopted 2026-09-30 on the user's decision, from a longer list.

**`FOCUS`** is the ingredient nothing in the model previously saw — Collins' mutual focus of
attention, the first requirement of an interaction ritual that works. It is also the axis with the
strongest contagion in `CHEMISTRY_V4.md` (pull 0.80), because gaze-following is reflexive.

**`SPONT`** is a real source of group friction that no other factor touches, and the split is what
made it viable: it was previously rejected because a *venue* cannot be scored on it, and under V6
an identity factor does not need to be.

**Rejected, with the reason kept so nobody re-proposes them:**

| | why not |
|---|---|
| `LEAD` — do you run the night | **it differs from room to room** (the user). With a louder friend you are the passenger; with a quieter cousin you are running it. A single number per person is the wrong shape — so it moved to observed traits (§4) |
| `STAMINA` — are you there till closing | **duration is already the time filter.** Asking it on a card sixty seconds before the user types an end time is asking twice and trusting the worse answer. Also observed (§4) |
| `SHOW` — is tonight documented | not necessary (the user) |
| `POL` — how dressed up | **identifies nobody** — everyone in Delhi dresses up on a Friday. Stays a preference |
| `NOV` — new places | stays a preference, with the soft repeat-avoidance rule |
| indoor / outdoor | a venue attribute, not a person |

---

# 3. The seven preferences

One-ended: **0 is irrelevant, 100 is the whole point, and there is no aversion anywhere.** Set once
at onboarding, edited in the profile, and they choose the exact venue of the type the skeleton asked
for (rung 3 of selection).

| Code | What it asks | Weight |
|---|---|---|
| `FOOD` | how much the food matters | 20 |
| `LIVE` | live music, an act, a set | 18 |
| `POL` | how dressed-up the room is — with a sense: *classy*, *current*, or both | 18 |
| `SCEN` | the look of the place | 16 |
| `NOV` | somewhere new | 14 |
| `HERIT` | somewhere with history | **10 for selection** (was 14, lowered 2026-10-05 — `VENUE_DATABASE_V1.md` §3c); 14 on the profile |
| **`GAMES`** | **something to play — pool, darts, bowling, an arcade** | **12** |

### 3a. `GAMES` moved here, and it is a promotion

As a vibe factor `GAMES` was the weakest thing in the set and V5 said so in its own §2: *"it may
behave nearly one-ended — 'I want games tonight' is a want; 'no games' is mostly indifference."*
That is the definition of a preference. It also dragged a whole clause of chemistry with it —
Sherif's bridging rule, the `split_cap` of 65, the games-pub-not-games-bar distinction — all of
which is now deleted rather than maintained.

As a preference it does the one job it was always good at: it tells the other person something true
about you (the badge is *Always On The Table*), and it tells the fill stage to prefer a venue with
a pool table when everything else is equal.

---

# 4. Observed traits — the third category, with no home yet

Decided as a category on 2026-09-30. These are the things **nobody can swipe honestly, and nobody
has to**, because the app watches them happen.

| | measured from |
|---|---|
| `LEAD` | who hosts, who locks the plan, who redraws the skeleton, who edits somebody else's |
| stamina | the end times this person actually keeps choosing |
| `NOV` revisits | venues appearing in more than one locked plan (already agreed as a soft rule) |
| the personal latency scale | already implemented — `ASSESSMENT_ENGINE.md` §6.2a learns it with use |

The latency scale proves the pattern works; the other three have no storage, no schema and no
consumer. **That is the open item** (`REMINDERS.md`).

---

# 5. What the skeleton owns — the four that left

| V5 vibe factor | now |
|---|---|
| `CROWD` 14 | the **size of the circle** the user enlarges at each stop |
| `ROAM` 14 | the **number of stops** — the count merge in `SKELETON_MERGE_V1.md` §2 |
| `RAMP` 10 | the **order and the peak** — and it needs no rule of its own, because aligning drawings on the clock produces the arc as a side effect (§5 of the merge spec) |
| venue energy | the **vertical axis** of the grid |

**`ROAM`'s split-the-difference clamp is not dead — it moved.** A count is a divisible quantity and
a split still has to be split rather than won, so the rule lives in the merge spec where the counts
are literal stops instead of a 0–100 axis, which is what it always wanted to be.

**`RAMP` is the clean win.** It existed because `ENRG` was doing two jobs — the level and the
trajectory — and the engine hard-coded the trajectory for everyone. A drawn line states both at
once and no arithmetic is needed to recover either.

---

# 6. What this costs, honestly

**The name carries a third less information.** Six factors give 132 possible names against V4's 240;
entropy falls from 7.18 to 6.49 bits (`VIBE_NAMES_V5.md` §5). Not recoverable by tuning.

**Chemistry lost three of its five cross-axis rules** with their axes, and `FOCUS` had to restore
the coupling (`CHEMISTRY_V4.md` §7).

**The vibe assessment now predicts less about the night**, which is the point, but it means the
swipe game has to justify itself on matching alone. If users do not care who they are matched
with, six cards of identity is six cards too many — and that is a product risk the old
architecture hid, because the cards were doing planning work whether or not anyone valued the
matching.

**Two pairs to watch for collapse:** `ENRG` × `MOVE` and `FOCUS` × `TALK`. Correlated factors
shrink the name vocabulary far faster than losing factors does, and if either pair collapses one of
them should leave the naming set even if it stays in the match score.

---

# 7. The venue types and the shape library

`FACTORS_V5.md` §4–§5 stand unchanged and are not reproduced here: the venue types, their scores,
and the shape library. **What changed is who reads them.** The type is now chosen by the supply grid
from `(hour, energy bucket, crowd bucket, radius ring)` — a query against real supply — rather than
by arithmetic over the vibe factors. The types' `TALK`, `AFFIL` and `MOVE` scores are still needed,
but as **rung-1 character discriminators and match-score inputs**, not as targets to hit.

The two types added on 2026-09-23 — `big loud bar` and `match bar` — remain, and `match bar` is now
load-bearing rather than speculative: it is the venue `FOCUS` exists to reach.

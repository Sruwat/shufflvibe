# The gold promotion — crowdsourcing the bands

**The user's design, 2026-10-03.** Costed in `simulations/goldrush.py`.

**This is the best answer to the band problem anyone has proposed**, because it collects the number
at the one moment it is true: a person standing in the room, at that hour, on that day.

---

# 1. The design

1. **Venues whose bands are missing are highlighted in gold**, and **contextually** — driven by the
   time window the user already chose after Play. Search *Deja Brew* having asked for 8–10 and it
   is gold; see it among a stop's options and it is gold; join a room whose plan contains it and it
   is gold.
2. **The reward requires actually going**, through the app: Go here → Lock this, or hosting a room
   with it, or joining one. **It must be in their Active Plan and location must be on.**
3. **On arrival a notification fires** — *"[promotion] active"* — opening a guided capture: one
   screen per shot, **live camera only, no uploads** (wide frame, crowd, bar).
4. **Then the factor-card swipe** — how accurate are these for this venue, right now.
5. **Voucher.**

**The cleverest part, and it should be said out loud:** the gold highlight is **demand steering**.
Every other crowdsourcing scheme collects most where coverage is already best. This one actively
points people at the **gaps**, using a signal the app already has.

---

# 2. Which bands actually need capturing

**The user is right that a Big Chill does not need this.** Six of eleven types need nothing at all —
a flat venue is already described by its type curve.

| type | venues | bands | day-modes | **slots** | |
|---|---|---|---|---|---|
| **club** | 25 | 2 | **1** | **50** | weekend only — a club midweek is shut or empty |
| **big loud bar** | 55 | 3 | 2 | **330** | the widest swing of any type |
| **pub** | 70 | 3 | 2 | **420** | same shape, shallower |
| **lounge / rooftop** | 50 | 3 | 2 | **300** | sunset, evening, late — three rooms, twice over |
| **live room** | 14 | 2 | 2 | **56** | the schedule matters more than the bands |
| match bar | 22 | — | — | — | driven by fixtures. Needs a schedule, not bands |
| buzzy restaurant | 80 | — | — | — | peaks at dinner and the type curve says so |
| table for the night · quiet bar · games · open ground | 100 | — | — | — | flat |

**214 of 416 venues, and 1,156 slots once day-modes are counted.**

**ONE capture per slot (2026-10-03, the user), and the time-box is what makes it safe.**

I had argued for three, because *"one capture is one night — a Tuesday at a Friday venue becomes
the band forever"*. **That risk is already gone in this design.** The slot *is* `(venue, day,
hour-band)` — *"Bohca, Friday, 20:00–22:00"* — and **the capture must happen inside that window or
it releases.** A capture cannot land in the wrong slot.

What remains is only the variation between one Friday-at-eight and the next at the same venue,
which is far smaller than the day-and-hour variation three captures were guarding against.

| | mean error | against the type curve |
|---|---|---|
| **no capture — the type curve** | **8.2** | — |
| **one capture** | **5.8** | **better** |
| three captures, median | 3.9 | better still |
| one capture, a volatile venue | 8.6 | slightly worse |

**Three is better than one. That is not the question.** The question is **whether one capture
everywhere beats three captures on a sixth of the database** — because that is what the same money
buys. **It does**, because the alternative to a noisy capture is not a better capture. **It is the
type curve**, which is worse than one capture and applies to every slot we skip.

---

# 3. What ₹5 lakh buys, at one capture per slot

| coverage | slots | **per capture** | |
|---|---|---|---|
| every slot — 214 venues, both day-modes | 1,156 | ₹433 | full coverage, modest reward |
| **weekend slots, all 214 venues** | **578** | **₹865** | **the answer** |
| the top 35 venues, both day-modes | 189 | ₹2,646 | deep but narrow |
| the top 35, weekend only | 103 | ₹4,854 | too narrow for this budget |

### Weekend slots across all 214 venues, at ₹865

**₹865 is a reward worth gambling for**, which is the entire point of the mechanic — a modest one
would not carry the advertising.

**Every venue that needs bands gets covered where it matters.** Thursday to Sunday is where the
plans are; a Tuesday at a club is mostly a closed door.

**Weekday slots keep the type curve**, which is what they would have had anyway, and they are the
least-queried slots in the database.

**And it leaves the top-35 weekday slots as an obvious phase two** if the first round lands.

---

# 4. One person per slot — and what the gamble actually fixes

**The user, 2026-10-03: one person sees it, completes it inside the window, and is paid. Fail
verification and they retry. Run out of time and it releases to the next person who browses, hosts
or joins.** *"I want to see if I'm lucky enough to get this."*

**It is good advertising, and it fixes two real problems the three-capture version had.**

**The promise becomes clean.** Three captures meant *"you might be third and get nothing."* One
capture plus a retry means **if you got the slot, you get paid** — provided you do it properly.
That is a promise worth advertising; the previous one was not.

**And failing verification stops being a punishment.** With three captures, failing cost you a slot
somebody else would take. With one and a retry, **failing costs thirty seconds** — which is exactly
the right stake, because the check will be wrong **1.4%** of the time (§4b) and that error now costs
nobody anything.

### Mechanics

**Reserve on arrival, not on sight.** The slot locks when the notification fires — they are at the
venue. Locking when somebody merely *sees* gold lets people who never go hold slots.

**Release at the end of the window, not on a timer.** The slot is *Friday 20:00–22:00*; at 22:00 it
is gone whether or not anyone completed it, and it becomes gold again for the next person. **The
window is the timer.**

**And tell them the window.** *"You have until 22:00"* on the notification. **The release is the
only part of this that can feel unfair, and it only feels unfair unannounced.**

---

# 4a. One task, not two — and the swipe is compulsory

**The user, 2026-10-03: make the swipes compulsory. Photos first, then swipes.**

**Correct, and it resolves the split I proposed rather than adopting it.** If both are required there
is no split — it is **one task and one payment**, and the question of which half is worth more
disappears.

**The ordering is right too, for a reason worth stating: the photos get the user looking.** Framing a
wide shot, a crowd shot and the bar makes somebody *see the room* before being asked to rate it.
Swiping first would be rating a room you walked into ninety seconds ago.

> **₹865 for the complete capture — photos then swipes — paid on verification.**
> **₹1,300 for the 24:00–02:00 band**, which nobody is awake to capture and which clubs are defined by.

**And it gives the photos their proper job.** They are no longer the data and no longer only proof
of presence — **they are the instrument that verifies the swipes.** That is a better job than either.

---

# 4b. Verification — and the asymmetry that sets the threshold

**The user: if the swipes do not match the photos even a little, assume mindless swiping.** The
mechanism exists because the fixed-rules program already measures people-fill, brightness and motion
from a photo — so a claimed *crowd 9* against a frame reading 1 is a contradiction the system can
see.

**The threshold is set by an asymmetry, not by accuracy** (`simulations/verify.py`). Paying ₹865 for
one bad capture costs ₹865. **Telling an honest user they cheated costs that user and everyone they
tell.**

| gap | misses needed | honest wrongly failed | careless caught |
|---|---|---|---|
| 4 | 2 | **8.9%** | 72% |
| **5** | **2** | **1.4%** | **48%** |
| 5 | 3 | 0.1% | 18% |
| 6 | 3 | 0.0% | 7% |

> **A capture fails only when two or more factors are off by five or more.** Catches **48%** of
> careless swiping, wrongly fails **1.4%** of honest users.

**Letting half of careless captures through is the right trade**, because **the retry catches what the
check does not** — a user who fails is asked to do it again, and the second attempt is almost always
the honest one. **Tune the false-accusation rate first.**

**And never phrase it as an accusation.** *"We couldn't verify this one — try again at your next
stop"* costs nothing and keeps the user. *"You didn't complete this honestly"* is unrecoverable and
will sometimes be wrong.

### The warning message is worth more than the algorithm

> *"Make sure you carefully complete this, since we'll be verifying whether the results you provide
> are real."*

**This improves the data whether or not the check behind it works.** Telling people an answer will
be checked is one of the most reliable effects there is — it moves them from satisficing to actually
looking.

**So show it before the photos, not between the photos and the swipes.** The user needs to know
while they are still looking at the room, not after they have stopped.

---

# 5. Five risks

**Selection bias, again.** Captures come from people who go out, when they go out, to venues they
already like. **The gold highlight is the mitigation** — it is the one mechanism in any of these
documents that actively steers collection toward the gaps.

**Gaming.** Somebody photographs an empty corner to finish fast. Live-only capture and a GPS fence
are already in the design. **With one capture a slot there is no cross-check to fall
back on**, which makes §4b load-bearing rather than a backstop — and is the real price of dropping
to one.

**The reward buying the wrong night.** People going somewhere they would not have gone, for ₹865.
**The design already requires the venue to be in a plan they built** — and a nudge toward a place
they would not have tried is half of what the app is for.

**The capture interrupting the evening.** Five screens of photography at 23:40 is a real cost.
**Under 60 seconds, and the notification never fires twice.**

**Bands go stale — and the user's answer is better than mine.** I proposed the gold returning to
anything older than six months, making this a permanent refresh mechanism. **He pointed out that by
the time bands go stale we should have partnership agreements with exactly these venues** — and he
is right, because **the 35 venues this programme targets are, by construction, the 35 most worth
partnering with.** They are the ones whose data the engine queries most and whose character the type
curve predicts worst.

**So the promotion is a bridge, not a permanent feature.** It buys a working database until
partnerships supply the same data directly and for free. **Still stamp every band with its capture
date** — not to re-run the promotion, but so that a band's age is visible when deciding which venue
to approach next. **The staleness clock becomes the partnership priority list.**

---

# 6. What this does to the MVP

**It does not change `MVP_INSTRUCTIONS.md`.** The MVP still offers venue lists rather than
generating plans, because bands will not exist on day one.

**But it is how the MVP earns its way out of that**, and it should run from launch. Every capture
moves one slot from *type curve* to *measured*, and when the top 35 are filled, **time-based plans
become honest for the venues that matter** — which is the first feature the deferred list gets back.

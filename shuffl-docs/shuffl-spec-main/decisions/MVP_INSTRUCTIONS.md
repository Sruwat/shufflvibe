# MVP instructions — what ships first, what waits, and why

**Decided 2026-10-03 (the user). This document outranks the others for scope.** Where a spec
describes something richer than what is below, the spec is the destination and this is the release.

> ## Find people like you, and places you like.
>
> **That sentence is the MVP.** Everything that does not serve it waits.

---

# 1. The decision that shapes everything else

**We launch with no partner agreements.** No venue has signed anything, so we have no schedules, no
reservations, no capacity, and no venue-supplied media.

**So the MVP does not promise accuracy about what a venue is like at a given hour, because it
cannot.** Every cut below follows from refusing to promise what we cannot keep.

**What we do have**, and it is enough: the factor scores from the lexicon method, images as
supporting evidence, the venue's own descriptions, and opening hours.

**And one thing that changes over the life of the MVP rather than being fixed at launch: the gold
promotion** (§2.6) collects the missing band data from users as they go out, so the app the first
cohort uses is measurably worse than the one the third cohort uses. **That is the intended shape.**

---

# 2. What ships

### 2.1 The vibe assessment — unchanged, and now the point of the app

The six identity factors, the adaptive swipe deck, latency, the daily name. **This is no longer a
supporting feature. It is the product**, because *find people like you* is half the sentence.

### 2.2 The skeleton — drawn, but it no longer generates a plan

**The user draws the shape of their night as specified.** Stops, energy, crowd.

**And then the app does not build the outing. It offers.** For each stop, a list of **5–10 venues
whose factor scores match that stop's shape and which are open at that hour**. The user picks one,
moves to the next stop, and builds their own night.

**In a room, the host picks (2026-10-05).** The merged skeleton gives the stops and the host chooses the
venue at each one; everyone else sees the stop list read-only with the host's choice marked. A vote
turns every stop into a negotiation on a night people joined to stop negotiating, and first-to-tap
rewards whoever is looking at their phone. **The host already carries the room's three filters, so
this is the same authority applied to the same object rather than a new one.**

**This is the single biggest change and it is the right one.** The app says *"here are eight places
that feel like what you drew"* instead of *"this is your 11pm"* — which is a claim we cannot
support without bands, and a claim nobody asked us to make.

**What it needs:** venue factor scores (have), **opening and closing hours (must add)**, and the
shape-distance ranking. Nothing else.

### 2.3 Venues — the full list, not a seed radius

**All ~360 NCR venues passing admission**, not 40–60 in one area. The earlier seed-radius argument
was about making the *automatic* plan honest; **since the app no longer generates a plan, breadth
beats depth.** A user picking from a list wants options, and a thin list in one neighbourhood is a
worse product than a broad list with coarse scores.

### 2.4 Rooms, joining, and the social half

**Host, Join, the room player, capsules, the group chat, profiles, friends, messages** — all of it.
**This is the other half of the sentence and it is the half we can actually deliver**, because it
depends on users rather than on venue data.

### 2.5 Vibe chemistry on a profile — new, and the thing to show off

**See §4.**

---

### 2.6 The gold promotion — shipping, and how the MVP earns its way forward

**`GOLD_PROMOTION_V1.md` runs from launch.** It is not a growth gimmick bolted on — it is **the
mechanism by which the MVP stops being a list and becomes a planner**, and it should be built with
the first release rather than after it.

**What the user sees.**

1. **Some venues are gold.** Contextually — driven by the time window they already chose after
   Play. A gold venue appears gold in search, among a stop's options, and inside a room's plan.
2. **Gold means a reward is available there, tonight, in this window — and only to them.** One
   person per slot. *"2 hours left · ₹865"*.
3. **They have to actually go**, through the app: it must be in their Active Plan with location on.
4. **On arrival the capture opens**, headed by the line that does most of the work:
   > *"Make sure you complete this carefully — we'll be verifying whether what you give us is real."*
5. **Photos first**, live camera only — wide frame, crowd, bar. **Then the swipes**, which are
   compulsory and are the actual data.
6. **Paid on verification.** Fail and they are asked to do it again, not accused. **"You have until
   22:00"** is on the notification from the start.

**Why it belongs in the MVP and not after it.**

**It is the only feature that makes the app better the more it is used, in a way the user can see.**
Every capture moves one slot from *estimated by its venue type* to *measured* — and when the slots
a venue is queried on are filled, **time-based plans become honest for that venue**, which is the
first thing the deferred list gets back.

**It also gives the MVP a reason to exist on a Tuesday.** The app's core loop is weekly at best;
the gamble — *am I lucky enough to get this one* — is a reason to open it and look.

**And it is the cheapest venue research anybody could run.** ₹5 lakh covers **the weekend slots of
all 214 venues that need them**, collected by people who were going out anyway, at the exact moment
the number is true.

**What it must not become.** A scheme people join for the money rather than the night. **The design
already guards this** — the venue has to be in a plan they built — and the copy should never lead
with the reward. **Gold is a thing you notice while planning a night, not a reason to plan one.**

---

# 3. What waits

| | why |
|---|---|
| **Bands** (hour-and-day factor scores) | venues carry **one** set of scores at MVP — but see §2.6, they are being collected from launch |
| **Slots and schedules** | the schedule lives on venue Instagram and nowhere machine-readable (`VENUE_DATABASE_V1.md` §2a1) |
| **Reservations** | needs partner agreements |
| **App-generated outing plans** | the whole point of §2.2 — we do not generate, we offer |
| **Time-based plans** (a stop anchored to an hour) | the same reason. Opening hours filter; nothing is scheduled |
| **Clock-anchored stops, `FOCUS`'s clock, programme-led `HERIT`** | all need the schedule |
| **Heatmaps** | **deferred to a user threshold, not removed** — see §3a. At low volume they are either empty or they identify individuals, which the privacy rules already forbid |
| **Dish and drink recommendations** | needs menus from partners |
| **"What's popping tonight"** | needs events |
| **Popularity floor / budget release** | keep the budget filter; the floor needs popularity data we can add later |

**Nothing is deleted.** Everything above is deferred and every spec stays as written — they are
the destination, not the release.

### 3a. Heatmaps — the threshold that turns them on

**Heatmaps are gated on having enough users to render them honestly.** The existing privacy rule in
`VIEW_FLOW.md` already sets the bar: an area renders only once **at least 20 distinct users** are
in it, data shows at neighbourhood level and never at venue level, and it is delayed 30–60 minutes
rather than live.

**So the switch defines itself: turn heatmaps on when the median active area clears 20 distinct
users on a normal Friday.** Not a date and not a headcount — the same number the privacy rule
already needs, measured rather than guessed.

**Below that threshold a heatmap is one of two bad things:** empty, which makes the app look dead,
or populated by so few people that an area identifies them, which the rule forbids. **Both failures
disappear at the same moment, which is why one threshold governs both.**

**Collect for it from day one** — locked plans already record venues and areas — so when the number
arrives the feature is a switch rather than a build.

---

# 4. Vibe chemistry on a profile — the MVP's distinctive feature

**The user, 2026-10-03: "include a list of the ways vibes interact with one another in terms of
chemistry, so we can give users insights other than just a vibe match score, by showing how the
vibe of the user they're viewing and their own vibe would get along and in what way."**

Prototyped in `simulations/pairchem.py`.

### What it is

**Open somebody's profile and you see, beneath the match percentage, what the two of you would
actually be like on a night out** — a headline and three or four lines, generated by running
`CHEMISTRY_V4`'s axis rules at n = 2.

> **ZOYA · 80% match · YOU WILL TRADE OFF**
> `FOCUS` — You will both be at the front for whatever is on.
> `ENRG` — You set the pace and they will come along.
> `AFFIL` — They will be the one talking to strangers.
> `TALK` — You will start the conversation and they will join it.

### The headlines

| | fires when |
|---|---|
| **SAME WAVELENGTH** | three or more of the top factors are aligned on the same pole |
| **TWO DIFFERENT NIGHTS** | two or more splitting axes are firmly opposed |
| **ALIGNED, WITH ONE SPLIT** | mostly together, one real difference |
| **YOU WILL CARRY THIS ONE** | three or more top factors led by the viewer, none by the other |
| **THEY WILL CARRY THIS ONE** | the mirror |
| **YOU WILL TRADE OFF** | both lead on something |
| **NOBODY IS PUSHING** | four or more factors flat on both sides |
| **PUSH AND PULL** | everything else |

The per-axis lines are a fixed table of nine readings per factor — one for each combination of
*(your pole, their pole)* across high / middle / low. **Fifty-four sentences, written once.** The
**full table is written as copy in `CHEMISTRY_LINES_V1.md`**, with the rules it follows and three notes for whoever edits it.

### Why it earns its place

**A percentage says how alike you are. The read says what would happen.** Those are different, and
the second is the reason to open a profile at all.

The worked case: **Ishaan matches Zoya 80% and Dev 71% — close numbers, nothing alike as nights.**
With Zoya the read has content on both sides. **With Dev, every line in the top four starts with
*you*** — he sits in the middle on all six factors, so nothing fires. That is not a bad match; **it
is a night one person has to carry**, and the percentage cannot say so.

### Where it appears

- **View Profile** — under the match percentage. The primary home.
- **The room player** — one line, for the host: *"you and the host will trade off."*
- **Friend requests and join requests** — the host sees the read, not only the grade.

---

# 5. What the MVP is actually testing

Three questions, in order of how much they matter:

1. **Do people care who they are matched with?** The entire identity half rests on this and it has
   never been tested. **§4 is the sharpest test of it** — if the chemistry read gets opened, screenshotted
   and argued with, the answer is yes.
2. **Is the swipe game worth playing daily?** Nine cards, every day, for a name and a match.
3. **Does drawing a skeleton beat a list of filters?** The skeleton survives into the MVP even
   though it no longer generates a plan, because *the shape of the night* is a better question than
   *what kind of bar.* If users do not get it, that is worth knowing before bands are built.
4. **Will people complete a capture?** §2.6 assumes somebody at a bar will give ninety seconds to
   photographs and swipes for ₹865. **If they will not, the band problem has no cheap solution**
   and the answer is partnerships, slower and sooner than planned. **This is the test with the
   clearest pass mark**: 578 slots, and we will know inside a month whether they are filling.

**Venue accuracy is deliberately not on this list.** We are not testing it because we are not
claiming it.

---

# 6. What the MVP must still get right

- **Opening and closing hours on every venue.** The one time field that cannot wait — a list
  containing closed venues is the fastest way to lose trust.
- **The factor scores have to be defensible**, because the user sees the list and judges it. Eight
  venues that feel like the drawn shape is the whole promise.
- **Nothing may imply hour-accuracy.** No "your 11pm", no "this is when it peaks". The copy says
  *feels like what you drew* and *open then*, and nothing more.
- **The capture must take under sixty seconds.** It happens at 23:40 in a bar somebody came to
  enjoy. Five slow screens is a cost to their evening and the reason they do not do a second one.
- **The verification must never accuse.** *"We couldn't verify this one — try again at your next
  stop."* It will be wrong 1.4% of the time (`GOLD_PROMOTION_V1.md` §4b), and with one capture per
  slot it is the **only** check on the data, so it is both load-bearing and fallible.
- **The chemistry lines must read as written by a person.** Fifty-four sentences carry the
  distinctive feature of the app; they are worth a proper copy pass.

# The skeleton merge v1 — how several drawn lines in one room become one plan

**Status: design, 2026-09-30. Prototyped (`simulations/skelmerge.py`).**

Since the architectural split, **the plan comes from the skeleton and from nothing else**. A room
has more than one skeleton in it — co-hosts, a group chat, a joiner who drew before browsing — and
the plan needs one. This document is that rule. It is the piece `CHEMISTRY_V4.md` §0 deliberately
does not contain.

**The hard part is not contagion. It is alignment.** You cannot average stop 2 of a three-stop
night with stop 2 of a two-stop night, because they are at different times of the evening. Every
other question here follows from how that one is answered.

---

# 1. The precondition — one window, or there is nothing to merge

**Distance, time and budget are the room's, not the person's.** Whoever opens the plan — the host,
or whoever hit Play first in a group chat — sets them, and everyone else draws inside them.

This is not a convenience. Two skeletons drawn over different windows cannot be merged without
inventing a window neither person chose. And it matches what groups actually do: **people agree
when they are going out before they argue about what they are doing.**

A member who disagrees with the window does not get a second window. They get an affordance to
**propose a change**, which re-opens the filters for the room and invalidates every drawing
(§7). That is deliberate friction — changing the window changes what everyone drew.

**Time is a start and an end**, so the window has a length `L`, and `L` is a hard constraint on
everything below.

---

# 2. Stage 1 — the stop count: a divisible quantity is split, never won

The stop count is what `ROAM` used to be, and it carries `ROAM`'s one non-contagion rule with it:

> **Nobody who drew a different number gets their own number back.**

This is the user's correction of 2026-09-23, moved here from `CHEMISTRY_V3.md` §7 and applied to
literal stops instead of a 0–100 axis, which is what it always wanted to be.

```python
COUNT_PULL = 0.50
SIZE_CEILING = {2: 5, 3: 4, 4: 4, 5: 3}     # Steiner: getting five people out of a bar is not linear

def merge_count(drawings, window_len):
    ns = [d.n for d in drawings]
    lo, hi, mean = min(ns), max(ns), sum(ns) / len(ns)
    ceiling = min(max(1, int(window_len // 1.5)),            # ~90 minutes a stop
                  SIZE_CEILING.get(len(drawings), 3))
    if lo == hi:
        return min(lo, ceiling)
    # the influence-weighted compromise, exactly as CHEMISTRY_V4 section 0.3
    share = impact(side_above_mean) / (impact(side_above_mean) + impact(side_below_mean))
    raw   = mean + COUNT_PULL * share * ((hi if leads_high else lo) - mean)
    n     = round_to_nearest(raw, ties_toward=mean)           # a tie is not a windfall for the roamer
    if hi - lo >= 2:
        n = clamp(n, lo + 1, hi - 1)                          # the split-the-difference clamp
    return min(n, ceiling)
```

| drawn counts | result | |
|---|---|---|
| 1, 4 | **3** | the user's original case — neither gets their own number |
| 1, 1, 4 | **2** | the majority sets it, and the roamer still gets a move |
| 3, 3, 1 | **2** | |
| 1, 5 | **3** | the tie at 3.50 goes toward the mean, not up |
| 2, 3 | **3** | one apart, so the clamp never fires |
| 2, 2, 2 | **2** | unanimous |
| **3, 3, 3, 1** | **2** | **the known flaw — see below** |

**Steiner belongs on the ceiling, not on the pull.** `CHEMISTRY_V3.md` §7 damped `ROAM`'s pull by
`2/n`, which made bigger groups stick near their own mean — that is not a coordination cost, it is
just a weaker rule. The real coordination cost is that **a group of five does not do five stops**,
so it caps the count. Applying it in both places was double-counting.

### 2a. The known flaw, named rather than buried

**Three people drew 3 stops, one drew 1, and the room gets 2.** The clamp forbids 3 because
somebody drew 1, and a three-to-one majority loses a stop to a single dissenter. That is the
largest single-person veto anywhere in the engine.

It is a deliberate consequence of the principle, not an oversight: on the stop count, **fairness
overrides influence**, because being overruled here means physically being dragged somewhere,
which is not true of any other axis. The symmetric reading of the user's rule — *a person who wants
four stops should not have to deal with one* — is that a person who wants one should not have to
deal with three.

**But it is the rule in this document most likely to be wrong**, and the failure case to watch is
exactly that one: a clear majority with one holdout. If real rooms hate it, the fix is to let the
clamp fire only when the dissenting side holds at least a third of the influence, and the reason it
is not written that way now is that a third is a number with nothing behind it.

---

# 3. Stage 2 — alignment: **a stop is a time, not an index**

Every drawing is resampled onto the shared window's clock before anything is averaged.

- Person *i* drew `n_i` stops over the window, so their stop *k* covers
  `[t0 + k·L/n_i, t0 + (k+1)·L/n_i]`.
- The merged plan has `N` slots, so slot *j* covers `[t0 + j·L/N, t0 + (j+1)·L/N]`.
- For slot *j*, read each person's drawing at the slot's **midpoint**.

```
window 20:00 – 02:00,  merged to 3 slots

Aarav drew 3:   [45,60]        [70,75]        [88,85]
Nitya drew 2:   [40,55] ...................  [52,62] ......
merged slots:   20:00-22:00    22:00-00:00    00:00-02:00
                   42/58          65/70          79/76
```

Nitya's first stop spans two merged slots, so its value is read twice — and that is correct in
clock terms: she asked for that energy for the first half of the night, which is two of the three
slots.

**Midpoint sampling, not overlap-averaging.** Averaging a person's drawing across the slot
boundary would soften their own position before the merge even starts, and a firm position holding
is the whole point. Midpoint keeps the drawn extremes intact.

---

# 4. Stage 3 — contagion per slot, on drawn values

For each slot, `CHEMISTRY_V4.md` §0.3 runs on the resampled numbers. Energy uses `pull` 0.75 with
the low pole discounted to 0.55; crowd uses `pull` 0.25 symmetric. **This is the user's correction
of 2026-09-25 honoured exactly: contagion is about the people who will be in the room, so drawn
intentions catch the same way swiped ones do.**

### 4a. The firmness of a drawn position — the multiplier that was blank

`REMINDERS.md` has carried *"a drawn position is firmer than a swiped one, and by how much is
unset"* for a week. It is not a multiplier. It is one row of the ladder:

| value | swiped strength | **drawn strength** |
|---|---|---|
| 0–20 / 80–100 | 1.00 | **1.00** |
| 21–30 / 70–79 | 0.50, or 0.75 if fast | **0.75** — a drag is always deliberate; there is no latency to read |
| **31–69** | **0.00** | **0.25** |

**The last row is the whole of it. A swiped 50 means "this card did nothing for me". A drawn 50
means "I want this stop at exactly medium".** The skeleton has no true neutrals, because nothing
on it happens by accident. That, and not a blanket multiplier, is what "firmer" amounts to.

### 4b. The consequence, which runs the other way from the phrase

Over 4,000 random rooms, the level's mean distance from the plain mean:

| | |
|---|---|
| drawn strengths (no true neutrals) | **6.88 points** |
| swiped strengths (neutrals at 0.00) | **11.66 points** |

**Drawn rooms move less, not more.** Per person a drawn position is firmer; but a room full of
firmer positions is a room that **compromises more**, because the moderates stop being bystanders
and start counting against the one person at an extreme. One loud voice carries a swiped room;
it does not carry a drawn one.

This is the right direction — a plan everyone drew should land nearer the middle of what everyone
drew — but it is the opposite of what the phrase in `REMINDERS.md` implied, so it is worth stating
before somebody "fixes" it.

---

# 5. Stage 4 — the arc: **a shape is not a quantity**

The order and the peak come out of §3 for free. Two people's arcs are already functions of time,
so the blended curve peaks wherever the blend peaks. **`RAMP` needs no merge rule at all** —
time-alignment produces the arc as a side effect, which is the cleanest thing about this design.

Except when the arcs are opposed.

> One person builds 35 → 90. One front-loads 88 → 30. The average is flat at ~60: **a night
> neither of them drew.**

Half of a rising night and half of a falling night is not a compromise. So:

```python
OPPOSED, AMPLITUDE = -0.50, 20

# if two drawings each span at least AMPLITUDE and correlate below OPPOSED,
# do not average. Take the whole shape - energy AND crowd - from the owner:
owner = argmax(amplitude(person) * total_drawn_strength(person))
```

**Both axes, from the same person.** Taking energy from one drawing and crowd from the average
produces a third shape nobody drew — the exact failure the rule exists to prevent. A shape is one
object.

| | result |
|---|---|
| builds 35→90 **vs** front-loads 88→30 (*r* = −1.00) | the whole shape is taken from the person with more firm drawn points |
| builds 35→90 **vs** drifts 62→48 (amplitude 14) | **averaged** — a drift is not an arc |

### 5a. And here the app should ask, not decide

This is the harshest rule in the document: one person's night is discarded whole. That is a signal,
not an outcome. **Two opposed arcs mean these two people want different nights, and no arithmetic
fixes that.** The right product response is to offer **two rooms instead of one plan**, and the
merge should surface the flag rather than quietly resolve it.

The consolation for the person who lost the arc is real but small: their **preferences** are still
served at rung 3 of venue selection, which is untouched by any of this.

---

# 6. Stage 5 — who is counted

**Drawers only. There is no inference from cards, ever.**

In a room of four where two have drawn, the plan is those two people's shape, and the card says so:
*"this is Aarav and Nitya's shape — you haven't drawn yet"*, with a button to draw and re-merge.

Inferring a non-drawer's skeleton from their vibe factors is precisely the inference the
architecture removed, and it would reintroduce it at the one point where it would be least visible.

**So if nobody draws, there is no plan** — which is exactly what the blurred SHUFFL screen in
`VIEW_FLOW.md` already specifies. The two rules agree, and neither was written for the other.

---

# 7. Stage 6 — the joiner, and when the merge re-runs

| | |
|---|---|
| **open room** (not locked) | the joiner is a member: **re-merge**. Their `disturbance` (`CHEMISTRY_V4.md` §8.3) is computable before they commit, so the join card can say *"you would barely change this room"* |
| **frozen room** (hosted, plan locked) | the skeleton does **not** change. The joiner's drawing is used only for `fit` — how well this plan serves them — as `OUTING_PLAN_ENGINE.md` §13.6.3 v5 already specifies with its counterfactual |
| **the window changes** | every drawing is invalidated and everyone redraws. Nothing else in the room is discarded |
| **a member leaves** | re-merge, and if the plan is locked, leave it alone and note it |

**The merge is idempotent on a stable membership** and must be, because it runs on every join,
every leave and every redraw. Log every `(drawn skeleton, merged result)` pair — that is the data
that replaces every constant in this document.

---

# 8. The output contract

```python
merged = {
  'window':  (start, end),
  'stops': [ { 'slot': 1, 'clock': (20.0, 22.0), 'energy': 42, 'crowd': 58,
               'sources': {'Aarav': (45, 60), 'Nitya': (40, 55)} }, ... ],
  'arc':     'blended' | 'taken whole from <name>',
  'counted': ['Aarav', 'Nitya'],          # drawers only
  'absent':  ['Zoya'],                    # members who have not drawn
  'notes':   [ ... ],                     # every line here is shown on the card
}
```

**Every stop carries its provenance**, because the room player already shows a per-person line per
stop and the best version of that line is now *"this is your line"*. Nothing else in the app can
say that.

`(energy, crowd)` per slot plus the hour is exactly the key the supply grid takes
(`supplygrid.py`), so the merged skeleton drops straight into venue selection with no adapter.

---

# 9. What is mine

| | direction | magnitude |
|---|---|---|
| align on the clock, not the index | **forced** — there is no other coherent option | — |
| a count is split, not won | **the user's**, 2026-09-23 | `COUNT_PULL` 0.50 is mine |
| ties round toward the mean | mine | — |
| Steiner on the ceiling, not the pull | mine — it was double-counted before | `SIZE_CEILING` is mine |
| the skeleton has no true neutrals | mine | 0.25 is `NEUTRAL_W`, reused |
| midpoint sampling over overlap-averaging | mine | — |
| a shape is not a quantity | mine | `OPPOSED` −0.50 and `AMPLITUDE` 20 are both arbitrary |
| drawers only, no inference | **follows from the architecture** | — |

**The three numbers to distrust first:** `OPPOSED` −0.50 and `AMPLITUDE` 20, which decide when a
person's whole night is discarded and rest on nothing; and `SIZE_CEILING`, which is a guess about
Delhi that a week of real plans would settle.

**And the rule to watch first is §2a** — the three-to-one case.

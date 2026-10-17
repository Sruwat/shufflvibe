# Profiles V1 — going-out personality as rules, not as a type library

**Status: adopted 2026-09-23, prototyped in `profiles.py` and `readings.py`. Every rule and every
magnitude is judgement, to be validated against real rooms.** This is a layer *on top of*
`OUTING_PLAN_ENGINE.md` §14.3's readings, never a replacement for them.

> **2026-10-14.** `ROAM` appears eight times below and **is not a factor** — it left the deck on 2026-09-30 and became the skeleton's stop count (`FACTORS_V6.md`). The rules here read against **six identity factors**. Everything else stands.

---

# 1. The problem it solves

The readings are computed **one axis at a time** and combined additively —
`score = Σ weight × met(reading)`. So the engine is structurally incapable of saying *this
combination means something the parts do not*. It also, by entry 118's rule, issues **no reading
at all** on an axis nobody has a position on — correct, but it leaves a silence that a person's
other answers often fill obviously.

Run on the current engine, everything unmentioned held at 50:

| room | what the engine produced before | what is wrong |
|---|---|---|
| `ENRG` 15, `TALK` 88 | **two stops**: haveli restaurant → quiet restaurant | three people who want a long calm conversation get **moved to a second restaurant** halfway through, because nobody stated a `ROAM` position and the default is two stops |
| `ENRG` 88, `TALK` 85 | **bowling alley → arcade bar** | two games venues for a room where **nobody mentioned games** |
| `ENRG` 15, `CROWD` 15, `AFFIL` 12 | **Piano Man → warehouse** | a calm, near-empty place to meet people, answered with a gig and then a club |

Nobody in any of those rooms said anything false. The engine simply had nothing to say about the
axes they left blank, and the defaults filled them badly.

---

# 2. Rules, not types — and why that is not a small distinction

The obvious version of this feature is a **library of going-out personalities**, and this project
has already built one and thrown it away: the 42-vibe library died because three of four real
testers sat **121 to 213** away from every vibe in it, against a median 110 *between* vibes
(`DECISIONS.md`, 2026-09-13). The external evidence says the same thing at scale. Gerlach et al.
(2018) ran 1.5M people and found **four** replicable personality types; a published reply showed
only about **42%** of people could be placed in any of them.

**A library has holes by construction. A rule does not.** If the pattern is not there, nothing
fires, and the plan falls back to the axis readings — which already degrade gracefully. This is
the **person-centred** approach used the way its own literature recommends: as a *complement* to
the variable-centred one, not a rival (Bergman & Magnusson; the HEXACO latent-profile work; the
2025 integration paper).

---

# 3. What a rule is

A rule reads the **shape** of one member's profile — two or three axes at once — and infers a want
on an axis they said nothing about.

```python
HIGH, LOW = 70, 30                       # the same poles the chemistry uses
('The Long Table', lambda m: lo(m,'ENRG') and hi(m,'TALK'), [('ROAM','low'), ('CROWD','low')])
```

## 3.1 The six

| Rule | Fires on | Infers | The reason, in a line |
|---|---|---|---|
| **The Long Table** | `ENRG` low + `TALK` high | `ROAM` low, `CROWD` low | a calm night that is all conversation wants one table, not three rooms |
| **Loud and Social** | `ENRG` high + `TALK` high | `CROWD` high, `GAMES` low | loud *and* talking is a packed bar, not a games night |
| **Lose Yourself** | `ENRG` high + `TALK` low + `MOVE` high | `CROWD` high, `RAMP` high | energy with no talk and a floor peaks at the end, in a full room |
| **Settled In** | `AFFIL` high + `GAMES` high | `ROAM` low | our own people with something to play settle in |
| **Working the Room** | `AFFIL` low + `CROWD` high | `ROAM` high | meeting people in full rooms takes more than one room |
| **Quiet Company** | `ENRG` low + `CROWD` low + `AFFIL` low | `TALK` high | you cannot meet anyone somewhere you cannot hear them |

Six is a starting set, chosen because each is a pattern a Delhi person would recognise and each
fills a silence the axes leave often. **Add rules from observed failures, never from intuition
alone**, and retire any that never change a plan.

## 3.2 The three guards

**1. An inference only ever speaks where the axis is silent.** Silent means: nobody in the room
is off the neutral band on that axis, *and* the axis issued no reading of its own. An inference
can therefore never contradict, override or outweigh something a person actually swiped. This is
the same principle as entry 118 — it fills the silence that rule created, and nothing else.

**2. It is discounted, twice.** The weight is `0.6 × axis weight × the share of the room whose
profile fires it`. So *The Long Table* firing for one member of four carries 0.6 × 14 × 0.25 =
2.1, against a stated `CROWD` want's 14. A stated want always wins.

**3. Every firing is logged** — rule, who it matched, the axis, the pole, and whether the plan
changed because of it. These are assertions the model is making on the user's behalf; they are
validated against real rooms, not believed.

## 3.3 Night-level axes move differently

`ROAM` and `RAMP` are one number for the whole night, so an inference cannot be a *reading* — it
moves the number, and it moves it **by the share of the room that fires it**:

```python
value = 50 + (target − 50) × share          # target is 25 for 'low', 75 for 'high'
```

One member of four inferring `ROAM` low gives 43.75 — still two stops. Three of three gives 25 —
one stop. **One person's profile cannot make a room of four settle in one place**, which is the
first thing that went wrong when this was built without the share term.

---

# 4. What it does to the three broken rooms

| room | before | after | the rule that fired |
|---|---|---|---|
| `ENRG` 15, `TALK` 88 | haveli → quiet restaurant (**2 stops**) | **haveli restaurant, one stop, all night** | The Long Table → `ROAM` low, `CROWD` low |
| `ENRG` 88, `TALK` 85 | bowling alley → arcade bar | **standing bar → taproom** | Loud and Social → `CROWD` high, `GAMES` low |
| `ENRG` 15, `CROWD` 15, `AFFIL` 12 | Piano Man → warehouse | **rooftop lounge → Old Delhi food walk** | Quiet Company → `TALK` high |

The third is better, not fixed: everyone is still served only *to a degree*, because **no venue
type is both quiet and outward-facing**. That is a venue-vocabulary hole, not a rule failure, and
it is logged as such.

---

# 5. It is not shown to the user

The daily name (`VIBE_NAMES_V4.md`) already occupies the "what kind of person are you tonight"
slot, and it is generated from the top two poles — the mellow case is already called *Low-Key
Table-Talker*. **The name knew; the plan did not.** This layer closes that gap on the plan side
and adds nothing to the profile screen.

Two reasons not to surface it: a second typology would compete with the name; and a visible type
makes people swipe **as their type**, which corrupts the one measurement everything else rests
on. The plan card already explains itself in plain words, and an inferred want simply reads as
one more line — *"a long table suits this one"* — with no label attached.

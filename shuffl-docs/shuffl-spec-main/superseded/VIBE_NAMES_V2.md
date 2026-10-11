> **Superseded by `VIBE_NAMES_V3.md` (2026-09-16).** The single names in the table below survive
> as V3 §4 (used when nothing else is within 15 of the top); the second line is withdrawn; the
> conditional V3 section at the bottom is now built, minus the strong/soft names, which stay held.

# Vibe names v2 — one name, from the top factor, settled by the person

**Supersedes `VIBE_NAMES_V1.md`**, which built a name from the highest factor and a tag from the
lowest. That scheme was measured on 2026-09-11 and dropped: across every tester who took the test
more than once, the top factor stayed the same **15 times out of 15**, and adding the refusal tag
took that to **6 of 15**. Half the testers had no refusal at all, so half the label did not exist.
See `DECISIONS.md` 2026-09-11.

## The rule

**The name is the highest factor. Nothing is appended to it.**

| Factor | Name | What it says |
|---|---|---|
| `CROWD` | **Crowd Chaser** | wants the fullest room in the city |
| `ENRG` | **Night Climber** | wants it building all night, and going late |
| `SCEN` | **Good Eye** | the room itself is half of why they went |
| `FOOD` | **Plate Chaser** | the food is the reason, not the setting |
| `POL` | **Dressed For It** | somewhere worth getting ready for |
| `NOV` | **First Timer** | somewhere none of them have been |
| `PLAY` | **Score Keeper** | a night with something to actually do |
| `LIVE` | **Set List** | a performance is the whole reason |
| `HERIT` | **Old Soul** | somewhere that has been there far longer |
| `AFFIL` | **Inner Circle** | their own people, at one table, all night |

Ten names. Unchanged from v1.

## When the top is tied

**The person decides.** A tie at the top sends one question — only the factors tied, pick exactly
one — and the answer is the name. No scale, no order, no averaging.

The hierarchy recorded on 2026-09-10 (`ENRG, CROWD, LIVE, PLAY, FOOD, SCEN, POL, HERIT, AFFIL,
NOV`) **no longer decides anything.** It was checked against four people who were asked directly
and was wrong for three of them. It survives in exactly one role: the *provisional* name for
somebody who has been asked and has not yet answered, shown as provisional until they do.

In the app, the tie is broken by response latency instead — highest score, shortest time to swipe
— with the forced choice kept for a genuine dead heat. Same rule, better instrument.

## The second line

Under the name, whatever else sat within 15 points of the top:

> **Night Climber**
> also strong on the food, dressing up

This line is allowed to change between sheets. The name is not. It is where a Night Climber who is
also 100 on food gets to keep that — the nuance the old scheme tried to force into the name, put
somewhere it can move without the identity moving.

`AFFIL` is left off this line. It runs within reach of the top for most people, so "also strong on
your own people" would be said about nearly everyone and mean nothing. It still competes for the
name itself, and wins it for people who are genuinely there for their own table.

Somebody with nothing else near the top gets the name and a confirmation instead:

> **Score Keeper**
> something to do, clearly

## Why the label is allowed to be this simple

It is a label. Matching into rooms happens on how a person's vector changes the room's blend;
outing plans are generated from the ten scores directly. Nothing downstream reads the name. So the
one thing it has to do is let somebody recognise themselves twice — and a name from the top factor
alone does that 15 times in 15, while every richer scheme measured did it less than half the time.

## On the eighteen real sheets (2026-09-11)

```
Night Climber    6      Set List        5
Score Keeper     2      Inner Circle    2
Crowd Chaser     1      Plate Chaser    1      Dressed For It   1
Good Eye         0      Old Soul        0      First Timer      0
```

Then the forced choices came in: Armaan to Crowd Chaser, Mannat to Score Keeper, Anchal to First
Timer. Every one of those had been a different name under the hierarchy.

Three names had not been won by anyone before Anchal. `SCEN`, `HERIT` and `NOV` are also the three
factors that have been hardest to card, so this is worth watching rather than explaining away —
though two of the three now have a winner.

## Rules for anyone rewriting the names

1. **The name is what they want.** Never what they refuse.
2. **No name may describe everybody.** `AFFIL` averages above 80 across testers, so *Inner Circle*
   only gets used when it is someone's single highest — and it is kept off the second line.
3. **Two words.** They have to sit on a card.
4. **Nothing in a name may be a friction.** *Crowd Chaser*, never *Crowd Tolerator*.
5. **The second line uses the reader's words** — *the food*, *somewhere new* — not the factor codes.


---

## V3 — proposed, conditional on the app's latency data

Two changes to the name were proposed on 2026-09-14. Neither is a change yet. Both depend on
response latency, which only exists in the app, and on the validation in
`ASSESSMENT_ENGINE.md` §6.3 passing.

### The bottom factor comes back — but only on a fast refusal

v1 appended the refused factor and was dropped because it made the label unstable. Each cause of
that instability has a latency answer, so the tag returns with one gate:

> score ≤ 25 **and** latency-firmness high on that card

A wall — a fast 0 — is identity-level and stable. A soft no — a slow 20 — is not, and the soft nos
were what flipped the tag. When the floor is tied, the refusal they answered fastest is the one.
Somebody with no fast refusal gets no tag, as before.

### Strong and soft names — held behind one check

Latency on the top factor would choose between the strong name and a softer sibling:

> fast `ENRG` → **Night Climber**
> slow `ENRG` → a name that says *leans toward a night that builds* without claiming it

This stops the name overclaiming. It also puts a threshold on the name itself, and anybody near
the threshold flips between the two on a retake for no reason they can see — which is the exact
instability that killed the refusal tag, now on the one thing that must not move.

Before it can go in:

1. **Latency-firmness on a person's top factor must be shown stable across sessions.** Added to
   the §6.3 validation list as its own check.
2. **Hysteresis.** Once strong, you stay strong unless latency drops well below the line.
3. **Ten softer siblings**, each to the same rules as the ten names — two words, what they want,
   never a friction — and each written so it does not read as a demotion.

If check 1 fails, the second line already does this job more safely: *a night that builds,
clearly* against *also strong on the food, dressing up*.

If both go in, the second line goes back to near-ties only, or goes entirely. Three things on a
card is too many.

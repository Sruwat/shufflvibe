# Mood Cards v1 — eight cards, issued only when the factors don't decide the night

Not part of the twenty. Handed out **after** the factor sheet is scored, and only to users with
**five or more genuine neutrals** — factors scoring 38–62 whose two cards agreed. A 50 built from
`LOVE IT + HATE IT` is a broken card, not a shrug, and does not count toward the trigger.

## The one design decision that matters

Every previous attempt **implied** mood through the register of a sentence and asked people which
night they preferred. That failed twice on real testers: v6's tone read as identical, and v7's
clean cards produced one moving pair out of six.

These cards **state the mood outright and ask whether it is true of you today.** Not *which of
these nights do you want* — *is this you, right now.* That single change removes everything that
broke the earlier versions:

| Old problem | Why it's gone |
|---|---|
| Tone had to be perceptible in prose | The card says the feeling in plain words |
| Tone competed with factor content | There is no factor content |
| One card could be simply more appealing | A description isn't appealing, it's accurate or not |
| Firm opinions drowned the signal | There is no opinion to drown it — only whether it fits |

## The scale

**THAT'S ME 88 · A BIT 62 · NOT REALLY 38 · NOT AT ALL 12.** Same four-way shape and same values
as the factor cards, so the interaction is one people already know.

Four levels rather than a straight pick-one: a forced choice throws away how strongly they felt,
and costs a lot — **0.72 against 0.51**. Acquiescence is handled by the pair, not the format:
someone who agrees with everything says THAT'S ME to both cards and the gap is untouched.

## The eight cards

| # | Pair | Card | Arousal | Valence |
|---|---|---|---|---|
| 1 | 1 | Right now you could be on the go all day. | +1.00 | +0.00 |
| 2 | 3 | Things have been going your way lately. | +0.00 | +1.00 |
| 3 | 2 | You've got energy to spare and you're looking for somewhere to put it. | +0.71 | +0.71 |
| 4 | 4 | You feel settled. Nothing is pulling at you. | -0.71 | +0.71 |
| 5 | 1 | Right now you'd rather move at your own pace. | -1.00 | +0.00 |
| 6 | 3 | Lately nothing has quite gone right. | +0.00 | -1.00 |
| 7 | 2 | You're running on empty. | -0.71 | -0.71 |
| 8 | 4 | You're wound up and can't switch off. | +0.71 | -0.71 |

## Why four pairs at these angles

| Pair | Cards | Angle | Reads |
|---|---|---|---|
| 1 | 1 – 5 | 0° | pure arousal |
| 2 | 3 – 7 | 45° | arousal and feeling moving together |
| 3 | 2 – 6 | 90° | pure valence |
| 4 | 4 – 8 | 135° | feeling moving against arousal |

Evenly spread over the half-circle, which is all a pair needs since it covers both directions.
**The two axes come apart completely — entanglement 0.00**, against 0.06 for the best integrated
card set and 0.20 for v6. Arousal and valence are each measured to a standard error of 0.35.

**If eight cards is too many, drop to three pairs — but re-angle them to 0° / 60° / 120°, do not
just delete one.** Removing the 135° pair from this set leaves 0° / 45° / 90°, which entangles the
axes at 0.33 and is worse than having fewer, better-placed pairs. Three at 60° apart scores 0.58
against 0.51 for four.

## Rules these cards follow

1. **Never a venue, a place, or a night out.** Carried over from the discarded ambient-image
   instrument, and the one part of it worth keeping.
2. **Never anything the ten factors measure** — no crowds, no other people, no food, no music,
   no clothes, no newness, no games, no old buildings, no looks. A mood card that mentions any of
   them is measuring a factor.
3. **About today, not in general.** Mood is a state. The sheet says so at the top.
4. **The two cards in a pair are true opposites**, and are meant to be recognised as such.

## Reading them

`THAT'S ME 88 / A BIT 62 / NOT REALLY 38 / NOT AT ALL 12`. For each pair, **gap = first card minus
second card**, keeping the sign. Then:

```
arousal, valence  =  least-squares fit of the four gaps against the four pair directions
```

**The gap means the opposite of what it means on the factor sheet.** There, the two cards say the
same thing and a large gap is a card defect. Here, the two cards are deliberate opposites and
**a large gap is the entire signal.** All four gaps at zero means no mood reading, not a clean one.

**The validity check.** Because each pair is a true opposite, `THAT'S ME` to both cards — or
`NOT AT ALL` to both — is a contradiction. One or two is careless answering; three or four means
the sheet was not engaged with and should be discarded rather than scored.

## What this does and does not fix

It fixes **how well mood can be measured**: 0.51, matching the integrated design's theoretical
best while removing the assumption that broke it.

It does **not** fix **when**. The spec defines mood as momentary affect at swipe time, so a reading
taken at onboarding is a fossil by the second night out. These cards belong at plan time, or they
need re-asking. That remains open and is the more important of the two problems.

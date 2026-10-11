# AFFIL as *give* — can how much someone wants their own people tell us how far they'll bend the rest of their night?

**Status: exploration, 2026-09-21. Prototyped (`give.py`), not in the engine.** The user's
reasoning: a high `AFFIL` score means the person wants to go with the flow of the group — their
friends matter more than the night — so it should say how far they are willing to bend their
other vibe factors. This document says whether that holds, what it would do, what it must not do,
and how to find out if it is true.

---

# 1. Does the psychology support it?

**For.** The need for affiliation (McClelland) and communion on the interpersonal circumplex
(Wiggins 1979; Horowitz et al. 2006) go with accommodation: people high in communion yield in
conflict, prioritise the relationship over the task, and avoid the friction of insisting.
Contagion susceptibility also runs with affiliative orientation (Doherty 1997's Emotional
Contagion Scale; Hatfield et al.) — attentive-to-others people catch the group's state more
readily. Both point the same way as the user's reading.

**Against — the confound.** Our `AFFIL` card measures *who you want to face tonight* — your own
table or the room. That is not the same thing as accommodation. A person can want their own
people around and be immovable about energy; a person facing the room (low `AFFIL`) may be the
most go-with-anything person in it — they are out to meet whoever. So the link is plausible for
the high pole and unknown for the low, and it is a trait being read off a nightly state.

**The thing the prototype found first.** When `AFFIL` is 80 or more, it is usually the person's
*top factor* — and the model already protects only the top. A person whose reason to go out is
their people already has everything else bending, by the rule that only the top stands. So
"high `AFFIL` = give" is **mostly already true by construction**. What is *not* yet encoded is the
band where `AFFIL` is high but not the top (65–79, or a strong #2 behind a stronger top), and
the way such a person pushes their *other* poles on the group.

---

# 2. What "give" would do — the narrow version that survived the runs

```python
def give(m):
    """0 - 0.4. Give comes from AFFIL being among the person's TOP reasons tonight."""
    if m.vibe['AFFIL'] < 65:              return 0.0
    if AFFIL is m's #1:                   return 0.4
    if AFFIL is m's #2 and strong:        return 0.4        # within 10 of the top, 25+ from the middle
    return 0.2                                              # high, but not why they are out
```

Where it applies — **only on the person's non-`AFFIL` vibe factors**, and never to preferences:

| Effect | Rule | Why |
|---|---|---|
| **their bend widens** on their own firm factors | bend × (1 + give): 25 points → 35 | they are satisfied by a calmer version of what they asked for |
| **they push their pole on the group less hard** | strength in the contagion counts × (1 − give / 2) | the room's number settles nearer the others |
| **they yield to a milder opposer** | a band-strength opposer (0.5) is enough to move their top to a strong #2 — **unless their side is the majority** | friends-first people give way; but two of them against one firm person are still two |
| **they catch a spark more readily** | as a neutral, their pull is 0.7 not 0.6 | contagion susceptibility |
| never | their own top, when it is `AFFIL`; the low pole; any preference | the top stands (§14.3); the low pole says nothing about give; taste is not chemistry |

---

# 3. The runs — the same room, with and without give

| Room | Without give (`AFFIL` 30) | With give (`AFFIL` 78, a strong #2) |
|---|---|---|
| **Kabir** `ENRG` 88 against **Neha** `ENRG` 25 at normal speed (a mild opposer) | Neha is flexible, opposes nobody; Kabir's energy stands → games pub → games bar; Kabir 0.5 / 1.0, Neha 1.0 / 0.5 | Kabir yields to the mild opposer: his people stand in for his energy → a table for the night → the live-band pub; **both 1.0 at both stops** |
| **two 88s against one firm 12** | the highs outnumber → the food street → bowling; A 0.5 / 1.0, C 1.0 / 0.5 | still the majority, so their tops stand — but they push at half strength and their bend is wider: a games pub → the food street, **everyone 1.0 at both** |
| **Bela** `ENRG` 12 against **Aarav** 88, Bela friends-first | Aarav's crowd stands in; rooftop → pub; both 1.0 | Bela's halved push tips the count: Aarav's energy stands, her talk stands in; games pub → games bar; Aarav 0.5 / 1.0, Bela 1.0 / 0.5 |

The pattern: give does not erase anyone — it turns "one person fully served, one to a degree"
into "both fully served" by letting the friends-first person be satisfied by a calmer version of
their own factor. That is the user's sentence made mechanical: *their friends matter more than
the night*.

---

# 4. What it must not become

- **Not a blanket multiplier on `AFFIL` 80+.** At 80+ `AFFIL` is nearly always the top, the top
  stands, and a multiplier on top of that double-counts. Give lives in the band and the #2.
- **Not a majority-breaker.** Two friends-first people against one firm person are still the
  majority. The prototype's first version had them both yielding; that was wrong.
- **Not on the low pole.** A room-facing person is not thereby rigid. No inference.
- **Not on preferences.** Food, an act, dress — taste is not what bends for friends.
- **Not a second friend mode.** Friend mode's stretch is *data* (plans together); give is
  *self-declared* (tonight's swipe). They combine as the larger of the two, never as a sum.

---

# 5. How to know if it is true — the test that decides it

Before this becomes a rule, one comparison on real plans: **do people whose `AFFIL` was among
their top reasons rate a night where their other factors were served only "to a degree" as
highly as a night where they were fully served?** If yes, give is real and the rule stays. If
they rate it lower — same as everyone else — the confound wins: `AFFIL` measures who they want
to face, not how far they bend, and the rule comes out. Thirty rated plans with a friends-first
member is enough to see it.

---

# 6. Recommendation

Adopt the narrow version (§2) as a rule, with the test in §5 attached and the four "must nots"
written in. It is small — one function, three touch-points — it is grounded, it produces nights
where more people are fully served, and it cannot move anyone's top. If the test fails, it is one
function to delete.

**Constants:** `GIVE_TOP` 0.4, `GIVE_HIGH` 0.2, `GIVE_FROM` 65; bend × (1 + give); strength × (1 −
give / 2); spark pull + 0.1 for a friends-first neutral.

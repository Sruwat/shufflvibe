> **Superseded by `PREFERENCE_ENGINE_V2.md` (2026-09-16).** Kept for the shape of the argument only.
>
> **Scope, as of 2026-09-12.** This document is the *learning* layer — how a known user's profile
> is refined across sessions and how the card count comes down over weeks. The *measurement* layer
> — how a single session of cards becomes a profile, including the branch question, the 0–5 scale,
> firmness, the split factor, the forced choice and response latency — is `ASSESSMENT_ENGINE.md`,
> and it supersedes anything here about how a session is scored. Card counts below (18, 28) are
> from an earlier design; the app deck is a fixed 14.
>
> **V2 of this document is owed** and its content is logged: `DECISIONS.md` 2026-09-12 (latency in
> the learning layer — a Kalman update replacing the fixed α, settled factors leaving the deck,
> unanswerable factors leaving it the other way, a session-quality gate, the re-check) and
> 2026-09-14 (the variable audit). None of it is implemented and all of it is post-validation.
> The factor set, vibe library and card counts below are also stale. Read this document for the
> shape of the learning layer, not for its constants.

# User Preference Learning Engine — Method

Extends the data model in `User Preference Learning Engine`. That doc says *what to store*; this says *what to do with it* — specifically how to cut the daily game from 18 cards to 3–8 without losing accuracy.

---

## 1. The reframe that makes short games possible

Today the app measures the user's vibe **from scratch every day**. That's why it needs 18 cards — it's re-solving a 10-dimensional problem with no prior.

But a returning user isn't unknown. They have a stable going-out type. Their daily vibe is that baseline plus a deviation:

```
today's vibe  =  trait (slow-moving baseline)  +  today's deviation
```

Once the trait is known, **you only need to measure the deviation** — a far smaller problem. That's the entire basis for card reduction. Day 1 needs 28 cards because the trait is unknown. Day 60 needs 3–5 because you're only asking "on-baseline today, or shifted, and which way?"

---

## 2. What the engine actually holds

Two layers, updated on different timescales:

| Layer | What | Updates | Timescale |
|---|---|---|---|
| **Trait** `μ` | 10-factor baseline — their overall going-out type | Slowly, after every session | Weeks |
| **Uncertainty** `σ` | Per-factor confidence in `μ` | Shrinks with evidence, grows with time | Days |
| **Volatility** `v` | How much this user swings day to day, per factor | After every session | Weeks |
| **State** | Today's vibe | Fresh each day | Daily |

`σ` and `v` are the two the current doc is missing, and they're the ones that control card count.

**`σ` (uncertainty)** — you may know a user's FOOD preference precisely but have almost no read on their PLAY. Cards should go where `σ` is high, not spread evenly across clusters.

**`v` (volatility)** — some users are the same vibe most days; others swing hard. A consistent user needs 3 cards to confirm. A volatile user needs 10 to pin down. **Personalising card count by measured volatility is the single biggest lever**, and it's also fairer: the people who'd find 18 cards boring are exactly the consistent ones who need fewest.

---

## 3. Updating the trait

After each completed session, with the day's measured vibe vector `x`:

```
μ_new  =  μ_old  +  α · (x − μ_old)          α ≈ 0.15, decaying to ~0.05 as sessions accumulate
v_new  =  v_old  +  β · (|x − μ_old| − v_old)   β ≈ 0.10
σ      shrinks by a factor each session, grows back slowly with days since last seen
```

A running weighted average, with volatility tracked as the average size of the daily swing. No ML needed for v1.

### Practical factors are trait, not state

**PREM, VALUE and CONV barely move day to day.** Someone's budget comfort and tolerance for travel are close to fixed; their energy and mood are not. So:

- Learn PREM/VALUE/CONV over the first ~2 weeks, then treat them as near-fixed
- **Stop testing them daily.** Re-check every ~10 days, or when behaviour contradicts them
- Mood factors (SOC/SOFT/FOOD/PLAY/CULT/CAS/FUN) still need daily measurement

This alone removes the 4 practical cards from most sessions — 18 → 14 before any other optimisation.

---

## 4. Choosing which cards to show

Don't show 2 cards per cluster. Show the cards that **best separate the vibes still in contention**.

**Step 1 — predict.** Build today's prior from the trait plus context (§6). Score all 30 vibes; keep those with meaningful probability. Usually 3–6 candidates.

**Step 2 — model the swipe.** For user vector `u` and card vector `c`, using the factor weights from `Factors and Vectors`:

```
match(u,c) = Σᵢ wᵢ · (1 − |uᵢ − cᵢ| / 100)
P(right)   = sigmoid( k · (match − c₀) )
```

**Step 3 — pick the most divisive card.** For each candidate card, compute `P(right)` *as if* the user were each candidate vibe. Choose the card where those predictions **disagree most** (highest weighted variance).

Intuitively: if the app thinks you're either Sunlit Brunch Friend or Candlelight Romantic, don't show a generic Soft & Scenic card — both would swipe right and you learn nothing. Show a card those two would *split on*. They differ most on CAS (75 vs 25) and PREM (45 vs 80), so Card 6 vs Card 7 is exactly the right test.

This is why the quartet structure in `CARD_SET_V2` matters: within each cluster the mood is held flat and the practicals swing, so there is always a card that splits any two same-cluster vibes.

**Step 4 — update and repeat.** After each swipe, update the posterior and re-pick. Cards are chosen one at a time, not batched.

---

## 5. When to stop

Stop as soon as any of these fires:

| Condition | Threshold |
|---|---|
| Top vibe is clear enough | `P(top) ≥ 0.80` |
| Next card would teach almost nothing | expected info gain below floor |
| Cap reached | see ladder below |

### Card ladder

| Stage | When | Cards | What it's doing |
|---|---|---|---|
| Onboarding | Day 1 | 28 | Nothing known — full instrument |
| Calibration | Days 2–14 | 10–14 | Learning trait, volatility, practicals |
| Steady state | Day 15+ | **5–9** | Measuring deviation only |
| Confident | Day 45+, low volatility | **3–5** | Confirm or detect a shift |
| Volatile user | any stage | 8–12 | Genuinely swings — needs the cards |

Tie-breakers still layer on top when the result is ambiguous, drawn from unused cards as already specified.

---

## 6. Context priors — cards you never have to show

Before any card is shown, the engine already has a strong guess. Free signals that sharpen it:

| Signal | Why it matters |
|---|---|
| **Day of week** | The strongest single predictor in nightlife. Friday ≠ Tuesday |
| **Time of day opened** | 11am and 10pm imply very different vibes |
| **Yesterday's vibe** | Vibes autocorrelate — especially across a weekend |
| **Went out yesterday?** | Fatigue effect; two big nights in a row is rare |
| **Weather** | Delhi-specific and large — heat and rain reshape going-out behaviour |
| **Payday proximity** | Moves PREM/VALUE more than anything else |

Learn per-user conditional patterns: *"this user is Party Monster on 70% of Fridays."* On a Friday, that prior alone may push `P(top) ≥ 0.80` before a single card — a **zero-card day**.

---

## 7. The quick-pick shortcut

You already have the "Your most recent vibe is X — same today?" screen. Widen it into the primary path.

Instead of a binary, show **the top 2–3 predicted vibes as tappable chips**, plus "something else":

> **Tonight you're probably…**
> `🔥 Party Monster` · `☕ Low-Key Loyalist` · `🕯️ Candlelight Romantic` · *Something else*

Tap one → done, zero cards. Tap "something else" → the adaptive game runs, and because the top candidates were just ruled out, it starts from a much better position and converges in 2–4 cards.

For a well-modelled user this should resolve most days with **one tap**, and the swipe game becomes the exception rather than the daily ritual. That fixes the boredom problem far more decisively than trimming 18 to 12.

---

## 8. Learning from behaviour, not just swipes

Swipes are *stated* preference. What the user actually does is *revealed* preference, and it's the stronger signal. Weight these into the trait update:

| Signal | Strength | What it says |
|---|---|---|
| **Post-outing star ratings** | Strongest | Ground truth on what they actually enjoyed |
| **Stops actually visited** (geofence) | Strong | Real behaviour, already tracked for referral fees |
| **Plan locked vs regenerated** | Strong | Regenerating repeatedly = the vibe read was wrong |
| **Rooms joined / left early** | Medium | Blend-style fit |
| **Venue pages opened** | Weak | Curiosity, not commitment |

**Contradiction rule:** when swipes and behaviour disagree persistently — user swipes premium but always visits cheap places — trust behaviour and correct the trait. Log it under Avoided Patterns so the engine can explain itself later.

There's also a free correction signal you already have: **repeated refreshes of a generated plan mean the vibe was wrong.** Treat a refresh as negative feedback on today's vibe estimate.

---

## 9. Guardrails

**Exploration budget.** If you only ever show cards matching what the user already likes, you stop learning about everything else and lock them into a narrow vibe. **Reserve one slot per session — roughly 1 in 5 sessions — for a high-`σ` or deliberately off-profile card.** Cheap insurance against a filter bubble, and it keeps the app feeling less predictable.

**Drift detection.** People genuinely change — new job, new relationship, seasons, moving neighbourhood. If measured vibes sit outside the expected band for ~5 sessions running, **inflate `σ`, lengthen the game temporarily, and re-learn.** Without this the trait calcifies and the engine slowly gets worse while looking confident.

**Confidence floor.** Never let a short game run on a stale model. If the user has been away more than ~14 days, grow `σ` and return them to a calibration-length game.

**Don't over-trim too early.** Dropping to 3 cards by day 10 will feel great and measure badly. The ladder is deliberately conservative — the accuracy cost of a bad vibe read (a wrong outing plan) is much higher than the boredom cost of two extra cards.

---

## 10. What to add to the preference database

Extending the existing table:

| Field | Type | Purpose |
|---|---|---|
| `trait_vector` | 10 floats | Baseline going-out type (`μ`) |
| `uncertainty` | 10 floats | Per-factor confidence (`σ`) — **drives card targeting** |
| `volatility` | 10 floats | Day-to-day swing size (`v`) — **drives card count** |
| `practical_locked_at` | date | When PREM/VALUE/CONV were last re-tested |
| `context_priors` | map | P(vibe \| weekday, time, weather) per user |
| `behaviour_delta` | 10 floats | Correction from revealed vs stated preference |
| `cards_seen_recent` | list | Prevents repeating the same card concept too often |
| `session_lengths` | list | For monitoring — is the ladder actually shortening? |
| `drift_flag` | bool | Set when recent vibes fall outside the expected band |

---

## 11. Build order

**Phase 1 — ships without ML.** Running-average trait, volatility tracking, card count from the ladder, card selection by "which card best splits the top 3 candidates," practical factors re-tested every 10 days. Gets you from 18 cards to roughly 8.

**Phase 2 — the big UX win.** Quick-pick chips with the top 3 predicted vibes, plus day-of-week and time-of-day priors. Most days become zero-card.

**Phase 3 — accuracy.** Full Bayesian updating with per-factor `σ`, behavioural feedback loop, drift detection, exploration budget.

---

## 12. What to measure

The engine is working if all four hold:

1. **Median cards per session falls** — 18 → ~8 by day 15, ~5 by day 45
2. **Vibe accuracy holds** — track "did the user regenerate the plan?" as the inverse proxy; it should not rise as cards fall
3. **Quick-pick acceptance climbs** — share of days resolved with one tap should grow week over week
4. **Completion rate rises** — fewer people abandoning mid-game

If cards fall but regeneration rate climbs, the ladder is too aggressive — slow it down.

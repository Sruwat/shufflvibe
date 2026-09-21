# Preference Engine V2 — the learning layer

**Supersedes `PREFERENCE_ENGINE.md`**, which was written on an older factor set, a 28-card deck and
no latency. The shape of that document survives — a slow-moving baseline, a per-factor uncertainty,
a per-factor volatility, and a card count that comes down as the app learns you. What changes is
the input: the app now knows how *sure* each swipe was, and that is what drives everything below.

**Audience:** the developer, after v1 is built. Nothing here ships on day one. All of it depends on
the latency validation in `ASSESSMENT_ENGINE.md` §6.3 passing.

**Reads:** `ASSESSMENT_ENGINE.md` — one session becomes a profile. This document is what happens
between sessions.

> **2026-09-17.** μ, σ, v, the states and the shrinking deck are on the **seven vibe factors**. The six
> preferences are not learned this way — they are set once and edited; the only automatic movement is a
> slow re-check (a preference card every 60 days) and the venues-attended evidence in §8b, at low
> reliability, which can *suggest* an edit on the profile but never makes one.

---

# 0. What this layer does

Day one, a user sees the full adaptive deck — ten to twenty cards — because nothing is known about
them. Day thirty, the same user should see four or five, because most of their factors are
settled and only the ones that move need asking. This layer decides which.

Three things per user, per factor:

| | What it is | Moves |
|---|---|---|
| **μ** | their baseline on this factor — what they usually want | slowly |
| **σ** | how sure *we* are about μ | shrinks with firm answers, grows with time |
| **v** | how much they swing day to day | slowly |

Plus today's state — this session's scores — which is what everything downstream reads.

---

# 1. The update — how sure the swipe was decides how much it counts

The old rule moved μ toward today's answer by a fixed fraction:

```
μ_new = μ_old + α · (x − μ_old)          α ≈ 0.15
```

A fast, committed swipe and a slow, deferred one moved μ the same amount. That is wrong. A firm
answer is a precise reading; a hesitant one is noisy. So the gain comes from firmness:

```python
R = 400.0                                 # observation-noise scale; tune

def update(mu, sigma2, x, firmness):
    """One factor, one session. firmness is the combined figure from
    ASSESSMENT_ENGINE §3.5 - score x latency x Next x Back."""
    noise = R / max(firmness, 0.05)       # firm -> low noise, soft -> high noise
    K     = sigma2 / (sigma2 + noise)     # the gain
    mu    = mu + K * (x - mu)
    sigma2 = (1 - K) * sigma2
    return mu, sigma2
```

A fast *love* pulls μ hard and shrinks σ a lot. A slow *up for it* after a Next barely moves
either. This is a Kalman update; the old fixed α was the special case where every swipe is
assumed equally reliable.

**σ grows back with time.** A factor not asked about for a while gets less certain:

```python
sigma2 += DRIFT_PER_DAY * days_since_last_asked        # DRIFT_PER_DAY ≈ 2.0; tune
```

---

# 2. Three states per factor — and the one the old engine could not see

σ is high on a factor for one of two reasons, and they need opposite responses:

| State | What it looks like | What to do |
|---|---|---|
| **not yet known** | few sessions, σ still high | ask — show the card |
| **settled** | several firm, consistent answers; σ small | stop asking — use μ |
| **unanswerable** | many sessions, every answer slow or deferred, scores wander | stop asking — μ is weak, learn it from where they go |

The old engine treated the first and third the same — "σ is high, show more cards" — and would
have asked an unanswerable factor forever. Latency separates them: σ that stays high *despite*
firm answers is not-yet-known; σ that stays high because every answer was soft is unanswerable.

```python
SETTLE_SESSIONS = 3          # consecutive firm, on-μ sessions
SETTLE_FIRM     = 0.6        # latency-firmness above this counts as firm
SETTLE_BAND     = 15         # score within this of μ counts as consistent
GIVEUP_SESSIONS = 5          # consecutive soft sessions before "unanswerable"
GIVEUP_FIRM     = 0.3

def state_of(factor_history):
    recent = factor_history[-SETTLE_SESSIONS:]
    if len(recent) == SETTLE_SESSIONS and all(
            h.firmness >= SETTLE_FIRM and abs(h.score - h.mu_at_time) <= SETTLE_BAND for h in recent):
        return 'settled'
    soft = factor_history[-GIVEUP_SESSIONS:]
    if len(soft) == GIVEUP_SESSIONS and all(h.firmness <= GIVEUP_FIRM for h in soft):
        return 'unanswerable'
    return 'not_yet_known'
```

---

# 3. The deck shrinks — settled and unanswerable factors leave it

This is the rule the user stated: **how fast someone answers a factor's cards, over time, becomes
their baseline, and the factor stops being shown.**

```python
def deck_for(user):
    ask = [f for f in FACTORS if state_of(user.history[f]) == 'not_yet_known']
    return build_adaptive_deck(ask)        # ASSESSMENT_ENGINE §2 - one card per factor to start,
                                           # a second if the first swipe is mild, POL always both
```

A settled factor is filled in from μ with σ small. An unanswerable factor is filled in from μ with
σ large — it carries little weight in a room's blend (abstention reads firmness) and wide bend at
plan time, which is the honest treatment of something the person cannot tell you.

Somebody settled on eight factors sees two cards. That is the 14 → 4 reduction the old document
promised, driven by observed conviction rather than a schedule.

**Next and Back feed this directly.** A factor that gets deferred every session is not settling —
`next_count` lowers firmness (§3.5 of the assessment engine), so it stays in `not_yet_known` or
drifts to `unanswerable`. A factor swiped once, firmly, session after session, settles fast.

---

# 4. The way back in — without this, settling is a trap

A settled factor is never gone for good. It returns to the deck when:

| Trigger | Why |
|---|---|
| **re-check timer** — every 14 days, one card | a preference that drifts over a month is otherwise invisible until it is badly wrong |
| **behaviour contradicts μ** — they went somewhere that badly mismatches the settled score, and rated it well | the world said something the cards did not |
| **"same as yesterday?" swiped left** | an explicit "something is different" — reopen the two or three factors with the widest bend |
| **a related factor unsettles** | `ENRG` and `CROWD` move together; if one comes back, check the other |

**The re-check card is hidden in the deck.** It is answered like any other card. The person sees
one more card than usual and nothing says why. A card flagged "just checking" is answered
differently, and the point of the re-check is an honest latency reading. If it comes back firm
and on-μ, the factor settles again for another cycle. If it has drifted, it is back in rotation.

---

# 5. Session quality — protecting μ from a session that was not really a session

Before μ moves at all, ask whether this session was trustworthy. Latency answers it with no extra
input:

| Pattern | Read as | Gain |
|---|---|---|
| nearly every swipe under 1 s | not reading | ×0.1 — today's state is recorded, μ barely moves |
| median latency far above the person's own baseline | distracted | ×0.3 |
| the pause fired twice | was away | ×0.3 |
| the deck-browser pattern (§3.6) | fine — score on the second looks | ×1.0 |
| otherwise | fine | ×1.0 |

The old engine had no gate; a session swiped through in twenty seconds moved μ as much as a
careful one.

---

# 6. Volatility splits in two

v tracked how much the *score* swings. With latency there is a second kind: how much the
*conviction* swings. They describe different people and the plan engine should treat them
differently:

| | score | latency | who | treat as |
|---|---|---|---|---|
| A | FOOD always ~80 | sometimes fast, sometimes slow | stable want, variable conviction | FOOD 80, wide bend |
| B | FOOD swings 40–100 | always fast | a genuinely different appetite each day, held firmly | a daily question — keep the card |
| C | FOOD swings 40–100 | always slow | does not know, and it shows | unanswerable |

There is also a leading indicator here: latency on a factor *rising* across sessions means the
preference is destabilising before the scores show it. Reopen it early.

---

# 7. Which card to show, when a factor is still open

Where several factors are open, the ones to spend cards on are those where a card will actually
resolve something: σ high **and** past firmness says they *can* answer it. A factor they always
hesitate on will not be resolved by asking again — but it might be by a *different image* for
that factor, which is card QA (`ASSESSMENT_ENGINE.md` §6.4) feeding selection.

---

# 8. The zero-card day

Context — day of week, yesterday's vibe, time opened — can make the "same as yesterday?" swipe
confident enough that no cards are needed. One guard on top of the old rule: only skip the cards
if the person's *historical firmness* on their top factors is high. Predictable and sure are
different things; a person whose pattern is regular but whose conviction is always soft should
still get a short deck.

And record the latency on the "same as yesterday?" swipe itself. A fast *yes* and a slow *yes*
mean different things.

---

# 8b. Behaviour is evidence too — what the app knows once somebody has used it for a while

The swipe game is one instrument. After a few weeks the app has others, and every one of them is
an observation of the same μ. Each is fed to the same update as §1 — an observed value `x` on a
factor, with a *reliability* in place of swipe firmness — so nothing new has to be invented to
consume it; only the weights differ.

| Source | What is observed, per factor | Reliability (as firmness) |
|---|---|---|
| a swipe session | the score | its firmness — §1, as now |
| a plan **rated well** (4 or 5) | for each stop, the venue's score on the factor the person was served on — confirmed | 0.40 |
| a plan **rated badly** (1 or 2) | for each stop, the served factor: an observation pulled 25 points *away* from the venue's score, toward 50 | 0.30 |
| a **regenerate / refresh** | the refused plan's two dominant factors, observed at 50 — "not this" | 0.20 |
| a **room joined** | the room plan's mean vector | 0.25 |
| a **venue searched** and viewed 10 s or more | the venue's vector | 0.15 |
| a venue **saved or shared** | the venue's vector | 0.30 |
| a venue **attended** (plan locked, night happened) | the venue's vector | 0.35 |
| the **"same as yesterday?"** swipe | yesterday's scores, confirmed or refused | latency of that swipe |

Behaviour counts less than a swipe because it is *revealed* through other people's choices and
the venue set, not stated. But it never goes quiet, it needs no cards, and it is the only
evidence for a factor the person has stopped being asked about (§3). A settled factor that
behaviour keeps contradicting is what reopens it (§4).

**The vibe profile.** μ across the ten factors *is* the person's vibe profile — what they usually
want, with σ saying how sure that is. Its nearest library vibe (`FACTORS_AND_VIBES_V4.md`, by
L1) is what friend mode uses to substitute a factor the venue set cannot serve
(`OUTING_PLAN_ENGINE.md` §13.9.4), and what names the person on a day they did not swipe. It
also carries a running **overall firmness** (`ASSESSMENT_ENGINE.md` §6.5), the mean over
sessions, which the plan engine reads to scale debt (§13.8).

---

# 9. What to store, on top of the assessment record

```python
@dataclass
class FactorLearning:
    user_id, factor:   str
    mu:                float
    sigma2:            float
    volatility_score:  float
    volatility_firm:   float
    evidence:          list[Observation]      # source, x, reliability, date - behaviour and swipes alike
    state:             str          # 'not_yet_known' | 'settled' | 'unanswerable'
    settled_since:     date | None
    last_asked:        date
    history:           list[SessionReading]   # score, firmness, next_count, back_count, mu_at_time, date

@dataclass
class UserLearning:
    user_id:            str
    factors:            dict[str, FactorLearning]
    overall_firmness:   float          # running mean of the per-session value, §6.5
    nearest_vibe:       str            # from mu, recomputed when mu moves
```

Keep every session reading forever. Every rule in this document was arrived at by re-reading old
answers under a new rule.

---

# 10. Constants, all set, all to adjust from data

| | value | replaced when |
|---|---|---|
| `R` observation-noise scale | 400 | μ stability across sessions is measured |
| `DRIFT_PER_DAY` | 2.0 | re-check hit rate is known |
| `SETTLE_SESSIONS` / `SETTLE_FIRM` / `SETTLE_BAND` | 3 / 0.6 / 15 | how fast people settle is known |
| `GIVEUP_SESSIONS` / `GIVEUP_FIRM` | 5 / 0.3 | how many factors go unanswerable is known |
| re-check cadence | 14 days | drift-on-re-check rate is known |
| session-quality gains | 0.1 / 0.3 | — |

Build them as constants in one place. Testing cannot start without values; the first thirty
returning users are where they get tuned.

---

# 11. Not established

- Everything. This layer has never run. It depends on the latency validation passing first.
- Whether three sessions is enough to call a factor settled, or whether it should scale with
  the person's overall firmness.
- Whether the re-check card, hidden, is actually answered the same way as a first-time card. It
  should be; check it.
- Whether the "unanswerable" state is common or rare. If common, the cards for those factors are
  the problem, not the people.

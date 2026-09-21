# Reminders — things to come back to

Open work, not open decisions. Each line says what, why it waits, and what unblocks it. Started
2026-09-16. Strike a line when it is done and say where it went.

## The split (2026-09-17) — what it leaves owed

- [x] ~~Re-cut the simulations.~~ `splitsim.py`, 2026-09-17 — twelve scenarios re-run (entry 101).
- [x] ~~Whole-point coverage as the last shape tie-break~~ — confirmed 2026-09-17 (entry 102).
- [ ] **Tag the venue database** with a type (`FACTORS_V5.md` §4) and score every venue on the seven
  vibe axes and six preference attributes. *Data work.*
- [ ] **Re-derive the blend styles** by clustering real rooms on seven axes; `BLEND_STYLE_DATABASE_V3`
  is authored. *Blocked on app data.*
- [ ] **Weights** on both kinds are set and unmeasured. *Blocked on app data.*
- [ ] **`TALK` and `ROAM` cards** — the two a picture may fail to carry. `GAMES` may be one-ended.
  *Watch on the first users.*
- [ ] **Preference re-check cadence** (60 days) and whether behaviour should ever edit a preference
  automatically. *Blocked on app data.*

## Chemistry V2 (2026-09-19) — open

- [x] ~~The talk floor~~ 40 — decided 2026-09-19 (entry 111).
- [ ] **Twelve tags** — too many? Watch which fire on real rooms; fold the rare ones into the formation words.
- [ ] **`Our Table` as a gate on the join list** versus a nudge to the host. *Needs the user.*
- [ ] **The `ENRG` asymmetry at the extreme** — a firm 12 who genuinely cannot do a club exists; the rule
  says they live with it, #2 standing in. Watch the first complaints.
- [ ] **Chemistry constants** (`SPARK_PULL` 0.6, `DRIFT_UP` 10, `TOLERATE_TO` 70, `CROWD_HALF` 0.5,
  `SETTLE_SHARE` 55 %, `SPLIT_AT` 5) — set; tune.

## After the designed night (2026-09-18) — open

- [x] ~~**The joiner's match under v4.**~~ Decided 2026-09-18 (entry 108, §14.3.5a).
- [x] ~~**When a top factor is absent everywhere.**~~ Decided 2026-09-18 (entry 108, §14.3.5a).
- [x] ~~**Friend mode under v4.**~~ Decided 2026-09-18 (entry 108, §14.3.5a).
- [x] ~~**Overall firmness has no consumer.**~~ Decided 2026-09-18 (entry 108, §14.3.5a).
- [ ] **`DEGREE` 0.5 and `SUB_MIN` 18 (68 / 32)** — set; tune when designed nights are rated.
- [ ] **The eleven venue types** are authored; the games pub was added because a room needed it. The
  venue database decides which are real and which split. *Data work.*
- [ ] **Vibe names V4 — review on app data**: two-factor stability on seven axes; whether *Insider* lands
  on half the names (raise `SECOND_MIN` for `AFFIL` if so). *Blocked on app data.*
- [ ] **Friend threshold** (`FRIEND_THRESHOLD` 3.0 and its weights) and `FRIEND_MAX_GIVE` 70 — set; tune.

## Design work owed

- [x] ~~Room chemistry into the blend-style names.~~ Done 2026-09-17 — `OUTING_PLAN_ENGINE.md`
  §13.6: debt/payback, seven states, the match. Chemistry is a chip next to the style name.
- [ ] **Chemistry words — revisit after testing.** *In Sync · Got Your Back · Best of Both · Along
  for the Ride · Something for Everyone · Open Night · Could Go Late* are a first draft, written to
  be positive. Check on real rooms whether people read them as meant, and whether *Something for
  Everyone* is honest enough for a Tug room. *Blocked on app data.*
- [x] ~~**Re-derive the 24 blend styles with payback in the vector.**~~ Moot — V3 styles are on seven axes; re-derivation is the split item above.
- [x] ~~**Friend-mode constants**~~ Re-scoped below — the combination search is retired; the relaxed bends stay.
- [ ] **Overall-firmness percentile** needs a population; until ~30 users it runs against the
  form-era testers' extreme-share distribution. *Resolves itself.*
- [ ] **Behavioural evidence reliabilities** (`PREFERENCE_ENGINE_V2.md` §8b) — set by judgement;
  check against swipe-predicted scores once both exist for the same people. *Blocked on app data.*
- [x] ~~**Variety across stops.**~~ Built 2026-09-18 — a tie-break in the designed night (§14.3.3).
- [x] ~~**Chemistry constants**~~ Superseded — chemistry is read from the design (§14.3.4); `SHIFT_*` / `REINF_GREAT` live on under the match, see below.
- [x] ~~**Vibe names — review on app data.**~~ Re-scoped to V4 below.
- [x] ~~**Whether `AFFIL` can be a second word.**~~ V4 allows it; the watch is on *Insider* frequency, below.
- [x] ~~Area scoring table.~~ Written 2026-09-17 — `AREA_SCORES_V1.md`, 35 neighbourhoods, three
  bands, authored from knowledge. Still owed: the two-hour hand check by five Delhi regulars
  (§4 of that file), and tagging every venue with an `area_id`. *Unblocked now.*
- [ ] **Image descriptions.** The image prompts and generation guides on disk are for the 28-card
  deck on an older factor set. Redo them against `CARD_SET_V9_IMAGE.md` and `CARD_READABILITY.md`
  — one image per card id, `A` and `B` per factor, `POL` classy and current. Until then every card
  is a placeholder. *Unblocked now — writing work.*
- [ ] **Instruction copy A/B.** Option 1 shipped (§3.7). Options 2 and 3 are in the 09-16 log
  entry if the first read of user data suggests people are answering about their personality
  rather than tonight. *Blocked on app data.*

## Held behind the latency validation (`ASSESSMENT_ENGINE.md` §6.3)

- [ ] **Latency feeding bend, group weight and abstention.** Designed (`OUTING_PLAN_ENGINE.md`
  §13.5 three levels; §5.3 firmness). Until §6.3 passes, `firmness_score` does these jobs.
- [ ] **The learning layer.** `PREFERENCE_ENGINE_V2.md` — Kalman gain, settled / unanswerable
  factors leaving the deck, hidden re-check, session gate. Not v1. Needs §6.3 plus returning users.
- [x] ~~**Refusal prefix on latency, not just hard pass.**~~ Gone — V4 has no prefix; both poles are wants.
- [ ] **Strong / soft names.** The remaining half of the old V3 proposal — *Night Climber* vs a
  softer sibling by latency on the top factor. Needs §6.3's fourth check, hysteresis, and ten
  softer names written. Lowest priority of the held items; the second word in the name now
  carries most of what this was for.

## Designed, low priority

- [x] ~~Room states.~~ Rewritten as the seven chemistry states, 2026-09-17 (§13.6.2). FRICTION
  retired; SPLIT became Tug and Trade.

## Deferred, not designed

- [ ] Heatmaps and the other front-end extras from the V2 flow doc.
- [ ] Final card images (see image descriptions above).

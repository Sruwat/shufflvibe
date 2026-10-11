# Reminders — things to come back to

Open work, not open decisions. Each line says what, why it waits, and what unblocks it. Started
2026-09-16. Strike a line when it is done and say where it went.

## The split (2026-09-17) — what it leaves owed

- [x] ~~Re-cut the simulations.~~ `splitsim.py`, 2026-09-17 — twelve scenarios re-run (entry 101).
- [x] ~~Whole-point coverage as the last shape tie-break~~ — confirmed 2026-09-17 (entry 102).
- [x] ~~`AFFIL`-low is served by the club alone~~ **Fixed 2026-09-23** by `big loud bar` (entry 122).
- [ ] **DECIDE the factor set** — retire `GAMES`; move `ROAM` from the deck to a slider; add `FOCUS` (is there one
  thing we are all pointed at) and `LEAD` (are you running tonight or being taken along). Proposed 2026-09-24, not
  decided. `POL`, `NOV` and an indoor/outdoor axis were considered and rejected by the user.
- [ ] **The skeleton's firmness multiplier** (§15.3) — a drawn position is firmer than a swiped one, but by how
  much is unset. Tune on real rooms.
- [ ] **Log every (implied line, drawn line) pair** (§15.5). It is the only direct measurement of how wrong the
  card model is per person, and it arrives free as a by-product of the feature.
- [ ] **Rewrite the `ENRG` and `CROWD` cards to be about the person, not the night.** With the skeleton carrying the
  night's shape, those two cards measure disposition — which means every magnitude tuned against the old wording
  is provisional until re-validated.
- [ ] **Does the skeleton replace the 70% plan-similarity rule outright?** §15.6 makes shape-against-plan the
  primary comparison and keeps 70% as a fallback; decide whether the fallback is worth keeping at all.
- [ ] **Measure `GLOBAL_SCALE` on the first users.** 0.26 log-seconds is a simulation figure and it
  is now the divisor for every first-time user's latency reading (§6.2). Recompute it monthly.
- [ ] **`K_SESSIONS = 3` and the recency window on `mad_personal`** (§6.2a) — both judgement. Watch
  whether a personal scale after one or two sessions helps or just adds noise.
- [ ] **Re-run §6.3's validation now that it is testable.** Under the old rank transform every
  person's `firmness_latency` had the same spread, so the check could neither pass nor fail. Use
  `firmness_latency_g` (global scale) for it.
- [ ] **Seed `card_baseline` before launch.** With appeal-driven swiping it is what stops a prettier
  photo reading as a firmer want, and it starts at zero. Seed from an internal run, or hold the
  latency term out of the ranking key until each card has ~30 observations (entry 125).
- [ ] **`K = 5` in the ranking key, and `position_baseline`** — both new, both judgement. `K` has one
  hard constraint (under 6, or latency bridges a score step); within that it is untested.
- [ ] **Add the §7.3 forced-choice screen to the front end.** Now rare (~1.4% of tied sheets) but
  still the only resolution when a session has no latency at all. Options already reworded to the
  eight vibe factors.
- [ ] **Re-run the worked examples** now that `ranked_wants` reads latency — any earlier plan where
  a member had two equal extremes was built on an arbitrary top factor.
- [x] ~~Rewrite §13.6.3 against v5~~ **Done 2026-09-23** (entry 127) — `fit` for the joiner,
  `disturbance` for the host, and the frozen / open distinction.
- [ ] **People are matched by similarity, rooms by fit.** Search and "friends you vibe the most
  with" use vector similarity between people, while the room match uses shift, reinforcement and
  chemistry — and the chemistry work says similarity is the wrong objective (an Open Night is the
  perfect match for someone firm on five or more factors). Decide which one the product means.
- [ ] **`CROWD`-low is still served by one type** — table for the night. A near-empty room is a real
  want and it currently has one answer. Watch whether a quiet-bar-at-40 variant is needed.
- [ ] **No venue type is both quiet and outward-facing.** A room that wants a calm, near-empty place
  to *meet people* (`ENRG` low, `CROWD` low, `AFFIL` low) is served only to a degree, by a rooftop
  lounge. Real hole or a want that does not exist? *Watch on the first users.*
- [ ] **The fill stage can return a stop with no venue.** If a type has one venue in the pool and an
  earlier stop used it, the later stop comes back empty (`readings.py` demo 7: two street/market
  stops, the second blank). Variety sits below score in the tie-break. Fix when the venue database
  is real, or promote variety.
- [ ] **Every `PROFILES_V1.md` magnitude** — the six rules themselves, `HIGH`/`LOW` at 70/30, the
  0.6 discount, the share term, `LINE_TARGET` 25/75. Validate against logged firings: how often did
  an inference change the plan, and was the plan better?
- [ ] **`RAMP`'s numbers** — the 60/40 thresholds, `peak_at = n − 1`, the descending sort under 40,
  and whether people can answer the `V-RAMP` cards at all.
- [x] ~~`COLLECTIVE_V1.md` §6.1, a twelfth venue type~~ **Done 2026-09-23** — `match bar`, and a
  thirteenth, `big loud bar` (entry 122).
- [x] ~~§6.3, the peak-end arc~~ **Half done 2026-09-23** — `RAMP` (entry 123) puts the peak where
  the room wants it and a neutral room now peaks a stop early and holds. **Still to do: score whole
  plans on `(peak + end) / 2`** rather than the mean of the stops, which is the other half.
- [ ] **`COLLECTIVE_V1.md` §6.2 — clock-anchored stops** (`starts_at`). An act or a match has an
  hour; a stop has only a duration. Also closes the `start_time`-with-no-screen gap.
- [ ] **`COLLECTIVE_V1.md` §6.4 — `MOVE` weighted higher as a closer in strangers' rooms** (12 → 18):
  synchrony and exertion bond independently, and a strangers' room is the one that needs it.
- [ ] **DECIDE: `FOCUS` as a vibe factor** (`COLLECTIVE_V1.md` §4). The blocker is now gone — the
  `match bar` exists (entry 122), so `FOCUS` would carry real information. Note it would be the
  **ninth** factor now that `RAMP` is in, and every card costs every user a swipe a day. Test it as
  a card on real users rather than adopting it on the regression alone.
- [ ] **Chemistry V3 §8's two unimplemented cross-rules** — Dunbar's 5+ (now with a job,
  `COLLECTIVE_V1.md` §6.6) and Simmel's pair-reads-`AFFIL`-high. Neither exists in `interplay.py`.
- [ ] **The mild-lean cliff.** A score of 55-69 has zero strength on every axis, so two mild wants
  lose to one firm opposite (TALK 12 v 60 and 55 reads 32). Decide whether the 70 / 30 threshold
  should be a ramp rather than a cliff.
- [ ] **The `ENRG` asymmetry, now isolated.** One 88 beats two firm 12s (reads 58) — the one place
  a lone enthusiast still overrules two firm opposites, kept on Barsade's evidence. It is the same
  shape as the `GAMES` and `MOVE` corrections. Decide whether Delhi behaves that way.
- [x] ~~Chemistry V3 is not wired into plan generation~~ **Done 2026-09-23** — `roomread.py` supplies
  the levels from `interplay.py`; tags and `ctx` are computed against them (entry 127).
- [ ] **`FIT_POOR` 0.40, the 0.5 reinforcement bar, and the `changed > stops/2` rule** (§13.6.3 v5)
  — all judgement. Tune on real join requests: how often does a host accept a *poor*, decline a
  *great*?
- [ ] **`ROAM` size damping, the concrete case.** A lone roamer (92) among four neutrals: V3 reads
  62 (two stops), the planner reads 92 (three). Decide which is right — does a majority of
  easy-going people get moved three times, or twice? *Watch on the first real rooms.*
- [ ] **`ROAM_BAND` 40-60 and the 55 / 45 duration lean** (§14.3.2 v2) — judgement, both to tune.
- [ ] **A reading can lose on its own axis.** The worked night's `GAMES` reading asked for *games
  available* (55-70) and the night landed in a games bar (90), because games bar and games pub tied
  at 52.7 on the readings and the tie went to individual satisfaction. Decide whether an axis's own
  reading should be allowed to lose on its own axis.
- [ ] **Tag the venue database** with a type (`FACTORS_V5.md` §4) and score every venue on the seven
  vibe axes and six preference attributes. *Data work.*
- [ ] **Re-derive the blend styles** by clustering real rooms on seven axes; `BLEND_STYLE_DATABASE_V3`
  is authored. *Blocked on app data.*
- [ ] **Weights** on both kinds are set and unmeasured. *Blocked on app data.*
- [ ] **`TALK` and `ROAM` cards** — the two a picture may fail to carry. `GAMES` may be one-ended.
  *Watch on the first users.*
- [ ] **Preference re-check cadence** (60 days) and whether behaviour should ever edit a preference
  automatically. *Blocked on app data.*

## `AFFIL` as give (2026-09-21) — open

- [ ] **Adopt the narrow give rule or not** (`AFFIL_AS_GIVE.md` §2, §6). *Needs the user.*
- [ ] **The test** that keeps or removes it: friends-first members' ratings of "to a degree" nights
  against fully-served ones, on thirty rated plans. *Blocked on app data.*

## The skeleton merge (2026-09-30) — open

- [ ] **§2a, the three-to-one case, is the rule most likely to be wrong.** Three people drew 3
  stops, one drew 1, and the room gets **2** — the largest single-person veto in the engine. It
  follows from the principle (on a count, fairness overrides influence) but watch it on real rooms.
  The fix if it is hated: let the clamp fire only when the dissenting side holds a third of the
  influence — not written that way now because a third is a number with nothing behind it.
- [ ] **`OPPOSED` −0.50 and `AMPLITUDE` 20** decide when one person's whole night is discarded, and
  they rest on nothing. The two most consequential arbitrary numbers in the spec.
- [ ] **`SIZE_CEILING`** (5 stops for a pair, 4 for three or four, 3 for five) is a guess about
  Delhi that a week of real plans would settle.
- [ ] **The "two rooms, not one plan" offer has no screen.** §5a says the app should ask rather than
  decide when two people draw opposed arcs. `VIEW_FLOW.md` records that it must; nothing designs it.
- [ ] **Log every `(drawn skeleton, merged result)` pair.** This is the data that replaces every
  constant in the merge spec, and it costs nothing to collect from day one.
- [ ] **Confirm the merge is idempotent on stable membership.** It re-runs on every join, leave and
  redraw, so a merge that drifts would corrupt a room slowly and invisibly. Assert it in a test.
- [ ] **Midpoint sampling over overlap-averaging** (§3) was chosen to preserve drawn extremes. If
  merged plans feel spiky rather than shaped, this is the first thing to try the other way.

## Factors V6 (2026-09-30) — open

- [ ] **Rewrite the `ENRG` card to be about the person, not the venue.** This was already owed, and
  the split makes it urgent rather than tidy: venue energy is the skeleton's vertical axis now, so
  an `ENRG` card that shows a loud room is measuring the wrong object. `CROWD`'s cards can simply
  be **deleted** — that axis left the deck.
- [ ] **`FOCUS` and `SPONT` have no cards at all.** `FOCUS` is easy to shoot (a crowd facing a stage
  against a circle facing each other). **`SPONT` is the problem** — every other factor is a scene
  and `SPONT` is a process, so watch it against the observation (how early people actually lock a
  plan) and drop the card if the two do not correlate.
- [ ] **The swipe game now has to justify itself on matching alone** (`FACTORS_V6.md` §6). The old
  architecture hid this risk because the cards were doing planning work whether or not anybody
  valued the matching. If users do not care who they are matched with, six cards is six too many.
- [ ] **Re-derive the six weights.** They now have exactly one job — weighting the match score — so
  they are testable for the first time: the right weights are the ones that predict which rooms
  people actually join.
- [x] ~~DECIDE the factor set (retire `GAMES`, `ROAM` to a slider, add `FOCUS` and `LEAD`)~~ Decided
  2026-09-30, entries 130–131. `GAMES` is a preference, `ROAM`/`CROWD`/`RAMP` are the skeleton's,
  `FOCUS` and `SPONT` are in, `LEAD` and stamina are observed traits, `SHOW` is out.
## Chemistry V4 and vibe names V5 (2026-09-30) — open

- [ ] **`FOCUS` pull 0.80 is the most aggressive number in the model.** It rests on gaze-following
  generalised a very long way, and it lets one gig-goer take a room of two firm refusers to 65.
  First thing to check against real rooms (`CHEMISTRY_V4.md` §4, §10).
- [ ] **`SPLIT_COST` 35** was picked only so a newly split axis outweighs a large ordinary move. No
  other justification (§8.3).
- [ ] **The size-normalisation divisors for `disturbance`** are synthetic (0.111 / 0.067 / 0.055 /
  0.046 for rooms of 2–5). Recalibrate from real rooms before the *People* sort ships, or it will
  quietly rank by room size (§8.3).
- [ ] **`SPONT` is the weakest-carded factor in the set.** Every other factor is a scene you can
  photograph; `SPONT` is a process, and "I decide at nine" has no image. Card it, measure how early
  people actually lock a plan, and **drop the card if the two do not correlate** (§5).
- [ ] **Test `Headline` / `Headliner`** for low `FOCUS` — it inverts the everyday meaning
  deliberately. Show *Headline Act* against *Front Row* and ask which one means "there's a band";
  if more than a third get it wrong, fall back to `Own-Show` (`VIBE_NAMES_V5.md` §2a).
- [ ] **Watch `ENRG` × `MOVE` and `FOCUS` × `TALK` for correlation.** Correlated factors collapse
  the name vocabulary far faster than losing factors does. If either pair collapses, one of them
  leaves the naming set even if it stays in the match score (§5).
- [ ] **Re-run `namesim.py` on real score distributions.** The 132-name vocabulary and the 41.8%
  single-name rate assume the six factors are independent, which real people will not be.
- [ ] **Does `TALK` split?** It is currently joint — whether you can hear each other is a fact about
  the room. But a room where two people shout over music while three lean in at a table is a real
  thing. If it splits, §0a's rule gains a third member and the reason has to be stated (§0a).
- [x] ~~Is `CROWD` venue-defining?~~ Moot 2026-09-30 — `CROWD` is the skeleton's now, and the
  atmosphere / venue-defining distinction is itself retired.
- [x] ~~The `GAMES` split-bridging rule and the `AFFIL`→`CROWD` buffer~~ Dead with their axes.

## Created by the split, with no document yet (2026-09-30)

- [x] ~~**The skeleton merge has no spec.**~~ Written 2026-09-30 — `SKELETON_MERGE_V1.md`, entry
  131. `ROAM`'s clamp landed there on literal stops; the drawn-firmness blank is filled and turned
  out not to be a multiplier at all (the skeleton has no true neutrals, §4a).
- [ ] **Clock-anchored stops are now blocking `FOCUS`.** A room at `FOCUS` 70+ *wants a clock* and
  the engine cannot say "this stop starts at ten". Previously nice to have; now a named dependency.
- [ ] **`VENUE_DATABASE_V1.md` is still unwritten** — schema, character tags, the supply grid, the
  four rungs, admission and eviction. `venuedb.py` and `supplygrid.py` both run and are not in the
  repo. Still the critical path.
- [ ] **The observed-traits layer still has no home.** `LEAD` (who hosts, who locks, who redraws),
  stamina (how late they actually stay) and `NOV` revisits are all measured from behaviour rather
  than swiped. Decided as a category on 2026-09-30; nothing specifies where it is stored or how it
  is used.
## Chemistry V3 (2026-09-22) — open

- [ ] **Every magnitude, now in V4** — the pulls (0.75 / 0.60 / 0.70 / 0.80 / 0.55 / 0), the
  discounts, `IMPACT_EXP` 0.6, the strength ladder, the cross-axis bonuses. Directions are
  evidenced; numbers are judgement (`CHEMISTRY_V4.md` §10). *Blocked on app data.*
- [x] ~~**`ROAM`'s rule is the weakest**~~ Moot 2026-09-30 — `ROAM` left chemistry for the skeleton.
  Watch whether size-damping matches what groups actually do.
- [x] ~~Is `MOVE` venue-defining too?~~ Yes — corrected 2026-09-22 (entry 116). Both it and `GAMES`
  are venue-defining; the atmosphere / venue-defining distinction is `CHEMISTRY_V3.md` §0a.
- [ ] **Whether `CROWD` is venue-defining as well.** A packed room is arguably a kind of place too
  (a club, a market) — but crowd is also a quality any place has at 11pm on a Saturday, so it stays
  an atmosphere axis with a low pull. *Watch on the first users.*
- [x] ~~The `MOVE` threshold~~ Retired 2026-09-22 — the indifference rule says it properly.

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

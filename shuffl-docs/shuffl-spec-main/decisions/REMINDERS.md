# Reminders — things to come back to

Open work, not open decisions. Each line says what, why it waits, and what unblocks it. Started
2026-09-16. Strike a line when it is done and say where it went.

## The split (2026-09-17) — what it leaves owed

- [x] ~~Re-cut the simulations.~~ `splitsim.py`, 2026-09-17 — twelve scenarios re-run (entry 101).
- [x] ~~Whole-point coverage as the last shape tie-break~~ — confirmed 2026-09-17 (entry 102).
- [x] ~~`AFFIL`-low is served by the club alone~~ **Fixed 2026-09-23** by `big loud bar` (entry 122).
- [x] ~~**DECIDE the factor set**~~ **Closed 2026-10-14 (entry 203).** **Settled by `FACTORS_V6.md`, 2026-09-30.** Six identity factors with `FOCUS` among them; `ROAM` left the deck and became the skeleton; `GAMES` is a preference. `LEAD` was never adopted and lives on in the observed-traits item.
- [ ] **The skeleton's firmness multiplier** (§15.3) — a drawn position is firmer than a swiped one, but by how
  much is unset. Tune on real rooms.
- [x] ~~**Log every (implied line, drawn line) pair**~~ **CLOSED AS DEAD 2026-10-14 (entry 207).**
  **The cards cannot imply a skeleton.** `CROWD`, the stop count and the peak left the deck on
  2026-09-30, and the app stopped generating a plan on 2026-10-05 — so the grid opens blank and
  there is no delta. **Replaced in `MVP_INSTRUCTIONS.md` §3b by predicted chemistry against
  outcome**, which tests the claim the deck actually makes now.
- [ ] **Rewrite the `ENRG` and `CROWD` cards to be about the person, not the night.** With the skeleton carrying the
  night's shape, those two cards measure disposition — which means every magnitude tuned against the old wording
  is provisional until re-validated.
- [x] ~~**Does the skeleton replace the 70% plan-similarity rule outright?**~~ **Closed 2026-10-14 (entry 203).** **Entry 187 removed the gates entirely** - 78% of rooms cut and 55% of users left with an empty list. There is no 70% rule to fall back to.
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
- [x] ~~**People are matched by similarity, rooms by fit.**~~ **Decided 2026-10-14 (entry 205).** **People are matched by the chemistry engine too** (`simulations/peoplematch.py`): the two rankings agree on the best friend only **37%** of the time.
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
- [x] ~~**DECIDE: `FOCUS` as a vibe factor**~~ **Closed 2026-10-14 (entry 203).** **It is one.** `FACTORS_V6.md`, weight 14.
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
- [x] ~~**The "two rooms, not one plan" offer has no screen.**~~ **Closed 2026-10-14 (entry 203).** **Screen 16.**
- [x] ~~**Log every `(drawn skeleton, merged result)` pair.**~~ **Decided 2026-10-14 (entry 206).** Now `MVP_INSTRUCTIONS.md` **§3b, item 3**.
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
- [x] ~~**Clock-anchored stops are now blocking `FOCUS`.**~~ **Decided 2026-10-14 (entry 205).** **Out of the MVP.** `FOCUS` selects venues that reliably have something on rather than routing to a performance; the clock returns with the venue partnerships in December.
- [x] ~~**`VENUE_DATABASE_V1.md` is still unwritten**~~ **Closed 2026-10-14 (entry 203).** **Written.** Schema, admission, the lexicon and the slot table are all in it.
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
- [x] ~~**`Our Table` as a gate on the join list**~~ **Closed 2026-10-14 (entry 203).** **No gates exist to be** (entry 187). It is a nudge to the host or nothing.
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

## The flow change (2026-10-10) - what entry 190 leaves owed

- [x] ~~**Make the no-wheel screen worth being on.**~~ **Answered 2026-10-12 (entry 191)** — the
  waiting screen: three group-ranked carousels and **Propose**. Was: *"to make the experience
  more entertaining for non wheel holders."* As specified a member without the wheel has a blank page
  and two buttons, which is a dead end for the four people who are not driving. The cheap version is
  read-only: show them the same SHUFFL screen with the controls removed, since they are already being
  shown every screen the wheel holder opens. Beyond that it wants an actual idea - reacting to what the
  holder is looking at, voting, or something to do while they wait.
- [x] ~~**Sign off the build-my-own meter set.**~~ **Settled 2026-10-13 (entry 198)** — five
  meters, three exact readouts, five badges, and not a factor name among them.
- [ ] **Does *how it looks* spread across the admitted set?** `HERIT` was dropped because almost
  everything in South Delhi is new, so the meter would sit pinned for most nights. **`SCEN` should
  spread and that is a prediction, not a measurement** — twenty minutes against the developer's
  enriched file, no users needed. Same check for *how dressed up*.
- [ ] **Widen the `MOVE` keyword list anyway.** It is no longer a meter, but it still feeds the deck,
  chemistry and the venue pros and cons, and at **96%** type-prior it is barely measured anywhere.
- [ ] **Where the 22:00 cut should actually sit.** `CROWD`'s two slots split at 22:00 (entry 196),
  which is a guess. **It should sit where the type curves diverge most, and we have the curves** —
  an hour's work, worth doing before launch rather than after.
- [x] ~~**Measure whether four bands discriminate.**~~ **Done 2026-10-13 (entry 197,
  `simulations/meterband.py`).** Blindness 6.5%, jitter 89.5% on the band; 28.8% and 51% on the word.
  The set stands; `FOCUS` stays a badge.
- [ ] **Check the hollow percentages against the real enriched database.** They rest entirely on how
  many keyword hits a factor gets across five reviews, which is assumed in the sim and
  **measurable the moment the developer's file exists** — no users needed. First thing to check
  against it.
- [x] ~~**A venue closed at the stop's hour, in build-my-own.**~~ **Decided 2026-10-14 (entry 199):
  blocked, with the reason stated.** Warn where we are guessing about the user; block where we know a
  fact they do not.
- [ ] **The venue photo library.** Owner media for the 296 admitted venues is a one-time ask and the
  only thing that makes list thumbnails free. Until it exists the placeholder is the launch state. The
  gold capture flow is the other half and it is a December item.
- [x] ~~**A sixth privacy toggle - tonight's shape.**~~ **Decided 2026-10-14 (entry 205).** Not a toggle. **The vibe stats are public with no toggle at all**, and tonight's shape is public to friends with **an Instagram-style per-person exclusion list**. *Past events* is flagged as the one that should keep a toggle and is the user's call.
- [ ] **Presence.** The green / grey online dot on the friend list is the first presence system in the
  app and nothing specifies one.
- [x] ~~**Friends who have not played today.**~~ **Decided 2026-10-14 (entry 205).** Greyed out so it is obvious they will have to play, **and still addable**.
- [x] ~~**One gathering or two.**~~ **Decided 2026-10-14 (entry 205).** There is one door and it is on the SHUFFL screen — the Messages button was cut by entry 203.
- [x] ~~**Does the five-minute vibe clock cover the deck, or only opening the app?**~~ **Decided
  2026-10-12 (entry 192): only opening the app.** It is a response clock and stops at the first card,
  or at the skeleton for somebody who has already swiped. After acceptance there is no clock at all.
- [x] ~~**What an expired invite looks like in the notifications bar.**~~ **Drawn and decided
  2026-10-13 (entry 193, screen 50)** — it expands in place, says what happened and what is left,
  and offers *Find the room* only when the night actually went public.
- [ ] **Confirm profile and settings stay reachable on the locked home screen.** The standing rule
  excepts *“profile settings and messages/social”*; the 2026-10-12 instruction said *“the
  only thing accessible is messages”*. Kept as the standing rule for now, because somebody who
  just declined an invite may want to turn off the notification that brought them there.
- [x] ~~**Sweep the drawn set for retired concepts.**~~ **Done 2026-10-13 (entry 195)** — ten
  screens fixed, four stamped RETIRED. **Re-run it after any retirement**: the screens that go stale
  are the ones a change is *not* about, so they are never in the redraw set.
- [x] ~~**Cap the proposal queue.**~~ **Decided 2026-10-14 (entry 199): five per person, no expiry,
  no answer required** — everybody in a capsule room is on a call, so the coordination is done out
  loud.
- [ ] **No recourse mid-night.** The lock is terminal, so a shut venue or a two-hour queue leaves only
  *End plan and start over* — redrawing skeletons and re-inviting. Probably right for a first
  release; **the first real night out will find it.** The minimal softening is a **status change, not
  an edit**: let the chat mark a stop skipped and have the active plan screen reflect it.
- [x] ~~**Does voice really end at the lock?**~~ **Decided 2026-10-14 (entry 200): yes, and it moves
  to the group chat.** The lock is a decision, not a departure.
- [ ] **Give the group chat a call option.** It has a name, a message bar and an insights panel, and
  **no call** — which entry 200's argument depends on. Without it, voice is deleted at the lock
  rather than relocated. Small: the group and its membership already exist.
- [x] ~~**A dormant state for the active plan screen.**~~ **Drawn 2026-10-14 (entry 201, screen 53)**
  - stops with pros and cons, members, insights, a countdown and Ditch. Nothing live until the night.
- [x] ~~**Adding people mid-build, when venues are already picked.**~~ **Already answered 2026-10-14
  (entry 201): the rebuild rule is general.** Any change to the set of drawers re-runs the merge;
  skeletons survive, venues and plan do not.
- [ ] **A conditional line on the add-friends sheet.** `SIZE_CEILING` caps stops by group size, so
  adding a fifth to a group of four costs a stop — **but only if they had merged to four**
  (entry 202). Show it when it would really cost one, never otherwise.
- [ ] **Re-check `SIZE_CEILING` on real groups.** Steiner-reasoned, never measured, and the solo entry
  added 2026-10-14 is uncapped by assertion rather than by evidence.
- [ ] **Sweep the flow doc the way the screens were swept.** Entry 204 found four passages reading as
  live instruction under banners saying the flow was retired. **A section banner does not inoculate
  the prose below it** — somebody reading for one thing lands in the middle. The four found are
  marked; nothing says the rest were checked.
- [ ] **Closing hours are not a fact for late venues (entry 203).** Delhi clubs list 01:00 and run to
  03:00 or 04:00 on Friday and Saturday. **Entry 199 blocks a stop whose venue is listed shut, on the
  argument that an opening hour is a fact** — for a club it is a claim, and a wrong one. Needs a
  per-type close confidence, and reviews corroborating it (*“still going at three”*).
- [x] ~~**Cross-factor inference lines for a profile.**~~ **Written 2026-10-14 (entry 208)** — six
  pairs, in `CHEMISTRY_LINES_V1.md`, with the firing rule and the disagreement line.
- [ ] **Banner the three engine docs still unbannered.** `CHEMISTRY_V4.md`, `ASSESSMENT_ENGINE.md` and
  `PREFERENCE_ENGINE_V2.md` carry no supersession notice. The first three were done 2026-10-14
  (entry 208); **these were not checked line by line and may be clean.**
- [ ] **Test the pair readings on real people before they ship.** Six pairs × four quadrants is a
  lot of claims about somebody, written from an armchair. **The failure mode is a confident sentence
  about a person that they do not recognise**, which is worse on a profile than anywhere else in the
  app.
- [ ] **Show the people-chemistry score as a line, not a number — or rescale it.** Measured
  (entry 205): the figure sits between **84% and 90%** for people who are nothing alike, so as a
  displayed number it trains users to ignore it. `CHEMISTRY_LINES_V1.md` already writes the lines.
- [x] ~~**Log the three observed traits from launch**~~ **Decided 2026-10-14 (entry 206).** **Yes.** Gathered with the other three unbackfillable obligations into `MVP_INSTRUCTIONS.md` **§3b**, which is the document a developer builds from — none of the six was in it.
- [x] ~~**Decide *past events*.**~~ **Decided 2026-10-14 (entry 206).** **Keeps its Everyone / Friends only / Nobody toggle.**
- [ ] **The drink-of-the-night list.** One drink per night character, written by hand, same shape as
  the vibe names. Small, and it does not exist yet.
- [ ] **Decide the voice transport, and decide it separately for public rooms.** A five-person mesh is
  cheap and **peer-to-peer exposes every participant's IP to every other**. Among friends that is what
  a group call already implies; **in a public room of strangers at midnight it is not**, so public
  rooms need a server mixing the audio. Cheap now, expensive to retrofit.
- [ ] **The rest of the call, which is unspecified.** Room capacity as a number; push-to-talk against a
  toggle; what the speaking ring does when two people talk at once; any moderation beyond the holder's
  remove cross; recording and consent. **The camera decision is written down and the call it replaces
  is not.**
- [ ] **Where “See all presets” goes on the waiting screen.** The preset shelf has an escape hatch
  because a mis-read of somebody's factors silently narrows their night. A group-ranked carousel of
  three to five has the same failure and currently no hatch.
- [ ] **Does the time window need a different control inside a room?** Distance and budget re-rank the
  carousels; the window invalidates every drawing and resets the room. Two outcomes that far apart
  should not sit behind one filter chip.
- [ ] **When the shuffle button renders.** On a list of three rooms a control promising new options
  returns the same three. It should appear only when there are more rooms than the list shows —
  measured mean at launch volume was **0.6 rooms per user** with the gates on.
- [ ] **The capsule room once a plan exists.** Screen 36 shows the pre-plan state, where the card above
  the controls says what the wheel holder is doing. Once every stop has a venue it should carry a
  **View plan** button like screen 29. Undrawn.
- [ ] **Who holds the wheel if the holder leaves.** No rule. Pass it to the longest-present member, or
  dissolve the group.

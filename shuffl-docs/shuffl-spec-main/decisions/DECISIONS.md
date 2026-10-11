# SHUFFL — Decision Log

Track decisions made about the app here as they're made. One entry per decision.

## Format

```
## [YYYY-MM-DD] Short decision title
**Decision:** What was decided.
**Context:** Why this came up / what prompted it.
**Alternatives considered:** What else was on the table, if relevant.
```

---

## [2026-08-14] Front-end aesthetic direction: Chrome Pulse
**Decision:** Chrome Pulse is the chosen visual-design direction for the app — near-black holographic look, cyan/violet duotone accent, frosted glass cards with glowing chrome edges, tracked mono headers, outlined pill buttons.
**Context:** Chosen after comparing three full aesthetic treatments (Neon Floor, Paper Vibes, Chrome Pulse) applied across all 24 screens from the Front End Final V2 spec, generated in the [SHUFFL — Front End V2 Screen Gallery](https://claude.ai/code/artifact/e9518cbb-3f17-4b2d-8f8e-cfc7bcb4b07b) artifact.
**Alternatives considered:** Neon Floor (dark club, saturated glow gradients, gradient-filled pill buttons); Paper Vibes (warm cream/paper, ink-black serif, flat hairline cards).

## [2026-08-14] "Front End Final V2" is the canonical flow reference ("the bible")
**Decision:** The `Front End Final V2` document is the source of truth for the app's front-end flow going forward. Any future change to a screen, flow, or feature should be checked against it, and any decision that changes what it describes should be logged here and (if it changes the flow itself) reflected back into the spec.
**Context:** A clean copy of the doc's full text has been saved alongside this log at [VIEW_FLOW.md](VIEW_FLOW.md) (renamed from `FRONT_END_V2_SPEC.md` — see the naming decision below) so it's available for reference in any future session, not just this one. It covers: Onboarding, After Opening the App, Play Button (Host/Join/Create), Active Plan Screen, Venue Flow, Add People Flow, Background Colour, Music Flow, Messages/Social Flow, Home Page, Task Bar, Profile Screen, Search Bar Flow, Outing Plan Flow, View Profile Flow, Settings Flow, and the new Dish/Drink Recommendations section.
**Alternatives considered:** N/A — this formalizes which of the two uploaded docs (`Front End Final (FE)` v1 vs `Front End Final V2`) governs going forward; V2 supersedes V1.

## [2026-08-14] Naming: "Front End Final V2" is now called "View Flow"
**Decision:** Going forward, the `Front End Final V2` document/spec is referred to simply as **View Flow**. The reference copy has been renamed from `FRONT_END_V2_SPEC.md` to `VIEW_FLOW.md`.
**Context:** Requested to give the canonical flow doc a shorter, standing name rather than repeating the full "Front End Final V2" filename each time.
**Alternatives considered:** N/A — pure naming/alias decision, no change to the doc's content or status as the canonical reference.

## [2026-08-14] View Flow updated: "What your friends are up to" room-card refinements
**Decision:** `VIEW_FLOW.md` updated to match `Front End Final V2 (1).docx`, which revised the **Home Page → "What your friends are up to"** paragraph only (everything else in the document was identical). Three changes: (1) room name + host name now display in the explicit format `[room name] by [host name]`; (2) the join button on a friend-hosted room card moves from beside the room name to the bottom of the card; (3) new rule — the join button only appears if the room still has remaining capacity *and* the user matches the blend-style criteria; if either fails, no join button is shown.
**Context:** User uploaded a follow-up version of the spec (`Front End Final V2 (1).docx`) and asked for a diff against View Flow, with the markdown copy updated if anything changed.
**Alternatives considered:** N/A — this is a spec correction/clarification from the source document, not a design choice made here.

## [2026-08-26] Vibe is not hideable; privacy toggles cover history only
**Decision:** Today's vibe, overall going-out type and vibe score are computed from the swipe game and are **always visible to other users** — they cannot be hidden or edited. User-controlled visibility toggles (Everyone / Friends only / Nobody) apply **only to history**: past events/outing plans and vibe history.
**Context:** View Flow previously specified visibility toggles for all five of today's vibe, vibe score, going-out type, vibe history and past events. That contradicts the core mechanic — rooms, blend styles and matching all run on seeing each other's vibes, so a hidden vibe would break participation. A backend engineer building from the old text would have implemented five toggles including one that breaks the room flow. `VIEW_FLOW.md` updated in both the Search Bar Flow and Settings Flow sections.
**Alternatives considered:** Keeping the vibe toggle and degrading gracefully when hidden — rejected, because a user with a hidden vibe can't meaningfully be matched into a room, so the feature would be misleading rather than private.

## [2026-08-26] Venue reporting needs its own opt-out, separate from heatmaps
**Decision:** Settings gets a distinct control — *"Contribute anonymised visit data to venue reporting"* — governing whether a user's visits feed SHUFFL for Business dashboards. It is independent of the heatmap contribution opt-out and of the history visibility toggles. Every opt-out in the app is purpose-specific; turning one off does not turn off another.
**Context:** Under India's DPDP Act consent is purpose-specific, so a social-visibility setting cannot double as commercial-data-sharing consent. The heatmap opt-out already established this pattern in View Flow; venue reporting follows it.
**Alternatives considered:** Reusing the existing visibility toggles — rejected, since those govern user-to-user visibility and now cover history only, and conflating the two would not survive a compliance review.

## [2026-08-26] Venue dashboards show aggregates only, never individuals
**Decision:** SHUFFL for Business dashboards display patterns, never people. Three rules: (1) **minimum group size** — no breakdown by vibe, age, gender or area displayed below ~25 distinct users, totals only beneath that; (2) **never individual-level** — no single-visitor rows, no persistent customer IDs, nothing letting a venue track one person across visits; (3) **separate opt-out** respected. Texture comes from granular aggregates and clearly-labelled composite personas, not real individuals.
**Context:** A draft of `SHUFFL for Business` proposed showing venues individual rows ("a 24 year old male party monster from Defence Colony visited your venue"). That is personal data under DPDP, identifiable in practice at a venue that saw twenty people that night, contradicts the app's own heatmap thresholds, and would undermine the "we only license aggregate data" position that enterprise data buyers audit.
**Alternatives considered:** Individual-level rows with user consent — rejected as disproportionate; venues act on patterns, not single visitors, so the added risk buys no added utility.

## [2026-08-26] Cross-venue insights: customers yes, competitor business no
**Decision:** Venue dashboards may show where a venue's *own* customers also go, but never another venue's business metrics. Banned: visit frequency at a named competitor, comparative performance, and churn/migration attribution ("customers who left you now go to X"). Named venues only above a volume threshold; below it, show category and area. Overlap stats are symmetric (if A sees B, B sees A), and venues may opt out of appearing by name in others' dashboards. Sequential insight ("your customers arrive from a cafe and go on to a bar; you're their 8pm stop") is preferred over competitive overlap — more actionable, names nobody.
**Context:** Both venues in any cross-venue insight are typically paying customers. Selling one customer's performance data to a competitor is a trust failure that ends the relationship and spreads by word of mouth in a market where venues are signed one at a time.
**Alternatives considered:** Dropping cross-venue insights entirely — rejected, as the sequential version is genuinely valuable and carries almost no risk.

## [2026-08-27] Beachhead segment is named "Delhi's going-out set"
**Decision:** The launch target segment is referred to as **"Delhi's going-out set"**, defined behaviourally as *"the one person in every friend group who picks the place."* Demographically: 18–30, South Delhi and Gurugram, out two or more nights a week. This replaces "the high-spend Delhi clubbing crowd" wherever it appears.
**Context:** The old phrasing had three problems. It was too narrow — "clubbing" implies nightclubs, but the product covers brunch, cafés, culture and dinner equally. "High-spend" is transactional and reads crudely in a pitch. And neither conveyed the actual strategic reason for choosing the segment. The behavioural definition does: **the person who picks the place is the person who opens the room**, so the beachhead maps directly onto the app's viral mechanic. Every host brings their whole group.
**Alternatives considered:** "The South Delhi social circuit" (geographic, but excludes Gurugram and says nothing about influence); "nightlife tastemakers" (overused, and again implies nightlife only); "high-frequency social core" (accurate but too clinical for a deck).

## [2026-08-28] Factor weights are per-vibe, not global — the Priority Engine
**Decision:** Matching no longer uses one global `FACTOR_WEIGHTS` vector for all users. Each vibe gets its own weights, **derived from its factor vector rather than hand-authored**: `w[f] = (1-α)·GLOBAL[f] + α·salience(f)/Σsalience`, where salience is how far the vibe sits from neutral on that factor — high-side only for `SHORTFALL_ONLY` factors plus `VALUE`/`CONV`, both directions for `SOC`/`CAS`/`PREM`. Ship at **α = 0.35**. Groups derive priorities from the blend style's own vector, never by averaging members' weights. Full spec in §5.3.1 of `OUTING_PLAN_ENGINE.md`.
**Context:** Global weights describe the average Delhi user, so any vibe built on a low-weighted factor — `PLAY` 5%, `CULT` 4%, `FUN` 6% — was scored mostly on factors it does not care about, partially defeating the point of having 30 vibes. The asymmetric penalties already prevent outright inversion of the top result; the damage is thin margins and wrong mid-shortlist ordering. For a **Chaos Collector** the arcade leads a live-music venue by only **3.2 points** under global weights — inside the range of the ±0.05 popularity/novelty bonuses and −0.10 travel penalty applied immediately after, so a marginally closer live venue takes the slot. Priority weights widen that to **8.9 points**. Since Stage 3 keeps the top 8 per slot and the sequencer draws combinations from all of them, ordering below rank 1 decides plans too: the Chaos Collector's second choice moves from live-music to a nightclub, and a Game-On Friend's from live-music to an outdoor venue. At α = 0.35 a Chaos Collector's `PLAY` weight goes 5%→14% and `FUN` 6%→13%, while `FOOD` falls 16%→10%. α = 0.5 puts at most 40% on any one factor; α = 0.7 reaches 50% and starves the smallest factors to 1%.
**Alternatives considered:** Hand-authoring 30 weight vectors — rejected: 300 more numbers to maintain, and they would drift out of step with the vibe definitions. Multiplying global weight by salience instead of blending additively — rejected: it inherits the global floor, so `PLAY` reaches only 8% even for a `PLAY` 100 vibe. Splitting `SOFT` into calm and scenic — deferred: correct but invalidates the locked V4 card set, every venue score and the weight table.

## [2026-08-28] Two vibe gaps identified; outdoor-active outings currently unreachable
**Decision:** Two structural holes are recorded against the 30-vibe set, to be filled at the next card-set revision rather than now. (1) **No active-and-scenic vibe** — the maximum `SOFT` among all vibes with `PLAY` ≥ 60 is **25**, so `PLAY` and `SOFT` are near-perfectly anti-correlated and no pair or trio of vibes can produce an outdoor-active plan. Proposed addition **The Daylight Mover** — `SOC 55, SOFT 55, FOOD 30, PLAY 80, CULT 25, CAS 70, FUN 55, PREM 25, VALUE 30, CONV 20` — covering run clubs, padel, cycling, trekking and day trips. (2) **No culture-and-high-energy vibe** — max `SOC` among vibes with `CULT` ≥ 70 is **45**, max `PLAY` is 35, so all four culture vibes are seated and contemplative and the gig-goer has no archetype. Proposed addition **The Front-Row Regular** — `SOC 75, SOFT 25, FOOD 30, PLAY 60, CULT 85, CAS 40, FUN 70, PREM 45, VALUE 50, CONV 35`. Each new vibe requires a matching blend style or it snaps to an indoor one — two Daylight Movers currently resolve to *Chill Fun Circle*, routing them to a games bar.
**Context:** Root cause of gap (1) is a factor definition, not a missing vibe: `SOFT` is defined as "pretty, calm, aesthetic" and so bundles scenery with low energy, making "scenic and active" inexpressible in the vector. Any vibe with `PLAY` 85 and `SOFT` 75 would read as high-energy-and-calm, which the factor definitions call incoherent. The Priority Engine does not fix this — reweighting re-ranks venues against vibes that exist but cannot manufacture a vibe shape none of the 30 has; an outdoor venue never wins a slot for any vibe not already inclined toward it. Live music and daytime/outdoor activity are both genuine pillars of Delhi going-out culture.
**Alternatives considered:** Riding outdoor on low `CONV` plus high `PLAY` with venue-side tagging — viable as an interim, but cannot distinguish "far and outdoors" from "far and indoors". Adding the vibes immediately — rejected for now: the V4 card set is locked and each new vibe needs a champion card.

## [2026-08-28] Vibes and Blend Style databases moved into decisions/
**Decision:** `Vibes Database` and `Blend Style Database` are now `decisions/VIBES_DATABASE.md` and `decisions/BLEND_STYLE_DATABASE.md`. They were previously external companion docs referenced by `OUTING_PLAN_ENGINE.md` but stored nowhere in the repo.
**Context:** Both are load-bearing — room matching gates on blend-style similarity thresholds in `VIEW_FLOW.md`, and plan template selection filters on `blend_style` in `OUTING_PLAN_ENGINE.md` §5.2 — yet neither was recoverable from the decisions folder, which made several engine questions unanswerable without re-uploading. `Factors and Vectors` and `Image Factor Scores` remain external and should follow.

## [2026-09-02] Factors are only what a card can test; sliders are gates, not factors
**Decision:** `VALUE`, `CONV` and any night-length measure are removed from the factor set. Budget, distance and duration are **manual slider inputs** (`Front End Final V2` lines 145, 141, 107) and already act as hard gates in §5.2. The rule going forward: **sliders set gates, cards set factors, nothing appears in both.**
**Context:** The old ten-factor set spent `VALUE` 12% + `CONV` 15% = **27% of all matching weight** re-deriving what the user had typed in directly, and the two could contradict each other with nothing to resolve the conflict — cards saying `VALUE` 20 against a slider set to ₹25k. A draft V2 factor set repeated the error by adding a `STAMINA` factor before the duration slider was spotted.
**Alternatives considered:** Keeping them as soft preferences alongside the gates — rejected, since a factor duplicating a stated constraint can only add noise. Weighting them down instead of removing — a half-measure that keeps the contradiction.

## [2026-09-02] Factor set V3 — nine card-testable factors
**Decision:** `SOC · ENRG · SCEN · FOOD · POL · NOV · PLAY · LIVE · HERIT`, weighted 16/13/13/15/14/9/8/7/5. Shortfall-only: `SCEN` `FOOD` `PLAY` `LIVE` `HERIT`. Bidirectional: `SOC` `ENRG` `POL` `NOV`. Genre is a **venue tag**, not a factor.
**Context:** Four changes from the old ten. **`SOFT` splits into `SCEN` + `ENRG`** — it bundled scenery with low energy, which made "scenic and active" literally inexpressible and was the root cause of the outdoor gap. **`FUN` dissolves** into `SOC` + `ENRG` + `POL`; it was never its own dimension. **`PREM`/`VALUE` become `POL`** — in the old data `VALUE ≈ PREM − 3` across all 30 vibes, so one was a wasted dimension. **`CULT` splits into `LIVE` and `HERIT`** — four vibes scored 75–95 on it while wanting a comedy club, a techno warehouse, Mehrauli ruins and a Chandni Chowk food walk. The Bollywood Extrovert was the proof: it sat at `CULT` 30, the model treating a Bollywood night as though music barely mattered; it now sits at `LIVE` 70.
**Alternatives considered:** Staying at eight factors and accepting the `CULT` conflation — rejected once comedy was added as a vibe and had nowhere coherent to sit. Genre as a continuous factor — rejected: Bollywood and techno cannot sit on one axis, you cannot be "60% of the way" between them.

## [2026-09-02] What is and is not a vibe
**Decision:** A vibe is **a mood you could be in tonight that produces a multi-stop plan**. Four things that look like vibes are not:

| Not a vibe | What it is | Where it lives |
|---|---|---|
| pre-game, 2am parathas | a **phase** | template slot |
| budget, duration, distance | a **stated constraint** | sliders |
| sober, vegetarian, halal | a **consumption constraint** | profile preference |
| run club, padel league | a **standing membership** | not daily; separate feature |

**Context:** Four separate drafts each smuggled in a non-vibe. "2 AM Paratha Pilgrim" described an ending, not a night. "Zero-Proof Regular" caused a concrete failure: a sober user could never reach a nightclub room, because not drinking was welded to a low-`ENRG` vector — when a sober person can be a Chaos Collector on Saturday and a Date-Night Dreamer on Sunday. Sobriety cuts across every vibe rather than being one. "Run-Club Riser" failed twice: a standing commitment rather than a daily mood, and it produces a degenerate one-stop 6am plan with no bookable venue.
**Alternatives considered:** A "no strong preference tonight" vibe — rejected on the same grounds as Plan-as-We-Go: a neutral vector has near-zero salience under the priority engine, so its weights collapse to global and it can never express a preference.
**Compliance note:** drinking preference can proxy for religion. Treat as sensitive under DPDP — never on profiles, never in venue analytics, its own opt-out.

## [2026-09-02] Blend styles come from group chemistry, not vector averaging
**Decision:** Blending uses three combination rules plus a chemistry state, replacing the mean. **PEAK** (`ENRG` `PLAY` `NOV`) — one enthusiast pulls the group, 55% of the way from mean to max. **CONSENSUS** (`SOC` `SCEN` `FOOD`) — agreement amplifies past the mean, scaled by how much they agree. **FLOOR** (`POL`) — the least dressed-up member binds, because underdressed gets you refused at the door while overdressed does not. Plus a group-size lift on `SOC`/`ENRG` only. Two new per-vibe numbers drive a chemistry state: **SPARK** (one clear driver, energy ignites), **STEADY**, **DRIFT** (nobody drives — the app supplies structure: `PLAY` +12, `NOV` −10), **FRICTION** (too many leaders — channel into activity), **SPLIT** (divergent attention — shared activity bridges it).
**Context:** Averaging cannot produce emergence. Four Deep-Chat Drinkers average to a Deep-Chat Drinker and stay quiet, but four chatty people at a table are genuinely louder than one. Grounded in interpersonal complementarity (Kiesler 1983; Horowitz et al. 2006 — dominance is complementary, affiliation is similar, so **different axes must combine by different rules**), group polarization (Moscovici & Zavalloni 1969), emotional contagion (Barsade 2002) and shared information bias (Stasser & Titus 1985). Application to nightlife is extrapolation, not established research. Validated: three low-energy but decisive vibes blend to `ENRG` 36 from a mean of 25; the same energy with **no driver** produces DRIFT instead.
**Alternatives considered:** Pure averaging — rejected, cannot reach the mainstream blend region at all. Hand-authoring blend styles — replaced by clustering 8,000 simulated realistic groups, which independently reproduced six existing hand-written styles (Golden Hour Circle, Playful Chaos Crew, Game Night Out, Quiet Taste Club, Indie Soul Evening, Low-Key Loyal Table) and surfaced *Friday Table Crew* — the ordinary excellent Friday — on its own.

## [2026-09-02] Agency is a user trait, not a vibe attribute
**Decision:** **Agency** (does this person drive the night) lives on the **user profile**, learned from host-versus-join ratio and plan-lock behaviour, with a neutral prior for new users. **Affiliation** (facing the room versus the table) stays on the vibe. Neither is card-tested.
**Context:** Putting agency on the vibe made picking "Chaos Collector" today automatically turn you into a decider, which is wrong — a shy person who feels chaotic is still shy. The error showed as correlation: agency ran 0.65 with `ENRG` and 0.67 with `SOC`, because it was encoding "how loud is this vibe" twice. Only one vibe in thirty was high-energy-and-low-agency, though "down for anything, never plans anything" is one of the most common friends anyone has. `VIEW_FLOW` already separates hosting from joining, giving a direct behavioural measure that needs no cards and cannot correlate with energy by construction.
**Alternatives considered:** Adding low-agency vibes to fix the distribution — rejected, their vectors are neutral on everything and therefore unmatched-able.

## [2026-09-02] Swipe game rebuilt: 18 cards, four-way, factor probes
**Decision:** Replace the 28 vibe-champion cards with **18 cards — two per factor — on a four-way swipe** (LOVE / YES / NO / HATE). Cards test factors directly; the response *is* the reading. Card count is fixed at 18 regardless of how many vibes exist.
**Context:** Simulated against the champion design: 18 cards reach **80.5% top-1 / 98.0% top-3** versus **58.4% / 89.0%** for 28 champion cards on the same four-way scale. Even 9 cards (one per factor) beat the full champion deck. Diminishing returns past two per factor — three buys 4 points, four buys nothing. Note the four-way scale alone, holding cards fixed, bought only ~6 points and a 21% card reduction; the gain comes from **redesigning cards for the scale**, not the scale itself. Watch the UX cost: a four-way choice takes longer per card, so 18 four-way cards may not feel faster than 28 binary ones.
**Alternatives considered:** Keeping 28 champion cards on four-way — worse on every metric. Factor probes positioned at the population centroid — tested and failed badly (39% top-3), because a centroid card scores similarly for everyone and carries almost no information.

## [2026-09-02] Scoring is plain symmetric L1 — clever variants tested and rejected
**Decision:** `HATE 12 / NO 38 / YES 62 / LOVE 88`, average the two cards per factor, then **plain symmetric subtraction** against each vibe, smallest total wins. No weighting, no asymmetric penalties, no confidence adjustment.
**Context:** Two "improvements" were tested and both lost. **Reusing the asymmetric shortfall rule cost 12 points** — the plan-matching penalty and the identification distance are different problems. Shortfall-only is right for "does this venue suit you" (a venue exceeding your standard does not hurt); it is wrong for "which vibe are you", because a vibe scoring far above your reading is strong evidence you are not it. **Discriminative weighting added nothing** (84.2% vs 84.9%) because all nine factors have near-identical spread across the vibes, 0.87–1.12 once normalised.
**Alternatives considered:** Bayesian posterior over vibes with adaptive card selection — works, but unnecessary once cards are factor probes, and cannot be scored by hand during a live test.

## [2026-09-02] Vibe values nudged off the swipe-bin boundaries
**Decision:** Every vibe value sits at least 4 points from the bin cuts at 25 / 50 / 75. Forty values moved, none by more than 4 points, every value kept its original bin.
**Context:** Forty of 270 values sat on or within 4 points of a cut — Chaos Collector's `FOOD` at exactly 25, Deep-Chat Drinker's `POL` at exactly 50 — so a single misread flipped them into the wrong bin. Sundowner Seeker had four such values, Long-Table Settler and Deep-Chat Drinker three each. Worth roughly +1 point of accuracy for no cost, concentrated on the most fragile vibes.

## [2026-09-02] Adaptive tie-breaker cards when the top two are close
**Decision:** After the base 18, if the top two vibes are within 25 points, show **2–3 bespoke cards built to split that specific pair**, from a pre-built library of ~12 covering the commonest confusions. Fall back to extra probes of the discriminating factor for pairs outside the library.
**Context:** Worth about **+3 points** at realistic card quality and **+3.5** at poor quality, for 1.3 extra cards on average. Bespoke cards beat extra factor probes by **7 points** at poor quality, because a repeat probe inherits the same contamination that caused the confusion — it asks the same question a third time and gets the same wrong answer. Deployed estimate: **≈85% top-1, ≈98% top-3, 19.3 cards average**, ranging 68%–94% depending entirely on how cleanly the cards read. The pairs needing breaking were **not** what bin-signature analysis predicted: Menu-Mood Maker / Long-Table Settler differ in one digit but by two full levels and never appear; the real confusions are Indie/Punchline, Off-Duty Gourmand / Old-Delhi Wanderer, Court Regular / Game-On Friend. **Bin adjacency is not practical confusability.**
**Alternatives considered:** Firing on a 45-point gap — rejected, triggered on 62–85% of users and became a mandatory second round.

## [2026-09-02] Card writing rules — describe the appeal, vary only on the neutral
**Decision:** Two rules for every card. **(1) Describe what an enthusiast loves, never the friction** — "a packed room with the music up and the whole place moving together", not "you can barely move and everyone's shouting". **(2) The two cards in a pair must differ only on something that is not itself a measured factor** — time of day, arriving versus staying, one dish versus the whole menu. Never on price, formality, crowd size or solitude.
**Context:** Both rules came from live failures. The first draft described the *sceptic's* view, so even people who love a crowded room swiped no and the card measured nothing. The rewrite then failed differently: **six of nine pairs varied on another factor** — SOC on formality (`POL`), ENRG on solitude (inverse `SOC`), SCEN and FOOD on price (`POL`), LIVE and HERIT on crowd (`SOC`). Two test subjects both produced pair disagreements that were the contamination, not real ambivalence. The factors are factors *because* people have strong opinions about them, so using one to vary another guarantees leakage. A third round caught "people are happily standing" (comfort) and "knowing its history is part of why you like it" (intellectual engagement, not age).
**Consequence:** the second card in a pair is no longer a contamination canceller but a **second clean sample** — worth about +4 points through noise reduction. A large disagreement inside a pair is now diagnostic of a card defect, not of the person.

## [2026-09-02] Vibes Database V3 — 35 vibes, gap-driven rather than archetype-driven
**Decision:** Five vibes added and `Court Regular` `POL` raised 55→72. New: **The Play-and-Plate One** (`FOOD`+`PLAY`), **The Monument Wanderer** (`SCEN`+`HERIT`+`POL`), **The Full-House Feaster** (`SOC`+`FOOD`+`ENRG`), **The Dressed-Up Front Row** (`POL`+`LIVE`+`SCEN`), **The Big-Night Regular** (high energy at mid polish, no other agenda). Uncovered factor pairs fall from **14 of 36 to 6**.
**Context:** Two real testers exposed the method. One scored `FOOD` 88 and `PLAY` 88 and matched nothing within 163 — no vibe combined those, the highest `PLAY` among food-led vibes being 35. Checking all 36 factor pairs systematically then found thirteen more holes, disproportionately involving `HERIT` (6), `LIVE` (5), `PLAY` (4) and `FOOD` (4) — the factors with fewest high-scoring vibes. The Big-Night Regular came from the second tester: sorting every high-energy vibe by polish showed nothing at `ENRG` 80+ with mid polish and no other agenda, plausibly the most common night out in Delhi. That is the mainstream-versus-subculture imbalance flagged earlier and not previously fixed. Testers moved from 107→47 and 163→79.
**Alternatives considered:** Filling all 14 gaps — rejected as fitting a matrix rather than a market. The six left open all involve `LIVE` or `HERIT` in combinations genuinely thin in Delhi; `FOOD`+`LIVE` (dinner with live music) and `PLAY`+`LIVE` (karaoke) are the most arguable and are first in line if the group test surfaces people who land badly.
**Note:** adding vibes is now free — the 18 cards test factors, so card count does not move with vibe count.

## [2026-09-02] Group fairness: relax the threshold per-member, flexible first
**Decision:** §6's single `FAIRNESS_THRESHOLD` becomes per-member, each member's floor rising with their preference sharpness. When no combination satisfies everyone, relax **the member with the most slack above their own floor**, one at a time, rather than dropping the threshold for everybody at once.
**Context:** The existing constraint already guarantees every member a stop above 0.72, and testing showed that guarantee is doing the work — weighting stubbornness into either the threshold or the objective changed outcomes by less than 0.005 across three separate simulations, because `max over stops` in a three-stop plan is very forgiving. The only moment someone genuinely loses out is **during relaxation**, where the current code short-changes everyone equally. Total compromise is unchanged; only its distribution moves, toward whoever converts it into least unhappiness.
**Alternatives considered:** A card testing stubbornness — rejected as structurally impossible: a swipe measures what you like, while stubbornness is how you react to being overruled, and an image can show a place but not a negotiation you lost. Measure it instead from swipe-posterior sharpness (day one) and rating-versus-personal-match correlation (once feedback accumulates). **Instrument `fairness_relaxed` before building any of this** — if it fires on 2% of plans it is not worth it. Gaming risk: cap how far a personal floor can rise, and seed from swipe confidence rather than star ratings, which are easier to fake deliberately.

## [2026-09-03] `PLAY` and `LIVE` are bidirectional, not shortfall-only
**Decision:** `PLAY` and `LIVE` move out of the shortfall-only set and become bidirectional in `factor_penalty`. The shortfall-only set is now exactly the three **passive** factors — `SCEN`, `FOOD`, `HERIT` — and the bidirectional set is `CROWD`, `ENRG`, `POL`, `NOV`, `AFFIL`, `PLAY`, `LIVE`. This is a straight correction, not a provisional change, and it holds independently of the bend work that surfaced it.
**Context:** The shortfall-only rule was justified as *"someone who didn't prioritise food is not harmed by excellent food."* That reasoning holds only for factors you can **ignore**. It does not hold for factors that are **imposed on you**. Under the current rules a Deep-Chat Drinker (`PLAY` 10, `LIVE` 30) is sent to an escape room or a venue with a loud band at **zero penalty** — the model asserts it costs them nothing. You can ignore good food; you cannot ignore being at a bowling alley when you came to talk, or a band loud enough that you cannot hear each other. The real distinction is **passive versus participatory**: `SCEN`, `FOOD` and `HERIT` are qualities of a room you can leave alone, while `PLAY` and `LIVE` are things the night makes you do. Under the old classification, every quiet, conversation-led vibe — Deep-Chat Drinker, Date-Night Dreamer, Quiet Luxury Type, Long-Table Settler — was structurally unprotected against exactly the venues that ruin their night.
**Consequences:** (1) `factor_penalty` now charges for exceeding on both factors. (2) The bend derivation gives low-scoring vibes a near-zero bend_up on them, which is too rigid on its own — see the bend flags and the 0.40 floor. (3) Card design is unaffected; both were already tested by dedicated card pairs.
**Alternatives considered:** Leaving them shortfall-only and handling the problem entirely inside bend — rejected, because the penalty rule would still be stating something false about how those factors work, and anything reading `factor_penalty` alone would inherit the error.

## [2026-09-03] Blend weight is per-factor firmness — a member with no position abstains
**Decision:** The group vector is no longer a head-count average. Each member's weight on each factor is their **firmness** on that factor, `|score − 50| / 50`, with **no floor**: a member sitting at the midpoint contributes nothing to that factor. Firmness is read from **distance from neutral**, not from distance to the nearest vibe. When every member's firmness on a factor sums below 0.05, the factor is undefined rather than 50, and the room routes to `DRIFT`. Firmness also scales the vibe's own bend — `bend_final = bend_vibe × (1 + k(1 − firmness))`, capped at 1.0, with `k` in the 1.0–1.8 band and 1.2 as the working value.
**Context:** Under head-count averaging, three Warehouse Heads plus one indifferent friend produced an `ENRG` of 80 rather than 90 — four ravers became three ravers and a compromise. The indifferent member had no objection to a 90-energy night; he voted for 50 simply by existing. Abstention holds the value at **90.0 exactly, at any flat headcount**, where a 0.25 weight floor still leaked 3–17 points. It also **reduces** harm rather than causing it: members landing outside their own bend fall from **10.26% to 8.41% per member-factor**. Real disagreement is untouched — two decided sides still cancel properly (3 Deep-Chat + 1 Big-Night Regular moves 37.8 → 41.4, not to the middle).
The property that makes this safe is that **one number drives both the weight and the bend, in opposite directions**. Weight is firmness; bend is its inverse. The member whose vote is removed is exactly the member who tolerates the outcome, so abstention cannot place anyone somewhere they would hate. The 0.25 floor quietly broke this by giving weight to people it also treated as fully flexible.
**Consequences:** (1) One decided member among three flat ones now decides **every factor** — realistic, but the room deserves a flag at formation rather than an arithmetic correction. (2) A room where nobody has a position has no answer at all; the vector cannot invent a night and needs popularity or a direct ask. (3) A single hard constraint is **not** rescued by weighting and never will be — a member needing `ENRG` 88 among three quiet people gets 32 weighted versus 37.8 plain. That is a genuine mismatch and must be caught at room formation. (4) The **certainty** term (agreement between a member's two cards on a factor) is computed but **not** used: retested across three noise levels it adds −0.010 / +0.005 / +0.001 against extremity alone. It scored well on one real tester's sheet (+0.71 → +0.88) and that is a sample of one.
**Alternatives considered:** *Distance to the nearest vibe* as the firmness signal — rejected outright, it correlates **−0.69 with whether a vibe covers you** and only −0.33 with actual constraint; it measures where the vibe list has holes, which is a fact about the list, not the person. *Pair disagreement alone* — rejected, it scores a consistent `YES/YES` as firm and cannot tell "I mildly want this" from "I don't mind", which is exactly how it misread a real tester's `CROWD`. *A person-level conform/non-conform tag* — rejected as a mechanism: it correlates **−0.999 with the mean of the per-factor bends**, so it is the same number restated, and a single label cannot express "flexible on seven factors, immovable on one." Keep it as a display line only. *A 0.25 weight floor* — rejected, arbitrary and it breaks the coherence property above.

## [2026-09-03] `CONSENSUS` — firmness-weighted agreement, undefined when nobody has a position
**Decision:** `CONSENSUS` is agreement across the factors people actually hold positions on. For each factor, take the members with firmness above 0.15, measure the spread of their scores against a 70-point scale, and weight the result by their mean firmness. Factors where fewer than two members have a position are skipped. When **no** factor qualifies, `CONSENSUS` is **undefined** and the room routes to `DRIFT`.
**Context:** First independent test of the measure. It separates cleanly with room to spare: four identical Deep-Chat Drinkers **1.00**, three Warehouse Heads plus a Front-Row Regular **0.93**, two Chaos Collectors against two Quiet Luxury Types **0.42**, a Warehouse Head with a Date-Night Dreamer **0.26**. The undefined case is a bug the test found: a room where nobody had an opinion returned **1.00 — "perfect agreement"** — which is wrong in spirit. Nobody agreed on anything; there was nothing to agree on. Left unfixed it would have marked the emptiest rooms as the most harmonious.
**Consequences:** The measure is sound; its **thresholds are not set** and cannot be set from simulation — see the note on blend states below.

## [2026-09-03] `FLOOR` is measured against the plan, not against the blended vector
**Decision:** `FLOOR` is the worst member's worst overrun past their own bend, scaled against a 40-point scale, and it is evaluated against **the multi-stop plan** — each member needs one stop they can live with — not against the single blended vector.
**Context:** First independent test. It fires where it should and stays silent where it should: four identical Deep-Chat Drinkers **0.00**, three Warehouse Heads plus a Quiet Luxury Type **0.90**, three Deep-Chat Drinkers plus a Chaos Collector **1.00**. The pair that matters is three Warehouse Heads plus a **flat** member, which scores **0.00** — the same coherence property as abstention, holding independently here. Both cases add a member far from the group; only the one with real positions registers.
The correction is the measurement target. Judging tolerance against one averaged point charges every member for a night nobody is actually served — average `FLOOR` reads **0.05** against the blend point versus **0.02** against a three-stop night. **The blend vector is a summary, not a venue.**
**Consequences:** Anything else reading the blend vector as if it were a destination inherits the same error and should be checked.

## [2026-09-03] The five blend states are held — they cannot be calibrated from simulation
**Decision:** `SPARK` / `STEADY` / `DRIFT` / `FRICTION` / `SPLIT` are **not** written into the engine spec, and no thresholds are set, until the group test reports how similar the members of a real room are.
**Context:** The same thresholds produce opposite worlds depending only on how rooms are formed. Random strangers: **60.2% SPLIT, 0.0% FRICTION-free**, i.e. most rooms declared irreconcilable. Friend-like groups: **0.0% SPLIT, 0.0% FRICTION, 74.7% STEADY**. Neither is credible and the truth sits somewhere between, at a point no simulation can locate — the input distribution is a fact about SHUFFL's users. The states themselves are **not** relabelled noise: they sit on real separation in the underlying numbers (`STEADY` consensus 0.75 / floor 0.07, `SPLIT` consensus 0.34 / floor 0.84), so the taxonomy survives; only its cut-points are unknown.
**Consequences:** `DRIFT` currently fires on about 2% of rooms and needs the undefined-`CONSENSUS` route to trigger at all. Do not describe the chemistry system publicly as five states until this is measured.

## [2026-09-04] Agency and `PEAK` are both removed — chemistry describes and gates, it never moves anyone's scores
**Decision:** **Agency is retired entirely**, reversing the 2026-09-02 entry that placed it on the user profile. It is not a factor, not a vibe attribute, not a profile trait, and nothing is instrumented for it. **`PEAK` is removed entirely**, including the two-sided version and the half previously recommended for shipping. Blend chemistry is now exactly three things — **abstention** (builds the room vector), **`CONSENSUS`** (does this room want the same night), **`FLOOR`** (would this member be stranded) — and its scope is **matching users to rooms and gating who may join a hosted room**. No part of chemistry may alter any member's factor scores or the plan's target vector. Venue suitability is handled entirely by the existing machinery: factor scores, bend, the passive/participatory split, priority weights, fairness relaxation, the novelty adjustment, the manual duration/budget inputs, the distance filter, and `FLOOR`.
**Context:** Both removals follow from one observation: **a high-agency person changes what happens on a night, not what anybody wants.** The group's natural organiser suggesting a bar does not shift anyone's factor scores; it shifts whose scores get acted upon, with the others following at some probability of not enjoying it. **That dynamic is the problem this app exists to remove**, so encoding it inside the engine would reinstall the failure inside the fix. Agency is therefore not a missing feature awaiting a formula — it is the thing being replaced, and the undefined-formula blocker is closed by deletion rather than by definition.
`PEAK` fails on the same ground, and the argument is sharper. It moved the group's target above the average on `ENRG`, `PLAY` and `NOV` when one member was keen. But **abstention already delivers the defensible half of this**: three high-energy members plus one indifferent member hold `ENRG` at **90.0, not the 80.0 plain averaging gave** — the enthusiast is not flattened. Crucially they carry the night *only because nobody objected*. What `PEAK` adds on top is precisely the case where it moves members **who did object**, which is not emergence but the loudest voice winning with extra steps. If a user's stated preferences can be overridden by someone else's enthusiasm, the reason to open the app in the first place is gone.
The emergence case that originally motivated `PEAK` — four quiet friends having a bigger night than any of them planned — survives its removal, on a distinction not drawn properly before: **the engine's job is not to predict emergence, only to avoid preventing it.** Four friends staying in a quiet bar until 3am *is* emergence; the venue supported it. Nothing required the model to send them somewhere loud on a theory about group psychology, and the counterfactual was never observable from app data in any case.
**Consequences:** (1) Of the three failures of plain averaging used to justify the chemistry rework, **one is now withdrawn** — "averaging erases emergent groups" is no longer claimed. The other two stand on mechanisms that do not move stated preferences: "it flattens the one enthusiast" is handled by abstention, "it hides genuine mismatch" by `FLOOR`. (2) The five room states derived from `CONSENSUS`, `FLOOR` **and peak lift**; they now fall out of **two inputs, not three**, which is more legible and materially easier to calibrate once the group test supplies the room-similarity distribution. The state definitions must be reworked accordingly before any threshold work begins. (3) A live inconsistency resolves by deletion: `PEAK` was specified with a per-member **conformity** input, but conformity-as-a-user-trait had already been rejected in favour of per-factor bend, leaving the tested implementation depending on a value no longer in the model. The consolidated spec had quietly substituted one-minus-firmness for it, which was never tested. (4) `AFFIL` is unaffected — it remains a card-tested factor scored individually, and the group-level seating suggestion built on it is descriptive, not prescriptive. (5) Nothing about venue scoring changes.
**Alternatives considered:** *Keeping `PEAK` only as a tie-breaker among venues already acceptable to everyone* — rejected; it is a smaller version of the same act, and the tie-break is better decided by fairness, which is grounded in what members actually asked for. *Keeping agency purely as instrumentation, recording host-versus-join ratio for later* — rejected as premature: there is no mechanism that would consume it, and the 2026-09-02 entry already documented the correlation trap it fell into once (agency ran 0.65 with `ENRG` and 0.67 with `SOC`, encoding "how loud is this vibe" twice). Any future reintroduction must first demonstrate on real behaviour that agency is not simply firmness under another name. *Retaining `PEAK` for the two-or-more-dissenters case only* — rejected; the review had already shown the proposed cut applied Asch's finding asymmetrically, protecting the lone enthusiast while discounting the lone objector, and the whole mechanism is now out regardless.

## [2026-09-04] Priority weights are derived per user, not per vibe
**Decision:** `priority_weights` is computed from **the user's own factor vector**, never from the vector of the vibe they matched to. §5.3.1 of `OUTING_PLAN_ENGINE.md` is retitled and rewritten accordingly, and its factor references are corrected to the current ten-factor set — `salience` now keys off `PASSIVE` (`SCEN`, `FOOD`, `HERIT`) instead of the retired `SHORTFALL_ONLY` list and the `VALUE`/`CONV` special case, both of which no longer exist. `PRIORITY_ALPHA` stays at **0.35**, still a judgement call rather than a derived value. Group priorities continue to derive from the room's blended vector, not from averaged member weight vectors.
**Context:** The spec contained a live contradiction. The section was titled *"the weights are per-vibe, not global"* and its prose argued from vibe identity, while the function it specified took `user_vector` and always had. Anyone implementing from the title would have written something different from anyone implementing from the code. **Per-user is the correct reading**: the vibe is the nearest archetype, not the person. A user can sit 70 points from their own vibe and still be planned for as themselves — the real tester behind the Crew-Night Regular sits 71 from his — and deriving weights from the archetype would discard precisely the individual detail the swipe game exists to capture. It would also compound the coverage problem: a user matched loosely to a vibe would be scored on that vibe's priorities rather than their own, so a poor match would produce a doubly poor plan.
The section's worked examples were additionally unusable, being written on `SOC`/`SOFT`/`CULT`/`FUN`/`VALUE`/`CONV`. They are rebuilt on the current factors.
**Evidence:** Tested on a three-person room. Under global weights a Front-Row Regular scoring `LIVE` 88 had live music counted at **6%** — identical to a user who never goes to gigs. Per-user weights move it to **12%** and `ENRG` from 12% to 16%, while `FOOD` falls 14%→9%. That reordering **changed the plan**: his stop moved from a live gig bar to a warehouse rave, which scores 92 on both `LIVE` and `ENRG` against the gig bar's 88 and 75. The other two members' stops were unchanged, which matches the documented behaviour — reweighting rarely inverts the top result and mostly reorders what sits behind it, and the plan is assembled from the top eight per slot rather than each slot's winner. Two further confirmations: the Crew-Night Regular user's `AFFIL` weight nearly doubles (8%→14%), correctly making his firmest position his most heavily weighted one; and a Quiet Luxury Type user's `PLAY` weight *rises* 7%→11% despite scoring **12** on it, which is the participatory rule behaving correctly — a low score there is a strong position, not an absence of one, and being taken to an escape room is a real cost.
**Consequences:** (1) A third implementation trap is recorded: **an undefined factor in a room's blended vector carries zero salience and must not be substituted with 50.** Under abstention a factor comes back undefined when no member holds a position on it; feeding 50 in would grant it the salience of a genuine neutral, which it is not. (2) **Venue costs computed under different weighting schemes are not comparable** — each is denominated in that user's own weights, so a cost moving between a global-weight run and a per-user run is a rescaling artefact, not a change in fit. Only the resulting ordering may be compared. (3) The pros & cons on the plan card derive from the same weights and therefore also become per-user. (4) §5.3.1 is now current; **the rest of `OUTING_PLAN_ENGINE.md` remains three model versions stale** and this edit does not change that.
**Alternatives considered:** *Deriving from the matched vibe's vector* — rejected as above; it discards individual detail and compounds poor matches. *Hand-authoring a weight set per vibe* — rejected, already rejected once: it would be hundreds of additional numbers to maintain and would drift out of step with the vibe definitions within months. A user's extremes already are their priorities. *Raising α above 0.35* — not taken; at 0.5 the largest single-factor weight reaches roughly 40%, which is defensible, but at 0.7 it reaches 50% while the smallest falls to 1%, effectively deleting factors from consideration.

## [2026-09-04] Tie-breakers also fire on distance, and distance is resolved before pairs
**Decision:** Tie-breaker cards now have **two triggers, not one**. The existing trigger stays: the top two vibes within **25** points. A second is added: **the nearest vibe further than 140 points away**. When both fire, the **distance set runs first**, the factor scores are recomputed from the new answers, and the pair trigger is **re-evaluated against the updated vector** — the pair set runs only if it still fires. `DISTANCE_TRIGGER = 140` is a starting value, to be instrumented and recalibrated against real users.
**Context:** The pair trigger asks *"which of these two is it?"* and nothing asked *"is it any of them?"* A user sitting far from every vibe has a perfectly clear winner by the gap test and triggered nothing at all — the distance was computed and then discarded. The pathological case makes it obvious: a room with no positions anywhere lands **150** from the nearest vibe, is described by nothing, and sails through unchallenged. 140 was chosen from the simulated distribution of nearest-vibe distance, where the median is 106 and the 90th percentile is 140: it fires on about **9.3%** of users, against 28.5% at a threshold of 120 (which makes a second round near-universal) and 2.1% at 160 (which almost never fires).
**Why distance is resolved first.** Both triggers fire together for about **10%** of users. Running the distance set first and re-checking was proposed on the grounds that updated scores might clear the pair on their own, and they do — **27%** of the time, saving 0.8 cards on average against always running both. But the **stronger reason is correctness, not card count**: pair tie-breakers are drawn from a library of cards built to separate two *specific* vibes, and after the distance cards are answered **the contending pair has changed 50% of the time and the winner itself 40% of the time.** Running pairs first therefore spends 2–3 bespoke cards separating a pair that is no longer the pair, in half of all cases. The reverse risk — distance cards *creating* a close pair where none existed — is **0.8%**, negligible.
**Consequences:** (1) The distance set is not the same instrument as the pair set. Pair cards separate two named vibes; **distance cards re-probe the factors whose readings are least reliable**, ranked by pair gap, to obtain a cleaner vector. They are a different library and need writing. (2) Worst-case card count for a user triggering both is **20 + 5.2 ≈ 25**, against 26 if both always ran. (3) A third case is now distinguishable and must not be conflated with either trigger: a factor whose reading is **missing** rather than ambiguous — as when a card is voided for measuring something other than its factor. That calls for a replacement card, not a tie-breaker. (4) Both thresholds are calibrated on simulated users. The real distribution of nearest-vibe distance is a fact about actual users; **instrument how often 140 fires before trusting it**.
**Alternatives considered:** *Running both sets up front whenever both trigger* — rejected; costs 0.8 more cards and, more seriously, wastes half of the pair cards on the wrong pair. *Firing pairs first* — rejected for the same reason, more strongly. *A tighter distance threshold of 120* — rejected, it fires on 28.5% of users and turns the second round into a routine part of onboarding rather than an exception.

## [2026-09-05] The engine stops matching to a vibe — bend comes from the user, flags fire on nearness
**Decision:** Vibe matching is removed from the engine. **Bend base is derived from the user's own factor vector**, not from the vector of the vibe they matched to. **Bend flags fire per factor on nearness plus a firmness gate**: a flag on factor `f` transfers from *any* flagged vibe whose score on `f` sits within **18 points** of the user's, and only where the user's own firmness on `f` is at least **0.20**. A flag describes a **position**, not a person. The vibe becomes a **label only** — name, description, colour, heatmap, filter, profile history — and its count is therefore a naming decision rather than an engineering constraint.
**Context:** Four real testers landed 71, 132, 147 and 225 from their nearest vibe against a simulated median of 106 and 90th percentile of 140. Three of four sat at or above that 90th percentile, which should not happen — and the reason is a flaw in the calibration, not the list: **the simulated users were generated by perturbing vibe vectors**, so they were vibe-shaped by construction. Real people are not drawn from that distribution. Chasing this by adding vibes would mean fitting the list to individuals; the proposal instead was to give every factor combination its own vibe, which at three bands across ten factors is **59,049** — not a product.
The resolution is that the combinatorics only matter if the engine needs the vibe, and it does not. Running the plan generator with bend taken from the user's own scores instead of their vibe's gives **all four real testers an identical top venue**. On simulated users agreement is 71%, but those users are the vibe-shaped artefact above. The vibe's only distinct contribution is the **flags** — which do matter, changing the outcome on 32% of venue pairings for flagged vibes, and which resist derivation: a fifth attempt, reducing them to thresholds on the score itself, separated cleanly on only **2 of 8** flagged factors.
**Evidence:** Measured across 6,000 users on two failure modes — a *false* flag (told they cannot tolerate something they scored above 45 on) and a *missed* flag (scored 20 or under on a participatory factor and given no protection at all):

| Rule | False | Missed |
|---|---|---|
| matched to nearest vibe (current) | 9% | **62%** |
| gated at distance 120 | 5% | 82% |
| per-factor nearness | 7% | 0% |
| **per-factor nearness + firmness gate** | **0%** | **0%** |

**The 62% is a live defect in the existing system**, independent of this decision: whether your nearest vibe happens to carry the flag you need is close to a coin flip, and the failure it produces is exactly the one that made `PLAY` and `LIVE` bidirectional — a quiet, conversation-led user sent to an escape room with no protection.
The two rules address different failures and are both required. **Nearness** stops a flag arriving from a vibe unlike the user on that factor. The **firmness gate** stops a flag landing where the user has no position at all — it was added after a real tester picked up a `POL` flag while scoring exactly 50 on it, which is meaningless, and it is what takes false flags from 7% to zero. Window 18 and gate 0.20 are working values; 8–25 and 0.20–0.30 all behave.
**Consequences:** (1) **Nobody is unmatched.** A user 225 from every vibe is served at their exact position; the distance now means only that their night lacks a good *name*. (2) The **distance tie-breaker trigger logged 2026-09-04 needs revisiting** — it was designed to catch users the engine could not serve, and the engine can now serve them. It may still be worth firing as a *labelling* signal, but its justification has changed and its 140 threshold was calibrated on the same vibe-shaped simulation criticised above. (3) `factor_penalty`, `user_bend` and §5.3.1 in `OUTING_PLAN_ENGINE.md` all take the user vector as their source and no longer need a vibe argument. (4) The vibe list's size and composition become a **product decision**. Adding vibes for coverage stops being an engineering fix — the two added on 2026-09-04 remain useful as labels but are no longer load-bearing. (5) **The 40 flags are still hand-authored and still unvalidated.** This changes how they are *distributed*, not whether they are *right*.
**Alternatives considered:** *A vibe per factor-range combination* — rejected on combinatorics: 1,024 at two bands, 59,049 at three, and none of them nameable, describable or colourable. *Gating the current matched flags on distance* — rejected, tested at 5% false but **82% missed**; it removes flags rather than redistributing them, making the real defect worse. *Deriving flags from thresholds on the score* — rejected, the fifth failed derivation, clean on only 2 of 8 factors. *Continuing to add vibes for each uncovered tester* — rejected as fitting the list to individuals; three of four testers would have warranted one.

## [2026-09-07] Mood supplies the level where the score has no preference
**Decision:** A factor now carries **three** numbers, not one. **Score** says whether the factor matters and in which direction — 88 wants it, 12 refuses it, 50 is take-it-or-leave-it. **Strength** is the level actually targeted, derived from the user's **momentary affect at swipe time** (Russell's *core affect*: valence and arousal, not diffuse long-run mood). **Bend** is tolerance, unchanged. The rule is that **mood fills the vacuum the score leaves**:
```
care   = |score - 50| / 50
target = clamp(score + G · (1 - care) · (arousal·A[f] + valence·V[f]))
```
Mood acts hardest where the score says nothing and is arithmetically incapable of overriding a strong score. **The vibe does not change with mood** — a Party Monster on a quiet night is still a Party Monster, sent to a Party Monster venue at lower intensity. Mood is displayed as a modifier on the name, never as a reassignment.
**Context:** One number per factor was doing two jobs — how much you want it, and how much you care — with the second *derived* from distance-from-neutral. That derivation is what made a mid-range answer mean "no information", and it is the root of several separate defects. The correction, which came from the user, is that a neutral score is not a missing reading: it is a genuine statement that the person has no preference, **and the right thing to do with no preference is let their mood decide.**
Three candidate rules were compared on four people — someone who wants a crowd (88), someone who wants quiet (12), someone mildly positive (62) and someone neutral (50):

| Rule | Behaviour |
|---|---|
| mood shifts every factor equally | pushes the person at 12 down to 5 — takes someone who already said no and pushes them further into no. Meaningless. |
| mood scales the distance from neutral | leaves the person at 50 exactly where they were. A person with no preference gets no guidance, which is the opposite of the point. |
| **mood fills the vacuum** | **the only rule that behaves on all four** |

Movement by score under the accepted rule: **4 points at 88, 8 at 75, 13 at 62, 16 at 50** and symmetrically below. It is self-limiting by construction and needs no guard rail.
**Consequences:** (1) **Two logged correctness defects dissolve rather than needing fixes.** A room where everyone is neutral previously produced *no blend vector at all* and a stranded-check that could not fire; under this rule every factor has a value, so the room has a vector and real firmness (measured 0.18–0.26 across trials, 10 of 10 factors defined). The related "fewer opinions makes you look like a better vibe match" bug has the same cause — a factor with no value — and goes with it. (2) It does **not** invent agreement: four neutral people sharing a mood score **0.93** on consensus, four in different moods score **0.48**. That is a real distinction the old model could not make at all. (3) **The daily test gets shorter with use.** Disposition is measured once and sharpens with every visit; the daily job is a mood reading. Simulated against re-swiping all twenty cards, the split loses on day one (9.8 vs 8.4) and wins from day three, reaching **6.9 vs 8.5 by day twenty**. (4) Mood is **two-dimensional** — two orthogonal axes score 4.9 against 5.2 for one and 7.0 for ignoring it; reading all ten factors separately is far worse at 11.6, because mood only moves in two directions and every extra reading adds noise. (5) Four to eight named mood states is the useful granularity; the jump from one to four captures most of the value. (6) Venues need **no separate mood score** — their factor vectors already place them on both axes sensibly, with a warehouse reading wired-and-cool and a tasting menu calm-and-warm.
**Open, and the reason this is not yet buildable:** there is **no instrument for reading mood.** Validated affective image sets rated on exactly these two axes exist in the literature, and a mood probe should dodge the "they all sound good" problem the factor cards have — it asks where you are, not what you like, so there is no desirable answer. But the design does not exist, the loadings of each factor onto arousal and valence are **my assumptions rather than measurements**, and the size of a real mood swing is unknown. That last number decides everything: at ±6 points mood changes the venue 15% of the time and is not worth measuring; at ±18 it is 35%.
**Alternatives considered:** *Mood as a modifier on the whole vector* — rejected, see the table. *Mood reassigning the vibe* — rejected on evidence: vibes sit a median 233 apart and a realistic mood shift moves a person about 60, so across sixteen tested combinations the vibe **never changed**, and in simulation it changes only 17% of the time at a mood strength of ±18 against 35% for the venue. Mood moves venues because venues are dense; it cannot move vibes because they are not. *Scoring each vibe on mood suitability* — not needed under this rule, since the vibe is held fixed and mood acts on the target vector.
**Caveats on the numbers above:** two of my own tests in this session failed and are not evidence for anything. An attempt to show the three parameters each independently change the venue was badly constructed — all four variants returned the same venue. A test of whether mood should move importance as well as level returned 37% against 38%, which shows nothing either way. Separately, the 51%-versus-35% venue-change comparison is confounded: the vacuum rule needs a larger coefficient to do any work at all, and I gave it nearly double the gain.

## [2026-09-07] Mood is read from the factor cards themselves, on six pairs only
**Decision:** No separate mood instrument. The **two cards in a factor pair carry deliberately different affective tone**, and the difference between a person's two answers is a mood reading with the factor score cancelled out. Six pairs carry a contrast — **`CROWD`, `SCEN`, `FOOD`, `POL`, `LIVE`, `HERIT`** — with their contrast directions spread evenly around the circumplex. The other four — **`ENRG`, `PLAY`, `NOV`, `AFFIL`** — are **deliberately tone-matched**, both cards shot in the same register, and contribute no mood signal.
**Context:** The arithmetic is what makes this work. Card A reads *score + mood·loadingA*, card B reads *score + mood·loadingB*; their average recovers the factor score and **their difference is pure mood, because the score cancels**. Ten pairs already exist, so this costs no extra items. It also does not violate the card-writing rule that a pair must differ only on something that is not itself a measured factor — **mood is a state, not a factor**, and is exactly the kind of thing a pair may vary on.
Against a purpose-built instrument of eight ambient image pairs, the integrated version was **better and cheaper**: mood error **0.42 across 20 items** versus **0.54 across 28**. A separate instrument was designed and is discarded.
**Why only six pairs.** A pair can only carry a contrast if its affective tone is independent of its factor content. Four cannot. **`ENRG` is the clearest failure — you cannot photograph high energy as low arousal, so the tone *is* the factor.** `PLAY` can only change tone by changing the activity, which changes the question. `AFFIL` is inherently warm-valenced; a cold version stops meaning "your own people". `NOV` carries its own arousal and yields only a weak contrast.
**The cost of getting it wrong is paid by the factor scores, not the mood reading.** A pair whose tone bleeds into its factor content still produces mood, but makes its own factor score worse — factor error rises from **8.5 to 9.0 at moderate bleed and 10.5 at strong bleed**, while mood error barely moves (0.44 → 0.48). Including the four risky pairs would buy a slightly better mood reading (0.51 → 0.44) at the cost of noticeably worse factor scores (8.5 → 9.6). **Factor scores are the foundation; they are protected.**
**Consequences:** (1) **Six clean pairs is comfortable, four is the floor** — mood error 0.50 at six, 0.60 at four, 0.83 at two. No compromise is needed since six are available. (2) The required tone separation is about **0.9 on the circumplex**; below 0.6 mood is thin, above 1.3 the factor scores start to suffer. At zero separation mood is invisible, which is the situation today. (3) **The pair-gap diagnostic changes shape.** A gap currently means uncertainty or a broken card; on the six contrast pairs part of it is now mood. Read the **residual** after the measured mood explains what it can — raw gap averages 26, residual 15.6. Every rule that consumes pair gaps needs updating. (4) "Tone-matched" must mean genuinely matched, both cards in the same register — **a half-hearted contrast is measurably worse than none**, and the most expensive place to make that mistake is `ENRG`, the factor everything else correlates with.
**Alternatives considered:** *A separate ambient-image instrument*, eight forced-choice pairs of non-venue imagery rated on valence and arousal — designed, tested, and discarded as strictly worse than the integrated version. Its one surviving contribution is the constraint that mood imagery must never depict a venue, which applies here too: **the tone must be carried by light, framing and motion, never by changing what the place is.** *Carrying a contrast on all ten pairs* — rejected, see the factor-error cost above. *Rating scales rather than forced choice* — rejected on the acquiescence evidence: ratings degrade when people lean positive (error 1.56 → 1.74), forced choices do not move at all.
**Caveat on the numbers:** two of my own tests in this session were mis-specified and their conclusions withdrawn. One modelled confounding as extra mood sensitivity rather than as mood masquerading as factor content, and produced the opposite of the correct result; the figures quoted above are from the corrected run. Everything here is simulated — the tone separations, the factor loadings onto arousal and valence, and the size of a real mood swing are all assumptions awaiting a real test.


## [2026-09-08] The 20-card design stands; phased and adaptive alternatives both tested and rejected
**Decision:** Keep the current structure — **20 cards, two per factor, six pairs carrying an affective contrast and four deliberately tone-matched**. Three alternatives were built and tested against it and none beat it: a two-phase split (ten clean factor cards then ten tone-loaded ones), adaptive selection of *which factors* carry a contrast, and adaptive selection of *which tone* the second card of a pair takes. All are rejected.
**Context:** The two-phase design was proposed to fix a real problem — a tone contrast only produces a signal on a factor the person engages with, and which factors those are cannot be known in advance. Across ten real testers, the six contrast pairs were engaged an average of **3.4 of 6**, with three testers engaged on two or fewer. Worse, the three factors people engage with most (`PLAY`, `AFFIL`, `ENRG`) are all tone-**matched**, because their tone cannot be separated from their content — the contrasts sit where they are *safe*, not where people *react*, and those turn out to be nearly opposite sets.
**Why the phased version loses.** At an identical twenty cards it is worse on both measures: **factor error 8.5 against 7.7, mood error 0.55 against 0.48.** The reason is that separating the phases throws away information. In the current design a tone-loaded card contributes to *both* readings — it still tells you about the factor once the mood is known — whereas phase 1 gains nothing from phase 2 existing. Tone-loaded cards are not a separate budget.
**Why adaptive targeting fails, and the ceiling effect behind it.** Answers are four fixed points, so a tone shift only registers if it pushes someone across a boundary between them. **The signal is largest at the mild answers and smallest at the extremes**: a true score of 62 yields a gap of 50, while 88 yields only 26 because the warm card cannot lift someone already at the ceiling. This inverts the intuition that a LOVE means "they resonate, so contrast them" — a LOVE means they are at the rail and tone has nowhere to move them.
That effect is real, but it does not convert into a usable rule. Targeting the mildly-answered factors, the strongly-answered ones, or a fixed safe six all scored **0.55–0.56**, indistinguishable. With ten phase-2 cards spread over six eligible factors you use nearly all of them whatever the order; adaptivity only pays when the budget forces a choice. A separate test of adapting the *tone* of card 2 to the answer on card 1 gave a marginal gain (0.48 → 0.43) but only in a variant where both cards carry tone, which the current design already does.
**Consequences:** (1) **There is a fixed exchange rate between the two readings and it cannot be designed around.** Every arrangement tested at twenty cards landed at factor 7.7–8.5 and mood 0.48–0.55. The only way past it is more cards: **20 clean + 8 tone gives the best factor reading measured anywhere (6.9) at a cost of 28 cards**, with no mood improvement. (2) **Mood needs about eight tone-loaded cards to be worth measuring at all.** At four it scores 1.07 against a do-nothing baseline of 1.13 — indistinguishable from guessing neutral. (3) The engagement problem is **acknowledged and unsolved**. Users who reject most of the six contrast factors will yield a thin mood reading, and no allocation strategy fixes it within the card budget.
**Alternatives considered:** *Ten clean plus ten tone-loaded* — rejected, worse on both axes at the same card count. *Adaptive factor targeting by engagement* — rejected, no measurable difference from a fixed allocation, and the ceiling effect means the intuitive version (target strong answers) targets exactly the factors least able to reveal mood. *Adaptive tone selection on card 2* — a real but small gain, subsumed by the existing design. *Twenty clean plus eight tone at 28 cards* — not rejected on merit; it is genuinely the best factor reading available and remains open if factor accuracy is later judged worth eight more cards.
**The caveat that governs all of it:** every figure above assumes the affective tone is perceptible. **It is not, in text.** A tester read both `FOOD` cards and both `POL` cards — the two cleanest contrasts in the set, with identical opening sentences — and reported no difference in tone. Until one pair is shot two ways and shown to one person, the entire mood layer is arithmetic resting on an untested premise.
**Correction to my own working:** the script comparing the phased design to the current one reported it as *better on mood and slightly worse on factors*. It is worse on both. I predicted the factor cost correctly and had the mood result backwards.

## [2026-09-08] The two cards in a pair differ only in the light
**Decision:** Card set **v7** replaces v6. Every contrast pair now holds the scene, the people and the activity identical and moves **only the light** — brightness carries arousal, colour temperature carries valence. Light is stated as fact, never as praise, because praise leaks into `SCEN`. `POL` moves to the diagonal opposite `SCEN` on the circumplex. The two cards of a pair are **never adjacent** on the sheet, minimum six cards apart. Full set in `CARD_SET_V7_CLEAN.md`.
**Context:** Arnav's fifth sheet was the first on which the tone pairs actually moved — **five of six fired**, against one of six on the author's own sheet. But no mood explains them. Fitting arousal and valence to his six gaps leaves **28.5 points unexplained per pair against 29.0 for predicting nothing at all** — the two-parameter fit buys 2%. A second explanation fits better: each pair differed on a **second measured factor**, and he picked the card matching his own profile every time. `CROWD` moved on *nobody in a rush* / *never sits still* (`ENRG`, and his `ENRG` is 88); `FOOD` on *everyone reaching across the table* (`AFFIL`, his is 88, and it produced the sheet's largest gap at 76); `LIVE` on *pushed up to the front* — the same crush wording he had already rejected on v4. Scored as a model, leak beats mood **22 to 29** on his sheet. **This was already forbidden.** The card rule logged on the v4 rewrite states that the two cards in a pair must differ only on something that is not itself a measured factor. Four of six pairs broke it, and I wrote them.
**Why light.** Warmth in prose attaches to other people almost by default, and other people are `CROWD` and `AFFIL`. Light is the only carrier found that is vivid enough to picture and neutral enough not to name a factor, and it happens to have two independent properties matching the two mood axes.
**Consequences:** (1) Expected **factor error 11.8 to 10.6, mood error 0.55 to 0.51**. Running the new circumplex placement with the old wording gives 11.9 / 0.56 — **no gain at all**. The wording is the entire fix; the loadings are a tidy-up. (2) Moving `POL` opposite `SCEN` drops the entanglement between the two mood estimates from **0.20 to 0.06**, so arousal and valence now come apart almost cleanly. Arousal is measured 8% less precisely, valence 5% better. (3) Two new risks, both testable. Every contrast card now describes light, and `SCEN` measures whether the look of a place matters — **check that `SCEN` scores do not predict the size of the tone gaps.** And near-identical cards may trigger a repeat-the-first-answer reflex; the six-card separation is the guard, and the check is whether gaps collapse to zero across the board. (4) The leak model was built **after** seeing Arnav's answers and does worse than nothing on the author's sheet, which had only one live pair. It is a diagnosis, not a validated model.
**Alternatives considered:** *Keeping v6 and treating Arnav's gaps as mood* — rejected, the mood fit is indistinguishable from predicting zero. *Carrying tone through pace* — rejected, pace is `ENRG`. *Carrying tone through formality or beauty* — already rejected on v5, they are `POL` and `SCEN`.

## [2026-09-08] A firm answer censors the mood reading, and the engine calls decided people calm
**Decision:** Record as a **named, unfixed defect**. Do not fix it by making the cards subtler. Keep the factor reading intact and accept that firm users produce a weak mood signal.
**Context:** The observation came from the user: someone who hates live music says HATE to both cards whatever mood they are in. It holds in the real data — across the two v6 sheets, pairs where the person **felt strongly averaged a gap of 8.7**, pairs where they were **undecided averaged 24.7**. Three times the signal on factors nobody cares about (12 pairs, 2 people). The consequence is not a missing reading but a **biased** one: a firm person's zero gap is indistinguishable from a calm person's zero gap, so at identical true mood the engine reports **0.87 for firm users against 1.19 for soft ones — 72%**. It systematically describes opinionated people as flat.
**Why the obvious fix is refused.** Writing cards that do not name the factor outright does repair the bias almost completely (72% to 94%) and improves mood slightly (0.52 to 0.48), but **factor error nearly doubles, 6.7 to 12.5**. Vibe matching runs on total distances of 100–140 across ten factors; 12.5 per factor is 125 points of error and erases the match. The mood gain is small for a structural reason worth keeping in mind: **attenuating the factor does not amplify the mood.** The mood shift is the same number of points and the answer noise is the same size, so the mood signal-to-noise is unchanged. Subtlety only shrinks the factor, and helps the bias solely by keeping people off the rails.
**Consequences:** (1) The defect is **partly self-limiting**. Mood is only applied where the user has no preference, so under-reading a decisive person's mood costs little on the factors they are decisive about. The genuine harm case is a person firm on the six contrast factors and soft on the four tone-matched ones — simulated at **3%**, but the author's own sheet is in that bucket, so with one of two real testers in a 3% bucket the population model is still wrong in an unidentified direction. (2) A **finer answer scale** is the cheap lever and remains open: 7 points, cards unchanged, gives 7.0 / 0.46 / 77% against today's 6.7 / 0.52 / 72%, because the top category narrows from *anything above 75* to *anything above 82*. It also raises reachable scores from 9 to 19 and firmness levels from 5 to 10. **But it dies on noise** — if a seven-way choice is even slightly less consistent than a four-way one, it lands at 8.3 / 0.54, worse than today on both. That is a UX question, answerable with one tester. (3) A four-way swipe cannot hold seven options; adopting the finer scale means abandoning the swipe.
**Alternatives considered:** *Cards that do not name the factor* — rejected on factor cost above. *A louder tone contrast* — improves mood (0.52 to 0.46) but not the bias (74%), because louder tone pushes more people onto the rails rather than off them. *Adaptive allocation of the contrast to soft factors* — already rejected earlier today as a null.

## [2026-09-08] The answer values set firmness, not matching — and are not to be tuned yet
**Decision:** Hold `LOVE 88 / YES 62 / NO 38 / HATE 12`. The next test changes the **words only** — `LOVE IT / UP FOR IT / NOT FOR ME / HATE IT` — with values unchanged so the sheet stays comparable to the five already collected.
**Context:** Tested eight value assignments against the five real sheets. **Widening the values does not change who a person matches to** — the nearest vibe changed 0 of 5 times in six of the eight assignments — and it makes the distance *worse*, 94 at today's values rising to 146 at `100/75/25/0`, because vibes average 48.7 and stretching users outward moves them away from the middle of the library. What the values do control is **firmness**: mean 0.41 today, 0.48 at `92/68`, 0.60 at `100/75`. Firmness drives blend weight, bend width and abstention, so this is a real lever pointed at the group engine rather than at matching. **The middle two labels matter more than the ends** — 57% of all answers across the five sheets were `YES` or `NO`, so moving `YES` from 62 to 70 shifts mean firmness as much as moving `LOVE` from 88 to 100.
**Why the wording is tested first.** The current labels are **intensity** words; the replacements are **stance** words. *No* rejects the thing, *not for me* only says it does not fit — which should be easier to give than `HATE` and pull people off the rail, which is exactly the censoring defect above. `DON'T MIND` was proposed and swapped for `UP FOR IT`: a shrug sits near 55 against *not for me* at 32, putting the midpoint of the middle two at **44 rather than 50** and tilting the whole scale negative.
**Consequences:** (1) Values cannot be re-fitted before the wording test, because if the new words shift the answer distribution the fit would have to be redone against it. (2) A structural mismatch surfaced and is **not addressed by any of this**: vibe scores run 5 to 100 while card answers can only reach 12 to 88, so **13% of the vibe library sits outside anything a user can produce.** This may be part of why real testers keep landing far from every vibe, and it is a property of the library, not of the scale. (3) Five sheets, four of them the same person — every number here is indicative only.

## [2026-09-08] The instrument splits — 20 clean factor cards for everyone, 6 mood cards only when the factors don't decide the night
**Decision:** Mood leaves the factor cards. **Everyone answers 20 factor cards carrying no affective tone at all.** Mood is measured by **a separate short set, issued conditionally** — only to users whose factor scores do not determine their night. The trigger is **five or more factors sitting within 13 points of neutral, counting only factors whose two cards agreed**. This reverses the decision of 2026-09-07 that there would be no separate mood instrument.
**Context:** The integrated design asked twenty cards to do two jobs, and the conflict between them caused most of the faults logged this week. Tone-loading is what admitted the content leak that produced Arnav's v6 gaps; removing the leak in v7 removed the gaps with it — **five of six tone pairs fired on v6, one of six on v7, mean gap 29.0 falling to 4.3.** Tone in text does not read, and the cost of trying was borne entirely by the factor scores. Separating the instruments ends the trade: the factor cards get to be about factors, and mood gets cards designed to measure mood.
**Why conditional.** Mood exists to supply the level where the score has no preference, so it is worth measuring exactly when a person has a lot of those and not otherwise. At the chosen threshold it fires for about **52%** of a simulated population and **3 of the 5 real sheets**. A decided user pays nothing. The earlier adaptive experiments failed because they reallocated a fixed budget among everyone; this one varies the budget itself, which is where adaptivity actually pays.
**The trigger must read the gap, not the score.** `LOVE + HATE` and `UP FOR IT + NOT FOR ME` both average to 50, and they mean opposite things. On Arnav's v6 sheet **one of his five 50s was a LOVE/HATE** — he would have been sent mood cards for a factor he held a violent opinion about. Any factor whose two cards disagree by more than one step is **excluded from the neutral count** and treated as a card fault instead.
**Consequences:** (1) The reopened comparison is not the one that was settled. A standalone ambient-image instrument was designed and discarded on 2026-09-07 as *strictly worse than the integrated version* — a judgement that assumed the integrated version worked. It does not, so the comparison must be rerun against a floor of zero. (2) **The one surviving constraint from that discarded design still holds**: mood imagery must never depict a venue, and tone must be carried by light, framing and motion rather than by changing what the place is. (3) Card count becomes variable — 20 for a decided user, ~26 for an undecided one. The four-way swipe and the values `88 / 62 / 38 / 12` are unchanged. (4) Every rule that reads a pair gap reverts to its original meaning: **a gap is a card defect again, not partly mood.** (5) The `SCEN` leak risk introduced by carrying tone in light disappears with the tone.
**Alternatives considered:** *Keeping mood inside the factor cards* — rejected on the v7 evidence above. *Issuing mood cards to everyone* — rejected, it spends cards on users whose factors already decide the night and reintroduces a fixed budget. *Asking a mood question at plan time instead of test time* — **not rejected, and still the stronger idea**: mood is defined in the spec as momentary affect at swipe time, so a reading taken at onboarding is stale by the second night out. Conditional mood cards fix the measurement; they do not fix the staleness. Both may be needed, and the plan-time question is logged here as open.

## [2026-09-08] A LOVE/HATE split is a card fault — card set v8 says the factor and nothing else
**Decision:** Card set **v8** replaces v7. All affective tone is removed. Every card states its factor and nothing else, and the two cards in a pair differ only on **which aspect of that same factor** they show — never on a second dimension of any kind. Full set in `CARD_SET_V8_CLEAN.md`.
**Context:** The insight is the user's: `YES + NO` genuinely means no preference, but `LOVE + HATE` means *"I love what this card says and hate what that one says"* — which is not a person being undecided, it is **two cards measuring different things**. Every LOVE/HATE observed so far has had a nameable second dimension in the wording. Arnav's v6 `FOOD` pair split 76 points on *everyone reaching across the table*, which is `AFFIL`, and he is 88 on it. An earlier tester's `FOOD` pair split on **how far you would travel for the dish** — effort, which is not one of the ten factors and not something the card was meant to ask.
**The new rule, beyond the existing ones.** A card may not introduce **difficulty of any kind** — distance, effort, cost, planning, or breaking an existing plan. These read as a hidden eleventh dimension and split a pair on something nobody chose to measure. *"Food so good it is the reason you came"* asks about food; *"food worth travelling across the city for"* asks about food **and** effort, and a person can love the first and hate the second while feeling exactly one way about food.
**Consequences:** (1) The pair-disagreement alarm is restored to full strength and given a threshold: **a gap of more than one step is a card defect**, to be fixed rather than interpreted. v7 already reads well on this — Arnav's disagreement fell from 6 of 10 pairs to 2 of 10 — and v8 should reach 0 or 1. (2) The remaining v7 defect is fixed: its `PLAY` pair split 26 points because card 7 was abstract (*doing something*) and card 13 concrete (*a game or a sport*). Abstraction level is itself a second dimension. Both v8 `PLAY` cards are pitched the same way. (3) **The two cards of a pair stay at least six apart on the sheet.** With tone gone the reflex to repeat an earlier answer would manufacture agreement, silencing the alarm that now does all the work. (4) Answer wording stays as the stance set — `LOVE IT / UP FOR IT / NOT FOR ME / HATE IT` — tested on Arnav and found to change nothing (50% at the extremes against 55%), so it is kept as neither better nor worse and one variable fewer.
**Alternatives considered:** *Two identical cards per factor* — rejected; two angles on the same factor read the factor better (factor error 9.2 against 10.2), and showing someone the same sentence twice invites a consistency answer rather than a considered one. *Treating a LOVE/HATE split as a hidden extra factor to be measured* — genuinely attractive and **held, not rejected**: each pair yields exactly one number, so the gap can pay for mood, or for an eleventh dimension, or for a card-fault alarm, but not for two of them. It is currently spent on the alarm. Revisit only after the alarm reads clean.

## [2026-09-09] The vibe name is generated from the user's own scores, not matched to a library
**Decision:** The user-facing vibe is **built from the person's factor scores** rather than looked up in the 42-vibe library. The rule is **highest factor + refused factor**:
```
high    = the factor with the highest score        (ties: first in factor order, for now)
refusal = the lowest-scoring factor AT OR BELOW 25 (HATE+HATE = 12, HATE+NOT FOR ME = 25)
          -> if nothing is at or below 25, there is no refusal and the label is one part
label   = "<high>, not <refusal>"   or just  "<high>"
```
**Stickiness: a label does not change unless the new reading beats it by 15 points, and the two halves are held independently** — the refusal slot survives unless that factor has climbed clearly above 25, and the high slot survives unless another factor beats it by 15. Without the per-half rule, someone flipping between a two-part and a one-part label counts as a change and stability drops from 82% to 69%.
**Context:** Four real testers made the library untenable as a naming mechanism. **Three of the four sit 121 to 213 from any of the 42 vibes**, against a median 110 between neighbouring vibes — only Arnav's v7 sheet lands at a defensible 76. Ruchi is the clearest case: `LIVE` 100 and `HERIT` 90, and **zero of 42 vibes have both above 75**. She sat **213** away on the rating and **162** on the swipe, so both instruments independently placed her outside the list. This is the hole predicted structurally on 2026-09-08 — `PLAY`, `LIVE` and `HERIT` each have only 3 to 5 vibes above 75 — and it is not fixable by adding vibes, because the same analysis found 32 of 45 factor pairs with at least one empty corner. **A generated label cannot have a hole**, which is the whole reason for the change.
**Why highest + refusal rather than the alternatives.** Measured across schemes: top 3 factors gives **120 labels, 38% stability, 0.8 people in 100 sharing yours** — worse than the library on every count. Top 2 gives 45 / 47% / 2.2. Top 1 gives 10 / 62% / 10.0. **Highest + lowest gives 90 / 38% / 1.1 but groups people tightest — two users sharing a label sit 197 apart against 210 for top 2 and 243 for top 1.** Social density is the binding constraint on label count, and it does not bind here: social features are not planned until roughly 1,000 users, at which point 90 to 100 labels still leaves about 11 people per label.
**Why the refusal test rather than the plain lowest.** Everyone has a lowest factor; not everyone refuses anything. **Meher's lowest was `PLAY` at 54 — she is mildly positive about games**, and "not games" would have been simply untrue. Ruchi's swipe sheet bottomed out at 38, also not a refusal. Nine of eleven real sheets have something at or below 25; the two that do not are exactly the two whose readings were soft — one inflated (19 of 20 answers positive), one compressed by the four-way scale. **The absence of a refusal is therefore a free diagnostic that the reading is weak**, pointing at the same people a low-spread flag catches.
**Consequences:** (1) **The 42-vibe library is no longer the source of the user-facing name.** It remains in use for **bend flags**, which fire on nearness to a flagged vibe per the decision of 2026-09-05, so it is not retired. (2) **Stability is a noise problem before it is a scheme problem** — the same label survives a retake 56% of the time on a clean reading and **19% on a messy one**. The 0–10 rating buys nearly triple the label stability of the four-way swipe, which is a point in its favour that had not come up in any earlier comparison. (3) **The ten one-word labels carry disproportionate weight.** Simulation says 97% of people would have a qualifying refusal, but the real sheets say 9 of 11 — so if the true rate is nearer 80%, one person in five lands in a pool of only ten names. Those ten should be the best-written. (4) About **100 names have to be written**, and that is the part of this that cannot be computed.
**Alternatives considered:** *Breaking ties by distinctiveness — the factor furthest from the population average* — **proposed by me and then withdrawn**: stability is 38% either way, identical, and on the real sheets it made Arnav less consistent (4 labels to 5) and flipped Ruchi's swipe reading away from `LIVE`, breaking the one agreement across both instruments. It may still be worth adopting for **meaningfulness** — it turns Arnav from "wants their own group", which describes every tester, into "wants a packed room" — but not for the reason I originally gave, and it needs real population averages that do not exist yet. Ties stay first-come. *Five broad themes* — 5 labels, 72% stable, 20 per 100 sharing, the best numbers of anything tested, and it **collapsed on contact with real data**: "The Inner Circle" came out strongest for 8 of 11 sheets because `AFFIL` averages **85.7** across all testers and identifies nobody. *Naming a fresh vibe per user with a model* — rejected, it destroys the social function entirely and supports no heatmap or filter; a hybrid that names a new vibe only when someone lands far from all existing ones remains open and is what would have caught Ruchi. *Adding six more vibes to fill the mapped corners* — superseded; generation removes the need.
**What is not established:** the population averages underpinning any distinctiveness rule come from **eleven sheets, six of them the same person**. The factor spreads that make `HERIT` (32), `LIVE` (29) and `PLAY` (29) look like the discriminating factors, and `AFFIL` (9) and `NOV` (6) look useless, rest on that same thin sample. Every scheme tested this session collapsed on a different property of the population, and there is not yet a population.

## [2026-09-09] The population centre is a running average, not a constant
**Decision:** Wherever the engine needs to know what an ordinary score looks like — the distinctiveness rule behind a vibe name, any future re-centring of firmness — it uses a **running average of every user so far, per factor**, not a fixed 50 and not a frozen table. **A user's vibe name is written once, at assignment, and is not recomputed when the centre moves.**
**Context:** Seven real sheets, 140 individual answers, gave the first per-factor population figures the project has ever had: `AFFIL` 87, `ENRG` 86, `FOOD` 86, `POL` 75, `NOV` 67, `PLAY` 64, `CROWD` 61, `LIVE` 60, `SCEN` 53, `HERIT` 39. The overall average answer is **7.1 out of 10**, and every individual's own average sits between 5.7 and 8.3.
**Why a running average rather than a tuned one.** It self-damps, which is exactly the wanted behaviour and costs nothing to specify. Typical error per factor is **5.5 points at 7 users, 2.8 at 30, 2.2 at 50, 1.2 at 300, 1.0 at 1000**. No decay constant, no window length, no threshold. It moves fast while it should and settles on its own.
**Why the label is frozen at assignment.** A live centre relabels people who did nothing. Ten new users arriving change the name of **18.1% of existing users at a base of 10, 4.6% at 50, 0.8% at 300** — churn nobody asked for. Across 400 users joining: **327 label changes if everyone is relabelled, 0 if the label is written once.** Freezing gives an adapting centre for new users and no churn for existing ones. The cost is that two identical people joining months apart can carry different names, which matters only in the launch phase while the centre is still moving.
**Consequences:** (1) A label then changes only on a **retake**, which is where the 15-point stickiness rule already lives — one rule covers both cases. (2) **One announced re-baseline at roughly 200 users**, recomputing everyone once and telling them the vibe has been sharpened. That fixes the early cohort, who are labelled against the worst version of the centre, and it is a moment rather than a drift. After that, frozen for good. (3) **The centre is not usable yet.** At seven sheets it is off by 5.5 points a factor and 16 on the worst — larger than the gap between many people's top two factors, which is the thing that decides their name. Keep scoring against 50 until there are roughly 50 sheets.
**Alternatives considered:** *A fixed constant* — rejected; the user's point is that it would be wrong within a month. *A warm-up threshold, using 50 below N and the running average above* — **tested and it barely helps**: 330 label changes with no threshold, 324 at a 60-user threshold, 305 at 150. The churn accumulates across all users regardless of how it starts, so the threshold only suppresses the first few dozen. My run's caption claimed it "cuts the churn a lot" and that is wrong. *A rolling window or exponential decay* — not needed; the running mean already adapts fastest exactly when it should.

## [2026-09-09] The 7.1 average is a card fault, not a scale fault
**Decision:** Do **not** recalibrate the scale around 7. Rewrite the four cards that everybody agrees with. The correction is the user's: people answering 7 does not mean 7 is neutral, it means the card was easy to say yes to.
**Context:** Across seven sheets the average answer is 7.1 of 10, which looked like an acquiescence lean. It is not. **A uniform lean inflates every factor and leaves the spreads alone.** What the data shows instead is that the inflated factors are the ones that fail to separate anybody:

| | mean spread across seven people |
|---|---|
| factors averaging 70 or more | **12.4** |
| factors averaging under 70 | **26.0** |

`FOOD` averages 86 with a spread of **11.2**, and **six of seven** people scored it 80+. `POL` averages 75 with a spread of **8.0**. Meanwhile `PLAY` (38.1), `HERIT` (34.0) and `SCEN` (31.9) separate people cleanly. The instrument is working on six factors and idling on four.
**The diagnosis.** `FOOD` A said *food so good it is the reason you came*; `AFFIL` A said *a night spent with your own group*. **Nobody wants bad food, a dead night, or to be kept away from their friends.** None of the four weak cards asks the reader to give anything up, so agreeing costs nothing.
**The rule that fixes it: a card must claim the factor beats the rest of the night, not that it is nice.** *The food is the best part of the night, not just part of it* is answerable only by someone for whom that is true. This does **not** violate the no-difficulty rule of 2026-09-08 — that rule bars external friction (distance, effort, cost, planning) because it smuggles in an eleventh dimension. Claiming a factor outranks the rest of the person's own night is internal ranking, which is the thing being measured.
**Consequences:** (1) Only `FOOD`, `AFFIL`, `ENRG` and `POL` are rewritten. **`PLAY`, `HERIT`, `SCEN`, `CROWD`, `LIVE` and `NOV` are left alone** — they already discriminate, and raising their bar would push them into a floor effect, which is the same fault mirrored. `HERIT` is already at 39. (2) If the rewrite works, the population centre falls and the spread of those four rises. **That is the test**, and it needs the next batch of sheets. (3) The adaptive centre logged above is unaffected and still needed — the centre will never be exactly 50 even with perfect cards.
**Alternatives considered:** *Recalibrating firmness around the observed centre* — rejected as treating the symptom; it would bake four bad cards into the engine's arithmetic. *Forced-choice items to cancel the lean* — tested on 2026-09-08 and shown to buy about one percentage point, because a lean is common to both halves of a comparison and cancels either way.

## [2026-09-09] Firmness is measured against the person's own answers, not against 50
**Direction, not yet implemented.** How much a member's opinion counts **in a group blend** stops being distance from the midpoint and becomes **distance from that person's own average, scaled by how many of their own factors sit at the same level**:
```
mean     = the person's average across their ten factors
near     = how many of their ten factors sit within 10 points of this one
firmness = min(1.0, |score - mean| / 50 * (1 + (10 - near) / 9))
```
Both directions count. A 70 from someone averaging 40 is a strong yes; a 70 from someone averaging 95 is a strong no; a 70 from someone averaging 70 is nothing.
**This changes nothing about the vibe name.** The name stays **highest factor + refused factor at 25 or below**, computed on raw scores. See below for why it cannot move it.
**Context: the current rule only detects "no opinion" when someone parks at 50.** Firmness-weighting exists so that a member without a view does not drag the room — but a member can have no differentiated view at any level. Meher rates eight of ten factors between 80 and 90; she has expressed no preference *between* options, only a high baseline, and the current rule hands her a **full 0.80 vote on four of them**.
**Evidence.** Across the three testers with two readings each, scores a person gave to **many** of their own factors moved **13.8 points** between sheets; scores they gave to **few** moved **9.5**. Thin — 20 observations against 6 — but the direction is consistent, and Meher's own case is clean: her `PLAY` 50 moved **0 points** across two different instruments and her `NOV` 60 moved 2, while her four 90s moved 15, 15, 2, 2 and her three 80s moved 18, 5, 18. **Her two most distinctive answers are her two most reliable, and the current rule scores `PLAY` 50 at firmness 0.00** — the most solid fact on her sheet, discarded for sitting on the midpoint.
**What it does to a real room.** Meher, Arnav and Divit together are currently sent somewhere good-looking, old, with live music — `SCEN` 62, `HERIT` 46, `LIVE` 60. Arnav scores those **20, 10 and 50**, so he is dragged 42 points off his own preference on a factor he actively refuses, because Meher's pen sat at 90 and the engine read that as conviction. Under the new rule the blend moves to `SCEN` 42, `HERIT` 27, `LIVE` 39 and his miss halves. Average voice in the room goes **Meher 0.62 to 0.33, Arnav 0.62 to 0.67, Divit 0.39 to 0.58** — the loudest voice becomes the person with strong views in both directions rather than the person who answered high.
**Why it cannot touch the vibe name.** Subtracting a person's own average is the **same adjustment to all ten factors**, so it cannot change which is biggest — everyone in a race running five seconds slower has the same winner. The frequency multiplier varies per factor and *can* reorder, but only factors that were near-tied already: **3.7% of the time in simulation and never for any of the five real testers.** What does move a name is subtracting a **different** number per factor — 87 off `AFFIL` but 39 off `HERIT` — and that is the population centre, logged separately and parked.
**Consequences:** (1) **Apply to group weighting only. Venue scoring keeps the raw scores.** Under the new rule someone who rates everything 90 and someone who rates everything 50 both come out near-zero firmness, which is correct for "who steers the room" and wrong for "what do they actually want" — the first person did ask for high intensity. Same split as name-versus-plan. (2) `bend` also scales on firmness and would inherit this; that interaction is unexamined. (3) **Hold implementation.** Two things gate it: more sheets to confirm the replication gap beyond three people, and evidence that the group flow is used enough to matter. If most real usage is one person planning for themselves, group weighting barely runs.
**Alternatives considered:** *Rank normalisation — convert each person's ten scores to their within-person ranking* — **rejected on data**: of the five people who took both forms, rank agreed on the top factor for only **1 of 5**, against 3 of 5 for raw, mean-centred and frequency-weighted alike. Ranking forces a total order this scale cannot support; Meher has four factors tied at 90 and the tie-break is arbitrary. *Mean-centring alone, without the frequency term* — kept as the core of the rule but insufficient on its own: it is a uniform shift, so it corrects the level and not the flatness. *Recentring firmness on the population rather than the person* — a different idea, parked with the adaptive centre.
**What is not established:** three people, 26 observations. The replication gap is in the predicted direction and Meher's individual case is unambiguous, but neither is proof. **3 of 5 was the ceiling on cross-form agreement under every transform tested** — the two people who disagree, Arnav and Divit, have their top two factors within a few points and no arithmetic rescues them. That is a stickiness problem, not a normalisation one.

## [2026-09-09] Answers are rescaled to a common spread, at a third strength — and this supersedes the firmness proposal
**Direction, not yet implemented. Supersedes the firmness rule of entry 46.** Each person's ten answers are **shifted to the population centre and stretched toward the population spread, at one third of the full correction**:
```
their_mean    = the person's average across their ten factors
their_spread  = their standard deviation, floored (see below)
full_stretch  = population_spread / their_spread
stretch       = 1 + 0.33 * (full_stretch - 1)
score'        = population_centre + (score - their_mean) * stretch      clamped to 0-100
```
**The refusal tag reads the RAW score, not the rescaled one.** A tag means *they pressed the bottom of the scale* — 25 or below as answered. Everything else — matching, group weighting, bend — reads the rescaled score.
**Context: this is the user's reframing and it is better than what entry 46 proposed.** Frequency of a score is not a proxy for whether an answer is trustworthy; it is a way to **control for enthusiasm while keeping the information in it**. An enthusiastic person answering 7 to 9 across the board is not indifferent — their 5 is a definite "much less than the rest" and their 10 is a definite "most important", and their 7s to 9s are still wanted, just not at the level a moderate answerer's 7 to 9 would mean. The correction is therefore a **rescaling of the scores themselves**, not a discount applied to firmness.
**Why this replaces the special rules.** Once the scores sit on a common scale the ordinary `|score - 50| / 50` firmness works again, and so does the existing bend. Entry 46's distance-from-mean firmness and the position-in-range bend that followed it were both patches for a problem that belongs one level up. **Divit was being quietly under-weighted in every group** — not for lacking opinions but for using a narrower part of the scale; that corrects itself. Spread of average firmness across the six testers falls from 0.071 to 0.050 at a third, and to 0.020 at full strength.
**Why a third, and not the full correction.** At full strength Meher's `NOV` 60 reads 32 and her `PLAY` 50 reads 14 — the user's judgement was that these should read 40 to 50 and 30 to 40, and **a third lands exactly there: 44 and 32**. Her 90s land at 82 rather than 87, still clearly wanted, and the gap between her 90s and her 80s widens from 10 points to 12 — the ordering inside her cluster sharpens without the cluster being blown apart. **The same figure is independently right on statistical grounds.** A person's spread is estimated from ten numbers, and that estimate is badly unstable: dropping any single factor moves it by **21% for Divit, 41% for Meher and 72% for Aditya**. Shrinking an unreliable estimate toward no-adjustment is the standard response, and it lands in the same place the user's eye did.
**Consequences:** (1) **It fixes the amplification problem it would otherwise cause.** At full strength Meher's two sheets went from 8.9 points apart to 12.2 — 37% less repeatable, eating a third of the 15-point stickiness margin. At a third they stay at 8.9. Centring alone actually improves it to 7.1, because it removes a day-to-day shift in how she used the scale. (2) **Nobody who was already spread out is disturbed**: Arnav stretches 0.96x and moves at most 6 points, PS 1.05x and 2 points. Only Meher, the squeezed case, moves meaningfully at 1.25x and 18 points. (3) **The vibe name is untouched.** A linear rescale with a positive multiplier cannot reorder, so the top factor is identical for all six testers. (4) **At a third, Meher does not gain a refusal tag** — her `PLAY` reads 32. That is correct and is why the tag now reads the raw score: she pressed 5 out of 10, which is *less keen*, not *no*. The full stretch was manufacturing a rejection she never made.
**The stretch needs a floor and 8 is not it.** Someone answering 8 to everything and 9 to one thing has almost no spread and divides by almost nothing. A floor of 8 points still sends their single 9 to **100** — a person with no real opinions turned into someone with a violent one. A floor near **15** gives 86 and is the better starting point. This was proposed at 8 without checking the case it was raised for.
**Alternatives considered:** *The full stretch* — rejected, too extreme on the user's judgement and on the wobble evidence. *No stretch, centring only* — keeps repeatability best of all (7.1) and still fixes the level problem, but leaves the flatness uncorrected: Meher's ten answers stay bunched and she keeps disproportionate weight in a room. *Entry 46's distance-from-mean firmness* — superseded; it is symmetric and so cannot tell "I want a lot of this" from "I want none of it", which made bend clamp shut on exactly the factors people reject (Arnav's `HERIT` 10 got a bend of 0.90 when accepting less costs him nothing). *Position-in-range bend* — superseded with it; both were patches at the wrong level.
**What is not established:** the population centre and spread it corrects toward are **70.5 and 26.5, from seven sheets with one person counted twice**. Meher's tag under the full stretch appeared or vanished depending on whether that spread was 20 or 23, which is well inside the uncertainty at this sample size. The one-third figure is calibrated to one person's intuition about one other person, and is only trustworthy because the statistical argument lands in the same place. Ten factors will always be a thin basis for estimating a person's spread, however many users there are — that part does not improve with scale.

## [2026-09-10] The cards become fragments of a scene, because a sentence gets reasoned with and an image does not
**Decision:** Card set **v9**. Every card stops being a statement about priorities and becomes **a detail of a room you either want to be in or you do not**. *Live music, and it is why you picked the place* becomes **The lights drop and everyone turns the same way.** Full set in `CARD_SET_V9_IMAGE.md`.
**Context:** The reasoning is the user's and it explains the data better than anything I proposed. A sentence naming a priority invites deliberation — *would I mind? is turning this down a bigger cost? I did enjoy that place with a band once* — and the answer to "would I mind" is almost always no. That is the **7.1 average out of 10**, the **nine of sixteen sheets that never say a clear no**, and the four factors that everybody agreed with. An image asks a different question, one that cannot be reasoned around: **do I want to be in that room.** Since the cards become images eventually, writing them as images now tests the mechanism rather than the stopgap.
**What changed in the writing.** Cards are now short, concrete and sensory — a fragment rather than a full scene. *A room so full you have to angle through it*, *a plate you would think about again next week*, *stone, brass, a floor worn smooth in a path*. Nothing states what the person values; the room does.
**Consequences:** (1) **This reopens the leak risk that the v8 rules exist to prevent.** Every card fault of the last week came from scene-description carrying a second factor — *everyone reaching across the table* was `AFFIL` inside a `FOOD` card. Evocative cards leak; that is why they were banned. The judgement here is that **a leaky card that discriminates beats a clean card that everybody agrees with**, and the pair-agreement alarm is what catches the leaks. That alarm therefore matters more under v9, not less. (2) Known residual leaks, accepted rather than solved: `LIVE` A implies a crowd (*everyone turns*), `AFFIL` A implies a populated room (*the rest of the room*), and `HERIT` B is carried by materials, which sits close to `SCEN`. A venue cannot be shown without showing whether people are in it. (3) All 20 v8.2 wordings are retired rather than deleted, so the sixteen sheets already collected still score. `RETIRED` now holds **39** wordings across five generations. (4) **The before-and-after this was meant to test is now two changes deep** — v8.2 never reached a single respondent before v9 replaced it, so the plain-language rewrite is untested and will stay that way.

## [2026-09-10] Ties for the top factor break by what governs the night, not by list order
**Decision:** When two or more factors tie for a user's highest score, the vibe name goes to the factor that comes first in this order:
```
ENRG, CROWD            what sets your state for the evening
LIVE, PLAY, FOOD       what you are actually there to do
SCEN, POL, HERIT       attributes of the room
AFFIL, NOV             the company, and the choice itself
```
**Context: ties are the single most common fault in the data — 10 of 16 sheets.** Six are three-way, two are four-way, one is five-way. Until now the winner was decided by **whichever factor I happened to list first**, which meant two-thirds of names were arbitrary. I had tested one alternative, found it useless, and parked the problem; it is in fact the largest one.
**The grounding, and its limits.** The ordering is the user's — *`ENRG` dictates the night whereas `FOOD` and `POL` dictate elements of the night* — read through the environmental-psychology split it matches. Russell's **core affect** treats arousal as a *state* variable that colours how everything else is experienced rather than an attribute of the setting; `ENRG` is arousal. Bitner's **servicescape** (1992) separates **ambient conditions** — the things shown to drive affective response — from spatial layout and from signs, symbols and artefacts, i.e. décor and style; that is the second and third tiers. Mehrabian and Russell (1974) put arousal at the centre of the approach-or-avoid decision. **Applying any of this to Delhi nightlife is extrapolation, not established research**, and the tier boundaries are judgement.
**Evidence.** Tested on the five people who have taken both forms, which is the only ground truth available — a good rule should make a person's two readings agree:

| tie-break | forms that agree |
|---|---|
| list order (what it does now) | 3 of 5 |
| **state, then activity, then room** | **4 of 5** |
| the same with `AFFIL` promoted | 2 of 5 |
| whichever factor separates people most | 1 of 5 |

It is the only rule that improves on doing nothing. It fixes **Arnav**, who came out *Night Climber* on one form and *Crowd Chaser* on the other — `ENRG` outranks `CROWD`, so both now read *Night Climber*.
**Alternatives considered:** *Promoting `AFFIL`* — rejected, 2 of 5. `AFFIL` averages 86 across every tester, so it wins ties it should not and the name stops identifying anyone; this is the same failure that killed the five-theme scheme on 2026-09-09. *Breaking ties toward the factor that separates people most* — rejected, **1 of 5**, the worst of all. The ordering it produces (`HERIT`, `PLAY`, `SCEN` first) is measured from sixteen sheets and moves whenever the sample does. *Breaking ties by distinctiveness against population averages* — tested and withdrawn on 2026-09-08; no effect on stability.
**Consequences:** (1) The tie-break is now **fixed and stated**, so a name no longer depends on the order of a list in the source. (2) It does **not** reduce how often ties happen — 10 of 16 sheets still have one, and a four- or five-way tie still means most of the person's top factors are indistinguishable. The fix makes the choice defensible, not informative. (3) `AFFIL` and `NOV` sitting last means someone whose genuine top factor is their own group will be named for something else whenever anything ties with it. That is deliberate, and it is a real cost for people like Arnav.
**What is not established:** five people, one comparison each. A rule chosen on 5 observations, where the runner-up scores 3, is a weak result — it is adopted because the reasoning stands on its own and the data does not contradict it, not because 4 of 5 is convincing.

## [2026-09-10] A card has to fail the people it is not for

Four cards were rewritten because they tested the wrong thing. Each described
something almost nobody turns down, so almost nobody scored it low, and a factor
that everyone rates highly separates nobody.

  SCEN A  the look of the place is the first thing that catches your eye
          -> the place has a good aesthetic, and that is the best thing about it
  FOOD A  a plate you would still be thinking about next week
          -> an amazing meal is the highlight of your night, above anything else
  LIVE A  talented people playing music you will remember
          -> talented people playing, and they have the spotlight of the room,
             not the crowd
  NOV B   a place that opened last month and nobody has told you about yet
          -> a place that opened recently that nobody has told you about, and you
             are still thinking of going

FOOD and LIVE share one fault. A memorable meal and a memorable gig are things
anybody would take if offered. The question is not whether they are good, it is
whether they are the reason you left the house, so the card has to say "above
anything else" and "has the room, not the crowd" - a person who would rather the
night were about the people now has something to disagree with.

NOV B was read as a puzzle rather than a scene. "Nobody has told you about it"
invites "why not, is it bad?", which is a different question from the one being
asked. Adding "and you are still thinking of going" turns the unknown into the
appeal, which is what NOV actually measures.

SCEN A is deliberately in the vocabulary the testers use. "Good aesthetic" is
not a description, it is the word this group already reaches for, and a card that
has to be translated first is a card that gets reasoned with. Applied here only,
not across the set.

The tie-breakers for SCEN, FOOD and LIVE were rewritten to match, since a
tie-breaker that tests a different idea from its card is what has been producing
the broken pairs.

## [2026-09-10] The short branch gets merged cards, not card A

Somebody who says they are clear about tonight sees ten cards, one per factor.
Those were card A of each pair, which is half of what the twenty-card group sees
- the shorter test was also the weaker one, which is backwards.

CARD_SOLO now holds one card per factor that carries both angles:

  FOOD  an amazing meal is the highlight of your night above anything else, and
        a menu you could get lost reading

Fewer questions, but each one decides more. The trade is that a merged card
cannot be half-agreed with cleanly - somebody who wants the meal but not the menu
has one answer for two ideas. That is acceptable here precisely because these are
the people who said they already know what they want.

This cannot be applied by updateMainCards. That function matches on question
text, and card A appears in both branches of the form, so it cannot tell which
section a question is in. Form 3 has to be rebuilt - rebuildForm3 does it, and
refuses if anyone has already answered.

## [2026-09-10] The rating scale is 0 to 5, not 0 to 10

Eleven options ask for a precision people do not have. In the answers collected
so far, 21% of every rating is a flat 10 and two thirds sit at 6 or above; the
gap between a 7 and an 8 is not a real distinction anybody was making.

Six matches what the app will show anyway - a heart filling in six states - so
the form now asks the question the same way the product will. A score is the
rating times twenty, which lands on the same 0-100 axis everything else uses, so
nothing downstream changes: 50 still means no opinion, 25 and under still means
refused.

Six options also removes the fence. There is no middle, so the smallest lean has
to pick a side, where 0-10 let anyone park on 5.

What this does NOT fix: the answers are high because the cards are likeable, not
because the scale is long. Replaying the existing answers onto 0-5 moves the
average from 64.8 to somewhere between 60.6 and 68.9 depending on how people
round - it brackets where we already are. The rewrite above is the fix for the
height; this change is about matching the product and removing false precision.

Old sheets are still 0-10 and new ones are 0-5, and a raw 3 cannot tell you which
- it means 30 on one and 60 on the other. So rate() asks each question what its
own bounds were rather than keeping a list of which form is which.

## [2026-09-10] The outing plan engine is rewritten onto the current factor set

`OUTING_PLAN_ENGINE.md` §1.1 still defined the ten factors as
`SOC · SOFT · FOOD · PLAY · CULT · CAS · FUN · PREM · VALUE · CONV` — two generations stale —
while §5.3 in the same file already used the current ten. The 2026-09-04 entry corrected §5.3.1
and left the top of the document behind, so the file defined its own vocabulary twice and
disagreed with itself. Every downstream reference has been moved over: the schema comment, the
day-part example, the slot emphasis example, the evidence-source table, the shrinkage example,
the evidence-weight example, and the §12 gotcha list.

A mapping table is now recorded at §1.1.1 so nobody has to re-derive it. Only `SOC` → `CROWD` was
ever written down; the rest are reconstructed from the definitions, and the note says so. `VALUE`
and `CONV` are retired as *factors* but not as *concerns* — spend and travel are a manual input
and a hard filter, which is a stronger guarantee than a weighted term a match score can trade away.

**One conflict was found and deliberately not resolved.** `FACTORS_AND_VIBES_V4.md` lists `PLAY`
and `LIVE` as shortfall-only; §5.3's executable spec has `PASSIVE = ('SCEN', 'FOOD', 'HERIT')` and
treats both as participatory. Under the first, an unwanted band costs nothing; under the second it
costs. §5.3 has the better argument — a band too loud to talk over is a real harm, and its comment
says exactly that — so §1.1 now follows §5.3 and the disagreement is flagged in place rather than
being settled by whichever file was open.

It is not a small difference. On the test data most people score low on `PLAY` and `LIVE`, so the
choice changes what gets recommended for the majority of users. It needs a decision on the merits.

Also corrected while in the file: the vibe count, 30 to 42, and the companion-doc list, which
pointed at `VIBES_DATABASE.md` and `BLEND_STYLE_DATABASE.md` — the latter superseded by V2, which
itself says the old file should be deleted.

## [2026-09-10] `PLAY` and `LIVE` are participatory — the conflict is settled in favour of §5.3

`FACTORS_AND_VIBES_V4.md` had both as shortfall-only; `OUTING_PLAN_ENGINE.md` §5.3 had them
participatory. V4 is corrected.

The argument is that both are things the night does *to* you. A game you did not ask for still
takes the table and still expects you to play. Music too loud to talk over still ends the
conversation, however good the band is. Neither can be left alone the way a good-looking room or
an excellent menu can, and *can this be ignored* is exactly what separates the two classes.

`PASSIVE` therefore stays at exactly `('SCEN', 'FOOD', 'HERIT')` — three factors, not five.

**This is not a small correction.** Under the shortfall-only reading, an unwanted band or an
unwanted pool table costs a plan nothing, so the sequencer would happily route a low-`LIVE` person
into a live room. Most testers so far score low on both — Ishaan is `PLAY` 0 and `LIVE` 10 — so
the wrong reading would have mis-planned the majority of users.

## [2026-09-10] Card wording is now governed by a written model of how the reader reads

New file: `CARD_READABILITY.md`. Five rules, each recovered from a card that failed rather than
from theory, and each one changed a score.

The two that prompted it, both found while reading the ten-card form:

**A load-bearing word at the end of a sentence is not read.** The merged `SCEN` card ended
"...the design and architecture are the highlight." *Highlight* is the whole test — it separates
*this is the point of the night* from *this is nice* — and sitting last, it was skipped. The card
read as a list of agreeable nouns and scored high with people who do not care about `SCEN` at all.
It now ends "...are the main highlight of the place **for you**", which forces the reader back
into the sentence. Rule: **the word that makes a card discriminate must never be the last word.**

**The first concrete noun becomes the entire card.** The merged `PLAY` card opened "A table with
a game already set up", which reads as a board game and never widens. Somebody happy to spend a
night at an arcade or a bowling alley answers *do you want a board game* instead. It now reads
"A table with a game already set up, **or you on your feet** playing games and keeping score."
Rule: **a factor with more than one physical form needs more than one image in the card.**

Three further rules were written up from earlier failures already logged: a card describing
something good measures nothing, use the reader's vocabulary rather than the correct one, and a
card that poses a question gets the question answered instead of itself.

**What is not established:** every rule is inferred from scores. The check that would actually
test them — asking a tester to describe what they pictured for cards 1, 5 and 9 — has still never
been run on anybody. Each rule is a hypothesis about a mental process no one has observed, and the
two applied today went onto cards nobody outside the project has seen.

**No rebuild needed for either card.** A merged wording appears only in the short branch and an
A or B wording only in the long one, so no question text is ambiguous any more and
`updateMainCards` can rewrite them in place. That was not true before Form 3 was rebuilt, when
card A sat in both sections — which is what forced the rebuild then and does not now.

## [2026-09-10] A 40 is a preference, not an absence of one — the neutral band narrows to 50

`neutral` and `middling` were the same test, 40 to 60. They are two different questions and now
have two different answers:

  middling   40 to 60   was this a soft answer? Only used to spot somebody who hedged on
                        nearly everything after telling us they were clear.
  neutral    50 +/- 5   did they tell us anything at all? Only a true 50.

**A 40 is not the absence of a preference. It is one:** would rather not, would not walk out over
it. The rest of the engine already reads it exactly that way — firmness 0.20, a fully open bend,
and a weight of 0.20 in a group blend, which is to say *easily overridden by anyone who cares more*.
The band was overriding that, calling the answer no-information, and chasing the person for
something they had already told us.

The chase could not work anyway. A tie-breaker is answered on the same scale, so a 40 asked again
comes back 40 and the factor never resolves. Found on a real submission: `FOOD` scored 2 on the
merged card, the tie-breaker went out, it was answered 2, and the factor came back exactly as
neutral as it started.

**Why it matters on the 0-5 scale specifically.** A single card can only score 0, 20, 40, 60, 80 or
100. Under the old band two of those six were unresolvable, so a third of the scale was a dead end.

**Measured on the 24 real sheets:** neutral readings fall from 37 to 24. Mood cards fire on zero
sheets either way — which is worth noting separately, because it means nobody has ever qualified
for the mood form and the reason it has never been answered is upstream of the form itself.

This also subsumes the four-way exemption for 62 and 38, which was the same observation about a
different scale: *"one card on a four-way choice has no other way to sit near the middle."* Under
the narrow band those fall outside it naturally and the special case is gone.

**The user's account of his own answer, which is the evidence here:** *"a 40 isn't neutral, it
should read as someone who wouldn't prefer the factor but it's not something that would kill their
night. I am a little hungry right now; when I'm not I'd have answered lower, because food isn't an
important part of my night on the weekend — I'd rather go to a club or get beers with friends."*
That is a person describing a mild, real, day-dependent preference. The scale caught it correctly
and the band discarded it.

## [2026-09-10] A function that emails more than one person never fires on the first click

`sendMissingTieBreakers` was written to unstick one person and shipped reading
`['FORM1', 'FORM3']`. Form 1 is retired but still holds every tester's answers, so one click
emailed **ten people** — nine of them chased on answers given to cards that have since been
rewritten twice, and which no follow-up could meaningfully settle.

It also called `startFreshChain_` before sending, deliberately clearing the once-only guard that
exists to stop exactly this. The single safety mechanism in the path was switched off by the thing
it was there to stop.

Three rules from it:

1. **Bulk actions preview by default.** `sendMissingTieBreakers` now lists who would be emailed and
   sends nothing; `sendMissingForReal` is a separate deliberate call. The same shape as
   `rebuildForm3Anyway`, which was already in the file — it should have been used here first,
   since this is the more dangerous of the two.
2. **Only live forms are read.** Answers on a retired form were given on cards that no longer
   exist, so no follow-up built from them settles anything. The log names what it skipped.
3. **Undo comes with the action.** `withdrawStaleTieForms` bins the forms and forgets them so
   nothing stale merges later. It cannot unsend an email, which is the point: the preview step is
   the only real protection, because after that there is no taking it back.

## [2026-09-11] A broken `POL` pair is a question, not a fault — the split is tested before it is built

Delhi reads "dressed up" two ways: **classy**, meaning suits and dresses, and **current**, meaning
whatever is in fashion. They are not the same appetite and somebody can want one and actively not
want the other. Meher scored **80 on the classy card and 20 on the trendy one**, which averaged to
a meaningless 50 and, under the old rule, was discarded as a broken pair so `POL` scored nothing.

**`POL` is not being split into an eleventh factor yet.** The cost is real — 42 vibe vectors, 24
blend styles, the weight table, the card budget and the `PASSIVE`/`PARTICIPATORY` lists all gain a
column — and the evidence does not support it yet (see the data note below). So the second sense is
tested first, using machinery that already exists.

**The rule.** For a factor marked `SPLIT` — only `POL` — a pair gap of 50 or more is the expected
answer rather than a fault. Take the higher card as what they meant, read them provisionally at
that value, and send a tie-breaker written **in that sense only**:

    classy   Turning up smart is half the point of the night for you.
    current  Turning up in whatever is current is half the point of the night for you.

When it comes back, the losing card is dropped rather than averaged back in — a 20 on the trendy
card is not a low `POL` score, it is a different thing they did not want, and averaging it back
would undo the whole point of asking.

If people who split on the cards then confirm strongly on their own sense, the second dimension is
real and there is a case for the eleventh factor. If they do not, `POL` was one factor with a bad
pair. Either way the answer arrives without rebuilding the vibe library first.

**The provisional score is the higher card, not the average.** If the tie-breaker never comes back
Meher reads `POL` 80 rather than 50. "Wants the classy one" is a better guess than "no opinion",
and the average is the single reading already known to be wrong.

Non-split factors are unchanged: a broken `FOOD` pair is still a fault, still says nothing about
the person, and still points at the cards.

## [2026-09-11] `updateMainCards` rewrites history, and it has been quietly corrupting card-level analysis

`exportRaw` reads each question through `getItem().getTitle()`, which returns the title the
question has **now**. `updateMainCards` edits titles in place. So every response given before a card
change is exported under the wording that replaced it.

This was found while testing whether classy and trendy are separate appetites. Nineteen people
appeared to have answered both cards, giving a correlation of +0.70 — a strong case for splitting,
since `AFFIL` was added on a third of its variance being independent and this looked like half.
Dating the responses showed **only two of the nineteen had actually seen those cards.** The rest
answered "Everyone here has clearly thought about what they are wearing" or older, which does not
distinguish the two senses at all. The +0.70 was measuring nothing.

**Any claim tying an answer to a specific card wording is only safe for responses collected since
the last `updateMainCards` run.** Several readings made during the 2026-09-10 session are affected
and should not be relied on.

The trade being made deliberately: rewriting titles in place is what lets a card be fixed without
killing the form's link or discarding its responses, which has been worth it several times over.
The cost is that the sheet stops recording what was actually on screen. The fix is to store the
wording with the answer at submission time rather than reading it back off the live form — not yet
built, and it does not recover the responses already collected.

## [2026-09-11] The first forced choice went against the hierarchy

**Armaan scored `CROWD` 100 and `ENRG` 100. Asked which one is the night, he picked `CROWD`.**

The hierarchy puts `ENRG` first, so it would have called him a **Night Climber**. He says the night
is the room being packed — **Crowd Chaser**. On the first case where the list could be checked
against the person, the list was wrong.

`ENRG` vs `CROWD` was flagged as the pair most likely to be unanswerable, because a packed room and
a loud late one usually arrive together. It turned out to be answerable and the answer was not the
assumed one.

**Why this matters more than one data point normally would.** Across the first 18 sheets, 12 labels
were decided by the hierarchy rather than by anyone's scores, and `ENRG` won **5 of its 6 labels on
a tie-break and only 1 outright**. Move `ENRG` to the end of the order and five people's labels
change. So the ordering is not a tidy-up applied to the rare tie — it is the thing naming most
people, and it has now been contradicted the first time it was tested.

**Not yet acted on.** One person, one pair. Four more forced choices are outstanding. If two more
come back against `ENRG`, the ordering is not defensible and the forced choice should replace it
rather than supplement it — the label would come from what people say when made to choose, and the
hierarchy would survive only as the fallback for anyone who never answers.

Three of the four outstanding have `AFFIL` in their tie set, which tests the other open question:
`AFFIL` runs high for nearly everyone, sits within 15 of the top on most sheets, and is last in the
order so it has never won a label. If people pick "who you came with" when forced, it is being
unfairly buried. If nobody does, that confirms it is inflated and should not compete for the name
at all.

**A related bug, found by the user before it fired.** `sendMissingForReal` decided who was owed a
question from the main sheet alone, and a person who has already picked still looks tied there —
the pick is kept beside the sheet, and `evaluate()` only reads the sheet. It would have asked
Armaan the identical question again, and `startFreshChain_` clears the once-only guard immediately
before sending, so nothing downstream would have caught it. Anyone with a recorded pick is now
skipped, and the preview names them.

## [2026-09-11] First face-validity check: a sheet read as the person, to someone who knows him

Abhiraj's sheet — `PLAY` 100 outright, `AFFIL` 20, `FOOD` 20, `SCEN` 20, `ENRG` 60 — was shown
to the user, who knows him, before any interpretation was offered. The user's reading: *"this
actually reads exactly as the person he is."* Specifically on `ENRG`: *"this person is exactly one
of the lowest ENRG levels of anyone I know."*

That is the first time a profile has been checked against someone's knowledge of the person
rather than against another sheet from the same person. Retake agreement shows the instrument is
consistent; this shows it is consistent about something real.

**On `ENRG` at 60 being the lowest so far — corrected the same day.** The first reading of this
was that the population floor sits at 60 and the scale is shifted up. The user, who knows the
population, disagrees: two specific people are expected to score 40 or 20, and 60 is simply where
this person lands. One sheet is not a floor. The adaptive-centre finding from 2026-09-09 stands
on its own evidence; this sheet neither adds to it nor contradicts it.

**What the user added instead, which is a property of the factor worth recording:** `ENRG`'s
useful range is asymmetric. A 0 on `FOOD` is a perfectly plannable answer — it means do not
route through a restaurant. A 0 on `ENRG` is not a quiet night, it is *one venue, stay put*, and
the plan engine has nothing to sequence. So `ENRG` will rarely be pressed to 0, not because the
cards are easy to agree with but because almost nobody who opens a nightlife app means it. The
bottom of the scale is compressed by what the product does with the answer, and that is fine.

The consequence for naming: `ENRG` will keep tying for the top more often than other factors,
and that is partly real. The forced choice is still the right way to settle those ties, but the
frequency of `ENRG` in them is not by itself evidence of a card fault.

**This sheet needed nothing from the hierarchy.** `PLAY` won by 30 points, the only tie-breaker
was on `LIVE` at a true 50, and the whole chain — send, answer, sweep, merge, export — ran on a
stranger without intervention. It is the reference case for what a clean reading looks like.

## [2026-09-11] Three branches — how sure you are decides how many cards you get

The branch question now has three answers instead of two:

    I know exactly what I want tonight    10 cards   one merged card per factor
    I have a fair idea                    14 cards   the middle set below
    Honestly not sure                     20 cards   both cards of every pair

**The middle set was decided from pair agreement, not by hand.** Across 22 long-branch sheets and
the five on current wording, each factor's two cards were compared:

    PLAY   gap  0   never disagreed once          one card
    LIVE   gap 12   never disagreed               one card
    HERIT  gap 16   never disagreed               one card
    AFFIL  gap 16   never disagreed               one card
    SCEN   gap 16   one disagreement in five      one card
    FOOD   gap 16   two in five                   one card - see below
    ENRG   gap 16   never disagreed               two cards - see below
    CROWD  gap 20   never disagreed               two cards - see below
    NOV    gap 28   two in five                   two cards
    POL    gap 36   two in five, both broken      two cards - the classy/current split

The principle that fell out: **two cards where the factor decides the night, or where it genuinely
has two senses. One everywhere the pair has agreed on every sheet.**

`ENRG` and `CROWD` keep two cards despite their pairs agreeing. They are the top of the hierarchy
and the ones tying for first, so a second card is cheap insurance on the two readings where a wrong
answer costs most.

`FOOD` drops to one card despite its pair disagreeing, because the disagreement is between the two
cards measuring different things - "highlight above anything else" is priority, "a menu you could
get lost in" is interest, and only priority is the factor. It takes card A alone, not the merged
card, which carries the menu half.

**No new wordings.** Every card on the 14 exists on the 10 or the 20 already. Single-card factors
use the merged text; two-card factors use the pair. The form is a rearrangement.

**Scoring needs nothing.** A single-card factor on the 14 behaves as it does on the 10 - a 40 or a
60 reads at face value. A two-card factor behaves as on the 20 - a true 50 or a broken pair is
chased, and POL routes to its one-sided question. The top-factor forced choice fires on all three.

Old Form 3 sheets said "pretty clear" or "quite unsure" and are still read correctly.

Requires a rebuild - a new page and new branch choices cannot be applied in place. Form 3 has
responses, so it is `rebuildForm3Anyway`, and the link changes.

## [2026-09-11] Response latency becomes a second measure of firmness — for the app, not the forms

**Decision:** The app records how long each card is on screen before the swipe, and reads that
time as a measure of how firmly the answer is held. Shorter means the person identified with the
card instantly; longer means they had to think. The top factor becomes **highest score, tie-broken
by shortest latency**. Proposed by the user and checked with a psychologist before being logged.

**The construct.** Attitude accessibility (Fazio and colleagues, 1986 onward): a strongly held
attitude activates automatically and fast, a weak one is constructed on the spot and takes time.
Bassili (1996) found latency predicts attitude stability better than asking people how certain
they are. The IAT rests on the same mechanism. This is validated ground.

**What latency measures, exactly: strength, not direction.** A fast "hate it" is as fast as a fast
"love it." The clock says how firmly the answer is held, never which answer it is. That is the
number the engine already calls firmness — `|score − 50| / 50` — which drives group weighting,
bend and abstention, and which is currently derived from the score itself. That derivation is
circular: someone who compresses to 3, 4 and 5 has low firmness on everything by construction,
whether or not they are decisive. Latency breaks the circle. Meher is the reference case: if she
answers `FOOD` in 1.5 seconds and `HERIT` in 11, her firm 4s and her soft 4s finally separate.
This is the compression problem approached from the side rather than the front.

**The design decision inside it: the timer is not shown.** Every use of latency in this literature
is unobtrusive. A visible countdown changes what is being measured — it induces time pressure,
which speeds every answer and adds noise; it makes people answer to beat the clock rather than to
say what they identify with; and it truncates the slow tail, which is the part of the distribution
carrying the most information. A visible timer serves a different goal, forcing intuitive answers
and stopping people overthinking. That is a legitimate choice but it is a different one, and it
spends most of the signal. **Measure silently.** A quiet auto-advance around 8 to 10 seconds for
somebody genuinely stuck is fine; a countdown they watch is not. The exact duration matters far
less than the visibility — in this literature answers cluster at 1 to 4 seconds, so a cap near 10
catches the tail without cutting anything real.

**The top-factor rule.** "Highest score, tie-broken by shortest latency" asks: of the things you
rated highly, which did you rate highly *without hesitation*? That is a real identity signal, it
is automatic, and it needs no follow-up question. In the app it replaces the forced-choice
tie-breaker built on 2026-09-11, with the forced choice kept as a fallback for genuine dead heats.

**What it needs to be usable — all standard in reaction-time work:**
- a per-person baseline, since some people are simply slow; use each person's own median
- a per-card baseline, subtracting the card's average across everyone, because a complex image or
  a long sentence takes longer regardless of identification
- the first two or three cards discarded as interface learning
- the clock starting when the image is fully rendered, not when requested, and stopping at
  gesture *start*, not gesture end
- log-latency, not raw seconds; the distribution is right-skewed and a mean is dominated by the one
  person who took a phone call mid-card

**Further applications, in build order:**
1. Firmness input — group weight, bend and abstention, without the circularity.
2. Soft-4 detection — a 4 in two seconds and a 4 in twelve are different answers. This is the
   neutral detector the scale itself cannot provide.
3. Card quality — a card everyone answers slowly is ambiguous. The broken-pair check, automated,
   and per card rather than per pair.
4. Disengagement — uniformly sub-second means not reading; uniformly slow means distracted. Both
   mean "do not trust this sheet."
5. Mood routing — elevated overall latency today means less decisive today, a better trigger for
   the mood cards than counting neutrals.

**Scope.** App only. Google Forms exposes no timing, so nothing in the current test changes and
none of this can be validated before the app exists. The forms continue to measure firmness from
the score alone.

**Not established.** Every claim above about how latency will behave on *these* cards with *this*
population is an extrapolation from the attitude literature. The confounds listed are the known
ones; the cards will have their own. The first thing to check once timing exists is whether
latency-firmness and score-firmness agree for people who are not compressed, and disagree for
people who are — if it does not separate Meher's answers, it is not doing the job it was brought
in for.

## [2026-09-11] The forced choice replaces the hierarchy — it was contradicted three times out of three

Entry 61 set the threshold: two more forced choices against the hierarchy and it is not defensible.
Three have come in and all three went against it.

    Armaan    tied ENRG / CROWD                   hierarchy: ENRG    picked: CROWD
    Mannat    tied LIVE / PLAY / FOOD / SCEN      hierarchy: LIVE    picked: PLAY
    Anchal    tied SCEN / POL / AFFIL / NOV       hierarchy: SCEN    picked: NOV

Anchal's is the sharpest: she chose the factor the hierarchy ranks last of her four.

**Decision.** When the top factors tie, the label is whatever the person picks when made to choose
one. The hierarchy no longer decides anything. It survives in exactly one role: the provisional
label for somebody who has been asked and has not answered, shown as provisional until they do.

The order was recorded on 2026-09-10 as "what governs the night." Three people have now said what
governs *their* night, and it was not the thing the order predicted in any of the three cases. An
ordering that was naming twelve of the first eighteen sheets has been wrong every time it was
checked. That is enough.

**What this does not mean.** Three points cannot define a new order, and none is proposed. The
pairs contradicted were adjacent in the list — CROWD over ENRG, PLAY over LIVE, NOV over SCEN — so
it is not that the order is upside down, it is that a fixed order is the wrong instrument. People
who tie at the top are people for whom several things matter equally, and which one is *the night*
is a fact about them, not about the factors.

**In the app** this is the same rule with a better instrument: highest score, tie-broken by
shortest latency (entry 64), with the forced choice as the fallback for a genuine dead heat.

**Also confirmed on the same sheet — the `POL` split found its second case.** Anchal scored 40 on
suits-and-dresses and 100 on latest-trends, the mirror of Meher's 80 and 20. The split fired, sent
her the *current* sense, and she confirmed it at 100. One person each way is not proof, but it is
exactly the pattern the split exists to find, and the first evidence that the two senses are real
rather than one factor with a bad pair.

**And the 14-card branch ran for the first time.** Anchal took it. Fourteen cards, the right six
singles and four pairs, and a sharp reading — three refusals, a clear top set, nothing soft. The
branch works.

## [2026-09-12] The tally is 3 of 4 against the hierarchy, not 3 of 3 — and a retest held

Aditya Sharma's forced choice arrived after entry 65 was written: tied `ENRG` / `SCEN` / `POL` /
`AFFIL`, picked **`ENRG`** — the first agreement with the hierarchy. The decision stands, since
three of four against is still the ordering being wrong most of the time it was checked, but the
record should say 3 of 4 rather than 3 of 3.

**Armaan retook the test on the 14-card branch** the day after taking the 10-card one. Agreement
between the two sheets +0.86, average gap 8 points. Tied `ENRG` / `CROWD` both times. **Picked
`CROWD` both times.** That is the forced choice passing a retest — the same person, a different
form, the same answer to the question the hierarchy got wrong.

One drift worth noting: `LIVE` went 0 to 40. That is a single-card factor on both branches, so it
is the same card both times, and the move is the person rather than the instrument.

**A bug found on the same export.** Aditya mistyped his address on the tie-breaker form —
`adityasgarma2622` — and the code let what he typed override the address the form had been built
for. His pick was stored under a name that matches nothing. A personal form was made for one known
person; what they type on it is a check, not the address of record. Fixed, with a one-off repair
for the stranded record. This is the third time in three days an identity was taken from the wrong
source — the retired-form bulk send, the pick that would have been re-asked, and now this — and
the rule is the same each time: the system already knows who it is talking to, and should not ask
the data to tell it.

## [2026-09-12] The vibe name is the top factor alone — `VIBE_NAMES_V2.md`

Implemented. `labelFor()` in the script builds the name, and it is now printed when a sheet lands
and again when a forced choice settles it. `labels()` lists everyone on Form 3.

Name from the highest factor, nothing appended. A tie is settled by the person's pick; the
hierarchy gives only a provisional name until they answer. A second line carries whatever else was
within 15 of the top, `AFFIL` excluded, and is allowed to move between sheets while the name is not.

`VIBE_NAMES_V1.md` is marked superseded and kept for the record. The ten names are unchanged.

## [2026-09-12] `ASSESSMENT_ENGINE.md` — the measurement layer, written for the backend

The day-one measurement — one session of cards becoming a vector, a firmness vector, a name and a
set of flags — had never been specified. `PREFERENCE_ENGINE.md` covers refinement across weeks and
`OUTING_PLAN_ENGINE.md` covers what the profile is used for; between them nothing said how a
session is scored, and that is the part that changed most this week.

Written for a backend engineer with no context, in the same shape as the plan engine spec, with
every constant currently running on the live test and pseudocode for each step: the three
branches and the 14-card set, the 0–5 rating, the reading rules (broken pair, neutral versus
merely soft, single cards at face value, the `POL` split, refusal), firmness from the score,
**latency capture and latency firmness**, the top factor with latency as the tie-break and the
forced choice as the fallback, the label, the follow-up chain with the identity rule, rescaling
at one third against a running centre, the stored record, a list of what will bite, and a list of
what is not established.

Latency is in from the start because it cannot be added to old data later. It ships in two roles
only — the tie-break, and logged beside score-firmness on every profile — and does not feed
group weighting, bend or abstention until a stated validation criterion is met on the first 30
users. The visible-timer point from entry 64 is repeated as a hard rule.

`PREFERENCE_ENGINE.md` now carries a scope note at the top pointing here and marking its card
counts as from an earlier design. `OUTING_PLAN_ENGINE.md`'s companion list names both.
`VIEW_FLOW.md` still says 18 and 28 cards and has not been edited — it is a product-flow document
and the card counts there are a front-end concern to update.

## [2026-09-12] The app deck is fourteen cards, fixed; latency, timeout, redo and pause are specified

Six decisions, settled together and written into `ASSESSMENT_ENGINE.md` §2 and §3.

**One deck of fourteen, no branch question.** The forms ask how sure someone is because a form
cannot measure it; the app measures it from latency, so the question has no job. Twenty is not
needed because its purpose — checking answers against each other to read sureness — is what
latency does directly. Ten is too few because a merged card carries two ideas and someone who
agrees with half of it lands in the middle with no way to tell which half. The fourteen is the
set derived from pair agreement on 2026-09-11, and `ENRG`/`CROWD` keeping two cards now has a
second reason: they tie at the top most, and two cards is two latency readings where the
tie-break works hardest. The three-length design stays on the forms as the test bed.

**Score first, always.** Latency never overrides a rating — a 100 answered slowly beats a 90
answered fast. It decides only when factors are level at the top, and separately feeds firmness,
which changes how much weight a score carries in a room, never the score.

**Timeout: 12 seconds, invisible.** A safety net for somebody who put the phone down, not a
pace-setter. Answers cluster at 1–4 s with a tail to 6–8, so an engaged person never reaches it.

**Nobody is told to be quick.** The drafted instruction — *"the cards disappear after a few
moments so try and answer as fast as you can"* — would undo the measurement: it tells people
there is a clock and that speed is the goal, and latency then measures compliance rather than
accessibility. Every study behind this measures people who are not trying to be fast. The copy
is still to be settled; the constraint is not.

**Redo covers any card**, timed out or already answered. The redo is a signal with two meanings
— confused-then-got-it, or unsure-and-still-unsure — and the final rating tells them apart. So a
redone card's firmness is **half its score-firmness, and no more than its second exposure's
latency allows**: a redone 100 sits at 0.50 and can beat a clean card answered at median speed;
a redone 60 sits at 0.10 and beats almost nothing. The user's argument, accepted: an extreme
after a redo is somebody who took a moment to see the picture and then genuinely resonated, and
that resolution counts. The score itself is never touched. The 0.5 is a starting point.

**Pause tells absence from hesitation.** One timeout is ambiguous; two in a row is somebody who
has put the phone down. On the second, the deck asks "Are you there?" — Yes continues and sends
the timed-out card to the end; "No, I was away" goes back to it; silence goes back to it and
freezes. A timeout that led to a pause is absence and carries **no penalty**; the first exposure
is discarded. The penalty applies to the redo path only. This is the user's mechanism, and it
solves something the plain redo design got wrong — it labels the timeout.

**Not established:** every constant here — 12 s, the 5 s windows, the 0.5 — is a starting point,
and how often redo and pause actually fire is unknown. The 30-user validation in §6.3 is where
they are set. If redo turns out common, that is a card problem before it is a constant problem.

## [2026-09-12] Latency in the learning layer — a factor answered fast and consistently settles into the baseline and leaves the deck

**Direction for `PREFERENCE_ENGINE.md` V2. Not implemented; depends on the latency validation
in `ASSESSMENT_ENGINE.md` §6.3 passing first.**

**The mapping in one formula.** The learning engine moves a user's trait toward each day's answer
by a fixed fraction (α ≈ 0.15). Latency replaces the fixed fraction with a gain set by how firmly
the answer was held — a Kalman update where observation noise is inversely proportional to
latency-firmness. A fast, committed answer pulls the trait hard and shrinks uncertainty a lot; a
slow one barely moves either. Everything else follows from this.

**The rule the user stated:** how fast someone answers a factor's cards, over time, becomes part
of their baseline, and the factor stops being shown. Precisely: a factor is **settled** when over
the last few sessions it was answered fast (latency-firmness above a floor) and consistently
(score within a band of μ). The card leaves the deck; μ stands in for today's value; σ is held
small. The deck shrinks to whatever is still unsettled — this is the 14 → 5–9 reduction, driven
by observed conviction rather than by a schedule or a self-report.

**A second exit from the deck.** A factor answered slowly and inconsistently over many sessions
is *unanswerable by asking*. It also leaves the deck, but its μ is marked weak, and the engine
learns it from where the person actually goes rather than from asking again. The engine today
cannot tell "we have not asked enough" from "they do not know"; latency can, and the two need
opposite responses.

**The way back in — without which this is a trap.** A settled factor returns to the deck when a
re-check timer fires (one silent card every couple of weeks), when behaviour contradicts the
settled score, when the user swipes left on "same as yesterday?", or when a related factor
unsettles. Without the re-check a preference that drifts over a month is invisible until it is
badly wrong.

**Three further uses recorded for V2:** a session-quality gate (uniformly sub-second, uniformly
slow, or paused → near-zero gain, the trait barely moves); card selection weighted by expected
information given past firmness (do not spend a card on a factor they cannot answer); and the
zero-card day guarded by historical firmness, since predictable and sure are different things.

**Thresholds, all unset:** sessions before settled (3), the latency floor (above own median),
the consistency band (15), the re-check cadence (14 days), the unanswerable cutoff (5 sessions).
Same class as the 12-second timeout — build them changeable, set them from data.

`PREFERENCE_ENGINE.md` is on the old factor set, the 30-vibe library and 18/28-card decks and
needs a V2 regardless of any of this.

## [2026-09-12] Latency and bend — three levels, and the second one changes what bend means

**Direction, not implemented. All three depend on the latency validation in
`ASSESSMENT_ENGINE.md` §6.3 passing.**

**How bend works now.** A cost multiplier — `penalty = |venue − user| × 0.5 / bend` — built from
two terms multiplied: the matched archetype's base (derived from the vibe's own score going down,
40 hand-written flags going up, passive overshoot free) and the user's score-firmness scaling it,
`base × (1 + 1.2 × (1 − firmness))`. The code's own comment says why both are needed: *"firmness
alone reports that a Warehouse Head will happily accept a dead bar."* The archetype knows what the
night requires; firmness says whether the person holds it.

**Level 1 — replace the firmness term.** `|score − 50| / 50` becomes the combined firmness once
validated. One line. Fixes the compressed reader, whose 4s all read as firmness 0.6 whether meant
or not.

**Level 2 — latency decides when to trust the archetype.** The multiply cannot tell a firm 60 from
a soft 60. Someone matched to a vibe at ENRG 90 who answered 60 *fast* genuinely does not need the
loud room, and the archetype is overriding something they said; answered *slow*, the archetype's
90 is a fair prior. So blend instead of multiply:

    bend = lerp( archetype_bend, own_bend, firmness_latency )

Firm answer, bend from their own score; soft answer, bend from the archetype. "Both are needed"
was true because there was no way to know which to trust. This is the same shift the naming went
through on 2026-09-11 — from a fixed rule about the factors to what the person actually said,
with the rule kept as fallback.

It also resolves the reverted centrality experiment recorded in the code: that scaler collapsed
42% of factors to fully open because centrality and score-firmness are the same quantity.
Latency-firmness is independent of the score and can carry weight without that collapse.

**Level 3 — measure the flags.** `BEND_FLAGS` is 40 guesses about what each archetype cannot
tolerate. With latency across users, each becomes a measurement: everyone whose top is
LIVE-dominant, their latency-firmness on LIVE — near 1.0 is a measured tier A. Over a few hundred
users the flags become a table read off data. A year out.

**Needs:** for settled factors (entry 70) the historical latency-firmness stands in, since there is
no card today; `own_bend` when no archetype applies — probably `(100 − score)/100` down and
`score/100` up with the same 0.40 floor, mirroring the archetype derivation; the passive asymmetry
untouched throughout.

Level 1 ships with validation. Level 2 is the one to design properly. Level 3 waits for volume.

## [2026-09-14] Latency against every variable — 44 of 59 reached

A full pass over every variable in the assessment engine, plan engine, blend and learning layer,
asking of each whether latency (how sure the person is of the score they gave) can feed it.
Fifty-nine variables. Latency reaches forty-four: eleven directly, twenty-four by changing the
formula, nine through firmness or bend. Six constants need re-setting once latency is in. The
fifteen it does not reach are structural properties of a factor, venue-side quantities, or
latency's own plumbing.

The three that matter most, in order:

1. **The room vector.** Weight is firmness; a compressed member currently barely registers on
   anything. With latency they pull where they are sure.
2. **Priority weights.** Salience is read off score extremity today. Latency *is* salience — a
   fast answer is a factor that matters to them. A cleaner source than the score.
3. **σ's third state.** "They do not know" is currently indistinguishable from "we have not
   asked." Latency separates them, and they need opposite responses.

Two the pass found that had not been raised before: **the broken-pair rule** — if one card of a
disagreeing pair was slow, that card was a guess and the fast one should be trusted rather than
the pair flagged; and **rescaling** — apply the one-third correction more strongly to soft
answers, where it is correcting noise, and less to firm ones, where it may be correcting signal.

Full list in the session record. Everything here is post-validation.

## [2026-09-14] A worked journey exposed two gaps in the plan engine

Priya — `AFFIL` 100, `PLAY` 0, `POL` 100, all answered fast — joins a room of three at 77%
similarity. The room's style holds at 91% after she joins. The plan engine then cannot serve her:
her best stop costs 56 against a threshold of 25, and **`FLOOR` fails**.

She is not hard to serve because her taste is unusual. She is hard to serve because she is
*certain*: a 100 with firmness 1.0 has a downward bend of zero, so any venue below 100 on that
factor costs at the maximum rate. The engine is doing what it was told — a sure person gets what
she is sure about — and it exposes two things nobody had specified.

**Gap 1 — the join filter and the plan disagree.** She passed the 70% similarity filter.
Similarity is on scores; whether a plan can serve her depends on firmness. A moderate person at
77% is fine, a certain person at 77% is not. Either the join filter should use firmness-weighted
distance, or the plan should be checked before the room is offered.

**Gap 2 — what happens when `FLOOR` fails is not written down anywhere.** The honest options:
tell her the room is not a fit; relax her softest-held constraint and re-plan; or find a fourth
venue that is hers. None is specified. `OUTING_PLAN_ENGINE.md` now says so.

**And this is exactly where latency decides the outcome.** Had she answered `AFFIL` 100 slowly,
her bend would open and the speakeasy at 75 would cost a fraction of 56. Fast, and the engine is
right that the room cannot give her the night she wants — and should say so before she joins.

## [2026-09-14] Naming V3, proposed and held — the refusal tag returns only on a fast refusal; strong/soft names wait for one check

The user proposed two changes to the name: bring back the bottom factor when the score is low
enough, and let latency on the top factor choose between a strong name (*Night Climber*) and a
softer sibling for somebody who answered slowly.

**The refusal tag, gated on latency — accepted, post-validation.** It was dropped on 2026-09-11
because it took retake stability from 15 of 15 to 6 of 15. Each cause has a latency answer: the
floor is usually tied, and the refusal answered fastest is the one they are surest of; a soft 20
counted the same as a hard 0, and only the hard 0 is identity-level. So: **tag only on a fast
refusal** — score ≤ 25 and latency-firmness high on that card. A wall is stable by nature; it was
the soft nos that flipped the tag.

**Strong/soft names — held behind one check.** The idea is sound: calling a hesitant person a
Night Climber overclaims, and a softer name does not. But it puts a threshold on the name itself,
and people near the threshold flip on retakes — the instability that killed the tag, now on the
one thing that must not move. Three conditions before it is safe: latency-firmness on a person's
top factor is stable across sessions (unmeasured — added to the §6.3 validation list); hysteresis,
so once strong you stay strong unless latency drops well below the line; and ten softer siblings
written to the same rules as the ten names. There is also a copy question — whether a softer
name lands as "the app gets me" or as a demotion — that data cannot answer.

If the top-factor latency check fails, the second line already carries the distinction —
"*a night that builds, clearly*" against "*also strong on the food, dressing up*" — more safely.

Recorded in `VIBE_NAMES_V2.md` as a conditional V3 section, not a change.

## [2026-09-15] Next and Back replace timeout-and-redo — doubt is stated, not inferred

**Supersedes the timeout / redo design of 2026-09-12 (entry 69). Nothing was built on it.**

The card has three actions: **Rate**, **Next** ("not yet" — the card goes to the back of the deck
and returns after everything else), and **Back** ("show me that again" — the previous card
returns; the rating may change or stay). Proposed by the user.

**Why it is better.** The old design inferred uncertainty from a card timing out, and a timeout
is ambiguous — torn, or phone in pocket — which is why the pause prompt had to exist. Next is
uncertainty *stated*. A torn person now has a button, so a timeout means absence and almost
nothing else. The pause mechanism stays, as the consequence of two consecutive timeouts, and
fires less. A card seen again after Next is answered with the whole deck as context — a
comparative reading, and probably a better one.

**Latency accumulates across exposures.** Every look at a card is stored with its own latency
and how it ended; the total is what ranks. A card deferred for 10 s and then stared at for 10 s
is slow in total, and the rank catches it without a special rule.

**Firmness from three signals**, each able only to lower it: score-firmness × latency rank on
total latency × a Next term (one Next ≈ ×0.67) × a Back term (rating changed ×0.5, came back and
left it ×0.85). The score is never touched — a deferred 100 is still 100. The user's example: a
100 rated at once has bend near 0.10; the same 100 after a Next and 20 s in total sits near 0.20.

**Pair separation on re-insert — the user's rule.** A deferred card can land next to its partner
at the back. When it would, **the partner is pulled forward to be the very next card shown.** The
deferred card stays where it went; the partner moves away from it. Two cards of one factor are
never seen back to back in either direction.

**Two kinds of deferrer — the user's distinction.** Nexting most of the deck after 1–3 s each is
somebody who wants to see everything before rating anything: those first looks are browsing,
not doubt — drop them and score on the second exposures. Nexting most of the deck near the 12 s
timeout is somebody genuinely unsure about most things: every signal is real. The line is the
median first-look latency on Nexted cards, around 4 s to start. Logged as a session pattern
either way.

**Also written in this pass, from the FLOOR discussion of the same day:** bend has no floor at
the extremes — `bend_down(100)` is zero and latency multiplies a zero — so a full heart was read
as "only a perfect match will do." One floor at each extreme (`BEND_EXTREME` ≈ 0.10) fixes it.
And `FLOOR`, defined on 2026-09-03 but never written as code, is now in `OUTING_PLAN_ENGINE.md`
§13.4, derived from latency-shaped bend: the chain is latency → firmness → bend → overrun →
FLOOR, and no separate identity check is needed because unsure factors have wide bend and do
not overrun. What to *do* when FLOOR fails (§13.1) is still open.

`ASSESSMENT_ENGINE.md` §3 rewritten; the brief's screen-by-screen rewritten at steps 3–7;
`OUTING_PLAN_ENGINE.md` §13.3–13.5 added.

## [2026-09-15] When `FLOOR` fails, relax the softest-held constraint and re-plan

**Decided.** Closes §13.1 of `OUTING_PLAN_ENGINE.md`, opened the day before.

A stranded member's *softest* overrunning factor — lowest latency-firmness among those missing
at their best stop — has its bend opened fully for this plan only, and the plan is run again.
Up to three times. If they are still stranded after three, what remains is what they are surest
about, and the room is not a fit: say so, before they join if this runs at the gate.

**Why softest and not smallest.** The smallest overrun might be on a factor they are certain
about, and giving way on it costs them something real. The one they hesitated over costs them
least. Latency is what says which that is, and by construction the top factor and the fast
refusals are relaxed last, if ever.

Plan-time only; the stored profile is untouched. The plan card names what was eased and for
whom. Every relaxation is logged — a factor relaxed often across many members is one the venue
set is weak on, which is the plan engine saying what to go and find.

When more than one member is stranded: worst first, one factor at a time, re-plan between. The
second may not be needed after the first.

The remaining open item in that section, §13.2 — the join filter judging on scores while
feasibility depends on firmness — is unchanged. Relaxation makes it less urgent: a person who
passes the filter and then cannot be served gets a relaxed plan or a clear no, rather than a
plan that quietly strands them.

## [2026-09-15] The app deck goes back to the four-way swipe, made adaptive — reversing 0–5 and the fixed fourteen

**Reverses two decisions:** the 0–5 six-state rating (2026-09-10) and the fixed deck of fourteen
(2026-09-12). Both were right when made. Both were made before latency existed as a signal, and
that is what changes the calculus.

**Why the four-way was dropped, and why that reason no longer holds.** On 2026-09-10 the scale
was the *only* measure of how firmly an answer was held, so six values beat four. Latency now
carries firmness. The scale only has to carry direction — and four directions, with a second card
to confirm a mild one, is enough.

**The mechanism.** Every factor starts with one card. *Love* or *hard pass* ends it. *Up for it*
or *not for me* adds a second card of the same factor, from a different angle, at least three
positions later. An extreme answer is believed; a mild one is checked. The deck is ten cards for
somebody decisive, twenty for somebody mild on everything, around fourteen for most — the branch
question's outcome, from behaviour rather than self-report, per factor rather than per session.

**The floor problem, and the rule that solves it.** The four-way's real failure was that people
would not swipe *hate*: 3% of scores reached the floor against 13% on a number scale. Adaptive
does nothing about that on its own. Two things do. The user's decision: **the bottom swipe is
"hard pass" in red, and there are no emoji** — *love* in gold, *up for it* in green, *not for me*
in grey. Swiping a vomit at a picture was a social act; a hard pass is a preference. And a new
rule: **refused = hard pass on any card, or not-for-me on both.** Somebody who says *not for me*
to both angles has refused it in plain language. A single *not for me* never ends a factor, so it
is never a refusal on its own. The floor is back without needing people to do the thing they
demonstrably would not.

**`POL` always gets both cards.** A *love* on the classy card would end `POL` and hide whether
they hard-pass the trendy one — exactly what the split exists to catch. The only exception.

**The merged `S` cards retire in the app.** They carried both angles when only one card would be
shown; adaptive shows `B` whenever it is needed. Every `A` card must now carry its factor alone.

**Progress bar above the card, no number.** The deck's length is not known until the last swipe,
so "3 of 14" is wrong the moment a second card is added. The bar shows factors resolved out of
ten and never moves backwards; a mild first swipe counts as half.

**Unchanged:** Next, Back, the 12 s silent timeout, the pause, the frozen state, latency capture
and the three-signal firmness. The swipe is a faster and more natural gesture than a heart fill,
so the latencies are probably cleaner, not worse.

**Not established:** how deck length distributes across real people, and whether *hard pass* in
red gets used where *hate* with a vomit did not. The second decides whether the refusal floor
rests on the swipe or entirely on the not-for-me-twice rule. First 30 users.

`ASSESSMENT_ENGINE.md` §2 rewritten, §3, §5.3, §5.5, §11, §12 amended; the brief's step 3 and
settled list rewritten; `CARD_SET_V9_IMAGE.md` notes the `S` retirement. The test forms are
unchanged — they keep 0–5 and the three branches, because a form cannot adapt per answer.

## [2026-09-15] The front-end flow is brought up to the specs — `Front End Final V3`

`Front End Final V2 (5).docx` was a design generation behind on the swipe game: 28 and 18 cards,
a four-direction swipe with emoji including a vomit for "hate," "2 to 4 tiebreaker cards," no
Next or Back, no timeout, no pause, and a profile line deriving "group chemistry type" from
agency, which was removed from the model on 2026-09-04.

**Rewritten:** the Swipe Game Flow section, whole — the instruction screen and its no-time-no-speed
rule; the card with the progress bar (no number) above and Next and Back below; the four swipes
as words in colour, no emoji; the adaptive deck, described for the front end without the user
ever being told; the silent 12 s timeout; the "Are you there?" pause with its three branches and
the frozen state; the card that will not resolve; the forced choice as tappable tiles, not a
scale; and the reveal with the "also strong on" second line. A closing list of what the front end
never does.

**Edited, one line each:** the 28-card onboarding line; the 18-card references in Screens 3 to 5;
the "2 to 4 tiebreaker cards" line, now pointing at `ASSESSMENT_ENGINE.md`; the reveal on the
onboarding and swiped-right paths, gaining the second line; Screen 2's "same as yesterday?"
swipe, gaining a backend note to record its latency; and the two "group chemistry type" lines —
**dropped**, both from the Profile Screen and the View Profile Flow. They were marked (NEW) and
derived from agency, which was removed from the model on 2026-09-04; nothing measures it and
nothing should promise it.

**Untouched:** everything else — rooms, capsules, plans, venues, profile, search, filters.

`VIEW_FLOW.md` is rebuilt from the V2 (5) text, since it was behind the docx, and
`Front End Final V3.docx` is generated from it. `FRONTEND_SWIPE_GAME_V3.md` holds the replacement
section on its own, with the one-line edits listed, for anyone applying them to a different copy.

## [2026-09-15] The public-room list filters on plan suitability for the joiner alone; `BEND_EXTREME` is 0.20

**Two corrections from a worked example, both the user's.**

**1. The joiner's list and the host's list use different variables.** A public room already has
its plan — the host had to make one before hosting. So when a user browses rooms, the only
question is *does this plan suit me*: 70% similarity between the room's plan and the plan they
would have got, **and** a `FLOOR` check for that one person against the room's actual venues.
Nothing in it reads the other members. How much the joiner would shift the room's blend is the
*host's* question, asked when the request arrives, and it sorts the host's request list into
Strong Matches and Others. The front-end document had the blend-drift check on both lists; it is
now on the host's only.

The worked run made the point: on five rooms, the 70% rule alone passed all five. The `FLOOR`
check — which needs the venues, not the plan's average — is what separated them. The room states
(DRIFT, FRICTION, SPLIT, SPARK, STEADY), if built, belong on the host's side and inside the room
while the plan is being made. Never on the joiner's list.

**2. `BEND_EXTREME` 0.10 → 0.20.** At 0.10 a firm 100 tolerated a 10-point miss, so the loudest
venue in the set — CROWD 92, ENRG 95 — already overran a firm Crowd Chaser, and the person who
says "packed and loud" with full confidence was the hardest person to place anywhere. At 0.20 a
firm 100 accepts an 80. On the same five rooms his `FLOOR` against the one that fits fell from
0.50 to 0.26. Still a starting point; the first evidence of where it sits.

**A constant this introduces:** the `FLOOR` cutoff for hiding a room from the joiner's list.
The worked run used 0.5 — a 20-point overrun past bend at their best stop. Unset; goes in the
provisional table.

`VIEW_FLOW.md` and `Front End Final V3.docx` Join flows corrected; `OUTING_PLAN_ENGINE.md`
§13.4a added; the brief's plan-engine note and provisional table updated.

## [2026-09-16] Every stop serves every member on something they ranked — `FLOOR` v3

**Replaces the one-stop-per-member constraint (§6 of the plan engine, and `FLOOR` as defined on
2026-09-03).** The user's correction, and the reason: the old rule produced "stop 1 the
restaurant, stop 2 the arcade, stop 3 the mixer" for three people wanting FOOD, PLAY and POL —
each person's night in one hour and two hours of somebody else's. The plan card had always
promised *"for X there are cocktails, for Y there are desserts"* under every stop. The engine only
guaranteed one. The engine was the odd one out.

**The rule.** Each member's factors are ranked top-first, down to a want floor of 60. At each
stop, each member is served on the highest-ranked factor the venue actually delivers — #1 counts
1.0, #2 counts 0.5, #3 counts 0.33. If no venue delivers everyone's #1, the person missed is
served on their #2 rather than on a weaker version of their #1. The user's framing: *look for
stops that involve all the top factors; if you can't, the second top factor of whoever was
missed.* It is better than the first draft, which fell back to "the venue has a bit of the same
factor" — vague, and it treated a games bar at PLAY 40 as serving the PLAY person when it barely
did. Falling back to a different factor they ranked is personal, graded, and gives the card a
real sentence: *for Rahul, a loud room* rather than *for Rahul, some games.*

**Priorities, in strict order.** (1) Nobody gets nothing — a stop with nothing for one member
loses to any stop with something for everyone, however good it is for the others. (2) Highest
total served, weighted by debt, so whoever was served further down their list counts more at
the next stop. (3) Cost, as the tie-break — it was the objective and is now only a separator.

**Two things had to be added to make it work.** *Delivers* is stricter than *does not overrun*:
a mildly held 70 has a wide bend, so a venue at 30 does not overrun it, but it does not deliver
it either — without a floor of 55 on the venue's own score, the #2 fallback was nearly free and
a restaurant "served" the PLAY person on energy. And AFFIL counts only as a #1, for the reason
it is kept off the label's second line: it runs high for everyone and would let any table of
friends count as serving them.

**Worked, no venue has all three:** speakeasy with board games (POL #1, the others on #2), posh
arcade (PLAY #1, the others on #2), trendy mixer (POL #1, the others on #2). Fine dining loses
stop 1 despite fully serving two people, because it has PLAY 5 and the third is served on
nothing. Neha never reaches her FOOD #1 — nothing with FOOD 80+ also has something for Rahul —
which is the venue set's limit and what relaxation (§13.1, now per stop) is for.

**`FLOOR` is per stop now.** A plan fails at a stop where somebody is served on nothing.
Relaxation applies to that stop: the softest-held want of whoever would get nothing.

**Constants, all starting points:** want floor 60, delivers 55, debt multiplier 0.6, the 1/rank
weights.

`OUTING_PLAN_ENGINE.md` §13.4 rewritten with the code; §6 marked superseded; §1.4 corrected; the
brief's plan-engine notes and provisional table updated.


## [2026-09-16] Hosting freezes the plan — the refresh button goes the moment a room is public

**The user's correction, to a worked example that had the host regenerate the plan after
somebody joined.** That is backwards. A person joins a public room *because of* its plan — the
room list filtered on whether that plan suited them (§13.4a), and the plan card showed them what
each stop had for them. A plan that can change after they have joined is not the one they agreed
to, and a host who can refresh at will makes the public-room list a list of plans that may not
exist by the time anyone arrives.

**The rule.** Refresh is available while the room is private — host and co-hosts, before Host Room
is pressed. It is removed on hosting and does not return. `FLOOR` v3 (entry 80) runs at
generation and on any private refresh; relaxation (§13.1) fires then, for the people in the room
then. Joiners are filtered against the fixed result and never trigger a regeneration. Blend style
and colour keep changing as people arrive, because those are the room's identity; the plan is
what they came for.

**Two freezes, named.** *Hosting freezes the plan. Locking freezes the room.* They were being
treated as one thing.

**Where refresh survives.** The solo Create flow — nobody else depends on it — and the SHUFFL
GC's "Recreate", which is a private group that all sees the new plan together. Only hosted public
rooms lose it.

**A side effect worth having.** The "Chill Wednesday" case from entry 73 — a decisive joiner
redefining a drifting room's style — is now cosmetic. The colour and name change; the night does
not. The room states, if built, have less to guard against on the joiner's side.

`VIEW_FLOW.md` and `Front End Final V3.docx` Host Button Flow amended; `OUTING_PLAN_ENGINE.md`
§13.4 gains a "when this runs" paragraph; the brief's plan-engine notes updated.

## [2026-09-16] The 09-16 batch — POL carries a sense, NOV is a filter, SCEN/HERIT are visual, constants are set, forms retired

Seven decisions from one message, made together because they share a premise: **testing moves
into the app** (a downloadable APK) from today, so the specs must be buildable as written, with
values in every constant and no rule waiting on data the app has not yet produced.

**1. `POL` is not an eleventh factor. It carries a sense.** Two cards (classy, current), one
score, one tag ∈ {classy, current, both}. Split → the higher card's score and its sense; agree →
the average and `both`. Written as *POL 88 (classy)* or *POL 88*. At plan time the sense is a
filter on `delivers` — a `classy` person is not served on `POL` by a `current` venue — not a
weight. No new column in the vibe library. `ASSESSMENT_ENGINE.md` §5.4 has the table;
`OUTING_PLAN_ENGINE.md` §13.4b has the plan-side rule. Closes the "does POL split?" flag.

**2. `NOV` is a night-tuning filter more than a factor.** It stays in the vector and the name —
First Timer is real — but its main job at plan time is familiar-vs-new among venues that already
serve the person. Low weight in the match; decisive in the choice. §13.4b.

**3. `SCEN` and `HERIT` are visual and cannot be tested in words.** The form-era readings on them
are weak by construction, not evidence about the population. Judge them on images, in the app.
`ASSESSMENT_ENGINE.md` §12 amended.

**4. Constants are set, not provisional.** 12 s timeout, 5 s pause windows, 0.15 latency gap,
Next/Back multipliers, ~4 s browser line, `BEND_EXTREME` 0.20, `MAX_RELAX` 3, `SERVE_WEIGHT`.
The brief's table is renamed "Set, and to be adjusted from data". The first 30 app users tune
them; nothing waits on those users to exist.

**5. The joiner's list criterion is concrete.** *Strong match* = at least one stop serves the
joiner on their #1 factor. *Other rooms* = every stop serves them on something, none on #1.
*Hidden* = any stop serves them on nothing. Reads straight off `serve_level` (entry 80).
`VIEW_FLOW.md` Join flows.

**6. The plan card says when a constraint was eased.** One line under the stop, plain words:
"Eased up on crowds for Ruchi — a live room has people in it." Never hidden. A relaxation the
person doesn't know about is a plan that quietly ignores them. `VIEW_FLOW.md` Outing Plan Flow.

**7. Forms retired; images are placeholders.** `SHUFFL_Forms_AppsScript.gs` is no longer a test
bed. Every spec and flow carries a note that card images are placeholders until the final set is
decided, with the swipe-game description and instructions left intact and current.

**Also:** `OUTING_PLAN_ENGINE.md` §5.3c's sequencing loop called `fairness_satisfied` (the
superseded §6 rule); it now calls `serve_level` from §13.4, with `served` leading the score.
`PREFERENCE_ENGINE_V2.md` written — Kalman gain from firmness, three factor states
(not-yet-known / settled / unanswerable), settled and unanswerable factors leaving the deck,
hidden re-check card every 14 days, session-quality gate. Not v1; held behind §6.3 validation.


## [2026-09-16] The name becomes three parts — `VIBE_NAMES_V3`; the relaxation note goes behind ⓘ; the last-card insertion case; instruction copy set

**The name.** V2's "top factor only, everything else on a second line" is reversed on the
user's call: the label has to be *a name, not a sentence*. V3 is `[refusal prefix] [top word]
[second word]` — *Luxury Diner*, *Quiet Luxury Diner*, *Solo Luxury Diner*. Three word-lists of
ten (top / second / refusal) and every name is composed from them; the developer never invents a
word. The second word is the old "also strong on" band — within 15 of the top, ≥ 60, `AFFIL`
excluded for V2's reason — and a tie for it goes to latency then weight, never a forced choice.
The prefix is the old V1 refusal tag, brought back with the gate the 09-14 proposal asked for:
until the §6.3 latency check passes, a hard pass alone earns it; after, any refusal with
latency-firmness ≥ 0.6. One prefix, the firmest. `POL` as top reads its sense: *Luxury* for
classy or both, *Hype* for current. The ten V2 single names survive for people with nothing
within 15 of the top. Written once per session.

**The risk, stated so it is measured, not forgotten.** The one-word name was stable 15/15 on
retake; V1's two-part name was 6/15. A three-part name will move more. Two things hold it still
— the prefix gate and the 15-point band — and `REMINDERS.md` carries the check to run on the
first 30 app users. The name is "your vibe *today*", so a different day giving a different name
is design; what must not happen is the name changing within a day.

**The relaxation note.** "Eased up on crowds for Ruchi" is replaced by a softer sentence with
the mechanics behind an ⓘ. Two sentences, chosen by direction: *"Ruchi might miss out on [the
food] a little here"* when a want was eased (score ≥ 50, venue below bend); *"Ruchi might not
like [the crowd] a little here"* when an aversion was eased (score < 50, venue above bend). The
ⓘ sheet has three lines: the factor, why it was that one (least sure when she swiped), what the
stop still gives her. Never hidden; detail one tap away. §13.1 gains `relaxation_notes`.

**Last-card insertion.** §2.4's `min(position_now + 3, len(deck))` already handled it; the
prose now says it: if card A was the last card, or fewer than three remain (deferred cards
count), card B goes at the end — which can make it the very next card. The pair is never dropped.

**Instruction copy.** Option 1 of three: *Swipe how you feel about tonight. Gut call — first
reaction wins. Not sure? Hit Next and it comes back later.* Names tonight, gives Next a job,
invites speed without asking for it. Options 2 (*These aren't questions, they're moods. Go with
whatever hits first. Anything you skip comes back at the end.*) and 3 (*First reaction. Tonight
only. Next if you're not sure.*) kept here for an A/B if the data wants one.

**Re-check card: hidden**, confirmed. A card labelled "just checking" is answered as a check.

**What "build" means from here.** The user's clarification: not code written on the spot — the
developer writes the code. "Build" means the algorithm is in the spec, complete and unambiguous,
with pseudocode where the prose could be read two ways. Items C1, C2, C3, C4, C6, C7 from the
09-16 walkthrough are at that standard; C5 (blend names carrying room chemistry) and C9–C12 are
in `REMINDERS.md`, which starts today.


## [2026-09-17] Room chemistry — a member whose top factor lost out is owed it; seven states; the match is blend-shift plus chemistry; Open Night rooms host without a plan

**The rule.** *Everyone's top factor should get served. If yours is not, the room owes it to you.*
After the abstention vector is built, any member whose top factor sits outside their own bend is
**owed**: their vote on that one factor counts `1 + RECIP` (= 3) times and the vector is rebuilt.
Capped — the room never goes more than `DEBT_ALLOW` (10) points past any firm member's bend on
that factor; the allowance *is* the compromise. If the cap stops the move short of 10 points, the
debt is unpaid at the room level and §13.4's stop-level debt pays it with a stop instead.

**Why this is allowed after 09-04 said chemistry never moves the target.** That rule was written
against `PEAK`, which made the loudest voice louder and moved members who had objected. Payback
does the reverse: it makes the *quietest* voice louder — once, on one factor, as a debt — and the
cap means no firm member is pushed past bend + allowance and no one's served top factor is
unseated. It never invents a value; it reweights a stated one. The plan engine already had the
idea at stop level (`debt` in §13.4's sequencing); this moves it up to the room. Entry 31 is
amended to that extent and no further — `DRIFT`'s old "PLAY +12" stays dead.

**The user's framing, which set the trigger.** Not "you abstained on the room's defining
factor" (the first draft) but "your top factor lost out" — the member sat out `FOOD`, the stop
went to their second factor and somebody else's first, so the room owes them `FOOD`. Simpler,
and it makes `TUG` resolvable: the person who wanted the quiet dinner is owed `FOOD`, gets the
say on it, and the night gains a dinner stop.

**Seven states**, read after payback, from firmness and debt alone — no `CONSENSUS` threshold,
no agency: `DRIFT` (nobody firm), `TUG` (opposed on the same factor, a debt unpaid), `TRADE`
(two paybacks on two factors), `COMPROMISE` (a payback landed), `ANCHORED` (one firm member,
the rest easy and not owed), `SPARK` (nobody blocks a bigger night), `LOCKSTEP` (the rest).
`FRICTION` retired — it was agency. The old `SPLIT` split into `TUG` and `TRADE`: opposed on one
factor and firm on different factors are different nights. `CONSENSUS` stays as a logged number.

**Display words, positive by design, on the user's instruction** — a chip next to the blend
style: In Sync · Got Your Back · Best of Both · Along for the Ride · Something for Everyone ·
Open Night · Could Go Late. A first draft; `REMINDERS.md` carries the revisit.

**The match.** The flow doc's original "how much does this person change our blend style" check,
made precise: add the joiner, re-run, read *shift* (L1 / 500), *reinforcement* (their firmness,
same direction, on the room's defining factors) and whether the state gets worse (→ `TUG`).
Great = low shift + high reinforcement; alright = low shift, low reinforcement (the easy person);
poor = high shift or a worse state. Per-state overrides in §13.6.3. **The plan stays the gate** —
hidden if any stop gives the joiner nothing (entry 79, 82) — and the match sorts and bands what
passes. Yesterday's band rule (strong = served on #1 somewhere) moves into the gate. The host's
request list uses the same match.

**Open Night.** The user's call, reversing my draft: a room where nobody has an opinion *thrives*
when hosted, and a joiner firm on five or more factors is its perfect match. So a `DRIFT` room
hosts **without a plan card** — there is nothing to plan from, and a generic night would be a
plan nobody asked for — and the plan generates and freezes the moment anyone in it is firm on
anything. Not an exception to hosting-freezes-plan: there was no plan, and the freeze happens at
the first moment there is one. Such rooms have no gate and are listed for everyone.

**Payback is one factor, not all.** The user confirmed: a concession on your top factor buys the
say on your top factor. One sentence explains it.

**On file:** `OUTING_PLAN_ENGINE.md` §13.6 (code, worked example, state table, match, Open Night,
constants); `BLEND_STYLE_DATABASE_V2.md` header; `VIEW_FLOW.md` Host / Join / room-list / room
screen; brief; `REMINDERS.md` (chemistry item closed, three new). Also removed a duplicated
§13.4b left by the 09-16 batch.


## [2026-09-17] Payback runs through the stops, not around them — the weak-second rule, the area carrying a factor, the dedicated stop as last resort; location enters the plan engine

**The correction.** My §13.6 draft let an unpaid room-level debt fall through to "that member
gets a stop that is theirs." The user's rule is stricter and better: a stop that serves someone
on their #2 is a compromise, and whether it is *enough* depends on the #2. **Strong #2** — 70 or
more, within 10 of #1 — is nearly as good as #1, and the room owes little. **Weak #2** — under
70, or more than 10 below #1 — and the room owes them: the next stop serves their #1 by the
venue, with the others on their #2 by the venue (a diner with a good crowd) or, if they have no
#2, their #1 carried by the area (a restaurant on a pub street, so the night can build). Bend is
checked for everyone at every stop; every person gets a reason to be at every stop. **A stop for
one person alone exists only when nothing of theirs can be served any other way** — the others
low and firm on everything they rank — and there the others' bend is not checked (that is the
compromise) but a hard refusal is still a wall; past that, relaxation and "not a fit".

**Serve levels become:** #1 by venue 1.0; strong #2 0.85; weak #2 0.5; #3+ 1/rank; anything by
the area 0.5; a #2 by the venue beats a #1 by the area at equal level. `DEBT_TRIGGER` 0.5: one
weak-#2 stop, or one area-carried stop, is enough to be owed. `SECOND_STRONG` 70, `SECOND_GAP`
10, `STRONG2` 0.85, `SOFT` 0.5 — set, tune on rated plans. §13.4c has the code; §13.4's
priorities stand.

**Location.** The user's aside became a section: `CROWD`, `ENRG`, `POL`, `SCEN` are as much
the street's as the venue's. Every venue gets an area; every area gets those four scores per
time band (early / late / after midnight); the effective score is the higher of the venue's own
and the weighted area's (0.7 crowd/energy, 0.6 dress/look). Used in serving (half strength,
named on the card), in overrun (a quiet room on a packed street does not fully spare a
crowd-hater), in venue scoring, and in sequencing. Not for the six factors that are the venue's
alone. §13.7. Area scoring is a data task — `REMINDERS.md`.

**What did not change.** Room-level payback (§13.6.1) still moves the room vector — that is the
identity and the match. Its unpaid remainder now goes into §13.4c's debt, never to a private
stop.


## [2026-09-17] Location is a fallback, not a score; debt and payback refined by running nine rooms through them

**The correction.** §13.7 as first written made the area raise a venue's effective score on
`CROWD`, `ENRG`, `POL`, `SCEN` and count in overrun and venue scoring. That is not what was
asked. The venue matters most; the area is a *compromise* — when the venue cannot serve
somebody on one of those four, the street around it sometimes can: a quaint pub in an aesthetic
neighbourhood serves the friend who wants her own people and a quiet night by the venue, and the
two who wanted somewhere beautiful by the neighbourhood. So: the area is consulted only for a
want the venue fails to deliver, serves it at half strength, never raises a score, never counts
against anyone. §13.7 rewritten; `eff` removed from §13.4c.

**Nine rooms, run.** A small pool (eight venues, four areas) and nine member sets — strong #2
everywhere; weak #2; weak #2 with the others having no #2; two people owed; the quaint pub; the
dedicated stop; the same with a hard pass; two firm camps with nothing in common; one firm
person with two easy ones. Six rules came out of it that the first draft did not have:

1. **Owed only while the #1 has not been served tonight.** Kabir's arcade at stop 1 counts;
   a weak-#2 stop later does not re-open a hard payback, it only leans the choice. Without this
   every night bounced.
2. **The debt outranks the energy arc.** Neha's late restaurant after the bar was being blocked
   by the never-drop-more-than-10 rule.
3. **If the arc leaves nothing, drop it for that stop.** The night may wind down.
4. **"Nobody gets nothing" applies to people who want something.** Two members with everything
   in 40–60 were being flagged as stranded. They are *Along for the Ride*: no debt, no dedicated
   stop, a bend line on the card.
5. **Stranded** means a member with wants who cannot be served anywhere the others tolerate.
   One such, with nothing yet tonight → the dedicated stop at the next slot. Two or more → not
   one person left out but a room that does not work: relaxation, then "not a fit". Stranded
   *after* having had something → zeros accepted from there.
6. **One dedicated stop per person per night**; after it their zeros are accepted; a hard refusal
   still blocks it.

With those, every room played as the rule intends. The traces are in §13.4c. The simulation is
`scratchpad/debtsim.py`; re-run it whenever the rule changes.

**Two things worth knowing from the traces.** In the quaint-pub room the rooftop lounge would
have served the two who wanted somewhere beautiful *by the venue* — and it sat just outside the
third friend's bend on energy. The pub on the pretty street is the compromise, and it is the
right one. And in the two-firm-camps room, both people were stranded at once: the rule says
that is not a compromise to be engineered but a room to be honest about.


## [2026-09-17] Three small calls, taken by default — the 70% gate stays, a strong #2 never triggers payback, a friend's Open Night always shows its join button

Closing the last three undecided items so the package has none.

1. **The 70% plan-similarity gate on the joiner's list stays.** It passes nearly every room on
   its own (five of five on the worked set) and the per-stop check does the real work — but it
   is cheap, and it stops the list showing a room whose plan is a different *kind* of night even
   where every stop technically serves the person. `VIEW_FLOW.md` Join flow; §13.4a unchanged.
2. **A strong #2 never triggers payback.** Three strong-#2 stops leave 0.45 of debt, under the
   0.5 trigger, so within a three-stop night it cannot fire — and that is the intent: a #2 within
   10 of your #1 and at 70 or more is the compromise working, not the room owing you. Written
   into §13.4c's constants note.
3. **A friend's Open Night in "What your friends are up to" always shows its join button.** It has
   no plan and no gate; the card carries the Open Night line. Every other friend's room uses the
   same gate and match as the public list (§13.4a, §13.6.3), replacing the old "blend style
   criteria" wording that pointed at a document that no longer exists.

Also today, in passing: §12 of the assessment engine had two stale lines (`POL` "may become two
factors"; naming V3 "proposed, not decided") — fixed; and §13.4a's joiner gate still used an
overrun-only check with an unset threshold — replaced by §13.4c's serve check: hidden if any
stop gives the joiner nothing (unless they want nothing) or overruns an aversion.

**State of play.** Nothing in the package waits on a decision. What remains is in `REMINDERS.md`:
constants to tune from data, four items held behind the latency validation, a watch-list to
measure, and two pieces of unblocked work — the area scoring table and the image descriptions.


## [2026-09-17] `AREA_SCORES_V1` — 35 Delhi NCR neighbourhoods scored on `CROWD` `ENRG` `POL` `SCEN` in three bands

The data table §13.7 needed, written as a first pass from knowledge of the city rather than
measured. Thirty-five areas across south/central Delhi, old/north/west Delhi, Gurgaon and
Noida–Ghaziabad–Faridabad; three bands (7–9:30, 9:30–12:30, 12:30–3) because most of Delhi shuts
at one and the `after` column mostly says what is still open. `POL` and `SCEN` barely move
across bands; `CROWD` and `ENRG` move a lot.

**Rules that came with it.** Tag a venue by the street its door opens onto, not its address;
hotel and mall venues take the district; a farmhouse with nothing around it is `None`; a
rooftop takes the area below, its view being the venue's own `SCEN`. The band is the stop's
*arrival time* from the plan, not the clock. Replacement: once an area has six scored venues,
`CROWD` and `ENRG` become the footfall-weighted median outright; `POL` and `SCEN` keep half the
authored weight because the street itself — the minar, the arcade, the murals — is not the sum
of its doors.

**Before it ships:** five Delhi regulars mark every number they disagree with by more than 15;
three against the table changes it. Two hours. Old Delhi's `SCEN` 80 is the number most likely
to be argued with. Day-of-week is the obvious first refinement and is not in.


## [2026-09-17] Dedicated stops made precise; payback goes to the most compatible want; overall firmness scales debt; friend mode replaces debt for people who go out together; the learning layer reads behaviour

Four rules from one message.

**1. The dedicated stop, precisely.** Only when *none* of a person's wants — one or four — can be
served at any rank anywhere the others tolerate, because the others are low and firm on all of
them or because no such venue exists. If even one want is served, no dedicated stop: the next
stop heightens one of their *other* wants — whichever the group's bends allow, #1 first. And at
the dedicated stop the others are not at zero: among the venues that serve the stranded person's
#1, take the one where the others get the most on a lower want or from the street. §13.4c rules
5–7 rewritten; `payback_target` and `dedicated_stop` changed.

**2. Overall firmness.** How opinionated somebody is in general — the share of extreme swipes
(plus mean latency-firmness once validated), as a population percentile. It scales every debt
increment 0.5–1.5×: a weak-#2 stop puts the opinionated person over the trigger at once and the
easy person halfway. Same scale on the room-level `RECIP`. Assessment §6.5 measures it; §13.8
uses it. The user's reasoning: debt and payback matter more for somebody firm on everything than
for somebody firm on two factors.

**3. Friend mode.** The user's observation that debt and payback only ever arise where a plan is
generated *for* people — co-hosts, or a private plan with friends — and that for actual friends
the model is wrong: friends give way without keeping score. So, pairwise and behavioural (about
three plans together in 90 days): bends relax toward each other's firm wants — friend A at `LIVE`
0 with friend B at 88 has their ceiling lifted to B's delivery floor, ~64 — and every stop is
built from one want of each, the combinations tried in rank order against real venues, with
substitutes from the person's vibe profile when nothing pairs, and dedicated stops only when even
that fails. No debt. §13.9. Mixed rooms run §13.4c with the friend-pair relaxations.

**4. The learning layer reads behaviour.** Plan ratings, refreshes, rooms joined, venues
searched / saved / attended, the "same as yesterday?" swipe — each an observation of μ with its
own reliability, fed to the same update as a swipe. μ *is* the vibe profile; its nearest library
vibe is what friend mode substitutes from. `PREFERENCE_ENGINE_V2.md` §8b.

**What did not change.** The priorities in §13.4; hosting freezes the plan; joiners never see
debt. The nine-room simulation still runs and is being updated to rules 5–7.


## [2026-09-17] Optimisation pass on debt, payback and friend mode — seven rooms run; four variables added

"Come up with new variables if necessary and optimise this." The four rules of the previous entry
were run through the simulation (`friendsim.py`, on top of `debtsim.py`) on seven rooms. Four
things broke or read wrong, each fixed with a variable:

1. **`AVERSION_FLOOR` 55.** A person at `FOOD` 12 was being kept out of a bar because the bar
   scored 40 on food. Bar food is not a food place. A venue under 55 on a factor cannot overrun an
   aversion to it — the mirror of `DELIVERS`, which already said a venue under 55 cannot *serve*
   it. Applied to `overrun`, `violated`, and friend-mode ceilings.
2. **`SERVED_FLOOR` 0.85.** Once a heritage restaurant entered the pool, Ruchi (`LIVE` 92,
   `HERIT` 62) got `HERIT` at half strength at stop 1, was therefore "served", and then got nothing
   for two stops with nothing reachable — no dedicated stop, by the letter of "even one want
   served". Half a reason once is not being served. A stranded person's zeros are accepted only
   after one *real* serving (a #1 or a strong #2); below that they get the stop.
3. **`FRIEND_MARGIN` 10.** The relaxed ceiling sat exactly at the friend's delivery floor (64),
   so a live-band bar at 65 failed by one point. The ceiling is the floor plus ten, still capped
   at `FRIEND_MAX_GIVE`.
4. **The arc is a preference.** The not-friends pair lost a stop that served both because the
   only venue that did sat outside the never-drop-more-than-10 rule. The arc now yields to
   nobody-gets-nothing and to the friend pairing, as it already yielded to payback.

And one reorder: in friend mode, when every member has a single want and nothing joins them, go
straight to a dedicated stop each — substitutes first sent a heritage person to a club because
`SCEN` stood in for `HERIT`. Substitutes are for people with more than one want to draw on.

**Logged variables added:** `stretch` (points past their own bend a friend accepted — the card's
honesty line and what tunes `FRIEND_MAX_GIVE`) and `venue_gaps` (factor pairs no venue serves —
what to go and find). §13.10 collects every variable added today in one table.

**Traces** are in §13.4c. The one to look at is L against O: the same two people, friends and not.
As friends, A stretches on live music and B gets the live-band bar; as strangers, B gets a
polished room twice and never the act. That is the whole argument for friend mode in two lines.


## [2026-09-17] `SERVED_FLOOR` stays at 0.85 — a weak #2 once is not being served

Shown on two runs of the same room: Tara (`LIVE` 92) among two people firm-low on live music,
with a heritage restaurant at stop 1. With `HERIT` 62 (a weak #2, served at 0.5) she is under the
floor when she becomes stranded, and stop 3 is her gig. With `HERIT` 85 (a strong #2, 0.85) the
old-city stop *was* her night, her zeros afterwards are accepted, and nobody sits through a gig.
The user confirmed the floor. "Even one want served → no dedicated stop" is read as *one real
serving* — a #1, or a strong #2 — not half a reason once.


## [2026-09-17] The mutual wall — `reach` looks ahead and reserves one-each stops; a person's own bend holds at their own stop; the others are softened, not trampled

**The user's scenario.** Aarav wants energy (88) and a crowd (70), hates live music and heritage.
Bela wants a gig (88) and somewhere beautiful (70), hates energy. Chirag wants food (88), hates
heritage. Each of Aarav's and Bela's top factors is the other's firm aversion. Run as it stood,
the planner spent two stops in Hauz Khas — a quiet restaurant and a quaint pub, the only venues
inside everyone's bend — giving Aarav and Bela half a reason each from the street, and declared
the room not a fit at the third stop. Wrong on two counts: the walls were visible before the
first stop, and two people with reachable #1s should each get a stop.

**Rule 8 — `reach`.** Before planning, the best level any venue can give each person with
everyone in bend. Under `SERVED_FLOOR` means structural: reserve them a dedicated stop, take the
last slots, run the ordinary slots with their zeros accepted. If reserved stops plus one for
everyone else exceed the night, extend it to `MAX_STOPS` (3); past that, not a fit — said before
anyone joins. The scenario now runs: Chirag's restaurant (everyone gets something) → Aarav's
arcade bar → Bela's jazz bar.

**Rule 6, corrected twice.** First run of the fix sent Aarav's dedicated stop to the gig — it
served Bela too, so it "softened the others" best — while overrunning Aarav's own hatred of live
music; and Bela's to a loud live-band bar, overrunning her hatred of energy. A person's *own* bend
holds at their own stop, and if their #1 has no venue inside it, their #2. Then: among venues
that qualify, the others' overrun is *minimised* as a tie-breaker (`OVERRUN_W` 0.01), not
forbidden — the arcade steps on Bela less than the club would. "Softened" now means what it says.

**`SERVED_FLOOR` is on the best single stop**, not the sum. Two half-reasons had been adding up
to one real serving.

**Regression:** P, Q, C, H re-run unchanged in meaning; H now gives each camp its stop instead of
"not a fit". As friends (S2), the same three needed no dedicated stops at all — Aarav stretched on
live, Bela on energy, and the night was rooftop → diner → live-band bar.


## [2026-09-17] Rule 9 — a served want compensates an overrun aversion; partial serving "to whatever degree"; the Piano Man room

**The user's room.** Aarav: energy 88, crowd 70, hates live music. Bela: a gig 88, hates
energy, milder on crowd. Chirag: food 88. The user's night: **Piano Man** first — live jazz for
Bela, a good crowd for Aarav (his #2), decent food for Chirag — then, since Aarav's #1 took the
hit, **Depot 48** — decent energy (not too high, for Bela), a good crowd, some live music, good
food. And the reasoning, which is the rule: *even if a person hates live music, as long as one of
their preferences is being satisfied they will be happy.*

**What the model did before.** Bend was a hard gate at every stop. Piano Man's act overran
Aarav's aversion to live music, so Piano Man was out; Depot's energy overran Bela's, so Depot
was out; the room fell into the mutual-wall case and got one stop each. The gate was the problem.

**Rule 9.** Bend gates only a person who is *served on nothing* at that stop. For a person
served on anything, every point a venue sits past an aversion ceiling is a cost — `OVERRUN_W`
0.01 per point, only where the venue is at or above `AVERSION_FLOOR` — not a bar. A hard pass is
still a wall. Order at a stop: nobody gets nothing → most served, weighted by debt → at stop 1
the calmer venue (the night builds) → least stepping-on. Served dominates; cost breaks ties.
That last tie-break is why Depot (energy 65) beats the club (92) for Aarav's compensation: both
serve him fully, the club steps on Bela by 54 points, Depot by 27.

**Partial serving.** "To whatever degree": a venue that *has* the thing (≥ 55) but not at the
person's level serves them at half — Depot's live music at 60 for Bela's 88. By the venue,
ahead of the street carrying it.

**Run.** U: Piano Man → Depot 48, exactly the user's night; with three stops, a live-band bar. S
(the earlier mutual wall): Piano Man → Depot → rooftop, everyone served at every stop, no
reserved stops. G (a hard pass on live): Ruchi's reserved stop is her #2, the haveli, because
her #1 is walled; reserved venues are now built at the pre-pass and held out of the ordinary
pool — the earlier run had spent the haveli at stop 1 and then had nothing for her. P, C, H
unchanged in meaning.

**Consequence.** Dedicated stops are now rare, as they were meant to be. `reach` (rule 8) is
computed under rule 9's gate and fires only for someone no venue can serve at all without
breaching a hard pass or leaving someone else unserved and out of bend.


## [2026-09-17] Bend by context — stretch in a group plan, gate for a solo plan or a joiner; every firm want gets a stop

The user's framing, which is the cleanest statement of the whole §13.4 family: in a plan for a
group, *bend's role is to see how far we can stretch that user through the stops.* A firm
aversion (low score, low bend) means at least one of their wants is served to some degree at that
stop (rule 9). A firm want (high score, low bend) means at least one stop includes it — now rule
10, extending the #1 guarantee to any firmly held #2: games *and* a proper meal, not games twice.
Bend is relaxed as far as it will go for cohesion while every want is still served.

The gate is elsewhere: a **solo plan** (nobody to stretch toward — every stop inside their bend,
served at their level; §13.4d has the code) and a **room someone wants to join** (the plan was
stretched for other people; every stop must be inside the joiner's bend and serve them; rule 9's
"served compensates" does not apply to somebody who had no say in the stretch — §13.4a aligned).

`COVER_K` 0.4: uncovered firm wants pull later stops; any still uncovered are reported on the
card and logged as a venue gap. Run on the Piano Man room and on a PLAY 90 / FOOD 80 person
among two energy people: games at stop 2, food at stops 1 and 3, nothing firm left unreached.


## [2026-09-17] Two scenarios run end to end — Priya joins a room; Priya hosts with three co-hosts — and the six holes they found

**Priya**: `FOOD` 88, `SCEN` 72, `POL` 65 (classy), `ENRG` 30, `CROWD` 40, a hard pass on
`LIVE`. Name: *Unplugged Plate Chaser*. Five public rooms; the gate hides three (a loud bar past
her energy ceiling; an arcade past it too; a Piano Man plan that violates her hard pass), passes
*Slow One* (quiet restaurant → rooftop, food at both) and the Open Night. Then as host with Sana
(a friend by data), Kabir and Rohan (`LIVE` 85 — walled by Priya's hard pass): quiet restaurant →
haveli → rooftop, Rohan's live music reported as unreachable, the room *Something for Everyone*.

**The holes, each fixed:**

1. **Shift counted factors the room was indifferent to.** Priya's firm `LIVE` 12 into a room
   with no position on `LIVE` read as a 38-point shift and made a perfect room *poor*. Shift is
   now the average move per factor the room *had a position on* (over 50); a joiner bringing an
   opinion where the room had none is not a shift. Bands rescaled to 0.10 / 0.20 — five and ten
   points average. §13.6.3.
2. **The room-level payback cap moved the room *away* from the owed member.** Rohan's `LIVE`
   payback, clamped by Priya's ceiling, landed *below* the abstention value. The clamp never
   moves the vector against the person being paid. §13.6.1.
3. **A hard pass had an allowance in the room-level cap.** It has none; a wall is a wall. §13.6.1.
4. **`TUG` only looked at defining factors.** Rohan owed and unpaid on `LIVE`, opposed by Priya —
   and the room read *In Sync*, because `LIVE` sat at 47. `TUG` now reads opposition on any
   factor somebody is owed and unpaid on. §13.6.2.
5. **The joiner's gate was ambiguous** between "served on something" and "served at their
   level". Settled: by the venue, full or partial; the street alone does not count for a joiner,
   who had no say in the stretch. §13.4a.
6. **The chemistry chip could lie after hosting.** Recomputed with joiners, a room could read
   *Got Your Back* for a payback the frozen plan never made. The chip freezes with the plan;
   style and colour keep recomputing by abstention only. §13.6.3a; flow doc.

**Not a hole, but noted:** three food-first stops for a room of two food people is a
monotonous night that rule 10 accepts; a *variety* preference across stops (no factor as the
lead twice in a row unless nothing else serves everyone) is a candidate rule. `REMINDERS.md`.
`joinsim.py` runs both scenarios.


## [2026-09-17] Exploration — five factors are preferences, five are vibe factors; two new vibe factors proposed

**Not a decision yet.** `VIBE_AND_PREFERENCE_V1.md` works through the user's proposal: `FOOD`
`LIVE` `HERIT` `NOV` `SCEN` are *preferences* — how important a thing is in a place, set once at
onboarding from a picture of the thing, edited in the profile, never asked daily, and
suppressible in a group because a low score is an absence of interest, not an aversion. `ENRG`
`ACTIV` (was `PLAY`) `AFFIL` `POL` `CROWD` are *vibe factors* — the shape of tonight, both poles
wanted, measured daily, untouchable in a group plan; debt, payback, friend mode and chemistry
run on them alone.

**What the exploration found.** The asymmetry names the thing half of this week's machinery was
compensating for: rule 9, `AVERSION_FLOOR`, the Piano Man workaround all existed because
one-ended factors were being treated as two-ended. The daily deck drops to five to ten cards.
`SCEN` and `HERIT` become testable — a picture of the thing. The name reads five moving factors
and the stable identity becomes badges. Chemistry gets a literature per axis and group types
in plain words. Joining splits into shape-fit (gate) and venue-fit (sort). The plan engine
becomes two stages — shape the night on vibe factors, fill the stops by preferences — and
§13.4c survives narrowed and cleaner.

**Two new vibe factors proposed:** `ROAM` (settle ↔ hop; sets the stop count, which was set
from duration alone) and `TALK` (conversation ↔ noise; distinct from `ENRG` and `AFFIL`).
`OPEN-AIR` considered and kept out of the deck as a seasonal switch. Seven vibe factors,
seven to fourteen cards a day.

**What it costs:** a rewrite of the plan engine's §5 and §13, the assessment engine's §1–2 and
§4–7, both databases, the names. `POL` sits on the borderline (level daily, sense stable). Six
decisions listed at the end of the document; the specs are rewritten when they are taken. Written
without reference to the Google Forms results, at the user's instruction.


## [2026-09-17] The split is decided — seven vibe factors, six preferences; `PLAY` becomes `GAMES` and `MOVE`; `POL` is a preference

The six questions at the end of `VIBE_AND_PREFERENCE_V1.md`, answered:

1. **The split, with `PLAY` split again**: `GAMES` (dependent on the venue having games) and
   `MOVE` (general — dancing, being on your feet). Two vibe factors where there was one.
2. **`ROAM` and `TALK` are vibe factors.** `OPEN-AIR` is a preference of the *place*, not the
   night — and is left out altogether, being seasonal rather than personal.
3. **`POL` is a preference.** How dressed-up a place is, is a thing about the place you care
   about or don't; its sense (classy / current) stays with it.
4. **Preference is importance.** Whichever direction the swipe, it says how much that aspect of
   a venue matters, so the plan can cater to everyone's preferences as far as possible. No
   aversion, no hard pass.
5. **The name from vibe factors; preferences as badges.**
6. **Debt, payback, friend mode and chemistry on vibe factors only; rule 9 retired.** Rule 10's
   translation to preferences is explained below and awaits a yes.

**The set:** vibe `ENRG` `GAMES` `MOVE` `AFFIL` `CROWD` `ROAM` `TALK`; preferences `FOOD` `LIVE`
`HERIT` `NOV` `SCEN` `POL`. Thirteen factors. Seven to fourteen cards a day, six once.

**Rule 10 on preferences, as proposed.** Rule 10 today says every *firmly held want* appears at
some stop. After the split, vibe wants are the shape and are met at every stop, so rule 10 has
nothing left to do there. What it would do instead: for every member, every preference swiped
*the whole point* (88) must be *had* by at least one stop's venue — the venue scores at least
`DELIVERS` (55) on it — somewhere in the night. Not centred on it; has it. A food person eats
properly once. *Nice to have* (62) pulls the venue choice but guarantees nothing. If two members'
whole-point preferences cannot share a venue, they get one stop each **inside the same shape** —
no debt and no payback, because nothing on the vibe was conceded; the fill order just rotates.
Any whole-point preference the venue set cannot serve at all is said on the card and logged as a
venue gap. That is the whole of it.

**Next:** the rewrite — plan engine §5 and §13, assessment engine §1–2 and §4–7, the factor
table, the blend database, the names, the flow doc's card screens — once rule 10 is confirmed.


## [2026-09-17] Shape → type → venue: the two-stage plan engine, stated

The user's formulation, which settles rule 10 and the architecture together: **the vibe factors
give the shape of the night** — number of stops (`ROAM`), atmosphere (`ENRG`, `TALK`), crowds
(`CROWD`), things to do (`GAMES`, `MOVE`), the table or the room (`AFFIL`). **From the shape,
the venue type at each stop is chosen.** Then **preferences pick the exact venue of that type**,
each person's served at each stop as far as availability allows. **A preference never alters the
venue type — only the exact venue.**

Rule 10 becomes: every whole-point preference is *had* by some stop's venue in the night — as a
doubled pull on the exact-venue choice until it is, rotating between members whose whole-point
preferences cannot share a venue, inside the same type, with no debt. Venue types are templates
on the vibe axes; every venue carries one from its own vibe-axis scores. `VIBE_AND_PREFERENCE_V1`
§4 rewritten to this. The rewrite of the specs follows.


## [2026-09-17] The split, written in — `FACTORS_V5`, `VIBE_NAMES_V4`, `CARD_SET_V10`, `BLEND_STYLE_DATABASE_V3`, plan engine §14, assessment Part 0a, the flow doc

Everything decided in entries 96–98, now in the specs:

- **`FACTORS_V5.md`** — the seven vibe factors with both poles named and weights (`ENRG` 18,
  `AFFIL` 16, `CROWD` 14, `TALK` 14, `ROAM` 14, `MOVE` 12, `GAMES` 12); the six preferences with
  importance ends and weights (`FOOD` 20, `LIVE` 18, `POL` 18, `SCEN` 16, `NOV` 14, `HERIT` 14);
  **ten venue types** on the vibe axes; a **sixteen-shape library** replacing the 42 vibes.
- **`OUTING_PLAN_ENGINE.md` §14** — shape → type → venue. `ROAM` sets the stop count. Types
  must fit every member's bend on every vibe axis; when none does, §13.4c runs on vibe wants.
  Fill: `pref_fit` with importance as the weight, whole-point-not-yet-had doubled — rule 10 on
  preferences. Rule 9 and `AVERSION_FLOOR` retired; §5.3's passive set gone. A banner at the
  top says to read §14 first.
- **`ASSESSMENT_ENGINE.md` Part 0a** — the two decks, the two sets of four labels, scoring a
  preference (importance = score, firmness = importance / 100), `POL` sense as an image pair,
  `refused` as a firm low pole, the record.
- **`VIBE_NAMES_V4.md`** — a pole word per factor per end, two-token names, fourteen single
  names, no prefix; seven badges from preferences.
- **`CARD_SET_V10.md`** — six preference cards (the thing itself) plus the sense pair; seven
  vibe factors × A/B with both poles in each image.
- **`BLEND_STYLE_DATABASE_V3.md`** — twenty group shapes on seven axes, authored, palettes by
  rule, denominator 350; five preference-shaped V2 styles retired as styles.
- **`VIEW_FLOW.md` / docx** — onboarding gets the preference deck screen and its line; the swipe
  game flow describes both decks; the profile shows badges and an editable "what I care about in
  a place" row with a redo link; the plan card shows the stop's type and two lines per person.
  `FRONTEND_SWIPE_GAME_V4.md` is the change record.
- `PREFERENCE_ENGINE_V2` learns vibe factors only; preferences re-check slowly and are never
  auto-edited. Brief banner. V4 factors, V3 names, V9 cards, V2 styles marked superseded.

**Still owed** (`REMINDERS.md`): the simulations re-cut to seven axes plus a fill stage; the venue
database tagged and scored; styles re-derived from real rooms; weights measured.


## [2026-09-17] The shape is a negotiation, not an average — night-level factors compromise, stop-level factors alternate; the compromise sets the number, the payback shapes the stops

**The correction.** §14.3 had the shape as the room's abstention vector moved along the arc,
with a type that fits everyone's bend. That is an average with a check. The user's meaning:
the shape is what comes out when each member's *top* vibe factors are put together — which
collide, which can be compromised, which get replaced by that member's next factor. The debt
machinery, run before any venue is chosen. A solo plan skips it.

**The question.** A: `ROAM` high firm, `CROWD` high. B: `AFFIL` high firm, `ROAM` low firm.
Relax `ROAM` to the middle (two stops instead of four)? Or keep `ROAM` high for A and let B's
next factor, `GAMES`, shape the stops?

**The answer: both, in sequence — because `ROAM` is a night-level factor.** The stop count is
one number both people live with; it cannot be served one stop each. So a `ROAM` collision is
settled by a firmness-weighted middle (approach 1). That creates a debt, paid by approach 2:
whoever ended further from their pole has their next-firmest vibe factor promoted into the
per-stop shape. Settled at two → A is owed, `CROWD` shapes the stops (the full rooms). Settled
at three → B is owed, `GAMES` shapes them (booths in games bars). Pure approach 2 is wrong for
`ROAM` — four stops with games at each is a consolation on a different axis, not a compromise on
the thing B was firm about; pure approach 1 is the average the engine exists to avoid.

**Stop-level factors** (`CROWD` `TALK` `MOVE` `GAMES` `AFFIL`, `ENRG` at a stop) collide
differently: first look for a *type* that serves both wants — `CROWD`-high and `AFFIL`-high do
not collide at all, a full room with a booth serves both — and if none, alternate across stops
with §13.4c's debt and payback. §14.3 rewritten; `stop_type` is `pick_best` over venue types.


## [2026-09-17] The simulations re-cut to the split model and the scenarios re-run — no walls on vibe factors; the order at a stop; coverage as the last tie-break; friend stretch reaches implied factors

`splitsim.py`: seven vibe axes, the ten venue types, a negotiation on `ROAM`, `pick_best` over
types, a fill stage on six preferences, seventeen venues. Twelve scenarios (the user's `ROAM`
case twice, the Piano Man room, the gig person, the quaint pub, the two energy camps, friends
versus not, games-versus-heritage, one firm person with two easy ones, the whole team out, Priya
hosting three). Traces in §14.8. What the runs changed:

1. **No walls on vibe factors.** With a hard pass as a wall, a love at 88 had to be one too, and
   Aarav-88 against Bela-12 left no type passable — a crash. A hard pass is a firm low pole, a
   want; extremes are handled by the reserved one-each stop, as designed.
2. **The order at a stop**, in full: nobody gets nothing → most served × debt → least stepping-on
   → variety (not the previous type) → calmer first at stop 1 → **whole-point coverage** → closeness
   to the room's firmness-weighted target. Cost had been sitting below the arc, which sent the
   whole team out to a quiet table first; closeness had been unweighted, which sent one firm
   person to a live room instead of a club because the easy people's 50s pulled the target.
3. **Coverage as the last tie-break.** The gig person's room tied between a pub and a street
   market on every shape criterion; only the pub's pool had an act. Preferences still never
   *alter* the type — this fires only between types the shape cannot tell apart — but it is the
   one place a preference touches the shape, so it is flagged for the user's veto.
4. **Friend stretch reaches implied factors.** A friend's `ENRG`-high want is served only by loud
   types; the other friend's firm `TALK` would block them all. The stretch now applies to any
   factor every serving type overruns, to the same cap. Below the cap a 15-against-90 split is a
   one-each night whether friends or not — the cap doing its job.
5. **`open ground` is an early-evening type** (stop 1 only); a variety penalty had been sending
   rooms to a lawn at midnight.

**What the split delivered, on the same rooms.** The gig person no longer needs a dedicated
stop — her act is a preference the fill serves at a pub. The quaint-pub room is a table and a
jazz bar, hers by the type, theirs by the venue. The two energy camps get two mid-energy places
where he has the crowd and she can talk, nobody owed. Two whole-point preferences went un-had in
twelve rooms — a live venue of lounge type, a games bar with heritage — both venue gaps, not
rules, and both said on the card.


## [2026-09-17] Coverage as the last tie-break, confirmed — a preference is an element of the venue, never of the night

The user's reading of §14.3.3 step 6, which is the rule's justification: live music is an
element *within* a venue. A person who prefers it, entering a room of people who do not, never
alters the course of the night or the types of its venues — the engine only looks, inside the
shape, for venues that possibly have live music too. A tie between two types is the shape
having no opinion, and at that point the fill's question — can somebody's whole-point thing be
had here — is the only question left. So the tie-break stands, and it is not an exception to
"preferences never alter the type"; it is that rule applied where the shape has nothing to say.


## [2026-09-18] The shape is composed first; compromise only on a structural collision; chemistry is how the shape formed

**The user's rule.** The shape of the night is all-inclusive first: put every member's top vibe
factors together and ask whether they form an actual night. If they do, that is the night -
no bend, no debt, no payback. Only when two of them collide *structurally* - not because of
anyone's bend but because no night of that length carries both - do the variables run. And the
room's chemistry is derived from how the shape was formed.

**What "collides" now means.** `ROAM` high against `ROAM` low (a night is one place or three);
or more demand-groups than the night has stops, even with one added. `ENRG` high against `ENRG`
low on a two-stop night is *not* a collision - a calm table then the club carries both - and the
chip says so: *Best of Both*. The previous §14.3 ran the compromise machinery from the first stop
and produced two mid-energy places where each got their strong #2; the composed night gives each
their #1, once. The user's priority, taken.

**Phase A - compose.** Each person brings their top vibe factor and a strong #2. A type
*carries* a demand structurally (>= 60 for a high pole, <= 40 for a low). Partition the demands
into the fewest groups, no more than the stop count `ROAM` asked for, each carried by some type;
if that fails, try one more stop, once - a concession on `ROAM` by everyone, *Got Your Back*.
Type per group: not one already used (variety), then coverage of an un-had whole-point
preference, then closeness to the people who brought the demands. Arc-ordered. **Phase B** - the
§13.4c machinery on types - runs only when Phase A returns nothing.

**Chemistry from formation.** One group -> *In Sync*; spread across stops -> *Best of Both*; a
stop added -> *Got Your Back*; Phase B with paybacks landing -> *Got Your Back*; Phase B with a
reserved stop or an unpaid debt -> *Something for Everyone*; one person bringing everything ->
*Along for the Ride*; nobody -> *Open Night*; one group, everyone 55+ on `ENRG`, nobody demanding
it -> *Could Go Late*. Computed whenever members change (Phase A needs no venues), frozen at
hosting. The room-level payback of §13.6.1 now serves the style vector only.

**Run** (`compose.py`, ten rooms, traces in §14.8): the Piano Man room composes as a calm table
then Piano Man - Bela's act found by coverage - every whole-point preference had, *Best of
Both*. The gig person's room is *In Sync* with her act at Piano Man. Three people each bringing
one thing and all wanting one place get two places and *Got Your Back*. Only the `ROAM`
collisions reach Phase B.


## [2026-09-18] The night is designed around every member's top factor, at every stop — no dedicated stops, no debt; a top moves only when a strong #2 stands in

**The user's rule, which replaces v3 of §14.3 the same day it was written.** All members' top
vibe factors are used, by default, to design the night. If somebody has a low score and a low
bend against another member's top factor, that member's *second* top factor is used instead — if
it is strong (68 or more, 32 or less) — and if they have no strong #2, their top factor is used
anyway. No compromise machinery. The night is designed so that every member is happy to at least
a certain degree with every stop. **No dedicated stops — a stop that is one person's defeats the
purpose.** The other factors, high or low, with their bend, shape the night too, as long as they
disrupt nobody's top; top factors do not move. *A person's top factor is their reason to go out
that night and it shouldn't be absent at any stop.*

**What the rule becomes in code.** `effective_top`: the top stands unless firmly opposed *and* a
strong #2 exists. Stop count: `ROAM` as one number. Each stop: the type that keeps the
least-happy member happiest — **maximin on the top factors** — then the most total, variety, the
arc, whole-point coverage, and everything else as signals. Satisfaction: 1.0 inside bend, 0.5 on
their side of the middle (the "certain degree"), 0 on the other side. Where no type gives someone
even the degree, the least-bad type is taken and the card says whose reason is missing at that
stop — it never becomes their stop.

**Chemistry from how the design went:** all tops fully present everywhere → *In Sync*; present
but some only to a degree → *Best of Both*; a #2 stood in, or `ROAM` was split → *Got Your Back*;
a top absent at a stop → *Something for Everyone*; one bringer → *Along for the Ride*; none →
*Open Night*; In Sync with everyone 55+ on `ENRG` and nobody's top being `ENRG` → *Could Go Late*.

**Retired from the group plan:** concession, debt and payback across stops; reach and reserved
stops; v3's compose-then-compromise; friend mode's combination search. Surviving: bend (inside
versus to-a-degree), firmness (who is firm on the opposite pole), latency (what a person's top
is), the joiner's gate, friend mode's relaxed bends (a friend's opposite pole is read through the
stretched ceiling). §13.4c, §13.9.3 and v2/v3 of §14.3 stay as the record.

**Run** (`design.py`, ten rooms, §14.8). The Piano Man room: Aarav and Bela firmly oppose each
other on energy and both have strong #2s, so CROWD and TALK stand in — a jazz bar (her act) and
Depot 48, both fully served at both stops, *Got Your Back*. The same two without strong #2s:
both tops stand, and the stops sit at the middle where each has energy to a degree — *Best of
Both*. Arjun-ENRG, Bea-ROAM, Chetan-GAMES needed an eleventh venue type — a *games pub*, board
games and a table you can talk at — before every stop could hold all three to a degree; it is
added to `FACTORS_V5.md`. The three-single-wants-one-place room is the one honest failure: the
lawn, with A's games absent and said on the card.


## [2026-09-18] The front-end flow under the designed night — the plan card's three notes

`VIEW_FLOW.md` Outing Plan Flow rewritten to §14.3 v4. Gone: the "Eased up on…" note and its ⓘ
sheet, the payback line, the dedicated-stop line. In their place, up to three plain notes per
stop, each read straight off the design: a **stand-in** note when a strong #2 is shaping the
night in place of a firmly opposed top, naming both people; a **to-a-degree** note when a top
factor is present but not inside bend, saying where it *is* fully served; an **absent** note when
no kind of place could carry a top factor with everyone else's — never hidden, never a separate
stop. An easy person reads "Divit's easy tonight." Whole-point preferences the night could not
serve get one line at the bottom of the card. The chemistry chip appears the moment a second
person is in the room, because the design needs no venues. Docx regenerated;
`FRONTEND_SWIPE_GAME_V4.md` carries the change record; the brief carries a banner.


## [2026-09-18] Bend counts at the extremes only — a swipe is "I'd love this", never "I must"

**The user's rule.** A vibe swipe says *I would love this* or *this is not my kind of night* —
not *I must have this* or *I absolutely cannot*. The only time the second pair applies is an
extreme score with a very low bend. So bend is read from score only at the extremes: 30–70 is
maximum bend by construction; 0–20 and 80–100 are **firm** only if bend (score × latency) is
0.0–0.3; everything else is flexible, and "inside bend" for a flexible person means on their side
of the middle. Until latency is validated, firm = extreme; after, a slow extreme swipe becomes
flexible.

**What it changes.** "Firmly opposed" — the one thing that moves a top factor — now needs a firm
person: a 25 opposes nobody, a slow 12 opposes nobody. "To a degree" (0.5) now only happens to
firm people met halfway. `ROAM` is split to one number only between firm demands. Signals weigh
flexible factors at a quarter. The joiner's gate loosens for everything but firm extremes.
Friend-mode stretch is only ever needed between two firm people. Overall firmness becomes the
count of firm factors — how many walls a person has tonight — which is the first clean meaning
it has had.

**Run** (`design2.py`): the same room flips on a slow swipe — Aarav's fast 88 against Bela's fast
12 is *Got Your Back* with both #2s standing in; Aarav's *slow* 88 makes him flexible, Bela's calm
night stands, and his crowd stands in. Bela at 25 instead of 12 opposes nobody and the stops sit
at the middle, *Best of Both*. §14.3.1a.


## [2026-09-18] Correction — firm is an extreme score OR a fast swipe near one, not both together; the numbers made solid

Entry 106 read the rule as "extreme *and* low bend". The user's meaning: the two count
independently. An extreme score (0–20, 80–100) is firm whatever the latency — a slow 12 is still
a 12. A score in the band next to the extremes (21–29, 71–79) is firm only when swiped fast
(latency-firmness ≥ 0.60). The middle (30–70) is never firm. Bend for the firm: 25 points at an
extreme, 28 in the band; for everyone else, anything on their side of the middle. The `ROAM`
middle is now weighted by 1 / bend rather than distance from 50, so a fast 25 against a 92 lands
at 60 (two stops), not 67. §14.3.1a rewritten with the numbers; `design2.py` re-run — the only
run that changed meaning is the slow 88, which is firm again.


## [2026-09-18] The four calls, taken by default; one worked example per state

1. A top factor absent everywhere → no extra stop; said on the card. 2. Friend mode = the
relaxed bend only, between firm people. 3. Overall firmness kept, as the count of firm factors,
no consumer yet. 4. The joiner's match re-runs the design with the joiner added; the gate reads
bend as §14.3.1a. §14.3.5a.

`examples.py` — one imaginary room per state, run: In Sync (three table-and-talk people, one
haveli); Best of Both (a firm 90 against a firm 15 on energy, no strong #2s — two mid-energy
places, both to a degree); Got Your Back (the same, Dev with a strong #2 — his crowd stands in);
Something for Everyone (games, a floor and conversation, all wanting one place — the lawn, Tanvi's
games absent and said); Along for the Ride (one firm person, two easy); Open Night (nobody past
the middle); Could Go Late (games and each other, everyone 55+ on energy, nobody's top); the
`ROAM` split (92 v 12, both firm → 52 → two stops); the band (a 25 at normal speed is flexible, a
25 swiped fast is firm); friends (an 85 v 20 gap inside the stretch — both tops stand, *In Sync*;
not friends — the crowd stands in, *Got Your Back*); solo.


## [2026-09-19] Chemistry V2 — the psychology of each axis feeds the chemistry, and the chemistry feeds the design

**The user's rule.** Blend chemistry is to be based on the psychological findings, and the plan
is to be fed by them. The example: one or two people high on energy with everyone else near
neutral lifts the room — an average of 45 with a peak of 88 becomes 70 — and the room wears a
tag for it. Energy cannot work both ways: a low-energy person can live with a high-energy night;
a high-energy person cannot live with a low one.

**Built** (`CHEMISTRY_V2.md`, run in `design3.py`):

- **`ENRG`, contagion, upward only.** 1–2 highs among neutrals: the room lifts by 0.6 of the gap —
  *Caught the Spark* (the room did not absorb the energy; it caught it). A firm high among firm
  lows: the lows get no weight in the room's energy — the highs set it; the lows' `ENRG`-low tops
  have their strong #2s stand in, or stand and are served to a degree — and on this axis "to a
  degree" reaches up to 70, because they can live with it. "Firmly opposed" reads one way. Same
  three rules on `TALK` and `MOVE`.
- **`AFFIL`, similar not complementary, non-averaging.** A firm high and a firm low together:
  *Table and Floor* — types that hold a table inside an open room get the tie-break. All high:
  *Our Table*, and the room is not offered to strangers. All low, or a public room of strangers:
  *Meet the Room*.
- **`CROWD`, density blocking a goal.** A crowd aversion counts in full when the room is for talk
  or games, at half when it is for energy or a floor. The street carrying crowd for a table —
  *Packed but Ours*.
- **`TALK`, masking is absolute.** A firm talker puts a floor of 40 under every type at every stop
  — the club is out however lively the room. *Buzz, Not Noise* when that caps a lively room.
- **`GAMES`, superordinate goals.** A games-carrying type takes a compromise stop, and the first
  stop of a strangers' room — *Common Ground*. The `games pub` type moves to energy 55 so it can
  sit between two energy camps.
- **`MOVE`, synchrony.** A closing floor stop for a room that started as strangers — *On Our Feet*.
- **`ROAM`, behaviour settings.** A settler and a roamer: one number by bend, and **stop
  durations** — 55 % of the night at the first stop, the rest split — *Settle Then Roam*. Shown on
  the card.
- **Group size.** Five or more: venues with room to split; a pair reads as its own table.
- **The chip:** a tag if one fires, else the formation word. Twelve tags.

**Run** (seven rooms, traces in `CHEMISTRY_V2` §10 / `design3.py`): the user's example lifts to
72 and ends at a live room and a games bar — *Caught the Spark*. Aarav-88 v Bela-12: her low does
not pull, the room reads 88, her talk stands in, and because she is a firm talker the floor keeps
the club out — a games pub and a games bar, *Buzz, Not Noise*. Priya-90 v Rohan-12 on
affiliation: a buzzy restaurant and a pub, *Table and Floor*. Two energy camps with no #2s: the
games pub takes the compromise stop, *Common Ground*, and the tolerant low is served to a degree
at a live room after. Farah-92 v Gaurav-12 on roaming: 3.3 hours at the first stop, 2.7 at the
second, *Settle Then Roam*.

**Flagged:** the talk floor at 40 leaves a firm talker only "to a degree" at a games bar (45);
50 would keep them out of games bars too. The one number here a wrong guess makes a night bad.


## [2026-09-19] Numbers — contagion is how many; every axis reads the strength on each pole first

**The user's correction.** A firm 12 does bring the energy down — depending on how many people
in the room are high. Two or three at 70+ with one firm 12 lift the room; one or two firm 12s
with one 88 bring it down to 50–60. And the same thinking for every axis.

**Built.** Every member counts on a pole with a *strength*: extreme 1.0, the band 0.75 fast /
0.5 normal, neutral 0. On `ENRG`: highs outnumber → they set it and the lows live with it; lows
match or outnumber → the lively middle, `mean(lows) + pull × gap`, pull 0.6 / 0.5 / 0.4 by how
many more lows — 58 for one 88 against one or two 12s, 52 against three. The spark rule now
needs a real high (80+). "Firmly opposed" reads one way only while the dominant pole
outnumbers. On the other axes: `TALK`'s floor holds whatever the numbers (masking does not
average); `MOVE` — movers outnumber → the night ends on a floor; `AFFIL` — both poles → *Table
and Floor*, the lean following the majority (a buzzy restaurant for a table majority, a street
or pub for a room majority); `GAMES` — a gamer or two among non-gamers → a games pub, games on
the premises but not the point; `CROWD` — the majority sets it, a minority hater weighed by the
goal, a minority lover served by the street; `ROAM` — the bend-weighted middle already counts
heads. `CHEMISTRY_V2.md` §0; run in `design3.py` on nine rooms.

**The talk floor, explained for the decision.** `TALK_FLOOR` is the least a venue type may score
on talk, at every stop, when any firm talker is in the room. At **40** it removes the club (10)
and the live room (25); games bars (45) stay, where the talker is only "to a degree" but the
energy people are fully served. At **50** it removes games bars too; the liveliest type left is a
pub or a street (55–60), where an 88-energy person is only "to a degree" — so in a talker's room
the energy people never get a full stop. Forty favours the energy people at the talker's
expense; fifty the reverse. The asymmetry the user stated — a talker cannot live with a loud
room — argues for fifty, with the fill preferring venues that have a quiet corner so the energy
people are not stuck at a degree. Awaiting the call.


## [2026-09-19] The talk floor is 40; every scenario for every vibe factor, run

**Talk floor 40.** The user's reasoning: at 50 the games bar goes too, and then the other people
in the group are stranded in their enjoyment; at a games bar you can still talk to your friends,
unlike a club or a live room. Forty it is. Also: *Something for Everyone* now outranks every
psychology tag on the chip — an absent top is always said.

**Thirty-six rooms** (`examples2.py`), one per scenario per axis — all high, all low, the spark,
highs outnumbering, a tie, lows outnumbering, the drift, for `ENRG`; all high, all low, both
splits, strangers, for `AFFIL`; and so on through the seven. The traces are the record; the
runs that matter: a crowd-hater with two ravers is the one honest failure in the set — the
warehouse at stop 2 has nothing for him and the card says so. The drift rule now needs nobody at
80 (a 70 was counting as high); everyone 55–79 reads *Could Go Late* again.


## [2026-09-21] Exploration — `AFFIL` as give: how far a person bends the rest of their night for the group

**The user's reasoning.** A high `AFFIL` score means the person wants to go with the flow of the
group — their friends matter more than the night — so it should say how far they will bend their
other vibe factors.

**What the exploration found** (`AFFIL_AS_GIVE.md`, prototyped in `give.py`). The psychology
half-supports it: communion goes with accommodation, and affiliative people catch the group's
state more readily. The confound: our `AFFIL` card measures *who you want to face*, not
accommodation — and the low pole says nothing either way. The structural finding: at 80+ `AFFIL`
is nearly always the person's top, and the model already protects only the top, so "high `AFFIL`
= give" is mostly already true by construction. What is not yet encoded is the band (65–79) and
the strong-#2 case, and how such a person *pushes* their other poles on the group.

**The narrow version that survived the runs:** give 0.4 when `AFFIL` is the person's #1 or a
strong #2, 0.2 when 65+ otherwise, 0 below; on their non-`AFFIL` factors only: bend × (1 +
give), contagion strength × (1 − give / 2), yield to a band-strength opposer unless their side
is the majority, spark pull + 0.1 as a neutral. Never their own `AFFIL` top, never the low pole,
never a preference, never summed with friend mode (the larger of the two). Runs: Kabir-88
against a mild opposer goes from 0.5 / 1.0 to both fully served, his people standing in for his
energy; two friends-first 88s against a firm 12 keep their tops (the majority) but push at half
strength and are satisfied by a games pub and a street — everyone fully served. The first
prototype had the two yielding to the one; the majority guard fixed it.

**Recommendation:** adopt the narrow version with one test attached — do friends-first members
rate "to a degree" nights as highly as fully-served ones? If not, the confound wins and the rule
comes out. Thirty rated plans decide it. Awaiting the call.


## [2026-09-22] Room-first, properly — the night is planned from the readings, never from an average; §14.3 v5

**The user's rule.** Plan generation is on the basis of room chemistry — the collective goals of
the room — not on serving each individual. Read the vibe of the room as a whole as accurately as
possible; do not change it so that everyone gets what they want. And, corrected the same day:
"the room as a whole" is not the average of the vibe factors — it is the way the factors
interact according to the psychology.

**What the model was.** Individual-first: nobody absent → the least-happy member → total
satisfaction → variety → *then* the chemistry as tie-breaks. The 09-18 rule that every top is
fully present at every stop, and maximin, put the person above the room.

**What it is now.** Every Chemistry V2 rule produces a *reading* — where contagion puts the
energy, *Table and Floor*, the talk floor, the crowd majority, games available, a floor at the
end, the stop count — and the stop types are chosen to meet the readings, weighted by the axis
weights. Order: the floor (nobody's reason *absent* — present to a degree is enough) → the
readings → variety → individual sums. No maximin; no L1 to a vector (the first prototype tried
closeness to the chemistry vector and produced washed-out lawns and pubs — the averaging failure
of entry 29 again; the user's correction caught it). The "strong #2 stands in" survives only as
the floor's mechanism. The chip is the reading; *Something for Everyone* and *Open Night* outrank
it; *Got Your Back*, *Best of Both*, *Along for the Ride* are retired as individual-bargain words.

**Run** (`readings.py`, eight rooms). The clearest case: two at 85+ with two near-neutral people
— the room reads 72 — now ends at a live-band pub and the food street; v4 sent them to a
warehouse because two people were fully served there and the neutrals were "easy". The two
neutrals count now. Two energy camps read 60 and get Depot 48 and a pub, both to a degree. Three
strangers wanting games, a floor and a crowd have no type that carries games and a floor: the
gamer is absent and the card says so.

**The honest cost, stated.** More people at "to a degree", by design. The room is read
accurately; fewer individuals are fully served. The user's philosophy chooses that and the
psychology of group convergence backs it.


## [2026-09-22] Chemistry V3 — one interplay rule per axis, each from a finding; the spark corrected to 80

**The user's question, and the honest answer.** Asked whether the chemistry rules were backed by
psychology: the *directions* were, the *magnitudes* were mine, and V2's rules were
per-situation rather than one mechanism per axis. V3 fixes both: one rule per axis, each with its
study, its direction, its asymmetry and a magnitude marked as judgement; plus two general
mechanisms that apply to all seven.

**The mechanisms.** Influence aggregates **sublinearly** — Latané's social impact theory, impact
∝ N^0.6, so the first firm person on a pole matters most and the fourth barely registers. And
**firmness is consistency** — Moscovici's minority influence works through consistency, which is
what an extreme or a fast near-extreme swipe *is*. Both were in V2 numerically; now they have
their reasons.

**The shape of every rule:** `room = base + pull × share × (peak − base)`, base the plain mean,
share the leading pole's slice of the room's influence (neutrals counting 0.25 — present but not
advocating), pull the axis's own constant.

| Axis | Finding | Pull | Asymmetry |
|---|---|---|---|
| `ENRG` | Barsade's ripple effect — a high-arousal member lifts the group | 0.75 | upward; lows discounted to 0.55 |
| `TALK` | Thorne 1987 — introverts with extraverts talk like extraverts; turn-taking selects the next speaker | 0.60 | upward; lows 0.50 |
| `MOVE` | the chameleon effect; synchrony — but a threshold: nobody dances alone | 0.70, halved under 1.5 strength | upward; lows 0.50 |
| `GAMES` | Sherif's superordinate goals | 0.50 | upward only; lows 0.30 |
| `CROWD` | Stokols — crowding is an appraisal, not an affect | 0.25 | **none** — a stress response does not yield to enthusiasm |
| `AFFIL` | the circumplex — affiliation is similar, not complementary; no contagion literature exists | **0.00** | split rooms have *no level*: the output is `split` |
| `ROAM` | Steiner's coordination losses — the weakest peg, extrapolated | 0.50 × (2/size) | none |

**The correction the user was right about.** Two 88s with two neutrals now reads **80**, not 72 —
V2 averaged the neutrals in at full weight; they are non-advocates at 0.25. And the user's guessed
`TALK` rule was right and is now evidenced: one firm talker among two low-talk people takes the
room from 43 to **58** (they guessed 30 → 60).

**Cross-axis, all with findings:** `AFFIL` ≥ 70 buffers crowding +8 (Evans & Lepore); `MOVE` ≥ 65
lifts `ENRG` +5 and back (synchrony); a firm split on *any* axis lifts `GAMES` +10 (Sherif); the
talk floor at 40 stays absolute (masking).

**Stated plainly in the document:** nothing here has been measured on a night out. Every study is
on groups, arousal, conversation or density in general — labs, workplaces, a boys' camp. §9 is a
two-column table of what is evidenced and what is mine, so the first real rooms know exactly
which numbers to replace. `interplay.py` runs all fifteen cases.


## [2026-09-22] `GAMES` is venue-defining — indifference is a vote against, and the split bonus is capped at a games pub

**The user's correction.** In Delhi a lone gamer among three people who do not care pulls the
room's `GAMES` *down*, not up: activities are not given the importance the vibe of the night and
the kind of venue are. My §4 had Sherif's superordinate goals doing recruitment work they were
never evidence for — Sherif is about hostile groups given a task, not about one person making a
night a games night.

**The rule.** `GAMES` becomes a **venue-defining** axis: every neutral adds 0.5 to the *low*
pole (not wanting games is a position against a games venue), and a tie between the poles is won
by indifference. The ladder: one gamer among three indifferent 53 → **49**; among two → **54**;
one of a pair → 74; two of four → 73; three of four → 80. The line falls at half the room.
Below it the lone gamer is served as V2 already had it — *games available, not the point*: a
**games pub**, a talkable venue that happens to have games.

**The bridge survives, capped at 65.** A firm split on any axis still adds +10 `GAMES`, but never
above the games-pub level: Sherif buys a venue that has games, not a venue whose point is games.

**Noted for watching:** `MOVE` is the other candidate for venue-defining treatment (a dance floor
is also a kind of place), but dancing reads as part of a Delhi night's vibe in a way board games
do not, so it keeps its upward mimicry rule for now. `CHEMISTRY_V3.md` §4 rewritten, §9's honest
column gains a row marked *domain knowledge, not a study*.


## [2026-09-22] `MOVE` is venue-defining too — and the distinction that the two corrections revealed

**The user: a lone dancer would not move the room either.** Correct, and for the same reason as
`GAMES`: the chameleon effect (Chartrand & Bargh) is about people mimicking each other *inside* a
place. It is not how a place gets chosen. People dance because there is a floor and others are on
it; nobody books a club because one of four fancies dancing. The "first follower" threshold I had
invented was reaching for this and getting it only half right.

**`MOVE` joins `GAMES`:** every neutral adds 0.5 to the low pole, ties go to indifference, the
threshold is retired. A lone dancer among three indifferent people takes the room from 54 to
**48**; among two, 58 to **51**; against one *firm* sitter, 50 to **37**. Two dancers of four
lift it to 74. The line is half the room, as with games.

**What survives of synchrony:** a room that is *already* moving still lifts its own energy (+5
`ENRG` at `MOVE` ≥ 65) and still closes on a floor. What does not: a high-energy room where
nobody asked for a floor now gains at most +5 `MOVE`, **capped at 60** — room to stand, never a
dance floor nobody asked for. Three people at `ENRG` 80–88 with `MOVE` in the forties read `MOVE`
53, not 65.

**The distinction, now §0a of the document and the more valuable output of both corrections.**
Axes divide into **atmosphere** (`ENRG`, `TALK`, `CROWD`) — a quality a place has more or less
of, where a neutral is a bystander and contagion lifts the room — and **venue-defining**
(`GAMES`, `MOVE`) — a *kind* of place, where a neutral is a vote against, ties go to
indifference, and one person's want cannot commit three others to a kind of night. There is no
"slightly a games bar". `AFFIL` (non-averaging) and `ROAM` (structural) are neither.

**The error both corrections fixed was one error:** applying a finding about people influencing
people to a decision about what sort of place to be in. Worth remembering the next time a study
looks like it transfers.


## [2026-09-22] The venue-defining rule, corrected — it is about the firm low, not about indifference

**The user.** One `MOVE` 88 will not move a room holding two `MOVE` 12s or 20s — those two bring
it down. But one `MOVE` 88 with two others at 40–60 *does* move the room, to 70–80. Same for
`GAMES`.

**What was wrong.** Entries 115 and 116 made neutrals count *against* on the venue-defining axes.
That conflated *doesn't mind* with *doesn't want*. A room of people who don't mind is movable on
any axis; what a lone enthusiast cannot beat is a firm refusal.

**The rule now.** On `GAMES` and `MOVE`: neutrals are bystanders at 0.25, exactly as on the
atmosphere axes — but a **firm low (≤ 30) is not discounted**, where `ENRG` cuts a calm person's
pull to 0.55 and `TALK` to 0.50. And a tie goes to the low pole: a night is not committed to a
kind of place on a tie. So the distinction between the two families of axis is **about the low
pole**, not about neutrals — §0a rewritten to say so.

| | `MOVE` | `GAMES` |
|---|---|---|
| one enthusiast + two neutrals | 61 → **75** | 62 → **72** |
| one enthusiast + three neutrals | 60 → **73** | 53 → **66** |
| one enthusiast + two firm lows | 40 → **28** | 41 → **32** |
| one enthusiast + one firm low | 50 → **37** | 52 → **43** |
| two enthusiasts + two firm lows | 51 → **38** | — |

**And one bug the runs exposed:** the Sherif bridge (+10 `GAMES` when the room is split) was
firing on rooms split *about games*, which turned a 32 into a 42 — adding games does not bridge a
games argument. The bridge now ignores a split on `GAMES` itself.


## [2026-09-22] An axis with no position issues no reading — found by isolating each axis in turn

Holding one axis extreme and everything else at 50 (`shape_by_axis.py`) exposed a flaw in §14.3
v5: the `ENRG` reading fired even when the room sat at 50, demanding "end at 50" — a graded demand
at the heaviest weight in the table. It pinned every night to mid-energy venues and crowded out
the axis that actually had a position: a room of three people who only wanted their own table was
sent to a lawn and a buzzy restaurant instead of a restaurant and a quiet bar.

**The rule:** a reading is emitted only where the room's level is 8 or more off the middle, or
somebody is firm on that axis. With it, each axis dictates its own part of the shape cleanly —
`AFFIL`-high gives a table for the night then a quiet bar; `CROWD`-high Depot 48 then a live-band
pub; `TALK`-high a restaurant then a jazz bar; `TALK`-low Piano Man then a gig; `MOVE`-high the
food street then a warehouse; `GAMES`-high two games venues; `ROAM` sets one, two or three stops
and their durations.


## [2026-09-23] `ROAM` splits the difference — a quantity is not an atmosphere

**The user's correction, on a worked example.** In the Ravi / Sana / Kabir night, Sana's firm
`ROAM` 12 set the whole room to one stop and Kabir's 75 counted for nothing, because the old rule
(§14.3.2, `design2.roam_count`) took the firmness-weighted middle **of the firm members only**.
The user: *a person who wants four or five stops should not have to deal with just one, and vice
versa — the room's `ROAM` should be around 45-50 and so two stops.*

**Why the old rule was wrong in kind, not in degree.** Firmness-weighting is right for the
atmosphere axes, where the question is how much of a quality a place has and the firmer voice
genuinely leads. Stops are a **divisible quantity**, and the disappointment is symmetric and
unavoidable: one stop means the roamer never gets the second door, three means the settler is
moved twice. Contagion has nothing to spread. The fair resolution of a divisible good between two
positions is the midpoint — Schelling's focal point (1960), equity theory (Adams 1965).

**The rule now.** (1) Everyone **off the neutral band** (70+ or 30-) has a position, firm or not —
firmness weights the number, it no longer decides who is heard. (2) Positions on **both poles**
clamp the result into **40-60**, which in stops always means **two**. (3) Firmness decides where
in the band, and that sets the **durations**: settler-led (<47) the first stop takes 55% of the
night, roamer-led (>53) 45%, otherwise even. (4) The clock still caps it — a split room under 3.5
hours does one stop, and the card says that is the clock.

**What changed in the worked night.** Sana 12 / Kabir 75 / Ravi 62: **12 → one stop** becomes
**40 → two stops, 3.3 h then 2.7 h** — a games pub, then a bowling alley. Sana gets the long
first sit, Kabir gets his second door. A firm 12 against a firm 92 → 52, two stops. Two firm
settlers against one roamer → 40, still two: the majority sets *where in the band*, not *whether
the roamer moves at all*.

**Applied in both places:** `design2.roam_value` / `roam_count` (what the planner runs) and
`interplay.py`'s `ROAM` axis, which gains a `split_band` so the documented chemistry level agrees
with the plan. `CHEMISTRY_V3.md` §7 and `OUTING_PLAN_ENGINE.md` §14.3.2 rewritten.

**Left open:** the two modules still disagree for a lone roamer among neutrals — Chemistry V3
size-damps (92 in a five reads 63, two stops) and the planner does not (three stops). That is the
same unwired-V3 gap now logged in `REMINDERS.md`, with a concrete case.

## [2026-09-23] Group psychology and collective effervescence — the model has three of Collins' four ingredients, and the missing one is mutual focus

**Research pass, at the user's request: `COLLECTIVE_V1.md`.** Durkheim's *conscience collective*
is the wrong tool — it is about shared moral belief across a society. The right one is
**collective effervescence**, and it has been operationalised: Collins' interaction ritual chains
(2004), Shteynberg on shared attention (2015), Boothby, Clark & Bargh on amplification (2014),
Tarr, Launay, Cohen & Dunbar on synchrony and exertion (2015), Gabriel et al. on measuring
effervescence (2017, 2020), Postmes & Spears on what anonymity actually does (1998).

**The finding that matters.** A working interaction ritual needs four ingredients: bodily
co-presence, a barrier to outsiders, **mutual focus of attention**, and a shared mood. The engine
has three — co-presence is given, `AFFIL` is the boundary, `ENRG` and `TALK` are the shared mood
— and **nothing at all for mutual focus**, which is the ingredient Collins says does the work.
`GAMES` is the closest and it is the opposite kind of thing: participatory and *splitting* (two
at the pool table, three at the bar). `LIVE` is a preference and by construction never alters a
venue type.

**Three rooms the factor set cannot tell apart:** people who want a gig, people who want the
match on, and people who want a loud club all read `ENRG` high / `TALK` low / `CROWD` high. The
first is anchored to a clock, the second needs a room facing a screen, the third needs neither.

**Proposed and NOT adopted: `FOCUS`** — is there one thing we are all pointed at tonight, or are
we the thing? High: a gig, a set, a match, a quiz, a screening. Low: no main event. It is
distinct from `LIVE` (a preference, picks a venue not a type), from `GAMES` (splitting, not
unifying), from `TALK` (attention to each other, not to a third thing) and from `ENRG` (a chamber
gig is `FOCUS` 90 / `ENRG` 30).

**And the test that argues against adopting it yet.** Scoring `FOCUS` on the venue types and
regressing it on the six existing stop axes (`focus_test.py`): **R2 0.91 on today's eleven
types** — as redundant as `TALK` (0.90), more than `MOVE` (0.59) or `GAMES` (0.60). It only
becomes independent information (0.66) once a **twelfth type** exists — a screening room / match
bar, which is *not* loud, *not* a floor and *not* games. So the order is the opposite of the
obvious one: add the venue type and clock-anchored stops first, both justified on their own, then
test `FOCUS` as a card rather than assuming it.

**Four changes that need no new factor, and one of them is the best-evidenced change available:**

1. **A twelfth venue type** — screening room / match bar (65 / 55 / 75 / 50 / 20 / 30). A sports
   bar is one of the commonest ways Delhi goes out and the engine cannot produce one.
2. **Clock-anchored stops** — `starts_at` on a stop. An act or a match has an hour; today a stop
   has only a duration. Also fixes the gap found on 2026-09-22, where `start_time` is in the plan
   request but no screen sets it.
3. **Peak-end instead of a smooth climb** (Kahneman; Redelmeier & Kahneman 1996; meta-analysed
   2022). What is remembered is the most intense moment and the last one, and duration barely
   enters. So score a plan on `(peak + end) / 2` rather than the mean of its stops, and require
   the highest-energy stop to be **last or second-to-last**. The same stops, reordered, are a
   better night.
4. **`MOVE` is a bonding instrument, not only an arousal one.** Synchrony and exertion each raise
   bonding independently, so a `MOVE`-high closing stop should weigh more in a **strangers'**
   room — 12 to 18 — and a lawn or a walk counts, not only a floor.

Plus two smaller ones: a focal stop is **high variance** (shared attention amplifies both
directions — bitter chocolate tasted together is worse), so it should require tier-one venue
confidence; and Dunbar's unimplemented 5+ rule finally has a job — a group of five or more with
no focal point *will* split into two conversations, which is fine at high `AFFIL` and a failure
when the room came to be one unit.

**Rejected candidates:** a collective-effervescence factor (an outcome, not a want — it belongs
in the chips, where *Caught the Spark* already is); planned vs spontaneous (a property of the
plan, and Open Night already carries it); risk / going big (bravado on a card, duty-of-care, no
modelling gain); talking to strangers (that is `TALK` x `AFFIL`); status (that is `POL`, `SCEN`,
`CROWD`).

**What this confirms about what exists:** `AFFIL` is not a preference but a ritual *requirement*
— a room that cannot say who is inside it produces no effervescence — which is a second reason
§6 of `CHEMISTRY_V3.md` is right to split it rather than average it. And `CROWD`'s low pull is
vindicated from an unexpected direction: sixty studies found anonymity does not disinhibit, it
makes people conform *harder* to the local norm.

## [2026-09-23] The room player, Find rooms on a venue, and a pinned venue — three front-end changes with one new engine input

**All three from the user.**

**1. The room player replaces the list as the first screen.** The top five eligible rooms, best
match first, played one at a time: room name, blend style and chip, the plan as the body of the
card, and rewind / play / forward at the bottom with a “3 of 5” counter. *Play* opens the
existing request-to-join box rather than joining silently, which keeps the one irreversible act
behind a confirmation. Skipping all five falls through to the list, with the skipped five at the
bottom under a “Skipped” divider. **Open Nights never enter the player** — they have no plan, so
there is no match to compute and no card to render; they stay in the list with their grey line.
Decided here: a **skip is logged** as a behavioural observation — it is the cleanest signal in the
app about a shape somebody did not want — and, like latency-firmness, it **feeds nothing until
validated**.

**2. “Find rooms” on every venue card**, beside “Go here”: public rooms with that venue in their
plan, in the same player. It is a reverse lookup on `plan_stops`, not a new score. The empty state
matters more than the hit, early on: “No rooms going here tonight”, then rooms going to the
**same venue type in the same area** — never nearest-by-score, which would send someone to a
club because they asked about a jazz bar.

**3. “Go here” now opens a card first** — the venue, its pros and cons for the group in the
two-lines-per-person form, the price rating — with **Lock** (the old behaviour: a one-venue plan)
and **“Build my night around this”** (a full plan with this venue kept as a stop).

**The engine addition, §14.6: a pinned venue.** The shape is computed as usual — a pin buys no
extra stops. If the pin’s type is already in the shape it takes that stop; if not it overrides
the closest stop’s type and the readings **re-solve around it**. Its position in the night falls
out of the existing energy sort, so no new ordering rule is needed. And nothing is violated
silently: if the pin breaks the talk floor or somebody’s firm pole, the plan is still built — the
user asked for this place — but the card names who it costs and they confirm. **This is the one
place an explicit user choice outranks a firm pole**, and only ever in their own room.

**Two degenerate cases handled rather than hidden:** `ROAM` giving one stop makes “Build my night around this” identical to Lock, so the button is disabled with “Your night is one place tonight”;
and a pin that collides with a firm member is surfaced by name on the card.

**Held for a decision, not adopted:** an **age-group parameter on the venue database**. My opinion
is in the chat and the open question is in `REMINDERS.md` — in short: yes, but as a *distribution*
with a confidence, sourced from observed visits rather than guessed at ingest, used only as a
soft weight at the fill stage, and never shown as a rule about who belongs where.
## [2026-09-23] Two venue types — `big loud bar` and `match bar`, both found by looking at what the engine was forced to answer with

**Neither came from listing Delhi venues; both came from running rooms and reading the output.**

**`big loud bar`** (`ENRG` 80, `AFFIL` 35, `CROWD` 85, `TALK` 48, `MOVE` 35, `GAMES` 20) — a
taproom, a standing bar, a brewery at eleven. It closes **two** holes:

1. **There was no loud venue you could still talk in.** Above `ENRG` 65 the only types were club
   (`TALK` 10), live room (25) and games bar (45), so a room that was loud *and* talkative — three
   people at `ENRG` 88 / `TALK` 85 — was sent to a **bowling alley and then an arcade bar**, for a
   room where nobody had mentioned games. It now goes to a **standing bar, then a taproom**.
2. **A firm `AFFIL`-low want was servable by the club alone.** Counting which types can serve a
   firm pole, `AFFIL`-low had exactly one — and the club is `TALK` 10, so a meet-the-room person
   plus any firm talker was an **unservable pair**: the talk floor of 40 excluded the only type
   that faces the room. `AFFIL`-low now has two.

**`match bar`** (65 / 55 / 75 / 50 / 20 / 30) — a screen everyone is facing, talk between overs.
A sports bar is one of the commonest ways the city goes out and the engine could not produce one.
It is also the venue that makes a `FOCUS` axis testable: `COLLECTIVE_V1.md` §5 found `FOCUS` 91%
predictable from the existing axes on eleven types and 66% once a focal venue exists.

**Coverage after** (types that can serve a firm pole): `ENRG` 5/2, `AFFIL` 6/2, `CROWD` 8/1,
`TALK` 4/2, `MOVE` 2/2, `GAMES` 2/9. **`CROWD`-low is now the thinnest at one** — table for the
night — and a near-empty room is a real want. Still open.

## [2026-09-23] `RAMP` — an eighth vibe factor, because `ENRG` was doing two jobs and hard-coding the second

**The user asked whether `ENRG` captures "chill versus hyped".** It does — that is **ideal
affect**, Tsai's LAP (calm, relaxed) and HAP (excited, enthusiastic), with Eysenck's arousability
underneath it for why people differ. But `ENRG` was carrying a second variable with no card of its
own: **the trajectory**. The arc was hard-coded — `lo = min(val, 45 + (val−45)×(k+1)/n)` ramped
*every* night up from 45 — so the engine asserted on everyone's behalf that a night should build.

Four nights people want, of which the old model could express two: **hyped straight there** (arrive
at the club at twelve and stay), **hyped building** (the default it imposed), **chill steady**,
**chill lifting**. And the peak-end rule makes where the peak sits the thing people actually
remember about a night — it should not be a constant.

**`RAMP` is structural, like `ROAM`, so it cost no weight.** `ROAM` says how many stops; `RAMP`
says in what order and where the peak is. Neither selects a venue type, so neither competes in the
type-selection sum; the weight (10, the lowest) is used for naming ties and nothing else. A split
settles in the middle band 40–60, exactly as `ROAM` does and for the same reason — this is a
position on a line, not a quality of a place — and the middle **is** the peak-end compromise: peak
one stop before the end, then hold.

**The arithmetic** (`OUTING_PLAN_ENGINE.md` §14.3.2b): `start = level − (level − 45) × ramp/100`,
`peak_at = n` if `ramp ≥ 60` or `n ≤ 2`, else `n − 1`. Energy 85 over three stops: `RAMP` 88 gives
**62 → 73 → 85**, `RAMP` 50 gives **75 → 85 → 85**, `RAMP` 12 gives **85 → 85 → 85**. Below 40 the
stops also sort **descending** — the room asked to start where it is ending.

**Run:** three people at `ENRG` 82–88. `RAMP` high → bowling alley → warehouse. The same three at
`RAMP` low → **warehouse → standing bar**. Split → standing bar → warehouse.

**Two new tags**, behind every chemistry tag: *Builds to It* and *Straight In*. Two new cards
(`V-RAMP-A/B`), so the deck is eight to sixteen.

**And a wording decision that matters more than it looks.** "Chill" must **not** appear on the
`ENRG` card. In ordinary use it means both low arousal *and* low social pressure — "a chill night
with the boys" — so a card that says it collects answers about the company rather than the room,
contaminating the axis everything else leans on. `ENRG`'s cards stay about the room. The social
sense of "chill" is `ENRG`-low **with** `TALK`-high, which is a profile, and it is handled there.

## [2026-09-23] Profile rules — the top and bottom factors infer a want on an axis nobody spoke on

**The user's question: can the top and bottom vibe factors infer a going-out personality that
shapes the night — low `ENRG` plus high `TALK` being someone mellow who wants their friends?**
Yes, and the engine needed it for a structural reason: the readings are computed one axis at a
time and **summed**, so it cannot say *this combination means something the parts do not*; and
entry 118's rule (an axis with no position issues no reading) leaves a silence that a person's
other answers often fill obviously.

**Three rooms it was getting wrong**, everything unmentioned at 50:

| room | before | after |
|---|---|---|
| `ENRG` 15, `TALK` 88 | **two stops**, haveli → quiet restaurant | **one table, all night** |
| `ENRG` 88, `TALK` 85 | bowling alley → arcade bar | standing bar → taproom |
| `ENRG` 15, `CROWD` 15, `AFFIL` 12 | Piano Man → **warehouse** | rooftop lounge → Old Delhi food walk |

The first is the user's own example and the failure is stark: three people who want a long calm
conversation were being **moved to a second restaurant halfway through**, because nobody stated a
`ROAM` position and the default is two stops.

**Rules, not a type library, and that distinction is the whole decision.** This project has
already built the library version and thrown it away — the 42 vibes died because three of four
real testers sat 121–213 from every vibe in it. The external evidence agrees at scale: Gerlach et
al. (2018) found **four** replicable types across 1.5M people, and a published reply showed only
~**42%** of people could be placed in any of them. A library has holes by construction; a rule
that does not match simply does not fire, and the plan falls back to the axes. This is the
**person-centred** approach used as its own literature recommends — complementary to the
variable-centred one, not a replacement.

**Six rules** (`PROFILES_V1.md` §3.1): *The Long Table*, *Loud and Social*, *Lose Yourself*,
*Settled In*, *Working the Room*, *Quiet Company*.

**Three guards, and they are what make it safe to run:** (1) an inference speaks **only where the
axis is silent** — nobody off the neutral band and no reading of its own — so it can never
contradict or outweigh something a person swiped; (2) it is discounted twice, `0.6 × axis weight ×
the share of the room whose profile fires it`; (3) every firing is **logged** with whether the
plan changed, to be validated rather than believed.

**The share term was not optional.** Built without it, *The Long Table* firing for **one** member
of four took a room of four down to a single stop. On night-level axes an inference now moves the
number by the share: `value = 50 + (target − 50) × share`. One of four gives 43.75 — still two
stops; three of three gives 25 — one.

**It is not shown to the user.** The daily name already occupies that slot and is generated from
the top two poles — the mellow case is already called *Low-Key Table-Talker*. **The name knew; the
plan did not.** A second visible typology would compete with the name, and a visible type makes
people swipe *as their type*, corrupting the measurement everything else rests on.

**What is still wrong, and it is not the rules' fault.** The quiet-but-outward room is better but
not fixed — everyone is served only *to a degree*, because **no venue type is both quiet and
outward-facing**. A vocabulary hole, logged as one.

## [2026-09-23] No warmup, and the tie-break becomes a ranking key

**The user, on two things at once: let the warm-up cards count, and the tie-break may not be
needed at all if latency is how much a person identifies with a card.** Both right, and the
second is the larger change.

**The warmup had a false premise.** `WARMUP = 3` discarded the first three cards as "interface
learning". But **nobody playing the vibe game knows they are answering anything** — they are shown
images and swipe on appeal, after a brief. There is no instrument to learn, so there is nothing
for three cards to be learning. And the cost was concentrated exactly where it hurt: the people
most likely to tie at the top are the **decisive** ones, whose deck is only eight cards, so three
of eight were thrown away. Measured over 30,000 simulated sheets, the tie-break could not fire at
all on **61%** of tied sheets, because one of the tied factors had been in the warmup.

**Replaced by a correction, not a deletion:** `position_baseline[i]`, the running mean of
`log(latency)` at deck position *i* across all users, subtracted exactly as `card_baseline` is. If
the first card really is slower for everyone it is removed; if not, the baseline sits at zero.
Nothing is discarded either way.

**And the tie-break stops being a tie-break.** A tie-break is a patch on a scale too coarse to
rank eight factors: four swipes give seven scores, which give only **four** distinct distances
from the middle (0, 12, 25, 38), so a tie at the top is the normal case — 67% of realistic sheets,
and 10 of 16 real tester sheets. Latency is continuous, so folding it into the key fixes the
coarseness rather than papering over it:

```python
K = 5.0     # < 12/2, so latency can never bridge one step of the score ladder
rank_key(f) = abs(score[f] - 50) + K * latency_firmness[f]
```

**`K = 5` is what keeps "score first, always" true** — the smallest gap on the ladder is 12 and
the largest latency bonus is 5, so a stronger score always wins and latency only ever orders
factors the scale could not separate. Same rule as before, one number instead of a threshold, and
the guessed 0.15 gap is gone.

| | tied sheets left unresolved |
|---|---|
| warmup 3, threshold 0.15 (the old rule) | **72%** |
| warmup 0, threshold 0.15 | 25% |
| warmup 0, **continuous key** | **1.4%**, with the score overruled **0.00%** of the time |

**The same key now ranks every factor, everywhere** — the top factor (§7.1), the second factor in
a name (`VIBE_NAMES_V4.md` §3.2, whose weight-order tie-break is retired with it: a fixed factor
order had already been contradicted by three of four testers asked directly), and the ordered
wants the plan engine reads. **The prototypes now read it too** — `ranked_wants` and
`effective_top` sorted by score alone and let Python's stable sort fall back to axis order, so
`ENRG` silently won every tie in every simulation run to date.

**§7.3's forced choice survives as a rare fallback** — about 1.4% of tied sheets, the case where
there is no latency at all (fewer than five usable cards) — and its options are **reworded to the
eight vibe factors**. The old list offered `FOOD`, `LIVE`, `POL`, `SCEN`, `HERIT`, `NOV`, which
became preferences in V5 and are not what a night is built around.

**One thing this makes load-bearing.** If people swipe on appeal, a better photograph is swiped
faster and its factor reads firmer — the image would be measuring itself. `card_baseline` removes
exactly that, because a card's average speed across all users *is* its prettiness. But it starts
at zero, so the first users are uncorrected: **seed it from an internal run before launch, or hold
the latency term out of the key until each card has ~30 observations.**

**And the brief must keep saying "tonight".** The experience is appeal-driven, which is why the
copy cannot say *attractive* — how a place looks is already a factor (`SCEN`). "Swipe how you feel
about tonight. Gut call — first reaction wins" gets the appeal-driven behaviour without buying the
confound.

## [2026-09-23] Latency is read against the person's own range, not as a rank — and the range becomes theirs as they use the app

**The user: a person's own timing range is the baseline. If they take 7–10 seconds across four
cards that is their normal, and 11 seconds or 3 seconds on another card means something.** Right,
and the rank transform could not express it.

**What ranking threw away.** It is scale-free: it keeps the order and discards the distances.
A session of 7.0, 7.2, 7.5, **10.0** s and a session of 2, 4, 8, **16** s both come out
`1.0, 0.67, 0.33, 0.0`. In the first, three cards were effectively identical and one stood out —
the entire signal — and ranking reports an even staircase. It manufactures spread where there was
none and flattens it where it was real.

**The replacement:** subtract their **own session median** (that is the 7–10 s band), divide by a
**shared scale** (`GLOBAL_SCALE`, the population MAD of centred adjusted latencies — 0.26
log-seconds in simulation), squash to 0–1. Not their own spread as the divisor: that would
standardise away exactly what we want to keep, the size of their deviations.

**The gain is not per-card accuracy, it is a quantity that did not exist.** Over 4,000 simulated
sessions with the truth known, tracking per-card identification goes from +0.180 to +0.187 — a
wash. But the **spread** of a person's firmness values goes from correlating **0.000** with how
decisive they actually were to **+0.098**. Under ranking every person's output spans 0–1 *by
construction*, so "how decisive is this person overall" was not weakly measured, it was
**mathematically unmeasurable** — and §6.3's validation criterion asks for precisely that. The one
job latency was brought in for, separating a firm 4 from a soft 4, was untestable under the old
transform. It is testable now.

**A near-timeout also reads correctly at last.** Eleven seconds from someone whose range is seven
to ten is now maximum softness; under ranking it was merely "slowest of eight", identical to a
card 0.3 s behind the rest.

**§6.2a — the scale becomes personal with use (the user's addition).** A first-time user has no
history and is read against the population. From the second session the app learns the deviation
size normal for them and blends: `(n·mad_personal + 3·GLOBAL_SCALE) / (n + 3)`. One session in
they are three-quarters population; at ten sessions mostly themselves. This matters most for the
steady, even swiper, who reads as flat against population units and whose ordering is squashed
into the middle of the range where noise dominates.

**And the line that keeps it honest:** personal units are right for ordering **that person's own**
factors — all the ranking key (§7.1) ever does — and wrong for comparing **one person to another**,
which is what `overall_firmness` and §6.3 do. So both numbers are stored: `firmness_latency` on
the personal scale, `firmness_latency_g` on `GLOBAL_SCALE`. They differ by a divisor, so nothing
has to be recomputed from raw.

**Card versioning, the trap found while writing this.** `card_baseline` is keyed on the card. If an
image is replaced and the key reused, the old image's slowness is subtracted from the new one and
the correction is wrong in an unknown direction — worse than none. The key is now
`(card_id, version)`, it **resets when the image changes**, and a version with under ~30
observations is treated as having no baseline rather than the old one.

Simulations: `baseline_test.py` (why the card baseline is needed at all: raw +0.25 against
+0.37 corrected) and `baseline_test2.py` (rank against within-person scaling).

## [2026-09-23] §13.6.3 rewritten against v5, and Chemistry V3 wired into the planner

**Two pieces of debt found by the review, both closed.**

### The match was documented against a retired model

§13.6.3's code called `payback()` and `chemistry()`, read `room.state`, iterated ten `FACTORS` and
tabulated *In Sync / Got Your Back / Best of Both / Along for the Ride*. Payback, debt and the
states were retired for the group plan by §14.3.5; the formation words by §14.3.0a. §14.3.5a call 4
recorded the replacement in one sentence and the section was never rewritten — so **a developer
reading the spec in order would have built the retired machine.**

**The rewrite makes explicit what §13.4a already implied: there are two questions, and they need
two numbers.** `fit` — *is this night mine* — reads the plan and the joiner and nothing else; it is
the gate, and it is what **orders the room player**. `disturbance` — *would this person change our
night* — re-reads and re-plans the room with the joiner in it and reports what moved: stops whose
type changed, readings lost or added, whose reason went absent, and how much the joiner agrees with
what the room already wants. Ordering the joiner's own list by `disturbance` would have sorted
rooms by how invisibly they could slot in, which is not the same as the nights they would enjoy.

**And a distinction the old text had no way to make.** After hosting, the plan and chip are frozen
(§13.6.3a), so a joiner *cannot* move the night. `disturbance` is then a **counterfactual** — how
far the night this room would now plan sits from the one it is committed to, which is a proxy for
*this person wanted a different night* — and `fit` is the direct number, which is why it can fail a
candidate on its own. While a room is still open, the plan does re-plan and `disturbance` is
literal.

**The run that shows the two numbers earning their keep** (`match5.py`), against Ravi `ENRG` 88 /
`CROWD` 75, Sana `AFFIL` 88 / `TALK` 88, Kabir `GAMES` 88: a settler who wants one place scores
**fit 0.81** — the night genuinely suits her — and still grades **poor**, because she takes the room
from two stops to one. What she would do to everyone else is the host's question, not hers. A
high-energy crowd person is *great* (nothing changes, reinforcement 1.00); someone who wants a
quiet near-empty room is *poor* (the room loses `CROWD full` and two reasons go absent).

Open Night is unchanged: no readings, nothing to disturb, firm on five or more axes is the perfect
match.

### Chemistry V3 is now what the planner reads

`readings.py` took its levels from `design3.chemistry_vector` — the **V2** rules — while the spec
documented V3. On the worked night they disagreed: `AFFIL` 88 against 63, `GAMES` 76 against 69.
Directions agreed, magnitudes did not, and the document described behaviour the code did not have.

`roomread.py` now supplies the room read: **levels from `interplay.py`** (sublinear influence,
per-axis pulls, the atmosphere / venue-defining distinction, the cross-axis rules, `AFFIL` returning
`split` instead of a number), with the twelve tags and the `ctx` flags computed against those
levels. `design3` stays for `is_firm`, `strength` and the talk floor.

**What changed in the output.** A *Caught the Spark* room now ends at a **club** rather than a games
bar, because V3 reads the room at 80 where V2 read 72 — the number the user expected when the case
was first described. The `AFFIL`-split room keeps its *Table and Floor* chip: porting the tag logic
exposed that V2's spark rule required somebody at 80 or above, which a first draft of the port had
dropped, turning a *Table and Floor* room into a *Caught the Spark* one on a 75.

## [2026-09-25] The SHUFFL screen, the skeleton, and the end of the Create button

**A front-end rewrite from the user, and the engine change underneath it.**

### The screens

**Play opens a SHUFFL screen** instead of popping Host / Join / Create above the task bar: Host and Join at the
top, **an outing plan already generated**, “Give me something else”, “Make a custom outing”, then the heatmaps, which
move off the home page. **Create is retired entirely** — every plan card now carries **Lock this** and **Host
this**, so hosting starts from a plan rather than from an empty room. That inverts the old order and deletes the
“you must create a plan before hosting” message.

**Host asks what you want to host.** A screen headed “What would you like to host?”: a venue search, two buttons —
**Make a custom plan** and **Make a custom plan with friends** — and five venues suggested on vibe match. Alone,
finishing the custom flow generates the plan, makes the room and hosts it in one go. With friends, **the plan stays
blank until every co-host has joined and drawn**, and only then does Host go live.

**Join is the room player.** The Alone / With Friends screen is gone. The joiner **draws a skeleton first**, then
gets the five best-matched rooms back to back with rewind / play / forward. Each card carries the match percentage
at the top, the host's DP, the plan, the pros and cons, the other members' DPs, a background in the room's blend
style, and **the host's music playing** — muted by default with a remembered toggle, because a phone cannot start
audio without a tap and nobody should be handed sound on the metro. Forward through all five and they drop into the
list with the skipped five under a **Skipped** divider. “Join with friends” sits top right and builds the capsule.

**Filters move to Join and shrink to three** — distance, budget, venues. Age range, duration and filter-by-vibe
are retired: the gate and the match already decide which rooms suit somebody, and filtering people out by vibe name
did the same job twice and worse.

### The skeleton (§15)

**The user draws the night: horizontal is stops, vertical is energy, circle size is crowd, and the circle fills with
figures of people as it grows.** A box above each circle shows the venue type being read, so a wrong read is visible
before they commit. It gives the engine three things the deck never could: a **stated stop count**, **energy per
stop in order**, and **crowd per stop** — the last of which has never existed, `CROWD` having always been one number
for the whole night. And being continuous, it is immune to the quantisation that leaves **67% of card sheets tied**
at the top factor.

**It overrides `ENRG` and `CROWD` for the plan, and nothing else.** The cards keep the vibe name, the blend style
and the room's colour — the cards are who you are today, the skeleton is what you want tonight, and a room that
changed colour whenever somebody redrew a line would be the wrong object.

**I was wrong about the chemistry and the user corrected it.** I argued that drawn intentions should be combined by
compromise rather than contagion — that two people who each drew a loud night are not infecting each other. Wrong:
contagion is about the people who will be stood in the room, not about the drawings. The skeleton is a better
*measurement* of a position; it does not change the physics of the evening. Every Chemistry V3 rule holds. Two
things do follow from it being drawn: it runs **per stop**, and **a drawn position is firmer than a swiped one** —
deliberate rather than gut — so it should carry more weight in the strength term.

**`RAMP` is superseded wherever a skeleton is drawn.** It existed because `ENRG` carried level and trajectory
together; the skeleton *is* the trajectory, stated. It survives only for the card-generated plan on the SHUFFL
screen.

**The grid is pre-drawn when the user is reacting to a plan** — faintly, with the line that plan implies — so the
task becomes *correct this* rather than *design your night*, and their first drag is the correction they wanted. It
starts blank when mapping a room. **The gap between the implied line and the drawn line is a direct measurement of
how wrong the card model was for that person**, which is validation data nothing else in the app can produce.

**The joiner draws too**, every time — one join a day, two at most. It buys the thing that matters: the match can
compare **shape against plan**, stop by stop, instead of card-vector against card-vector through a 70% similarity
that passes nearly every room anyway.

**The presets are the shape library made visible** — *The Pregame Clubbing Night*, *The Pub Crawl*, *The Brunch
and Cocktail Day Out* — as a separate path for people who will not draw.

**Still open, deliberately not written:** retiring `GAMES`, moving `ROAM` to a slider, and adding `FOCUS` and
`LEAD` as vibe factors.

## [2026-09-25] Line-Up is the look

**Eight directions were mocked as music-service dialects** — Daily Mix, Sleeve Notes, The Deck, On Air, Side A,
Flyer, Mixtape, and a hybrid. The user picked **Flyer and Daily Mix** and asked for one that had **Daily Mix's
organisation with Flyer's eye-catching-ness**. That hybrid is **Line-Up**, and it is adopted.

**The rule that makes it one thing rather than a compromise: the cover art *is* the poster.** In a music app the
artwork is a quiet container and the type sits outside it; on a flyer the poster is the type. Here every tile
carries its own headline in poster caps, so the shelves stay scannable while each object on them is eye-catching
alone.

**Three rules keep it from going cheap.** Glow is spent only on what is live — the primary action, the room you
are on, the night you are running, and nothing else. Type is split by job: Bebas Neue names things, Instrument Sans
carries anything that has to be read, Plex Mono holds times and labels — which matters here more than in most apps,
because the explaining is the product. And door times sit left in mono, so a plan reads as a tracklist and a line-up
at once.

**The accents are not the brand.** Every vibe and blend style already carries a colour palette, and that is what
fills the artwork; the magenta is the app's, the gradients belong to whoever's night it is. **The whole look needs
no photography**, which is what `VIEW_FLOW.md`'s media rule wanted anyway.

In the repo: `design/THEME_LINEUP.md` and `design/lineup/` — the SHUFFL screen, the room player and the plan card
at 3x, plus a live page. **Not decided:** the skeleton game's visual (the Deck direction's waveform is the obvious
candidate and does not conflict), motion, and whether a light mode should ever exist.

## [2026-09-30] Vibe names V5 and Chemistry V4 - the identity set, named and blended (entry 130)

**The factor split from entry 130's predecessor lands in the two documents that read the factors.** The identity
set is now six: `ENRG` 18, `AFFIL` 16, `TALK` 14, `FOCUS` 14, `MOVE` 12, `SPONT` 10. `CROWD`, `ROAM` and `RAMP`
belong to the skeleton because the user drags them; `GAMES` is a preference. `FOCUS` and `SPONT` are in on the
user's decision; `LEAD`, `STAMINA` and `SHOW` are out.

### Vibe names V5 (`VIBE_NAMES_V5.md`)

**Twelve poles, 132 possible names against V4's 240, and the simulation uses all 132.** New words: `FOCUS`
Headline / Headliner against Front-Row / Front-Rower, `SPONT` Locked-In / Planner against Last-Minute / Wildcard.
Retired: the `CROWD`, `ROAM`, `RAMP` and `GAMES` rows - *Nomad* is the loss that will be felt.

**`SECOND_MIN` drops from 25 to 20, and the measured reason is the weaker of the two.** On 20,000 synthetic
people (`simulations/namesim.py`), six factors at `SECOND_MIN` 25 push the **single-name rate from 41.9% to
56.6%** - more than half of all users would get a one-factor name, and the ten commonest names were all singles.
At 20 the rate is 41.8%, which is V4's 41.9% almost exactly. The better reason: `|s-50| >= 20` means a score of
30 or 70, **which is the firmness-band boundary the rest of the engine already uses**. At 25 the naming threshold
lined up with nothing; at 20 the second slot requires exactly what everything else calls having a position.

The cost is honest and not recoverable by tuning: **entropy falls from 7.18 to 6.49 bits**, about a third less
information in a name. The first slot stays flat (16-18% per factor), so losing four factors did not concentrate
the name on the survivors. **What will actually shrink the vocabulary is correlation between real factors** -
`ENRG` x `MOVE` and `FOCUS` x `TALK` are the pairs to watch.

### Chemistry V4 (`CHEMISTRY_V4.md`)

**V3 asked what this room wants from a venue. V4 asks who this room is**, because the plan comes from the
skeleton. Three outputs: the identity vector (name, blend style, colour), `match` (the *People* sort) and
`disturbance` (point 6). It picks no venue, sets no stop count and vetoes nothing.

**V3's atmosphere / venue-defining distinction is retired - it rested entirely on chemistry choosing places.**
What replaced it is a property of the axis: **an axis splits when both poles can be enacted at the same time in
the same room by two people standing next to each other.** `AFFIL` and `MOVE` split - some hold the table while
others work the room, some are on the floor while others sit. `ENRG`, `TALK`, `FOCUS` and `SPONT` are joint
facts. This is better than V3's rule because it **explains `AFFIL`'s long-standing exception rather than leaving
it a one-off**, and it predicted its own second member.

**`MOVE` leads upward again, and it splits.** The user's 2026-09-22 correction - mimicry is real inside a venue
and is not how a venue gets chosen - was right and is now moot, because V4 chooses no venue. The question it asks
is the one mimicry answers: will this room end up dancing. But a lone dancer does not convert two firm sitters,
so where V3 read 28 and naive contagion would read 58, V4 reads **split** - one on the floor, two at the table,
and a venue that has both.

**`FOCUS`: pull 0.80, the strongest in the table, low pole discounted to 0.45, the strongest asymmetry.** Gaze
cueing is reflexive (Frischen 2007); Shteynberg on shared attention; Boothby on amplified shared experience;
Collins' mutual focus. Above `ENRG` because you have to catch a mood but cannot help following a gaze, and
strongly asymmetric because **nothing un-focuses a room**. It also produces a flag rather than only a level: at
70+ the room **wants a clock**, which is what makes clock-anchored stops urgent rather than nice.

**The old test against `FOCUS` is void.** `COLLECTIVE_V1.md` §5 got R² = 0.91 regressing it on the other axes and
recommended holding it - but that test asked whether the other axes could pick the same *venue*. `FOCUS` no
longer picks venues. The live question is whether people vary independently on it, which only a card and a few
hundred sheets can answer. §5 said exactly that about itself.

**`SPONT` is the only axis in the model whose low pole leads.** A commitment is asymmetric: one person's booking
binds everyone, one person's openness binds nobody. One planner at 12 against two firmly spontaneous people at
85 and 90 still reads 47. Its output is a product rule - the room's **join window**: at 30 or below the room is
closed to late joins, at 70 or above it is open right to the hour. Nothing in the app currently knows which rooms
are still live to a nine-o'clock joiner.

**The talk floor is retired** (the user, 2026-09-30). The physics has not changed; the reason has. The floor
protected someone from a plan the engine **inferred for them**, and there is no inference left - every stop
exists because somebody dragged a line there, and every joiner sees the plan first. `TALK` stays in the identity
vector and the match score, so a loud club still scores low for a talker while browsing.

**Cross-axis: three of V3's five died with their axes, and `FOCUS` restored the coupling as predicted.** `MOVE`
or `FOCUS` >= 70 each add +5 `ENRG`; `ENRG` >= 75 adds +5 `MOVE` capped at 60. **The cap has a better reason
now: a derived value must never win the name.** A factor that got where it is by arithmetic rather than by
anybody swiping should not become who the room is - so every future cross-axis rule is capped inside 30-70. And
the rule that deliberately does not exist: high `ENRG` does not raise `FOCUS`, because a loud club is `ENRG` 90
and `FOCUS` 30.

### Point 6, tested - and I had overstated it

I said the *People* sort and the *least-disturbed* sort were nearly the same thing. On 4,000 synthetic rooms
(`chem4.py`) they are **correlated but not the same sort**: r = -0.59 pooled, -0.61 size-normalised, and **of the
400 best-matched rooms only 158 (40%) are in the 400 least-disturbed** - 174 (44%) after normalising. They come
apart because disturbance depends on the room's *structure*: a room of neutrals is moved by anyone however well
matched, and a room already firm on both poles is saturated however badly matched. **So point 6 is worth its own
line on the join card** - *you would barely change this room* - rather than being folded into the People sort.

**Two measurements that corrected guesses.** `disturbance` **must be size-normalised**: raw means run 0.111 for
a pair down to 0.046 for a five, so an un-normalised least-disturbed sort would simply surface the biggest rooms
in the city - a plausible-looking bug that would be hard to see in the app. And **`AFFIL`-split rooms are the
least volatile, not the most** (0.044 against 0.078): a room already at both extremes cannot be moved. They are
still the likeliest to be a bad night, but that is a different property and conflating the two was the error.

**Two numbers to distrust first:** `FOCUS` pull 0.80, the most aggressive claim in the document, and `SPLIT_COST`
35, picked only so a newly split axis outweighs a large ordinary move.

### Still open

`ROAM`'s split-the-difference clamp is **not dead, it moved** - it belongs to the skeleton merge, which has no
document yet. Clock-anchored stops are now blocking `FOCUS`. Simmel's pair rule is still unimplemented. `SPONT`
is the weakest-carded factor in the set: every other factor is a scene you can photograph and `SPONT` is a
process, so it should be carded, watched against the observation of how early people actually lock a plan, and
dropped if the card does not correlate.

## [2026-09-30] The skeleton merge, factors V6, and the screen reorganisation (entry 131)

### The skeleton merge (`SKELETON_MERGE_V1.md`)

**The hole left by the split is closed.** A room has several drawn skeletons and the plan needs one.
**The hard part was never contagion - it was alignment**, and the answer is that **a stop is a time, not an
index**. Every drawing is resampled onto the shared window's clock before anything is averaged, so a three-stop
night and a two-stop night can be merged at all: at 22:00 one person is in their stop 2 and the other is still in
their stop 1, and those are the two values that meet.

**This forces a precondition worth stating: distance, time and budget belong to the room, not the person.**
Whoever opens the plan sets them; two skeletons drawn over different windows cannot be merged without inventing a
window neither person chose. A co-host who disagrees gets *propose a change*, which reopens the filters and asks
everyone to redraw. It also matches what groups do - **people agree when they are going out before they argue
about what they are doing.**

**The stop count inherits `ROAM`'s split-the-difference clamp**, now on literal stops, which is what it always
wanted to be. 1 and 4 gives 3; 1/1/4 gives 2; 1 and 5 gives 3 because ties round toward the mean rather than
handing the roamer a windfall. **Steiner moved from the pull to the ceiling** - damping the pull by 2/n just made
big groups stick near their mean, which is not a coordination cost; the real cost is that a group of five does not
do five stops, so it caps the count.

**The known flaw is named rather than buried (§2a): three people drew 3 stops, one drew 1, and the room gets 2.**
A three-to-one majority loses a stop to a single dissenter - the largest single-person veto in the engine. It is a
deliberate consequence of the principle (on a count, **fairness overrides influence**, because being overruled
here means physically being dragged somewhere) but it is the rule most likely to be wrong, and that exact case is
the one to watch.

**`RAMP` needs no merge rule at all.** Aligning drawings on the clock produces the arc as a side effect. That is
the cleanest thing in the design.

**The drawn-firmness multiplier that has been blank for a week is filled, and it is not a multiplier.** It is one
row of the ladder: **a swiped 50 means "this card did nothing for me"; a drawn 50 means "I want this stop at
exactly medium".** The skeleton has no true neutrals, so drawn mid-range values count 0.25 where swiped ones count
0. **And the consequence runs the other way from the phrase**: measured over 4,000 rooms, drawn rooms move **6.9**
points from their plain mean against swiped rooms' **11.7**. Per person a drawn position is firmer; a room full of
firmer positions **compromises more**, because the moderates stop being bystanders. One loud voice carries a
swiped room and does not carry a drawn one.

**A shape is not a quantity (§5).** One person builds 35 to 90, another front-loads 88 to 30, and the average is
flat at 60 - a night neither drew. So arcs correlating below -0.50, where both span at least 20 points, are **not
averaged**: the whole shape is taken from the person with more firm drawn points, **both axes from the same
drawing**, because taking energy from one and crowd from the average produces a third shape nobody drew. **And
here the app asks instead of deciding**: two opposed arcs are the signal to offer **two rooms rather than one
plan**, since no arithmetic resolves two people wanting different nights.

**Drawers only, no inference, ever (§6).** In a room of four where two drew, the plan is those two people's shape
and the card says so. Inferring a non-drawer's skeleton from their vibe cards is exactly the inference the
architecture removed. **So if nobody draws there is no plan** - which is what the blurred SHUFFL screen already
specified. The two rules agree and neither was written for the other.

### Factors V6 (`FACTORS_V6.md`)

**Six identity factors**: `ENRG` 18, `AFFIL` 16, `TALK` 14, `FOCUS` 14, `MOVE` 12, `SPONT` 10. **Seven
preferences**: `FOOD` 20, `LIVE` 18, `POL` 18, `SCEN` 16, `NOV` 14, `HERIT` 14, **`GAMES` 12**. **Four quantities
to the skeleton**: `CROWD`, `ROAM`, `RAMP` and venue energy.

**Three kinds of signal, not two** - the identity factors (swiped), the skeleton (drawn) and **observed traits**
(measured): `LEAD`, stamina and `NOV` revisits, which nobody can swipe honestly and nobody has to. The personal
latency scale already proves the pattern works; the other three have no storage and no consumer yet.

**`GAMES` as a preference is a promotion.** V5's own §2 said it behaved nearly one-ended - "I want games" is a
want, "no games" is mostly indifference - which is the definition of a preference. It also took a whole clause of
chemistry with it: Sherif's bridging rule, the `split_cap` of 65 and the games-pub-not-games-bar distinction are
all deleted rather than maintained.

**The identity factors do not choose the venue type - they choose the character within it.** `TALK` is register
(conversational / social / loud), `AFFIL` and `MOVE` together are layout (table-led / open / floor), `FOCUS` is
whether the venue is oriented at something. `ENRG` does nothing at the venue because the skeleton has it, and
`SPONT` sets the room's join window.

**The honest cost (§6):** the vibe assessment now predicts less about the night, which is the point, but it means
**the swipe game has to justify itself on matching alone**. If users do not care who they are matched with, six
cards of identity is six cards too many - a product risk the old architecture hid, because the cards were doing
planning work whether or not anybody valued the matching.

### The screens (`VIEW_FLOW.md`)

**Play no longer goes straight to the filters.** It opens the SHUFFL screen **with its features blurred**, and
tapping any blurred feature is what prompts distance, time, budget and the skeleton. **Two gating layers, both
deliberate**: the swipe game gates the app, the filters and skeleton gate the SHUFFL screen. The blur *is* the
empty state, so the app never shows a bare one - and it is the front-end half of a back-end rule, because with no
drawing there is genuinely no plan to show.

**The SHUFFL screen is now everything about going out.** A **search bar at the very top, above Host and Join**,
searching venues, events and heatmaps. The automatic plan with **"Give me something else"** (same skeleton, new
venues) and **"Reset"** (clear the skeleton, draw again) - which is why **"Make a custom outing" is retired**:
every plan is custom now, so a button for it described a distinction that no longer exists. *What's poppin
tonight*, suggested venues and the heatmaps all move here.

**The home screen is now the social hub**: profile search, stories, the notifications bar, *what your friends are
up to*, and posts. **Messages is now messages** - DMs, group chats, and a search through them. The group-chat flow
is unchanged. A notifications bar buried under a stories rail inside a DM list was the most overloaded surface in
the app.

**Time is a start and an end**, not a duration - the two together are the window, which is what every skeleton is
drawn inside and what caps the stop count.

**Join gains a fifth filter: Place or People.** *Place* sorts by `fit` (does this night suit me), *People* by
`match` (are these my kind of people). Both numbers already existed, so it needs no engine work - and it settles
something the spec had been guessing at, because the player used to be ordered by `fit` purely because one of the
two had to be picked. **Now the user picks.** Under *People* the card also carries the disturbance line - *you
would barely change this room* - which earns its own line because only about 40% of best-matched rooms are also
the least-disturbed.

**Also revised:** the Go-here card's one-stop case reads the merged skeleton instead of `ROAM`, and its talk-floor
case is **now a warning rather than a veto** - the line on the card was always the part worth keeping. Tell the
user what they are choosing, then let them choose it.

## [2026-09-30] Drawn once a night, the capsule gate, and the status bar (entry 132)

Three front-end changes from the user, all of them consequences of the skeleton moving to the front of the flow.

### The skeleton is drawn once a night, and nothing asks twice

**The unlock sequence runs once** - the first time the user taps a blurred feature on the SHUFFL screen - and
every later entry point reads it instead of re-collecting it. **Host -> "Make a custom plan" now asks for
nothing**: the plan generates from the skeleton already drawn, the room is made and it is hosted in one tap.

**The single rule underneath it: a window belongs to a room and a shape belongs to a person.** So anybody joining
something somebody else started draws a skeleton and **is never asked about distance, budget or time at all** -
co-hosts, capsule members and joiners alike. There are now five entry points to the skeleton game and the filters
appear at exactly one of them.

**Flagged for the user:** "Make a custom plan" now does exactly what **"Host this"** on the SHUFFL screen's plan
does - before the change it earned its place by running the custom flow, and the flow has already run. Either
rename it to **"Host tonight's plan"** or drop it. Needs a call on wording, not on behaviour.

### Co-hosts: the room exists first, and the plan waits on skeletons

**"Make a custom plan with friends" creates the room immediately** and sends invites that land in the invitees'
**home-screen notifications bar**. A co-host who accepts is taken **straight into the room and onto the skeleton**,
and **cannot leave it**: closing or backing out shows *"To be a co-host for this room you have to draw your
skeleton for the night."*

**The host watches a counter.** Create Plan is greyed and unclickable with **"1/5"**, **"2/5"** beside it - the
denominator is everyone invited including the host, the numerator is how many have **entered and finished a
skeleton**. Entering without drawing does not count. Create Plan goes live only at 5/5.

**The deadlock has a way out that needs no new control.** A co-host who accepts and never draws would hold the
room forever, and there is deliberately **no timeout on the skeleton**. Instead the host removes them with the
**cross that already sits above every person's icon**, and the denominator drops. Two gates with different
natures: the swipe-game gate has a five-minute timer because a missing vibe means the app cannot read that person
at all, so waiting is pointless; the skeleton gate has none, because a missing skeleton means the plan is
incomplete and a plan is worth waiting for.

**The host keeps the filter button until Create Plan is pressed**, and changing the **time window resets the
counter to 0/5** - everyone drew inside a window that no longer exists. Distance and budget reset nothing.

### The capsule cannot browse until its members have drawn

**Adding people to a capsule now blanks the join screen** with one line: **"Waiting for capsule members"**, plus
the DPs of whoever is outstanding, dropping off as each finishes.

**The reason is structural, not procedural:** rooms are matched against the capsule's **merged** skeleton, and a
merge counts drawers only - so a capsule with two undrawn members would be matched as though those two were not
coming. There is otherwise **no way to know what kind of night the people in the capsule want.**

**And it moves a problem earlier, which is the best thing about it.** Because capsule members draw before they
browse, **a capsule can discover it wants two different nights before it has looked at a single room** - if two
members drew opposed arcs, the "two rooms, not one plan" offer fires on the capsule itself. That is the earliest
and kindest place it could fire.

### The status bar - the bar above the task bar becomes the app's live status line

It used to appear only when a plan locked and only said "[room name]'s outing plan". It now carries **every state
in which the user is waiting on somebody or somebody is waiting on them**, always one line, always tappable, and
**tapping it always opens the thing it is talking about**:

| state | the bar says |
|---|---|
| hosting, room open | **"[Room]: Active"** |
| somebody joins | flashes **"[User] joined [Room]"**, then settles back |
| co-hosts invited | **"[Room]: 2/5 skeletons"** |
| capsule awaiting members | **"[User]'s capsule: awaiting members"** |
| capsule complete | **"[User]'s capsule: ready to browse"** |
| capsule requested a room | **"[Room]: awaiting approval from capsule"** |
| request sent to the host | **"[Room]: awaiting the host"** |
| plan locked | **"[Room]'s outing plan"** |

**The point of the section is that every waiting box in the app can now be minimised into the bar and reopened
from it**, so the user is never trapped in a waiting screen and never loses track of a wait they walked away
from. It matters most for the capsule's room-approval box and the host-approval box, because both take minutes.

**The capsule's room approval is now spelled out.** The creator's screen blurs behind a *"Waiting on approval from
the capsule"* box; **every other member gets the same room view the creator is looking at**, headed *"[Creator] is
viewing this room"*, with swipe right to approve and left to decline. All approvals sent, the request goes to the
host. One decline and the creator sees *"[Name] declined this room"* and browsing resumes where it left off. The
three-minute removal rule applies to the **capsule invite**, not to a room - by then members are committed, and
the creator can cancel and pick another room.

**Precedence is mine and was not specified:** a **locked plan beats everything**, since the night is happening;
below that the most recent state wins and the displaced one stays reachable from its own screen. The alternative
- a stacked or swipeable bar - is more honest and worse to use.

### Also done

A consistency pass on `VIEW_FLOW.md` caught twelve screens still describing the pre-V6 app: the daily deck said
seven factors and listed `CROWD`, `ROAM` and `GAMES`; the tiebreak tiles asked users to break ties between
**preferences** (the kitchen, the act on stage) which predates the 2026-09-17 split entirely; the preference deck
said six cards; the profile showed six badges and six preference rows; the Join flow still said three filters;
and the reveal still pointed at `VIBE_NAMES_V3`. All corrected.

## [2026-09-30] "Host tonight's plan", and thirteen screens in Line-Up (entry 133)

**The rename is made.** "Make a custom plan" becomes **"Host tonight's plan"** and its sibling becomes **"Host
with co-hosts"**, because once the skeleton is drawn at Play the first button does exactly what *Host this* on the
SHUFFL screen's plan does. Named for what it does.

**Thirteen screens rendered at 3x** in the Line-Up theme and pushed to `design/screens/`, with `SCREENS.md`
explaining what each one is showing: home, the SHUFFL screen locked and unlocked, the skeleton game, host, the
host room at 3/5, Place-or-People, the room player, the capsule waiting, the plan card, the active plan, messages
and the profile.

**What the set was built to make legible, because prose was not doing it.** The **status bar in four of its eight
states** across four different screens - it is the newest element in the app and its whole point is that it is the
same bar everywhere. The **two gates one level apart**, both blurring rather than emptying. And the **skeleton's
second axis**, where the figures-of-people fill is what makes crowd readable without a label.

**Three rendering notes for whoever picks this up.** Each screen is rendered in its own page load - a large
document loses the webfont race against paint, which is the bug that cost half a day on the pitch deck. Every
block inside the phone's flex column needs `flex:0 0 auto` or it is silently squeezed (the venue shelf collapsed
to slivers before this was caught). And the host room needed two passes: the member list that makes **3/5** legible
pushed Create Plan off the bottom, so the amber "waiting on two skeletons" card was cut as redundant - the list
already says it.

**Not drawn, and listed in `SCREENS.md`:** the capsule's room-approval pop-up, the "two rooms, not one plan" offer
for opposed arcs, the swipe game, the venue screen, the Go-here card, and all motion.

## [2026-10-01] The capsule approval, both sides, and the two-rooms offer (entry 134)

The three screens `SCREENS.md` listed as specified-but-undrawn, drawn. Sixteen now in `design/screens/`.

**The capsule's room approval is a pair, and that is the finding.** Drawing only the member's pop-up would have
hidden what makes it work: the creator sees a blurred room behind a *"Waiting on approval from the capsule"* box
with the undecided DPs dropping off, and every other member sees **the creator's live view**, headed *"[Creator] is
viewing this room"*, with swipe right to approve. The same moment from two sides, and the second only reads once
you have seen the first. Both carry the minimise-to-status-bar affordance, which is the thing that stops either
person being trapped in the wait.

**The two-rooms offer is the only screen in the app that tells the user the model found a problem it will not
solve for them**, so it has to do three jobs at once: show that the drawings really are opposed (the two arcs
crossing), show what averaging would cost (**the flat line, in dead grey, labelled as the night neither of them
drew**), and name what the one-night option costs - whose shape wins, **why** (the firmer drawing), and what the
loser keeps (their preferences, served at every stop regardless).

**It recommends the split and still offers the other**, because §5a says *ask, do not decide* - a screen that only
offered two rooms would be deciding. The consolation line matters more than it looks: without it, "one night,
Zoya's shape" reads as a pure loss, and it is not.

**Still not drawn:** the swipe game, the venue screen, the Go-here card, settings, the onboarding run, and all
motion.

## [2026-10-01] The venue screen and the Go-here card (entry 135)

Eighteen screens now in `design/screens/`. The swipe game stays undrawn **on the user's instruction** - the card
images and the identity-factor set both need more deliberation first, and drawing it now would fix a look around
a deck that may still change.

**The venue screen found a real conflict between the spec and the theme.** `VIEW_FLOW.md` says the recommendation
line is *"highlighted in green"*. **Line-Up has no green as chrome** - `#24E0FF` and `#FFC247` are artwork-only
by `THEME_LINEUP.md`'s own rule, and there is no green in the palette at all. The screen uses the live magenta,
which is right on the theme's terms (the recommendation *is* the primary thing on the screen, which is what the
magenta is for) - but **the two documents currently disagree and one of them should change.**

**The Go-here card is drawn in its warning state, not its clean one**, because the warning is what changed on
2026-09-30 and it is the part a developer could get wrong. The treatment worth keeping: the unservable line sits
**in amber inside the per-person list**, where Bela's vibe line would be, **and** again as a block underneath -
once in context, once as the question. In the block alone it reads as bolted on; in the list alone it is
missable.

**Both buttons stay live, and that is the entire content of the change.** The talk floor is a warning now rather
than a veto, and a greyed *Build my night* would silently undo it.

**Still undrawn:** the swipe game (held), settings, the onboarding run, the Go-here card's one-stop state (one
line different from screen 18), and all motion.

## [2026-10-01] The screens audited against the flow doc (entry 136)

All eighteen screens checked line by line against `VIEW_FLOW.md` as pushed. **One screen was wrong, the doc was
silent on five things the screens show, and the doc contradicted itself once.** Both sets now agree.

**The screen that was wrong:** the room player had the host's music **playing**. The doc says *muted by default
with a speaker toggle* and the doc is right - a phone cannot start audio without a tap, and somebody opening this
on the metro should not be handed sound. The mock now reads *tap to play*.

**The contradiction, and it is the real find: the duration slider.** Time became a **start and an end** on
2026-09-30, and the window is what every skeleton is drawn inside and what caps the stop count. **A slider that
changes the night's length after people have drawn invalidates every drawing in the room** - it is the one control
in the app that can silently break the merge. It was still specified in two places. Retired in both, with what
replaces it named: the window is set in the unlock sequence and changed by the filter chip, and changing it
reopens the skeleton.

**It survived three documents because nobody re-read it after the window arrived, and drawing the screens is what
found it** - there was nowhere to put it.

**Five things the screens showed that the doc did not say**, all now written in: the venue recommendation's colour
(the spec said *highlighted in green* and the adopted theme has **no green as chrome** at all, so it uses the live
colour, which is what the primary thing on a screen is meant to carry); the host room's **member list** with
per-person DREW / DRAWING / NOT IN YET and a remove cross on each row, **which is what makes the n/5 counter
legible** - the number says how many, the list says who; the capsule approval card's **who else has decided** row,
without which approving feels like voting into a void and the last person has no idea they are last; the
**two-rooms screen** in full, including the note that its consolation line is load-bearing (without it, "one
night, her shape" reads as a pure loss, nobody picks it, and the screen becomes a disguised decision rather than a
question); the blurred SHUFFL screen's **centred prompt**, because blurred shapes with no stated way in are a
puzzle rather than an invitation; and the **filter chip carrying its current values** rather than a bare icon.

## [2026-10-01] The vibe never touches a venue, and who gets into the database (entry 137)

Two corrections from the user, and the second one finally gave `VENUE_DATABASE_V1.md` a spine, so it is written.

### 1. The vibe does not score venues

**The identity factors are for matching people, blending a room's chemistry, and gating the app. That is all.**
**Venues come into play only after the skeleton**, and they are reached by the drawn shape and chosen by the
preferences.

**This retires the last place the vibe was still doing planning work**, and it was doing it invisibly: `FACTORS_V6`
§2a had `TALK` acting as register at rung 1, `AFFIL` and `MOVE` as layout, `FOCUS` as orientation. A user would
have had a venue chosen partly by cards they swiped on appeal, with no way to know. Gone.

**Where that work actually lives now:** register is **derived from the venue's own curve** and used to describe a
venue rather than filter it; layout is a **character tag** like any other, asked for by the room; `FOCUS` keeps
only the clock-anchor flag, which changes *when* a stop happens and scores no venue.

**Six assertions in the specs and three screens were wrong.** The screens are the part worth noting, because they
were showing a number that could not exist: *what's poppin that suits your vibe*, *suggested for your vibe* on
Host, and the venue screen's *"Strongly recommended for Peak Front-Rower tonight · 94"*. All three now rank on
**shape fit plus preferences**, which is available because the skeleton always exists before any of those screens
is reachable.

**And the venue screen got better out of it.** It used to say *"recommended for Peak Front-Rower"*; it now says
**"this is your 11pm"** - which is more specific, more useful, and true. Naming the stop tells the user where the
place would land in a night they have already drawn.

### 2. Admission: premium means established and reputed, not expensive

The user's rule and his example: **Kent's in Defence Colony and Nik Baker's sit at the same price point.** Both
established, both reputed. Kent's is **too locally run to promise anyone a vibe**, and the room is old.

**So reviews and interaction get a venue considered, never admitted.** The API finds candidates; a filter decides:
rating **spread** SD <= 0.85, operator class (chain / group / hotel / professionally-run independent), fit-out
<= 15 years, >= 200 reviews, recency drift, and a 4.0 mean floor.

**The spread is the one that does the work, and it is the finding.** Nik Baker's and a Kent's-like place have the
**same mean rating and the same price band** - any ranking built on stars cannot tell them apart, which is exactly
the failure the user named. The separation is 0.62 against **1.34**: most nights are the night you were told
about, versus a lot of 5s and a lot of 2s.

**A high standard deviation IS "too locally run to ensure anyone any vibe there", measured.** It is not a
judgement about quality, it is reliability, and it comes free from the same API call that returns the mean. For an
app that makes a **promise about a night** rather than a recommendation about a place, it is the single most
load-bearing number available - one bad stop sinks a night, because peak-end means people remember the worst
moment and the last one. Nobody ranks venues this way.

### The casualty, named now rather than discovered later

**Run the filter and Dilli Haat fails it.** So does the old-school dhaba. Publicly or locally run, old rooms, wide
spread. By the user's own rule that is correct - but it means the **`street / market` type may admit zero venues**
at launch, **`HERIT` becomes a preference the engine can almost never serve**, and a slice of `FOOD` goes with it,
because the best cheap food in Delhi is owner-run and old.

Three ways out, none chosen: **accept it** (and `HERIT` probably should not ship until there is somewhere to point
it); **a second admission track for institutions**, where the variance *is* the experience and nobody expects a
market to be consistent; or **admit and flag**, with the plan card saying *"Dilli Haat is a market - it's whatever
it is tonight"*. **Two is the honest answer, three is the cheap one, one is what happens if nobody decides.**

### And it argues FOR seeding one area

Two goals pull opposite ways and both are right: **the preview is only honest if the database is dense; the
promise is only kept if it is choosy.** The resolution is not to compromise on either but to **shrink the area**.
Forty to sixty venues in one radius, fully curved and tagged, is also the first state in which rungs 1 to 4 face
real competition - everything simulated so far ran on fourteen venues with one per `(type, area)` cell, which is
to say **the selection ladder has never actually been tested**.

## [2026-10-01] HERIT is character, not a type - and the casualty section was wrong (entry 138)

**The user corrected yesterday's claim that the admission filter kills `HERIT` and a slice of `FOOD`. It does
not, and the error is worth naming because it is easy to repeat: I had *old-feeling* and *unreliable* as one axis.
They are two, and they are independent.**

His example settles it: **Ikk Punjab has old-style architecture and is established and premium.** A sufi night or
a sitar performance in a safe, established area is heritage too. The admission filter cuts the reliability axis;
`HERIT` lives on the character axis; **the reliable-and-old-feeling box is large, premium, and where a great deal
of the best Indian hospitality sits.** `FOOD` likewise - there is a lot of very good food in premium venues.

### How HERIT is actually served - three routes, all premium-compatible

| | | standing |
|---|---|---|
| **fabric** | the building genuinely is old - a haveli, a colonial bungalow, a listed structure | **85** |
| **styled** | a new or renovated room built to feel old. **Ikk Punjab is this** | **65** |
| **programme** | a sufi evening, sitar and tabla, qawwali, a ghazal night | **+25 at that hour** |

**So `HERIT` is hour-scoped, exactly as the energy curve is.** Qila reads 85 all week and **100 on a Thursday at
21:30** because the sufi evening is on; Piano Man reads 15 most of the week and 40 when the sitar set is. Same
rooms, different nights - which is the whole point of letting programming carry it.

**And it is far cheaper to populate than the energy curve**, which needs a judgement per venue *per hour* and has
no source at all. Heritage needs **one lookup** (INTACH and ASI listings, heritage precincts, and the venue's own
copy, which almost always states a period when there is one), **one glance** (nobody can automate *does this room
feel old*; anybody can decide it from four photos in five seconds - under an hour for 40-60 seed venues), and
**one feed** (venue socials, Insider, BookMyShow, District - the only part needing refresh, and the only one
genuinely automatable, because event listings are structured data by nature).

### Two consequences

**`street / market` is retired as a venue type.** The user: *"we're sticking to venues."* It was never in scope,
and it was the only thing the admission filter actually excluded - so removing it takes the whole casualty
section with it. Old Delhi food streets, night markets and melas are out; the heritage they carried is served by
heritage-character **venues** instead.

**Programme-led `HERIT` needs clock-anchored stops** - the ghazal set is at 21:00, not "in the evening". That is
the same unbuilt feature `FOCUS` has been blocked on since 2026-09-30. **One feature, two factors**, which makes
it the most load-bearing item on the open list.

## [2026-10-01] Selection V2 - the skeleton is exclusive, and the curve becomes bands (entry 139)

**The user: "venue selection should happen exclusively on the basis of the skeleton - energy and crowd at that
moment - and then move onto the preference factors depending on whether there is a clash in the room. The
preference factors are fixed per venue; ENRG and CROWD are tagged in bands: Depot 48, 8pm-12am, ENRG 88,
CROWD 88."** Four rungs become three and the character rung is gone.

### Stage 1 does the work; stage 2 only breaks a tie

Stage 1 ranks every venue whose band covers the hour by `|dE| + 0.6|dC|` against the drawn point. **No
preference, no tag, no vibe.** If one venue is clearly closest it is the pick and nothing else runs.

**And the simulation found the hole in that immediately: without a gate, preferences can overrule the shape.** At
a stop drawn for 23:00 e86 c88, a venue **25 points off** the drawn shape won on a single preference. That is the
engine ignoring the only thing the user actually stated. So **`SHAPE_GATE = 12`: only venues within 12 of the best
distance may compete at all.** Beyond it a user could tell the difference. **That one constant is what makes stage
1 *exclusive* rather than merely *first*.**

### The clash rule, and why most clashes are not clashes

Inside the gate: take the preferences live in the room (anyone at 70+), **subtract what earlier stops already
served**, and if one candidate serves the rest, there is no clash. If none does, it resolves by **who cares,
summed** - two people at 80 beat one at 95.

**The carry is the part that matters.** A room of three with four live preferences, where **no single venue serves
more than two**, still gets all four across two stops: Piano Man takes `LIVE` and `SCEN` at 20:00, Social takes
`FOOD` and `GAMES` at 23:00. Neither stop could have done it alone and at neither stop did the engine have to pick
a loser. **Only what survives to the end gets the unserved line**, at the bottom of the card rather than under a
stop, because by then it is a fact about the night.

### Bands, and this is the cheap part

**The curve stops being a point per hour and becomes two to four blocks.** `Depot 48 - 19:00-22:00 e55 c40 ·
22:00-02:00 e88 c88`.

**This cuts the only field with no source by about two-thirds.** It was nine judgements per venue, a few thousand
across a city. It is now 2-4 per venue - for a 50-venue seed radius, **roughly 150 judgements: an afternoon's
work, once.** It does not solve where energy comes from at scale, but **it takes the seed out of the "needs
hiring" category entirely**, which was the thing blocking everything else. It is also closer to how anybody
describes a venue: *"it's quiet till ten and then it goes."* The supply grid expands each band across its hours,
so nothing downstream changes.

### Two consequences

**Preferences are fixed per venue, so HERIT programming cannot sit on the venue row.** Events move to their own
table - `(venue, date, from_hour, to_hour, kind)` - read at stage 2 beside the fixed preferences. **The venue is
static; the calendar moves.** Cleaner than carrying a function on the row, and it is the same table the `FOCUS`
clock-anchor will read.

**Tags no longer filter anything.** They are how a preference *finds* a venue (`HERIT` looks for
`heritage-building`) and what the card *prints*. That retires the dangling rung-1 input from entry 138 properly,
rather than re-sourcing it: the right answer was that the rung should not exist.

## [2026-10-02] Tagging venues from images - the method, and its three limits (entry 140)

**The user's method: hold a reference set of images per factor, embed a venue's own photos, score by similarity.**
It is the right idea and it fills most of the table. Three things break on contact.

### Three of the named factors have no consumer

`MOVE`, `TALK` and `AFFIL` are identity factors and have not touched a venue since 2026-10-01, so tagging venues
for them is work nothing reads. **And `SCEN` was not on the list although it is the single most image-assessable
field there is** - `SCEN` *is* the look of the place. The work shrinks by three and grows by one, and the one it
grows by is the easiest.

### Selection bias: use the share, not the mean

**People post a venue at its best**, so every mean similarity drifts up and venues compress toward each other.
Simulated on five venues with known truth, the **mean** could see **56 points** of spread and the **share of
photos clearing the high-pole threshold** could see **94**. Score by the fraction of a venue's photos that match,
not the average - the bias is roughly constant across venues, so a share stays comparable where a mean does not.

### The real risk, and it is invisible if you get it wrong

**If every `ENRG`-high reference is a dark club and every `ENRG`-low is a daylight cafe, the embedding learns
BRIGHTNESS, not energy.** On the test set the confounded version **rates a brightly-lit club calmer than a
candlelit restaurant** - rank error 8 against 0.

**The rule: a reference set must vary on everything except the factor.** `ENRG`-high needs a dark club AND a
bright afternoon party AND a lit-up wedding floor; 10-20 per pole, deliberately mixed on time of day, colour,
indoor/outdoor and crowd. **Nothing downstream catches this if it is wrong, because the number looks fine.** The
reference set is the one artefact here that has to be built carefully by a person.

### What images cannot give at all

**Bands are hour-scoped; an image score is a property of a venue.** Photo timestamps are when somebody POSTED, not
when they were there. **Images give the amplitude and cannot give the shape.**

**Popular Times is the exact complement** - an honest hourly crowd curve that says nothing about how hot the room
feels. **Combine them: shape from Popular Times, ceiling from images.** Depot 48 at a photo-derived peak of 88
becomes `19:00-21:00 e54 / 21:00-23:00 e72 / 23:00-25:00 e87`. A seed, not an answer - but **correcting 2-4
numbers is a different job from inventing them**, which is what takes the seed radius from needing hiring to an
afternoon.

### The access hinge - and the answer is not Instagram

The user named the dependency correctly. **Instagram hashtag search is not a viable base**: the Graph API returns
a business's own media only once they connect their account, hashtag search is capped at a handful of tags per
week with no engagement data, and scraping is against terms and actively blocked.

**Google Places photos is viable today** - user-submitted photos per venue, under licence, no hashtag needed - and
it arrives in **the same call** as the rating, the review count, the review text and Popular Times. That is
**admission, the CROWD band, the ENRG seed and the FOOD signal from one integration.** The design assumes Places;
Instagram becomes enrichment for venues that connect their own account later.

**And `CROWD` should not come from images even though it could** - Popular Times gives the number directly and
hourly, so inferring it from a biased photo sample with unreliable timestamps would be estimating what we can
simply read.

## [2026-10-02] The band problem, measured - the shape comes from the type (entry 141)

Five ways to get an hourly shape when images cannot give one, scored over 20 venues and 3,000 drawn stops
against known truth. **The metric is not error in the number - it is whether the pick still lands inside
`SHAPE_GATE`**, because inside the gate the user got a venue that fits what they drew.

| method | mean error | inside the gate |
|---|---|---|
| flat, no shape | 14.5 | 70% |
| crowd as the shape | 9.6 | 78% |
| **the TYPE's canonical shape x image amplitude** | **8.2** | **83%** |
| the type shape shifted to the crowd peak | 10.1 | 75% |
| two bands only | 12.4 | 70% |

**The shape comes from the TYPE, not the crowd**, and the first reason is the real one: **crowd and energy peak at
different hours, and the gap is type-dependent.** A restaurant is fullest and loudest together; a big loud bar is
fullest at midnight and loudest an hour later; a club is both, late. Crowd-as-shape bakes that lag in as a
*different* error per type, so no constant corrects it. The type is also already known - it is stage 1 - and
**twelve curves authored once replace a judgement per venue per hour forever, including for every venue added
later**, which is what decides whether this scales past one neighbourhood.

### Two things the test killed, one of them mine

**Shifting the curve to the venue's crowd peak makes it worse** - 75% against 83%. The crowd peak is a noisy
estimator of the energy peak and shifting on it adds error. That was my own proposal and it is wrong.

**Two bands is no better than having no shape at all** - 70% against 70%. If a venue gets two blocks the shape has
already been thrown away.

### So it is four bands, not two to four

| bands | 2 | 3 | **4** | 5 | 9 (full curve) |
|---|---|---|---|---|---|
| inside the gate | 73% | 77% | **84%** | 79% | 83% |

**Four is indistinguishable from the full hourly curve and there is no gain beyond it.** The spec said two to
four; it is four.

### The correction ladder

**a** opening hours pin the curve to the clock, free with the Places call - a place that shuts at 23:00 cannot
peak at 01:00. **b** hand-correct the four numbers for the seed radius, once, an afternoon. **c** learn from
users: End Plan already rates each stop, so one extra tap - *"louder or quieter than you expected?"* - corrects a
band per locked plan. That is the only route that ends up right and the only one that needs users, so it is last.

### And §5.7 now does each field

Method, cost and **failure mode** for all eight. The summary: **three fields need a human and the rest do not** -
the reference sets (once, carefully), the styled-versus-fabric call on heritage (five seconds a venue), and the
four energy numbers for the seed radius. Everything else comes out of one Places call and a text pass.

## [2026-10-02] What the APIs actually return - three assumptions broken (entry 142)

Checked against the Google Places API docs rather than asserted from memory. **Three load-bearing assumptions in
`VENUE_DATABASE_V1.md` were wrong.**

**There is no popular-times field in the Places API.** There never has been - it is visible in the Maps UI and is
not exposed. The document had been assuming it came free with the Places call.

**No rating histogram, and a maximum of 5 reviews.** Places returns `rating` and `userRatingCount` and nothing
about the distribution. **So the admission filter's best test - rating spread SD <= 0.85, the thing that separates
Nik Baker's from a Kent's-like place - cannot be computed from free data at all.**

**A maximum of 10 photos per place**, against the ~40 the top-decile-share method assumed.

### What replaces each

**Popular Times: mostly moot.** Entry 141 already measured that the type's canonical shape beats crowd-as-shape
for the `ENRG` band, so energy never needed it. The `CROWD` band did - and the fix is symmetric: **author a crowd
curve per type too**, scaled by a per-venue busyness amplitude from **`userRatingCount` / months open**
(`openingDate` is a field). Both bands become *type shape x venue amplitude*, and neither needs a field Google
does not publish.

**The spread: no free replacement, and this one hurts.** Admission keeps rating, count, operator class, fit-out
age, and a weak drift check from the 5 reviews against the lifetime mean. **§1.2's argument still stands - spread
is the right thing to measure - but nothing free provides it.** This is now the first candidate for paid data.

**Ten photos: the share-versus-mean conclusion FLIPS.** §5.2 said to score by the share of photos clearing the
high-pole threshold rather than the mean. Measured at the cap over 400 trials: the **share orders venues right 92%
of the time at 40 photos and 83% at 10**, while the **plain mean goes 99% to 88%**. A decile of ten photos is one
photo, so the share quantises and loses resolution. **Share at 30+ photos, mean at the cap** - and the selection
bias has to be corrected with a per-TYPE constant rather than measured per venue.

### The offsetting surprise

**The Enterprise + Atmosphere field set is far richer than assumed and replaces work assigned to image inference.**
`liveMusic` is a **boolean** - `LIVE` does not need inferring at all. `goodForWatchingSports` decides the `match
bar` type. `outdoorSeating` is a setting tag for free. `regularOpeningHours` is the clock-pin from entry 141.
`servesCocktails` / `servesDinner` / `servesBrunch` and the rest are direct `FOOD` and type signals. Plus
`editorialSummary`, `generativeSummary`, `neighborhoodSummary` and `reviewSummary` as text to tag from.

**Net: the structured fields got better and the statistical fields got worse.** Tagging is easier than the
document assumed; admission is harder.

## [2026-10-02] The licence finding - Places is a display API, not a data source (entry 143)

**Read the Google Maps Platform Terms rather than assuming. The venue database as designed cannot be populated
from Google, and this supersedes three days of "assume Places".**

**3.2.3(a) No Scraping** forbids pre-fetching, indexing or storing Google Maps Content outside the Services, and
names **copying and saving business names, addresses or user reviews** explicitly. **3.2.3(c) No Creating Content**
forbids deriving from it - its own example (v) is *constructing an index of tree locations from Street View*,
which is structurally identical to constructing an index of venue energy bands from Places photos - and (vii)
forbids using the content to train, test, validate or fine-tune models. **3.2.3(d)(iii)** forbids use **in a
listings or directory service**, which a stored tagged searchable venue set squarely is.

**And the Service Specific Terms say what may be cached: `place_id`. That is the entire list.** Not the name, the
rating, the attributes or the photos.

**This is not a grey area and should not be treated as one.** In hindsight it is not surprising either - Places is
priced and shaped for live display inside an app, which is exactly what the licence permits.

### What Google is still good for

**`place_id` as the join key**, cached indefinitely and legitimately, with every other source hanging off it.
**Live display on the venue screen** - photos, hours, rating, fetched at view time with attribution, which is
exactly what `VIEW_FLOW.md`'s existing media rule already permitted and nothing more. And **deciding where to send
a human during the seed pass** - looking at Google to decide where to go is not storing Google's content.

### What populates the database instead

**Manual curation of the seed radius** (ours - a person deciding things is not Google's content), **the venue
partner agreement** (licensed; a draft already exists in the project folder, and it should now also ask for photos,
video and the event calendar), **our own users** (in-app media, End Plan ratings, band corrections - and this
compounds), **OpenStreetMap** for the base layer under ODbL, which explicitly permits storage and derivation, and
**a licensed places provider** if and when the seed needs to scale.

**The seed radius was already the plan; this makes it the only plan.** Fifty venues curated by hand is no longer a
compromise forced by cost - it is the only licensed version of this. It was already costed at an afternoon.

### What it kills

**Image-similarity tagging cannot run on Places photos.** The method survives - reference sets, the confound rule,
mean-versus-share - but it has to run on venue-supplied, user-supplied or licensed images. At seed scale that is
the venue's own media, which the partner agreement already asks for.

**The supply grid cannot be built from Google**, since it is precomputed and shipped to the phone, which is
storage and redistribution of derived content.

**And there is no video anywhere in the Places API** - photos only, maximum 10, and even those may not be stored.
Video can only come from the venue (partner agreement) or our own users.

## [2026-10-02] Bohca - the first real venue, and what reviews can and cannot build (entry 144)

Tested whether reviews alone can populate a venue row, on a real place the user named: **Bohca, Qutub**. Built
from public reviews, listings and the venue's own posts - no visit, no images, nothing stored from any API.
`VENUE_TEST_BOHCA.md` has the full row.

### The finding that validates a design decision

**`FACTORS_V5.md` cites Bohca as the example of a `games pub`. Every nightlife source calls it a club. Both are
right**, and Bohca's own Facebook explains why: *"Weekend = Brunch at Bohca... lovely board games to keep you
engrossed... the Hoppi Sunday Brunch."*

**A board-games brunch place at 2pm on Sunday and a packed loud bar at midnight - the same room.** That is the
single best validation the **hour-scoped `types[]`** decision has had, and it came from a venue the user picked
for unrelated reasons.

### What reviews are good at

**Character, richly**: upscale but current rather than classy; ~Rs 2,000 a head; reservations three days ahead for
a weekend; a guestlist, bouncers and a door that turns people away; Bollywood and Punjabi; a terrace; open since
2017; a dance floor. **Types, including the hour split. Preferences. And most tags** - though most of those came
from stated service options (`outdoor seating`, `reservations required`, `all you can eat`) rather than prose.

### What they cannot do, and it is the part that matters

**The bands.** Not one of the eight energy and crowd numbers is stated anywhere - they are inferred from "massive
crowd", "party till late" and a closing time. **Reviews establish the amplitude and the direction and never the
hour** - the same gap §5.4 found for images, arriving by a different route. The type curve plus one amplitude does
the real work; reviews only confirm the amplitude is high.

### And one genuinely useful idea came out of it

Google says **4.1 across 953**; TripAdvisor says **2.9 across 9**. The spread cannot be computed from 5 returned
reviews (§5.0) - **but the text carries it anyway.** *"One of the finest places for a late night party"* sits in
the same corpus as *"puking teenagers, smoky indoors, over smart bouncers"* and *"variability in service
quality"*. **That is a bimodal distribution described in words.**

**So sentiment variance across the five returned review texts may substitute for the rating SD** that admission
lost in entry 142. Same latent quantity, read from prose instead of stars, and five texts is enough to see a split
this wide. **It would not have been obvious without running a real venue through it.**

### And one problem it exposed

**`prefs{}` are fixed, and Bohca's `GAMES` is not.** Board games are a Sunday-brunch thing, so a fixed `GAMES` 45
is too high at midnight and far too low at Sunday lunch. The fix needs no new mechanism: **let the hour-scoped
`games pub` type carry it**, and put the recurring Sunday entry in **the events table** already built for heritage
programming and the `FOCUS` clock anchor.

## [2026-10-02] Negative reviews are routed, not filtered - and the crowd's vibe (entry 145)

**The user, on the Bohca test: a complaint about the door is not a criticism of the venue.** *"The drinks tasted
bad"* and *"service was slow"* are real criticism; *"they outcast you based on your drive"* is a grievance about a
policy.

**But the right move is to ROUTE them, not filter them.** A complaint about a strict door is **evidence that the
door is strict**, which is true and useful. **Most negative reviews of a nightlife venue are accurate descriptions
written by somebody who disliked what they accurately described** - and for an app matching people to rooms, that
is the most valuable text in the corpus.

*"Too loud"* raises the `ENRG` band. *"Packed, couldn't move"* raises `CROWD`. *"Over smart bouncers"* becomes
`guestlist` and lifts `POL`. *"Full of teenagers"* is crowd-age character. *"Too much Bollywood"* is a programming
tag. **Only badly-made drinks, slow service and things like smoky air belong in the quality signal.** The rest are
tags and bands wearing a one-star rating.

### And it fixes the sign on entry 144's idea

Entry 144 proposed sentiment variance as a substitute for the rating spread admission lost in entry 142. **That
only works AFTER routing.** Variance in *execution* complaints is the consistency signal. Variance in *door*
complaints is just evidence of a door - and counting it as inconsistency would **penalise exactly the selective,
well-run venues the filter is built to find.** Without the routing step the substitute would have had its sign
backwards on the venues that matter most.

### The crowd's vibe, which is not the venue's

A venue has no vibe factors and that does not change. **But the people in it do**, and that is screen 17's *"who
goes here"* donut - normally computed from users who went. Estimated from reviews as a **cold start**, Bohca after
22:00 reads `ENRG` 85, `MOVE` 80, `AFFIL` 68, `SPONT` 22, `TALK` 25, `FOCUS` 25.

**Which names it Peak Floor-Filler** - a sentence about the people, and it reads true from both directions: the
reviews that loved it and the ones that did not describe the same room.

**Two caveats.** It is **one hour of one kind of night** - the Sunday brunch crowd is close to the opposite, so
*who goes here* is **hour-scoped like everything else** and should be read at the hour the stop falls. And it is a
**cold start, not a measurement**: the honest version comes from users who locked a plan containing the venue, and
the estimate should be **visibly replaced rather than blended** once there are twenty real readings.

## [2026-10-02] Day-scoped types, AFFIL as a type function, and the door (entry 146)

### Bohca is a club on weekends and a pub on weekdays

**The user: "Bohca is a club after 10PM on weekends and a pub after 10PM on weekdays."** The same clock, a
different venue - hour-scoping alone cannot say it. **`types[]` and `bands[]` both gain a day dimension**, so a
venue carries **eight numbers instead of four** (four weekday, four weekend) with a specific day overriding only
where something genuinely differs, as Sunday brunch does at Bohca. The supply grid gains `day_mode` and doubles,
which is nothing. **Default to two modes, allow seven, use the override sparingly** - every override is a number
somebody has to keep true.

### AFFIL for a club is a function, not a field

**The user: "for nightclubs the AFFIL rating should be the same since almost every single nightclub in Delhi
operates the same, and it should go up or down depending on the CROWD rating."**

**This is the same move as the type energy curve, applied to a different quantity**, and right for the same
reason: **where venues of a type do not meaningfully differ, a per-venue field is a per-venue opportunity to be
wrong.** Proposed `AFFIL_club(hour) = 45 + 0.35 x (CROWD_band(hour) - 50)`.

**The direction needs the user's call.** I have it RISING with crowd - Delhi club culture is table-booked and
group-arriving, so the fuller it gets the harder people hold their table, while an emptier room lets people move
and mix. **The opposite reading is defensible** and would invert the slope. It feeds the *who goes here* crowd
estimate and nothing in selection, since `AFFIL` is an identity factor.

**Watch for the pattern elsewhere** - `TALK` in clubs is probably the next one, pinned to energy rather than
crowd.

### Quora: low value, one high-value finding

**The corpus is 7-13 years old** and several venues in the top answers have closed. **And the format is wrong**:
Quora answers *where should I go* with a list of names; tagging needs *what was it like* with a description.
**Reviews describe, Quora recommends** - a clean statement of which sources justify an integration.

**But the dominant recurring topic across a decade is the DOOR** - stag entry, couple entry, free for girls,
guestlist. More than music, price or food. A question that persistent is structural.

**So: the door is a hard gate and the engine does not model it.** A group of four men can be refused where a mixed
four walks in, and **a plan routed to a venue the room cannot enter is the worst failure the app has** - worse
than a bad match, because the night stops. It reads at stage 1 as a filter alongside the radius, and it is
readable from exactly the reviews entry 145 taught us to route.

**Worth noting how it arrived:** Quora was useless for the question asked of it, and **the uselessness was the
signal** - when a decade of people keep asking the same question, that question is a field you are missing.

## [2026-10-02] The lexicon method, and the method underneath it (entry 147)

### The method, stated once: the type is the prior, the venue is the deviation

**This arrived three times from three directions in two days, so it is the method rather than three patches.** The
type supplies the hourly energy shape and the venue supplies one amplitude; the type supplies `AFFIL` entirely and
the venue supplies nothing; the type supplies the prior for every lexicon factor and the text moves it. **Where
venues of a type do not meaningfully differ, a per-venue field is a per-venue opportunity to be wrong.**

### AFFIL, corrected twice over

My draft had club `AFFIL` rising with the crowd band, reasoning that a fuller room makes people hold their table.
**Wrong about Delhi.** The user: *"people on tables are not high AFFIL by themselves, people mostly use tables to
order bottles of alcohol then dance among the crowd."* **A table in a Delhi club is a logistics base, not a social
enclosure.**

So `AFFIL` is a **type constant**, identical across clubs - and the deeper point: *"someone who wants to be among
their group will be among their group in a club, or will not if they don't want to."* **It is a fact about what a
person does in a room, not about the room.** The clearest case yet for why identity factors do not touch venues.

### The door, walked back

I made the door a hard stage-1 gate off the Quora finding. **The user corrected the inference, and the correction
is about what the app is for:** *"there are only about 8-10 nightclubs people actually go to on a weekend, getting
entry there is their job, and most people know what it's like. The main utility is finding people to go with, or
joining a group that is going, rather than getting recommended the right club where they can enter."*

So the door stays a **tag**, printed for information, filtering nothing. **And the strategic point nothing else in
these documents says: the app's value is hour-dependent.** Early, there are hundreds of venues and selection does
real work. Late, there are **eight to ten clubs everybody already knows** and selection does almost nothing -
**the job is the room, not the room's plan.** That also reframes the thin club supply flagged earlier: it is not a
gap to fill, it is the nature of that end, and solving it with more venues would be solving the wrong problem.

### The lexicon method

**Built and run on Bohca's real corpus.** The principle is entry 145's: **polarity is irrelevant** - *"too loud"*
and *"amazing energy"* are the same evidence, so a one-star review about noise is worth as much as a five-star one
about atmosphere.

**Three fixes took it from unusable to usable, and the first run is why they exist:**

| failure | fix |
|---|---|
| *"traditional tapas"* fired `HERIT`, scoring a 2017 hotel bar **77** | **exclusion contexts** |
| one-sided evidence pinned `ENRG`, `POL`, `SCEN` to **98** | **blend toward the type prior** |
| `TALK`, `FOCUS`, `LIVE` scored nothing - nobody writes *"I could not hear"* | **the prior answers when the text does not** |

**Mean gap against the hand-built row: 23.1 points -> 7.1, and 8 of 11 factors scored -> 11 of 11.** `HERIT` went
**77 to 10 on one exclusion rule**.

**It still cannot give the bands** - it gives a venue-level amplitude, which is exactly what images were going to
supply, so **reviews and images are interchangeable sources for the same input** and the hourly shape still comes
from the type. Images become what the user called them: **supporting data** - and `GAMES` at 37 against a
hand-built 45 on a single mention is the case in point, where **one photograph of a board-game shelf settles it**.

**The honest limit:** the hand-built row came from the same corpus, so 7.1 measures the method **reproducing
careful reading**, not being right about Bohca. Real validation is a venue the user knows well, scored blind.

## [2026-10-02] Summer House scored blind, and the popularity floor (entry 148)

### The popularity floor

**The user: there are more than 8-10 clubs - there is a long tail - "but the app should only suggest the popular
ones if the user hasn't set a budget."** So **popularity is a default floor and a budget releases it.**

**Right rather than merely convenient:** a user who states no budget has told you nothing about price, so the safe
default is *the places people actually go* - **being sent somewhere obscure is a worse failure than being sent
somewhere predictable.** A user who states a budget has told you what matters, and then the long tail is not a
risk but the answer. `popularity` is `userRatingCount` normalised within `(type, area)` - already fetched.

**And it resolves the thin-club worry properly.** The late set is small *by default and deliberately*. Not thin
supply - a floor doing its job, lifting the moment somebody says what they want to spend.

### Summer House Cafe, scored blind

Run cold on a corpus gathered from Google, TripAdvisor, JustDial, Wanderlog, Time Out, District, LBB, Delhi10,
Reddit and the venue's own Instagram. **The test is not whether the numbers look plausible - it is whether the
method SEPARATES two venues it has never compared.**

**7 of 11 factors separate Bohca and Summer House by 20+ points, and the separations are all in the right
places:** `LIVE` **15 against 92** (DJs against Boxout Wednesdays and touring acts), `FOCUS` **25 against 78**
(nobody faces a DJ; everybody faces a band), `TALK` **18 against 63** (*"catch up with friends"* appears in one
corpus and not the other), `POL` **90 against 63** (bouncers and guestlist against *"everyone wears whatever the
hell they want"*). **Nothing had to be told these venues differ.**

### And the blind run found the method's real limit

**`ENRG` came back 41 for a venue that is also a late party.** The cause: **the corpus is hour-blind.** Reviews of
a daytime terrace date spot and reviews of *"party harder"* sit in the same bag and get averaged into a number
describing neither.

**Partitioning by time markers helps a lot and not uniformly.** Splitting on *during the day / brunch / 5pm*
against *night / party / DJ / late* gives `MOVE` **30 against 70**, `FOCUS` **28 against 78**, `LIVE` **35 against
92** - large and correct. But `ENRG` only moves 38 to 48, because the venue's own category blurb (*"Relaxed
cafe"*) is a daytime descriptor that appears in every listing and lands in the unmarked pool.

**The honest resolution is that this is not the lexicon's job.** The `ENRG` band comes from the type curve times
an amplitude (entry 141); asking the text for it is asking the wrong source. **The lexicon's job is the
preferences and the character, and at those it is strong.** Partitioning stays, because it sharpens the factors
that genuinely vary by hour.

## [2026-10-03] The slot model - every factor resolves for a (day, hour) (entry 149)

**The user: "each venue's factor scores should be hour and day dependent, so for a particular venue the factor
scores will actively get replaced with the factor scores of that hour range and day in real time."**

### The correction that forced it

**The user had been to Summer House on a Thursday and a Friday after 23:00 and seen no live act either time,
until it closed at 01:30. The lexicon had scored it `LIVE` 92.**

**The score was not wrong - it was the right answer to the wrong question.** Summer House genuinely is a
live-music venue; that is its reputation and it is accurate. What the text could not say is **when**, because
**Boxout is a Wednesday**, and reviewers write about venues while the venue's own Instagram writes about the
schedule.

### The row becomes a base plus slots

`base` holds what does not move; a `slot` is a `(days, hours)` window naming **only the factors it changes** and
inheriting the rest. Resolution starts from base and applies the most specific match - a named day beats a range
beats `all`. Summer House now reads `LIVE` **95 on a Wednesday at nine** and **12 on a Friday at eleven**, which
is exactly what the user saw and what a flat number could never have said.

**This supersedes the flat `prefs{}` of 2026-10-01 and the `bands[]` of 2026-10-02 by absorbing them** - bands
were this idea applied to two factors and the events table was it applied to a third. **One mechanism, three
names.**

### The cost is about ten authored numbers a venue

Summer House carries 11 base and 30 slot numbers, roughly double the flat row - **but almost none is authored.**
The base comes from the lexicon in one pass; the **ordinary slots are generated** from the type curve times the
venue amplitude; **only the exceptions are written by hand**, and there are one or two. Summer House's single
exception is Boxout Wednesday; Bohca's are Sunday brunch and the weekend club mode. **A 50-venue seed is still an
afternoon.**

### Three consequences

**`prefs{}` are no longer fixed**, reversing 2026-10-01 - **but only for the factors that move.** `SCEN`, `HERIT`
fabric, `FOOD` and `POL` stay in the base; `LIVE`, `FOCUS`, `GAMES` and `MOVE` move into slots. **That decision
was right about most preferences and wrong about the programmed ones**, and Bohca's Sunday board games was the
first sign of it.

**The events table and the slot table are the same thing.** Heritage programming, the `FOCUS` clock anchor, Boxout
Wednesday and Sunday brunch are all a `(days, hours)` window overriding some factors. Two tables collapse to one.

**And it sharpens the division of sources: reviews fill the base, the venue's own posts fill the slots.** Boxout
Wednesday was stated plainly on Summer House's Instagram and appeared in **not one review** - which is the whole
division of labour in a single example.

## [2026-10-03] Where the slots come from - the schedule has no API (entry 150)

**The reframe first, because it shrinks the problem: most slots are not events.** The weekday/weekend split, the
day/night split and the kitchen hours come from opening hours and the type curve. **Only the exceptions need a
schedule, and the exceptions are mostly recurring weekly rituals.** *Boxout Wednesday is not an event - it is a
standing fact about Wednesdays.* You learn it once and it holds for months. That turns *a live events feed* into
*a one-time look refreshed quarterly*, which is a much smaller problem.

**What exists:** the **venue's own Instagram is the primary source and effectively the only one** - Boxout
Wednesday was announced there and appeared in **zero reviews**. **District and Paytm Insider have APIs but they
are partnership-gated** and only cover what sells tickets. Scraper services exist and are paid and grey. **Google
Places has no events field at all.**

**And the one that should have worked does not.** `schema.org/Event` markup on the venue's own site would be ideal
- it is published *for* machine reading and it is the venue's own data. **Checked on summerhousecafe.in: zero
Event nodes, and the entire site is four links, all menus.** Meanwhile the Instagram has 24.1k followers and
carries the programme.

**That is the Delhi independent venue in one example: the web presence is a menu and the schedule is an Instagram
feed.** Any design assuming a parseable events page fails on most of the seed radius.

**So: one manual pass at seed time** - fifty Instagram accounts, note the recurring nights, an hour or two, and it
is the same pass that collects the images. **The partner agreement carries it after that**, because the venue
wants the traffic. **Refresh quarterly, not nightly** - treating a recurring ritual as live data solves a problem
that does not exist. One-off events are genuinely feed-shaped and genuinely unserved, and matter less because the
engine selects on the ordinary night.

## [2026-10-03] MVP instructions - what ships without partner agreements (entry 151)

**The user is launching with no partner agreements**, so there are no schedules, no reservations, no capacity and
no venue-supplied media. **`MVP_INSTRUCTIONS.md` is written and outranks the other specs for scope.**

> **Find people like you, and places you like.** That sentence is the MVP.

### The biggest change: the app offers instead of generating

**The user still draws a skeleton, and the app no longer builds the outing from it.** Each stop returns **5-10
venues whose factor scores match that stop's shape and which are open at that hour**, and the user picks. They
build their own night.

**This is the right call and it follows from refusing to promise what we cannot keep.** *"Here are eight places
that feel like what you drew"* is supportable from the lexicon scores alone; *"this is your 11pm"* needs bands we
do not have and makes a claim nobody asked for.

**And it inverts the seed-radius argument.** That argument was about making the *automatic* plan honest - since
there is no automatic plan, **breadth beats depth**, so the MVP carries the **full ~360-venue NCR list** rather
than 40-60 in one area. A user picking from a list wants options.

### What waits, and the one deletion

Bands, slots, schedules, reservations, app-generated plans, time-anchored stops, clock anchors, dish and drink,
and *what's popping tonight* - all deferred, specs unchanged, they are the destination rather than the release.
**Heatmaps are cut outright**: they need volume we will not have, and at low volume they are either empty or they
identify individuals, which the privacy rules forbid.

**The one thing that cannot wait is opening and closing hours on every venue.** A list containing closed venues is
the fastest way to lose trust.

### The distinctive feature: vibe chemistry on a profile

**The user's idea, and it is the best thing in the MVP.** Under the match percentage on somebody's profile, a
**headline and three or four lines saying what the two of you would actually be like** - generated by running
`CHEMISTRY_V4`'s axis rules at n = 2. Eight headlines, and a fixed table of **nine readings per factor across
(your pole, their pole) - 54 sentences, written once.**

**Why it earns its place: a percentage says how alike you are, the read says what would happen.** The worked case:
**Ishaan matches Zoya 80% and Dev 71% - close numbers, nothing alike as nights.** With Zoya the read has content
on both sides. **With Dev every line in the top four starts with *you***, because he sits in the middle on all six
factors and nothing fires. **That is not a bad match - it is a night one person has to carry**, and the percentage
cannot say so.

### And it is the sharpest test the MVP runs

**Do people care who they are matched with?** The entire identity half of the app rests on it and it has never
been tested. **If the chemistry read gets opened, screenshotted and argued with, the answer is yes.** Venue
accuracy is deliberately not on the test list, because the MVP does not claim it.

## [2026-10-03] The 54 chemistry lines, and heatmaps gated rather than cut (entry 152)

**Heatmaps are deferred to a user threshold, not removed** (the user's correction). **And the switch defines
itself from a rule already in `VIEW_FLOW.md`:** an area may only render once **20 distinct users** are in it.
**So: turn heatmaps on when the median active area clears 20 distinct users on a normal Friday.** Not a date, not
a headcount - the same number the privacy rule already needs, measured rather than guessed.

**Below that threshold a heatmap is one of two bad things:** empty, which makes the app look dead, or populated by
so few people that an area identifies them, which the rule forbids. **Both failures disappear at the same moment,
which is why one threshold governs both.** Collect for it from day one - locked plans already record venues and
areas - so it is a switch rather than a build when the number arrives.

### The 54 lines (`CHEMISTRY_LINES_V1.md`)

Six factors x nine pole combinations, written as copy rather than as a lookup table. **Written to the viewer about
the person whose profile is open**, one sentence each, saying **what will happen rather than what you are**.

**Three rules the copy follows, and the second is the one that will be broken first:**

**A difference is never a warning.** *"You'll dance and they'll hold the table - that's a good arrangement"* is the
tone. The app is not a compatibility test.

**No line may be true of everybody.** If a sentence reads fine against any other pole combination it is not saying
anything. **The mid/mid lines are most at risk**, which is why several are deliberately short - a flat axis
genuinely has little to say and padding it would be worse than admitting it.

**The low/low lines are the hardest and the most valuable.** Two people who both want the quiet, seated, unplanned
version of a night are a real and under-served pair, and their lines must never read as the absence of energy.
*"A calm night, and you both actually want one"* is the model.

## [2026-10-03] The gold promotion - crowdsourcing the bands (entry 153)

**The user's design, and it is the best answer to the band problem anyone has proposed**, because it collects the
number at the one moment it is true: a person standing in the room, at that hour, on that day. Venues with missing
bands go gold **contextually** - driven by the time window the user already chose - and the reward requires
actually going, through the app, with location on. `GOLD_PROMOTION_V1.md` has the design and the costing.

**The cleverest part is the demand steering.** Every other crowdsourcing scheme collects most where coverage is
already best. **The gold highlight actively points people at the gaps**, using a signal the app already has.

### What actually needs capturing

**The user is right that a Big Chill does not need this** - six of eleven types need nothing, because a flat venue
is already described by its type curve. The programme targets **clubs, big loud bars, pubs, lounges and live
rooms: 214 of 416 venues, and 1,156 slots once day-modes are counted.** Three captures a slot, median taken, each
tagged `(venue, day-mode, hour-band)` and counting toward that slot only.

### What Rs 2-3 lakh buys, and it is a coverage question not a voucher question

| coverage | captures | per capture | |
|---|---|---|---|
| everything | 3,468 | **Rs 72** | nobody completes it twice |
| top 60 | 972 | Rs 257 | workable |
| **top 35 - clubs + the named bars** | **567** | **Rs 441** | **a real voucher** |
| top 20 | 324 | Rs 772 | overpaying, widen instead |

**The top 35 is the answer, and it is the same 35 the app queries most.** The rest keeps the type curve, which is
already 83% as good at putting the pick inside the shape gate - so the captures are spent where the curve is
weakest and the traffic heaviest, which is the same place.

### And the split should be inverted

**The user proposed a voucher for the photos and a bonus for the swipe. It should be the other way round.** The
photos give an **estimate**, after the reference sets and the confound rule. **The swipe gives the band itself** -
a person in the room at 23:40 on a Friday saying *this is an 8 for energy, a 9 for how full*. **It is the number
we have spent a week trying to infer from photographs and review text, stated by somebody looking at it.**

So: **Rs 450 a capture - Rs 180 for the photos as proof of presence, Rs 270 for the swipe as the data** - with a
**1.5x multiplier on the 24:00-02:00 band** (Rs 675), which is the band nobody is awake to capture and the one
clubs are entirely defined by.

### The risk the design does not handle

**Bands go stale.** A capture is true for a season. **Stamp every band with its capture date and let the gold
return to anything older than six months** - which turns the promotion from a launch campaign into **how the
database stays alive**, worth more than the initial fill.

## [2026-10-03] The capture cap, compulsory swipes, and verification (entry 154)

### Does capping a slot at three captures let us pay more? No - and it is worth far more than a raise

Simulated. **Without the cap, 53% of everything paid for is a duplicate**, because visits pile onto the popular
slots: you pay three times for a Friday at the club everybody already goes to and never once for its Tuesday.
**At the same Rs 441 the budget covers 7.6 venues without the cap and 34.8 with it.**

**So the cap adds no money - it makes the money do what the costing assumed.** What it legitimately allows is
**dropping the waste buffer**: any honest plan without a cap needs 40-60% extra for duplicates, and removing that
is arithmetically a raise already spent in the Rs 441. **Keep Rs 450 and take the coverage** - Rs 600 buys 20
venues instead of 35, and the 15 dropped are exactly the second-tier ones the type curve serves worst.

**One practical note: the budget is a ceiling, not a commitment.** 567 captures needs 200-280 users doing two or
three each. **If uptake is lower, raise the amount rather than leave it unspent** - with the cap, a higher price
cannot be wasted on duplicates.

**And reserve on arrival, not on sight**, with a 45-minute release - otherwise people who never go hold slots.
**Show gold to more than three with a counter** (*"2 rewards left here tonight"*) so a slot cannot stall on one
person changing their mind.

### Compulsory swipes resolve the split rather than adopting it

**The user: make the swipes compulsory, photos first.** Correct - and if both are required there is no split. **One
task, one payment**, and the question of which half is worth more disappears. **Rs 450 complete, Rs 675 for the
24:00-02:00 band.**

**The ordering is right for a reason worth stating: the photos get the user looking.** Framing a wide shot, a crowd
shot and the bar makes somebody *see the room* before being asked to rate it. Swiping first is rating a room you
walked into ninety seconds ago.

**And it gives the photos their proper job** - no longer the data, no longer only proof of presence, but **the
instrument that verifies the swipes.** Better than either.

### Verification, and the asymmetry that sets the threshold

**Paying Rs 450 for one bad capture costs Rs 450. Telling an honest user they cheated costs that user and everyone
they tell.** So the threshold is tuned on the false-accusation rate first:

**A capture fails only when two or more factors are off by five or more** - catching **48%** of careless swiping
and wrongly failing **1.4%** of honest users. **Letting half the careless captures through is the right trade**,
because the median of three absorbs them, which is what the three were always for.

**And never phrase it as an accusation.** *"We couldn't verify this one - try again at your next stop"* costs
nothing and keeps the user; *"you didn't complete this honestly"* is unrecoverable and will sometimes be wrong.

**The warning sentence is worth more than the algorithm.** Telling people an answer will be checked moves them
from satisficing to actually looking, whether or not the check works. **So show it before the photos** - the user
needs to know while they are still looking at the room.

### Staleness: the user's answer is better than mine

I proposed the gold returning to any band older than six months, making this a permanent refresh mechanism. **He
pointed out that by the time bands go stale we should have partnership agreements with exactly these venues** - and
he is right, because **the 35 venues this programme targets are by construction the 35 most worth partnering
with**: the ones the engine queries most and whose character the type curve predicts worst.

**So the promotion is a bridge, not a feature.** Still stamp every band with its capture date - not to re-run the
promotion, but so a band's age is visible when choosing which venue to approach. **The staleness clock becomes the
partnership priority list.**

## [2026-10-03] One capture per slot, and the gamble (entry 155)

**The user: one person per slot. They see it, complete it inside the window, and are paid. Fail verification and
they retry. Run out of time and it releases to the next person.** *"I want to see if I'm lucky enough to get
this."* Budget raised to Rs 5 lakh.

### The time-box is what makes one capture safe, and it was already in his design

I had argued for three because *"one capture is one night - a Tuesday at a Friday venue becomes the band
forever"*. **That risk is already gone.** The slot IS `(venue, day, hour-band)` and **the capture must happen
inside that window or it releases** - so a capture cannot land in the wrong slot. What remains is only the
variation between one Friday-at-eight and the next at the same venue, which is far smaller than the day-and-hour
variation the three were guarding against.

| | mean error |
|---|---|
| no capture, the type curve | **8.2** |
| **one capture** | **5.8** |
| three captures, median | 3.9 |

**Three is better than one, and that is not the question.** The question is **whether one capture everywhere beats
three captures on a sixth of the database**, because that is what the same money buys - and it does, because
**the alternative to a noisy capture is not a better capture, it is the type curve**, which is worse than one
capture and applies to every slot we skip.

### Rs 5 lakh at one capture a slot

| coverage | slots | per capture |
|---|---|---|
| every slot, both day-modes | 1,156 | Rs 433 |
| **weekend slots, all 214 venues** | **578** | **Rs 865** |
| the top 35, both day-modes | 189 | Rs 2,646 |

**Weekend slots across all 214 venues at Rs 865.** A reward worth gambling for - which a modest one would not be,
and the mechanic needs it. Every venue covered where it matters, since Thursday to Sunday is where the plans are
and a Tuesday at a club is mostly a closed door. Weekday slots keep the type curve, which is what they would have
had anyway. **Top-35 weekday slots become an obvious phase two.**

### What the gamble fixes, beyond the advertising

**The promise becomes clean.** Three captures meant *"you might be third and get nothing"*. One plus a retry means
**if you got the slot, you get paid** - provided you do it properly. That is worth advertising; the previous one
was not.

**And failing verification stops being a punishment.** With three, failing cost you a slot somebody else would
take. With one and a retry it costs **thirty seconds** - exactly the right stake, because the check is wrong 1.4%
of the time and that error now costs nobody anything.

**The release is the only part that can feel unfair, and only if unannounced** - so the notification says *"you
have until 22:00"*. **The window is the timer**; there is no separate countdown.

### And the real price of dropping to one

**There is no cross-check left.** With three captures an outlier could be caught by comparison; with one, the
photo-against-swipe verification (§4b) is the only thing standing between a careless capture and the database.
**That makes §4b load-bearing rather than a backstop**, and it is the one thing to watch when the first captures
come in.

## [2026-10-03] The gold promotion folded into the MVP (entry 156)

**`GOLD_PROMOTION_V1.md` ships with the first release rather than after it**, written into
`MVP_INSTRUCTIONS.md` as §2.6 with the user-facing flow: gold appears contextually, one person per slot, the
verification warning before the photos, photos then compulsory swipes, paid on verification, retry on failure,
and the window stated up front.

**Three reasons it belongs in the MVP and not after it.** It is **the only feature that makes the app better the
more it is used in a way the user can see** - each capture moves a slot from estimated to measured, and filled
slots are what bring time-based plans back. It **gives the MVP a reason to exist on a Tuesday**, since the core
loop is weekly at best and the gamble is a reason to open the app and look. And it is **the cheapest venue
research anybody could run** - Rs 5 lakh covers the weekend slots of all 214 venues that need them, collected by
people who were going out anyway, at the moment the number is true.

**What it must not become: a scheme people join for the money rather than the night.** The design already guards
it - the venue must be in a plan they built - and **the copy should never lead with the reward. Gold is something
you notice while planning a night, not a reason to plan one.**

**And it adds a fourth question to what the MVP tests, with the clearest pass mark of the four:** will somebody at
a bar give ninety seconds to photographs and swipes for Rs 865? **If not, the band problem has no cheap solution**
and the answer is partnerships, slower and sooner than planned. 578 slots - we will know inside a month whether
they are filling.

**Also fixed:** the earlier cross-reference had been inserted inside the deferred-features table and was breaking
it.

## [2026-10-03] The pre-promotion build - the confidence gate (entry 157)

**The user: build the database from reviews, photos and the venue's own information first, fill slots "as much as
possible" - Bohca's club-after-ten is accurate and goes in - and leave the convoluted ones empty for the gold
promotion.** So every slot needs a decision, and `VENUE_DATABASE_V1.md` §2a0 is the rule.

### The gate

**A slot fills at 3.** `structured` (a Google field) and `own_copy` (the venue's own site or Instagram, **stating
the time**) are worth 3 each; a `timed_review` naming an hour or a day **and** a character is worth 2; the lexicon
base is worth 1 and **never fills a slot on its own**, because it describes a venue and a slot is about an hour.

### What it produces

**Bohca's weekend club mode fills** on two timed reviews plus the closing time; **its weekday late night goes
gold** because nothing in any source says what it is. **Summer House's Boxout Wednesday fills** on their own
Instagram; **its Thursday-to-Saturday late slot goes gold** because *"party harder"* names no hour.

**And the gate refusing Summer House's 18-22 slot on a single timed review is it working rather than failing** -
one person's seven o'clock is one night, two agreeing would have filled it, and the cost of being wrong is a venue
in the wrong list for months.

### The finding: the gold list is not a separate decision

**Nobody chooses which venues go gold. The build produces the list by failing to fill a slot.** The empty slots
and the promotion's target queue are the same object seen from either end - export them, sort by popularity, done.

**And look at which slots they are: every daytime slot fills from structured data alone, and every late slot but
one is gold.** The evidence is thinnest exactly where the venue transforms, because that is the part nobody writes
down - **a listing states what a place IS, reviews describe the night people had, and the quiet Tuesday at eleven
is unrecorded everywhere.**

Expect **half to two-thirds of slots fillable before a single capture**, gaps concentrated in the late bands.
**And the three findings line up:** the slots hardest to derive, the slots the type curve predicts worst, and the
slots users query most are the same slots. Nothing has to be traded off.

### The rule that matters most of the five

**Never infer a slot from the type curve and store it.** It is the one mistake that would poison everything,
because **a stored guess is indistinguishable from a measurement a month later.** Leave it empty and let the
fallback happen at query time, where it is visible and reversible. And **mark every filled slot with its source**,
so that when a capture contradicts it later the source decides which wins: a capture beats a timed review, and
nothing beats the venue's own statement of its own programme.

## [2026-10-04] The OSM pull, a real admission pass, and the pipeline (entry 158)

### OSM works, and it is not enough

**Overpass returns 406 without a User-Agent header** - that was blocking four earlier attempts. With one: **598KB
in 5.5 seconds, free, no key, and ODbL means everything in it is storable.** 2,027 named Delhi NCR venues.

**But only 124 are bars, pubs or nightclubs** against the ~360 we estimated pass admission, **7 of those 124 have
opening hours**, and the sample is visibly stale - Blue Frog closed years ago, Yo!China is a restaurant tagged as
a bar, and there are entries called *"Bar and restaurant"* and *"sam"*. **OSM cannot build this database.**

### The reframe that dissolves the licence problem

**What we need to store is not Google's content - it is our own.** Venue type, bands, slots, factor scores, tags,
admission verdict: **those are our judgements.** Storing `place_id` plus our own numbers is fully permitted, and we
never need to store Google's name, address or rating because **we re-fetch those live for display**, which is
exactly what Places is licensed for and what the venue screen already does.

### A real admission pass found a flaw in the filter immediately

Twelve Delhi NCR venues researched live. **8 admitted, 2 rejected, 2 incomplete** - and one of the rejections is
the finding: **Privee fails on a 3.6 mean**, a well-known club in the Shangri-La with 1,380 reviews.

**We already knew why: clubs collect door complaints that restaurants do not** (entry 145), and we decided those
are evidence about the door rather than quality. **But the mean rating has already counted them before we see
it.** Kitty Su 4.1, Bohca 4.1, Privee 3.6 against Piano Man 4.5, Hauz Khas Social 4.3, Summer House 4.2.

**A club rates roughly half a point below a bar of the same quality, structurally** - so an absolute 4.0 floor is
a TYPE bar, not a quality bar, and it excludes the type the app most needs. **The mean floor becomes the 35th
percentile within the venue's own type**, which is what `quality` already does and what the filter should have
been doing from the start.

### And the pipeline, which is the answer to "can you do it yourself"

**Partly.** One browse plus one tight extraction per venue is about 400 characters and four venues to a batch -
so a bounded set is feasible by hand and 2,027 venues is not. **`simulations/pipeline.py` is what does it at
scale**: OSM skeleton in, Places enrichment live, admission type-relative, the lexicon over the five returned
review texts, the confidence gate, and out comes the database plus **the gold list it implies**.

It stores **only IDs and our own derived data**. And it is honest about two columns it cannot fill: `rating_sd`
(no histogram exists - it substitutes **sentiment variance over the five texts, routed first**) and `fitout_years`
(not in any API - a human glance at the photos, about three seconds a venue).

## [2026-10-04] The pipeline made runnable, and the runbook (entry 159)

**Hand collection stopped at 16 venues on the user's call.** `simulations/pipeline.py` is now a real tool and
`VENUE_BUILD_RUNBOOK.md` is the instructions.

### What the pipeline does

Three stages. **`discover`** runs Nearby Search over 22 Delhi NCR districts x 5 types - 110 calls, ~$3.85.
**`enrich`** makes one Details call a venue, **caching every response so a re-run costs nothing**, with backoff on
429 and 5xx. **`build`** needs no API at all: type-relative admission, the lexicon over the five review texts, the
confidence gate, and out come `venues.json`, `gold_list.json` and `human_pass.csv`. `--dry-run` prices any stage
without spending.

### Three bugs the smoke test caught before anything was pushed

**The lexicon's priors are keyed by SHUFFL venue types and `coarse_type` is keyed by Google's**, so every factor
was falling through the no-prior path and returning extremes - `ENRG` 7 and `TALK` 100 off two keyword hits on a
venue with five reviews. A `PRIOR_KEY` map fixes it; all eleven factors now score sanely.

**`human_pass.csv` listed every venue including rejected ones**, so somebody would have been eyeballing photos of
places already filtered out. Now admitted-only - 20 rows became 5.

**And an unknown operator failed admission, so a venue needing a human to classify it could never reach the
human.** Unknown now passes and is flagged instead. That one would have silently deleted every independent venue
not on the chain list.

### The validation set

`realrun.py` holds the **16 venues researched by hand**, with real ratings and counts - **14 admitted, 2
rejected**. It is the only validation set that exists: run the pipeline over the same sixteen and the numbers
should match, and the discrepancies will be more interesting than the agreements.

**And one failure worth keeping in the file:** searching *"Cirrus 9"* returned a venue at The Oberoi when Cirrus 9
is at the Shangri-La. **A wrong-venue match is worse than no data**, and it is the failure mode hand collection
has that an API call does not - **the API matches on a place_id; a human search matches on a name and a guess.**

## [2026-10-05] The flow doc caught up to the MVP, and three screens redrawn (entry 160)

**`MVP_INSTRUCTIONS.md` §2.2 retired the plan generator on 2026-10-03 and nothing on the front end had been told.**
The flow doc is updated and the three screens built on the generator are redrawn.

### The flow doc

**The SHUFFL screen's middle section is rewritten.** Item 3 was *an outing plan, already generated for them*; it is
now **the shape as a list of stops, each carrying a count of the venues that fit it and are open at that hour**.
**A new section, THE STOP LIST, specifies the core loop of the first release** - 5-10 venues ranked by shape
distance, open-hours as a hard filter, picking fills a stop and is reversible, and **nothing is scheduled**.
*Give me something else* is retired: **it regenerated a plan and nothing generates a plan any more**, and the need it
served - *this shape, different venues* - is now the stop list itself, which is a list of exactly that.

**A second new section specifies gold on the front end**, since `GOLD_PROMOTION_V1.md` ships at launch: the three
surfaces a venue can appear gold on, the time box and amount in the reward line, and the capture order - **the
verification warning first, then live-camera photos, then the compulsory swipes** - with the note that `#FFC247` is
artwork-only everywhere else and **gold is the single exception**.

**Also marked:** *What's poppin* deferred, **heatmaps gated rather than cut** at 20 distinct users, and **a preset is
a shape and not a plan** - which is why presets survive a cut that removed the generator.

### Four copies of the flow doc, two of them different

**`frontend/VIEW_FLOW.md` was a stale fork**: 469 lines against the live 798, last written 2026-09-25, still
carrying the **seven-factor deck, the V4 names and six preferences** - all three superseded on 09-30. Anyone reading
the front-end folder rather than the decisions folder would have built the wrong assessment. **All four copies are
now byte-identical.**

### The screens

**03** loses the generated line-up and gains the shape with a per-stop count of places; *What's poppin* and the
heatmap line come off; suggested venues grows to three rows. **02** is the same screen blurred, so it was blurring
the old model. **10** changes one control: **Regenerate a stop became Change a stop**, because a refresh glyph on a
card whose venues the user picked promises something the app no longer does.

**Fifteen were checked and left alone**, and **17 turned out to need nothing** - the green-versus-magenta
disagreement flagged on 10-01 was resolved in the screen's favour when the doc was corrected.

**Two sets still do not exist and both ship: the stop list** - which screen 03 now points at three times - **and
every gold screen.** They are new screens rather than changed ones, which is why this pass did not produce them.

## [2026-10-05] The stop list and the gold promotion, drawn (entry 161)

**Five screens, closing the two gaps the morning's audit named.** Both ship at MVP, so neither could stay undrawn.

### 19, the stop list

**The most overdue screen in the set** - `MVP_INSTRUCTIONS.md` 2.2 made it the core loop on 10-03 and screen 03 had
been pointing at it three times with nothing to point to. **Three things it does that the generated plan did not:**
it restates the stop **in the user's own words** - *a big loud bar, you can still hear each other* - so they can
tell whether the list is answering the right question, and **never shows a factor score**; it says **open at 22:30**
in the header, because opening hours are the one field the screen cannot work without; and the footer states the
only claim the app makes, which is that **nothing here is booked**.

### 20-23, the promotion end to end

**The order on 21 is the part to keep. The warning comes before the camera** - not after the photos, not beside the
reward. It sets the terms while the user has invested nothing, **which is the only moment it reads as fair rather
than as an accusation.** Then live camera only, with the reason given in a line rather than enforced silently: *a
photo from another night is evidence about another night.*

**22 carries the fact that decides the design: the swipes are what gets stored and the photographs only corroborate
them.** A build that treated the photos as the data and the swipes as a flourish would have it backwards.

**23 states the payoff twice, because there are two** - the money, and **the slot moving from estimated from its
venue type to measured.** The closing line is the gamble made explicit: you were the only capture for this slot.

### One theme rule broken on purpose

**`#FFC247` is artwork-only by `THEME_LINEUP.md`. Gold is now the single exception**, and it reads precisely because
nothing else in the chrome uses it. Written into `VIEW_FLOW.md` with the rest of the gold section.

**Still undrawn:** gold in search and inside a room's plan (the treatment carries over unchanged from 19), **and the
verification failure state**, which is one screen different from 23. That one fires about **1.4%** of the time and,
with one capture per slot, **is the only check on the data** - load-bearing and fallible at once, which is why its
copy may never accuse.

## [2026-10-05] The host picks, gold in search, and the failure state (entry 162)

### The host picks

**The question screen 10 raised yesterday is answered: in a room, the host chooses the venue at each stop.** The
merged skeleton gives the stops; the host opens each stop's list and picks, and the plan fills in for everyone as
they do.

**The two alternatives are worse for the same reason. A vote turns every stop into a negotiation on a night people
joined to stop negotiating**, and first-to-tap rewards whoever happens to be looking at their phone. **The host
already carries the room's three filters** (`SKELETON_MERGE_V1.md` 1), so picking is the same authority applied to
the same object rather than a new one being invented.

**What a member sees is the part that decides whether it feels fair:** the stop list read-only, the host's choice
marked, and *Aarav is picking your 22:30* - the same push the capsule approval already uses. **Members are locked
out of the decision, never out of the information.** `Change a stop` on the plan card is the host's control alone,
and a member tapping it gets the read-only list with *ask Aarav to change this* - **never a greyed button with no
explanation.**

### 24, gold in search

**One rule, easy to get wrong and expensive: gold marks a venue and never ranks one.** Summer House is first
because it fits best and would sit third if it fitted third, and the screen says so in its own voice. **The moment
gold moves a venue up a list, the fit number stops being true and the whole screen is advertising.**

**The other thing it keeps straight** is the one the search spec already flagged: the number against a place is a
fit against tonight's shape, while the vibe match lives on the home screen's people search. **Two numbers that look
alike and come from completely different places.**

### 25, the verification failure

**The most delicate copy in the app** - about **1.4%** of genuine captures fail, and with one capture per slot this
is the only check on the data. Four rules: **it never says the user did anything wrong**, because 1.4% of the time
they did not; **it gives the rate in plain words** rather than hiding a number they would be right to want; **it
puts the slot back on the board and says so**, because a failure that silently consumed the slot is the one outcome
nobody would forgive; and **it says what usually fixes it**, since a retry with no guidance is a second coin toss.

**And it is quiet. The paid screen spends the gold; this one does not**, beyond the one button offering another -
a failure rendered at the volume of a payment reads as a penalty.

**Still undrawn:** gold inside a room's plan, and the member's read-only stop list. Both are existing screens with
one element changed.

## [2026-10-05] The last two screens, and the set is complete (entry 163)

**Twenty-seven screens. Every surface the MVP ships is now drawn.**

### 26, gold inside a room's plan

**The only gold surface where the screen is shared and the reward is not**, which is why it needed drawing rather
than describing. A gold stop renders gold on a plan five people are looking at, so the card has to state what a
shared screen otherwise leaves ambiguous: **one person per slot means one person, not one room.** **Without that
line a room of five reads the chip as five rewards** - and four of them find out otherwise at the venue, which is
the worst place to find out.

**The `Change a stop` control carries *you are the host* beside it**, so the asymmetry introduced yesterday is
explained where it is exercised rather than discovered.

### 27, the member's stop list

**Screen 19 with the decision removed and nothing else removed.** The header names who is choosing, the host's pick
is marked, the rest stay visible but dimmed, and **the affordance is a request rather than a greyed button**. The
footer is the rule in one line: *you can see everything Aarav can; the pick is his because the room is.*

**That sentence is the test for every other screen that gates something.** A greyed control with no explanation
was the failure mode, and the member's list is where it would have been easiest to ship.

### What is left

**Nothing on the release path.** The swipe game (held for the card images), settings and onboarding, the Go-here
card's one-stop state, and motion.

## [2026-10-05] The developer's first venue database, reviewed (entry 164)

**110 South Delhi venues delivered. The structure is right, the evidence layer is missing, and one decision caused
nearly all of it.** Written up as `VENUE_DB_REVIEW_01.md`.

### What pass 1 got right, and should not be rebuilt

**1,818 field-level source rows** - every non-Unknown field carrying a URL, a source date and an access date. **No
API gives us that**, and it is the audit trail if the licensing is ever questioned.

**And it invented nothing.** *Estimated slots: 0. No invented time schedules.* Every gap is an honest `Unknown`.
**That is the single most important behaviour in the job** - a fabricated slot is indistinguishable from a measured
one a month later - and the developer got it right without being asked twice. The `Needs_Verification` sheet
already names almost every gap this review found, so **the problem was never diagnosis. It was being blocked.**

### The decision that caused it: the licence read as stricter than it is

**The rule is about storage, not access.** We may call Places and derive our own data; we may not store Google's
names, ratings or review text; we may store `place_id` indefinitely and anything we computed ourselves. **The
developer read it as *do not call Google at all*, built from official websites only, and so had no ratings, no
review text, no hours, no coordinates and no place_ids.**

**Measured:** all nine factor scores filled on **0 of 110** rows, any score on 9. Opening hours 61%, coordinates
34%, **`google_place_id` 3%**, price band 2%, fit-out 0%. Of 155 slots, **2 carry any score.** And **admission
never ran** - all 110 admitted on *named public venue with official location evidence*, which tests whether a place
exists, not whether it is established. Four of our six criteria have no column at all.

### The finding that is hardest to see from inside

**Website presence became the filter, and an official website is a proxy for chain or hotel, not for established
nightlife.** 91 of 110 rows are Group, Chain or Hotel-attached - **83%**. 33 rows are branches of nine brands. 26
are hotel F&B. **Only 36 of 110 are a nightlife type at all, and only 3 are clubs.** Aerocity carries 21 venues
against Hauz Khas's 8 - the airport hotel district outweighing the actual nightlife centre by nearly three to one.

**Five well-known venues inside the stated catchment are absent:** Summer House, Bohca, Dear Donna, Depot 48 and
Imperfecto HKV - and the catchment names all four of those areas.

**Rating volume is exactly what separates a chain coffee branch from an established independent bar, which is why
admission is built on it.** Without ratings, website presence was the only signal available and it pointed the
wrong way. **This is the Nik Baker's-versus-Kent's test failing in the other direction** - every chain with a
corporate website in, the independents people actually go out to missing.

### What the brief asks for

`place_id` on all 110; discovery re-run from Nearby Search rather than websites; `enrich` then `build`, so
admission runs properly with **the mean floor relative to type**; the list expected to shrink and new independents
expected to appear, both being the filter working; and **`Venue_Sources` and the `Unknown` discipline kept exactly
as they are.**

## [2026-10-05] The catchment split in two, South Delhi the default (entry 165)

**`pipeline.py` carried one list of 22 NCR districts, and the first database pass is South Delhi only.** It now
carries two - `SOUTH_DELHI` (20 districts) and `REST_OF_NCR` (12) - with `--catchment` choosing, defaulting to
south-delhi. **100 calls and ~$3.50 against 160 and ~$5.60**, and the NCR list is kept rather than deleted because
**NCR is the destination** (`MVP_INSTRUCTIONS.md` 2.3, ~360 venues) and trimming would have thrown it away.

**The South Delhi list is built to match the developer's own stated catchment** so the comparison is like for like:
Hauz Khas and Deer Park, Safdarjung Enclave, Green Park and SDA, Panchsheel Park, Malviya Nagar, Saket, Mehrauli
and Qutub, Vasant Kunj, Vasant Vihar, Aerocity, Defence Colony, Lajpat Nagar, South Extension, GK I and II, Kailash
Colony, Nehru Place, Kalkaji and CR Park. **Ten of these had no district at all in the old list** - which is part
of why a website-led pass was reaching for a different method.

**Districts are allowed to overlap and several do.** Deduplication is on `place_id`, so over-covering costs one
extra call at $0.035 and **can never produce a duplicate row** - the cheaper error by a wide margin when the
alternative is missing a venue.

**The check that the method actually changed**, written into the brief: **the five known in-catchment venues the
website pass missed - Summer House, Bohca, Dear Donna, Depot 48, Imperfecto HKV - should appear without being
named.** If they do not, the problem is the discovery call and not the catchment.

## [2026-10-05] The consistency sweep - fourteen documents told what changed (entry 166)

**Four stale cross-references turned up by accident in one day, so the whole spec set was swept.** They shared a
cause: **the architectural split of 09-30 and the corrections of 10-01 and 10-03 were written into the new
documents, and the old ones were never re-read.** A document that was right when written is not wrong by anyone's
fault, and that is exactly why nobody catches it.

### The banner

**Eleven documents that predate the split now carry the same note above their body**, naming the six identity
factors and their weights, the four that left the deck, the fact that **the identity factors no longer plan
anything**, the fact that **the vibe never touches a venue**, and the current successors - and ending **where the
body below disagrees with this note, this note wins.**

**The bodies were not rewritten and should not be.** `OUTING_PLAN_ENGINE.md` is 2,980 lines of machinery whose
history is worth keeping; a sweep that rewrote it would have introduced more errors than it fixed. **Three docs
were left alone entirely** - `CARD_READABILITY.md`, `AFFIL_AS_GIVE.md` and `FRONTEND_SWIPE_GAME_V4.md` name no
factors and nothing in them went stale.

### Six documents needed more than a banner

**`FACTORS_V6.md` 2a was the worst**, because it is a *current* document that contradicted a later correction. It
had `TALK` as register at rung 1, `AFFIL`+`MOVE` as layout, `FOCUS` deciding venue orientation - **retired on
10-01 and never swept back.** A developer opening the factors spec would have wired the vibe into venue selection,
**which is precisely the thing the split removed.** Rewritten to say the opposite, with what each factor does
touch.

**`CARD_SET_V10.md`** now states its own gap plainly: four of its seven factors are retired, and **`FOCUS` and
`SPONT` have no cards at all.** That is the one item here that blocks building rather than merely misleading.

**`ASSESSMENT_ENGINE.md`** carried three different deck lengths from three different factor sets - 10/20/14 in
2.2, 7-14 in 0a. **Corrected to 6/12/9**, with the arithmetic named so it is obvious next time.

**`COLLECTIVE_V1.md` said *nothing here is adopted*. Section 4 proposed `FOCUS` and `FOCUS` was adopted** on
09-30 - and now carries the strongest pull in the model at 0.80, on this document's own argument. Its test argued
against adopting `FOCUS` **on its own**; it was adopted as part of a wider split, which is a different question.

**`OUTING_PLAN_ENGINE.md`'s 09-17 banner** still said the vibe factors give the shape of the night and the venue
type. They do not: the user draws the shape.

### And three in documents updated earlier the same day

**The sweep found generator language I had missed this morning**, which is the useful part - the pass caught its
own author. `VIEW_FLOW.md` still said **the plan generates from the merged skeletons** at 5/5, and that an Open
Night **generates for everyone** the moment anyone is firm. Both corrected to the host picking from the stop list.
The room's chemistry chip still cited **CHEMISTRY_V2, superseded twice.** And `ASSESSMENT_ENGINE.md` cites
`IMAGE_PROMPTS.md`, **which does not exist** - a dead link is worse than a stale one, so it is marked.

**Outstanding:** `CARD_SET_V11.md` with scenes for `FOCUS` and `SPONT`.

## [2026-10-05] Preference tagging, HERIT's weight, and within-factor chemistry (entry 167)

**Four proposals from the user, three adopted and one adopted with its limits measured.** Prototyped in
`simulations/prefserve.py`.

### Silence as absence - and the Kwality test, which failed usefully

**A venue is tagged on `ENRG` and `CROWD` always; preferences only where the evidence speaks.** Three states:
**served with a score**, **not specialised** (a flag, never a zero), and **unknown**. The line between the last
two is the whole rule: **silence about food at a restaurant is evidence** - reviewers of restaurants write about
food - **and silence about food at a bar is not**, because reviewers of bars write about drinks and the room. That
is the Summer House case the user raised.

**The Kwality test produced two results, not one.** The hypothesis HELD: all five reviews say the place is old
without being asked - *since the 1970s*, *running since 1940*, *a piece of Delhi history*, *my grandparents ate
here*. **Age is narrated**, because it is one of the few venue attributes a reviewer treats as a story rather than
a fact.

**And the scorer FAILED it. `HERIT` came out 47** on a 1940 institution. The lexicon's list was museum vocabulary -
heritage, colonial, haveli, old-world - **and people do not write like that.** They write *institution*, *old
school*, *legendary*, *since 1940*, *my grandparents*. Widened: **47 -> 88 on 34 hits.**

**A second defect surfaced that nobody was looking for: `SCEN` scored 75** on reviews saying the decor is *dated*,
the room *plain*, *no frills* - because `decor` was a hi keyword and the lo list held only *shabby, run-down,
dingy*. **The look of a room is the attribute reviewers criticise most readily and the list could not hear any of
it.** Widened: **34**. The Summer House regression is unchanged at 7.1 points, so neither list broke anything.

**`SCEN` 34 against `HERIT` 88 is the user's own 10-01 finding, measured** - old-feeling and badly-kept are
orthogonal, and a single 'old' axis could never have said that.

**`NOV` came out of this as underivable from any corpus**: *somewhere new* is new to the USER, served from their
own history, never from a venue tag.

### Selection is no longer conditional

**Stage 2 used to run only where stage 1 tied and the room clashed, because the app had to emit ONE venue.** The
app now offers a list, so **stage 1 decides who is in the list and stage 2 decides the order within it.** The
clash machinery survives as the rule for which preferences count, not for whether to look.

### Within-factor chemistry

**A preference's weight is a function of the energy drawn for that stop.** `FOOD` 0.25 and `HERIT` 0.30 at high
`ENRG`, `SCEN` 0.55, `POL` and `GAMES` flat, and **`LIVE` the only one that RISES, to 1.30** - a gig IS high
energy, so it should be boosted rather than cut. **Nothing is taken from the user**: they still said `FOOD` 88,
and they also drew a room where food cannot be the point. The engine believes the drawing.

**Two limits measured rather than asserted.** **Suppression does not promote anything** - `FOOD` and `HERIT` fall,
`GAMES` merely stands still. In the user's own example the loud stop went to **Hauz Khas Social first and Game
Palacio third**, because Social serves `GAMES` *and* `FOOD`. **That is the engine being right and the example being
too specific**: a loud bar with pool tables is a better answer to *high energy, wants to play* than a dedicated
arcade, and it found that unprompted. **And the weights bite before suppression does** - with `LIVE` 62 against
`GAMES` 88 the live venue still won, because `LIVE` is weighted 18 and `GAMES` 12.

### `HERIT` to 10, and one reading flagged

**`HERIT` 14 -> 10 for selection only**; the badge and the profile are unchanged. It is about how hard the
preference argues for a venue, not how much it says about a person.

**The group rule is written as a veto and flagged as uncertain:** a preference is live only if somebody is at 70+
**and nobody is at 30-**. The alternative - averaging, so one low member damps rather than vetoes - is materially
different, and the user's sentence can be read either way.

## [2026-10-05] Preferences are preferences - and the multiplier does not survive (entry 168)

**The user corrected the veto reading, and the correction supplied a better mechanism than the one it replaced.**

### The rule

**A preference is live at a stop when somebody is at 60 or above AND some venue inside the shape gate can actually
serve it.** Live preferences order the list; a preference failing either test is not considered at that stop and
**carries to the next one** rather than being marked served.

**It is never a gate and never a veto.** A low member is **not an objector - they are simply not an advocate**,
which is where entry 167 had it wrong. And the hour does the rest: only venues open at that hour are in the list,
so *GAMES, depending on the time* needs no new machinery.

### Within-factor chemistry: proposed, measured, not adopted

**The observation was right - you cannot have high `ENRG` and high `FOOD` in the same room. The mechanism was
redundant.** `prefgate.py` measured it:

**The shape gate already performs the suppression.** With no multiplier applied, the share of in-gate venues that
can serve `FOOD` falls from **80% at a quiet stop to 10% at a loud one**, and `HERIT` from 43% to 2%. **The
correlation the table encoded is already in the data, venue by venue.**

**Over 4,000 stops the two methods agree 90.2% of the time - and where they differ the multiplier is wrong.** The
disagreements are all one shape: **a venue inside the gate that serves a suppressed preference anyway** - the loud
bar that genuinely does good food. At E94 with `FOOD` 88, feasibility finds a loud bar serving FOOD, POL and GAMES;
the multiplier discards FOOD 88 and sends them to a club. **The multiplier penalises exactly the venue that solves
the problem.**

**It is the error section 2a1 already forbids for slots, in a new place: the prior is for when evidence is missing,
never for overruling evidence that is present.** We have the venue's own tags, so they win.

**The `LIVE` boost to 1.30 goes with it.** Unlike the suppressions it was never a feasibility claim - it was mine,
and nothing evidences it.

**The prototype is kept** (`prefserve.py` section C, marked superseded) because the measurement that retired it only
makes sense next to the thing it retired.

## [2026-10-05] The editorial line scored, the venue's own fields given precedence (entry 169)

**Two gaps in the scoring path, both found by describing it rather than by running it.**

### The corpus was the reviews and nothing else

**`editorialSummary` and `generativeSummary` were being fetched and discarded.** They are the densest sentences
the call returns - *"sophisticated restaurant with a terrace, specialising in tapas and sharing plates"* carries
`POL`, `SCEN` and `FOOD` in fourteen words - and with **five reviews as the hard cap**, throwing away two more
texts was expensive. The corpus is now reviews plus both summaries.

### The structured fields did not touch the scores

**`liveMusic` only fed the slot gate, so `LIVE` was being guessed from whether five reviewers happened to mention
a band.** That is backwards: **a structured field is the venue saying so on its own listing.** Where it is present
it now beats any amount of keyword inference; where it is absent it says nothing.

`liveMusic` true sets `LIVE` 85, false marks it **not specialised**. `goodForWatchingSports` sets `FOCUS` 78.
`outdoorSeating` floors `SCEN` at 60. **And the `serves*` family is used only in its all-false form**, because
every bar serves dinner - the field proves a kitchen exists, not that food is the point. **It is good evidence of
absence and poor evidence of presence, and only the half it is good at is used.**

This is section 3b's three states reaching the code: **served with a score, not specialised, unknown** - and
`not_specialised` is emitted as a flag on the row, never as a zero.

### And the smoke test caught a third thing nobody was looking for

**A jazz club scored `ENRG` 0 and `TALK` 100.** `pipeline.py`'s `PRIOR_KEY` mapped venues to a `live room` prior
**that `lexicon.py` did not have**, so every live venue fell through the no-prior path, which damps far less.
**A type with no prior is not a neutral type - it is an undamped one**, and it produces exactly the extremes the
priors were introduced to stop. `live room` and `cafe` priors added, `cafe` unmapped from `buzzy restaurant`, and
**every value in `PRIOR_KEY` now has a prior behind it.** Piano Man moved from `ENRG` 0 to 21, `TALK` 100 to 83.

**This is the second time the same shape of bug has appeared in this file** - the first was `coarse_type` keys not
matching the lexicon's at all. **A mapping between two modules' vocabularies needs a test that every value on the
left has a home on the right**, and now there is one.

**Regressions unchanged:** the lexicon at 7.1 points mean gap, `realrun.py` at IN 14 / OUT 2.

## [2026-10-05] The venue build, all of it, in one file (entry 170)

**Everything was already pushed and nothing was in one place.** The instructions were spread across
`VENUE_BUILD_RUNBOOK.md` (the commands), `VENUE_DATABASE_V1.md` (the reasoning), `VENUE_DB_REVIEW_01.md` (the
licence clarification) and `pipeline.py` itself. `VENUE_DATABASE_HOW_TO.md` is all of it in one file, **written
plainly at the user's request** - short sentences, no jargon, the reasoning kept only where a rule would look
arbitrary without it.

**It covers:** the storage rule stated as a two-row table; which APIs and exactly what each returns, including the
five-review cap and the five things no API provides; what we deliberately do not use and why website-scraping
selected the wrong venues; the three commands with costs; admission including the within-type comparison; how one
factor score is worked out in five steps; the venue's own fields taking precedence; the three states; the band
rule; the human pass; what the app does with the result and therefore which two fields are load-bearing; and the
four traps, including the type-mapping bug that has now appeared twice.

**The old documents stay** - the runbook is still the commands-only page and now points here, and
`VENUE_DATABASE_V1.md` is still where the reasoning lives in full.

## [2026-10-06] The scoring index, and the module that was missing (entry 171)

**The developer could not find the scoring algorithm because there are seven of them and nothing said so.** It was
all pushed; it was never indexed.

**`SCORING.md`** is the index: a person's daily factors, the daily name, a room's identity and match and
disturbance, the two-person chemistry read, the skeleton merge, a venue's factors, and the stop list. For each one -
what goes in, what comes out, where the rules are written, and **which file you can run to watch it work.**

**Six of the seven already had a runnable file. The first did not** - the person-scoring path had 1,034 lines of
spec and twenty pseudocode blocks in `ASSESSMENT_ENGINE.md` and nothing to execute. **`simulations/assess.py`** is
that reference: swipes in, a scored profile and a name out, standard library only, every function pure.

### Two defects the module found in the spec it implements

**A single *not for me* was being counted as a refusal.** The spec's one-line rule reads `all(swipe == 'not')`,
which is correct only for a FINISHED factor - a lone *not* queues a second card rather than ending anything, and
**the prose beside it says exactly that.** Code and prose disagreed and the code was the one people would copy.

**A second card could land before its own first card.** Inserting B cards shifts the deck right, and measuring from
the original index put the last factor's B card ahead of its A card. Fixed by measuring from where the A card sits
now, and **checked exhaustively: 12,288 B cards across all 4,096 possible decks, none misplaced.**

### What the module confirms

It reproduces section 2.2's pair table exactly from one rule - **a factor's score is the mean of its cards** - and
it independently produces *Night Climber* for the session of 2026-10-05, which was worked out by hand at the time.

**And it shows that session for what it was: incomplete.** Only `ENRG` was answered at an extreme, so five factors
each queue a second card and the deck runs to eleven. Those five scores are provisional, which is what was said at
the time and is now demonstrable.

## [2026-10-06] Presets move to the SHUFFL screen, and the group chat stops making plans (entry 172)

**Six changes from the user, four taken as proposed and two argued.**

### The two controls

**Screen 03 had no primary action.** The redraw of 10-05 made the stop rows tappable and left *Reset* as the only
button, so the main thing a user does on that screen was a quiet affordance - **the user spotted it.** It now
carries **`Build this night`**, which opens the first stop with no venue and reads *Continue* once some are filled,
next to **`Redraw skeleton`** - *Reset* renamed because it never said what it reset.

### Presets move, and the user's reason beats the one the doc had

**They were a line of text under the skeleton and they are now a shelf on the SHUFFL screen.** The reason: a button
under the skeleton *gets blended into the background with the presence of the skeleton*. Somebody mid-draw is
concentrating on the drawing, and small text offering an alternative reads as a fallback for people who cannot
manage. **The same list, after you have drawn, named by things you recognise, reads as an offer** - *I do not want
this much control tonight, I want a tried and tested one.* **Drawing stays the only way in**, which also killed my
objection that presets on a gated screen are circular: they were never the route in.

**Matched to preferences and vibe**, four or five to the shelf, with **See all presets** as the escape hatch -
without it a mis-read of somebody's factors silently narrows their night and they never find out. **Written down as
a deliberate exception to vibe-to-shape inference**, because offering is not deciding and the alternatives are one
tap away - and because otherwise somebody will later 'fix' it by making the suggestion stronger.

**Time-sensitivity needed no new rule.** A Foodie's Day Out cannot run at 23:00 because its venues are shut, and
the stop list only shows venues open at that hour. **Feasibility, not a timetable.**

### Two arguments won, one lost

**Won: a preset opens with one button.** `Choose venues`, not Lock - there is nothing to lock until every stop has
a venue. The three buttons live on the finished card.

**Won: presets must not filter the public rooms list.** At launch volume a third filter stacked on plan similarity
and the per-member FLOOR check returns an empty screen. **The user went further and was right**: a preset becomes
an ordinary plan with a shape and venues, so the existing ranking already surfaces it. No new matching at all.

**Lost, and fairly: coloured pills over artwork tiles.** I drew both. My argument was that four lit colours leave
nothing primary on the screen; the user looked at it and chose pills with a dark glyph texture, **which is a better
idea than either of mine.** One piece of the objection survived: **no preset is gold**, because gold already means
there is money at that venue tonight.

### Presets do not exist in a room - and that disposes of a problem

**The only place people draw together is a friends room, and presets are excluded there**, because that is the one
case where the group is genuinely working out its shape and a preset would flatten it. **Everywhere else the plan
is set before anyone joins.** So a tapped preset and a drawn skeleton never meet in a merge - which removes the
question of **what firmness a preset has**, since `SKELETON_MERGE_V1.md` resolves opposed drawings by whose is
firmer and a preset has nothing to measure. **The rule removes the collision instead of inventing a number for it.**

### The group chat stops making plans

**The Create button generated an outing plan from everyone's vibes, and it was the last way a plan could come into
existence outside the Play flow.** Since the unlock sequence collects the filters and the shape after Play, a second
generator in a group chat described a path that no longer exists. **No plans, no shapes, no skeletons in a group
chat.**

**What replaces it is better.** The chemistry of the group - `CHEMISTRY_V4` at *n* people rather than two, which is
section 4's profile read generalised, **the same engine and no new machinery** - plus **a venue the group would all
like, from their going-out history and their preferences.**

**And my objection to that was wrong.** I said a venue needs a shape and an hour. The user's answer: history and
preferences are not the vibe. **Section 0 forbids identity factors picking venues; preferences are explicitly how a
venue gets chosen, and history is behaviour.** And it needs no hour **because it is not a stop** - it is a statement
about a place, not a position in a night.

**Cold start, written in as a judgement call:** a group with no history shows **chemistry only**, rather than a
preference-only guess dressed up as a recommendation. Reversible.

**Still open:** *The Desert Run* is drawn as a drive. If it was meant to be *dessert*, the glyphs and its place in
the library both change.

## [2026-10-06] The OSM discovery pass, and the second brief (entry 173)

**The developer's second file: five of six sheets byte-for-byte identical to the first, plus one new sheet of 436
OpenStreetMap candidates.** The database has not moved - still 0 of 110 venues with a full set of factor scores,
3 with a `place_id`, admission never run. The new sheet is **step 1 of their 4-step pipeline and is labelled as
such**, so the execution is honest. The problem is the source it executed against.

### Discovery is the gate

**Foursquare can only enrich what OSM already found**, so a venue absent from OpenStreetMap never enters the
pipeline at all. **The ceiling on the whole database is set at step 1**, before any scoring happens.

**What OSM returned for South Delhi: 436 candidates, of which 17 are bar/pub/nightclub - 4% - and exactly one is a
nightclub.** 419 are restaurants and cafes. **Zero overlap with the 110 venues they already have.** Nine of ten
reference venues absent, including **Hauz Khas Social, which is row 1 of their own Venues sheet** - a discovery
pass that cannot find a venue already catalogued will not find the ones that are not.

**And the pool it did return is the excluded category**: Aggarwal Sweets three times over as literal duplicates,
A1 Chaap Junction, Ajit Khalsa Dhaba. The bar list includes **Blue Frog, closed in Delhi years ago.** OSM here is
thin, stale and duplicated.

**Structurally: OSM in Delhi is volunteer-maintained, and volunteers map daytime food.** Nightlife is the category
it is weakest at, which is the category this app is strongest on.

### Three passes, three different biases, one cause

**Pass 1 used official websites and selected for chains and hotels** - 83% Group/Chain/Hotel, 3 clubs - because a
corporate website is a proxy for being a chain. **Pass 2 used OSM and selected for whatever hobbyists mapped.**
**Neither ranks by whether anyone actually goes there.**

**The fix is a discovery source whose index is built from real-world prominence, because that is the same signal
admission measures.** Nearby Search ranks on exactly that, which is why it and the filter agree rather than fight.
That is an argument about signal, not a preference for Google.

### The brief

`VENUE_DB_INSTRUCTIONS_02.md` is deliberately long: the measured findings, **the exact HTTP calls** - endpoint,
headers, field masks, bodies, per-call prices - a table of why each alternative source is rejected with its
specific reason, the four build stages with every threshold, what to keep from the existing file and how to
migrate it, **acceptance tests to run before spending the enrichment budget**, and the six traps ranked by cost.

**The acceptance test that matters: Summer House, Bohca, Dear Donna, Depot 48 and Imperfecto HKV must appear in
`candidates.json` without anyone naming them.** It is the one check that separates a working discovery pass from
the two that failed, and it costs $3.50 to run.
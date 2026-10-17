# Simulations

Python 3, no dependencies. Each file is the rules of its day run on imaginary rooms and a small
venue pool; the traces they print are the ones quoted in `decisions/DECISIONS.md`.

| File | Model | Status |
|---|---|---|
| `give.py` | the AFFIL-as-give prototype on Chemistry V2 (`specs/AFFIL_AS_GIVE.md`) — an exploration | exploration |
| `dayflow.py` | **a user swipes the identity deck and gets a vibe** - the adaptive deck, the swipe-to-score table, latency firmness, the ranking key and the name, end to end | **current** |
| `assess.py` | **the swipe scorer** - swipes to a scored profile and a name. The runnable reference for ASSESSMENT_ENGINE | **current** |
| `midband.py` | **is a 50 a reading or an absence** - where the model honours it and where it does not | **current** |
| `midsweep.py` | **the mid-band change across 4,000 rooms** - what it moves, and the two things that must move with it | **current** |
| `peoplematch.py` | **matching people** - the chemistry engine against plain similarity, and the cases where they invert | **current** |
| `meterband.py` | **the build-my-own meters** - blindness against jitter, what the span buys, and how often the hollow mark is on | **current** |
| `roomrank.py` | **ranking rooms** - the plan against the shape, and what the join gates would delete at launch volume | **current** |
| `roomfit.py` | **you against a room** - the headline from match and disturbance, and the axis lines | **current** |
| `roomline.py` | **the room line** - one sentence describing a room, from the vector chem4 already produces | **current** |
| `coordtag.py` | **coordinate tags against factor scores** - where quantising starts to win, and how far away that is | **current** |
| `prefgate.py` | **the test that retired within-factor chemistry** - feasibility against the multiplier over 4,000 stops | **current** |
| `prefserve.py` | **preference service** - the Kwality HERIT test, silence-as-absence, and within-factor chemistry | **current** |
| `pipeline.py` | **THE PIPELINE, runnable** - `discover` / `enrich` / `build`. Cached, retried, cost-estimating. See `specs/VENUE_BUILD_RUNBOOK.md` | **current** |
| `realrun.py` | **a real admission pass** over twelve researched Delhi venues - the run that found the mean floor is wrong for clubs | **current** |
| `prebuild.py` | **the pre-promotion build** - the confidence gate deciding which slots fill now and which are left for a capture, run on Bohca and Summer House (`specs/VENUE_DATABASE_V1.md` §2a0) | **current** |
| `onecap.py` | **one capture per slot** - why the time-box replaces the three, and what Rs 5 lakh then covers (`specs/GOLD_PROMOTION_V1.md`) | **current** |
| `capcheck.py` | **does the 3-capture cap let us pay more?** No - but without it 53% of what you pay for is a duplicate and coverage drops from 35 venues to 8 | **current** |
| `verify.py` | **the verification threshold**, set by the asymmetry between paying for a bad capture and wrongly accusing an honest user | **current** |
| `goldrush.py` | **costing the gold promotion** - which bands actually need capturing, and how far Rs 2-3 lakh goes (`specs/GOLD_PROMOTION_V1.md`) | **current** |
| `pairchem.py` | **pairwise vibe chemistry** - what two people would be like together rather than how alike they are; the 54-line reading table behind the MVP's profile feature (`specs/MVP_INSTRUCTIONS.md` §4) | **current** |
| `slots.py` | **the slot model** - every factor resolved for a (day, hour), and the Summer House LIVE correction that forced it (`specs/VENUE_DATABASE_V1.md` §2) | **current** |
| `lexicon.py` | **scoring a venue from review text** - the keyword method run on Bohca's real corpus, and the three fixes that took it from 23 points of error to 7 (`specs/VENUE_DATABASE_V1.md` §5.8) | **current** |
| `universe.py` | **how big the Delhi NCR universe is** - ~360 venues passing the admission bar, the district working, and the type mix that is thinnest exactly where nights end | **current** |
| `photocap.py` | **what the 10-photo API cap does to the estimators** - the share-versus-mean conclusion flips at the cap (`specs/VENUE_DATABASE_V1.md` §5.0.1) | **current** |
| `bandfix.py` | **the band problem, measured** - five ways to get an hourly shape without timestamps, scored on whether the error moves the pick (`specs/VENUE_DATABASE_V1.md` §5.4) | **current** |
| `imagetag.py` | **tagging venues from images** - selection bias, the confounded reference set, and why bands need Popular Times as well (`specs/VENUE_DATABASE_V1.md` §5) | **current** |
| `select3.py` | **selection V2** - the skeleton chooses, the shape gate keeps it exclusive, and a clash at one stop resolves across the night (`specs/VENUE_DATABASE_V1.md` §4) | **current** |
| `herit.py` | **how HERIT is served in a premium-only database** - fabric, styling and programming, and why old-feeling and unreliable are two axes rather than one (`specs/VENUE_DATABASE_V1.md` §1.4) | **current** |
| `admission.py` | **who gets into the venue database** - the premium bar, and why rating SPREAD rather than rating mean is what separates a place we can promise from one we cannot (`specs/VENUE_DATABASE_V1.md`) | **current** |
| `venuetag.py` | **how a venue is tagged and stored** - five contrasting rows, derived register/role, the supply grid they build, and what a drawn stop finds in it | **current** |
| `venuedb.py` | the venue database prototype and the four-rung selection ladder | **current** |
| `supplygrid.py` | the live preview as a query against real supply, not a table of type targets | **current** |
| `skelmerge.py` | **the skeleton merge** - clock alignment, the stop-count clamp, drawn firmness and the opposed-arc rule (`specs/SKELETON_MERGE_V1.md`) | **current** |
| `chem4.py` | **Chemistry V4** - contagion on the six identity axes only; splits-vs-joint, `FOCUS` and `SPONT`, plus the match / disturbance test behind point 6 (`specs/CHEMISTRY_V4.md`) | **current** |
| `namesim.py` | the vibe-name vocabulary: V4's eight factors against V5's six, and why `SECOND_MIN` drops 25 -> 20 (`specs/VIBE_NAMES_V5.md`) | **current** |
| `interplay.py` | the Chemistry **V3** interplay rules - superseded by `chem4.py` — what these people do to each axis of the room (`specs/CHEMISTRY_V3.md`) | history |
| `interactions.py` | pairs of axes interacting, on the readings model | current |
| `readings.py` | room-first from the readings — the current model (§14.3 v5, 2026-09-22); `roomfirst.py` is the rejected closeness-to-vector attempt | **current** |
| `design3.py` | Chemistry V2 on the designed night: one-way energy, the talk floor, Table and Floor, Common Ground, stop durations, the tags (`specs/CHEMISTRY_V2.md`) | **current** |
| `examples.py` | one room per chemistry state, plus the band, friends and solo, on `design2.py` | current |
| `design2.py` | `design.py` plus the extremes-only bend rule (§14.3.1a, 2026-09-18) | **current** |
| `design.py` | the designed night: every member's top vibe factor at every stop, maximin over types, a strong #2 standing in for a firmly opposed top, no debt, no dedicated stops; chemistry from how the design went (§14.3 v4, 2026-09-18) | **current** |
| `compose.py` | compose-first, then compromise on a collision (§14.3 v3, superseded the same day) | history |
| `splitsim.py` | the split factor set — seven vibe axes, ten venue types, the ROAM negotiation, a fill stage on six preferences; now Phase B of `compose.py` | current (as Phase B) |
| `friendsim.py` | debt / payback across stops, overall firmness, friend mode, on the ten-factor scale (§13.4c, §13.8, §13.9) | history |
| `joinsim.py` | the joiner's gate and match, room-level payback and chemistry, on the ten-factor scale (§13.6) | history |
| `debtsim.py` | the first debt / payback model (§13.4c as of 2026-09-17 morning) | history |

Run one with `python readings.py`. Add a room at the bottom of the file to try a scenario; the
venue pool is small and authored, so a preference that goes un-had is as often a gap in the pool
as a rule.
